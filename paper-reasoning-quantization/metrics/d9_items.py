#!/usr/bin/env python3
"""B1 v3: item-level verification questions (методика «спроси про конкретный фрагмент»).

Problem with v1/v2: block-level "any distortions here?" forces the annotator to invent an
answer. v3 asks about ONE concrete fragment per question, quoting both sides:

  «EN: `escalation_reason`  →  RU: `эскалация_reason`. Искажение?»   answer: 0 / 1 / 2 / 3

Item types (2–6 per run, mixed order, ~40 % are controls):
  token_ok    EN code token rendered identically      — control, correct answer 0
  token_bad   code token altered (diff shown)         — positive control, answer ≥2
  num_ok      number present unchanged                — control, 0
  num_bad     number altered/lost (both sides shown)  — positive control, 3
  term_ok     glossary term rendered with required RU — control, 0
  term_wrong  glossary term rendered otherwise        — answer ≥2
  phrase      judge-flagged span: EN line vs RU line  — MAIN SIGNAL (human decides)
  open        «ещё искажения, не перечисленные выше?» — keeps a recall channel (0/severity)

Controls measure annotator care (acquiescence / laziness) and are reported separately;
kappa is computed on non-control items only.

Outputs annotation/d9/v3/items.json, annotation/d9/v3/Q<i>_<k>.md (relay verbatim).
Usage: python3 d9_items.py [--runs 30] [--max-items 5] [--seed 20261116] [--force]
"""
import argparse, json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "metrics"))
from defects import code_tokens, num_tokens, parse_glossary, strip_code

OUT = ROOT / "annotation" / "d9" / "v3"
JUDGE_ABS = ROOT / "judge" / "absolute"
JUDGES = ["gpt-oss-120b", "gemma-4-31b"]
GLOSSARY = ROOT / "corpus" / "glossary_council_2026-11-11.md"
SEV_ANSWER = "0 = не искажение; 1 = minor; 2 = major; 3 = critical."


def blocks_pair(text):
    """[(en_line, ru_line)] naive alignment by non-empty line index within paragraph blocks."""
    return text


def en_ru_pairs(en, ru):
    """Align lines by ordinal position of non-empty lines (documents are structurally parallel
    translations of the same fixture; used only to give context, never to decide a defect)."""
    el = [l for l in en.splitlines() if l.strip()]
    rl = [l for l in ru.splitlines() if l.strip()]
    return list(zip(el, rl))


def term_present(ru_low, eq):
    stem = re.sub(r"[.,;:]$", "", eq.lower().split()[0]) if eq else ""
    key = stem[: max(4, len(stem) - 1)] if len(stem) > 4 else stem
    return bool(key) and key in ru_low


