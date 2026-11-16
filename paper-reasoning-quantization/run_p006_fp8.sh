#!/usr/bin/env bash
# P-006: temperature on FP8 (second quantisation format) — closes SUMMARY §9.3.
#
# Why: P-004 varied temperature on NVFP4 only, so the temperature conclusions (H5)
# and the "greedy + thinking off" recommendation are NVFP4-local. This run repeats
# the temperature anchors on the FP8 checkpoint.
#
# WHY THE LEGACY PIPELINE AND A FROZEN GLOSSARY
# ---------------------------------------------
# The comparison target is C3/C4 (FP8, T=0.2), produced on 2026-11-11. Since then
# the EN->RU engine moved to ~/techdoc-translator (ADR-014) and changed behaviour
# in ways that break comparability with C3/C4:
#   * headings are now translated (old needs_skip() had `s.startswith('#')`);
#   * metadata lines are matched by a generic `Key: value` heuristic, so the
#     `Abstraction:` / `changelog-path:` lines that used to be skipped verbatim
#     now get merged into a paragraph block and partially translated;
#   * the glossary parser sees 73 terms in today's council glossary vs 56 then.
# Measured on corpus/S1.md: old pipeline 5 blocks / 11 ok / 22 skip; new pipeline
# 10 blocks / 17 ok / 15 skip. That is a pipeline confound, not a model effect.
# So P-006 runs the *vendored* engine snapshot (vendor/legacy_local_translate_d5d77db.py,
# byte-identical to council@d5d77db) with the glossary snapshot of 2026-11-11
# (corpus/glossary_council_2026-11-11.md, 56 terms) — exactly what C3/C4 saw.
#
# Conditions (Council corpus, 7 fixtures x 3 reps = 21 runs each):
#   FP8_T00_local_fp8_t00_think_off  T=0.0 off   <- anchor vs C3 (same quant, T=0.2)
#   FP8_T00_local_fp8_t00_think_on   T=0.0 on    <- H4 at greedy, FP8 vs NVFP4
#   (optional, --with-t08) T=0.8 off/on = 42 more runs, "hot" end of the curve
#
# Resume-safe: finished rep*.md are skipped. Artifacts stay in runs/FP8_* and
# results/*_fp8.*, so Council and FreeBSD tables are never overwritten.
#
# Usage:
#   bash run_p006_fp8.sh                  # core: T=0.0 x thinking (42 runs)
#   bash run_p006_fp8.sh --with-t08       # core + T=0.8 x thinking (84 runs)
#   bash run_p006_fp8.sh --metrics-only   # only aggregate + summary
#   bash run_p006_fp8.sh --dry-run        # print the plan, change nothing
#
# Env: BASE (default http://127.0.0.1:1919/v1), MODEL (default Qwen3.6-35B-FP8),
#      PY (default .venv-analysis/bin/python).
set -u
cd "$(dirname "$0")"

MODEL=${MODEL:-Qwen3.6-35B-FP8}
BASE=${BASE:-http://127.0.0.1:1919/v1}
PY=${PY:-$PWD/.venv-analysis/bin/python}
[ -x "$PY" ] || PY=python3

FIXTURES=${FIXTURES:-"S1 S2 S3 S4 S5 S6 S7"}
# Frozen inputs: the engine and glossary exactly as C3/C4 saw them.
TRANSLATOR=$PWD/vendor/legacy_local_translate_d5d77db.py
GLOSS=$PWD/corpus/glossary_council_2026-11-11.md
EXPECT_TERMS=56

CORE_SPECS=(
  "FP8_T00_local_fp8_t00_think_off 0.0 false"
  "FP8_T00_local_fp8_t00_think_on  0.0 true"
)
HOT_SPECS=(
  "FP8_T08_local_fp8_t08_think_off 0.8 false"
  "FP8_T08_local_fp8_t08_think_on  0.8 true"
)

STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/p006_fp8_${STAMP}.log"
mkdir -p runs results
log() { echo "[p006 $(date +%FT%T)] $*" | tee -a "$LOG"; }

DO_RUNS=1; DO_METRICS=1; WITH_T08=0; DRY=0
for arg in "$@"; do
  case "$arg" in
    --with-t08)     WITH_T08=1 ;;
    --runs-only)    DO_METRICS=0 ;;
    --metrics-only) DO_RUNS=0 ;;
    --dry-run)      DRY=1 ;;
    -h|--help)      sed -n '2,44p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg (see --help)"; exit 2 ;;
  esac
done

