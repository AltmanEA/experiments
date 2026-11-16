#!/usr/bin/env python3
"""C3 (PLAN-CLOSEOUT §C3): pairwise «машинный вывод vs official RU» on FreeBSD.

Reads results/judge_pairwise_freebsd_ref.csv (judge_batch --mode pairwise
--tag _freebsd_ref, staged runs dir with the official reference as a pseudo
condition). Condition A is always the machine translation, B the official RU —
so «A wins» means the machine beat the official text in the judge's eyes.
Reports direct counts + reverse counts (position control) and a sign check
against chrF (results/chrf_freebsd.md, 83.6–84.7).

Output: results/pairwise_freebsd.md / .csv
Usage: pairwise_freebsd_report.py [--csv PATH] [--out-prefix PATH]
"""
import argparse, csv
from collections import defaultdict
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"


def base_order(cond):
    head, sep, suffix = cond.partition("__")
    return (head, suffix if sep else "direct")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(RES / "judge_pairwise_freebsd_ref.csv"))
    ap.add_argument("--out-prefix", default=str(RES / "pairwise_freebsd"))
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(a.csv)) if r.get("_status") != "fail"]
    if not rows:
        raise SystemExit(f"no rows in {a.csv}")

    # (machine_condition, judge, order) -> winner counts
    cnt = defaultdict(lambda: defaultdict(int))
    for r in rows:
        cond, order = base_order(r["condition"])
        # strip machine-condition prefix "F_" for readability
        cnt[(cond, r["judge"], order)][r["winner"]] += 1

    lines = ["# Pairwise: машинный вывод FreeBSD vs official RU (C3)", "",
             "Условие A = машинный перевод, B = официальный RU-текст. «A» в verdict —",
             "машина не хуже официального. reverse — контроль позиции (как в C1):",
             "вердикт переложен обратно на условия.", "",
             "| машинное условие | судья | порядок | n | A | tie | B | p vs 0.5 | verdict |",
             "|---|---|---|---|---|---|---|---|---|"]
    out_csv = []
    conds = sorted({k[0] for k in cnt})
    for cond in conds:
        for judge in sorted({k[1] for k in cnt if k[0] == cond}):
            for order in ("direct", "reverse"):
                w = cnt.get((cond, judge, order))
                if not w:
                    continue
                t, b = w.get("tie", 0), w.get("B", 0)
                aa = w.get("A", 0)
                p = stats.binomtest(b, aa + b, 0.5).pvalue if aa + b else float("nan")
                verdict = ("B" if b > aa else "A") if (p == p and p < 0.05) else "tie"
                lines.append(f"| {cond} | {judge} | {order} | {aa + t + b} | {aa} | {t} | "
                             f"{b} | {p:.4f} | {verdict} |")
                out_csv.append({"condition": cond, "judge": judge, "order": order,
                                "n": aa + t + b, "a": aa, "tie": t, "b": b,
                                "p_binom": round(p, 5), "verdict": verdict})
        # pooled over judges, direct order (headline)
        w = defaultdict(int)
        for (c, j, o), v in cnt.items():
            if c == cond and o == "direct":
                for k, x in v.items():
                    w[k] += x
        t, b, aa = w.get("tie", 0), w.get("B", 0), w.get("A", 0)
        p = stats.binomtest(b, aa + b, 0.5).pvalue if aa + b else float("nan")
        verdict = ("B" if b > aa else "A") if (p == p and p < 0.05) else "tie"
        lines.append(f"| **{cond}** | **pooled (direct)** | — | **{aa + t + b}** | **{aa}** | "
                     f"**{t}** | **{b}** | **{p:.4f}** | **{verdict}** |")
        out_csv.append({"condition": cond, "judge": "pooled", "order": "direct",
                        "n": aa + t + b, "a": aa, "tie": t, "b": b,
                        "p_binom": round(p, 5), "verdict": verdict})
        lines.append("")

    lines += ["Чтение: при доминировании официального RU и высоком chrF (83.6–84.7) вывод —",
              "«машинный перевод близок к официальному, но стабильно уступает ему по",
              "суждению судей»; доминирование A или ничьи означали бы, что судья не",
              "различает тексты (ср. null-пробу C1: 40/40 tie при идентичных входах).", ""]

    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    with open(a.out_prefix + ".csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_csv[0]))
        w.writeheader()
        w.writerows(out_csv)
    print(f"wrote {a.out_prefix}.md / .csv ({len(conds)} conditions)")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
