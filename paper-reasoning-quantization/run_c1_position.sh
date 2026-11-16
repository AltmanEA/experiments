#!/usr/bin/env bash
# C1 (PLAN-CLOSEOUT): position control for pairwise judgements — PLAN §6.2 requires
# "blind pairwise with order permutation + position bias report", which P-002a did not
# implement (condition A was always in slot A, and every one of the 168 verdicts came
# back as winner=A with 0 ties).
#
# Two stages, both cloud-judging only (no translation runs, no GPU):
#   reverse    — all 4 P-002a contrasts, slots mirrored, winner mapped back to conditions
#                (21 units x 2 judges x 4 contrasts = 168 requests)
#   tie-probe  — same text in both slots on 10 units (2 orders x 5 units x 2 judges = 40);
#                bounds the meaning of "0 ties in 168" in the main table.
#
# Pacing: --rpm 20 (daytime ceiling 60, night window doubles it but this batch is small),
# gemma needs --timeout 600 (it times out on long prompts; those cells close via --repair).
# Resume-safe: judge_batch.py skips cells that already hold a valid verdict.
#
# Usage:
#   bash run_c1_position.sh              # reverse + tie-probe + aggregate + report
#   bash run_c1_position.sh --reverse-only
#   bash run_c1_position.sh --probe-only
#   bash run_c1_position.sh --report-only
#   bash run_c1_position.sh --dry-run
set -u
cd "$(dirname "$0")"

PY=${PY:-python3}
[ -x "$PY" ] || PY=python3
PAIRS="C3_local_fp8_think_off:C4_local_fp8_think_on,C5_local_nvfp4_think_off:C6_local_nvfp4_think_on,C1_cloud_bf16_think_off:C2_cloud_bf16_think_on_clean,T00_local_nvfp4_t00_think_off:T00_local_nvfp4_t00_think_on"
# Null probe runs on both sides of the sharpest contrast (42:0, 2.1x length gap).
PROBE_PAIRS="C1_cloud_bf16_think_off:C2_cloud_bf16_think_on_clean,C5_local_nvfp4_think_off:C6_local_nvfp4_think_on"
# 5 units spread over fixtures (stride picks one rep per fixture).
PROBE_UNITS="S1/rep1,S2/rep2,S3/rep3,S4/rep1,S5/rep2"
RPM=${RPM:-20}
TIMEOUT=${TIMEOUT:-600}

DO_REV=1; DO_PROBE=1; DO_REPORT=1; DRY=0
for arg in "$@"; do
  case "$arg" in
    --reverse-only) DO_PROBE=0 ;;
    --probe-only)   DO_REV=0 ;;
    --report-only)  DO_REV=0; DO_PROBE=0 ;;
    --dry-run)      DRY=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/c1_position_${STAMP}.log"
log() { echo "[c1 $(date +%FT%T)] $*" | tee -a "$LOG"; }

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

stage_reverse() {
  log "=== reverse order: 4 contrasts x 21 units x 2 judges = 168 requests ==="
  quota
  gate_check 200
  $PY metrics/judge_batch.py --mode pairwise --order reverse --pairs "$PAIRS" \
    --workers 4 --rpm "$RPM" --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
  $PY metrics/judge_batch.py --mode pairwise --order reverse --repair \
    --workers 2 --rpm 12 --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
}

stage_probe() {
  log "=== tie null probe: A-vs-A on 5 units, both sides, 2 judges = 40 requests ==="
  quota
  gate_check 60
  for ord in same_a same_b; do
    $PY metrics/judge_batch.py --mode pairwise --order "$ord" --pairs "$PROBE_PAIRS" \
      --units "$PROBE_UNITS" --workers 3 --rpm "$RPM" --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
    $PY metrics/judge_batch.py --mode pairwise --order "$ord" --repair \
      --workers 2 --rpm 12 --timeout "$TIMEOUT" 2>&1 | tee -a "$LOG"
  done
}

stage_report() {
  log "=== aggregate + position report ==="
  $PY metrics/judge_batch.py --mode pairwise --aggregate 2>&1 | tail -2 | tee -a "$LOG"
  .venv-analysis/bin/python metrics/pairwise_report.py 2>&1 | tail -3 | tee -a "$LOG"
}

log "START C1 position control: reverse=$DO_REV probe=$DO_PROBE report=$DO_REPORT dry=$DRY"
if [ "$DRY" = "1" ]; then
  $PY metrics/judge_batch.py --mode pairwise --order reverse --pairs "$PAIRS" --dry-run 2>&1 | head -3 | tee -a "$LOG"
  $PY metrics/judge_batch.py --mode pairwise --order same_a --pairs "$PROBE_PAIRS" --units "$PROBE_UNITS" --dry-run 2>&1 | head -2 | tee -a "$LOG"
  log "DRY: nothing requested"; exit 0
fi

[ "$DO_REV" = "1" ]   && stage_reverse
[ "$DO_PROBE" = "1" ] && stage_probe
[ "$DO_REPORT" = "1" ] && stage_report
log "ALL DONE; log=$LOG"
log "NEXT: read results/pairwise_report.md — section 'Контроль позиции'. Decision rule:"
log "  bias<0.05 & McNemar p>0.05 & concordance>=0.8 -> publish direct verdicts as is."
