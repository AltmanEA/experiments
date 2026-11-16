#!/usr/bin/env bash
# Rebuild every derived result artifact from the raw runs/ and judge/ trees, in the one
# order that reproduces results/ exactly. Nothing here calls the cloud or the GPU: it is
# all local computation over committed artifacts.
#
#   bash metrics/rebuild_all.sh            # rebuild everything + MANIFEST
#   bash metrics/rebuild_all.sh --figures  # also matplotlib figures (needs .venv-analysis)
#
# Design notes:
#   * stdlib scripts run under system python3 (vLLM venv: numpy only, no scipy);
#     anything importing scipy/matplotlib/sacrebleu runs under .venv-analysis/bin/python.
#   * Defect CSVs are regenerated per domain with the same --out-prefix used originally,
#     so condition keys and schemas match what judge_effects/stats_tests expect.
#   * The script is idempotent: running it twice on an unchanged tree yields the same
#     bytes (bootstrap seeds are fixed at 20000 in the scripts themselves).
set -euo pipefail
cd "$(dirname "$0")/.."

PYV=${PYV:-.venv-analysis/bin/python}
[ -x "$PYV" ] || PYV=python3
DO_FIGS=0
[ "${1:-}" = "--figures" ] && DO_FIGS=1

step() { echo "== $*"; }

# ── defect metrics (per domain; original --out-prefix values) ──────────────────────
step "defects: council (defects.csv)"
python3 metrics/aggregate.py >/dev/null
step "defects: FP8 temperature grid (defects_fp8.csv)"
python3 metrics/aggregate.py \
  --conditions FP8_T00_local_fp8_t00_think_off FP8_T00_local_fp8_t00_think_on \
               FP8_T08_local_fp8_t08_think_off FP8_T08_local_fp8_t08_think_on \
  --out-prefix _fp8 >/dev/null
step "defects: FreeBSD (defects_freebsd.csv)"
python3 metrics/aggregate.py \
  --fixtures F1_config F2_security F3_disks F4_network-servers F5_firewalls \
  --corpus-dir corpus/freebsd-ru/source \
  --conditions F_C5_local_nvfp4_think_off F_C6_local_nvfp4_think_on \
               F_T00_local_nvfp4_t00_think_off F_T00_local_nvfp4_t00_think_on \
  --out-prefix _freebsd >/dev/null
step "defects: P-008 cloud FP8 (defects_p008.csv)"
GLOSS=corpus/glossary_council_2026-11-11.md python3 metrics/aggregate.py \
  --conditions P8_cloud_fp8_think_off --out-prefix _p008 >/dev/null

# ── judge CSVs (from judge/<mode>/*.json) ──────────────────────────────────────────
step "judge CSV: absolute (council+fp8+p008)"
python3 metrics/judge_batch.py --mode absolute --aggregate >/dev/null
step "judge CSV: absolute (freebsd)"
python3 metrics/judge_batch.py --mode absolute --tag _freebsd --aggregate >/dev/null
step "judge CSV: pairwise (all presentation orders)"
python3 metrics/judge_batch.py --mode pairwise --aggregate >/dev/null

# ── core18 subset: the 18 conditions that the judge-agreement decision was made on ──
step "judge CSV: core18 subset"
python3 - <<'PYEOF'
import csv
CORE = {"C1_cloud_bf16_think_off","C2_cloud_bf16_think_on","C2_cloud_bf16_think_on_clean",
        "C3_local_fp8_think_off","C4_local_fp8_think_on","C5_local_nvfp4_think_off",
        "C6_local_nvfp4_think_on","K0_cloud_no_glossary",
        "T00_local_nvfp4_t00_think_off","T00_local_nvfp4_t00_think_on",
        "T04_local_nvfp4_t04_think_off","T04_local_nvfp4_t04_think_on",
        "T06_local_nvfp4_t06_think_off","T06_local_nvfp4_t06_think_on",
        "T08_local_nvfp4_t08_think_off","T08_local_nvfp4_t08_think_on",
        "T10_local_nvfp4_t10_think_off","T10_local_nvfp4_t10_think_on"}
src = "results/judge_absolute.csv"
rows = [r for r in csv.DictReader(open(src)) if r["condition"] in CORE]
with open("results/judge_absolute_core18.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"core18: {len(rows)} rows")
PYEOF

# ── effects / stats / reports ──────────────────────────────────────────────────────
step "paired effects: council (all temperature) + domains"
python3 metrics/judge_effects.py --domain council --all-temperature >/dev/null
python3 metrics/judge_effects.py --domain freebsd >/dev/null
python3 metrics/judge_effects.py --domain fp8 >/dev/null
python3 metrics/judge_effects.py --domain p008 >/dev/null

step "statistical tests: 4 domains (Wilcoxon + Holm, E-008 noise gate)"
"$PYV" metrics/stats_tests.py --domain council      >/dev/null
"$PYV" metrics/stats_tests.py --domain freebsd      >/dev/null
"$PYV" metrics/stats_tests.py --domain fp8          >/dev/null
"$PYV" metrics/stats_tests.py --domain p008         >/dev/null

step "inter-judge agreement: full set + core18"
"$PYV" metrics/judge_agreement.py --out-prefix results/judge_agreement >/dev/null
"$PYV" metrics/judge_agreement.py --csv results/judge_absolute_core18.csv \
      --out-prefix results/judge_agreement_core18 >/dev/null

step "chrF vs official RU (FreeBSD)"
"$PYV" metrics/chrf.py --conditions F_C5_local_nvfp4_think_off F_C6_local_nvfp4_think_on \
      F_T00_local_nvfp4_t00_think_off F_T00_local_nvfp4_t00_think_on >/dev/null

step "pairwise report (main + position control + tie probe + verbosity)"
"$PYV" metrics/pairwise_report.py >/dev/null

step "article tables (Tables 3-7)"
"$PYV" metrics/article_tables.py >/dev/null

if [ "$DO_FIGS" = "1" ]; then
  step "figures (matplotlib, .venv-analysis)"
  "$PYV" metrics/make_figs.py >/dev/null
  "$PYV" metrics/make_figs_domains.py >/dev/null
fi

# ── provenance ─────────────────────────────────────────────────────────────────────
step "manifest + versions"
( cd results && sha256sum *.csv *.md figs/*.png 2>/dev/null > MANIFEST.sha256 )
{
  echo "# Версии окружения анализа"
  echo
  echo "Пересобрано: $(date -Is)  ·  host=$(hostname)"
  echo
  echo '```'
  "$PYV" -c "import sys; print('python', sys.version.split()[0])"
  "$PYV" -m pip freeze 2>/dev/null | grep -Ei '^(scipy|matplotlib|sacrebleu|numpy)==' || \
    "$PYV" -c "import scipy,matplotlib,sacrebleu,numpy as n;print(f'scipy=={scipy.__version__}');print(f'matplotlib=={matplotlib.__version__}');print(f'sacrebleu=={sacrebleu.__version__}');print(f'numpy=={n.__version__}')"
  echo '```'
  echo
  echo "Bootstrap seed во всех скриптах зафиксирован (20 000). Статистика: Wilcoxon + Holm,"
  echo "порог эффекта — 95-й перцентиль внутриконфигурного разброса (E-008)."
} > results/VERSIONS.md

echo "== done. results/MANIFEST.sha256 + results/VERSIONS.md written."
