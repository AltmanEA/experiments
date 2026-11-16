#!/usr/bin/env python3
"""B1 v4: paragraph-grounded verification cards (built from scratch).

Methodology (final): one CARD = one paragraph, shown as EN block + aligned RU block, plus
ONE concrete question about a specific fragment inside THAT paragraph. No open-ended
questions. Answer = a single digit 0/1/2/3.

Every question quotes both sides and points at a real, checkable object:
  code   «EN `escalation_id` → RU `эскалация_id`. Токен должен остаться байт-в-байт. Искажение?»
  num    «EN «timeout 30» → RU «timeout 3». Число совпадает? Искажение?»
  term   «EN term «Session» (глоссарий → «Сессия») → RU «Сеанс». Искажение?»
  judge  «Судья усомнился: EN «…» → RU «…». Фактическое искажение?»
Controls (correct answer known a priori) are interleaved to measure annotator care and are
reported separately; κ is computed on non-control items.

Alignment: paragraph blocks of the EN fixture vs the RU run, matched by order (they are
structurally parallel translations). If counts differ, unaligned blocks are skipped
(no question is invented without both sides present).

Output: annotation/d9/v4/cards/<x>_<i>.md + items.json (machine key for scoring).
Usage: python3 d9_para.py [--seed 20261116] [--max-per-run 5] [--force]
"""
import argparse, json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "metrics"))
from defects import code_tokens, num_tokens, parse_glossary, strip_code

OUT = ROOT / "annotation" / "d9" / "v4"
JUDGE_ABS = ROOT / "judge" / "absolute"
JUDGES = ["gpt-oss-120b", "gemma-4-31b"]
GLOSSARY = ROOT / "corpus" / "glossary_council_2026-11-11.md"
ANS = "Ответ одной цифрой: 0 = не искажение; 1 = minor; 2 = major; 3 = critical."


def para_blocks(text):
    """Split into paragraph blocks (blank-line separated); heading glued to next block."""
    chunks, cur = [], []
    for ln in text.splitlines():
        if ln.strip():
            cur.append(ln)
        elif cur:
            chunks.append("\n".join(cur)); cur = []
    if cur:
        chunks.append("\n".join(cur))
    blocks, head = [], None
    for c in chunks:
        first = c.splitlines()[0]
        if len(c.splitlines()) == 1 and re.match(r"^#{1,6} ", first):
            head = c; continue
        blocks.append((head + "\n" + c) if head else c)
        head = None
    return blocks


def term_present(ru_low, eq):
    stem = re.sub(r"[.,;:]$", "", eq.lower().split()[0]) if eq else ""
    key = stem[: max(4, len(stem) - 1)] if len(stem) > 4 else stem
    return bool(key) and key in ru_low


def nearest_token(ru_tokens, t):
    if not ru_tokens:
        return ""
    return max(ru_tokens, key=lambda r: len(set(r.lower()) & set(t.lower())) - abs(len(r) - len(t)))


