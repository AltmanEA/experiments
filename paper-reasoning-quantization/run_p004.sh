#!/usr/bin/env bash
# P-004 orchestrator: 8 temperature conditions (NVFP4 local) -> defects aggregate ->
# absolute judging (2 judges) -> repair -> aggregate. Resume-safe: run_progress.sh
# and judge_batch.py skip completed artifacts.
# Usage: bash run_p004.sh [--skip-runs] [--skip-judge]
set -u
cd "$(dirname "$0")"
MODEL=Qwen3.6-35B-A3B-NVFP4
OFFS=("T04_local_nvfp4_t04_think_off 0.4 false" "T06_local_nvfp4_t06_think_off 0.6 false"
      "T08_local_nvfp4_t08_think_off 0.8 false" "T10_local_nvfp4_t10_think_off 1.0 false")
ONS=("T04_local_nvfp4_t04_think_on 0.4 true" "T06_local_nvfp4_t06_think_on 0.6 true"
     "T08_local_nvfp4_t08_think_on 0.8 true" "T10_local_nvfp4_t10_think_on 1.0 true")
CONDS_OFF="T04_local_nvfp4_t04_think_off T06_local_nvfp4_t06_think_off T08_local_nvfp4_t08_think_off T10_local_nvfp4_t10_think_off"
CONDS_ON="T04_local_nvfp4_t04_think_on T06_local_nvfp4_t06_think_on T08_local_nvfp4_t08_think_on T10_local_nvfp4_t10_think_on"
log() { echo "[p004 $(date +%FT%T)] $*"; }

if [ "${1:-}" != "--skip-runs" ]; then
  for spec in "${OFFS[@]}" "${ONS[@]}"; do
    set -- $spec; COND=$1; T=$2; TH=$3
    log "RUN $COND (temp=$T thinking=$TH)"
    TEMP=$T bash ./run_progress.sh "$COND" "$TH" "$MODEL" || log "FAIL runner $COND"
  done
  log "runs complete: $(find runs/T0*_local_nvfp4_* runs/T10_local_nvfp4_* -name 'rep*.md' 2>/dev/null | wc -l)/168"
fi

if [ "${1:-}" != "--skip-judge" ] && [ "${2:-}" != "--skip-judge" ]; then
  log "aggregate defects"
  python3 metrics/aggregate.py || log "FAIL aggregate defects"
  log "judge absolute (off-conditions)"
  python3 metrics/judge_batch.py --mode absolute --conditions $CONDS_OFF --workers 8 --rpm 24 || log "FAIL judge off"
  log "judge absolute (on-conditions)"
  python3 metrics/judge_batch.py --mode absolute --conditions $CONDS_ON --workers 8 --rpm 24 || log "FAIL judge on"
  log "repair failed cells"
  python3 metrics/judge_batch.py --mode absolute --repair --workers 4 --rpm 24 || log "FAIL repair"
  log "aggregate judge"
  python3 metrics/judge_batch.py --mode absolute --aggregate || log "FAIL aggregate judge"
fi
log "ALL DONE"
