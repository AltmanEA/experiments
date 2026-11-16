#!/usr/bin/env python3
"""P-003: combine defect metrics (D1-D7) and MQM scores into paper tables.

Output: results/article_tables.md

Reads results/defects.csv, results/judge_absolute.csv, results/judge_effects.csv.
Run order: aggregate.py -> judge_batch.py --aggregate -> judge_effects.py -> this.

Tables: 3 = condition quality (main plan + P-004 temperature grid);
4 = paired MQM effects; 5 = temperature sub-table (MQM, repeat noise, D3, wall).

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
    ("C5_local_nvfp4_think_off", "C5 NVFP4, off (T=0.2)"),
    ("C6_local_nvfp4_think_on", "C6 NVFP4, on (T=0.2)"),
]
# P-003a: temperature grid on NVFP4 (0.2 = C5/C6 above, not repeated here)
T_CONDS = [
    ("T00_local_nvfp4_t00_think_off", "T00 NVFP4, off"), ("T00_local_nvfp4_t00_think_on", "T00 NVFP4, on"),
    ("T04_local_nvfp4_t04_think_off", "T04 NVFP4, off"), ("T04_local_nvfp4_t04_think_on", "T04 NVFP4, on"),
    ("T06_local_nvfp4_t06_think_off", "T06 NVFP4, off"), ("T06_local_nvfp4_t06_think_on", "T06 NVFP4, on"),
    ("T08_local_nvfp4_t08_think_off", "T08 NVFP4, off"), ("T08_local_nvfp4_t08_think_on", "T08 NVFP4, on"),
    ("T10_local_nvfp4_t10_think_off", "T10 NVFP4, off"), ("T10_local_nvfp4_t10_think_on", "T10 NVFP4, on"),
]
DEFECTS = [
    ("code_missing", "D3 code"),
    ("num_lost", "D4 num"),
    ("term_missing_nc", "D5nc term"),
    ("echo", "D6 echo"),
    ("contam_nc", "D7nc contr"),
]

# temperature sub-table: T -> (off condition, on condition); 0.2 reuses C5/C6
T_ROWS = [("0.0", "T00_local_nvfp4_t00_think_off", "T00_local_nvfp4_t00_think_on"),
          ("0.2", "C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on"),
          ("0.4", "T04_local_nvfp4_t04_think_off", "T04_local_nvfp4_t04_think_on"),
          ("0.6", "T06_local_nvfp4_t06_think_off", "T06_local_nvfp4_t06_think_on"),
          ("0.8", "T08_local_nvfp4_t08_think_off", "T08_local_nvfp4_t08_think_on"),
          ("1.0", "T10_local_nvfp4_t10_think_off", "T10_local_nvfp4_t10_think_on")]


def boot_ci(vals, n=20000, seed=11):
    rnd = random.Random(seed)
    ms = sorted(statistics.mean(rnd.choices(vals, k=len(vals))) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def repeat_noise(scores):
    """Per-fixture spread of MQM across repeats.

    Mixed = sd over all judge x rep scores (P-004 columns in STATUS.md);
    gen = sd over per-fixture judge-averaged scores, i.e. generation+server noise
    with judge noise partially cancelled. Both averaged over fixtures.
    """
    mixed, gen = [], []
    for by_rep in scores.values():
        vals = [v for vs in by_rep.values() for v in vs]
        if len(vals) > 1:
            mixed.append(statistics.stdev(vals))
        means = [statistics.mean(vs) for vs in by_rep.values() if vs]
        if len(means) > 1:
            gen.append(statistics.stdev(means))
    f = lambda xs: (statistics.mean(xs) if xs else float("nan"))
    return f(mixed), f(gen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=20000)
    a = ap.parse_args()

    defects = defaultdict(lambda: defaultdict(list))
    with open(RES / "defects.csv") as fh:
        for r in csv.DictReader(fh):
            for k, _ in DEFECTS:
                defects[r["condition"]][k].append(float(r[k]))
            if r["wall"]:
                defects[r["condition"]]["wall"].append(float(r["wall"]))

    mqm, ncrit = defaultdict(list), defaultdict(list)
    # scores[condition][fixture][rep] = [score per judge]  (for repeat noise)
    scores = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with open(RES / "judge_absolute.csv") as fh:
        for r in csv.DictReader(fh):
            mqm[r["condition"]].append(float(r["score"]))
            ncrit[r["condition"]].append(float(r["n_critical"]))
            scores[r["condition"]][r["fixture"]][r["rep"]].append(float(r["score"]))

    lines = ["## Table 3. Condition quality: defects (per run) and MQM", "",
             "| condition | " + " | ".join(lbl for _, lbl in DEFECTS) +
             " | MQM mean | 95% CI | crit/run | n |",
             "|---" * (len(DEFECTS) + 5) + "|"]
    for cond, label in CONDS + T_CONDS:
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

    # Table 5: temperature grid (NVFP4 local), mean of judges
    lines += ["", "## Table 5. Temperature grid (NVFP4 local, MQM mean of judges)", "",
              "| T | MQM off | noise off (mix/gen) | D3 off | wall off, s | "
              "MQM on | noise on (mix/gen) | D3 on | wall on, s |",
              "|---|---|---|---|---|---|---|---|---|"]
    for t, off, on in T_ROWS:
        cells = [t]
        for cond in (off, on):
            sc = mqm.get(cond, [])
            mx, gn = repeat_noise(scores.get(cond, {}))
            d3 = defects[cond]["code_missing"]
            wall = defects[cond]["wall"]
            cells += [f"{statistics.mean(sc):.1f}" if sc else "—",
                      f"{mx:.1f} / {gn:.1f}",
                      f"{statistics.mean(d3):.2f}" if d3 else "—",
                      f"{statistics.mean(wall):.0f}" if wall else "—"]
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "_noise mix = sd over 3 repeats x 2 judges (mixed generation + judge noise, "
              "as in STATUS.md P-004); noise gen = sd over judge-averaged repeats "
              "(generation/server noise only)._"]

    (RES / "article_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\nwrote results/article_tables.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
