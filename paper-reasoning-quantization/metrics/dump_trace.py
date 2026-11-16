#!/usr/bin/env python3
"""P-007: dump reasoning_content traces for thinking=on runs (NVFP4 local).

Why: the pipeline (techdoc-translator) discards `reasoning_content` and keeps
only `message.content`. To explain the mechanics of the D3 defect ("thinking
translates enum/contract tokens inside backticks") we need the traces.

Design: the translator module is imported and `call_model` is monkey-patched,
so every request the pipeline makes (blocks *and* line fallbacks) is recorded
with its prompt, content, reasoning_content and usage. The translated output
is still written exactly as the pipeline would write it — patched call_model
returns `clean_response(content)` just like the original `_call_cloud`.

Output (kept away from runs/ so metrics never pick it up):
  runs_trace/<condition>/<fixture>/rep<k>.md            translated text
  runs_trace/<condition>/<fixture>/rep<k>.log           pipeline stderr
  runs_trace/<condition>/<fixture>/rep<k>.trace.jsonl   one record per request
  runs_trace/<condition>/<fixture>/rep<k>.trace.json    summary (counts, lengths)

Usage:
  dump_trace.py --condition TRACE_S4 --fixture S4 --rep 1 --thinking true
  dump_trace.py --condition TRACE_P007 --fixtures S4 S5 --reps 1 2 3 --thinking true
Env: TRANSLATE_API_BASE (default http://127.0.0.1:8000/v1), TRANSLATE_API_KEY,
     TRANSLATE_MODEL, TRANSLATE_TEMP, TRANSLATE_TOP_P, TRANSLATE_CHAT_KWARGS,
     TRANSLATOR (default ~/techdoc-translator/techdoc_translator.py)
"""
import argparse, importlib.util, json, os, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_translator(path):
    path = Path(os.path.expanduser(path))
    if not path.exists():
        sys.exit(f"translator not found: {path} (set TRANSLATOR=...)")
    spec = importlib.util.spec_from_file_location("techdoc_translator", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["techdoc_translator"] = mod
    spec.loader.exec_module(mod)
    return mod


def make_call_model(mod, records):
    """Replacement for mod.call_model: same request, but the raw message
    (content + reasoning_content) is recorded before cleaning."""
    api_base = os.environ.get("TRANSLATE_API_BASE", "http://127.0.0.1:8000/v1").rstrip("/")
    api_key = os.environ.get("TRANSLATE_API_KEY", "local")
    timeout = int(os.environ.get("REQUEST_TIMEOUT", "1800"))
    max_attempts = int(os.environ.get("MAX_RETRIES", "2"))
    temp = float(os.environ.get("TRANSLATE_TEMP", "0.2"))
    top_p = float(os.environ.get("TRANSLATE_TOP_P", "0.95"))
    extra = os.environ.get("TRANSLATE_CHAT_KWARGS")

    def call(user_prompt, model_name):
        payload = {"model": model_name, "temperature": temp, "top_p": top_p,
                   "stream": False,
                   "messages": [{"role": "system", "content": mod.SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt}]}
        if extra:
            try:
                payload["chat_template_kwargs"] = json.loads(extra)
            except json.JSONDecodeError:
                pass
        req = urllib.request.Request(
            api_base + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {api_key}"},
            method="POST")
        for attempt in range(1, max_attempts + 1):
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 - mirror pipeline retry behaviour
                records.append({"attempt": attempt, "error": str(e)[:200],
                                "prompt": user_prompt, "wall_s": round(time.time() - t0, 2)})
                print(f"[trace] request error attempt {attempt}/{max_attempts}: {e}",
                      file=sys.stderr, flush=True)
                continue
            choice = (data.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            content = (msg.get("content") or "").strip()
            reasoning = msg.get("reasoning_content") or ""
            records.append({
                "attempt": attempt,
                "prompt": user_prompt,
                "prompt_chars": len(user_prompt),
                "content": content,
                "reasoning_content": reasoning,
                "reasoning_chars": len(reasoning),
                "finish_reason": choice.get("finish_reason"),
                "usage": data.get("usage"),
                "wall_s": round(time.time() - t0, 2),
            })
            if not content:
                print(f"[trace] empty content attempt {attempt}/{max_attempts} "
                      f"(reasoning {len(reasoning)} chars)", file=sys.stderr, flush=True)
                continue
            return mod.clean_response(content)
        return None

    return call


def run_one(mod, cond, fixture, rep, corpus_dir, glossary, out_root):
    out_dir = out_root / cond / fixture
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / f"rep{rep}.md"
    if md.exists() and md.stat().st_size > 0:
        print(f"[trace] skip {cond}/{fixture}/rep{rep} (exists)")
        return "skipped"
    records = []
    mod.call_model = make_call_model(mod, records)
    src = Path(corpus_dir) / f"{fixture}.md"
    if not src.exists():
        sys.exit(f"missing source: {src}")
    old_argv = sys.argv
    sys.argv = ["techdoc_translator.py", "--allow-cloud",
                "--input-en", str(src), "--output-ru", str(md),
                "--glossary", str(glossary)]
    t0 = time.time()
    code = 0
    try:
        mod.main()
    except SystemExit as e:
        code = int(e.code or 0)
    finally:
        sys.argv = old_argv
    wall = round(time.time() - t0, 1)
    with open(out_dir / f"rep{rep}.trace.jsonl", "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    ok = [r for r in records if r.get("content")]
    summary = {
        "condition": cond, "fixture": fixture, "rep": rep,
        "exit": code, "wall_s": wall,
        "requests": len(records),
        "requests_with_content": len(ok),
        "reasoning_chars_total": sum(r.get("reasoning_chars", 0) for r in records),
        "reasoning_chars_mean": round(
            sum(r.get("reasoning_chars", 0) for r in ok) / len(ok), 1) if ok else 0,
        "content_chars_total": sum(len(r.get("content", "")) for r in records),
        "model": os.environ.get("TRANSLATE_MODEL", ""),
        "temp": os.environ.get("TRANSLATE_TEMP", ""),
        "chat_kwargs": os.environ.get("TRANSLATE_CHAT_KWARGS", ""),
    }
    (out_dir / f"rep{rep}.trace.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[trace] {cond}/{fixture}/rep{rep} exit={code} wall={wall}s "
          f"requests={summary['requests']} reasoning={summary['reasoning_chars_total']} chars")
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True)
    ap.add_argument("--fixtures", nargs="*", default=["S4", "S5"])
    ap.add_argument("--fixture", help="single fixture (alias for one-element --fixtures)")
    ap.add_argument("--reps", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--rep", type=int, help="single rep")
    ap.add_argument("--corpus-dir", default="corpus")
    ap.add_argument("--glossary", default=None,
                    help="default: $GLOSS or ~/council/docs/en/glossary/index.md")
    ap.add_argument("--out-root", default="runs_trace")
    a = ap.parse_args()

    fixtures = [a.fixture] if a.fixture else a.fixtures
    reps = [a.rep] if a.rep else a.reps
    glossary = a.glossary or os.environ.get("GLOSS") or str(
        Path(os.path.expanduser("~/council")) / "docs/en/glossary/index.md")
    translator = os.environ.get("TRANSLATOR",
                                str(Path(os.path.expanduser("~/techdoc-translator"))
                                    / "techdoc_translator.py"))
    # BACKEND is read at module import time, so the env must be set first.
    os.environ.setdefault("TRANSLATE_BACKEND", "cloud")
    os.environ.setdefault("TRANSLATE_API_KEY", "local")
    mod = load_translator(translator)
    out_root = Path(a.out_root)
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    corpus_dir = Path(a.corpus_dir)
    if not corpus_dir.is_absolute():
        corpus_dir = ROOT / corpus_dir

    print(f"[trace] translator={translator}")
    print(f"[trace] model={os.environ.get('TRANSLATE_MODEL')} "
          f"temp={os.environ.get('TRANSLATE_TEMP', '0.2')} "
          f"kwargs={os.environ.get('TRANSLATE_CHAT_KWARGS')}")
    for fx in fixtures:
        for k in reps:
            run_one(mod, a.condition, fx, k, corpus_dir, glossary, out_root)
    print("[trace] ALL DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
