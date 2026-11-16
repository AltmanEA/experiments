#!/usr/bin/env python3
"""B1: human-vs-judge Cohen's kappa for D9 (PLAN.md §6.2, PLAN-CLOSEOUT.md B1).

Turns the blind human answers (annotation/d9/answers.csv) into a human score with the
same MQM weights as the judges (critical*25 + major*10 + minor*2, floor 0), maps to the
same bands as judge_agreement.py, and reports:
  - quadratic-weighted Cohen's kappa (bands) human vs mean-of-judges, and vs each judge;
  - binary kappa on ">=1 critical";
  - judge recall on human-critical runs (how many human-critical runs the judge flagged);
  - the same, restricted to tier2 (free-check, no candidate framing) — the
    bias-control replication;
  - bootstrap 95 % CI (20 000, seed 20261116).

Protocol: answers.csv must be frozen first — metrics/d9_interview.py prints its sha256;
run `python3 d9_agreement.py --freeze` BEFORE opening annotation/d9/manifest_key.json.
This script refuses to compute if the csv changed after the freeze stamp.

Writes results/d9_agreement.md / .csv.

Usage: python3 metrics/d9_agreement.py [--freeze]
"""
import argparse, csv, hashlib, json, re, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "annotation" / "d9"
RESULTS = ROOT / "results"
JUDGE_ABS = ROOT / "judge" / "absolute"
JUDGES = ["gpt-oss-120b", "gemma-4-31b"]
SEV_W = {"1": 2, "2": 10, "3": 25}
BANDS = [(95, 101, "A"), (85, 95, "B"), (70, 85, "C"), (50, 70, "D"), (-1, 50, "E")]
SEED, NBOOT = 20261116, 20000

sys.path.insert(0, str(ROOT / "metrics"))
from judge_agreement import band, weighted_kappa  # same bands/weights as P-003c


def human_score(x):
    """Score from human answers: confirmed candidates + free additions."""
    w = []
    sev = {}
    for r in ANSWERS.get(x, []):
        if r["q"].startswith("cand:") and r["answer"] == "д":
            cid = r["q"].split(":", 1)[1]
            s = next((r2["answer"] for r2 in ANSWERS[x] if r2["q"] == f"sev:{cid}"), None)
            if s:
                w.append(SEV_W[s])
                if s == "3":
                    sev["crit"] = True
        elif r["q"] == "free":
            # numeric format: "0" or severities "3", "3,2", "3 2"
            for ch in re.split(r"[,\s]+", r["answer"].strip()):
                if ch in SEV_W:
                    w.append(SEV_W[ch])
                    if ch == "3":
                        sev["crit"] = True
                elif ch and ";" in ch:
                    # legacy/inline text format: type;severity[;quote]
                    bits = [b.strip() for b in ch.split(";")]
                    if len(bits) >= 2 and bits[1] in SEV_W:
                        w.append(SEV_W[bits[1]])
                        if bits[1] == "3":
                            sev["crit"] = True
    return max(0, 100 - sum(w)), bool(sev.get("crit")), len(w)


def judge_scores(cond, fix, rep):
    """Per-judge scores + mean + any-critical flag, from judge/absolute/<cond>/<fix>/<rep>.<judge>.json."""
    out = {}
    crit = {}
    for j in JUDGES:
        f = JUDGE_ABS / cond / fix / f"{rep}.{j}.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            out[j] = data.get("score")
            crit[j] = int(any(d.get("severity") == "critical" for d in data.get("defects", [])))
    vals = [v for v in out.values() if v is not None]
    out["mean"] = sum(vals) / len(vals) if vals else None
    out["crit"] = max(crit.values()) if crit else 0
    return out


def boot_ci(rows, key):
    """Bootstrap CI for weighted kappa on (human_band, judge_band) pairs."""
    pairs = [(r["h_band"], r[key + "_band"]) for r in rows if r.get(key + "_band")]
    if len(pairs) < 3:
        return None
    cats = {b for p in pairs for b in p}
    rng = np.random.default_rng(SEED)
    kappas = []
    for _ in range(NBOOT):
        idx = rng.integers(0, len(pairs), len(pairs))
        kappas.append(weighted_kappa([pairs[i] for i in idx], cats))
    lo, hi = np.percentile(kappas, [2.5, 97.5])
    return weighted_kappa(pairs, cats), float(lo), float(hi), len(pairs)


