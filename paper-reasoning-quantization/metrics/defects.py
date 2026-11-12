#!/usr/bin/env python3
"""Defect metrics D1-D7 for paper experiments (PLAN.md §6.1).

Usage:
  python3 defects.py --en EN.md --ru RU.md --log run.log \
      --glossary ../../../docs/en/glossary/index.md [--json out.json]

Deterministic, no-reference metrics. Parsed from: EN source, RU output,
pipeline stderr log, glossary. D9 (factual distortions) stays manual.
NOTE (P-000): calibrate D3-D5/D7 against manual check on S3 before use.
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

ECHO_PATTERNS = [
    r"(?im)^\s*(translation|перевод)\s*[:：]",
    r"(?m)^\s*={3,}\s*$",
    r"(?i)\b(Let's|Wait|I need to|As an AI)\b",  # leaked reasoning (H2)
    r"(?im)^\s*<\|?im_start\|?>",
]

def parse_glossary(path):
    """Return {EN_term: RU_equivalent} from **Term** (RU) entries."""
    pairs = {}
    for m in re.finditer(r"\*\*(.+?)\*\*\s*[（(]([^）)]+)[）)]", Path(path).read_text(encoding="utf-8")):
        en, ru = m.group(1).strip(), m.group(2).strip()
        if en and ru and not ru.startswith("A") :  # RU equivalent, not definition start
            pairs[en] = ru
    return pairs

def code_tokens(text):
    return set(re.findall(r"`([^`\n]+)`", text))

def num_tokens(text):
    return Counter(re.findall(r"\b\d[\d.,:/-]*\w*\b", text))

def list_markers(text):
    return Counter(re.findall(r"(?m)^\s*(\d+\.|[-*])\s", text))

def strip_code(text):
    """Remove inline code spans; terms/enums inside backticks are contract
    tokens (D3), not prose — counting them in D5/D7 creates the P-001 confound."""
    return re.sub(r"`[^`\n]*`", " ", text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", required=True); ap.add_argument("--ru", required=True)
    ap.add_argument("--log", required=True); ap.add_argument("--glossary", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    en = Path(a.en).read_text(encoding="utf-8")
    ru = Path(a.ru).read_text(encoding="utf-8")
    log = Path(a.log).read_text(encoding="utf-8", errors="replace")

    # D1/D2 — pipeline stderr counters
    d = {
        "D1_linecount_fb": len(re.findall(r"\[linecount\]", log)),
        "D2_fix": len(re.findall(r"\[fix\]", log)),
        "D2_fuzz_fix": len(re.findall(r"\[fuzz-fix\]", log)),
        "D2_path_fix": len(re.findall(r"\[path-fix\]", log)),
        "D2_fail": len(re.findall(r"\[FAIL\]", log)),
    }

    # D3 — code-token preservation (EN tokens must appear verbatim in RU)
    en_t, ru_t = code_tokens(en), code_tokens(ru)
    missing = sorted(t for t in en_t if t not in ru_t)
    d["D3_code_total"], d["D3_code_missing"] = len(en_t), missing

    # D4 — numeric/date/identifier preservation (multiset containment)
    en_n, ru_n = num_tokens(en), num_tokens(ru)
    lost = {k: c - ru_n.get(k, 0) for k, c in en_n.items() if c > ru_n.get(k, 0)}
    d["D4_num_total"], d["D4_num_lost"] = sum(en_n.values()), lost

    # D5 — glossary term accuracy: canonical RU equivalent (lowercased) present
    # for EN terms actually occurring in the block (algorithmic filter, not research scope)
    gloss = parse_glossary(a.glossary)
    ru_low = ru.lower()

    def d5(en_text, ru_text_low):
        hits, absent = [], []
        for term, eq in gloss.items():
            if re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", en_text, re.I):
                # prefix match (>=4 chars): RU equivalents decline; full-nominative
                # substring check would miss case forms (see E-007 lemma caveat)
                stem = re.sub(r"[.,;:]$", "", eq.lower().split()[0]) if eq else ""
                key = stem[:max(4, len(stem) - 1)] if len(stem) > 4 else stem
                (hits if key and key in ru_text_low else absent).append(term)
        return hits, absent

    hits, absent = d5(en, ru_low)
    d["D5_terms_found"] = len(hits) + len(absent)
    d["D5_terms_missing"] = absent

    # D5-nc / D7-nc — same metrics on prose only (inline code spans removed).
    # Authoritative variant for research comparisons (P-001 confound fix).
    en_nc, ru_nc_low = strip_code(en), strip_code(ru).lower()
    hits_nc, absent_nc = d5(en_nc, ru_nc_low)
    d["D5_nc_terms_found"] = len(hits_nc) + len(absent_nc)
    d["D5_nc_terms_missing"] = absent_nc

    # D6 — structural artifacts
    d["D6_echo"] = [p for p in ECHO_PATTERNS if re.search(p, ru)]
    en_m, ru_m = list_markers(en), list_markers(ru)
    d["D6_markers_lost"] = {k: c - ru_m.get(k, 0) for k, c in en_m.items() if c > ru_m.get(k, 0)}

    # D7 — contamination traps: RU equivalents of glossary terms whose EN term
    # does NOT occur in block but the RU word appears anyway (E-003 pattern).
    ru_words = {eq.lower() for term, eq in gloss.items()
                if not re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", en, re.I)}
    d["D7_contaminants"] = sorted(w for w in ru_words if w and w in ru_low)
    ru_words_nc = {eq.lower() for term, eq in gloss.items()
                   if not re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", en_nc, re.I)}
    d["D7_nc_contaminants"] = sorted(w for w in ru_words_nc if w and w in ru_nc_low)

    print(json.dumps(d, ensure_ascii=False, indent=2))
    if a.json:
        Path(a.json).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
