#!/usr/bin/env bash
# Paced cloud runner: respects neuraldeep rate limits with margin.
# Limits (tier "coder", 2026-11-11): session 1200 req / 3h, week 6000, RPM 60,
# concurrency 1. Safety margins used here: RPM<=45 (75%), session reserve>=15%.
# Retry policy: pipeline MAX_RETRIES=1 (no retry storms); on any retry/429 the
# runner pauses 60 s and re-queues the run once.
#
# Usage: [GLOSS=path] FIXTURES="S1.." REPS=3 cloud_paced.sh <condition-id> <model>
set -u
cd "$(dirname "$0")"
COND=$1; MODEL=$2; GLOS=${GLOSS:-../../docs/en/glossary/index.md}
FIXTURES=${FIXTURES:-S1 S2 S3 S4 S5 S6 S7}; REPS=${REPS:-3}
PROG="runs/progress_${COND}.txt"
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }

KEY=$(python3 - <<'EOF'
import json,os
p=os.path.expanduser('~/.config/opencode/opencode.json')
print(json.load(open(p))['provider']['neuraldeep']['options']['apiKey'])
EOF
)
BASE=${NEURALDEEP_BASE_URL:-https://api.neuraldeep.ru/v1}
RPM_CAP=${RPM_CAP:-40}          # soft ceiling, provider limit is 60 (33% margin)
RESERVE_PCT=${RESERVE_PCT:-15}  # keep >=15% of session limit untouched

limits() { curl -sS -m 20 "$BASE/limits" -H "Authorization: Bearer $KEY"; }

session_used() {
  limits | python3 -c "import json,sys; print(json.load(sys.stdin).get('chat',{}).get('session',{}).get('used',0))" 2>/dev/null || echo 0
}

# wait until a request is safe; prints one-line status
gate() {
  local j; j=$(limits) || { log "limits unavailable, sleep 60"; sleep 60; return 1; }
  python3 - "$j" "$RPM_CAP" "$RESERVE_PCT" <<'PY' || return 1
import json,sys
d=json.loads(sys.argv[1]); rpm_cap=int(sys.argv[2]); reserve=int(sys.argv[3])
ch=d.get("chat",{}); dec=d.get("decision",{})
s=ch.get("session",{}); w=ch.get("week",{}); r=ch.get("rpm",{})
can=dec.get("can_request", True)
need=[]
if not can: need.append("can_request=false")
if ch.get("cooldown_sec",0)>0: need.append(f"cooldown={ch['cooldown_sec']}s")
if r.get("remaining",99)<20: need.append(f"rpm_remaining={r.get('remaining')}")
limit=s.get("limit",0); rem=s.get("remaining",0)
if limit and rem < max(20, limit*reserve//100): need.append(f"session_reserve({rem}/{limit})")
if w.get("remaining",99)<max(50, (w.get("limit",0) or 0)*reserve//100): need.append(f"week_reserve({w.get('remaining')})")
if need:
    ra = dec.get("retry_after_sec") or ch.get("cooldown_sec") or 20
    print("WAIT", ";".join(need), "retry_after=", min(int(ra), 900))
    sys.exit(3)
print("OK", f"session {rem}/{limit}", f"week {w.get('remaining')}/{w.get('limit')}", f"rpm {r.get('remaining')}/{r.get('limit')}")
PY
}

wait_for_gate() {
  for i in $(seq 1 240); do
    out=$(gate 2>/dev/null) && { log "gate $out"; return 0; }
    ra=$(echo "$out" | sed -n 's/.*retry_after= \([0-9]*\)/\1/p'); ra=${ra:-120}
    [ "$ra" -gt 900 ] && ra=900
    log "gate HOLD: ${out:-no data} -> sleep ${ra}s"
    sleep "$ra"
  done
  return 1
}

export TRANSLATE_BACKEND=cloud CLOUD_MODEL="$MODEL" NEURALDEEP_BASE_URL="$BASE"
export REQUEST_TIMEOUT=1800 MAX_RETRIES=1
unset CLOUD_CHAT_KWARGS
done_n() { find "runs/$COND" -name 'rep*.md' 2>/dev/null | wc -l; }
TOTAL=$(( $(echo $FIXTURES | wc -w) * REPS ))
log "START $COND model=$MODEL ($(done_n)/$TOTAL done)"

for f in $FIXTURES; do
  for k in $(seq 1 "$REPS"); do
    R="runs/$COND/$f"; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { log "skip $f rep$k (exists)"; continue; }
    wait_for_gate || { log "ABORT: gate unresolvable"; exit 5; }
    used_before=$(session_used)
    s=$(date +%s)
    python3 ../../tools/local_translate.py en ru "$GLOS" < "corpus/$f.md" > "$R/rep$k.md" 2> "$R/rep$k.log"
    e=$?; w=$(( $(date +%s)-s ))
    echo "$(date +%FT%T) $COND $f rep$k exit=$e wall=${w}s" >> runs/runlog.txt
    grep -q "model=$MODEL" "$R/rep$k.log" || { rm -f "$R/rep$k.md" "$R/rep$k.log"; log "ABORT MODEL-MISMATCH $f rep$k"; exit 6; }
    # DEGRADED = infrastructure only (429/retry). [FAIL] is a quality metric, not a retry.
    if grep -q '\[retry\]\|429' "$R/rep$k.log"; then
      echo "DEGRADED $COND $f rep$k" >> runs/runlog.txt
      log "DONE $f rep$k exit=$e wall=${w}s DEGRADED -> pause 60s, requeue once"
      rm -f "$R/rep$k.md" "$R/rep$k.log"; sleep 60
      wait_for_gate || exit 5
      s=$(date +%s)
      python3 ../../tools/local_translate.py en ru "$GLOS" < "corpus/$f.md" > "$R/rep$k.md" 2> "$R/rep$k.log"
      e=$?; w=$(( $(date +%s)-s ))
      echo "$(date +%FT%T) $COND $f rep$k requeue exit=$e wall=${w}s" >> runs/runlog.txt
      grep -q '\[retry\]\|429' "$R/rep$k.log" && { log "SECOND-FAILURE $f rep$k -> stop"; exit 7; }
    fi
    log "DONE $f rep$k exit=$e wall=${w}s ($(done_n)/$TOTAL)"
    # adaptive pacing: keep sustained rate under RPM_CAP/min, not just under the hard 60
    if [ -n "${used_before:-}" ]; then
      after=$(session_used); reqs=$(( after - used_before ))
      [ "$reqs" -lt 0 ] && reqs=0   # session window reset mid-run
      need=$(( reqs * 60 / RPM_CAP ))
      if [ "$need" -gt "$w" ]; then
        gap=$(( need - w )); [ "$gap" -gt 60 ] && gap=60
        log "pace: ${reqs} req in ${w}s -> sleep ${gap}s"; sleep "$gap"
      fi
    fi
    sleep 3
  done
done
log "ALL DONE $(done_n)/$TOTAL"
