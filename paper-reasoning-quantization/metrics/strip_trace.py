#!/usr/bin/env python3
"""Strip leaked reasoning traces from cloud thinking-model output (P-001).

The cloud endpoint qwen3.6-35b-a3b returns its chain of thought inside the
`content` field, interleaved with the translation. This filter removes those
lines post-hoc so quality metrics become comparable with the local thinking
conditions (C4/C6), where the trace goes to a separate channel.

Design constraints:
  * algorithmic and deterministic (no LLM, no per-run tuning, no model call);
  * applied identically to every condition; on clean conditions it must remove
    nothing (checked with --dir over C1/C3..C6);
  * fenced code blocks are never touched; headings, tables and HTML are kept;
  * no Cyrillic prose is dropped unless the line carries an explicit planning
    marker ("Let's", "I'll", "Final:", "Output:", checkmarks).

Rules per line (outside fenced code), after inline code spans are masked:
  R1 marker  - planning/meta word occurs anywhere in the line;
  R2 english - >=4 Latin words and Cyrillic share < 35% of letters
               (reasoning is English, translation is Russian);
  R3 mapping - arrow notation with an English term on the left
               ("Gated transitions" -> "Переходы с затворами").

Usage:
  strip_trace.py --in RU.md --out CLEAN.md [--json STATS.json]
  strip_trace.py --dir runs/COND [--out-dir runs/COND_clean] [--report]
"""
import argparse, difflib, json, re, shutil, sys
from pathlib import Path

CODE_SPAN = re.compile(r"`[^`\n]*`|\\.`")           # inline code / escaped backticks
CYR = re.compile(r"[\u0400-\u04FF]")
LATIN = re.compile(r"[A-Za-z]")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]{1,}")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
TABLE = re.compile(r"^\s*\|")
HTML = re.compile(r"^\s*<[/!a-zA-Z]")
ONLY_CODE = re.compile(r"^\s*(?:[-*+]\s*)?`[^`]*`\s*$")
URL = re.compile(r"https?://\S+")
QUOTED = re.compile(r'"[^"\n]*"|„[^“\n]*“|«[^»\n]*»')
# R9: inline trace tail — cut the line at the first English planning marker
TRACE_CUT = re.compile(r"\s(?=(?:[-—]\s*)?(?:let'?s|let’s|wait\b|hmm\b|actually\b|or\s+literally|but\s+let'?s|i'll|i\s+will|now\s+let|we\s+can\b|this\s+translates?\b)\s)", re.I)
# R10: payload lines ("Final: ...", "Translation: ...") carry the model's real
# answer; under leakage they are the ONLY place the translated row appears, so
# they are unwrapped (payload kept) instead of being dropped.
UNWRAP = re.compile(r"""^\s*(?:[-*+]\s*)?
    (?:final(?:\s+(?:string|answer|output|decision|check|row|table))?|output|translation
      |result|text\s+to\s+output|i(?:'ll|\s+will)\s+output(?:\s+exactly)?)\s*:\s*(.+)$""",
    re.I | re.X)
STUB = re.compile(r"\((?:used|checked|ok)\)\s*$", re.I)

MARKERS = re.compile(r"""(?ix)
   \b(?:let'?s|wait|actually|hmm|okay|i'll|i\s+will|i\s+need|i\s+should
      |let\s+me|verify|double[\s-]check|check(?:\s+specific|\s+the|\s+exact)?\s*:
      |final\s*:|output\s*:|note\s*:|russian\s*:|input\s*:|markdown\s*:
      |translation\s*:|translated\s*:|result\s*:|original\s*:|closer\s+to
      |refined\s*:|check\s+(?:terms|exact\s+words)|so\s*:
      |grammar\s*/\s*style|matches?\s+(?:constraints|perfectly|the|exactly)
      |one\s+minor\s+(?:adjustment|point|change)|the\s+translation|this\s+translates
      |translat(?:e|ing)\s+only|constraints?\s+met|all\s+good|done\.?$
      |proceeds?|output\s+generation|\[self[\s-]correction
      |\[output[^\]]*\]|output\s*->|draft|ready\.?
      |двойная\s+проверка|проверка\s+терминов)(?![A-Za-z])
""")
CHECK = re.compile(r"[✅✔✓☑]")
# R3: term-mapping reasoning lines ("Gated transitions" -> "Переходы с затворами")
ARROW = re.compile(r"->|=>|→")

def is_mapping(probe):
    m = ARROW.search(probe)
    if not m:
        return False
    left = probe[:m.start()]
    latin = len(LATIN_WORD.findall(left))
    cyr = len(CYR.findall(left))
    if cyr / max(1, cyr + latin) > 0.2:
        return False
    quoted = bool(re.search(r'["«„“\']', left))
    return latin >= 2 or (latin >= 1 and quoted)

