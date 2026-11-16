#!/usr/bin/env python3
"""P-002a: pairwise judge results -> preference matrix + sign tests (PLAN §6.3),
plus the position control that PLAN §6.2 requires (C1).

Reads results/judge_pairwise.csv (judge_batch.py --mode pairwise --aggregate), which
holds every presentation order produced by judge_batch.py --order:
  direct   : the original P-002a layout (condition A in slot A)
  reverse  : same pairs, slots mirrored, winner mapped back to conditions
  same_a/b : one text in both slots — a null probe for tie behaviour

Main table (unchanged semantics): per contrast, per judge and pooled —
  * preference counts A/tie/B;
  * exact two-sided binomial test of A vs B against p=0.5 (ties excluded,
    ties are reported separately — no tie adjustment pretends to be data);
  * direction agreement between the two judges and vs the absolute-MQM effect
    from results/judge_effects.csv (triangulation: pairwise "sign" should
    reproduce absolute contrasts whose CI crossed 0).

Then two control sections, only if reversed / null-probe cells exist:
  * Position control: slot-level preference in each order, the position-bias
    estimate, an exact McNemar (binomial) test on discordant units, and the
    fraction of units whose winner survives the order switch.
  * Tie null probe: how often a judge says tie when both slots hold the very
    same text — bounds the meaning of "0 ties in 168" in the main table.

Output: results/pairwise_report.md / .csv
Usage: pairwise_report.py
"""
import csv, statistics
from collections import defaultdict
from pathlib import Path

from scipy import stats


def split_order(cond):
    """'A-vs-B__reverse' -> ('A-vs-B', 'reverse'); bare name -> (name, 'direct')."""
    base, sep, suffix = cond.partition("__")
    return (base, suffix) if sep else (cond, "direct")

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


def load_rows():
    """All judged pairwise cells, annotated with (base contrast, presentation order)."""
    rows = []
    for r in csv.DictReader(open(RES / "judge_pairwise.csv")):
        if r.get("_status") == "fail":
            continue
        base, order = split_order(r["condition"])
        r["_base"], r["_order"] = base, order
        # Pre-C1 rows predate the order/winner_slot columns: direct order, slot == verdict.
        r["_slot"] = r.get("winner_slot") or r["winner"]
        rows.append(r)
    return rows


def binom(k, n):
    return stats.binomtest(k, n, 0.5).pvalue if n else float("nan")


def pearson(x, y):
    if len(set(x)) < 2 or len(set(y)) < 2:
        return float("nan")
    return stats.pearsonr(x, y).statistic


# Pair labels may use the short alias judge_batch.py accepts on the CLI.
CLEAN = {"C2_clean": "C2_cloud_bf16_think_on_clean"}


