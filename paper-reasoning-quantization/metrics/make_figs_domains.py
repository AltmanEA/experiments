#!/usr/bin/env python3
"""Paper figures for the domains added after P-003b: FP8 grid (P-006), FreeBSD (P-005),
placement/quantization (P-008). Complements make_figs.py (fig1-5, Council NVFP4) and
reuses its style and bootstrap protocol.

  fig6_fp8_curve.png               MQM vs T on FP8 (0.0/0.2/0.8) x thinking, NVFP4 dashed
  fig7_thinking_deficit_domains.png thinking deficit per quantisation and domain —
                                   shows the FreeBSD sign flip (boundary condition)
  fig8_placement_quantization.png  P-008 contrasts vs the E-008 noise threshold
  fig9_d3_by_domain.png            contract-token corruption D3 across domains

Usage: make_figs_domains.py [--boot 20000]
Runs under .venv-analysis (matplotlib); reads only results/*.csv.
"""
import argparse, csv, random, statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
FIGS = RES / "figs"

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 150, "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.3})

FP8_ROWS = [("0.0", "FP8_T00_local_fp8_t00_think_off", "FP8_T00_local_fp8_t00_think_on"),
            ("0.2", "C3_local_fp8_think_off", "C4_local_fp8_think_on"),
            ("0.8", "FP8_T08_local_fp8_t08_think_off", "FP8_T08_local_fp8_t08_think_on")]
NVFP4_ROWS = [("0.0", "T00_local_nvfp4_t00_think_off", "T00_local_nvfp4_t00_think_on"),
              ("0.2", "C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on"),
              ("0.4", "T04_local_nvfp4_t04_think_off", "T04_local_nvfp4_t04_think_on"),
              ("0.6", "T06_local_nvfp4_t06_think_off", "T06_local_nvfp4_t06_think_on"),
              ("0.8", "T08_local_nvfp4_t08_think_off", "T08_local_nvfp4_t08_think_on"),
              ("1.0", "T10_local_nvfp4_t10_think_off", "T10_local_nvfp4_t10_think_on")]


