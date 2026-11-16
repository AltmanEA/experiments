#!/usr/bin/env bash
# Overnight batch for the *current* local model (operator rule: one model at a time).
#
# Covers everything that needs no cloud quota and no operator action:
#   P-005  second domain (FreeBSD Handbook): 4 conditions x 5 fixtures x 3 reps = 60 runs
#   P-007  reasoning_content traces: S4/S5 x 3 reps = 6 runs (thinking on)
#   then   defect metrics, chrF vs official RU, nightly summary
#
# Judging (LLM-as-judge) is NOT run here: it needs cloud quota, and the weekly
# budget is nearly exhausted (5668/6000 at the time of writing). Run it later:
#     bash run_nightly.sh --judge-only
# which is also resume-safe.
#
# Everything is resume-safe: finished .md/.json artifacts are skipped, so an
# interrupted night can simply be restarted. A per-stage log goes to
# runs/nightly_<stamp>.log and a final digest to results/nightly_summary.md.
#
# Usage:
#   bash run_nightly.sh                     # runs + local metrics (default)
#   bash run_nightly.sh --runs-only         # only the 66 translation runs
#   bash run_nightly.sh --metrics-only      # only aggregate + chrF + summary
#   bash run_nightly.sh --judge-only        # only the cloud judging stage
#   bash run_nightly.sh --with-judge        # runs + metrics + judging
#   bash run_nightly.sh --dry-run           # print the plan, change nothing
#
# Env: MODEL (default Qwen3.6-35B-A3B-NVFP4), BASE (default 127.0.0.1:8000),
#      PY (analysis interpreter, default .venv-analysis/bin/python),
#      JUDGE_WORKERS (default 4), JUDGE_RPM (default 20).
set -u
cd "$(dirname "$0")"

MODEL=${MODEL:-Qwen3.6-35B-A3B-NVFP4}
BASE=${BASE:-http://127.0.0.1:8000/v1}
PY=${PY:-$PWD/.venv-analysis/bin/python}
[ -x "$PY" ] || PY=python3
JUDGE_WORKERS=${JUDGE_WORKERS:-4}
JUDGE_RPM=${JUDGE_RPM:-20}

FB_CORPUS=corpus/freebsd-ru/source
FB_GLOSS=$PWD/corpus/freebsd-ru/glossary_pipeline.md
FB_PAIRS=corpus/freebsd-ru/gloss_pairs
FB_FIXTURES="F1_config F2_security F3_disks F4_network-servers F5_firewalls"
FB_CONDS="F_C5_local_nvfp4_think_off F_C6_local_nvfp4_think_on F_T00_local_nvfp4_t00_think_off F_T00_local_nvfp4_t00_think_on"
TRACE_CONDS="TRACE_S4_local_nvfp4_t00_think_on TRACE_S5_local_nvfp4_t00_think_on"

STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/nightly_${STAMP}.log"
mkdir -p runs results
log() { echo "[nightly $(date +%FT%T)] $*" | tee -a "$LOG"; }

DO_RUNS=1; DO_METRICS=1; DO_JUDGE=0; DRY=0
for arg in "$@"; do
  case "$arg" in
    --runs-only)    DO_METRICS=0; DO_JUDGE=0 ;;
    --metrics-only) DO_RUNS=0; DO_JUDGE=0 ;;
    --judge-only)   DO_RUNS=0; DO_METRICS=0; DO_JUDGE=1 ;;
    --with-judge)   DO_JUDGE=1 ;;
    --dry-run)      DRY=1 ;;
    -h|--help)      sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg (see --help)"; exit 2 ;;
  esac
done

# ─────────────────────────────────────────────── preflight
preflight() {
  local ok=0
  log "preflight: model=$MODEL base=$BASE py=$PY"
  if ! curl -sf -m 5 "$BASE/models" | grep -q "\"$MODEL\""; then
    log "PREFLIGHT FAIL: $MODEL not served at $BASE"
    curl -s -m 5 "$BASE/models" | head -c 300 | tee -a "$LOG"; echo | tee -a "$LOG"
    ok=1
  else
    log "preflight OK: server offers $MODEL"
  fi
  [ -f "$FB_GLOSS" ] || { log "PREFLIGHT FAIL: missing $FB_GLOSS (run metrics/glossary_to_pipeline.py)"; ok=1; }
  for f in $FB_FIXTURES; do
    [ -f "$FB_CORPUS/$f.md" ] || { log "PREFLIGHT FAIL: missing fixture $FB_CORPUS/$f.md"; ok=1; }
  done
  [ -f "$HOME/techdoc-translator/techdoc_translator.py" ] \
    || { log "PREFLIGHT FAIL: translator not found (set TRANSLATOR=...)"; ok=1; }
  df -h . | tail -1 | tee -a "$LOG"
  return $ok
}