def main():
    rows = load_rows()
    by = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # cond -> judge -> winner
    for r in rows:
        if r["_order"] != "direct":
            continue  # main table keeps the original P-002a (direct-order) semantics
        by[r["condition"]][r["judge"]][r["winner"]] += 1

    # C1 decision rule (fixed before the position run): direct pooled verdicts may be
    # published as-is ONLY if pooled position bias < 0.05 and McNemar p > 0.05 and
    # sign-concordance >= 0.8 (nan McNemar = no discordant units = passes trivially).
    # Otherwise the headline verdicts are recomputed on direct+reverse (4 observations
    # per unit) and the direct-only pooled row is starred.
    byu = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # union of both orders
    for r in rows:
        if r["_order"] in ("direct", "reverse"):
            byu[r["_base"]][r["judge"]][r["winner"]] += 1
    rev_rows = [r for r in rows if r["_order"] == "reverse"]
    USE_UNION = False
    if rev_rows:
        dmap = {(r["_base"], r["fixture"], r["rep"], r["judge"]): r for r in rows
                if r["_order"] == "direct"}
        rmap = {(r["_base"], r["fixture"], r["rep"], r["judge"]): r for r in rev_rows}
        _units = sorted(set(dmap) & set(rmap))
        _sa_d = sum(1 for u in _units if dmap[u]["_slot"] == "A") / len(_units)
        _sa_r = sum(1 for u in _units if rmap[u]["_slot"] == "A") / len(_units)
        _b01 = sum(1 for u in _units if dmap[u]["winner"] == "A" and rmap[u]["winner"] == "B")
        _b10 = sum(1 for u in _units if dmap[u]["winner"] == "B" and rmap[u]["winner"] == "A")
        _conc = sum(1 for u in _units if dmap[u]["winner"] == rmap[u]["winner"])
        _p = binom(_b01, _b01 + _b10)
        _bias = abs((_sa_d + (1.0 - _sa_r)) / 2.0 - 0.5)
        USE_UNION = not (_bias < 0.05 and (_p != _p or _p > 0.05)
                         and _conc / len(_units) >= 0.8)

    # absolute-MQM deltas (mean of judges) for triangulation
    mqm = {}
    try:
        for r in csv.DictReader(open(RES / "judge_effects.csv")):
            if r["judge"] == "(mean of judges)":
                mqm[r["contrast"]] = (float(r["delta_mean"]), float(r["ci_low"]),
                                      float(r["ci_high"]))
    except FileNotFoundError:
        pass

    pos_csv = []          # position-control rows -> pairwise_position.csv
    out_csv, lines = [], ["# Pairwise judge preferences (P-002a)", "",
                          "Binomial two-sided on A vs B (ties excluded, reported separately).",
                          "Triangulation column: sign of the absolute-MQM paired effect "
                          "(positive delta = B better).",
                          "NOTE: main table = direct presentation order only (original "
                          "P-002a). Per the C1 decision rule it is superseded by the "
                          "union table below." if USE_UNION else "",
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

    # ----- union table (direct+reverse, 4 obs/unit): the HEADLINE per the C1 rule -----
    if USE_UNION:
        lines += ["## Основной ряд: объединение прямого и обратного предъявления (C1)",
                  "",
                  "Правило C1 не пройдено ни одним рядом (см. «Контроль позиции»):",
                  f"pooled position bias = {_bias:.3f}, McNemar p = {_p:.4f}, знак совпал в",
                  f"{_conc}/{len(_units)} ({_conc / len(_units):.1%}). Значит за итоговые",
                  "вердикты принимаются наблюдения обоих порядков (по 4 на единицу:",
                  "2 порядка × 2 судьи); прямые pooled-вердикты выше помечены как",
                  "superseded. winner переложен на условия, поэтому «A лучше» сопоставимо.",
                  "",
                  "| контраст | судья | n | A | tie | B | p vs 0.5 | verdict | abs-MQM Δ (95% CI) | agree |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for cond in sorted(byu):
            label = TRIANGULATE.get(cond, "")
            m = mqm.get(label)
            for judge in sorted(byu[cond]):
                w = byu[cond][judge]
                a, t, b = w["A"], w["tie"], w["B"]
                p = stats.binomtest(b, a + b, 0.5).pvalue if a + b else float("nan")
                verdict = ("B" if b > a else "A") if (p == p and p < 0.05) else "tie"
                agree = ""
                if m:
                    abs_sign = "B" if m[0] > 0 else "A"
                    agree = "yes" if verdict == abs_sign else ("—" if verdict == "tie" else "NO")
                lines.append(f"| {cond} | {judge} | {a + t + b} | {a} | {t} | {b} | "
                             f"{p:.4f} | {verdict} | "
                             f"{f'{m[0]:+.1f} ({m[1]:+.1f}…{m[2]:+.1f})' if m else '—'} | {agree} |")
                out_csv.append({"contrast": cond, "judge": f"{judge} (union)",
                                "n": a + t + b, "a": a, "tie": t, "b": b,
                                "p_binom": round(p, 5), "verdict": verdict,
                                "mqm_delta": m[0] if m else "", "agree": agree})
            w = defaultdict(int)
            for judge in byu[cond]:
                for k, v in byu[cond][judge].items():
                    w[k] += v
            a, t, b = w["A"], w["tie"], w["B"]
            p = stats.binomtest(b, a + b, 0.5).pvalue if a + b else float("nan")
            verdict = ("B" if b > a else "A") if (p == p and p < 0.05) else "tie"
            agree = ""
            if m:
                abs_sign = "B" if m[0] > 0 else "A"
                agree = "yes" if verdict == abs_sign else ("—" if verdict == "tie" else "NO")
            lines.append(f"| **{cond}** | **pooled (union)** | **{a + t + b}** | **{a}** | "
                         f"**{t}** | **{b}** | **{p:.4f}** | **{verdict}** | "
                         f"{f'**{m[0]:+.1f}** ({m[1]:+.1f}…{m[2]:+.1f})' if m else '—'} | {agree} |")
            out_csv.append({"contrast": cond, "judge": "pooled (union)", "n": a + t + b,
                            "a": a, "tie": t, "b": b, "p_binom": round(p, 5),
                            "verdict": verdict, "mqm_delta": m[0] if m else "", "agree": agree})
            lines.append("")

    # ------------------------------------------------ C1: position control (PLAN §6.2)
    rev = [r for r in rows if r["_order"] == "reverse"]
    if rev:
        lines += ["", "## Контроль позиции (задача C1, PLAN §6.2: перестановка порядков, все 4 контраста)", "",
                  "Единица = (контраст, фикстура, повтор, судья). Прямой порядок — из P-002a,",
                  "обратный — `judge_batch.py --order reverse`; вердикт в обратном порядке",
                  "переложен обратно на условия, поэтому столбцы «условие A лучше» сопоставимы.",
                  "`slot A` — доля выборов, когда судья указал на **слот** A (до переклада):",
                  "при отсутствии смещения ≈ 0.5 и в прямом, и в обратном предъявлении.", "",
                  "| контраст | судья | n пар | A лучше (прям.) | A лучше (обр.) | slot A (прям.) | slot A (обр.) | position bias | McNemar p | знак совпал |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        direct_by_unit = {(r["_base"], r["fixture"], r["rep"], r["judge"]): r for r in rows
                          if r["_order"] == "direct"}
        rev_by_unit = {(r["_base"], r["fixture"], r["rep"], r["judge"]): r for r in rev}
        units = sorted(set(direct_by_unit) & set(rev_by_unit))
        for base in sorted({u[0] for u in units}):
            for judge in sorted({u[3] for u in units if u[0] == base}):
                us = [u for u in units if u[0] == base and u[3] == judge]
                if not us:
                    continue
                d = [direct_by_unit[u] for u in us]
                v = [rev_by_unit[u] for u in us]
                a_d = sum(1 for r in d if r["winner"] == "A")
                a_r = sum(1 for r in v if r["winner"] == "A")
                sa_d = sum(1 for r in d if r["_slot"] == "A") / len(d)
                sa_r = sum(1 for r in v if r["_slot"] == "A") / len(v)
                # McNemar on discordant units: same unit, opposite verdicts.
                b01 = sum(1 for x, y in zip(d, v) if x["winner"] == "A" and y["winner"] == "B")
                b10 = sum(1 for x, y in zip(d, v) if x["winner"] == "B" and y["winner"] == "A")
                p_mcn = binom(b01, b01 + b10)
                conc = sum(1 for x, y in zip(d, v) if x["winner"] == y["winner"])
                bias = abs((sa_d + (1.0 - sa_r)) / 2.0 - 0.5)
                lines.append(f"| {base} | {judge} | {len(us)} | {a_d} | {a_r} | "
                             f"{sa_d:.2f} | {sa_r:.2f} | {bias:.3f} | {p_mcn:.4f} | "
                             f"{conc}/{len(us)} |")
                pos_csv.append({"contrast": base, "judge": judge, "n": len(us),
                                "a_direct": a_d, "a_reverse": a_r,
                                "slotA_direct": round(sa_d, 3), "slotA_reverse": round(sa_r, 3),
                                "position_bias": round(bias, 3), "p_mcnemar": round(p_mcn, 5),
                                "concordant": conc, "conc_frac": round(conc / len(us), 3)})
        # Pooled over contrasts/judges: the headline numbers for the article.
        d_all = [direct_by_unit[u] for u in units]
        v_all = [rev_by_unit[u] for u in units]
        sa_d = sum(1 for r in d_all if r["_slot"] == "A") / len(d_all)
        sa_r = sum(1 for r in v_all if r["_slot"] == "A") / len(v_all)
        b01 = sum(1 for u in units if direct_by_unit[u]["winner"] == "A"
                  and rev_by_unit[u]["winner"] == "B")
        b10 = sum(1 for u in units if direct_by_unit[u]["winner"] == "B"
                  and rev_by_unit[u]["winner"] == "A")
        conc = sum(1 for u in units if direct_by_unit[u]["winner"] == rev_by_unit[u]["winner"])
        p_mcn = binom(b01, b01 + b10)
        bias = abs((sa_d + (1.0 - sa_r)) / 2.0 - 0.5)
        lines.append(f"| **все контрасты** | **pooled** | **{len(units)}** | "
                     f"**{sum(1 for r in d_all if r['winner'] == 'A')}** | "
                     f"**{sum(1 for r in v_all if r['winner'] == 'A')}** | **{sa_d:.2f}** | "
                     f"**{sa_r:.2f}** | **{bias:.3f}** | **{p_mcn:.4f}** | "
                     f"**{conc}/{len(units)}** |")
        lines += ["",
                  "Правило решения (зафиксировано до прогона): если `position bias` < 0.05 и",
                  "McNemar p > 0.05, а согласованность знака ≥ 0.8 — порядок не влияет, pooled-",
                  "вердикты основной таблицы публикуются как есть; смещение репортится в подписи.",
                  "Иначе — основной вердикт пересчитывается на объединении прямого и обратного",
                  "предъявления (по 4 наблюдения на единицу), а исходный pooled-ряд помечается.",
                  ""]
        (RES / "pairwise_position_units.csv").parent.mkdir(exist_ok=True)
        with open(RES / "pairwise_position_units.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["contrast", "fixture", "rep", "judge", "winner_direct", "slot_direct",
                        "winner_reverse", "slot_reverse", "agree"])
            for u in units:
                x, y = direct_by_unit[u], rev_by_unit[u]
                w.writerow([u[0], u[1], u[2], u[3], x["winner"], x["_slot"],
                            y["winner"], y["_slot"], int(x["winner"] == y["winner"])])

    # ------------------------------------------------ C1: tie null probe (0 ties / 168?)
    probe = [r for r in rows if r["_order"].startswith("same_")]
    if probe:
        lines += ["", "## Null-проба на ничьи (A vs A)", "",
                  "Один и тот же текст в обоих слотах: правильное поведение судьи — `tie`.",
                  "Доля ничьих здесь — верхняя граница того, что судья вообще умеет говорить",
                  "`tie`; «0 ничьих из 168» в основной таблице значит столько, сколько позволяет",
                  "эта граница.", "",
                  "| группа | судья | n | tie | A | B | доля tie |", "|---|---|---|---|---|---|---|"]
        grp = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for r in probe:
            key = f"{r['_base']}::{r['_order']}"
            grp[key][r["judge"]][r["winner"]] += 1
        for key in sorted(grp):
            for judge in sorted(grp[key]):
                w = grp[key][judge]
                n = sum(w.values())
                lines.append(f"| {key} | {judge} | {n} | {w['tie']} | {w['A']} | {w['B']} | "
                             f"{(w['tie'] / n if n else 0):.2f} |")
                out_csv.append({"contrast": key, "judge": judge, "n": n, "a": w["A"],
                                "tie": w["tie"], "b": w["B"],
                                "verdict": "tie-probe", "mqm_delta": "", "agree": ""})
        w = defaultdict(int)
        for grp_key in grp:
            for judge in grp[grp_key]:
                for k, vv in grp[grp_key][judge].items():
                    w[k] += vv
        n = sum(w.values())
        lines.append(f"| **все группы** | **pooled** | **{n}** | **{w['tie']}** | **{w['A']}** | "
                     f"**{w['B']}** | **{(w['tie'] / n if n else 0):.2f}** |")

    # ------------------------------------------- verbosity-confound check (free, direct)
    # "42:0 with 0 ties" could be a length artefact: the longer output tends to win.
    # If the pairwise winner tracks |len(A)-len(B)| rather than the absolute-MQM sign,
    # that belongs in the article regardless of the position control.
    if direct_len_rows := [r for r in rows if r["_order"] == "direct"]:
        cache = {}

        def chars(cond, fix, rep):
            key = (cond, fix, rep)
            if key not in cache:
                p = ROOT / "runs" / CLEAN.get(cond, cond) / fix / f"rep{rep}.md"
                cache[key] = len(p.read_text(encoding="utf-8")) if p.exists() else None
            return cache[key]

        lines += ["", "## Проверка на длину вывода (verbosity confound, бесплатно)", "",
                  "Победитель pairwise против разницы длин |A|−|B|. Если победа объясняется",
                  "длиной, а не качеством, — это ограничение к §5.10. r_point — точечно-",
                  "бисериальная корреляция (победа B, lenB−lenA); `nan` = вердикт не варьировался",
                  "(все единицы в одну сторону), тогда читается колонка «побеждал более длинный».",
                  "",
                  "| контраст | n пар | mean len A | mean len B | побеждал более длинный | r_point |",
                  "|---|---|---|---|---|---|"]
        byu = defaultdict(list)
        for r in direct_len_rows:
            byu[r["_base"]].append(r)
        for base in sorted(byu):
            if "-vs-" not in base:
                continue
            ca, cb = base.split("-vs-", 1)
            lens = []
            for r in byu[base]:
                la, lb = chars(ca, r["fixture"], r["rep"]), chars(cb, r["fixture"], r["rep"])
                if la is not None and lb is not None:
                    lens.append((r["winner"], lb - la, la, lb))
            if len(lens) < 3:
                continue
            wins_long = sum(1 for w, dl, _, _ in lens if (w == "B" and dl > 0) or (w == "A" and dl < 0))
            xs = [dl for w, dl, _, _ in lens]
            ys = [1 if w == "B" else 0 for w, _, _, _ in lens]
            r_pt = (pearson(xs, ys) if len(set(ys)) > 1 and len(set(xs)) > 1 else float("nan"))
            lines.append(f"| {base} | {len(lens)} | {statistics.mean(l for _,_,l,_ in lens):.0f} | "
                         f"{statistics.mean(l for _,_,_,l in lens):.0f} | "
                         f"{wins_long}/{len(lens)} | {r_pt:+.2f} |")

    (RES / "pairwise_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(RES / "pairwise_report.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_csv[0])); w.writeheader(); w.writerows(out_csv)
    if pos_csv:
        with open(RES / "pairwise_position.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(pos_csv[0]))
            w.writeheader(); w.writerows(pos_csv)
    print("\n".join(lines))
    print(f"\nwrote results/pairwise_report.md/.csv ({len(by)} contrasts)"
          + (f", pairwise_position.csv ({len(pos_csv)} rows)" if pos_csv else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
