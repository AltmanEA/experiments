#!/usr/bin/env python3
"""B1: blind D9 annotation — sample selection, anonymization, fixed interview cards.

PLAN-CLOSEOUT.md B1 / PLAN.md §6.2, §7. 30 runs (min-sufficient tier, disclosed in §9.4),
stratified: one per condition + extra random, fixed seed. Raw C2 excluded (leakage is
trivially critical; C2_clean is used instead — disclosed).

Design (agreed 2026-11-16): two-tier blind verification.
  tier1 (20 runs): card lists candidate defects from deterministic detectors (defects.py
    logic) + judge quotes (both judges, quotes only); annotator confirms/denies + severity
    + free additions.
  tier2 (10 runs): no candidates, only the fixed free-check question. Replicates kappa
    without candidate framing.

Deterministic: cards are rendered verbatim from this script; the human interview is
conducted against these files (agent only relays them 1:1). The X->condition key is
written to manifest_key.json and MUST NOT be opened by anyone before answers are frozen
(sha256 of answers recorded in answers_frozen.sha256).

Outputs:
  annotation/d9/blind/X<k>.md         anonymized RU outputs (annotator-visible)
  annotation/d9/questions/X<k>.md     fixed interview cards (annotator-visible)
  annotation/d9/candidates/X<k>.json  structured candidates (for agreement script)
  annotation/d9/manifest_key.json     key — seal until freeze
  annotation/d9/sample_manifest.json  public metadata (tier, fixture, rep, hashes; no cond)

Usage: python3 d9_sample.py [--n 30] [--n-tier2 10] [--seed 20261116] [--force]
"""
import argparse, hashlib, json, random, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # metrics/
ROOT = HERE.parent                               # repo root
RUNS = ROOT / "runs"
CORPUS = ROOT / "corpus"
JUDGE_ABS = ROOT / "judge" / "absolute"
GLOSSARY = CORPUS / "glossary_council_2026-11-11.md"
OUT = ROOT / "annotation" / "d9"

EXCLUDE_DIRS = {"_pilot_backup"}
EXCLUDE_CONDITIONS = {"C2_cloud_bf16_think_on"}  # raw C2: trivially-critical leakage
JUDGES = ["gpt-oss-120b", "gemma-4-31b"]
FIXTURES = ("S1", "S2", "S3", "S4", "S5", "S6", "S7")  # Council corpus only (PLAN §6.2)
MAX_CANDS = 12  # time budget: ~6 min/run

# reuse detectors from defects.py
sys.path.insert(0, str(HERE))
from defects import code_tokens, num_tokens, parse_glossary, strip_code, ECHO_PATTERNS


def conditions():
    """Council conditions only: dirs containing S1..S7 fixture dirs (excludes FreeBSD F_*)."""
    return sorted(d.name for d in RUNS.iterdir()
                  if d.is_dir() and d.name not in EXCLUDE_DIRS and d.name not in EXCLUDE_CONDITIONS
                  and (d / "S1").is_dir())


def runs_of(cond):
    out = []
    d = RUNS / cond
    for fix in FIXTURES:
        for rep in sorted(d.glob(f"{fix}/rep*.md")):
            out.append((fix, d / fix / rep.name))
    return out


def pick_sample(n, rng):
    """Stratified: 1 run per condition (covers mandatory T00 off/on, C2_clean, K0, P8,
    FP8), then random extras from the remaining population."""
    conds = conditions()
    chosen, pool = [], []
    for c in conds:
        rs = runs_of(c)
        fix, path = rng.choice(rs)
        chosen.append((c, fix, path))
        for f, p in rs:
            if p != path:
                pool.append((c, f, p))
    if len(chosen) > n:
        chosen = rng.sample(chosen, n)
    else:
        pool = [x for x in pool if all(x[2] != c[2] for c in chosen)]
        rng.shuffle(pool)
        chosen += pool[: n - len(chosen)]
    rng.shuffle(chosen)
    return chosen[:n]


def load_judge_defects(cond, fix, rep_stem):
    """Quotes + descriptions (severity/category shown to annotator WITHOUT judge verdicts)."""
    out = []
    for j in JUDGES:
        f = JUDGE_ABS / cond / fix / f"{rep_stem}.{j}.json"
        if not f.exists():
            continue
        try:
            defects = json.loads(f.read_text(encoding="utf-8")).get("defects", [])
        except json.JSONDecodeError:
            continue
        for d in defects:
            out.append(d)
    return out


