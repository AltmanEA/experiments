#!/usr/bin/env python3
"""Inter-judge agreement for absolute MQM scores (P-003c).

Pairs the two judges on identical (condition, fixture, rep) units and reports:
  - Pearson / Spearman correlation of raw scores;
  - mean |Δ| and its distribution (median, p90);
  - quadratic-weighted Cohen's kappa on score bands (A >=95, B 85-94, C 70-84,
    D 50-69, E <50) — band cuts follow the MQM severity weights (25/10/2);
  - systematic bias (mean signed Δ = primary - secondary);
  - breakdowns by condition and by fixture;
  - decision data for «mean vs consensus»: how condition ranking (Spearman
    over condition means) changes between primary-only, secondary-only and
    the two-judge mean.

stdlib + numpy only (runs with the system python too).

Usage:
  python3 metrics/judge_agreement.py                       # council 756 rows
  python3 metrics/judge_agreement.py --csv results/judge_absolute_freebsd.csv
"""
import argparse, csv, itertools, statistics, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BANDS = [(95, 101, "A"), (85, 95, "B"), (70, 85, "C"), (50, 70, "D"), (-1, 50, "E")]


def band(s: int) -> str:
    for lo, hi, name in BANDS:
        if lo <= s < hi:
            return name
    return "E"


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def rankdata(v):
    """Average ranks (ties), numpy-only."""
    v = np.asarray(v, float)
    order = np.argsort(v, kind="stable")
    ranks = np.empty(len(v), float)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return ranks


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))


def weighted_kappa(pairs, categories, weight="quadratic"):
    """Quadratic-weighted Cohen's kappa for ordinal categories."""
    cats = sorted(categories)
    idx = {c: i for i, c in enumerate(cats)}
    n = len(cats)
    O = np.zeros((n, n))
    for a, b in pairs:
        O[idx[a], idx[b]] += 1
    if O.sum() == 0:
        return float("nan")
    O /= O.sum()
    r = O.sum(axis=1)
    c = O.sum(axis=0)
    E = np.outer(r, c)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            W[i, j] = (i - j) ** 2 / (n - 1) ** 2
    num = 1.0 - (W * O).sum() / (W * E).sum()
    return float(num) if (W * E).sum() > 0 else float("nan")