def letters(line):
    probe = CODE_SPAN.sub(" ", line)
    probe = URL.sub(" ", probe)
    return probe

def skeleton(line):
    """Line with code spans and quoted segments removed: what remains is the
    meta-skeleton of a reasoning line."""
    return QUOTED.sub(" ", letters(line))

BULLET = re.compile(r"^\s*(?:[-*+]\s*)?")
WRAPPED_ROW = re.compile(r"^`\s*\|.*\|\s*`\s*$")

def unwrap(line):
    """Return the payload of a 'Final: <translated fragment>' line, or None."""
    # backticked draft row: `| `x` | yes |`  ->  | `x` | yes |
    bare = BULLET.sub("", line).strip()
    if WRAPPED_ROW.match(bare):
        pay = bare.strip("`").replace("\\`", "`").strip()
        if pay.startswith("|") and CYR.search(pay):
            return pay
    m = UNWRAP.match(line)
    if not m:
        return None
    pay = m.group(1).strip()
    if pay.startswith("|"):                 # markdown row: drop trailing commentary
        k = pay.rfind("|")
        if k > 0:
            pay = pay[:k + 1]
    pay = pay.strip().strip('`"«»„“\'').replace("\\`", "`").strip()
    if len(pay) < 3 or not CYR.search(pay):
        return None
    return pay

def norm(line):
    return re.sub(r"\s+", " ", line).strip()

def classify(line, in_fence, en_lines=frozenset()):
    s = line.strip()
    if in_fence:
        return False, "code"
    if not s:
        return False, "blank"
    if s.startswith("```") or HEADING.match(line) or TABLE.match(line) or HTML.match(line):
        return False, "struct"
    if ONLY_CODE.match(line):
        return False, "code-span-only"
    if norm(line) in en_lines:      # metadata / verbatim fragment from the source
        return False, "en-copy"
    probe = letters(line)
    cyr = len(CYR.findall(probe)); lat = len(LATIN.findall(probe))
    if MARKERS.search(probe) or CHECK.search(probe):
        return True, "marker"
    if is_mapping(probe):
        return True, "mapping"
    # R4: glossary self-check stubs ("Term" -> "Термин" (checked), Term -> Term (used))
    if STUB.search(s):
        return True, "stub"
    # R5: arrow with a quoted pair on either side, no matter the language
    if ARROW.search(probe) and re.search(r'["«„“]', probe) and len(s) <= 120:
        return True, "mapping-quoted"
    # R6: short glossary self-check stub, incl. identity mappings (Term -> Term)
    if ARROW.search(probe) and len(s) <= 60 and not s.rstrip().endswith((".", "|")):
        return True, "stub"
    # R7: whole line is a quoted candidate translation
    if re.fullmatch(r'\s*(?:[-*+]\s*)?"[^"]{20,}"\s*', line):
        return True, "quoted-candidate"
    # R8: punctuation/junk only
    if not re.search(r"[\w\u0400-\u04FF]", s):
        return True, "junk"
    if lat >= 4 and cyr / max(1, cyr + lat) < 0.35:
        return True, "english"
    sk = skeleton(line)
    s_cyr = len(CYR.findall(sk)); s_lat = len(LATIN.findall(sk))
    if s_lat >= 4 and s_cyr / max(1, s_cyr + s_lat) < 0.35:
        return True, "english-skeleton"
    return False, "keep"