SPECS=("${CORE_SPECS[@]}")
[ "$WITH_T08" = "1" ] && SPECS+=("${HOT_SPECS[@]}")
CONDS=()
for spec in "${SPECS[@]}"; do set -- $spec; CONDS+=("$1"); done
NRUNS=$(( ${#CONDS[@]} * $(echo $FIXTURES | wc -w) * 3 ))

# ─────────────────────────────────────────────── preflight
preflight() {
  local ok=0
  log "preflight: model=$MODEL base=$BASE py=$PY"
  log "preflight: engine=$TRANSLATOR (frozen d5d77db snapshot)"
  log "preflight: glossary=$GLOSS (frozen 2026-11-11 snapshot)"
  local have
  have=$(curl -sf -m 5 "$BASE/models" | python3 -c \
    "import json,sys; print(' '.join(m['id'] for m in json.load(sys.stdin).get('data',[])))" 2>/dev/null)
  case " $have " in
    *" $MODEL "*) log "preflight OK: server offers $MODEL" ;;
    "")  log "PREFLIGHT FAIL: server $BASE not reachable"; ok=1 ;;
    *)   log "PREFLIGHT FAIL: expected '$MODEL', server offers [$have]"; ok=1 ;;
  esac
  [ -f "$TRANSLATOR" ] || { log "PREFLIGHT FAIL: missing $TRANSLATOR"; ok=1; }
  [ -f "$GLOSS" ]      || { log "PREFLIGHT FAIL: missing $GLOSS"; ok=1; }
  for f in $FIXTURES; do
    [ -f "corpus/$f.md" ] || { log "PREFLIGHT FAIL: missing fixture corpus/$f.md"; ok=1; }
  done
  df -h . | tail -1 | tee -a "$LOG"
  return $ok
}

# Guard against exactly the confound described in the header: the frozen engine
# must reproduce C3's structure on S1 (5 blocks, 11 ok / 22 skip, headings kept EN).
parity_probe() {
  log "=== probe: frozen engine reproduces the C3 pipeline structure ==="
  local out log_tmp
  log_tmp=$(mktemp)
  out=$(TRANSLATE_BACKEND=cloud NEURALDEEP_BASE_URL="$BASE" NEURALDEEP_API_KEY=local \
        CLOUD_MODEL="$MODEL" CLOUD_CHAT_KWARGS='{"enable_thinking":false}' \
        TRANSLATE_TEMP=0.0 TRANSLATE_TOP_P=0.95 REQUEST_TIMEOUT=600 \
        python3 "$TRANSLATOR" en ru "$GLOSS" < corpus/S1.md 2>"$log_tmp")
  local rc=$?
  local terms blocks done_line first_head
  terms=$(sed -n 's/.*Glossary loaded: \([0-9]*\) terms.*/\1/p' "$log_tmp" | head -1)
  blocks=$(grep -c 'Block L' "$log_tmp")
  done_line=$(sed -n 's/^Done: \(.*\)$/\1/p' "$log_tmp" | head -1)
  first_head=$(printf '%s\n' "$out" | head -1)
  log "probe: exit=$rc terms=${terms:-?} blocks=${blocks:-?} done='${done_line:-?}' first_line='${first_head:-?}'"
  rm -f "$log_tmp"
  local ok=0
  [ "$rc" -eq 0 ] || { log "PROBE FAIL: engine exited $rc"; ok=1; }
  [ "${terms:-0}" = "$EXPECT_TERMS" ] || { log "PROBE FAIL: expected $EXPECT_TERMS glossary terms, got ${terms:-?}"; ok=1; }
  [ "${blocks:-0}" -eq 5 ] || { log "PROBE FAIL: expected 5 blocks on S1 (C3 layout), got ${blocks:-?}"; ok=1; }
  case "${done_line:-}" in
    11\ ok*22\ skip*) : ;;
    *) log "PROBE FAIL: expected '11 ok, 22 skip' on S1, got '${done_line:-?}'"; ok=1 ;;
  esac
  [ "$first_head" = "# Council" ] || { log "PROBE FAIL: heading was translated ('$first_head'); C3 keeps '# Council'"; ok=1; }
  [ "$ok" -eq 0 ] && log "probe OK: pipeline parity with C3 confirmed"
  return $ok
}

# thinking must actually change behaviour, otherwise "on" silently duplicates "off"
thinking_probe() {
  log "=== probe: enable_thinking really switches reasoning on this server ==="
  local out
  out=$(python3 - "$BASE" "$MODEL" <<'PY'
import json, sys, urllib.request
base, model = sys.argv[1], sys.argv[2]
msg = "Translate to Russian, answer only with the translation: The kernel provides disk quota support."
for want in (True, False):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": msg}],
                       "temperature": 0.0,
                       "chat_template_kwargs": {"enable_thinking": want}}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer local"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    m = d["choices"][0]["message"]
    n = len(m.get("reasoning_content") or "")
    print(f"enable_thinking={str(want).lower():5s} reasoning_chars={n} content_len={len(m.get('content') or '')}")
PY
) || { log "PROBE FAIL: request error"; return 1; }
  echo "$out" | tee -a "$LOG"
  local on off
  on=$(echo "$out"  | sed -n 's/.*enable_thinking=true .*reasoning_chars=\([0-9]*\).*/\1/p')
  off=$(echo "$out" | sed -n 's/.*enable_thinking=false .*reasoning_chars=\([0-9]*\).*/\1/p')
  if [ "${on:-0}" -le 0 ]; then
    log "PROBE FAIL: enable_thinking=true produced no reasoning_content — 'on' would duplicate 'off'"
    return 1
  fi
  if [ "${off:-0}" -ne 0 ]; then
    log "PROBE FAIL: enable_thinking=false still produced reasoning_content ($off chars)"
    return 1
  fi
  log "probe OK: on=$on chars reasoning, off=0"
  return 0
}

