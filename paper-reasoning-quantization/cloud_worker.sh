#!/usr/bin/env bash
# Parallel cloud worker: runs a DISJOINT set of fixtures for one condition.
# Safe to run alongside cloud_paced.sh: file names are disjoint per fixture,
# and the provider allows parallel_limit=16 concurrent chat requests
# (we use <=3 workers total). Refuses to start if another worker holds the
# same fixture (lock dir per fixture).
#
# Usage: cloud_worker.sh <condition-id> <model> "<fixtures>" <tag>
#   tag = short label used in progress file name and runlog comment
set -u
cd "$(dirname "$0")"
COND=$1; MODEL=$2; FIXTURES=$3; TAG=${4:-w1}
GLOS=${GLOSS:-../../docs/en/glossary/index.md}
REPS=${REPS:-3}
PROG="runs/progress_${COND}__${TAG}.txt"
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }

KEY=$(python3 - <<'EOF'
import json,os
p=os.path.expanduser('~/.config/opencode/opencode.json')
print(json.load(open(p))['provider']['neuraldeep']['options']['apiKey'])
EOF
)
BASE=${NEURALDEEP_BASE_URL:-https://api.neuraldeep.ru/v1}

limits() { curl -sS -m 20 "$BASE/limits" -H "Authorization: Bearer $KEY"; }

# gate: RPM headroom + session/week reserve; returns 0 (go) or 3 (wait)
gate() {
  local j; j=$(limits) || return 4
  python3 - "$j" <<'PY'
import json,sys
d=json.loads(sys.argv[1]); ch=d.get("chat",{}); dec=d.get("decision",{})
s=ch.get("session",{}); w=ch.get("week",{}); r=ch.get("rpm",{})
need=[]
if not dec.get("can_request", True): need.append("can_request=false")
if ch.get("cooldown_sec",0)>0: need.append(f"cooldown={ch['cooldown_sec']}s")
if r.get("remaining",99) < 20: need.append(f"rpm_remaining={r.get('remaining')}")
lim=s.get("limit",0)
if lim and s.get("remaining",0) < lim*15//100: need.append(f"session_reserve({s.get('remaining')}/{lim})")
if w.get("remaining",99) < (w.get("limit",0) or 0)*15//100: need.append(f"week_reserve({w.get('remaining')})")
if d.get("abuse_cooldown_sec",0) > 0: need.append(f"abuse_cooldown={d['abuse_cooldown_sec']}s")
if need:
    print("WAIT", ";".join(need)); sys.exit(3)
print("OK", f"session {s.get('remaining')}/{lim}", f"week {w.get('remaining')}/{w.get('limit')}",
      f"rpm {r.get('remaining')}/{r.get('limit')}", f"parallel_limit {d.get('parallel_limit','?')}")
PY
}

wait_gate() {
  for i in $(seq 1 240); do
    out=$(gate 2>/dev/null); rc=$?
    [ $rc -eq 0 ] && { log "gate $out"; return 0; }
    [ $rc -eq 4 ] && { log "gate: limits unavailable -> sleep 60"; sleep 60; continue; }
    log "gate HOLD ($TAG): $out -> sleep 30"; sleep 30
  done
  return 1
}

export TRANSLATE_BACKEND=cloud CLOUD_MODEL="$MODEL" NEURALDEEP_BASE_URL="$BASE"
export REQUEST_TIMEOUT=1800 MAX_RETRIES=1
unset CLOUD_CHAT_KWARGS 2>/dev/null || true

log "START $COND worker=$TAG fixtures=[$FIXTURES] model=$MODEL"
for f in $FIXTURES; do
  LOCK="runs/$COND/.lock_$f"
  mkdir "$LOCK" 2>/dev/null || { log "SKIP $f: locked by another worker"; continue; }
  trap 'rmdir "$LOCK" 2>/dev/null' EXIT
  for k in $(seq 1 "$REPS"); do
    R="runs/$COND/$f"; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { log "skip $f rep$k (exists)"; continue; }
    wait_gate || { log "ABORT $TAG: gate unresolvable"; exit 5; }
    s=$(date +%s)
    python3 ../../tools/local_translate.py en ru "$GLOS" < "corpus/$f.md" > "$R/rep$k.md" 2> "$R/rep$k.log"
    e=$?; w=$(( $(date +%s)-s ))
    echo "$(date +%FT%T) $COND $f rep$k exit=$e wall=${w}s concurrency=3 worker=$TAG" >> runs/runlog.txt
    grep -q "model=$MODEL" "$R/rep$k.log" || { rm -f "$R/rep$k.md" "$R/rep$k.log"; log "ABORT MODEL-MISMATCH $f rep$k"; exit 6; }
    if grep -q '\[retry\]\|429' "$R/rep$k.log"; then
      echo "DEGRADED $COND $f rep$k worker=$TAG" >> runs/runlog.txt
      log "DONE $f rep$k wall=${w}s DEGRADED -> sleep 60, requeue once"
      rm -f "$R/rep$k.md" "$R/rep$k.log"; sleep 60
      wait_gate || exit 5
      s=$(date +%s)
      python3 ../../tools/local_translate.py en ru "$GLOS" < "corpus/$f.md" > "$R/rep$k.md" 2> "$R/rep$k.log"
      e=$?; w=$(( $(date +%s)-s ))
      echo "$(date +%FT%T) $COND $f rep$k requeue exit=$e wall=${w}s worker=$TAG" >> runs/runlog.txt
      grep -q '\[retry\]\|429' "$R/rep$k.log" && { log "SECOND-FAILURE $f rep$k -> stop worker"; exit 7; }
    fi
    log "DONE $f rep$k exit=$e wall=${w}s"
  done
  rmdir "$LOCK" 2>/dev/null; trap - EXIT
done
log "WORKER DONE [$FIXTURES]"
