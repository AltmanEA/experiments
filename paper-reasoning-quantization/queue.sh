#!/usr/bin/env bash
# Serialized queue for remaining paper runs: one provider at a time, no parallelism.
# Local models one at a time (operator rule); cloud stream runs strictly alone.
set -u
cd "$(dirname "$0")"
LOG=runs/queue.log
echo "NOTE: cloud phase requires CLOUD_ALLOWED=1 (operator approval)."
echo "=== queue start $(date +%FT%T)" >> "$LOG"

echo "--- C2 cloud bf16 thinking (7 fixtures x3)" >> "$LOG"
CLOUD_ALLOWED=${CLOUD_ALLOWED:-0} bash run_cloud.sh C2_cloud_bf16_think_on qwen3.6-35b-a3b >> "$LOG" 2>&1
echo "--- pause 60s (provider cooldown)" >> "$LOG"; sleep 60

echo "--- K0 cloud no-glossary (resume)" >> "$LOG"
GLOSS=corpus/empty_glossary.md CLOUD_ALLOWED=${CLOUD_ALLOWED:-0} bash run_cloud.sh K0_cloud_no_glossary qwen3.6-35b-a3b-noreason >> "$LOG" 2>&1
echo "--- pause 60s" >> "$LOG"; sleep 60

echo "--- C6 local NVFP4 thinking (resume)" >> "$LOG"
FIXTURES="S1 S2 S3 S4 S5 S6 S7" REPS=3 bash run_local.sh C6_local_nvfp4_think_on true >> "$LOG" 2>&1

echo "=== queue done $(date +%FT%T)" >> "$LOG"
