#!/usr/bin/env bash
# Cloud judging batch, 2026-11-16 (quota day): P-005 + P-006 + P-002a.
#
# Pacing is driven by /v1/limits at launch time (see NOTES/journal for the reading):
#   * 02:30Z: night window ACTIVE, capacity_factor=2 -> chat rpm limit 120,
#     session 2371/2400 left, week 5971/6000.
#   * 03:00Z (~30 min after launch): night window ENDS -> capacity_factor 1,
#     the rpm ceiling and the session window halve again.
# So the batch is split: stage A (the critical path, P-005 FreeBSD) runs NOW at
# the doubled ceiling; stages B/C run at the daytime-safe ceiling and simply
# inherit whatever time they need. The pacer gate in judge_batch.py already holds
# on rpm_remaining<20, cooldown and session/week reserve, so these --rpm values
# are ceilings, not promises.
#
# Resume-safe: judge_batch.py skips existing valid cells; rerun after fixing 429s.
#
# Usage: bash run_judge_20261116.sh [--dry-run]
set -u
cd "$(dirname "$0")"

PY=${PY:-$PWD/.venv-analysis/bin/python}
[ -x "$PY" ] || PY=python3
STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/judge_20261116_${STAMP}.log"
mkdir -p runs
log() { echo "[judge $(date +%FT%T)] $*" | tee -a "$LOG"; }

FB_CORPUS=corpus/freebsd-ru/source
FB_PAIRS=corpus/freebsd-ru/gloss_pairs
FB_FIXTURES="F1_config F2_security F3_disks F4_network-servers F5_firewalls"
FB_CONDS="F_C5_local_nvfp4_think_off F_C6_local_nvfp4_think_on F_T00_local_nvfp4_t00_think_off F_T00_local_nvfp4_t00_think_on"
FP8_CONDS="FP8_T00_local_fp8_t00_think_off FP8_T00_local_fp8_t00_think_on FP8_T08_local_fp8_t08_think_off FP8_T08_local_fp8_t08_think_on"
# NOTE: full condition names required — task_list() resolves files by directory name
# (CLEAN_ALIAS only knows C2_clean) and SILENTLY drops pairs whose files are missing.
PAIRS="C3_local_fp8_think_off:C4_local_fp8_think_on,C5_local_nvfp4_think_off:C6_local_nvfp4_think_on,C1_cloud_bf16_think_off:C2_cloud_bf16_think_on_clean,T00_local_nvfp4_t00_think_off:T00_local_nvfp4_t00_think_on"

# Ceilings: A rides the night doubling, B/C stay inside the daytime ceiling (60)
# with headroom for the gate's rpm_remaining<20 hold.
RPM_NIGHT=${RPM_NIGHT:-40}
RPM_DAY=${RPM_DAY:-20}
WORKERS=${WORKERS:-8}
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

run() { # run <label> <args...>
  local label=$1; shift
  log "=== $label ($# args) ==="
  if [ "$DRY" = "1" ]; then
    log "DRY: $PY metrics/judge_batch.py $*"
    return 0
  fi
  python3 metrics/judge_batch.py "$@" 2>&1 | tee -a "$LOG"
  log "=== $label done (exit=${PIPESTATUS[0]}) ==="
}

log "START judging batch (night window: $([ -n "${FORCE_DAY:-}" ] && echo forced-day || echo auto))"

# ── A. P-005 FreeBSD absolute: 60 runs x 2 judges = 120 requests (critical path)
run "P-005 absolute (120)" --mode absolute --tag _freebsd \
  --fixtures $FB_FIXTURES --corpus-dir "$FB_CORPUS" --pairs-dir "$FB_PAIRS" \
  --conditions $FB_CONDS --workers "$WORKERS" --rpm "$RPM_NIGHT" --timeout 600

# ── B. P-006 FP8 temperature absolute: 84 runs x 2 judges = 168 requests
run "P-006 absolute (168)" --mode absolute \
  --conditions $FP8_CONDS --workers "$WORKERS" --rpm "$RPM_DAY" --timeout 600

# ── C. P-002a pairwise: 4 contrasts x 21 x 2 judges = 168 requests
run "P-002a pairwise (168)" --mode pairwise \
  --pairs "$PAIRS" --workers "$WORKERS" --rpm "$RPM_DAY" --timeout 600

# ── Repair pass: only cells recorded _status=fail (gemma long-prompt timeouts)
run "repair freebsd" --mode absolute --tag _freebsd --repair \
  --fixtures $FB_FIXTURES --corpus-dir "$FB_CORPUS" --pairs-dir "$FB_PAIRS" \
  --conditions $FB_CONDS --workers 2 --rpm 12 --timeout 600
run "repair fp8" --mode absolute --repair \
  --conditions $FP8_CONDS --workers 2 --rpm 12 --timeout 600
run "repair pairwise" --mode pairwise --repair \
  --pairs "$PAIRS" --workers 2 --rpm 12 --timeout 600

# ── Aggregates
log "=== aggregates ==="
python3 metrics/judge_batch.py --mode absolute --tag _freebsd --aggregate 2>&1 | tee -a "$LOG"
python3 metrics/judge_batch.py --mode absolute --aggregate 2>&1 | tee -a "$LOG"
python3 metrics/judge_batch.py --mode pairwise --aggregate 2>&1 | tee -a "$LOG"
python3 metrics/judge_effects.py --domain freebsd 2>&1 | tee -a "$LOG"

log "ALL DONE; log=$LOG"
log "artifacts: judge_freebsd/absolute/ (120+10), judge/absolute/FP8_* (168), judge/pairwise/ (168)"
log "NEXT: metrics/stats_tests.py on F- and FP8-contrasts, then SUMMARY-RU restrictions"
