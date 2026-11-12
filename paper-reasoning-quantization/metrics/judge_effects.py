#!/usr/bin/env python3
"""Paired condition effects from MQM absolute scores (P-002).

For each contrast (A -> B) the 21 (fixture, rep) units are paired across
conditions, so fixture difficulty cancels out. Judges are averaged per unit
unless --split-judges is given.

Output: results/judge_effects.md and judge_effects.csv

Usage: judge_effects.py [--boot 20000] [--split-judges]
"""
import argparse, csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [
    ("C3_local_fp8_think_off", "C4_local_fp8_think_on", "thinking ON vs OFF, FP8"),
    ("C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on", "thinking ON vs OFF, NVFP4"),
    ("C1_cloud_bf16_think_off", "K0_cloud_no_glossary", "no glossary vs glossary, cloud"),
    ("C1_cloud_bf16_think_off", "C2_cloud_bf16_think_on_clean", "thinking ON (clean) vs OFF, cloud"),
    ("C2_cloud_bf16_think_on", "C2_cloud_bf16_think_on_clean", "post-processing (clean vs raw)"),
    ("C3_local_fp8_think_off", "C5_local_nvfp4_think_off", "NVFP4 vs FP8, thinking OFF"),
    ("C4_local_fp8_think_on", "C6_local_nvfp4_think_on", "NVFP4 vs FP8, thinking ON"),
    ("C1_cloud_bf16_think_off", "C3_local_fp8_think_off", "FP8 vs cloud bf16, thinking OFF"),
]


def load():
    sc = defaultdict(list)
    for f in (ROOT / "judge" / "absolute").glob("*/*/rep*.json"):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        if d.get("_status") == "fail" or "score" not in d:
            continue
        cond = f.parent.parent.name
        fix = f.parent.name
        rep = int(f.name.split(".")[0][3:])
        judge = f.name.split(".")[1]
        sc[(cond, fix, rep, judge)].append(d["score"])
    return sc


def boot(vals, n=20000, alpha=0.05, seed=11):
    rnd = random.Random(seed)
    ms = sorted(statistics.mean(rnd.choices(vals, k=len(vals))) for _ in range(n))
    return ms[int(alpha / 2 * n)], ms[int((1 - alpha / 2) * n) - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=20000)
    ap.add_argument("--split-judges", action="store_true")
    a = ap.parse_args()

    sc = load()
    judges = sorted({k[3] for k in sc})
    units = sorted({k[1:3] for k in sc})
    rows, lines = [], ["| contrast | judge | n | Δ mean | 95% CI | W/T/L |",
                       "|---|---|---|---|---|---|"]

    for ca, cb, label in PAIRS:
        groups = judges if a.split_judges else ["(mean of judges)"]
        for judge in groups:
            deltas = []
            for fix, rep in units:
                if a.split_judges:
                    va = sc.get((ca, fix, rep, judge), [])
                    vb = sc.get((cb, fix, rep, judge), [])
                else:
                    va = [v for j in judges for v in sc.get((ca, fix, rep, j), [])]
                    vb = [v for j in judges for v in sc.get((cb, fix, rep, j), [])]
                if va and vb:
                    deltas.append(statistics.mean(vb) - statistics.mean(va))
            if not deltas:
                continue
            lo, hi = boot(deltas, a.boot)
            w = sum(1 for d in deltas if d > 0)
            t = sum(1 for d in deltas if d == 0)
            l = sum(1 for d in deltas if d < 0)
            lines.append(f"| {label} | {judge} | {len(deltas)} | {statistics.mean(deltas):+.1f} | "
                         f"{lo:+.1f} – {hi:+.1f} | {w}/{t}/{l} |")
            rows.append({"contrast": label, "judge": judge, "n": len(deltas),
                         "delta_mean": round(statistics.mean(deltas), 2),
                         "ci_low": round(lo, 2), "ci_high": round(hi, 2),
                         "win": w, "tie": t, "loss": l})

    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/judge_effects.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(ROOT / "results/judge_effects.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("\n".join(lines))
    print(f"\nwrote results/judge_effects.md/.csv ({len(rows)} contrasts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
