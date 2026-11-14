#!/usr/bin/env bash
# P-004 extension: T=0.0 anchor conditions (probe showed server non-deterministic
# at greedy -> n=3 kept; T=0 rep-variation = serving non-determinism, E-008 noise floor).
set -u
cd "$(dirname "$0")"
MODEL=Qwen3.6-35B-A3B-NVFP4
log() { echo "[p004t0 $(date +%FT%T)] $*"; }
for spec in "T00_local_nvfp4_t00_think_off 0.0 false" "T00_local_nvfp4_t00_think_on 0.0 true"; do
  set -- $spec
  log "RUN $1 (temp=$2 thinking=$3)"
  TEMP=$2 bash ./run_progress.sh "$1" "$3" "$MODEL" || log "FAIL runner $1"
done
log "runs done: $(find runs/T00_local_nvfp4_* -name 'rep*.md' | wc -l)/42"
python3 metrics/aggregate.py || log "FAIL aggregate defects"
python3 metrics/judge_batch.py --mode absolute --conditions T00_local_nvfp4_t00_think_off T00_local_nvfp4_t00_think_on --workers 8 --rpm 24 || log "FAIL judge"
python3 metrics/judge_batch.py --mode absolute --repair --workers 2 --rpm 12 --timeout 600 || true
python3 metrics/judge_batch.py --mode absolute --aggregate || log "FAIL aggregate judge"
log "ALL DONE"
