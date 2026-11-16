#!/usr/bin/env bash
# P-008 (cloud variant): local bf16 was never provided by the operator, but the
# cloud endpoint now serves quantized checkpoints (qwen3.6-fp8-noreason). That
# splits the placement<->quantization confound (SUMMARY §9.1) WITHOUT a local bf16:
#
#   cloud FP8 (this run)  vs  C3  (local FP8, same params)  -> placement effect
#   cloud FP8 (this run)  vs  C1  (cloud bf16, same params) -> quantization effect
#
# Same parameters as C1/C3: Council corpus, T=0.2, thinking off, legacy engine +
# frozen glossary (vendor/legacy_local_translate_d5d77db.py, 56 terms) — the same
# pipeline C1/C3 saw. Parity probe runs before any request (same guard as P-006).
#
# Pacing: requests are strictly serial (one block at a time, engine retries are
# bounded), daytime rpm ceiling is 60; expected ~300 translation requests + 42
# judging requests. Resume-safe.
#
# Usage:
#   CLOUD_ALLOWED=1 bash run_p008_cloud_fp8.sh            # 21 runs
#   bash run_p008_cloud_fp8.sh --judge-only               # judging only
#   bash run_p008_cloud_fp8.sh --metrics-only             # aggregate + summary
#   bash run_p008_cloud_fp8.sh --dry-run
set -u
cd "$(dirname "$0")"

MODEL=${MODEL:-qwen3.6-fp8-noreason}
COND=${COND:-P8_cloud_fp8_think_off}
FIXTURES=${FIXTURES:-"S1 S2 S3 S4 S5 S6 S7"}
TRANSLATOR=$PWD/vendor/legacy_local_translate_d5d77db.py
GLOSS=$PWD/corpus/glossary_council_2026-11-11.md
EXPECT_TERMS=56
PY=${PY:-$PWD/.venv-analysis/bin/python}
[ -x "$PY" ] || PY=python3

DO_RUNS=1; DO_JUDGE=1; DRY=0
for arg in "$@"; do
  case "$arg" in
    --judge-only)  DO_RUNS=0 ;;
    --metrics-only) DO_RUNS=0; DO_JUDGE=0 ;;
    --dry-run)     DRY=1 ;;
    *) echo "unknown option: $arg"; exit 2 ;;
  esac
done

STAMP=$(date +%Y%m%d-%H%M%S)
LOG="runs/p008_cloud_fp8_${STAMP}.log"
log() { echo "[p008 $(date +%FT%T)] $*" | tee -a "$LOG"; }

if [ "$DO_RUNS" = "1" ] && [ "${CLOUD_ALLOWED:-0}" != "1" ]; then
  echo "BLOCKED: cloud usage requires explicit operator approval: CLOUD_ALLOWED=1 (see run_cloud.sh)." >&2
  exit 9
fi

# ── parity probe (identical guard to P-006): the frozen engine must reproduce
# the C1/C3 pipeline structure exactly, or we are measuring the pipeline again.
parity_probe() {
  log "=== probe: frozen engine reproduces the C1/C3 pipeline structure ==="
  # Same guard as P-006: run the frozen engine on S1 (a few real cloud requests)
  # and require the C1/C3-era structure: 56 terms, 5 blocks, '11 ok, 22 skip',
  # headings untranslated ('# Council' stays EN).
  local log_tmp rc terms blocks done_line first_head ok=0
  log_tmp=$(mktemp)
  out=$(TRANSLATE_BACKEND=cloud CLOUD_MODEL="$MODEL" \
        TRANSLATE_TEMP=0.2 TRANSLATE_TOP_P=0.95 REQUEST_TIMEOUT=600 MAX_RETRIES=1 \
        python3 "$TRANSLATOR" en ru "$GLOSS" < corpus/S1.md 2>"$log_tmp")
  rc=$?
  terms=$(sed -n 's/.*Glossary loaded: \([0-9]*\) terms.*/\1/p' "$log_tmp" | head -1)
  blocks=$(grep -c 'Block L' "$log_tmp")
  done_line=$(sed -n 's/^Done: \(.*\)$/\1/p' "$log_tmp" | head -1)
  first_head=$(printf '%s\n' "$out" | head -1)
  log "probe: exit=$rc terms=${terms:-?} blocks=${blocks:-?} done='${done_line:-?}' first_line='${first_head:-?}'"
  rm -f "$log_tmp"
  [ "$rc" -eq 0 ] || { log "PROBE FAIL: engine exited $rc"; ok=1; }
  [ "${terms:-0}" = "$EXPECT_TERMS" ] || { log "PROBE FAIL: expected $EXPECT_TERMS glossary terms, got ${terms:-?}"; ok=1; }
  [ "${blocks:-0}" -eq 5 ] || { log "PROBE FAIL: expected 5 blocks on S1 (C1 layout), got ${blocks:-?}"; ok=1; }
  case "${done_line:-}" in
    11\ ok*22\ skip*) : ;;
    *) log "PROBE FAIL: expected '11 ok, 22 skip' on S1, got '${done_line:-?}'"; ok=1 ;;
  esac
  [ "$first_head" = "# Council" ] || { log "PROBE FAIL: heading was translated ('$first_head'); C1 keeps '# Council'"; ok=1; }
  [ "$ok" -eq 0 ] && log "probe OK: pipeline parity with C1/C3 confirmed"
  return $ok
}