# ─────────────────────────────────────────────── P-005 runs
stage_runs() {
  log "=== P-005: FreeBSD domain, $MODEL (60 runs) ==="
  local specs=(
    "F_C5_local_nvfp4_think_off   0.2 false"
    "F_C6_local_nvfp4_think_on    0.2 true"
    "F_T00_local_nvfp4_t00_think_off 0.0 false"
    "F_T00_local_nvfp4_t00_think_on  0.0 true"
  )
  # off-conditions first: they are ~15x cheaper, so a short night still yields data
  for spec in "${specs[@]}"; do
    set -- $spec
    local cond=$1 temp=$2 think=$3
    log "RUN $cond (temp=$temp thinking=$think)"
    GLOSS=$FB_GLOSS CORPUS_DIR=$FB_CORPUS BASE=$BASE TEMP=$temp \
      bash ./run_progress.sh "$cond" "$think" "$MODEL" "$FB_FIXTURES" 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    [ "$rc" -ne 0 ] && log "WARN runner $cond exit=$rc (continuing; resume-safe)"
  done
  local n; n=$(find runs/F_* -name 'rep*.md' 2>/dev/null | wc -l)
  log "P-005 runs done: $n/60"
}

# ─────────────────────────────────────────────── P-007 traces
stage_traces() {
  log "=== P-007: reasoning_content traces (S4, S5 x 3 reps) ==="
  export TRANSLATE_BACKEND=cloud TRANSLATE_API_BASE="$BASE" TRANSLATE_API_KEY=local
  export TRANSLATE_MODEL="$MODEL" TRANSLATE_TEMP=0.0 TRANSLATE_TOP_P=0.95
  export TRANSLATE_CHAT_KWARGS='{"enable_thinking":true}'
  export REQUEST_TIMEOUT=1800 MAX_RETRIES=1
  for fx in S4 S5; do
    local cond="TRACE_${fx}_local_nvfp4_t00_think_on"
    log "TRACE $fx -> runs_trace/$cond"
    python3 metrics/dump_trace.py --condition "$cond" --fixture "$fx" --reps 1 2 3 \
      2>&1 | tee -a "$LOG"
  done
  local n; n=$(find runs_trace -name 'rep*.trace.jsonl' 2>/dev/null | wc -l)
  log "P-007 traces done: $n/6"
}

# ─────────────────────────────────────────────── local metrics
stage_metrics() {
  log "=== defect metrics (FreeBSD domain) ==="
  GLOSS=$FB_GLOSS python3 metrics/aggregate.py \
    --fixtures $FB_FIXTURES --corpus-dir "$FB_CORPUS" \
    --conditions $FB_CONDS --out-prefix _freebsd 2>&1 | tee -a "$LOG"

  log "=== chrF vs official RU reference ==="
  if [ -d corpus/freebsd-ru/reference ]; then
    "$PY" metrics/chrf.py --conditions $FB_CONDS --tag freebsd 2>&1 | tee -a "$LOG"
  else
    log "SKIP chrF: corpus/freebsd-ru/reference missing"
  fi

  log "=== nightly digest ==="
  python3 metrics/nightly_summary.py --log "$LOG" 2>&1 | tee -a "$LOG"
}

# ─────────────────────────────────────────────── cloud judging
stage_judge() {
  log "=== P-005 judging: absolute MQM, 2 judges (120 requests) ==="
  python3 metrics/judge_batch.py --mode absolute --tag _freebsd \
    --fixtures $FB_FIXTURES --corpus-dir "$FB_CORPUS" --pairs-dir "$FB_PAIRS" \
    --conditions $FB_CONDS --workers "$JUDGE_WORKERS" --rpm "$JUDGE_RPM" \
    --timeout 600 2>&1 | tee -a "$LOG"
  log "=== repair failed cells ==="
  python3 metrics/judge_batch.py --mode absolute --tag _freebsd --repair \
    --fixtures $FB_FIXTURES --corpus-dir "$FB_CORPUS" --pairs-dir "$FB_PAIRS" \
    --workers 2 --rpm 12 --timeout 600 2>&1 | tee -a "$LOG"
  log "=== judge aggregate + paired effects ==="
  python3 metrics/judge_batch.py --mode absolute --tag _freebsd --aggregate 2>&1 | tee -a "$LOG"
  python3 metrics/judge_effects.py --domain freebsd 2>&1 | tee -a "$LOG"
}

# ─────────────────────────────────────────────── main
log "START nightly: runs=$DO_RUNS metrics=$DO_METRICS judge=$DO_JUDGE dry=$DRY"
log "plan: P-005 60 runs ($MODEL, T in {0.0,0.2} x thinking) + P-007 6 traces"
[ "$DO_JUDGE" = "1" ] && log "note: judging needs cloud quota (120 requests, ~25 min at $JUDGE_RPM RPM)"

if [ "$DRY" = "1" ]; then
  preflight || log "DRY: preflight reported problems above"
  log "DRY: would run stage_runs / stage_traces / stage_metrics / stage_judge per flags"
  log "DRY: nothing was started"
  exit 0
fi

preflight || { log "ABORT: preflight failed (server down or assets missing)"; exit 3; }

T0=$(date +%s)
if [ "$DO_RUNS" = "1" ]; then
  stage_runs
  stage_traces
fi
if [ "$DO_METRICS" = "1" ]; then stage_metrics; fi
if [ "$DO_JUDGE" = "1" ]; then stage_judge; fi
T1=$(date +%s)
log "ALL DONE in $(( (T1-T0)/60 ))m$(( (T1-T0)%60 ))s; log=$LOG"
log "artifacts: runs/F_*/ (60), runs_trace/ (6), results/defects_freebsd.csv, results/chrf_freebsd.md"
[ "$DO_JUDGE" = "0" ] && log "NEXT: run 'bash run_nightly.sh --judge-only' on a day with cloud quota"
exit 0
