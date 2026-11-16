#!/usr/bin/env python3
"""P-003b: Wilcoxon signed-rank tests + Holm correction + noise thresholds.

Implements PLAN.md §6.3 for every contrast in judge_effects.py (main plan +
P-004 temperature grid) on two levels:
  * MQM  - paired deltas over (fixture, rep) units, judges averaged (same
           pairing/units as judge_effects.py, so fixture difficulty cancels);
  * defects (D3/D4/D5nc/D6/D7nc) - paired deltas over the same units, rows of
           results/defects.csv taken in file order within (condition, fixture)
           = rep 1..3 (aggregate.py writes them sorted).

Test: scipy.stats.wilcoxon, two-sided, zero_method='wilcox'.
Multiplicity: Holm within families:
  mqm/thinking (all thinking ON-vs-OFF contrasts incl. per-T), mqm/quantization,
  mqm/temperature (trends from the T=0 anchor), mqm/other, and one family per
  defect metric across all contrasts.

Noise threshold (E-008): for each contrast, the 95th percentile of the pooled
within-config repeat spread |x_i - x_j| (all rep pairs inside the same
fixture, both conditions of the contrast). An effect is declared only if
p_holm < alpha AND |mean delta| exceeds the threshold. Noise floor = the same
statistic computed for the T=0 (greedy) conditions, plus pure per-metric
repeat sd there.

Output: results/stats_tests.md / stats_tests.csv
Usage: stats_tests.py [--alpha 0.05] [--judge-dir DIR] [--out-prefix NAME]
"""
import argparse, csv, statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from judge_effects import FP8_PAIRS, FREEBSD_PAIRS, MAIN, temperature_pairs, load

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

DEFECT_METRICS = [("code_missing", "D3 code"), ("num_lost", "D4 num"),
                  ("term_missing_nc", "D5nc term"), ("echo", "D6 echo"),
                  ("contam_nc", "D7nc contr")]
FLOOR_CONDS = {"T00_local_nvfp4_t00_think_off": "T00 off",
               "T00_local_nvfp4_t00_think_on": "T00 on"}
# per-domain overrides (see --domain): contrasts, defects CSV, noise floors
DOMAINS = {
    "council": {"pairs": None, "defects": "defects.csv", "floors": FLOOR_CONDS},
    "freebsd": {"pairs": FREEBSD_PAIRS, "defects": "defects_freebsd.csv",
                "floors": {"F_T00_local_nvfp4_t00_think_off": "F T00 off",
                           "F_T00_local_nvfp4_t00_think_on": "F T00 on"}},
    "fp8": {"pairs": FP8_PAIRS, "defects": "defects_fp8.csv",
            "floors": {"FP8_T00_local_fp8_t00_think_off": "FP8 T00 off",
                       "FP8_T00_local_fp8_t00_think_on": "FP8 T00 on"}},
}


def family(label):
    if "thinking ON vs OFF" in label:
        return "thinking"
    if "vs FP8" in label or "vs cloud bf16" in label:
        return "quantization"
    if "vs T=0 anchor" in label or "vs T=0.2" in label:
        return "temperature"
    return "other"


def contrast_list(domain="council"):
    """Contrasts for the domain, deduplicated on the condition pair (C5:C6 repeats
    as 'T=0.2'); the per-T label wins."""
    pairs = DOMAINS[domain]["pairs"]
    if pairs is None:
        pairs = MAIN + temperature_pairs()
    by_key = {}
    for ca, cb, label in pairs:
        by_key[(ca, cb)] = label
    out = [(ca, cb, label) for (ca, cb), label in by_key.items()]
    order = {"thinking": 0, "quantization": 1, "temperature": 2, "other": 3}
    out.sort(key=lambda t: (order[family(t[2])], t[2]))
    return out


