#!/usr/bin/env python3
"""P-003b: paper figures (matplotlib) into results/figs/.

Five figures (NEXT-EXPERIMENTS.md P-003b):
  fig1_off_curve.png    off-curve MQM vs T with bootstrap CI, T=0.2 outlier marked
  fig2_thinking_deficit.png  thinking ON-vs-OFF MQM deficit per T with CI
  fig3_d3_by_temp.png   D3 code corruption per T, off vs on
  fig4_noise_by_temp.png     repeat noise per T (mixed / generation), off vs on
  fig5_d3_matrix.png    D3 heatmap fixture x condition (defect on S4/S5)

Reads results/judge_absolute.csv, results/defects.csv, results/judge_effects.csv.
Usage: make_figs.py [--boot 20000]
"""
import argparse, csv, random, statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
FIGS = RES / "figs"

# NVFP4 temperature grid: T -> (off condition, on condition); 0.2 = C5/C6
T_ROWS = [("0.0", "T00_local_nvfp4_t00_think_off", "T00_local_nvfp4_t00_think_on"),
          ("0.2", "C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on"),
          ("0.4", "T04_local_nvfp4_t04_think_off", "T04_local_nvfp4_t04_think_on"),
          ("0.6", "T06_local_nvfp4_t06_think_off", "T06_local_nvfp4_t06_think_on"),
          ("0.8", "T08_local_nvfp4_t08_think_off", "T08_local_nvfp4_t08_think_on"),
          ("1.0", "T10_local_nvfp4_t10_think_off", "T10_local_nvfp4_t10_think_on")]

# condition rows for the D3 heatmap (paper order, short labels)
HEAT_CONDS = [
    ("C1_cloud_bf16_think_off", "C1 bf16 off"), ("C2_cloud_bf16_think_on", "C2 bf16 on raw"),
    ("C2_cloud_bf16_think_on_clean", "C2c bf16 on clean"), ("K0_cloud_no_glossary", "K0 no gloss"),
    ("C3_local_fp8_think_off", "C3 FP8 off"), ("C4_local_fp8_think_on", "C4 FP8 on"),
    ("C5_local_nvfp4_think_off", "C5 NVFP4 off .2"), ("C6_local_nvfp4_think_on", "C6 NVFP4 on .2"),
    ("T00_local_nvfp4_t00_think_off", "T00 off"), ("T00_local_nvfp4_t00_think_on", "T00 on"),
    ("T04_local_nvfp4_t04_think_off", "T04 off"), ("T04_local_nvfp4_t04_think_on", "T04 on"),
    ("T06_local_nvfp4_t06_think_off", "T06 off"), ("T06_local_nvfp4_t06_think_on", "T06 on"),
    ("T08_local_nvfp4_t08_think_off", "T08 off"), ("T08_local_nvfp4_t08_think_on", "T08 on"),
    ("T10_local_nvfp4_t10_think_off", "T10 off"), ("T10_local_nvfp4_t10_think_on", "T10 on"),
]
FIXES = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 150, "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.3})


def boot_ci(vals, n=20000, seed=11):
    rnd = random.Random(seed)
    ms = sorted(statistics.mean(rnd.choices(vals, k=len(vals))) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def load_data():
    mqm = defaultdict(list)
    scores = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with open(RES / "judge_absolute.csv") as fh:
        for r in csv.DictReader(fh):
            mqm[r["condition"]].append(float(r["score"]))
            scores[r["condition"]][r["fixture"]][r["rep"]].append(float(r["score"]))
    d3 = defaultdict(lambda: defaultdict(list))  # cond -> fixture -> values
    with open(RES / "defects.csv") as fh:
        for r in csv.DictReader(fh):
            d3[r["condition"]][r["fixture"]].append(float(r["code_missing"]))
    return mqm, scores, d3


def repeat_noise(by_fix):
    """(mixed sd over 6 scores, gen sd over judge-averaged repeats), fixture-mean."""
    mixed, gen = [], []
    for by_rep in by_fix.values():
        vals = [v for vs in by_rep.values() for v in vs]
        if len(vals) > 1:
            mixed.append(statistics.stdev(vals))
        means = [statistics.mean(vs) for vs in by_rep.values() if vs]
        if len(means) > 1:
            gen.append(statistics.stdev(means))
    f = lambda xs: (statistics.mean(xs) if xs else float("nan"))
    return f(mixed), f(gen)


def load_effects():
    """label -> (delta, lo, hi) for mean-of-judges rows of judge_effects.csv."""
    out = {}
    with open(RES / "judge_effects.csv") as fh:
        for r in csv.DictReader(fh):
            if r["judge"] == "(mean of judges)":
                out[r["contrast"]] = (float(r["delta_mean"]), float(r["ci_low"]),
                                      float(r["ci_high"]))
    return out


def err_x(xs, lo, hi):
    return [x - l for x, l in zip(xs, lo)], [h - x for x, h in zip(xs, hi)]


def fig1_off_curve(mqm, boot):
    ts = [float(t) for t, _, _ in T_ROWS]
    means, los, his = [], [], []
    for _, off, _ in T_ROWS:
        sc = mqm[off]
        means.append(statistics.mean(sc))
        lo, hi = boot_ci(sc, boot)
        los.append(lo)
        his.append(hi)
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.errorbar(ts, means, yerr=err_x(means, los, his), marker="o", ms=6,
                capsize=3, color="#1f4e79", label="thinking OFF")
    for x, y in zip(ts, means):
        ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=8)
    ax.annotate("выброс вниз\nпри T=0.2", (0.2, means[1]), xytext=(0.34, means[1] - 13),
                textcoords="data", fontsize=8, color="#a33",
                arrowprops=dict(arrowstyle="->", color="#a33", alpha=0.8))
    ax.axhline(means[0], ls=":", color="#888", lw=1, label=f"якорь T=0 ({means[0]:.1f})")
    ax.set_xlabel("temperature"); ax.set_ylabel("MQM (среднее судей)")
    ax.set_title("NVFP4, thinking OFF: качество vs температура")
    ax.set_xticks(ts); ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout(); fig.savefig(FIGS / "fig1_off_curve.png"); plt.close(fig)


