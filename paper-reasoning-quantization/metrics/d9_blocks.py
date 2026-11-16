#!/usr/bin/env python3
"""B1 v2: block-wise blind D9 interview (methodology: one paragraph, one question, one digit).

Takes the frozen B1 sample (annotation/d9/sample_manifest.json + manifest_key.json — key is
read here only to locate run files, never printed) and cuts each run into paragraph blocks
aligned with the EN fixture. Each block becomes ONE question:

    Q: «В этом блоке есть фактические искажения? (числа, термины, потеря/добавление
       смысла, порча `кода`, лишние строки)»
    A: 0 = нет; 1/2/3 = minor/major/critical. Несколько — через запятую ("3,2").

Blocks over MAX_LINES lines are split in halves (one question still). If RU has extra
blocks vs EN (added content / leakage), each extra block gets its own card asking whether
the content belongs here. If EN blocks are missing from RU, an omission card is generated
for each.

Outputs:
  annotation/d9/v2/cards/X<k>_<b>.md   one block pair + one question (relay verbatim)
  annotation/d9/v2/order.json          presentation order per run (block shuffle, fixed seed)
  annotation/d9/v2/answers.csv         x, block, answer  (appended by d9_blockint.py)

Usage: python3 d9_blocks.py [--force]
"""
import argparse, json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "annotation" / "d9" / "v2"
MAX_LINES = 6


def split_blocks(text):
    """Paragraph blocks; a heading attaches to the following chunk; blank runs skipped."""
    chunks, cur = [], []
    for ln in text.splitlines():
        if ln.strip():
            cur.append(ln)
        elif cur:
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    blocks, head = [], None
    for ch in chunks:
        if len(ch) == 1 and re.match(r"^#{1,6} ", ch[0]):
            head = ch[0]; continue
        b = ch[:]
        if head:
            b = [head] + b; head = None
        blocks.append("\n".join(b))
    return blocks


def cap(blocks):
    out = []
    for b in blocks:
        lines = b.splitlines()
        if len(lines) <= MAX_LINES:
            out.append(b)
        else:
            mid = len(lines) // 2
            out.append("\n".join(lines[:mid]))
            out.append("\n".join(lines[mid:]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if OUT.exists() and any(OUT.iterdir()) and not a.force:
        sys.exit(f"{OUT} непустая — --force для пересборки")
    OUT.mkdir(parents=True, exist_ok=True)

    key = {r["x"]: r for r in json.loads((OUT.parent / "manifest_key.json").read_text(encoding="utf-8"))["runs"]}
    order_rng = random.Random(20261116)
    order = {}

    for x in sorted(key, key=lambda s: int(s[1:])):
        k = key[x]
        en = (ROOT / "corpus" / f"{k['fixture']}.md").read_text(encoding="utf-8")
        ru = (ROOT / "runs" / k["condition"] / k["fixture"] / f"{k['rep']}.md").read_text(encoding="utf-8")
        be, br = cap(split_blocks(en)), cap(split_blocks(ru))
        cards = []

        n = min(len(be), len(br))
        for i in range(n):
            q = ("В этом блоке перевода есть фактические искажения? (изменённые числа, "
                 "подмена терминов, потеря/добавление смысла, порча `кода`, лишние строки)\n"
                 "Ответ — цифра: 0 = нет; 1 = minor; 2 = major; 3 = critical. "
                 "Несколько — через запятую (3,2).")
            cards.append({"b": i + 1, "kind": "pair", "en": be[i], "ru": br[i], "q": q})
        for i in range(n, len(be)):  # EN blocks with no RU counterpart
            q = ("Этот блок EN-источника отсутствует в переводе. Пропуск значимого "
                 "содержания — какой severity? (если блок не значим — 0)\n0/1/2/3.")
            cards.append({"b": i + 1, "kind": "en_only", "en": be[i], "ru": None, "q": q})
        for j in range(n, len(br)):  # RU extras
            q = ("Этот фрагмент перевода есть в RU, но нет в EN-источнике. Лишний контент — "
                 "какой severity? (если это допустимое оформление — 0)\n0/1/2/3.")
            cards.append({"b": len(be) + (j - n) + 1, "kind": "ru_only", "en": None, "ru": br[j], "q": q})

        seq = order_rng.sample(range(1, len(cards) + 1), len(cards))
        # present shuffled block order per run (order.json, not visible to annotator as key)
        for c in cards:
            body = [f"# {x} · блок {c['b']} · вопрос {c['b']} из {len(cards)}", ""]
            if c["en"]:
                body += ["**EN:**", "", ">>>", c["en"], "<<<", ""]
            if c["ru"]:
                body += ["**RU:**", "", ">>>", c["ru"], "<<<", ""]
            if c["kind"] == "en_only":
                body += ["**RU: блок отсутствует в переводе.**", ""]
            if c["kind"] == "ru_only":
                body += ["**EN: фрагмент отсутствует в источнике.**", ""]
            body += ["", c["q"]]
            (OUT / f"{x}_{c['b']:02d}.md").write_text("\n".join(body) + "\n", encoding="utf-8")
        order[x] = {"n_cards": len(cards), "present": seq,
                    "stats": {"en_blocks": len(be), "ru_blocks": len(br)}}

    (OUT / "order.json").write_text(json.dumps(order, ensure_ascii=False, indent=2), encoding="utf-8")
    tot = sum(o["n_cards"] for o in order.values())
    mism = [x for x, o in order.items() if o["stats"]["en_blocks"] != o["stats"]["ru_blocks"]]
    print(f"{len(order)} прогонов, {tot} блок-карточек, несовпадение числа блоков: {mism or 'нет'}")


if __name__ == "__main__":
    main()