def holm(ps):
    """Holm step-down adjustment; ps: list of p, returns adjusted list."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    m = len(order)
    adj = [float("nan")] * len(ps)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * ps[idx]))
        adj[idx] = running
    return adj


def wilcoxon(deltas):
    if not deltas or all(d == 0 for d in deltas):
        return float("nan"), float("nan"), 0
    nz = sum(1 for d in deltas if d != 0)
    try:
        res = stats.wilcoxon(deltas, alternative="two-sided", zero_method="wilcox")
        return float(res.statistic), float(res.pvalue), nz
    except ValueError:
        return float("nan"), float("nan"), nz


def rep_absdiffs(vals_by_fix):
    """All |rep_i - rep_j| within each fixture (within-config repeat spread)."""
    diffs = []
    for xs in vals_by_fix.values():
        for i in range(len(xs)):
            for j in range(i + 1, len(xs)):
                diffs.append(abs(xs[i] - xs[j]))
    return diffs


def p95(diffs):
    return float(np.percentile(diffs, 95)) if diffs else float("nan")


def load_mqm(judge_dir):
    sc = load(judge_dir)
    judges = sorted({k[3] for k in sc})
    unit = {}
    for key in sorted({k[:3] for k in sc}):
        vals = [v for j in judges for v in sc.get(key + (j,), [])]
        if vals:
            unit[key] = statistics.mean(vals)
    return unit


def load_defects(defects_csv="defects.csv"):
    per = defaultdict(dict)  # metric -> {(cond,fix,rep): value}
    with open(RES / defects_csv) as fh:
        rows = list(csv.DictReader(fh))
    seen = defaultdict(int)
    for r in rows:
        key = (r["condition"], r["fixture"])
        seen[key] += 1
        for k, _ in DEFECT_METRICS:
            per[k][(r["condition"], r["fixture"], seen[key])] = float(r[k])
    return per


def by_cond_fix(data):
    out = defaultdict(lambda: defaultdict(list))
    for (cond, fix, _rep), v in data.items():
        out[cond][fix].append(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--judge-dir", default=None,
                    help="default: judge/absolute (council/fp8), "
                         "judge_freebsd/absolute (freebsd)")
    ap.add_argument("--out-prefix", default=None)
    ap.add_argument("--domain", choices=["council", "freebsd", "fp8"], default="council")
    a = ap.parse_args()
    if a.judge_dir is None:
        a.judge_dir = "judge_freebsd/absolute" if a.domain == "freebsd" else "judge/absolute"
    if a.out_prefix is None:
        a.out_prefix = "stats_tests" if a.domain == "council" else f"stats_tests_{a.domain}"

    mqm = load_mqm(a.judge_dir)
    defects = load_defects(DOMAINS[a.domain]["defects"])
    contrasts = contrast_list(a.domain)

    def unit_delta(data_a, data_b):
        """Paired deltas keyed by (fixture, rep), condition stripped."""
        pa = {(c[1], c[2]): v for c, v in data_a.items()}
        pb = {(c[1], c[2]): v for c, v in data_b.items()}
        keys = sorted(set(pa) & set(pb))
        return keys, [pb[k] - pa[k] for k in keys]

    # ---- MQM level -------------------------------------------------------
    mqm_cf = by_cond_fix(mqm)
    rows = []
    for ca, cb, label in contrasts:
        da = {k: v for k, v in mqm.items() if k[0] == ca}
        db = {k: v for k, v in mqm.items() if k[0] == cb}
        _, deltas = unit_delta(da, db)
        if not deltas:
            continue
        w, p, nz = wilcoxon(deltas)
        diffs = rep_absdiffs(mqm_cf[ca]) + rep_absdiffs(mqm_cf[cb])
        rows.append({"level": "mqm", "family": family(label), "contrast": label,
                     "metric": "MQM", "n": len(deltas), "nonzero": nz,
                     "delta": statistics.mean(deltas), "W": w, "p_raw": p,
                     "thr_p95": p95(diffs)})

    # ---- defect level ----------------------------------------------------
    for mk, mlabel in DEFECT_METRICS:
        data = defects[mk]
        cf = by_cond_fix(data)
        for ca, cb, label in contrasts:
            da = {k: v for k, v in data.items() if k[0] == ca}
            db = {k: v for k, v in data.items() if k[0] == cb}
            _, deltas = unit_delta(da, db)
            if not deltas or all(d == 0 for d in deltas):
                continue
            w, p, nz = wilcoxon(deltas)
            diffs = rep_absdiffs(cf[ca]) + rep_absdiffs(cf[cb])
            rows.append({"level": "defect", "family": f"defect/{mk}",
                         "contrast": label, "metric": mlabel,
                         "n": len(deltas), "nonzero": nz,
                         "delta": statistics.mean(deltas), "W": w, "p_raw": p,
                         "thr_p95": p95(diffs)})

    # ---- Holm per family --------------------------------------------------
    fams = defaultdict(list)
    for i, r in enumerate(rows):
        fams[r["family"]].append(i)
    for idxs in fams.values():
        adj = holm([rows[i]["p_raw"] for i in idxs])
        for i, pa in zip(idxs, adj):
            rows[i]["p_holm"] = pa
    for r in rows:
        r["sig_test"] = r["p_holm"] < a.alpha
        r["sig_vs_noise"] = (r["p_holm"] < a.alpha
                             and abs(r["delta"]) > r["thr_p95"])

    # ---- noise floors (T=0 conditions) ------------------------------------
    def cf_all(data, cond):
        out = defaultdict(list)
        for (c, fix, _r), v in data.items():
            if c == cond:
                out[fix].append(v)
        return out.values()

    floors = []
    for cond, clabel in DOMAINS[a.domain]["floors"].items():
        d = rep_absdiffs(mqm_cf[cond])
        sd_mix = [statistics.stdev(xs) for xs in mqm_cf[cond].values() if len(xs) > 1]
        per_metric = {}
        for mk, mlabel in DEFECT_METRICS:
            sds = [statistics.stdev(xs) for xs in cf_all(defects[mk], cond) if len(xs) > 1]
            per_metric[mlabel] = statistics.mean(sds) if sds else float("nan")
        floors.append((clabel, p95(d), statistics.mean(sd_mix), per_metric))

    # ---- output ------------------------------------------------------------
    fmt_p = lambda p: "n/a" if np.isnan(p) else ("<0.0001" if p < 1e-4 else f"{p:.4f}")
    lines = [f"# Statistical tests (P-003b): Wilcoxon signed-rank + Holm, alpha={a.alpha}",
             "",
             "Units: (fixture, rep), judges averaged; Holm within each family.",
             "\"effect\" = p_holm < alpha AND |Δ| > pooled 95th percentile of",
             "within-config repeat spread (E-008 threshold).", ""]
    for fam in sorted({r["family"] for r in rows},
                      key=lambda f: (f.startswith("defect"), f)):
        sub = [r for r in rows if r["family"] == fam]
        lines += [f"## Family: {fam} ({len(sub)} tests)", "",
                  "| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for r in sub:
            lines.append(f"| {r['contrast']} | {r['metric']} | {r['n']} | {r['nonzero']} | "
                         f"{r['delta']:+.2f} | {r['W']:.0f} | {fmt_p(r['p_raw'])} | "
                         f"{fmt_p(r['p_holm'])} | {r['thr_p95']:.2f} | "
                         f"{'YES' if r['sig_vs_noise'] else 'no'} |")
        lines.append("")

    lines += ["## Noise floor (T=0, greedy; server non-determinism)", "",
              "| cond | MQM p95 of |Δrep| | MQM sd (mixed) | " +
              " | ".join(ml for _, ml in DEFECT_METRICS) + " (pure repeat sd) |",
              "|---|---|---|" + "---|" * len(DEFECT_METRICS)]
    for clabel, p95v, sdm, per_metric in floors:
        lines.append(f"| {clabel} | {p95v:.2f} | {sdm:.2f} | " +
                     " | ".join(f"{per_metric[ml]:.2f}" for _, ml in DEFECT_METRICS) + " |")
    lines += ["", "_MQM sd (mixed) here is sd over the 3 repeat means (judges averaged); "
              "the STATUS.md column 'noise' is sd over all 6 scores (3 reps × 2 judges)._"]

    (RES / f"{a.out_prefix}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    keys = ["level", "family", "contrast", "metric", "n", "nonzero", "delta", "W",
            "p_raw", "p_holm", "thr_p95", "sig_test", "sig_vs_noise"]
    with open(RES / f"{a.out_prefix}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(r[k], 6) if isinstance(r[k], float) else r[k])
                        for k in keys})
    print("\n".join(lines))
    print(f"\nwrote results/{a.out_prefix}.md/.csv ({len(rows)} tests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