def build_candidates(cond, fix, rep_stem, en_text, ru_text):
    """Deterministic detector candidates + judge-quote candidates, deduped by quote."""
    cands, seen = [], {}

    def add(ctype, quote, note, sources):
        if not quote:
            return
        key = (ctype, quote)
        if key in seen:
            seen[key]["sources"] |= sources
            return
        c = {"id": None, "type": ctype, "quote": quote, "note": note, "sources": set(sources)}
        cands.append(c)
        seen[key] = c

    # contract/code tokens (D3 rule)
    ru_t = code_tokens(ru_text)
    for t in sorted(code_tokens(en_text)):
        if t not in ru_t:
            add("формат", t, f"токен `{t}` из EN не найден в RU дословно", {"detektor"})

    # numbers (D4 rule)
    en_n, ru_n = num_tokens(en_text), num_tokens(ru_text)
    for k, c in en_n.items():
        if c > ru_n.get(k, 0):
            add("число", k, f"в EN `{k}` встречается {c} раз, в RU — {ru_n.get(k, 0)}", {"detektor"})

    # glossary terms in prose (D5_nc rule)
    gloss = parse_glossary(GLOSSARY)
    en_nc, ru_nc_low = strip_code(en_text), strip_code(ru_text).lower()
    for term, eq in gloss.items():
        if re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", en_nc, re.I):
            stem = re.sub(r"[.,;:]$", "", eq.lower().split()[0]) if eq else ""
            key = stem[: max(4, len(stem) - 1)] if len(stem) > 4 else stem
            if key and key not in ru_nc_low:
                add("термин", term, f"глоссарий: требуется RU-эквивалент «{eq}» — не найден", {"detektor"})

    # contaminants (D7_nc rule)
    for w in sorted({eq.lower() for term, eq in gloss.items()
                     if not re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", en_nc, re.I)}):
        if w and w in ru_nc_low:
            add("добавление", w, f"RU-слово «{w}» — эквивалент термина, которого нет в EN этого прогона", {"detektor"})

    # echo / leakage patterns (D6 rule)
    for p in ECHO_PATTERNS:
        m = re.search(p, ru_text)
        if m:
            add("добавление", m.group(0)[:80], "структурный артефакт/утечка (pattern-детектор)", {"detektor"})

    # judge quotes (no category/severity shown — only neutral description)
    for d in load_judge_defects(cond, fix, rep_stem):
        q = (d.get("quote") or "").strip()
        if not q:
            continue
        tmap = {"accuracy": "смысл", "terminology": "термин", "fluency": "формулировка", "format": "формат"}
        t = tmap.get(d.get("category"), "пропуск")
        k = (t, q[:120])
        if any((c["type"], c["quote"]) == k for c in cands):
            for c in cands:
                if (c["type"], c["quote"]) == k:
                    c["sources"].add("судья")
        else:
            cands.append({"id": None, "type": t, "quote": q[:120],
                          "note": (d.get("description") or "")[:160], "sources": {"судья"}})
    return cands


def find_line(text, quote):
    """Best line index (1-based) where quote occurs; exact substring, then word-overlap."""
    if not quote:
        return None
    lines = text.splitlines()
    q = quote.strip().strip("`")
    for i, ln in enumerate(lines):
        if q and q in ln:
            return i + 1
    qw = [w for w in re.split(r"\W+", q.lower()) if len(w) > 3][:4]
    if not qw:
        return None
    best, best_hits = None, 0
    for i, ln in enumerate(lines):
        lw = ln.lower()
        h = sum(1 for w in qw if w in lw)
        if h > best_hits:
            best, best_hits = i + 1, h
    return best if best_hits >= max(1, len(qw) - 1) else None


def numbered(text):
    return "\n".join(f"{i:>3}| {ln}" for i, ln in enumerate(text.rstrip().splitlines(), 1))


def render_card(x, tier, fix, ru_path, en_text, ru_text, cands):
    lines = [f"# Карточка {x} — прогон из фикстуры {fix} (повтор {ru_path.stem[-1]})", "",
             "Строки пронумерованы (`N| текст`); в вопросах ссылки — на эти номера.", ""]
    lines += ["## EN-источник", "", "```", numbered(en_text), "```", ""]
    lines += ["## RU-вывод", "", "```", numbered(ru_text), "```", ""]
    if tier == 1:
        lines += ["## Вопрос 1 — кандидаты. Ответ: одна строка из цифр, по одной на кандидата",
                  "(порядок A1, A2, …): `0` — не дефект; `1`/`2`/`3` — дефект, minor/major/critical.",
                  "Например, для 4 кандидатов: `0203` (A2 — major, A4 — critical, остальные — не дефекты).", ""]
        for c in cands:
            loc = c.get("loc") or "?"
            lines.append(f"- **{c['id']}** [{c['type']}] {loc} — цитата: `{c['quote']}` — {c['note']}"
                         + (" ⚠ пограничный" if c.get("borderline") else ""))
        if not cands:
            lines.append("(кандидатов нет — переходите к вопросу 2)")
        lines += ["", "## Вопрос 2 — другие фактические искажения (числа, подмена терминов,",
                  "потеря/добавление смысла), которых нет в списке кандидатов?",
                  "Ответ — одно число: `0` — нет; `1`/`2`/`3` — нашли искажение",
                  "minor/major/critical. Несколько — через запятую (например `3,2`).", ""]
    else:
        lines += ["## Сравните EN и RU. Фактические искажения:",
                  "изменённые числа, подмена терминов, потеря/добавление смысла, порча",
                  "`кода`, лишние строки?",
                  "Ответ — одно число: `0` — чисто; `1`/`2`/`3` — нашли искажение",
                  "minor/major/critical. Несколько — через запятую (например `3,2`).", ""]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--n-tier2", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if any((OUT / s).exists() for s in ("blind", "questions")) and not a.force:
        sys.exit(f"{OUT} уже существует — не перезаписываем (свежий прогон: --force). "
                 "Перегенерация карточек после начала разметки нарушает слепоту.")

    rng = random.Random(a.seed)
    sample = pick_sample(a.n, rng)
    tier2 = set(rng.sample(range(a.n), a.n_tier2))

    for sub in ("blind", "questions", "candidates"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    public, key = [], []
    for i, (cond, fix, rep_path) in enumerate(sample):
        x = f"X{i + 1}"
        tier = 2 if i in tier2 else 1
        en_text = (CORPUS / f"{fix}.md").read_text(encoding="utf-8")
        ru_text = rep_path.read_text(encoding="utf-8")

        cands = build_candidates(cond, fix, rep_path.stem, en_text, ru_text)
        for c in cands:
            ln = find_line(ru_text, c["quote"])
            if ln:
                c["loc"] = f"RU:{ln}"
            else:
                ln = find_line(en_text, c["quote"])
                c["loc"] = f"EN:{ln}" if ln else None
            c["borderline"] = len(c["sources"]) == 1  # detector-only or judge-only
        # time budget: cap, priority = both-sources > критичные типы > остальные
        prio = {"формат": 0, "число": 1, "термин": 2, "пропуск": 3, "добавление": 4}
        cands.sort(key=lambda c: (-len(c["sources"]), prio.get(c["type"], 9), c["quote"]))
        cands = cands[:MAX_CANDS]
        for n, c in enumerate(cands):
            c["id"] = f"A{n + 1}"
            c["sources"] = sorted(c["sources"])

        shutil.copyfile(rep_path, OUT / "blind" / f"{x}.md")
        (OUT / "candidates" / f"{x}.json").write_text(
            json.dumps({"tier": tier, "candidates": cands if tier == 1 else []},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        (OUT / "questions" / f"{x}.md").write_text(
            render_card(x, tier, fix, rep_path, en_text, ru_text, cands if tier == 1 else []), encoding="utf-8")

        public.append({"x": x, "tier": tier, "fixture": fix, "rep": rep_path.stem,
                       "sha256_ru": hashlib.sha256(ru_text.encode()).hexdigest()[:16]})
        key.append({"x": x, "condition": cond, "fixture": fix, "rep": rep_path.stem})

    (OUT / "sample_manifest.json").write_text(
        json.dumps({"seed": a.seed, "n": a.n, "n_tier2": a.n_tier2, "runs": public},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "manifest_key.json").write_text(
        json.dumps({"seed": a.seed, "runs": key}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"готово: {a.n} прогонов (tier2={a.n_tier2}) в {OUT}")
    print("карточки: annotation/d9/questions/, ключ sealed: annotation/d9/manifest_key.json")


if __name__ == "__main__":
    main()
