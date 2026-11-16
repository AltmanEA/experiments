#!/usr/bin/env bash
# C2 + C3 from PLAN-CLOSEOUT — cloud-judging only (no translation runs, no GPU).
#
#   C2  intra-judge test-retest: ~10 % of absolute cells (2 units per condition x
#       23 conditions x 2 judges = 92 requests) re-judged by the SAME judge into an
#       isolated tree (judge_retest/, tag _retest) — primary judge/ is never touched.
#       Units chosen deterministically (S1/rep3, S4/rep1 — same two for every condition,
#       reps vary across fixtures). Report: metrics/judge_retest.py ->
#       results/judge_retest.md/.csv.
#   C3  pairwise FreeBSD «machine vs official RU»: 4 machine conditions x 5 fixtures
#       x rep1 (official ref exists in rep1 only) x 2 judges, direct + reverse
#       (position control) = 80 requests. Staged runs dir with symlinks so both sides
#       of a pair resolve from one --runs-dir. Report: metrics/pairwise_freebsd_report.py
#       -> results/pairwise_freebsd.md/.csv.
#
# Total: 172 requests + repair (~<=200). Priced against DAYTIME limits on purpose
# (--rpm 20 vs the 60 daytime cap): safe to launch in the evening, no night-window
# assumptions, gate re-checks /v1/limits before every batch anyway.
#
# Run overnight, detached:
#   setsid nohup bash run_c2c3_night.sh > runs/c2c3_console.out 2>&1 &
# Resume-safe: rerun after interruption; completed cells are skipped, only
# _status=fail cells are retried by --repair.
#
#   bash run_c2c3_night.sh --c2-only | --c3-only | --report-only | --dry-run
set -u
cd "$(dirname "$0")"

PY=${PY:-python3}
PYV=.venv-analysis/bin/python; [ -x "$PYV" ] || PYV=$PY
RPM=${RPM:-20}          # daytime pacing; provider doubles capacity at night
TIMEOUT=${TIMEOUT:-600} # gemma times out on long FreeBSD prompts; repair closes leftovers

FB_FIXTURES="F1_config F2_security F3_disks F4_network-servers F5_firewalls"
FB_DOMAIN="--corpus-dir corpus/freebsd-ru/source --pairs-dir corpus/freebsd-ru/gloss_pairs"
# two units per condition: rep3 of S1, rep1 of S4 (spread reps across fixtures)
RETEST_UNITS="S1/rep3,S4/rep1"
STAGE=runs_c3_stage
REF=REF_freebsd_official
C3_CONDS="F_C5_local_nvfp4_think_off F_C6_local_nvfp4_think_on \
F_T00_local_nvfp4_t00_think_off F_T00_local_nvfp4_t00_think_on"

DO_C2=1; DO_C3=1; DO_REPORT=1; DRY=0
for arg in "$@"; do
  case "$arg" in
    --c2-only)     DO_C3=0 ;;
    --c3-only)     DO_C2=0 ;;
    --report-only) DO_C2=0; DO_C3=0 ;;
    --dry-run)     DRY=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/c2c3_night_${STAMP}.log"
log() { echo "[c2c3 $(date +%FT%T)] $*" | tee -a "$LOG"; }

quota() {
  $PY - <<'EOF' 2>/dev/null | tee -a "$LOG"
import json, subprocess, sys
sys.path.insert(0, "metrics")
from judge import credentials
key, base = credentials()
d = json.loads(subprocess.run(["curl", "-sS", "-m", "20", base.rstrip("/") + "/limits",
                               "-H", f"Authorization: Bearer {key}"],
                              capture_output=True, text=True).stdout)
c = d["chat"]
print(f"quota: night={d['night']['active']} rpm={c['rpm']['remaining']}/{c['rpm']['limit']} "
      f"session={c['session']['remaining']}/{c['session']['limit']} "
      f"week={c['week']['remaining']}/{c['week']['limit']} "
      f"can_request={d['decision']['can_request']} {d['decision']['blockers']}")
EOF
}

# hard gate: never start a batch the provider would refuse anyway
gate_check() {
  $PY - "$1" <<'EOF' || exit 5
import json, subprocess, sys
sys.path.insert(0, "metrics")
from judge import credentials
key, base = credentials()
d = json.loads(subprocess.run(["curl", "-sS", "-m", "20", base.rstrip("/") + "/limits",
                               "-H", f"Authorization: Bearer {key}"],
                              capture_output=True, text=True).stdout)
c = d["chat"]
need = 0 if len(sys.argv) < 2 else int(sys.argv[1])
if not d["decision"].get("can_request", True):
    print(f"BLOCKED by provider: {d['decision'].get('blockers')}"); sys.exit(1)
if c["session"].get("remaining", 0) < need + 30:
    print(f"BLOCKED: session {c['session'].get('remaining')} < need {need}+30 (wait for reset)"); sys.exit(1)
if c["week"].get("remaining", 0) < need + 200:
    print(f"BLOCKED: week {c['week'].get('remaining')} < need {need}+200"); sys.exit(1)
print("gate OK")
EOF
}

