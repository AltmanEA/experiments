#!/usr/bin/env bash
# Run remaining C6 (NVFP4 thinking on) with a progress indicator.
# Progress: runs/progress_C6.txt (append) + stdout.
set -u
cd "$(dirname "$0")"
export TRANSLATE_BACKEND=cloud
export NEURALDEEP_BASE_URL=http://127.0.0.1:8000/v1
export NEURALDEEP_API_KEY=local
export CLOUD_MODEL=Qwen3.6-35B-A3B-NVFP4
export CLOUD_CHAT_KWARGS='{"enable_thinking":true}'
export REQUEST_TIMEOUT=1200

PROG=runs/progress_C6.txt
TOTAL=21
done_n() { find runs/C6_local_nvfp4_think_on -name 'rep*.md' | wc -l; }
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }

log "START remaining C6: $(done_n)/$TOTAL done"
for f in S4 S5 S6 S7; do
  for k in 1 2 3; do
    R=runs/C6_local_nvfp4_think_on/$f; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { log "skip $f rep$k (exists)"; continue; }
    log "START $f rep$k ($(done_n)/$TOTAL done so far)"
    s=$(date +%s)
    python3 ../../tools/local_translate.py en ru ../../docs/en/glossary/index.md \
      < corpus/$f.md > "$R/rep$k.md" 2> "$R/rep$k.log"
    e=$?
    w=$(( $(date +%s)-s ))
    echo "$(date +%FT%T) C6_local_nvfp4_think_on $f rep$k exit=$e wall=${w}s" >> runs/runlog.txt
    fails=$(grep -c '\[FAIL\]' "$R/rep$k.log" || true)
    log "DONE $f rep$k exit=$e wall=${w}s fails=$fails ($(done_n)/$TOTAL)"
  done
done
log "ALL DONE $(done_n)/$TOTAL"
