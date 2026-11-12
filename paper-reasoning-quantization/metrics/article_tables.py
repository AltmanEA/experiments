#!/usr/bin/env python3
"""P-003: combine defect metrics (D1-D7) and MQM scores into paper tables.

Output: results/article_tables.md

Reads results/defects.csv, results/judge_absolute.csv, results/judge_effects.csv.
Run order: aggregate.py -> judge_batch.py --aggregate -> judge_effects.py -> this.

Usage: article_tables.py [--boot 20000]
"""
import argparse, csv, random, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

# order as they appear in the paper (grouped by contrast)
CONDS = [
    ("C1_cloud_bf16_think_off", "C1 cloud bf16, off"),
    ("C2_cloud_bf16_think_on", "C2 cloud bf16, on (raw)"),
    ("C2_cloud_bf16_think_on_clean", "C2c cloud bf16, on (clean)"),
    ("K0_cloud_no_glossary", "K0 cloud, no glossary"),
    ("C3_local_fp8_think_off", "C3 FP8, off"),
    ("C4_local_fp8_think_on", "C4 FP8, on"),
    ("C5_local_nvfp4_think_off", "C5 NVFP4, off"),
    ("C6_local_nvfp4_think_on", "C6 NVFP4, on"),
]
DEFECTS = [
    ("code_missing", "D3 code"),
    ("num_lost", "D4 num"),
    ("term_missing_nc", "D5nc term"),
    ("echo", "D6 echo"),
    ("contam_nc", "D7nc contr"),
]


def boot_ci(vals, n=20000, seed=11):
    rnd = random.Random(seed)
    ms = sorted(statistics.mean(rnd.choices(vals, k=len(vals))) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=20000)
    a = ap.parse_args()

    defects = defaultdict(lambda: defaultdict(list))
    with open(RES / "defects.csv") as fh:
        for r in csv.DictReader(fh):
            for k, _ in DEFECTS:
                defects[r["condition"]][k].append(float(r[k]))

    mqm, ncrit = defaultdict(list), defaultdict(list)
    with open(RES / "judge_absolute.csv") as fh:
        for r in csv.DictReader(fh):
            mqm[r["condition"]].append(float(r["score"]))
            ncrit[r["condition"]].append(float(r["n_critical"]))

    lines = ["## Table 3. Condition quality: defects (per run) and MQM", "",
             "| condition | " + " | ".join(lbl for _, lbl in DEFECTS) +
             " | MQM mean | 95% CI | crit/run | n |",
             "|---" * (len(DEFECTS) + 5) + "|"]
    for cond, label in CONDS:
        cells = []
        for k, _ in DEFECTS:
            v = defects[cond][k]
            cells.append(f"{statistics.mean(v):.2f}" if v else "—")
        sc = mqm.get(cond, [])
        if sc:
            lo, hi = boot_ci(sc, a.boot)
            lines.append(f"| {label} | " + " | ".join(cells) +
                         f" | **{statistics.mean(sc):.1f}** | {lo:.1f}–{hi:.1f} | "
                         f"{statistics.mean(ncrit[cond]):.2f} | {len(sc)} |")
        else:
            lines.append(f"| {label} | " + " | ".join(cells) + " | — | — | — | 0 |")

    eff = []
    with open(RES / "judge_effects.csv") as fh:
        for r in csv.DictReader(fh):
            if r["judge"] == "(mean of judges)":
                eff.append(r)
    if eff:
        lines += ["", "## Table 4. Paired MQM effects (21 fixture x rep pairs, judges averaged)", "",
                  "| contrast | Δ MQM | 95% CI | W/T/L | n |", "|---|---|---|---|---|"]
        for r in eff:
            lines.append(f"| {r['contrast']} | {float(r['delta_mean']):+.1f} | "
                         f"{float(r['ci_low']):+.1f} – {float(r['ci_high']):+.1f} | "
                         f"{r['win']}/{r['tie']}/{r['loss']} | {r['n']} |")

    (RES / "article_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\nwrote results/article_tables.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
