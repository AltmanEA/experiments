#!/usr/bin/env python3
"""Paired condition effects from MQM absolute scores (P-002, P-003a).

For each contrast (A -> B) the 21 (fixture, rep) units are paired across
conditions, so fixture difficulty cancels out. Judges are averaged per unit
unless --split-judges is given.

Output: results/judge_effects.md and judge_effects.csv
(--out-prefix writes results/<prefix>.md/.csv instead, e.g. --out-prefix
 judge_effects_freebsd; fixtures are taken from the condition dirs present
 under judge/<absolute|pairwise...>, so a second domain isolated by --tag
 needs its own judge dir and out prefix.)

Usage: judge_effects.py [--boot 20000] [--split-judges] [--judge-dir DIR]
                        [--out-prefix NAME] [--all-temperature] [--domain council|freebsd]
"""
import argparse, csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAIN = [
    ("C3_local_fp8_think_off", "C4_local_fp8_think_on", "thinking ON vs OFF, FP8"),
    ("C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on", "thinking ON vs OFF, NVFP4"),
    ("C1_cloud_bf16_think_off", "K0_cloud_no_glossary", "no glossary vs glossary, cloud"),
    ("C1_cloud_bf16_think_off", "C2_cloud_bf16_think_on_clean", "thinking ON (clean) vs OFF, cloud"),
    ("C2_cloud_bf16_think_on", "C2_cloud_bf16_think_on_clean", "post-processing (clean vs raw)"),
    ("C3_local_fp8_think_off", "C5_local_nvfp4_think_off", "NVFP4 vs FP8, thinking OFF"),
    ("C4_local_fp8_think_on", "C6_local_nvfp4_think_on", "NVFP4 vs FP8, thinking ON"),
    ("C1_cloud_bf16_think_off", "C3_local_fp8_think_off", "FP8 vs cloud bf16, thinking OFF"),
]

# P-003a: temperature grid (P-004), NVFP4 local. 0.2 = C5/C6.
T_GRID = [("0.0", "T00_local_nvfp4_t00_think"), ("0.2", None), ("0.4", "T04_local_nvfp4_t04_think"),
          ("0.6", "T06_local_nvfp4_t06_think"), ("0.8", "T08_local_nvfp4_t08_think"),
          ("1.0", "T10_local_nvfp4_t10_think")]


# P-006: temperature transfer on FP8 (legacy frozen engine, T in {0.0, 0.8} x thinking).
# C3/C4 (T=0.2) are the same engine's anchor; NVFP4 pairs test H4 (quantization x
# temperature interaction at the same T).
FP8_PAIRS = [
    ("FP8_T00_local_fp8_t00_think_off", "FP8_T00_local_fp8_t00_think_on",
     "thinking ON vs OFF, FP8 T=0.0"),
    ("FP8_T08_local_fp8_t08_think_off", "FP8_T08_local_fp8_t08_think_on",
     "thinking ON vs OFF, FP8 T=0.8"),
    ("FP8_T00_local_fp8_t00_think_off", "FP8_T08_local_fp8_t08_think_off",
     "T=0.8 vs T=0 anchor, FP8 thinking OFF"),
    ("FP8_T00_local_fp8_t00_think_on", "FP8_T08_local_fp8_t08_think_on",
     "T=0.8 vs T=0 anchor, FP8 thinking ON"),
    ("FP8_T00_local_fp8_t00_think_off", "T00_local_nvfp4_t00_think_off",
     "NVFP4 vs FP8, T=0.0 thinking OFF"),
    ("FP8_T00_local_fp8_t00_think_on", "T00_local_nvfp4_t00_think_on",
     "NVFP4 vs FP8, T=0.0 thinking ON"),
    ("C3_local_fp8_think_off", "FP8_T00_local_fp8_t00_think_off",
     "T=0.0 vs T=0.2, FP8 thinking OFF (legacy engine)"),
    ("C4_local_fp8_think_on", "FP8_T08_local_fp8_t08_think_on",
     "T=0.8 vs T=0.2, FP8 thinking ON (legacy engine)"),
]

