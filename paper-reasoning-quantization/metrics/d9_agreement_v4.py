#!/usr/bin/env python3
"""B1 v4: human-vs-judge agreement for D9 (PLAN.md §6.2, PLAN-CLOSEOUT.md B1).

v4 protocol (annotation/d9/METHOD-v4.md): each card = EN paragraph + aligned RU
paragraph + ONE concrete question; answer 0/1/2/3 (not-a-defect / minor / major /
critical). Card kinds: code | num | term | judge; control kinds: neg (true 0),
pos (planted defect).

Operator decision 2026-11-20: pos-control is DISCARDED as a methodology defect
(the planted-defect instruction shown to the annotator was incorrect — recall
6/23 is an artifact of the cards, not of the annotator). Agreement conclusions
use ONLY:
  - main signal: 24 `judge`-kind cards (no preset answer), and
  - neg-control as a quality gate (2.9 % errors, threshold 15 %).

Human run score: MQM weights 2/10/25 per severity answer on MAIN cards only
(controls excluded from the sum), same as judge MQM: score = max(0, 100 - sum).
Bands A-E from judge_agreement.py (same cuts as P-003c). Reports:
  - quadratic weighted Cohen's kappa on bands, human vs mean judge / each judge
    (bootstrap 20 000, seed 20261116);
  - binary kappa on ">=1 critical" + judge recall on human-critical runs;
  - neg-control accuracy and (discarded) pos-control recall, for transparency;
  - fragment-level judge precision: share of the 24 judge-doubted fragments the
    human confirmed as defects (the only human-vs-judge quantity this card design
    can identify — band kappa is reported but is structurally biased toward 0
    because a run has ~0.8 main cards vs a whole-output judge score).

Refuses to compute unless answers.csv matches the freeze stamp
(annotation/d9/v4/answers_frozen.sha256, written by d9_answer.py --freeze
BEFORE opening manifest_key.json).

Writes results/d9_agreement.md / .csv (v4 layout).

Usage: python3 metrics/d9_agreement_v4.py
"""
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
V4 = ROOT / "annotation" / "d9" / "v4"
KEY = ROOT / "annotation" / "d9" / "manifest_key.json"
RESULTS = ROOT / "results"
JUDGE_ABS = ROOT / "judge" / "absolute"
JUDGES = ["gpt-oss-120b", "gemma-4-31b"]
SEV_W = {"1": 2, "2": 10, "3": 25}
SEED, NBOOT = 20261116, 20000
NEG_GATE = 0.15

sys.path.insert(0, str(ROOT / "metrics"))
from judge_agreement import band, weighted_kappa  # same bands/weights as P-003c


def load_answers():
    csv_path = V4 / "answers.csv"
    stamp = V4 / "answers_frozen.sha256"
    if not stamp.exists():
        sys.exit("ответы не заморожены: сначала d9_answer.py --freeze, затем вскрытие ключа")
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if stamp.read_text().strip() != digest:
        sys.exit("answers.csv изменён после freeze — переморозьте и перепроверьте слепоту")
    ans = {}
    with csv_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ans[r["qid"]] = r["answer"]
    return ans, digest


def judge_scores(cond, fix, rep):
    out, crit = {}, {}
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


def boot_ci(pairs):
    if len(pairs) < 3:
        return None
    cats = {b for p in pairs for b in p}
    if len(cats) < 2:
        return None
    rng = np.random.default_rng(SEED)
    ks = [weighted_kappa([pairs[i] for i in rng.integers(0, len(pairs), len(pairs))], cats)
          for _ in range(NBOOT)]
    lo, hi = np.percentile(ks, [2.5, 97.5])
    return weighted_kappa(pairs, cats), float(lo), float(hi), len(pairs)


