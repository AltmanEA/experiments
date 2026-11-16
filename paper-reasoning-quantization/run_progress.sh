#!/usr/bin/env bash
# Local-model run with progress indicator (serial; one model at a time).
# Usage: run_progress.sh <condition-id> <true|false> <model-id> [fixtures]
# Env: BASE=server URL, TEMP=temperature (default 0.2; set e.g. 0.6/1.0 for P-004),
#      COUNCIL_DIR=path to council checkout (default ~/council), GLOSS=glossary path,
#      CORPUS_DIR=fixtures directory (default corpus; second domain: corpus/freebsd-ru/source),
#      TRANSLATOR=path to techdoc_translator.py (default ~/techdoc-translator/techdoc_translator.py).
#
# Pipeline note (ADR-014): the EN->RU engine moved out of the council checkout into
# the external techdoc-translator repo. Its CLI is flag-based
# (--input-en/--output-ru/--glossary) and its env names are TRANSLATE_API_BASE /
# TRANSLATE_API_KEY / TRANSLATE_MODEL / TRANSLATE_CHAT_KWARGS. The legacy
# positional CLI (local_translate.py en ru <gloss>) is still supported through
# TRANSLATOR_LEGACY=1 for re-running older conditions byte-identically.
set -u
cd "$(dirname "$0")"
COUNCIL_DIR=${COUNCIL_DIR:-$HOME/council}
TRANSLATOR=${TRANSLATOR:-$HOME/techdoc-translator/techdoc_translator.py}
TRANSLATOR_LEGACY=${TRANSLATOR_LEGACY:-0}
GLOSS=${GLOSS:-$COUNCIL_DIR/docs/en/glossary/index.md}
CORPUS_DIR=${CORPUS_DIR:-corpus}
COND=$1; THINK=$2; MODEL=$3; FIXTURES=${4:-S1 S2 S3 S4 S5 S6 S7}
BASE=${BASE:-http://127.0.0.1:8000/v1}
TEMP=${TEMP:-0.2}
PROG="runs/progress_${COND}.txt"
TOTAL=$(( $(echo $FIXTURES | wc -w) * 3 ))
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }

# preflight: translator present, server up, model id matches
[ -f "$TRANSLATOR" ] || { log "PREFLIGHT FAIL: translator not found at $TRANSLATOR"; exit 5; }
have=$(curl -sf -m 5 "$BASE/models" | python3 -c "import json,sys; print(' '.join(m['id'] for m in json.load(sys.stdin).get('data',[])))" 2>/dev/null)
case " $have " in
  *" $MODEL "*) log "preflight OK: model=$MODEL" ;;
  "") log "PREFLIGHT FAIL: server $BASE not reachable"; exit 3 ;;
  *)  log "PREFLIGHT FAIL: expected '$MODEL', server offers [$have]"; exit 4 ;;
esac

# Same knobs for both pipeline flavours (names differ, values must not).
export TRANSLATE_BACKEND=cloud
export TRANSLATE_API_BASE="$BASE" TRANSLATE_API_KEY=local
export TRANSLATE_MODEL="$MODEL" REQUEST_TIMEOUT=1800
export TRANSLATE_CHAT_KWARGS="{\"enable_thinking\":$THINK}"
export TRANSLATE_TEMP="$TEMP" TRANSLATE_TOP_P=0.95
# legacy aliases (local_translate.py read these)
export NEURALDEEP_BASE_URL="$BASE" NEURALDEEP_API_KEY=local
export CLOUD_MODEL="$MODEL" CLOUD_CHAT_KWARGS="$TRANSLATE_CHAT_KWARGS"

done_n() { find "runs/$COND" -name 'rep*.md' 2>/dev/null | wc -l; }
# ETA is computed from *this session* only: resumed runs are skipped instantly and
# would otherwise drag the average down and make the estimate uselessly optimistic.
fmt_hms() { local s=$1; printf '%dh%02dm%02ds' $((s/3600)) $((s%3600/60)) $((s%60)); }
sess_start=$(date +%s); sess_done=0
progress_line() {
  local n=$1 pct=$(( $1 * 100 / TOTAL )) eta="—"
  if [ "$sess_done" -gt 0 ]; then
    local avg=$(( ($(date +%s) - sess_start) / sess_done ))
    eta=$(fmt_hms $(( avg * (TOTAL - n) )))
  fi
  printf 'progress %2d/%d (%3d%%) elapsed %s eta %s' \
    "$n" "$TOTAL" "$pct" "$(fmt_hms $(( $(date +%s) - sess_start )))" "$eta"
}
log "START $COND model=$MODEL thinking=$THINK temp=$TEMP ($(done_n)/$TOTAL done)"
for f in $FIXTURES; do
  for k in 1 2 3; do
    R="runs/$COND/$f"; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { log "skip $f rep$k (exists)"; continue; }
    s=$(date +%s)
    if [ "$TRANSLATOR_LEGACY" = "1" ]; then
      python3 "$TRANSLATOR" en ru "$GLOSS" \
        < "$CORPUS_DIR/$f.md" > "$R/rep$k.md" 2> "$R/rep$k.log"
    else
      python3 "$TRANSLATOR" --allow-cloud \
        --input-en "$CORPUS_DIR/$f.md" --output-ru "$R/rep$k.md" --glossary "$GLOSS" \
        > /dev/null 2> "$R/rep$k.log"
    fi
    e=$?; w=$(( $(date +%s)-s ))
    echo "$(date +%FT%T) $COND $f rep$k exit=$e wall=${w}s" >> runs/runlog.txt
    fails=$(grep -c '\[FAIL\]' "$R/rep$k.log" || true)
    sess_done=$((sess_done+1))
    log "DONE $f rep$k exit=$e wall=${w}s fails=$fails ($(done_n)/$TOTAL) $(progress_line "$(done_n)")"
  done
done
log "ALL DONE $(done_n)/$TOTAL"
