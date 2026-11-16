#!/usr/bin/env python3
"""P-002a: pairwise judge results -> preference matrix + sign tests (PLAN §6.3).

Reads results/judge_pairwise.csv (judge_batch.py --mode pairwise --aggregate).
Per contrast (over all units x judges, and per judge):
  * preference counts A/tie/B;
  * exact two-sided binomial test of A vs B against p=0.5 (ties excluded,
    ties are reported separately — no tie adjustment pretends to be data);
  * direction agreement between the two judges and vs the absolute-MQM effect
    from results/judge_effects.csv (triangulation: pairwise "sign" should
    reproduce absolute contrasts whose CI crossed 0).

Output: results/pairwise_report.md / .csv
Usage: pairwise_report.py
"""
import csv, statistics
from collections import defaultdict
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

# contrast label -> (direction of "B is better" in the absolute-MQM effect table,
# so we can triangulate); key = pairwise condition dir "A-vs-B".
TRIANGULATE = {
    "C3_local_fp8_think_off-vs-C4_local_fp8_think_on":
        "thinking ON vs OFF, FP8",
    "C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on":
        "thinking ON vs OFF, NVFP4",
    "C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean":
        "thinking ON (clean) vs OFF, cloud",
    "T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on":
        "thinking ON vs OFF, NVFP4 T=0.0",
}


def main():
    rows = list(csv.DictReader(open(RES / "judge_pairwise.csv")))
    by = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # cond -> judge -> winner
    for r in rows:
        if r.get("_status") == "fail":
            continue
        by[r["condition"]][r["judge"]][r["winner"]] += 1

    # absolute-MQM deltas (mean of judges) for triangulation
    mqm = {}
    try:
        for r in csv.DictReader(open(RES / "judge_effects.csv")):
            if r["judge"] == "(mean of judges)":
                mqm[r["contrast"]] = (float(r["delta_mean"]), float(r["ci_low"]),
                                      float(r["ci_high"]))
    except FileNotFoundError:
        pass

    out_csv, lines = [], ["# Pairwise judge preferences (P-002a)", "",
                          "Binomial two-sided on A vs B (ties excluded, reported separately).",
                          "Triangulation column: sign of the absolute-MQM paired effect "
                          "(positive delta = B better).", "",
                          "| contrast | judge | n | A | tie | B | p vs 0.5 | verdict | "
                          "abs-MQM Δ (95% CI) | agree |",
                          "|---|---|---|---|---|---|---|---|---|---|"]
    for cond in sorted(by):
        label = TRIANGULATE.get(cond, "")
        m = mqm.get(label)
        # +1 if B better in absolute table (delta>0); pairwise B winner should win too
        for judge in sorted(by[cond]):
            w = by[cond][judge]
            a, t, b = w["A"], w["tie"], w["B"]
            n = a + t + b
            if a + b > 0:
                p = stats.binomtest(b, a + b, 0.5).pvalue
            else:
                p = float("nan")
            if p == p and p < 0.05:
                verdict = "B" if b > a else "A"
            else:
                verdict = "tie"
            agree = ""
            if m:
                abs_sign = "B" if m[0] > 0 else "A"
                agree = "yes" if verdict == abs_sign else ("—" if verdict == "tie" else "NO")
            lines.append(f"| {cond} | {judge} | {n} | {a} | {t} | {b} | "
                         f"{p:.4f} | {verdict} | "
                         f"{f'{m[0]:+.1f} ({m[1]:+.1f}…{m[2]:+.1f})' if m else '—'} | {agree} |")
            out_csv.append({"contrast": cond, "judge": judge, "n": n, "a": a, "tie": t,
                            "b": b, "p_binom": round(p, 5), "verdict": verdict,
                            "mqm_delta": m[0] if m else "", "agree": agree})
        # pooled row over judges
        w = defaultdict(int)
        for judge in by[cond]:
            for k, v in by[cond][judge].items():
                w[k] += v
        a, t, b = w["A"], w["tie"], w["B"]
        p = stats.binomtest(b, a + b, 0.5).pvalue if a + b else float("nan")
        verdict = ("B" if b > a else "A") if (p == p and p < 0.05) else "tie"
        agree = ""
        if m:
            abs_sign = "B" if m[0] > 0 else "A"
            agree = "yes" if verdict == abs_sign else ("—" if verdict == "tie" else "NO")
        lines.append(f"| **{cond}** | **pooled** | **{a + t + b}** | **{a}** | **{t}** | "
                     f"**{b}** | **{p:.4f}** | **{verdict}** | "
                     f"{f'**{m[0]:+.1f}** ({m[1]:+.1f}…{m[2]:+.1f})' if m else '—'} | {agree} |")
        out_csv.append({"contrast": cond, "judge": "pooled", "n": a + t + b, "a": a,
                        "tie": t, "b": b, "p_binom": round(p, 5), "verdict": verdict,
                        "mqm_delta": m[0] if m else "", "agree": agree})
        lines.append("")

    (RES / "pairwise_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(RES / "pairwise_report.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_csv[0])); w.writeheader(); w.writerows(out_csv)
    print("\n".join(lines))
    print(f"\nwrote results/pairwise_report.md/.csv ({len(by)} contrasts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