def main():
    ans, digest = load_answers()
    items = json.loads((V4 / "items.json").read_text(encoding="utf-8"))
    key = {r["x"]: r for r in json.loads(KEY.read_text(encoding="utf-8"))["runs"]}

    # --- control gate (per METHOD-v4 §2; pos discarded by operator decision) ---
    neg_ok = neg_n = pos_ok = pos_n = 0
    main_cards = Counter()
    cards_by_x = {}
    for it in items:
        for c in it["items"]:
            a = ans.get(c["qid"])
            if a is None:
                sys.exit(f"нет ответа на {c['qid']}")
            if c["control"] == "neg":
                neg_n += 1; neg_ok += (a == "0")
            elif c["control"] == "pos":
                pos_n += 1; pos_ok += (a in ("1", "2", "3"))
            else:  # main signal: control is None, kind == "judge"
                main_cards[c["kind"]] += 1
            cards_by_x.setdefault(it["x"], []).append((c, a))
    neg_err = 1 - neg_ok / neg_n
    if neg_err > NEG_GATE:
        sys.exit(f"neg-контроль: ошибки {neg_err:.1%} > {NEG_GATE:.0%} — разметку не принимать")

    rows = []
    for x in sorted(cards_by_x, key=lambda s: int(s[1:])):
        k = key[x]
        defects = [(c["qid"], c["kind"], a) for c, a in cards_by_x[x]
                   if c["control"] not in ("neg", "pos") and a in SEV_W]
        wsum = sum(SEV_W[a] for _, _, a in defects)
        hs = max(0, 100 - wsum)
        hcrit = any(a == "3" for _, _, a in defects)
        js = judge_scores(k["condition"], k["fixture"], k["rep"])
        if js["mean"] is None:
            sys.exit(f"нет судейских файлов для {x} ({k['condition']}/{k['fixture']}/{k['rep']})")
        rows.append({"x": x, "condition": k["condition"], "fixture": k["fixture"], "rep": k["rep"],
                     "human_score": hs, "human_defects": len(defects),
                     "human_defect_detail": ";".join(f"{q}:{a}" for q, _, a in defects),
                     "human_crit": int(hcrit),
                     "judge_mean": js["mean"], "judge_gptoss": js.get("gpt-oss-120b"),
                     "judge_gemma": js.get("gemma-4-31b"), "judge_crit": js["crit"],
                     "h_band": band(int(hs)),
                     "mean_band": band(int(js["mean"])),
                     "gptoss_band": band(int(js["gpt-oss-120b"])) if js.get("gpt-oss-120b") is not None else None,
                     "gemma_band": band(int(js["gemma-4-31b"])) if js.get("gemma-4-31b") is not None else None})

    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "d9_agreement.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    out = ["# D9: слепая ручная разметка vs судьи (B1, методика v4, PLAN §6.2)", "",
           f"Прогонов размечено: **{len(rows)}** (30 из 483 Council-прогонов, ≈6 %, seed 20261116).",
           f"Ответы: sha256 {digest[:16]}… (заморожены до вскрытия ключа).",
           "Человеческий score: веса MQM 25/10/2 по **main-карточкам** (24 вопроса `judge`,",
           "без контрольных), те же полосы A–E, что в P-003c.", "",
           "**Решение оператора (2026-11-20):** pos-контроль отброшен как дефект описания",
           "методики (инструкция к контрольным карточкам с подставным дефектом была",
           "некорректна; recall 6/23 — артефакт карточек). Выводы — только по main-сигналу;",
           "neg-контроль — гейт качества.", "",
           "## Контроль качества", "",
           f"- neg-контроль (ожидание 0): **{neg_ok}/{neg_n} верно, ошибки {neg_err:.1%}** "
           f"(порог 15 % — пройдены).",
           f"- pos-контроль: {pos_ok}/{pos_n} (recall {pos_ok/pos_n:.0%}) — **отброшен**, "
           "не используется ни в каком выводе.",
           f"- main-карточки (24, тип `judge`): "
           + ", ".join(f"{v}×`{k}`" for k, v in sorted(main_cards.items())) + ".", "",
           "## Согласие человек vs судья (только main-сигнал)", ""]

    for key_name, label in [("mean", "средний судья (2)"), ("gptoss", "gpt-oss-120b"),
                            ("gemma", "gemma-4-31b")]:
        pairs = [(r["h_band"], r[key_name + "_band"]) for r in rows if r.get(key_name + "_band")]
        res = boot_ci(pairs)
        if res:
            k, lo, hi, n = res
            out.append(f"- **κ (полосы, weighted) человек vs {label}: {k:.3f}** "
                       f"[95 % CI {lo:.3f}…{hi:.3f}], n={n}")
        else:
            out.append(f"- κ человек vs {label}: не вычисляется (вырожденное распределение полос)")

    bp = [(str(int(r["human_crit"])), str(int(r["judge_crit"]))) for r in rows]
    out.append(f"- κ «≥1 critical» (человек vs «хотя бы один судья critical»): "
               f"{weighted_kappa(bp, {'0','1'}):.3f}")
    hc = [r for r in rows if r["human_crit"]]
    if hc:
        rec = sum(r["judge_crit"] for r in hc) / len(hc)
        out.append(f"- recall судьи на человеческих critical: **{rec:.0%}** "
                   f"({sum(r['judge_crit'] for r in hc)}/{len(hc)})")
    hc_all = [r for r in rows if r["human_defects"]]
    out.append(f"- прогоны с ≥1 человеческим дефектом: {len(hc_all)} из {len(rows)}; "
               f"распределение человеческих полос: "
               + ", ".join(f"{b}×{c}" for b, c in sorted(Counter(r['h_band'] for r in rows).items())))

    # fragment-level: how did the human judge the fragments the judges doubted?
    frag = []
    for x in sorted(cards_by_x, key=lambda s: int(s[1:])):
        for c, a in cards_by_x[x]:
            if c["control"] not in ("neg", "pos"):
                frag.append((x, c["qid"], a))
    conf = sum(1 for _, _, a in frag if a in ("1", "2", "3"))
    sev3 = sum(1 for _, _, a in frag if a == "3")
    out += ["", "## Фрагментарный уровень (единственный измеримый в v4)", "",
            f"Судьи усомнились в {len(frag)} фрагментах (24 main-карточки); человек",
            f"подтвердил искажение в **{conf}/{len(frag)} = {conf/len(frag):.0%}** "
            f"(из них critical {sev3}), остальные {len(frag)-conf} назвал чистыми.",
            "",
            "**Ограничение интерпретации:** на уровне прогонов κ полос структурно прижат к 0:",
            "у человека на прогон ~0.8 main-карточек (единицы ошибок), у судьи — score по",
            "всему выводу, поэтому человек почти всегда в полосе A. Публикуемый показатель",
            "B1 — фрагментарная точность судей по человеческой проверке выше; κ полос",
            "репортится как есть, без доверия к её величине."]

    out += ["", "## Попрогонно", "",
            "| X | условие | фикстура | rep | чел. score | полоса | чел. дефекты | судья (mean) | полоса | чел. crit | судья crit |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['x']} | {r['condition']} | {r['fixture']} | {r['rep']} | "
                   f"{r['human_score']} | {r['h_band']} | {r['human_defect_detail'] or '—'} | "
                   f"{r['judge_mean']:.1f} | {r['mean_band']} | {r['human_crit']} | {r['judge_crit']} |")
    (RESULTS / "d9_agreement.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
