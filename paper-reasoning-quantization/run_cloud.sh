#!/usr/bin/env bash
# Cloud runner. Usage: [GLOSS=path] FIXTURES="S1.." REPS=3 run_cloud.sh <condition-id> <model>
set -u
cd "$(dirname "$0")"
if [ "${CLOUD_ALLOWED:-0}" != "1" ]; then
  echo "BLOCKED: cloud provider usage is disabled by operator (2026-11-11)."
  echo "Set CLOUD_ALLOWED=1 only after explicit operator approval." >&2
  exit 9
fi
COND=$1; MODEL=$2; GLOS=${GLOSS:-../../docs/en/glossary/index.md}; FIXTURES=${FIXTURES:-S1 S2 S3 S4 S5 S6 S7}; REPS=${REPS:-3}
export TRANSLATE_BACKEND=cloud
export CLOUD_MODEL="$MODEL"          # BUGFIX: model arg was never exported -> all runs used default
unset CLOUD_CHAT_KWARGS
export REQUEST_TIMEOUT=1800
echo "runner: cond=$COND model=$MODEL gloss=$GLOS" > "runs/.runner-$COND.meta"

# Rate-limit barrier: never hammer the provider. Probe first, honor Retry-After.
cloud_ok() {
  python3 - "$MODEL" <<'EOF'
import json,os,sys,time,urllib.request,urllib.error
key=os.environ.get("NEURALDEEP_API_KEY")
if not key:
    cfg=os.path.join(os.path.expanduser("~"),".config/opencode/opencode.json")
    key=json.load(open(cfg))["provider"]["neuraldeep"]["options"]["apiKey"]
base=os.environ.get("NEURALDEEP_BASE_URL","https://api.neuraldeep.ru/v1")
body=json.dumps({"model":sys.argv[1],"messages":[{"role":"user","content":"ping"}],"max_tokens":1}).encode()
req=urllib.request.Request(base.rstrip("/")+"/chat/completions",data=body,
    headers={"Content-Type":"application/json","Authorization":"Bearer "+key})
try:
    urllib.request.urlopen(req,timeout=60); print("OK")
except urllib.error.HTTPError as e:
    if e.code==429:
        ra=e.headers.get("Retry-After")
        print("429", ra or "")
    else:
        print("ERR", e.code)
except Exception as e:
    print("ERR", str(e)[:60])
EOF
}
echo "--- preflight $COND"
for i in $(seq 1 120); do
  st=$(cloud_ok)
  case "$st" in
    OK) echo "preflight OK"; break ;;
    429*) wait=${st#429 }; wait=${wait:-300}
          echo "preflight 429, sleep ${wait}s ($(date +%FT%T))"; sleep "$wait" ;;
    *)   echo "preflight $st, sleep 60s"; sleep 60 ;;
  esac
done
for f in $FIXTURES; do
  for k in $(seq 1 "$REPS"); do
    R=runs/$COND/$f; mkdir -p "$R"
    [ -s "$R/rep$k.md" ] && { echo "skip $COND/$f rep$k"; continue; }
    s=$(date +%s)
    python3 ../../tools/local_translate.py en ru "$GLOS" < corpus/$f.md > "$R/rep$k.md" 2> "$R/rep$k.log"
    e=$?; echo "$(date +%FT%T) $COND $f rep$k exit=$e wall=$(( $(date +%s)-s ))s" >> runs/runlog.txt
    grep -q "model=$MODEL" "$R/rep$k.log" || echo "MODEL-MISMATCH $COND $f rep$k expected=$MODEL" >> runs/runlog.txt
    if grep -q '\[retry\]\|\[FAIL\]' "$R/rep$k.log"; then
      echo "DEGRADED $COND $f rep$k (retry/FAIL present)" >> runs/runlog.txt
    fi
    sleep 2
  done
done
echo DONE $COND >> runs/runlog.txt
