#!/usr/bin/env python3
"""LLM-as-judge (MQM absolute + pairwise) for paper experiments. PLAN.md §6.2.

Judges: neuraldeep gpt-oss-120b (primary), gemma-4-31b (secondary). Never a
participant model family; Kimi excluded per operator. Key resolution follows
tools/local_translate.py (_cloud_credentials pattern).

Usage:
  judge.py absolute  --en F --ru RU [--gloss-pairs gp.txt] --judge MODEL --json OUT
  judge.py pairwise  --en F --a A.md --b B.md --gloss-pairs gp.txt --judge MODEL --json OUT
  judge.py pairs-for <conditionA> <conditionB> --fixtures S1..S7   # emits task list

MQM score = 100 - (critical*25 + major*10 + minor*2), floored at 0.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path

BASE_DEFAULT = "https://api.neuraldeep.ru/v1"

def credentials():
    key = os.environ.get("NEURALDEEP_API_KEY")
    base = os.environ.get("NEURALDEEP_BASE_URL", BASE_DEFAULT)
    if not key:
        cfg = Path.home() / ".config/opencode/opencode.json"
        opts = json.load(open(cfg, encoding="utf-8")).get("provider", {}).get("neuraldeep", {}).get("options", {})
        key = opts.get("apiKey"); base = opts.get("baseURL", base)
    return key, base

def ask(model, system, user, max_attempts=3, timeout=300):
    key, base = credentials()
    payload = {"model": model, "temperature": 0.0, "top_p": 1.0, "stream": False,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]}
    tmp = tempfile.mktemp(suffix=".json")
    Path(tmp).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        for i in range(max_attempts):
            p = subprocess.run(["curl", "-sf", base.rstrip("/") + "/chat/completions",
                                "-H", "Content-Type: application/json",
                                "-H", f"Authorization: Bearer {key}",
                                "--max-time", str(timeout), "--data-binary", f"@{tmp}"],
                               capture_output=True, text=True, timeout=timeout + 30)
            if p.returncode == 0:
                try:
                    c = json.loads(p.stdout)["choices"][0]["message"]["content"]
                    if c.strip():
                        return c
                except (KeyError, IndexError, json.JSONDecodeError):
                    pass
    finally:
        Path(tmp).unlink(missing_ok=True)
    return None

MQM_SYS = """You are a professional MQM translator-quality evaluator (EN->RU technical docs).
You receive an English source, the block's glossary pairs (EN term -> required RU equivalent),
and one candidate Russian translation. Report defects ONLY, in strict JSON:
{"defects":[{"category":"accuracy|terminology|fluency|format","severity":"minor|major|critical",
"description":"...", "quote":"..."}]}
Rules:
- terminology = required glossary equivalent replaced by a different lemma, or omitted, or used
  where the EN term does not occur. Russian case/number inflection of the required equivalent
  (консенсус -> консенсуса, Роль -> Роли) is CORRECT usage, never a defect.
- code tokens (backticked) must be byte-identical: critical.
- Numbers/dates changed: critical. Leaked reasoning/meta text (English planning lines): critical.
- Style alternatives, word order, synonym choice outside the glossary are NOT defects.
- Quote must be the exact RU substring you object to.
- Deduplicate: one entry per distinct problem; if clean, {"defects":[]}."""

PAIR_SYS = """You are a blind judge comparing two Russian translations (A and B) of the same
English source (technical docs, EN->RU). Glossary pairs are provided for reference.
Choose the better translation overall (accuracy first, then terminology, fluency, format).
Answer strict JSON: {"winner":"A"|"B"|"tie","confidence":0..1,"reason":"short"}.
Positional neutrality: judge solely on quality, not order."""

def extract_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["absolute", "pairwise"])
    ap.add_argument("--en", required=True); ap.add_argument("--judge", required=True)
    ap.add_argument("--ru"); ap.add_argument("--a"); ap.add_argument("--b")
    ap.add_argument("--gloss-pairs", default="")
    ap.add_argument("--json")
    a = ap.parse_args()
    en = Path(a.en).read_text(encoding="utf-8")
    gloss = Path(a.gloss_pairs).read_text(encoding="utf-8") if a.gloss_pairs else "(none)"

    if a.mode == "absolute":
        ru = Path(a.ru).read_text(encoding="utf-8")
        user = f"=== EN SOURCE ===\n{en}\n=== GLOSSARY PAIRS ===\n{gloss}\n=== RU CANDIDATE ===\n{ru}"
        out = ask(a.judge, MQM_SYS, user)
        d = extract_json(out) if out else None
        if d is None:
            print("JUDGE_FAIL", file=sys.stderr); return 2
        w = {"critical": 25, "major": 10, "minor": 2}
        d["score"] = max(0, 100 - sum(w.get(x.get("severity"), 2) for x in d.get("defects", [])))
    else:
        A, B = Path(a.a).read_text(encoding="utf-8"), Path(a.b).read_text(encoding="utf-8")
        user = f"=== EN SOURCE ===\n{en}\n=== GLOSSARY PAIRS ===\n{gloss}\n=== A ===\n{A}\n=== B ===\n{B}"
        out = ask(a.judge, PAIR_SYS, user)
        d = extract_json(out) if out else None
        if d is None:
            print("JUDGE_FAIL", file=sys.stderr); return 2
        d["_hash_ab"] = hash(A) & 0xFFFF; d["_hash_b"] = hash(B) & 0xFFFF
    print(json.dumps(d, ensure_ascii=False, indent=2))
    if a.json:
        Path(a.json).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