def strip(text, en_lines=frozenset(), near_dup=True):
    out, removed, unwrapped = [], [], []
    in_fence = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line); continue
        if not in_fence:
            pay = unwrap(line)
            if pay is not None:
                unwrapped.append({"line": i, "from": line.strip()[:120], "to": pay[:120]})
                line = pay
        drop, why = classify(line, in_fence, en_lines)
        if not drop and not in_fence:
            cut = TRACE_CUT.split(line, 1)
            if len(cut) > 1:
                head = cut[0].rstrip()
                if len(CYR.findall(head)) >= 10:
                    line, why2 = head, "inline-cut"
                else:
                    drop, why = True, "inline-cut"
        if drop:
            probe = letters(line)
            removed.append({"line": i, "why": why, "text": line.strip()[:160],
                            "cyr": len(CYR.findall(probe)), "lat": len(LATIN.findall(probe))})
        else:
            out.append(line)
    if not removed and not unwrapped:
        # nothing to strip: return the document untouched (validation invariant
        # for the clean conditions)
        return text, removed, unwrapped
    # keep the LAST occurrence of a repeated long line: in reasoning traces the
    # final answer follows the intermediate drafts
    spans = [len(re.findall(r"`[^`\n]*`", l)) for l in out]

    def preference(i):        # more code spans wins; ties -> later line
        return (spans[i], i)

    def dedupable(line):
        # repeated table rows/headers are legitimate output of block-wise
        # translation; only prose lines may be collapsed as drafts
        return (len(line.strip()) > 20 and not TABLE.match(line)
                and not HEADING.match(line) and bool(CYR.search(line)))

    last = {}
    for i, line in enumerate(out):
        if dedupable(line):
            k = norm(line)
            if k not in last or preference(i) > preference(last[k]):
                last[k] = i
    # near-duplicates (paraphrased drafts of the same paragraph), keep the last
    idx = [i for i, l in enumerate(out) if len(l.strip()) > 60] if near_dup else []
    for a_pos, i in enumerate(idx):
        for j in idx[a_pos + 1:]:
            if last.get(norm(out[i])) != i:
                break
            r = difflib.SequenceMatcher(None, norm(out[i]), norm(out[j])).quick_ratio()
            if r > 0.93 and difflib.SequenceMatcher(None, norm(out[i]), norm(out[j])).ratio() > 0.85:
                last[norm(out[i])] = j if preference(j) > preference(i) else i   # drop the weaker draft
                break
    cleaned, blank, prev = [], 0, None
    for i, line in enumerate(out):
        if not line.strip():
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
            if dedupable(line) and last.get(norm(line)) != i:
                continue
            if prev is not None and norm(line) == prev and len(line.strip()) > 20:
                continue          # immediate repetition (draft row copied twice)
            prev = norm(line)
        cleaned.append(line)
    return "\n".join(cleaned).rstrip() + "\n", removed, unwrapped

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src"); ap.add_argument("--out", dest="dst")
    ap.add_argument("--dir"); ap.add_argument("--out-dir")
    ap.add_argument("--json"); ap.add_argument("--report", action="store_true")
    ap.add_argument("--en-dir", default="corpus")
    ap.add_argument("--dedup", choices=["near", "exact"], default="near",
                    help="near=also drop paraphrased drafts (>0.85 similarity); exact=norm-equal only")
    a = ap.parse_args()

    if a.src:
        text = Path(a.src).read_text(encoding="utf-8")
        en = Path(a.en_dir) / f"{Path(a.src).parent.name}.md"
        en_lines = frozenset(norm(l) for l in en.read_text(encoding="utf-8").splitlines()) if en.exists() else frozenset()
        cleaned, removed, unwrapped = strip(text, en_lines, a.dedup == "near")
        Path(a.dst).write_text(cleaned, encoding="utf-8")
        stats = {"in": a.src, "unwrapped": len(unwrapped), "removed": len(removed),
                 "removed_cyr_heavy": sum(1 for r in removed if r["cyr"] > r["lat"]),
                 "before_lines": len(text.splitlines()),
                 "after_lines": len(cleaned.splitlines()), "detail": removed}
        if a.json:
            Path(a.json).write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in stats.items() if k != "detail"}, ensure_ascii=False))
        return 0

    args_en_dir = a.en_dir
    src = Path(a.dir); dst = Path(a.out_dir or (str(src) + "_clean"))
    total = {"files": 0, "unwrapped": 0, "removed": 0, "removed_cyr_heavy": 0}
    rows = []
    for md in sorted(src.glob("*/rep*.md")):
        rel = md.relative_to(src)
        out = dst / rel; out.parent.mkdir(parents=True, exist_ok=True)
        en = Path(args_en_dir) / f"{md.parent.name}.md"
        en_lines = frozenset(norm(l) for l in en.read_text(encoding="utf-8").splitlines()) if en.exists() else frozenset()
        cleaned, removed, unwrapped = strip(md.read_text(encoding="utf-8"), en_lines, a.dedup == "near")
        out.write_text(cleaned, encoding="utf-8")
        log = md.with_suffix(".log")
        if log.exists():
            shutil.copy2(log, dst / rel.with_suffix(".log"))
        total["files"] += 1
        total["unwrapped"] = total.get("unwrapped", 0) + len(unwrapped)
        total["removed"] += len(removed)
        total["removed_cyr_heavy"] += sum(1 for r in removed if r["cyr"] > r["lat"])
        rows.append({"file": str(rel), "removed": len(removed),
                     "cyr_heavy": sum(1 for r in removed if r["cyr"] > r["lat"])})
    print(json.dumps({"dir": str(src), "out_dir": str(dst), **total}, ensure_ascii=False))
    if a.report:
        for r in rows:
            print(f"  {r['file']:22s} removed={r['removed']:4d} cyr_heavy={r['cyr_heavy']:3d}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