def build_items(x, cond, fix, rep, en, ru, rng):
    items = []
    ru_low = ru.lower()

    # ---- code tokens: identical vs altered
    en_t, ru_t = sorted(code_tokens(en)), code_tokens(ru)
    ru_set = set(ru_t)
    ok_tokens = [t for t in en_t if t in ru_set and len(t) <= 40]
    bad_tokens = [t for t in en_t if t not in ru_set and len(t) <= 40]
    for t in rng.sample(ok_tokens, min(1, len(ok_tokens))):
        items.append({"type": "token_ok", "control": "neg", "en": f"`{t}`", "ru": f"`{t}`",
                      "q": f"EN-токен `{t}` должен остаться без изменений. В переводе он передан "
                           f"как `{t}`. Это искажение?"})
    for t in bad_tokens[:1]:
        near = min(ru_t, key=lambda r: -len(set(t) & set(r))) if ru_t else ""
        items.append({"type": "token_bad", "control": "pos", "en": f"`{t}`", "ru": f"`{near}`",
                      "q": f"EN-токен `{t}` должен остаться без изменений. Ближайшее написание "
                           f"в переводе — `{near}` (точного нет). Это искажение?"})

    # ---- numbers
    en_n, ru_n = num_tokens(en), num_tokens(ru)
    ok_nums = [k for k in en_n if ru_n.get(k, 0) >= 1 and len(k) <= 12]
    bad_nums = [k for k, c in en_n.items() if ru_n.get(k, 0) < c and len(k) <= 12]
    for k in rng.sample(ok_nums, min(1, len(ok_nums))):
        items.append({"type": "num_ok", "control": "neg", "en": k, "ru": k,
                      "q": f"В EN есть число `{k}`. В переводе оно передано как `{k}`. "
                           f"Это искажение?"})
    for k in bad_nums[:1]:
        items.append({"type": "num_bad", "control": "pos", "en": k, "ru": "не найдено",
                      "q": f"В EN есть число `{k}`. В переводе такое написание не встречается. "
                           f"Это искажение?"})

    # ---- glossary terms
    gloss = parse_glossary(GLOSSARY)
    en_nc = strip_code(en)
    found = [(t, e) for t, e in gloss.items()
             if re.search(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", en_nc, re.I)]
    good = [(t, e) for t, e in found if term_present(ru.lower(), e)]
    wrong = [(t, e) for t, e in found if not term_present(ru.lower(), e)]
    for t, e in rng.sample(good, min(1, len(good))):
        items.append({"type": "term_ok", "control": "neg", "en": t, "ru": e,
                      "q": f"Термин «{t}» по глоссарию передаётся как «{e}». Встречается в EN-блоке. "
                           f"В переводе «{e}» присутствует. Это искажение?"})
    for t, e in wrong[:1]:
        items.append({"type": "term_wrong", "control": "pos", "en": t, "ru": f"нет «{e}»",
                      "q": f"Термин «{t}» по глоссарию требуется передавать как «{e}». "
                           f"В переводе этого слова нет. Это искажение?"})

    # ---- judge-flagged spans: MAIN SIGNAL (quote + its EN counterpart)
    pairs = en_ru_pairs(en, ru)
    flagged = []
    for j in JUDGES:
        f = JUDGE_ABS / cond / fix / f"{rep}.{j}.json"
        if f.exists():
            for d in json.loads(f.read_text(encoding="utf-8")).get("defects", []):
                q = (d.get("quote") or "").strip()
                if q and len(q) <= 90:
                    flagged.append((q, d.get("description") or ""))
    seen = set()
    for q, desc in flagged:
        if q in seen or len(items) >= 5:
            continue
        seen.add(q)
        # locate the RU line and the positionally aligned EN line (context only)
        ru_line = next((l for l in ru.splitlines() if q in l), None)
        if not ru_line:
            continue
        idx = ru.splitlines().index(ru_line)
        rl = [l for l in ru.splitlines() if l.strip()]
        pos = rl.index(ru_line) if ru_line in rl else None
        en_line = pairs[pos][0] if pos is not None and pos < len(pairs) else "(контекст не найден)"
        items.append({"type": "phrase", "control": None, "en": en_line[:200], "ru": ru_line[:200],
                      "q": f"Судья усомнился в этом фрагменте. EN: «{en_line.strip()[:220]}»  \n"
                           f"RU: «{ru_line.strip()[:220]}»  \nУтверждается: {desc[:200]}  \n"
                           f"Это фактическое искажение перевода?"})

    # ---- open channel (1 per run)
    items.append({"type": "open", "control": None, "en": "", "ru": "",
                  "q": "Фактические искажения, которых нет в вопросах выше? "
                       "(изменённые числа/термины, потеря или добавление смысла, порча `кода`, "
                       "лишние строки). Если есть — назовите одно слово или цифру из перевода."})
    # order: open always last, verification items shuffled by caller
    verif = [i for i in items if i["type"] != "open"]
    open_item = [i for i in items if i["type"] == "open"]
    return verif, open_item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-items", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if OUT.exists() and any(OUT.iterdir()) and not a.force:
        sys.exit(f"{OUT} непустая — --force")
    OUT.mkdir(parents=True, exist_ok=True)

    key = json.loads((OUT.parent / "manifest_key.json").read_text(encoding="utf-8"))["runs"]
    rng = random.Random(a.seed)
    all_items, n = [], 0
    for k in key:
        x, cond, fix, rep = k["x"], k["condition"], k["fixture"], k["rep"]
        en = (ROOT / "corpus" / f"{fix}.md").read_text(encoding="utf-8")
        ru = (ROOT / "runs" / cond / fix / f"{rep}.md").read_text(encoding="utf-8")
        items = build_items(x, cond, fix, rep, en, ru, rng)[0][: a.max_items - 1]
        items += build_items(x, cond, fix, rep, en, ru, rng)[1]
        rng.shuffle(items[:-1])
        for i, it in enumerate(items):
            it["qid"] = f"{x}#{i + 1}"
            body = (f"# {it['qid']} (вопрос {i + 1} из {len(items)} по прогону {x})\n\n"
                    f"{it['q']}\n\n{SEV_ANSWER}\n")
            (OUT / f"{x}_{i + 1}.md").write_text(body, encoding="utf-8")
        all_items.append({"x": x, "items": [{kk: it[kk] for kk in
                                            ("qid", "type", "control", "q")} for it in items]})
        n += len(items)
    (OUT / "items.json").write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    types = {}
    for r in all_items:
        for it in r["items"]:
            types[it["type"]] = types.get(it["type"], 0) + 1
    print(f"{len(all_items)} прогонов, {n} вопросов: {types}")


if __name__ == "__main__":
    main()