def binary_kappa(pairs):
    cats = {"0", "1"}
    return weighted_kappa(pairs, cats)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    a = ap.parse_args()

    csv_path = OUT / "answers.csv"
    stamp = OUT / "answers_frozen.sha256"
    if not csv_path.exists():
        sys.exit(f"нет {csv_path} — сначала пройдите интервью (d9_interview.py)")
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if a.freeze:
        stamp.write_text(digest + "\n", encoding="utf-8")
        print(f"answers.csv заморожен: sha256={digest}")
        print("теперь можно вскрывать manifest_key.json и запускать согласие без --freeze")
        return
    if not stamp.exists():
        sys.exit("ответы не заморожены: сначала --freeze, затем вскрытие ключа")
    if stamp.read_text().strip() != digest:
        sys.exit("answers.csv изменён после freeze — переморозьте и перепроверьте слепоту")

    ANSWERS.clear()
    with csv_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ANSWERS[r["x"]].append(r)

    key = json.loads((OUT / "manifest_key.json").read_text(encoding="utf-8"))["runs"]
    pub = {r["x"]: r for r in json.loads((OUT / "sample_manifest.json").read_text(encoding="utf-8"))["runs"]}

    rows = []
    for k in key:
        x, cond, fix, rep = k["x"], k["condition"], k["fixture"], k["rep"]
        if x not in ANSWERS:
            continue
        hs, hcrit, n = human_score(x)
        js = judge_scores(cond, fix, rep)
        rows.append({"x": x, "condition": cond, "fixture": fix, "rep": rep,
                     "tier": pub[x]["tier"], "human_score": hs, "human_defects": n,
                     "human_crit": int(hcrit), "judge_mean": js["mean"],
                     "judge_gptoss": js.get("gpt-oss-120b"), "judge_gemma": js.get("gemma-4-31b"),
                     "h_band": band(int(hs)), "mean_band": band(int(js["mean"])) if js["mean"] is not None else None,
                     "gptoss_band": band(int(js["gpt-oss-120b"])) if js.get("gpt-oss-120b") is not None else None,
                     "gemma_band": band(int(js["gemma-4-31b"])) if js.get("gemma-4-31b") is not None else None,
                     "judge_crit": js["crit"]})

    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "d9_agreement.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    out = ["# D9: слепая ручная разметка vs судьи (B1, PLAN §6.2)", "",
           f"Прогонов размечено: **{len(rows)}** (tier1 {sum(r['tier'] == 1 for r in rows)}, "
           f"tier2 {sum(r['tier'] == 2 for r in rows)}), seed "
           f"{json.loads((OUT / 'sample_manifest.json').read_text())['seed']}.",
           f"Ответы: sha256 {digest[:16]}… (заморожены до вскрытия ключа).",
           "Человеческий score: те же веса MQM (25/10/2), те же полосы A–E, что в P-003c.", ""]

    for key_name, label in [("mean", "средний судья (2)"), ("gptoss", "gpt-oss-120b"),
                            ("gemma", "gemma-4-31b")]:
        res = boot_ci(rows, key_name)
        if res:
            k, lo, hi, n = res
            out.append(f"- **κ (bands, weighted) человек vs {label}: {k:.3f}** "
                       f"[95 % CI {lo:.3f}…{hi:.3f}], n={n}")
    # tier2 replication
    t2 = [r for r in rows if r["tier"] == 2]
    res = boot_ci(t2, "mean")
    if res:
        k, lo, hi, n = res
        out.append(f"- **tier2 (free-check, без кандидатов) κ человек vs средний судья: "
                   f"{k:.3f}** [CI {lo:.3f}…{hi:.3f}], n={n} — контроль candidate-framing")

    bp = [(str(int(r["human_crit"])), str(int(r["judge_crit"]))) for r in rows]
    out.append(f"- κ «≥1 critical» (человек vs средний судья): {binary_kappa(bp):.3f}")
    hc = [r for r in rows if r["human_crit"]]
    if hc:
        rec = sum(r["judge_crit"] for r in hc) / len(hc)
        out.append(f"- recall судьи на человеческих critical: **{rec:.0%}** ({sum(r['judge_crit'] for r in hc)}/{len(hc)})")
    out += ["", "## Попрогонно", "",
            "| X | tier | условие | фикстура | чел. score | полоса | судья (mean) | полоса | чел. crit | судья crit |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['x']} | {r['tier']} | {r['condition']} | {r['fixture']} | "
                   f"{r['human_score']} | {r['h_band']} | {r['judge_mean']:.1f} | {r['mean_band']} | "
                   f"{r['human_crit']} | {r['judge_crit']} |")
    (RESULTS / "d9_agreement.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


ANSWERS = defaultdict(list)

if __name__ == "__main__":
    main()