# P-005: second domain (FreeBSD Handbook, NVFP4 local, T in {0.0, 0.2} x thinking).
FREEBSD_PAIRS = [
    ("F_C5_local_nvfp4_think_off", "F_C6_local_nvfp4_think_on",
     "thinking ON vs OFF, NVFP4 T=0.2 (FreeBSD)"),
    ("F_T00_local_nvfp4_t00_think_off", "F_T00_local_nvfp4_t00_think_on",
     "thinking ON vs OFF, NVFP4 T=0.0 (FreeBSD)"),
    ("F_C5_local_nvfp4_think_off", "F_T00_local_nvfp4_t00_think_off",
     "T=0.0 vs T=0.2, thinking OFF (FreeBSD)"),
    ("F_C6_local_nvfp4_think_on", "F_T00_local_nvfp4_t00_think_on",
     "T=0.0 vs T=0.2, thinking ON (FreeBSD)"),
]


def temperature_pairs():
    """Thinking contrasts at each T, plus trend contrasts from the T=0 anchor."""
    out = []
    for t, stem in T_GRID:
        if stem is None:
            a, b = "C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on"
        else:
            a, b = f"{stem}_off", f"{stem}_on"
        out.append((a, b, f"thinking ON vs OFF, NVFP4 T={t}"))
    anchor = "T00_local_nvfp4_t00_think"
    for t, stem in T_GRID[1:]:
        suffix = "_off"
        b = "C5_local_nvfp4_think_off" if stem is None else f"{stem}{suffix}"
        out.append((f"{anchor}{suffix}", b, f"T={t} vs T=0 anchor, thinking OFF"))
        suffix = "_on"
        b = "C6_local_nvfp4_think_on" if stem is None else f"{stem}{suffix}"
        out.append((f"{anchor}{suffix}", b, f"T={t} vs T=0 anchor, thinking ON"))
    return out


def load(judge_dir="judge/absolute"):
    sc = defaultdict(list)
    base = Path(judge_dir)
    if not base.is_absolute():
        base = ROOT / base
    for f in base.glob("*/*/rep*.json"):
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
    ap.add_argument("--judge-dir", default="judge/absolute")
    ap.add_argument("--out-prefix", default="judge_effects")
    ap.add_argument("--all-temperature", action="store_true",
                    help="add P-004 contrasts (per-T thinking + T=0 anchor trends)")
    ap.add_argument("--domain", choices=["council", "freebsd", "fp8"], default="council",
                    help="freebsd: P-005 contrasts on the second domain (implies "
                         "--judge-dir judge_freebsd/absolute --out-prefix judge_effects_freebsd); "
                         "fp8: P-006 FP8 temperature contrasts (out prefix judge_effects_fp8)")
    a = ap.parse_args()
    if a.domain == "freebsd":
        if a.judge_dir == "judge/absolute":
            a.judge_dir = "judge_freebsd/absolute"
        if a.out_prefix == "judge_effects":
            a.out_prefix = "judge_effects_freebsd"
    if a.domain == "fp8" and a.out_prefix == "judge_effects":
        a.out_prefix = "judge_effects_fp8"

    sc = load(a.judge_dir)
    judges = sorted({k[3] for k in sc})
    units = sorted({k[1:3] for k in sc})
    if a.domain == "freebsd":
        pairs = FREEBSD_PAIRS
    elif a.domain == "fp8":
        pairs = FP8_PAIRS
    else:
        pairs = MAIN + (temperature_pairs() if a.all_temperature else [])
    rows, lines = [], ["| contrast | judge | n | Δ mean | 95% CI | W/T/L |",
                       "|---|---|---|---|---|---|"]

    for ca, cb, label in pairs:
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
    md = ROOT / "results" / f"{a.out_prefix}.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not rows:
        print("no paired units found (missing judge outputs for these conditions)")
        print(f"wrote results/{a.out_prefix}.md (header only)")
        return 1
    with open(ROOT / "results" / f"{a.out_prefix}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("\n".join(lines))
    print(f"\nwrote results/{a.out_prefix}.md/.csv ({len(rows)} contrasts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