def boot_ci(vals, n=20000, seed=11):
    rnd = random.Random(seed)
    ms = sorted(statistics.mean(rnd.choices(vals, k=len(vals))) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def load_mqm():
    mqm = defaultdict(list)
    with open(RES / "judge_absolute.csv") as fh:
        for r in csv.DictReader(fh):
            mqm[r["condition"]].append(float(r["score"]))
    with open(RES / "judge_absolute_freebsd.csv") as fh:  # FreeBSD domain lives separately
        for r in csv.DictReader(fh):
            if not r["condition"].startswith("REF"):
                mqm[r["condition"]].append(float(r["score"]))
    return mqm


def load_defects():
    out = {}
    for name in ("defects.csv", "defects_fp8.csv", "defects_freebsd.csv"):
        with open(RES / name) as fh:
            for r in csv.DictReader(fh):
                out.setdefault(r["condition"], []).append(float(r["code_missing"]))
    return out


def load_effects(prefixes):
    """contrast rows (mean-of-judges) from several judge_effects CSVs."""
    rows = []
    for p in prefixes:
        f = RES / p
        if not f.exists():
            continue
        for r in csv.DictReader(open(f)):
            if r["judge"] == "(mean of judges)":
                rows.append(r)
    return rows


def err(ax, xs, ys, los, his, marker="o", **kw):
    """Errorbar with asymmetric bootstrap CIs; fmt built from marker + caller's ls."""
    lo_err = [y - l for y, l in zip(ys, los)]
    hi_err = [h - y for y, h in zip(ys, his)]
    ls = kw.pop("ls", "-")
    ax.errorbar(xs, ys, yerr=[lo_err, hi_err], fmt=ls + marker, capsize=3, **kw)


def fig6_fp8_curve(mqm, boot):
    """MQM vs temperature on FP8; NVFP4 dashed for reference (same judges, same corpus)."""
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    for rows, color, label, ls in ((FP8_ROWS, "tab:red", "FP8", "-"),
                                   (NVFP4_ROWS, "tab:blue", "NVFP4", "--")):
        for is_on, marker in ((True, "o"), (False, "s")):
            xs, ys, los, his = [], [], [], []
            for t, off_c, on_c in rows:
                cond = on_c if is_on else off_c
                v = mqm.get(cond)
                if not v:
                    continue
                lo, hi = boot_ci(v, boot)
                xs.append(float(t)); ys.append(statistics.mean(v)); los.append(lo); his.append(hi)
            if not xs:
                continue
            err(ax, xs, ys, los, his, color=color, ls=ls, marker=marker, ms=4.5, lw=1.4,
                label=f"{label} thinking {'on' if is_on else 'off'}")
    ax.set_xlabel("temperature"); ax.set_ylabel("MQM (среднее двух судей)")
    ax.set_title("Разрыв thinking on/off есть на обоих квантах и сужается с ростом T\n"
                 "(Council, замороженный движок; NVFP4 — пунктиром для сопоставления)",
                 fontsize=8.5)
    ax.set_ylim(30, 100); ax.legend(fontsize=7.5, ncol=2, loc="lower right")
    fig.tight_layout(); fig.savefig(FIGS / "fig6_fp8_curve.png"); plt.close(fig)
    return "fig6_fp8_curve.png"


def load_thresholds():
    """contrast -> 95th percentile of within-config repeat spread (E-008 noise gate)."""
    thr = {}
    for name in ("stats_tests.csv", "stats_tests_fp8.csv", "stats_tests_freebsd.csv"):
        f = RES / name
        if not f.exists():
            continue
        for r in csv.DictReader(open(f)):
            if r["level"] == "mqm":
                thr[r["contrast"]] = float(r["thr_p95"])
    return thr


def fig7_deficit_by_domain():
    """The boundary-condition figure: thinking helps where contract tokens are sparse.

    Each row carries its own E-008 threshold (grey segment): an effect counts only if it
    is both Wilcoxon-significant and beyond that threshold. FreeBSD's +7.3/+7.8 is
    significant but *inside* its noise gate — the figure must not imply otherwise.
    """
    rows = load_effects(["judge_effects.csv", "judge_effects_fp8.csv",
                         "judge_effects_freebsd.csv"])
    thr = load_thresholds()
    want = [("thinking ON vs OFF, NVFP4 T=0.0", "NVFP4, T=0 (Council)", "stats"),
            ("thinking ON vs OFF, FP8 T=0.0", "FP8, T=0 (Council)", "stats"),
            ("thinking ON vs OFF, NVFP4 T=0.2", "NVFP4, T=0.2 (Council)", "stats"),
            ("thinking ON vs OFF, FP8 T=0.2", "FP8, T=0.2 (Council)", "stats"),
            ("thinking ON vs OFF, NVFP4 T=0.0 (FreeBSD)", "NVFP4, T=0 (FreeBSD)", "below"),
            ("thinking ON vs OFF, NVFP4 T=0.2 (FreeBSD)", "NVFP4, T=0.2 (FreeBSD)", "below")]
    by = {r["contrast"]: r for r in rows}
    labels, ds, los, his, thrs = [], [], [], [], []
    for key, short, kind in want:
        r = by.get(key)
        if not r:
            continue
        labels.append(short)
        ds.append(float(r["delta_mean"]))
        los.append(float(r["ci_low"])); his.append(float(r["ci_high"]))
        thrs.append(thr.get(key, 0.0))
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    ys = list(range(len(labels)))
    for y, d, lo, hi, t in zip(ys, ds, los, his, thrs):
        # verdict colour: outside the noise gate = effect, inside = not established
        established = t and abs(d) > t
        c = ("tab:red" if d < 0 else "tab:green") if established else "tab:grey"
        ax.plot([-t, t], [y, y], color="black", lw=7, alpha=0.13,
                solid_capstyle="butt", zorder=1)
        ax.errorbar(d, y, xerr=[[d - lo], [hi - d]], fmt="o", color=c, capsize=3,
                    ms=5.5, zorder=3)
    ax.axvline(0, color="k", lw=1, zorder=2)
    ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel("Δ MQM, thinking ON − OFF (среднее судей, 95 % CI)")
    ax.set_title("Council (плотные contract-токены): thinking стоит 20–44 балла;\n"
                 "FreeBSD (токенов нет): +7.3/+7.8 — значимо, но внутри шума", fontsize=8.5)
    import matplotlib.lines as ml
    ax.legend(handles=[ml.Line2D([], [], marker="o", ls="", color="tab:red",
                                 label="за порогом E-008"),
                       ml.Line2D([], [], marker="o", ls="", color="tab:grey",
                                 label="внутри шумового порога"),
                       ml.Line2D([], [], color="black", alpha=0.25, lw=7,
                                 label="± 95-й перцентиль разброса повторов")],
              fontsize=7, loc="lower right")
    fig.tight_layout(); fig.savefig(FIGS / "fig7_thinking_deficit_domains.png")
    plt.close(fig)
    return "fig7_thinking_deficit_domains.png"


def fig8_placement_quantization():
    """P-008: placement and quantization effects, both far below the noise threshold."""
    eff = RES / "judge_effects_p008.csv"
    st = RES / "stats_tests_p008.csv"
    if not eff.exists():
        return None
    rows = [r for r in csv.DictReader(open(eff)) if r["judge"] == "(mean of judges)"]
    thr = {}
    if st.exists():
        for r in csv.DictReader(open(st)):
            if r["level"] == "mqm":
                thr[r["contrast"]] = float(r["thr_p95"])
    labels, ds, los, his = [], [], [], []
    for r in rows:
        labels.append(r["contrast"])
        ds.append(float(r["delta_mean"])); los.append(float(r["ci_low"]))
        his.append(float(r["ci_high"]))
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    ys = range(len(labels))
    for y, d, lo, hi in zip(ys, ds, los, his):
        ax.errorbar(d, y, xerr=[[d - lo], [hi - d]], fmt="o", color="tab:purple",
                    capsize=3, ms=5)
    ax.axvline(0, color="k", lw=1)
    for y in ys:  # per-contrast E-008 threshold, mirrored
        t = thr.get(labels[y], 0)
        if t:
            ax.plot([-t, t], [y, y], color="grey", lw=6, alpha=0.25, solid_capstyle="butt")
    ax.set_yticks(list(ys))
    ax.set_yticklabels(["размещение:\nлокаль vs облако (FP8)",
                        "квантование:\nbf16 vs FP8 (облако)"], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Δ MQM (положительный = второе условие лучше), 95 % CI")
    ax.set_title("P-008: оба эффекта внутри полосы шума повторов (серое)")
    fig.tight_layout(); fig.savefig(FIGS / "fig8_placement_quantization.png")
    plt.close(fig)
    return "fig8_placement_quantization.png"


def fig9_d3_by_domain(defects):
    """D3 contract corruption: Council on/off pairs vs FreeBSD (all zeros)."""
    groups = [("Council NVFP4 T0 off", "T00_local_nvfp4_t00_think_off"),
              ("Council NVFP4 T0 on", "T00_local_nvfp4_t00_think_on"),
              ("Council FP8 T0 off", "FP8_T00_local_fp8_t00_think_off"),
              ("Council FP8 T0 on", "FP8_T00_local_fp8_t00_think_on"),
              ("FreeBSD T0 off", "F_T00_local_nvfp4_t00_think_off"),
              ("FreeBSD T0 on", "F_T00_local_nvfp4_t00_think_on")]
    labels, means, los, his = [], [], [], []
    for short, cond in groups:
        v = defects.get(cond)
        if not v:
            continue
        labels.append(short)
        means.append(statistics.mean(v))
        los.append(boot_ci(v)[0]); his.append(boot_ci(v)[1])
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    xs = range(len(labels))
    colors = ["tab:green" if "off" in l else "tab:red" for l in labels]
    for x, m, lo, hi, c in zip(xs, means, los, his, colors):
        ax.errorbar(x, m, yerr=[[m - lo], [hi - m]], fmt="o", color=c, capsize=3, ms=5)
    ax.set_xticks(list(xs)); ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=7.5)
    ax.set_ylabel("D3: испорченных contract-токенов на прогон")
    ax.set_title("Та же модель и тот же режим thinking:\n"
                 "порче нужны contract-токены, которые можно испортить")
    fig.tight_layout(); fig.savefig(FIGS / "fig9_d3_by_domain.png"); plt.close(fig)
    return "fig9_d3_by_domain.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=20000)
    a = ap.parse_args()
    FIGS.mkdir(exist_ok=True)
    mqm = load_mqm()
    made = [fig6_fp8_curve(mqm, a.boot),
            fig7_deficit_by_domain(),
            fig8_placement_quantization(),
            fig9_d3_by_domain(load_defects())]
    made = [m for m in made if m]
    print("wrote " + ", ".join(f"results/figs/{m}" for m in made))


if __name__ == "__main__":
    main()
