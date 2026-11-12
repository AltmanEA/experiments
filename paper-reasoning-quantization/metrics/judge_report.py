#!/usr/bin/env python3
"""Report MQM judge results as paper-ready tables (P-002 / P-003).

Reads judge/absolute/<condition>/<fixture>/rep<k>.<judge>.json and writes
  results/judge_table.md   per condition x judge: mean score, 95% bootstrap CI,
                           defect counts by severity, n;
  results/judge_fixtures.csv per condition x fixture x judge mean score.

Usage: judge_report.py [--judge all|gpt-oss-120b|...] [--boot 4000]
"""
import argparse, csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABEL = {
    "C1_cloud_bf16_think_off": "C1 cloud bf16, off",
    "C2_cloud_bf16_think_on": "C2 cloud bf16, on (raw)",
    "C2_cloud_bf16_think_on_clean": "C2c cloud bf16, on (clean)",
    "K0_cloud_no_glossary": "K0 cloud, no glossary",
    "C3_local_fp8_think_off": "C3 FP8, off",
    "C4_local_fp8_think_on": "C4 FP8, on",
    "C5_local_nvfp4_think_off": "C5 NVFP4, off",
    "C6_local_nvfp4_think_on": "C6 NVFP4, on",
}
ORDER = list(LABEL)

def boot_ci(vals, n=4000, alpha=0.05, seed=17):
    if len(vals) < 2:
        return (float("nan"), float("nan"))
    rnd = random.Random(seed)
    means = [statistics.mean(rnd.choices(vals, k=len(vals))) for _ in range(n)]
    means.sort()
    return means[int(alpha / 2 * n)], means[int((1 - alpha / 2) * n) - 1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="all")
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    recs = []
    for f in sorted((ROOT / "judge" / "absolute").glob("*/*/rep*.json")):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        if d.get("_status") == "fail" or "score" not in d:
            continue
        meta = d.get("_meta", {})
        judge = meta.get("judge", f.name.split(".")[1])
        if a.judge != "all" and judge != a.judge:
            continue
        defs = d.get("defects", [])
        sev = [x.get("severity", "minor") for x in defs]
        recs.append({"cond": f.parent.parent.name, "fix": f.parent.name,
                     "rep": int(f.name.split(".")[0][3:]), "judge": judge,
                     "score": d["score"], "crit": sev.count("critical"),
                     "maj": sev.count("major"), "min": sev.count("minor")})
    if not recs:
        print("no judge results"); return 1

    judges = sorted({r["judge"] for r in recs})
    conds = [c for c in ORDER if any(r["cond"] == c for r in recs)]

    # per condition x judge
    by = defaultdict(list)
    for r in recs:
        by[(r["cond"], r["judge"])].append(r)
    lines = ["| condition | judge | n | MQM mean | 95% CI | critical | major | minor |",
             "|---|---|---|---|---|---|---|---|"]
    for c in conds:
        for j in judges:
            rs = by.get((c, j), [])
            if not rs:
                continue
            sc = [r["score"] for r in rs]
            lo, hi = boot_ci(sc, a.boot)
            lines.append(f"| {LABEL.get(c, c)} | {j} | {len(rs)} | {statistics.mean(sc):.1f} | "
                         f"{lo:.1f}–{hi:.1f} | "
                         f"{statistics.mean(r['crit'] for r in rs):.2f} | "
                         f"{statistics.mean(r['maj'] for r in rs):.2f} | "
                         f"{statistics.mean(r['min'] for r in rs):.2f} |")
    # combined (mean over judges)
    lines += ["", "| condition | n (all judges) | MQM mean | 95% CI |", "|---|---|---|---|"]
    for c in conds:
        sc = [r["score"] for r in recs if r["cond"] == c]
        lo, hi = boot_ci(sc, a.boot)
        lines.append(f"| {LABEL.get(c, c)} | {len(sc)} | {statistics.mean(sc):.1f} | {lo:.1f}–{hi:.1f} |")

    # inter-judge agreement on the same (condition, fixture, rep)
    if len(judges) > 1:
        paired = defaultdict(dict)
        for r in recs:
            paired[(r["cond"], r["fix"], r["rep"])][r["judge"]] = r["score"]
        xs, ys = [], []
        for v in paired.values():
            if len(v) == len(judges):
                xs.append(v[judges[0]]); ys.append(v[judges[1]])
        if len(xs) > 2:
            diff = statistics.mean(abs(a - b) for a, b in zip(xs, ys))
            try:
                corr = statistics.correlation(xs, ys)
            except (AttributeError, statistics.StatisticsError):
                corr = float("nan")
            exact = sum(1 for a, b in zip(xs, ys) if a == b) / len(xs)
            lines += ["", f"Judge agreement ({judges[0]} vs {judges[1]}), n={len(xs)} paired runs: "
                          f"mean |Δscore| = {diff:.1f}, Pearson r = {corr:.2f}, "
                          f"identical score = {100 * exact:.0f}%."]

    # per fixture matrix
    fx = sorted({r["fix"] for r in recs})
    mat = defaultdict(list)
    for r in recs:
        mat[(r["cond"], r["fix"], r["judge"])].append(r["score"])
    out = [["condition", "fixture", "judge", "n", "mean", "sd"]]
    for c in conds:
        for f in fx:
            for j in judges:
                v = mat.get((c, f, j), [])
                if v:
                    out.append([c, f, j, len(v), round(statistics.mean(v), 2),
                                round(statistics.stdev(v), 2) if len(v) > 1 else 0.0])

    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/judge_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(ROOT / "results/judge_fixtures.csv", "w", newline="") as fh:
        csv.writer(fh).writerows(out)
    print("\n".join(lines))
    print(f"\nwrote results/judge_table.md, results/judge_fixtures.csv ({len(recs)} scores)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
