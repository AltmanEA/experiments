#!/usr/bin/env bash
# Local-model run with progress indicator (serial; one model at a time).
# Usage: run_progress.sh <condition-id> <true|false> <model-id> [fixtures]
# Env: BASE=server URL, TEMP=temperature (default 0.2; set e.g. 0.6/1.0 for P-004),
#      COUNCIL_DIR=path to council checkout (default ~/council), GLOSS=glossary path.
set -u
cd "$(dirname "$0")"
COUNCIL_DIR=${COUNCIL_DIR:-$HOME/council}
TRANSLATE_PY=$COUNCIL_DIR/tools/local_translate.py
GLOSS=${GLOSS:-$COUNCIL_DIR/docs/en/glossary/index.md}
COND=$1; THINK=$2; MODEL=$3; FIXTURES=${4:-S1 S2 S3 S4 S5 S6 S7}
BASE=${BASE:-http://127.0.0.1:8000/v1}
TEMP=${TEMP:-0.2}
PROG="runs/progress_${COND}.txt"
TOTAL=$(( $(echo $FIXTURES | wc -w) * 3 ))
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }

# preflight: server up, model id matches
have=$(curl -sf -m 5 "$BASE/models" | python3 -c "import json,sys; print(' '.join(m['id'] for m in json.load(sys.stdin).get('data',[])))" 2>/dev/null)
case " $have " in
  *" $MODEL "*) log "preflight OK: model=$MODEL" ;;
  "") log "PREFLIGHT FAIL: server $BASE not reachable"; exit 3 ;;
  *)  log "PREFLIGHT FAIL: expected '$MODEL', server offers [$have]"; exit 4 ;;
esac

export TRANSLATE_BACKEND=cloud NEURALDEEP_BASE_URL="$BASE" NEURALDEEP_API_KEY=local
export CLOUD_MODEL="$MODEL" REQUEST_TIMEOUT=1800
export CLOUD_CHAT_KWARGS="{\"enable_thinking\":$THINK}"
export TRANSLATE_TEMP="$TEMP"

done_n() { find "runs/$COND" -name 'rep*.md' 2>/dev/null | wc -l; }
log "START $COND model=$MODEL thinking=$THINK temp=$TEMP ($(done_n)/$TOTAL done)"
for f in $FIXTURES; do
  for k in 1 2 3; do
    R="runs/$COND/$f"; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { log "skip $f rep$k (exists)"; continue; }
    s=$(date +%s)
    python3 "$TRANSLATE_PY" en ru "$GLOSS" \
      < "corpus/$f.md" > "$R/rep$k.md" 2> "$R/rep$k.log"
    e=$?; w=$(( $(date +%s)-s ))
    echo "$(date +%FT%T) $COND $f rep$k exit=$e wall=${w}s" >> runs/runlog.txt
    fails=$(grep -c '\[FAIL\]' "$R/rep$k.log" || true)
    log "DONE $f rep$k exit=$e wall=${w}s fails=$fails ($(done_n)/$TOTAL)"
  done
done
log "ALL DONE $(done_n)/$TOTAL"