def load_units(csv_path):
    """-> {unit: {judge: score}} keeping only fully-judged units."""
    units = defaultdict(dict)
    with open(csv_path, newline="") as fh:
        for row in csv.DictReader(fh):
            key = (row["condition"], row["fixture"], row["rep"])
            units[key][row["judge"]] = int(row["score"])
    return units


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="results/judge_absolute.csv")
    ap.add_argument("--primary", default="gpt-oss-120b")
    ap.add_argument("--secondary", default="gemma-4-31b")
    ap.add_argument("--out-prefix", default="results/judge_agreement")
    a = ap.parse_args()

    csv_path = Path(a.csv)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    units = load_units(csv_path)
    pairs = [(k, v) for k, v in sorted(units.items())
             if a.primary in v and a.secondary in v]
    if len(pairs) < 3:
        sys.exit(f"need >=2 fully-judged units, got {len(pairs)} (judges: {a.primary}/{a.secondary})")
    dropped = len(units) - len(pairs)

    ks = [k for k, _ in pairs]
    x = np.array([v[a.primary] for _, v in pairs], float)
    y = np.array([v[a.secondary] for _, v in pairs], float)
    d = x - y
    abs_d = np.abs(d)

    r = pearson(x, y)
    rho = spearman(x, y)
    kappa_w = weighted_kappa([(band(int(sx)), band(int(sy))) for sx, sy in zip(x, y)],
                             {b[2] for b in BANDS})

    lines, rows = [], []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit(f"# Inter-judge agreement — {csv_path.name}")
    emit(f"judges: primary={a.primary}, secondary={a.secondary}")
    emit(f"units (cond×fix×rep judged by both): {len(pairs)}; skipped (single-judge): {dropped}")
    emit("")
    emit(f"Pearson r           : {r:.3f}")
    emit(f"Spearman rho        : {rho:.3f}")
    emit(f"weighted kappa (bands): {kappa_w:.3f}")
    emit(f"mean |Δ|            : {abs_d.mean():.2f}  (median {np.median(abs_d):.1f}, p90 {np.percentile(abs_d, 90):.1f}, max {abs_d.max():.0f})")
    emit(f"signed Δ (prim−sec) : mean {d.mean():+.2f}, sd {d.std(ddof=1):.2f}; "
         f"primary higher in {(d > 0).sum()}, equal in {(d == 0).sum()}, lower in {(d < 0).sum()}")
    emit("")

    # ---- breakdown by condition
    emit("## By condition (Δ = primary − secondary)")
    emit("| condition | n | r | mean prim | mean sec | mean Δ | mean |Δ| |")
    emit("|---|---|---|---|---|---|---|")
    by_cond = defaultdict(list)
    for (c, f, k), v in pairs:
        by_cond[c].append(v)
    cond_stats = {}
    for c, vs in sorted(by_cond.items()):
        cx = np.array([v[a.primary] for v in vs], float)
        cy = np.array([v[a.secondary] for v in vs], float)
        cd = cx - cy
        cond_stats[c] = (cx.mean(), cy.mean())
        emit(f"| {c} | {len(vs)} | {pearson(cx, cy):.3f} | {cx.mean():.1f} | {cy.mean():.1f} "
             f"| {cd.mean():+.1f} | {np.abs(cd).mean():.1f} |")
        rows.append({"level": "condition", "group": c, "n": len(vs),
                     "pearson": round(pearson(cx, cy), 3),
                     "mean_primary": round(cx.mean(), 2), "mean_secondary": round(cy.mean(), 2),
                     "mean_signed_delta": round(cd.mean(), 2),
                     "mean_abs_delta": round(np.abs(cd).mean(), 2)})
    emit("")

    # ---- breakdown by fixture
    emit("## By fixture")
    emit("| fixture | n | r | mean Δ | mean |Δ| |")
    emit("|---|---|---|---|---|")
    by_fix = defaultdict(list)
    for (c, f, k), v in pairs:
        by_fix[f].append(v)
    for f, vs in sorted(by_fix.items()):
        fx_ = np.array([v[a.primary] for v in vs], float)
        fy = np.array([v[a.secondary] for v in vs], float)
        fd = fx_ - fy
        emit(f"| {f} | {len(vs)} | {pearson(fx_, fy):.3f} | {fd.mean():+.1f} | {np.abs(fd).mean():.1f} |")
        rows.append({"level": "fixture", "group": f, "n": len(vs),
                     "pearson": round(pearson(fx_, fy), 3),
                     "mean_primary": round(fx_.mean(), 2), "mean_secondary": round(fy.mean(), 2),
                     "mean_signed_delta": round(fd.mean(), 2),
                     "mean_abs_delta": round(np.abs(fd).mean(), 2)})
    emit("")

    # ---- mean vs consensus decision data
    emit("## Среднее vs консенсус (ранжирование условий)")
    conds = sorted(cond_stats)
    mean_rank = {c: m for c, (p, s) in cond_stats.items() for m in [((p + s) / 2)]}
    prim = {c: cond_stats[c][0] for c in conds}
    sec = {c: cond_stats[c][1] for c in conds}

    def ranks(vals):
        order = sorted(conds, key=lambda c: -vals[c])
        return {c: i + 1 for i, c in enumerate(order)}

    r_mean, r_prim, r_sec = ranks(mean_rank), ranks(prim), ranks(sec)
    rho_pm = spearman([r_prim[c] for c in conds], [r_mean[c] for c in conds])
    rho_sm = spearman([r_sec[c] for c in conds], [r_mean[c] for c in conds])
    moved = [c for c in conds if r_prim[c] != r_mean[c] or r_sec[c] != r_mean[c]]
    emit(f"Spearman rank corr vs two-judge mean: primary ρ={rho_pm:.3f}, secondary ρ={rho_sm:.3f} "
         f"(k={len(conds)} conditions)")
    emit(f"conditions whose rank shifts under single-judge scoring: {len(moved)}"
         + (f" — {', '.join(moved)}" if moved else ""))
    emit("")
    emit("| condition | mean of judges | primary only | secondary only | max rank shift |")
    emit("|---|---|---|---|---|")
    for c in sorted(conds, key=lambda c: -mean_rank[c]):
        shift = max(abs(r_prim[c] - r_mean[c]), abs(r_sec[c] - r_mean[c]))
        emit(f"| {c} | {mean_rank[c]:.1f} | {prim[c]:.1f} | {sec[c]:.1f} | {shift} |")

    out_md = ROOT / f"{a.out_prefix}.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    out_csv = ROOT / f"{a.out_prefix}.csv"
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    emit(f"\nwrote {out_md}\nwrote {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
