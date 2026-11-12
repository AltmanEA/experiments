#!/usr/bin/env python3
"""Build EN->RU glossary pair lists for the LLM judge (PLAN.md §6.2).

The judge must know which Russian equivalent each English term is required to
get. Pairs are extracted from docs/en/glossary/index.md entries of the form

    **Term** (Русский эквивалент) Definition...

Two outputs:
  corpus/gloss_pairs.txt        all 54 pairs (reference / fallback);
  corpus/gloss_pairs/S8.txt     pairs whose EN term occurs in fixture S8, i.e.
                                the same algorithmic per-document filtering the
                                translation pipeline applies. Terms without a
                                Russian equivalent are skipped, never invented.

Usage: make_gloss_pairs.py [--glossary PATH] [--out-dir corpus]
"""
import argparse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIR = re.compile(r"^\*\*(?P<en>[^*]+?)\*\*\s*\((?P<ru>[^)]+)\)", re.M)
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")

def load(glossary):
    pairs = []
    for m in PAIR.finditer(Path(glossary).read_text(encoding="utf-8")):
        en, ru = m.group("en").strip(), m.group("ru").strip()
        if en and ru:
            pairs.append((en, ru))
    return pairs

def relevant(pairs, text):
    low = text.lower()
    hits = []
    for en, ru in pairs:
        # whole-word, case-insensitive; plural/gerund forms of the term also count
        stem = re.escape(en.lower())
        if re.search(rf"(?<![a-z]){stem}(?:s|es|ed|ing)?(?![a-z])", low):
            hits.append((en, ru))
    return hits

def render(pairs):
    head = ("# EN term -> required RU equivalent (algorithmically extracted from "
            "docs/en/glossary/index.md)\n")
    return head + "".join(f"{en} -> {ru}\n" for en, ru in pairs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glossary", default=str(ROOT.parent.parent / "docs/en/glossary/index.md"))
    ap.add_argument("--out-dir", default=str(ROOT / "corpus"))
    a = ap.parse_args()

    pairs = load(a.glossary)
    out = Path(a.out_dir)
    (out / "gloss_pairs").mkdir(parents=True, exist_ok=True)
    (out / "gloss_pairs.txt").write_text(render(pairs), encoding="utf-8")
    print(f"all pairs: {len(pairs)} -> {out / 'gloss_pairs.txt'}")

    for fx in sorted(out.glob("S[0-9]*.md")):
        sub = relevant(pairs, fx.read_text(encoding="utf-8"))
        (out / "gloss_pairs" / f"{fx.stem}.txt").write_text(render(sub), encoding="utf-8")
        print(f"  {fx.stem}: {len(sub):2d} pairs")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
