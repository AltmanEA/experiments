#!/usr/bin/env python3
"""C2 (PLAN-CLOSEOUT): intra-judge test-retest noise.

The same absolute cells, judged a second time by the SAME judge on the SAME input,
are compared against the primary verdicts (results/judge_absolute.csv). This measures
the one noise component neither inter-judge agreement (mean |Δ| 19.0) nor generation
noise (E-008 gen 4.0 at greedy) covers: how stable a single judge's own score is.
It also answers the §6.2 gap ("3 judge repetitions, median") in the cheapest form:
2 judges x 2 independent repetitions.

Run the batch first (run_c2c3_night.sh stage_c2 writes judge_retest/absolute/),
then:  .venv-analysis/bin/python metrics/judge_retest.py

Output: results/judge_retest.md / .csv
"""
import csv, argparse
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

# thinking contrasts whose sign must survive re-judging (the article's headline pairs)
CONTRASTS = [("T00_local_nvfp4_t00_think_off", "T00_local_nvfp4_t00_think_on"),
             ("C3_local_fp8_think_off", "C4_local_fp8_think_on"),
             ("C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on")]


def load(path):
    out = {}
    for r in csv.DictReader(open(path)):
        try:
            r["score"] = float(r["score"])
        except (KeyError, ValueError):
            continue
        out[(r["condition"], r["fixture"], r["rep"], r["judge"])] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", default=str(RES / "judge_absolute.csv"))
    ap.add_argument("--retest", default=str(RES / "judge_absolute_retest.csv"))
    ap.add_argument("--out-prefix", default=str(RES / "judge_retest"))
    a = ap.parse_args()

    prim, ret = load(a.primary), load(a.retest)
    common = sorted(set(prim) & set(ret))
    if not common:
        raise SystemExit("no overlapping cells — did the retest batch run?")

    d = [abs(prim[k]["score"] - ret[k]["score"]) for k in common]
    x = [prim[k]["score"] for k in common]
    y = [ret[k]["score"] for k in common]
    drift = [ret[k]["score"] - prim[k]["score"] for k in common]
    n = len(common)

    # severity-band threshold crossings (MQM bands: passable >=80, usable 60..80, bad <60)
    def band(s):
        return "passable" if s >= 80 else ("usable" if s >= 60 else "bad")
    band_same = sum(1 for k in common if band(prim[k]["score"]) == band(ret[k]["score"]))
    crit_same = sum(1 for k in common
                    if (int(prim[k]["n_critical"]) > 0) == (int(ret[k]["n_critical"]) > 0))

    r = stats.pearsonr(x, y).statistic if len(set(x)) > 1 and len(set(y)) > 1 else float("nan")
    rho = stats.spearmanr(x, y).statistic if len(set(x)) > 1 and len(set(y)) > 1 else float("nan")

    lines = ["# Intra-judge test–retest (C2)", "",
             f"Клеток в повторном суде: {n} из {len(ret)} запрошенных "
             f"(первичные — {len(prim)}); те же вход, модель-судья, temperature=0.", "",
             f"- mean |Δ| intra-judge: **{mean(d):.2f}** (median {median(d):.1f}, max {max(d):.0f});",
             f"- средний signed Δ (retest − primary): {mean(drift):+.2f} — систематического дрейфа нет,"
             if abs(mean(drift)) < mean(d) / 2 else
             f"- средний signed Δ (retest − primary): **{mean(drift):+.2f}** — заметный дрейф, смотреть ниже;",
             f"- Pearson r = {r:.3f}, Spearman ρ = {rho:.3f};",
             f"- доля |Δ| ≤ 10: {sum(1 for v in d if v <= 10) / n:.1%}, ≤ 20: {sum(1 for v in d if v <= 20) / n:.1%};",
             f"- пересечение полос severity (≥80 / 60…80 / <60): совпало {band_same}/{n} = {band_same / n:.1%};",
             f"- совпадение «есть ≥1 critical или нет»: {crit_same}/{n} = {crit_same / n:.1%}.", "",
             "Ориентир: межсудейский mean |Δ| = 19.24 (полный набор, §7 SUMMARY);",
             "шум генерации greedy = 4.0 (E-008). Intra-judge шум должен лежать НИЖЕ",
             "межсудейского, иначе одиночные суждения в таблицах неинтерпретабельны.", ""]

    # per-judge breakdown
    lines += ["| судья | n | mean |Δ| | r | полосы совп. | critical совп. |", "|---|---|---|---|---|---|"]
    out_csv = []
    for judge in sorted({k[3] for k in common}):
        ks = [k for k in common if k[3] == judge]
        dd = [abs(prim[k]["score"] - ret[k]["score"]) for k in ks]
        xx = [prim[k]["score"] for k in ks]
        yy = [ret[k]["score"] for k in ks]
        rr = (stats.pearsonr(xx, yy).statistic
              if len(set(xx)) > 1 and len(set(yy)) > 1 else float("nan"))
        bs = sum(1 for k in ks if band(prim[k]["score"]) == band(ret[k]["score"]))
        cs = sum(1 for k in ks if (int(prim[k]["n_critical"]) > 0) == (int(ret[k]["n_critical"]) > 0))
        lines.append(f"| {judge} | {len(ks)} | {mean(dd):.2f} | {rr:.3f} | "
                     f"{bs / len(ks):.1%} | {cs / len(ks):.1%} |")
        out_csv.append({"judge": judge, "n": len(ks), "mean_abs_delta": round(mean(dd), 2),
                        "pearson_r": round(rr, 3), "band_agree": round(bs / len(ks), 3),
                        "critical_agree": round(cs / len(ks), 3)})

    # sign survival of the headline thinking contrasts on the retested cells
    lines += ["", "## Знак thinking-контраста на пересуженных клетках", "",
              "Обе стороны контраста пересужена на одних и тех же (fixture, rep, judge):",
              "совпал ли знак Δ(score_off − score_on) с первичным рядом.", "",
              "| контраст | n пар | знак совп. | знак изменил | p (бином. vs 0.5) |", "|---|---|---|---|---|"]
    for off, on in CONTRASTS:
        pairs = []
        for k in common:
            if k[0] != off:
                continue
            k2 = (on,) + k[1:]
            if k2 in ret and k2 in prim:
                d1 = prim[off, k[1], k[2], k[3]]["score"] - prim[on, k[1], k[2], k[3]]["score"]
                d2 = ret[off, k[1], k[2], k[3]]["score"] - ret[on, k[1], k[2], k[3]]["score"]
                pairs.append((d1, d2))
        if not pairs:
            lines.append(f"| {off} vs {on} | 0 | — | — | — |")
            continue
        agree = sum(1 for d1, d2 in pairs if (d1 > 0) == (d2 > 0) or (d1 == 0 and d2 == 0))
        p = stats.binomtest(agree, len(pairs), 0.5).pvalue
        lines.append(f"| {off} vs {on} | {len(pairs)} | {agree} | {len(pairs) - agree} | {p:.4f} |")
        out_csv.append({"contrast": f"{off} vs {on}", "n": len(pairs),
                        "sign_agree": agree, "sign_flip": len(pairs) - agree,
                        "p_binom": round(p, 5)})
    lines += ["", f"Сгенерировано: judge_retest.py, cells={n}", ""]

    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    fields = ["judge", "n", "mean_abs_delta", "pearson_r", "band_agree", "critical_agree",
              "contrast", "sign_agree", "sign_flip", "p_binom"]
    with open(a.out_prefix + ".csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(out_csv)
    print(f"wrote {a.out_prefix}.md / .csv (n={n})")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