stage_c2() {
  log "=== C2 intra-judge retest: 23 cond x 2 units x 2 judges = 92 requests ==="
  quota
  gate_check 120
  CONDS=$($PY -c "import csv;print(' '.join(sorted({r['condition'] for r in csv.DictReader(open('results/judge_absolute.csv'))})))")
  $PY metrics/judge_batch.py --mode absolute --tag _retest \
    --conditions $CONDS --units "$RETEST_UNITS" \
    --workers 4 --rpm "$RPM" --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
  $PY metrics/judge_batch.py --mode absolute --tag _retest --repair \
    --workers 2 --rpm 12 --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
}

stage_c3() {
  log "=== C3 pairwise FreeBSD vs official RU: 4 cond x 5 fixtures x rep1 x 2 judges x 2 orders = 80 ==="
  # staging: pair resolution needs both sides under one --runs-dir
  mkdir -p "$STAGE"
  for c in $C3_CONDS; do ln -sfn "../runs/$c" "$STAGE/$c"; done
  ln -sfn "../runs_freebsd_ref/$REF" "$STAGE/$REF"
  local pairs=""
  for c in $C3_CONDS; do pairs="$pairs,$c:$REF"; done
  pairs=${pairs#,}
  quota
  gate_check 120
  for ord in direct reverse; do
    $PY metrics/judge_batch.py --mode pairwise --tag _freebsd_ref --order "$ord" \
      --fixtures $FB_FIXTURES $FB_DOMAIN --runs-dir "$STAGE" \
      --pairs "$pairs" --workers 4 --rpm "$RPM" --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
    $PY metrics/judge_batch.py --mode pairwise --tag _freebsd_ref --order "$ord" --repair \
      --fixtures $FB_FIXTURES $FB_DOMAIN --runs-dir "$STAGE" \
      --workers 2 --rpm 12 --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
  done
}

stage_report() {
  log "=== aggregate + reports ==="
  $PY metrics/judge_batch.py --mode absolute --tag _retest --aggregate 2>&1 | tail -1 | tee -a "$LOG"
  $PYV metrics/judge_retest.py 2>&1 | tail -25 | tee -a "$LOG"
  $PY metrics/judge_batch.py --mode pairwise --tag _freebsd_ref --aggregate 2>&1 | tail -1 | tee -a "$LOG"
  $PYV metrics/pairwise_freebsd_report.py 2>&1 | tail -15 | tee -a "$LOG"
  ( cd results && sha256sum *.csv *.md figs/*.png 2>/dev/null > MANIFEST.sha256 )
  log "manifest refreshed"
}

log "START C2+C3 night batch: c2=$DO_C2 c3=$DO_C3 report=$DO_REPORT dry=$DRY"
if [ "$DRY" = "1" ]; then
  CONDS=$($PY -c "import csv;print(' '.join(sorted({r['condition'] for r in csv.DictReader(open('results/judge_absolute.csv'))})))")
  $PY metrics/judge_batch.py --mode absolute --tag _retest --conditions $CONDS \
    --units "$RETEST_UNITS" --dry-run 2>&1 | head -4 | tee -a "$LOG"
  mkdir -p "$STAGE"; for c in $C3_CONDS; do ln -sfn "../runs/$c" "$STAGE/$c"; done
  ln -sfn "../runs_freebsd_ref/$REF" "$STAGE/$REF"
  $PY metrics/judge_batch.py --mode pairwise --tag _freebsd_ref --order direct \
    --fixtures $FB_FIXTURES $FB_DOMAIN --runs-dir "$STAGE" \
    --pairs "F_C5_local_nvfp4_think_off:$REF" --dry-run 2>&1 | head -4 | tee -a "$LOG"
  log "DRY: nothing requested"; exit 0
fi

[ "$DO_C2" = "1" ]     && stage_c2
[ "$DO_C3" = "1" ]     && stage_c3
[ "$DO_REPORT" = "1" ] && stage_report
log "ALL DONE; log=$LOG"
log "NEXT: results/judge_retest.md (intra noise vs inter-judge 19.24) and"
log "      results/pairwise_freebsd.md (machine vs official RU, with position control)."
log "Decision rule C2: intra mean|Δ| should be clearly BELOW inter-judge 19.24 and sign"
log "agreement of thinking contrasts >= 90 %; otherwise table-4 single verdicts need a caveat."