def fig2_thinking_deficit(eff):
    ts, ds, los, his = [], [], [], []
    for t, _, _ in T_ROWS:
        label = f"thinking ON vs OFF, NVFP4 T={t}"
        if label not in eff:
            continue
        d, lo, hi = eff[label]
        ts.append(float(t)); ds.append(d); los.append(lo); his.append(hi)
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.errorbar(ts, ds, yerr=err_x(ds, los, his), marker="s", ms=6,
                capsize=3, color="#a33")
    ax.axhline(0, color="k", lw=1)
    for x, y in zip(ts, ds):
        ax.annotate(f"{y:+.1f}", (x, y), textcoords="offset points", xytext=(0, -14),
                    ha="center", fontsize=8)
    ax.axhspan(-8.4, 8.4, color="#cccccc", alpha=0.45, zorder=0,
               label="шумовой пол ±8.4 (T=0, mix)")
    ax.set_xlabel("temperature"); ax.set_ylabel("Δ MQM (on − off)")
    ax.set_title("Дефицит thinking по температурам (NVFP4, 95 % CI)")
    ax.set_xticks([float(t) for t, _, _ in T_ROWS]); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIGS / "fig2_thinking_deficit.png"); plt.close(fig)


def fig3_d3(d3):
    ts = [float(t) for t, _, _ in T_ROWS]
    off = [statistics.mean([v for xs in d3[c].values() for v in xs]) for _, c, _ in T_ROWS]
    on = [statistics.mean([v for xs in d3[c].values() for v in xs]) for _, _, c in T_ROWS]
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(ts, off, marker="o", color="#1f4e79", label="thinking OFF")
    ax.plot(ts, on, marker="s", color="#a33", label="thinking ON")
    for xs, ys, dy in ((ts, off, 8), (ts, on, -13)):
        for x, y in zip(xs, ys):
            ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, dy),
                        ha="center", fontsize=7.5)
    ax.set_xlabel("temperature"); ax.set_ylabel("D3: потерянных code-фрагментов на прогон")
    ax.set_title("Порча contract-токенов (D3) по температурам, NVFP4")
    ax.set_xticks(ts); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIGS / "fig3_d3_by_temp.png"); plt.close(fig)


def fig4_noise(scores):
    ts = [float(t) for t, _, _ in T_ROWS]
    vals = {k: [] for k in ("mix_off", "gen_off", "mix_on", "gen_on")}
    for t, off, on in T_ROWS:
        for key, cond in (("off", off), ("on", on)):
            mx, gn = repeat_noise(scores[cond])
            vals[f"mix_{key}"].append(mx)
            vals[f"gen_{key}"].append(gn)
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(ts, vals["mix_off"], marker="o", color="#1f4e79", label="off, смешанный (6 оценок)")
    ax.plot(ts, vals["gen_off"], marker="o", ls="--", color="#1f4e79", alpha=0.6,
            label="off, генерация (3 средних)")
    ax.plot(ts, vals["mix_on"], marker="s", color="#a33", label="on, смешанный")
    ax.plot(ts, vals["gen_on"], marker="s", ls="--", color="#a33", alpha=0.6,
            label="on, генерация")
    ax.axhline(8.4, ls=":", color="#888", lw=1, label="шумовой пол сервера (mix, T=0 off)")
    ax.set_xlabel("temperature"); ax.set_ylabel("sd повторов внутри фикстуры (ед. MQM)")
    ax.set_title("Разброс повторов по температурам (NVFP4)")
    ax.set_xticks(ts); ax.legend(fontsize=7.5, loc="lower center", ncol=2)
    fig.tight_layout(); fig.savefig(FIGS / "fig4_noise_by_temp.png"); plt.close(fig)


def fig5_matrix(d3):
    import numpy as np
    grid = [[statistics.mean(d3[c].get(f, [0.0])) for f in FIXES] for c, _ in HEAT_CONDS]
    labels = [lbl for _, lbl in HEAT_CONDS]
    fig, ax = plt.subplots(figsize=(6.4, 6.2))
    im = ax.imshow(np.array(grid), cmap="Reds", vmin=0)
    ax.set_xticks(range(len(FIXES)), FIXES)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    for i in range(len(labels)):
        for j in range(len(FIXES)):
            v = grid[i][j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                    color="white" if v > max(1.0, 0.6 * max(map(max, grid))) else "black")
    ax.grid(False)
    ax.set_title("D3: потерянных code-фрагментов на прогон\n(среднее 3 повторов)", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout(); fig.savefig(FIGS / "fig5_d3_matrix.png"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=20000)
    a = ap.parse_args()
    FIGS.mkdir(exist_ok=True)
    mqm, scores, d3 = load_data()
    eff = load_effects()
    fig1_off_curve(mqm, a.boot)
    fig2_thinking_deficit(eff)
    fig3_d3(d3)
    fig4_noise(scores)
    fig5_matrix(d3)
    names = ["fig1_off_curve", "fig2_thinking_deficit", "fig3_d3_by_temp",
             "fig4_noise_by_temp", "fig5_d3_matrix"]
    print("wrote:", ", ".join(f"results/figs/{n}.png" for n in names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