# ─────────────────────────────────────────────── runs
stage_runs() {
  log "=== P-006: FP8 temperature anchors, $MODEL ($NRUNS runs) ==="
  for spec in "${SPECS[@]}"; do
    set -- $spec
    local cond=$1 temp=$2 think=$3
    log "RUN $cond (temp=$temp thinking=$think)"
    TRANSLATOR="$TRANSLATOR" TRANSLATOR_LEGACY=1 GLOSS="$GLOSS" CORPUS_DIR=corpus \
      BASE="$BASE" TEMP="$temp" \
      bash ./run_progress.sh "$cond" "$think" "$MODEL" "$FIXTURES" 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    [ "$rc" -ne 0 ] && log "WARN runner $cond exit=$rc (continuing; resume-safe)"
  done
  local n; n=$(for c in "${CONDS[@]}"; do find "runs/$c" -name 'rep*.md' 2>/dev/null; done | wc -l)
  log "P-006 runs done: $n/$NRUNS"
}

# ─────────────────────────────────────────────── metrics
stage_metrics() {
  log "=== defect metrics (FP8 conditions) ==="
  GLOSS=$GLOSS python3 metrics/aggregate.py \
    --fixtures $FIXTURES --corpus-dir corpus \
    --conditions "${CONDS[@]}" --out-prefix _fp8 2>&1 | tee -a "$LOG"

  log "=== summary ==="
  python3 - "${CONDS[@]}" <<'PY' 2>&1 | tee -a "$LOG"
import csv, statistics, sys
from collections import defaultdict
from pathlib import Path
conds = sys.argv[1:]
p = Path("results/defects_fp8.csv")
if not p.exists():
    print("_results/defects_fp8.csv not found_"); raise SystemExit(0)
rows = list(csv.DictReader(p.open()))
by = defaultdict(list)
for r in rows:
    by[r["condition"]].append(r)
print("\n| condition | runs | FAIL | D5nc term | D7nc contr | wall, s |")
print("|---|---|---|---|---|---|")
for c in conds:
    rs = by.get(c, [])
    if not rs:
        print(f"| {c} | 0 | — | — | — | — |"); continue
    def m(k):
        v = [float(r[k]) for r in rs if r.get(k) not in (None, "", "None")]
        return f"{statistics.mean(v):.2f}" if v else "—"
    print(f"| {c} | {len(rs)} | {m('fail')} | {m('term_missing_nc')} | "
          f"{m('contam_nc')} | {m('wall')} |")
PY
}

# ─────────────────────────────────────────────── main
log "START P-006: runs=$DO_RUNS metrics=$DO_METRICS with_t08=$WITH_T08 dry=$DRY"
log "plan: ${#CONDS[@]} conditions x $(echo $FIXTURES | wc -w) fixtures x 3 reps = $NRUNS runs"
log "conditions: ${CONDS[*]}"

if [ "$DRY" = "1" ]; then
  preflight || log "DRY: preflight reported problems above"
  parity_probe || log "DRY: pipeline parity probe failed (see above)"
  thinking_probe || log "DRY: thinking probe failed (see above)"
  log "DRY: would run stage_runs / stage_metrics"
  log "DRY: nothing was started"
  exit 0
fi

preflight || { log "ABORT: preflight failed (server down or assets missing)"; exit 3; }
parity_probe || { log "ABORT: pipeline parity with C3 not reproduced — results would not be comparable"; exit 4; }
thinking_probe || { log "ABORT: thinking probe failed — refusing to produce a duplicate 'off' condition"; exit 5; }

T0=$(date +%s)
if [ "$DO_RUNS" = "1" ]; then stage_runs; fi
if [ "$DO_METRICS" = "1" ]; then stage_metrics; fi
T1=$(date +%s)
log "ALL DONE in $(( (T1-T0)/60 ))m$(( (T1-T0)%60 ))s; log=$LOG"
log "artifacts: runs/FP8_*/ , results/defects_fp8.csv, results/summary_fp8.md"
log "NEXT: judge these conditions with cloud quota, then re-run --metrics-only"
exit 0
