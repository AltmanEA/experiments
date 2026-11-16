#!/usr/bin/env python3
"""chrF of FreeBSD machine outputs vs official RU reference (P-003c / P-005).

Machine translations live in the run layout <runs-dir>/<condition>/<fixture>/rep<k>.md,
references in <reference-dir>/<fixture>.md. chrF is corpus-level per condition x fixture
(averaged over reps), computed with sacrebleu char tokenization.

Run with the analysis venv (needs sacrebleu):
  .venv-analysis/bin/python metrics/chrf.py \
      --runs-dir runs --conditions F_C5_local_nvfp4_think_off F_C6_local_nvfp4_think_on
  .venv-analysis/bin/python metrics/chrf.py --runs-dir runs_freebsd_ref \
      --conditions REF_freebsd_official --self-check   # sanity: reference vs itself

Outputs: results/chrf_<tag>.csv and results/chrf_<tag>.md
"""
import argparse, csv, statistics, sys
from pathlib import Path

import sacrebleu

ROOT = Path(__file__).resolve().parent.parent


def read_md(p: Path) -> str:
    # One segment per document: collapse newlines to spaces. Markdown markup is
    # kept (char-level metric, and references carry the same markup, so it does
    # not skew comparisons).
    return " ".join(p.read_text(encoding="utf-8").split())


def chrf_pair(hyp_text: str, ref_text: str) -> float:
    # One segment per document. sacrebleu takes references as a list of
    # reference *streams* (refs[i][seg]), hence the nested list.
    return sacrebleu.corpus_chrf([hyp_text], [[ref_text]]).score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default="runs")
    ap.add_argument("--reference-dir", default="corpus/freebsd-ru/reference")
    ap.add_argument("--fixtures", nargs="*",
                    default=["F1_config", "F2_security", "F3_disks",
                             "F4_network-servers", "F5_firewalls"])
    ap.add_argument("--conditions", nargs="*", required=True)
    ap.add_argument("--reps", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--tag", default="freebsd")
    ap.add_argument("--self-check", action="store_true",
                    help="hyp==ref is allowed (sanity run of the pipeline)")
    a = ap.parse_args()

    runs = Path(a.runs_dir)
    if not runs.is_absolute():
        runs = ROOT / runs
    refs = Path(a.reference_dir)
    if not refs.is_absolute():
        refs = ROOT / refs

    rows = []
    for cond in a.conditions:
        for fx in a.fixtures:
            ref_p = refs / f"{fx}.md"
            if not ref_p.exists():
                sys.exit(f"missing reference: {ref_p}")
            ref_text = read_md(ref_p)
            per_rep = {}
            for k in a.reps:
                hyp_p = runs / cond / fx / f"rep{k}.md"
                if not hyp_p.exists():
                    continue
                per_rep[k] = chrf_pair(read_md(hyp_p), ref_text)
            if not per_rep:
                continue
            vals = list(per_rep.values())
            rows.append({"condition": cond, "fixture": fx,
                         "n_reps": len(vals),
                         "chrf": round(statistics.mean(vals), 2),
                         "chrf_sd": round(statistics.stdev(vals), 2) if len(vals) > 1 else 0.0,
                         **{f"rep{k}": round(v, 2) for k, v in sorted(per_rep.items())}})
            flag = "  <-- hyp==ref!" if (not a.self_check and (runs / cond / fx / f"rep{a.reps[0]}.md").resolve() == ref_p.resolve()) else ""
            print(f"{cond:36s} {fx:20s} chrF={statistics.mean(vals):6.2f} sd={statistics.stdev(vals) if len(vals) > 1 else 0.0:5.2f}{flag}")

    if not rows:
        print("no (condition, fixture) pairs found with both hyp and ref")
        return 1

    out_csv = ROOT / "results" / f"chrf_{a.tag}.csv"
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # condition-level summary (mean over fixtures)
    by_cond = {}
    for r in rows:
        by_cond.setdefault(r["condition"], []).append(r["chrf"])
    out_md = ROOT / "results" / f"chrf_{a.tag}.md"
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write(f"# chrF vs official RU reference ({a.tag})\n\n")
        fh.write("Metric: sacrebleu corpus chrF (beta=2, char n-grams 1..6),\n")
        fh.write("one document per unit; condition value = mean over fixtures.\n\n")
        fh.write("| condition | mean chrF | min fixture | max fixture |\n|---|---|---|---|\n")
        for c, v in sorted(by_cond.items(), key=lambda kv: -statistics.mean(kv[1])):
            fh.write(f"| {c} | {statistics.mean(v):.2f} | {min(v):.2f} | {max(v):.2f} |\n")
        fh.write("\n## Per fixture\n\n| condition | " + " | ".join(a.fixtures) + " |\n")
        fh.write("|---" * (len(a.fixtures) + 1) + "|\n")
        idx = {(r["condition"], r["fixture"]): r["chrf"] for r in rows}
        for c in sorted(by_cond):
            cells = [f"{idx.get((c, fx), float('nan')):.2f}" if (c, fx) in idx else "—"
                     for fx in a.fixtures]
            fh.write(f"| {c} | " + " | ".join(cells) + " |\n")
    print(f"wrote {out_csv} ({len(rows)} rows)\nwrote {out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