def questions_for_pair(en_b, ru_b, gloss, judge_spans, rng):
    """Concrete, checkable questions about fragments inside THIS paragraph pair."""
    qs = []
    ru_low = ru_b.lower()
    en_t, ru_t = code_tokens(en_b), code_tokens(ru_b)
    en_n, ru_n = num_tokens(en_b), num_tokens(ru_b)
    en_nc = strip_code(en_b)

    # code token preserved (control neg) / altered (positive)
    if en_t:
        t = rng.choice(sorted(en_t))
        if t in ru_t:
            qs.append(("code", "neg", f"Токен кода должен остаться без изменений (байт в байт). "
                       f"EN `{t}` → RU `{t}`. Это искажение?", t, t))
        else:
            near = nearest_token(sorted(ru_t), t)
            qs.append(("code", "pos", f"Токен кода должен остаться без изменений (байт в байт). "
                       f"EN `{t}` → в RU дословно нет, ближайшее `{near}`. Это искажение?", t, near))

    # number preserved (control neg) / lost (positive)
    if en_n:
        k = rng.choice(sorted(en_n))
        if ru_n.get(k, 0) >= 1:
            qs.append(("num", "neg", f"Числа/идентификаторы должны совпадать. "
                       f"EN `{k}` → RU `{k}`. Это искажение?", k, k))
        else:
            qs.append(("num", "pos", f"Числа/идентификаторы должны совпадать. "
                       f"EN `{k}` → в RU такое написание не встречается. Это искажение?", k, ""))

    # glossary term (only if the EN term occurs in this paragraph, prose only)
    found = [(t, e) for t, e in gloss.items()
             if re.search(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", en_nc, re.I)]
    if found:
        t, e = rng.choice(sorted(found))
        if term_present(ru_low, e):
            qs.append(("term", "neg", f"По глоссарию термин «{t}» передаётся как «{e}». "
                       f"Здесь EN «{t}» → RU содержит «{e}». Это искажение?", t, e))
        else:
            qs.append(("term", "pos", f"По глоссарию термин «{t}» требуется передавать как «{e}». "
                       f"Здесь EN «{t}» → в RU слова «{e}» нет. Это искажение?", t, ""))

    # judge-flagged span located in this paragraph (main signal, answer unknown)
    for q in judge_spans:
        if q[:40] and (q[:40] in ru_b or any(w in ru_b for w in q.split()[:4] if len(w) > 4)):
            qs.append(("judge", None, f"Судья усомнился в фрагменте ниже. Это фактическое "
                       f"искажение перевода?", q[:160], q[:160]))
            break
    return qs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--max-per-run", type=int, default=5)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if OUT.exists() and any(OUT.iterdir()) and not a.force:
        sys.exit(f"{OUT} непустая — --force")
    (OUT / "cards").mkdir(parents=True, exist_ok=True)

    gloss = parse_glossary(GLOSSARY)
    key = json.loads((ROOT / "annotation/d9/manifest_key.json").read_text(encoding="utf-8"))["runs"]
    rng = random.Random(a.seed)
    runs_out, nq = [], 0

    for k in key:
        x, cond, fix, rep = k["x"], k["condition"], k["fixture"], k["rep"]
        en = (ROOT / "corpus" / f"{fix}.md").read_text(encoding="utf-8")
        ru = (ROOT / "runs" / cond / fix / f"{rep}.md").read_text(encoding="utf-8")
        be, br = para_blocks(en), para_blocks(ru)
        # judge spans (quote text only, no severity) for this run
        spans = []
        for j in JUDGES:
            f = JUDGE_ABS / cond / fix / f"{rep}.{j}.json"
            if f.exists():
                spans += [d.get("quote", "").strip() for d in
                          json.loads(f.read_text(encoding="utf-8")).get("defects", []) if d.get("quote")]

        pool = []  # (kind, control, qtext, en_block, ru_block)
        for en_b, ru_b in zip(be, br):          # only aligned paragraphs
            for kind, ctrl, qt, frag_en, frag_ru in questions_for_pair(en_b, ru_b, gloss, spans, rng):
                pool.append({"kind": kind, "control": ctrl, "q": qt,
                             "en": en_b, "ru": ru_b, "frag_en": frag_en, "frag_ru": frag_ru})
        rng.shuffle(pool)
        chosen = pool[: a.max_per_run]
        # guarantee at least one positive control if any exists
        if chosen and not any(c["control"] == "pos" for c in chosen):
            pos = [p for p in pool if p["control"] == "pos"]
            if pos:
                chosen[-1] = pos[0]
        items = []
        for i, c in enumerate(chosen, 1):
            qid = f"{x}#{i}"
            card = (f"# {qid} — абзац {i}\n\n"
                    f"**EN:**\n\n> " + c["en"].replace("\n", "\n> ") + "\n\n"
                    f"**RU:**\n\n> " + c["ru"].replace("\n", "\n> ") + "\n\n"
                    f"**Вопрос.** {c['q']}\n\n{ANS}\n")
            (OUT / "cards" / f"{x}_{i}.md").write_text(card, encoding="utf-8")
            items.append({"qid": qid, "kind": c["kind"], "control": c["control"],
                          "frag_en": c["frag_en"], "frag_ru": c["frag_ru"], "q": c["q"]})
        runs_out.append({"x": x, "n": len(items), "items": items})
        nq += len(items)

    (OUT / "items.json").write_text(json.dumps(runs_out, ensure_ascii=False, indent=2), encoding="utf-8")
    kinds, ctrl = {}, {"neg": 0, "pos": 0}
    for r in runs_out:
        for it in r["items"]:
            kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
            if it["control"]:
                ctrl[it["control"]] += 1
    print(f"{len(runs_out)} прогонов, {nq} карточек; по типам {kinds}; контроль neg/pos = {ctrl['neg']}/{ctrl['pos']}")


if __name__ == "__main__":
    main()
