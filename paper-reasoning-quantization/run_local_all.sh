#!/usr/bin/env bash
# Run every remaining local-model experiment on the *currently served* checkpoint.
#
# Right now that is Qwen3.6-35B-FP8 on http://127.0.0.1:1919/v1 (NVFP4 on :8000 is
# down). What is still missing on FP8 is P-006: the temperature anchors that let the
# P-004 temperature conclusions (and "greedy + thinking off") be checked on a second
# quantisation format.
#
#   P-006 core  FP8_T00_local_fp8_t00_think_{off,on}   T=0.0 x thinking  = 42 runs
#   P-006 hot   FP8_T08_local_fp8_t08_think_{off,on}   T=0.8 x thinking  = 42 runs
#                                                                        -----------
#                                                                        84 runs
# then defect metrics -> results/defects_fp8.csv + results/summary_fp8.md.
#
# Everything else in the registry is NOT local-model work:
#   P-005 runs + P-007 traces  done (NVFP4)
#   P-002a / P-005 judging     cloud quota only
#   P-008                      needs an operator-provided bf16 checkpoint
#
# Resume-safe: finished rep*.md are skipped, so this can be re-run at any time.
# If another local run is still going, this script waits for it first (one model
# at a time, per the operator rule).
#
# Usage:
#   bash run_local_all.sh              # wait for any running job, then run everything
#   bash run_local_all.sh --no-wait    # fail instead of waiting
#   bash run_local_all.sh --core-only  # skip the T=0.8 extension (42 runs)
#   bash run_local_all.sh --dry-run    # print the plan, change nothing
#
# Env: BASE (default http://127.0.0.1:1919/v1), MODEL (default Qwen3.6-35B-FP8).
set -u
cd "$(dirname "$0")"

BASE=${BASE:-http://127.0.0.1:1919/v1}
MODEL=${MODEL:-Qwen3.6-35B-FP8}

WAIT=1; EXTRA=1; DRY=0
for arg in "$@"; do
  case "$arg" in
    --no-wait)   WAIT=0 ;;
    --core-only) EXTRA=0 ;;
    --dry-run)   DRY=1 ;;
    -h|--help)   sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg (see --help)"; exit 2 ;;
  esac
done

STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/local_all_${STAMP}.log"
mkdir -p runs results
log() { echo "[local-all $(date +%FT%T)] $*" | tee -a "$LOG"; }

# ─────────────────────────────────────────────── which checkpoint is served
served_models() {
  curl -sf -m 5 "$BASE/models" | python3 -c \
    "import json,sys; print(' '.join(m['id'] for m in json.load(sys.stdin).get('data',[])))" 2>/dev/null
}

# ─────────────────────────────────────────────── is another local run active
# Matches the runners, not this script: `pgrep -f run_local_all` would match
# itself, so the patterns are the two worker scripts only.
running_jobs() {
  pgrep -af 'run_progress\.sh|run_p006_fp8\.sh|legacy_local_translate|techdoc_translator\.py' \
    | grep -v "run_local_all" || true
}

wait_for_idle() {
  local jobs
  jobs=$(running_jobs)
  [ -z "$jobs" ] && return 0
  if [ "$WAIT" = "0" ]; then
    log "BUSY: another local run is active and --no-wait was given:"
    printf '%s\n' "$jobs" | tee -a "$LOG"
    return 1
  fi
  log "waiting for the active local run to finish (one model at a time):"
  printf '%s\n' "$jobs" | tee -a "$LOG"
  local waited=0
  while [ -n "$(running_jobs)" ]; do
    sleep 60; waited=$((waited+60))
    [ $((waited % 600)) -eq 0 ] && log "still waiting (${waited}s elapsed)"
  done
  log "previous run finished after ${waited}s; starting"
  return 0
}

# ─────────────────────────────────────────────── plan
PLAN_RUNS=42
[ "$EXTRA" = "1" ] && PLAN_RUNS=84
CONDS="FP8_T00_local_fp8_t00_think_off FP8_T00_local_fp8_t00_think_on"
[ "$EXTRA" = "1" ] && CONDS="$CONDS FP8_T08_local_fp8_t08_think_off FP8_T08_local_fp8_t08_think_on"

log "START run_local_all: base=$BASE model=$MODEL extra_t08=$EXTRA wait=$WAIT dry=$DRY"
log "plan: P-006 on FP8 -> $PLAN_RUNS runs, then defect metrics"
log "conditions: $CONDS"

# ─────────────────────────────────────────────── preflight
ok=0
have=$(served_models)
case " $have " in
  *" $MODEL "*) log "preflight OK: $MODEL served at $BASE" ;;
  "")  log "PREFLIGHT FAIL: nothing served at $BASE (start the checkpoint first)"; ok=1 ;;
  *)   log "PREFLIGHT FAIL: expected '$MODEL', server offers [$have]"; ok=1 ;;
esac
[ -f vendor/legacy_local_translate_d5d77db.py ] \
  || { log "PREFLIGHT FAIL: missing frozen engine vendor/legacy_local_translate_d5d77db.py"; ok=1; }
[ -f corpus/glossary_council_2026-11-11.md ] \
  || { log "PREFLIGHT FAIL: missing frozen glossary corpus/glossary_council_2026-11-11.md"; ok=1; }

if [ "$DRY" = "1" ]; then
  log "dry: would wait for active jobs (if any), then run:"
  log "dry:   bash run_p006_fp8.sh $([ "$EXTRA" = "1" ] && echo '--with-t08')"
  running_jobs | sed 's/^/dry: active: /' | tee -a "$LOG"
  log "dry: nothing was started"
  exit 0
fi

[ "$ok" -eq 0 ] || { log "ABORT: preflight failed"; exit 3; }
wait_for_idle || { log "ABORT: local model busy"; exit 4; }

# ─────────────────────────────────────────────── the actual work
T0=$(date +%s)
args=()
[ "$EXTRA" = "1" ] && args+=(--with-t08)
log "delegating to run_p006_fp8.sh ${args[*]:-}"
bash ./run_p006_fp8.sh "${args[@]}" 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
T1=$(date +%s)

log "run_p006_fp8.sh exit=$rc after $(( (T1-T0)/60 ))m$(( (T1-T0)%60 ))s"

n=0
for c in $CONDS; do
  k=$(find "runs/$c" -name 'rep*.md' 2>/dev/null | wc -l)
  log "  $c: $k/21"
  n=$((n+k))
done
log "total: $n/$PLAN_RUNS runs"
[ -f results/defects_fp8.csv ] && log "metrics: results/defects_fp8.csv, results/summary_fp8.md"
log "NEXT: cloud judging of FP8_* conditions on a day with quota"
log "ALL DONE (exit=$rc); log=$LOG"
exit "$rc"
