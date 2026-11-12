#!/usr/bin/env bash
# Serial local runner (operator rule: one local model at a time).
# Usage: FIXTURES="S1 S2" REPS=3 run_local.sh <condition-id> <thinking true|false>
set -u
cd "$(dirname "$0")"
COND=$1; THINK=$2; FIXTURES=${FIXTURES:-S1 S2 S3 S4 S5 S6 S7}; REPS=${REPS:-3}
export TRANSLATE_BACKEND=cloud
export NEURALDEEP_BASE_URL=http://127.0.0.1:8000/v1
export NEURALDEEP_API_KEY=local
export CLOUD_MODEL=Qwen3.6-35B-A3B-NVFP4
export CLOUD_CHAT_KWARGS="{\"enable_thinking\":$THINK}"
export REQUEST_TIMEOUT=1200
for f in $FIXTURES; do
  for k in $(seq 1 "$REPS"); do
    R=runs/$COND/$f; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { echo "skip $COND/$f rep$k"; continue; }
    s=$(date +%s)
    python3 ../../tools/local_translate.py en ru ../../docs/en/glossary/index.md \
      < corpus/$f.md > "$R/rep$k.md" 2> "$R/rep$k.log"
    e=$?; echo "$(date +%FT%T) $COND $f rep$k exit=$e wall=$(( $(date +%s)-s ))s" >> runs/runlog.txt
  done
done
echo DONE $COND >> runs/runlog.txt