# ── thinking really off on this endpoint: reasoning_content must be empty
thinking_probe() {
  log "=== probe: noreason endpoint really switches reasoning off ==="
  "$PY" - "$MODEL" <<'EOF' || exit 4
import json, sys, subprocess
sys.path.insert(0, "metrics")
from judge import credentials
key, base = credentials()
body = {"model": sys.argv[1], "temperature": 0.2,
        "messages": [{"role": "user", "content": "Translate: `phase_id` is required."}]}
p = subprocess.run(["curl", "-sS", "-m", "90", base.rstrip("/") + "/chat/completions",
                    "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
                    "--data-binary", json.dumps(body)], capture_output=True, text=True, timeout=120)
d = json.loads(p.stdout)
m = d["choices"][0]["message"]
rc = m.get("reasoning_content") or ""
content = m.get("content") or ""
if len(rc) > 50:
    print(f"probe FAIL: reasoning_len={len(rc)}"); sys.exit(1)
for s in ("Let's", "Wait", "Actually", "I need to"):
    if s in content:
        print(f"probe FAIL: leak {s!r} in content"); sys.exit(1)
print(f"probe OK: reasoning_len={len(rc)}, content clean")
EOF
}

stage_runs() {
  log "=== runs: $COND ($MODEL, T=0.2, thinking off, legacy engine, cloud) ==="
  export TRANSLATE_BACKEND=cloud CLOUD_MODEL="$MODEL"
  export TRANSLATE_TEMP=0.2 TRANSLATE_TOP_P=0.95
  export REQUEST_TIMEOUT=600 MAX_RETRIES=1
  unset CLOUD_CHAT_KWARGS
  for f in $FIXTURES; do
    mkdir -p "runs/$COND/$f"
    for k in 1 2 3; do
      local md="runs/$COND/$f/rep$k.md"
      [ -s "$md" ] && { log "skip $f rep$k (exists)"; continue; }
      local t0=$(date +%s)
      python3 "$TRANSLATOR" en ru "$GLOSS" < "corpus/$f.md" > "$md" 2> "runs/$COND/$f/rep$k.log"
      local rc=$? wall=$(( $(date +%s) - t0 ))
      local fails; fails=$(grep -oE '[0-9]+ fail' "runs/$COND/$f/rep$k.log" | tail -1 | grep -oE '^[0-9]+' || echo "?")
      log "DONE $f rep$k exit=$rc wall=${wall}s fails=${fails:-?}"
      # serial + pause: keep well under the 60 rpm ceiling, no retry storms
      sleep 3
    done
  done
  local n; n=$(find "runs/$COND" -name 'rep*.md' 2>/dev/null | wc -l)
  log "runs done: $n/21"
  [ "$n" = "21" ]
}

stage_metrics() {
  log "=== defect metrics (P-008) ==="
  GLOSS=$GLOSS python3 metrics/aggregate.py \
    --conditions "$COND" --out-prefix _p008 2>&1 | tee -a "$LOG"
}

stage_judge() {
  log "=== judging $COND: 21 x 2 = 42 requests ==="
  python3 metrics/judge_batch.py --mode absolute --conditions "$COND" \
    --workers 4 --rpm 20 --timeout 600 2>&1 | tee -a "$LOG"
  python3 metrics/judge_batch.py --mode absolute --conditions "$COND" --repair \
    --workers 2 --rpm 12 --timeout 600 2>&1 | tee -a "$LOG"
  python3 metrics/judge_batch.py --mode absolute --aggregate 2>&1 | tail -3 | tee -a "$LOG"
}

log "START P-008: runs=$DO_RUNS judge=$DO_JUDGE dry=$DRY model=$MODEL"
if [ "$DRY" = "1" ]; then log "DRY: nothing started"; exit 0; fi

if [ "$DO_RUNS" = "1" ]; then
  parity_probe || { log "ABORT: parity probe failed"; exit 4; }
  thinking_probe || { log "ABORT: thinking probe failed"; exit 4; }
  stage_runs || log "WARN: runs incomplete (resume-safe, rerun)"
  stage_metrics
fi
[ "$DO_JUDGE" = "1" ] && stage_judge
log "ALL DONE; log=$LOG"
log "NEXT: CONTRAST — vs C3 (placement, same quant) and vs C1 (quantization, same placement)."
