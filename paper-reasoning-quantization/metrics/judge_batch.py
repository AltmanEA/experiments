#!/usr/bin/env python3
"""Batch LLM-as-judge runner with pacing, resume and aggregation (P-002).

Wraps metrics/judge.py prompts (MQM absolute / pairwise) into a paced batch over
the whole run matrix. Pacing follows the same policy as cloud_paced.sh: soft RPM
ceiling below the provider limit, session/week reserve, gate on /v1/limits, and
retries only after a 60 s pause (no retry storms -> no `abuse` window).

Results are one JSON per (condition, fixture, rep, judge) under
  judge/<mode>/<condition>/<fixture>/rep<k>.<judge>.json
so the batch is resume-safe: existing valid files are skipped.

Usage:
  judge_batch.py --mode absolute --judges gpt-oss-120b,gemma-4-31b --workers 2
  judge_batch.py --mode absolute --limit 4          # smoke test
  judge_batch.py --mode pairwise --pairs C3:C4,C5:C6,C1:C2_clean
  judge_batch.py --aggregate --mode absolute        # -> results/judge_absolute.csv
"""
import argparse, csv, json, os, re, statistics, subprocess, sys, threading, time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "metrics"))
from judge import MQM_SYS, PAIR_SYS, credentials, extract_json  # noqa: E402

FIXES = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
REPS = [1, 2, 3]
CLEAN_ALIAS = {"C2_clean": "C2_cloud_bf16_think_on_clean"}
DEFAULT_CONDS = ["C1_cloud_bf16_think_off", "C2_cloud_bf16_think_on", "K0_cloud_no_glossary",
                 "C3_local_fp8_think_off", "C4_local_fp8_think_on",
                 "C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on",
                 "C2_cloud_bf16_think_on_clean"]

# ---------------------------------------------------------------- rate control
class Pacer:
    """Global request pacing shared by all workers."""

    def __init__(self, rpm, reserve_pct=15):
        self.min_gap = 60.0 / max(1, rpm)
        self.rpm = rpm
        self.reserve = reserve_pct
        self.lock = threading.Lock()
        self.last = 0.0
        self.key, self.base = credentials()
        self.gate_ok_at = 0.0

    def _limits(self):
        p = subprocess.run(["curl", "-sS", "-m", "20", self.base.rstrip("/") + "/limits",
                            "-H", f"Authorization: Bearer {self.key}"],
                           capture_output=True, text=True)
        if p.returncode != 0:
            return None
        try:
            return json.loads(p.stdout)
        except json.JSONDecodeError:
            return None

    def gate(self):
        """Return 0 if a request is allowed, else seconds to wait."""
        d = self._limits()
        if d is None:
            return 60
        ch, dec = d.get("chat", {}), d.get("decision", {})
        s, w, r = ch.get("session", {}), ch.get("week", {}), ch.get("rpm", {})
        need = []
        if not dec.get("can_request", True):
            need.append("can_request=false")
        if ch.get("cooldown_sec", 0) > 0:
            need.append(f"cooldown={ch['cooldown_sec']}s")
        if r.get("remaining", 99) < 20:
            need.append(f"rpm_remaining={r.get('remaining')}")
        lim, rem = s.get("limit", 0), s.get("remaining", 0)
        if lim and rem < max(20, lim * self.reserve // 100):
            need.append(f"session_reserve({rem}/{lim})")
        wl = w.get("limit", 0) or 0
        if w.get("remaining", 99) < max(50, wl * self.reserve // 100):
            need.append(f"week_reserve({w.get('remaining')}/{wl})")
        if need:
            ra = dec.get("retry_after_sec") or ch.get("cooldown_sec") or 30
            return max(5, min(int(ra), 900))
        return 0

    def wait(self):
        with self.lock:
            now = time.time()
            if now - self.gate_ok_at > 60:
                while True:
                    pause = self.gate()
                    if pause == 0:
                        self.gate_ok_at = time.time()
                        break
                    log(f"gate HOLD {pause}s", to="pacer")
                    time.sleep(pause)
            gap = self.min_gap - (time.time() - self.last)
            if gap > 0:
                time.sleep(gap)
            self.last = time.time()

# ---------------------------------------------------------------- task building
def task_list(mode, conds, pairs):
    tasks = []
    if mode == "absolute":
        for cond in conds:
            for fx in FIXES:
                for k in REPS:
                    md = ROOT / "runs" / cond / fx / f"rep{k}.md"
                    if md.exists():
                        tasks.append({"cond": cond, "fix": fx, "rep": k, "ru": str(md)})
    else:
        for a_name, b_name in pairs:
            a_cond = CLEAN_ALIAS.get(a_name, a_name)
            b_cond = CLEAN_ALIAS.get(b_name, b_name)
            for fx in FIXES:
                for k in REPS:
                    a = ROOT / "runs" / a_cond / fx / f"rep{k}.md"
                    b = ROOT / "runs" / b_cond / fx / f"rep{k}.md"
                    if a.exists() and b.exists():
                        tasks.append({"pair": f"{a_name}-vs-{b_name}", "cond": f"{a_name}-vs-{b_name}",
                                      "fix": fx, "rep": k, "a": str(a), "b": str(b)})
    return tasks

def out_path(mode, task, judge):
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", judge)
    p = ROOT / "judge" / mode / task["cond"] / task["fix"]
    p.mkdir(parents=True, exist_ok=True)
    return p / f"rep{task['rep']}.{slug}.json"

# ---------------------------------------------------------------- one request
def build_user(mode, task, gloss):
    en = (ROOT / "corpus" / f"{task['fix']}.md").read_text(encoding="utf-8")
    if mode == "absolute":
        ru = Path(task["ru"]).read_text(encoding="utf-8")
        return f"=== EN SOURCE ===\n{en}\n=== GLOSSARY PAIRS ===\n{gloss}\n=== RU CANDIDATE ===\n{ru}"
    a = Path(task["a"]).read_text(encoding="utf-8")
    b = Path(task["b"]).read_text(encoding="utf-8")
    return f"=== EN SOURCE ===\n{en}\n=== GLOSSARY PAIRS ===\n{gloss}\n=== A ===\n{a}\n=== B ===\n{b}"

def call(model, system, user, key, base, timeout=240):
    """Single HTTP attempt; returns (content, http_status) or (None, status)."""
    payload = {"model": model, "temperature": 0.0, "top_p": 1.0, "stream": False,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]}
    tmp = ROOT / "judge" / f".payload.{os.getpid()}.{threading.get_ident()}.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        p = subprocess.run(["curl", "-sS", "-o", str(tmp) + ".resp", "-w", "%{http_code}",
                            base.rstrip("/") + "/chat/completions",
                            "-H", "Content-Type: application/json",
                            "-H", f"Authorization: Bearer {key}",
                            "--max-time", str(timeout), "--data-binary", f"@{tmp}"],
                           capture_output=True, text=True, timeout=timeout + 30)
        status = (p.stdout or "").strip() or ("000" if p.returncode else "200")
        body = Path(str(tmp) + ".resp").read_text(encoding="utf-8", errors="replace") if Path(str(tmp) + ".resp").exists() else ""
        try:
            c = json.loads(body)["choices"][0]["message"]["content"]
            return (c if c.strip() else None), status
        except (KeyError, IndexError, json.JSONDecodeError):
            return None, status
    finally:
        for f in (tmp, Path(str(tmp) + ".resp")):
            f.unlink(missing_ok=True)

# ---------------------------------------------------------------- main loop
LOG_LOCK = threading.Lock()

def log(msg, to="run"):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    with LOG_LOCK:
        print(line, flush=True)
        d = ROOT / "judge"
        d.mkdir(exist_ok=True)
        with open(d / f"{to}log.txt", "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

def score_defects(d):
    w = {"critical": 25, "major": 10, "minor": 2}
    defs = d.get("defects", [])
    return max(0, 100 - sum(w.get(x.get("severity"), 2) for x in defs))

def worker(tasks, args, pacer, counters):
    key, base = pacer.key, pacer.base
    while True:
        with counters["lock"]:
            if not tasks:
                return
            task = tasks.pop(0)
            counters["started"] += 1
        for judge in task.get("judges", args.judges):
            dest = out_path(args.mode, task, judge)
            if dest.exists() and not args.force:
                try:
                    if json.loads(dest.read_text()).get("_status") != "fail":
                        with counters["lock"]:
                            counters["skipped"] += 1
                        continue
                except json.JSONDecodeError:
                    pass
            gloss_file = ROOT / "corpus" / "gloss_pairs" / f"{task['fix']}.txt"
            gloss = gloss_file.read_text(encoding="utf-8") if gloss_file.exists() else "(none)"
            system = MQM_SYS if args.mode == "absolute" else PAIR_SYS
            user = build_user(args.mode, task, gloss)
            for attempt in (1, 2):
                pacer.wait()
                content, status = call(judge, system, user, key, base, timeout=args.timeout)
                d = extract_json(content) if content else None
                ok = d is not None and (args.mode == "pairwise" or isinstance(d.get("defects"), list))
                if ok:
                    if args.mode == "absolute":
                        d["score"] = score_defects(d)
                    d["_meta"] = {"judge": judge, "condition": task["cond"], "fixture": task["fix"],
                                  "rep": task["rep"], "mode": args.mode, "attempt": attempt,
                                  "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
                    dest.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
                    with counters["lock"]:
                        counters["ok"] += 1
                    extra = f"score={d['score']}" if args.mode == "absolute" else f"winner={d.get('winner')}"
                    log(f"OK   {task['cond']} {task['fix']} rep{task['rep']} {judge} {extra}")
                    break
                # failure: 429/5xx or unparsable -> pause, retry once, then record
                log(f"FAIL {task['cond']} {task['fix']} rep{task['rep']} {judge} "
                    f"http={status} attempt={attempt}")
                if attempt == 1:
                    time.sleep(60)
            else:
                dest.write_text(json.dumps({"_status": "fail",
                                            "_meta": {"judge": judge, "condition": task["cond"],
                                                      "fixture": task["fix"], "rep": task["rep"]}},
                                           ensure_ascii=False, indent=2), encoding="utf-8")
                with counters["lock"]:
                    counters["failed"] += 1

def repair_tasks(mode):
    """Tasks for judge cells previously written as _status=fail."""
    grouped = {}
    for f in sorted((ROOT / "judge" / mode).glob("*/*/rep*.json")):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        judge = f.name.split(".")[1]
        if d.get("_status") == "fail":
            cond, fx = f.parent.parent.name, f.parent.name
            rep = int(f.name.split(".")[0][3:])
            grouped.setdefault((cond, fx, rep), set()).add(judge)
    tasks = []
    for (cond, fx, rep), judges in grouped.items():
        ru = ROOT / "runs" / cond / fx / f"rep{rep}.md"
        if ru.exists():
            tasks.append({"cond": cond, "fix": fx, "rep": rep, "ru": str(ru),
                          "judges": sorted(judges)})
    return tasks

def run(args):
    conds = args.conditions or DEFAULT_CONDS
    pairs = [tuple(p.split(":")) for p in (args.pairs or "").split(",") if p]
    if args.mode == "pairwise" and not pairs:
        pairs = [("C3_local_fp8_think_off", "C4_local_fp8_think_on"),
                 ("C5_local_nvfp4_think_off", "C6_local_nvfp4_think_on"),
                 ("C1_cloud_bf16_think_off", "C2_clean"),
                 ("C1_cloud_bf16_think_off", "K0_cloud_no_glossary")]
    tasks = repair_tasks(args.mode) if args.repair else task_list(args.mode, conds, pairs)
    total = sum(len(t.get("judges", args.judges)) for t in tasks)
    log(f"START mode={args.mode} tasks={len(tasks)} requests={total} "
        f"judges={','.join(args.judges)} workers={args.workers} rpm={args.rpm}")
    if args.dry_run:
        for t in tasks[:10]:
            print(t)
        return 0
    if args.limit:
        tasks = tasks[:args.limit]
    pacer = Pacer(args.rpm)
    counters = {"lock": threading.Lock(), "ok": 0, "skipped": 0, "failed": 0, "started": 0}
    threads = [threading.Thread(target=worker, args=(tasks, args, pacer, counters), daemon=True)
               for _ in range(args.workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log(f"END ok={counters['ok']} skipped={counters['skipped']} failed={counters['failed']}")
    return 0 if counters["failed"] == 0 else 3

def aggregate(mode):
    base = ROOT / "judge" / mode
    rows = []
    for f in sorted(base.glob("*/*/rep*.json")):
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        if d.get("_status") == "fail":
            continue
        meta = d.get("_meta", {})
        row = {"condition": f.parent.parent.name, "fixture": f.parent.name,
               "rep": f.name.split(".")[0].replace("rep", ""), "judge": meta.get("judge", f.name.split(".")[1])}
        if mode == "absolute":
            defs = d.get("defects", [])
            sev = [x.get("severity", "minor") for x in defs]
            row.update({"score": d.get("score"), "n_critical": sev.count("critical"),
                        "n_major": sev.count("major"), "n_minor": sev.count("minor"),
                        "categories": ",".join(sorted({x.get("category", "?") for x in defs}))})
        else:
            row.update({"winner": d.get("winner"), "confidence": d.get("confidence")})
        rows.append(row)
    if not rows:
        print("no judge results"); return 1
    out = ROOT / "results" / f"judge_{mode}.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")
    if mode == "absolute":
        by = defaultdict(list)
        for r in rows:
            by[(r["condition"], r["judge"])].append(r["score"])
        print(f"{'condition':34s} {'judge':16s} {'n':>3s} {'mean':>6s} {'sd':>5s}")
        for (c, j), v in sorted(by.items()):
            sd = statistics.stdev(v) if len(v) > 1 else 0.0
            print(f"{c:34s} {j:16s} {len(v):3d} {statistics.mean(v):6.2f} {sd:5.2f}")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["absolute", "pairwise"], default="absolute")
    ap.add_argument("--judges", default="gpt-oss-120b,gemma-4-31b")
    ap.add_argument("--conditions", nargs="*")
    ap.add_argument("--pairs", help="comma list condA:condB (pairwise only)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--rpm", type=int, default=36)
    ap.add_argument("--limit", type=int, help="only first N tasks (smoke test)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--aggregate", action="store_true")
    ap.add_argument("--repair", action="store_true", help="retry only cells marked _status=fail")
    ap.add_argument("--timeout", type=int, default=240)
    a = ap.parse_args()
    a.judges = [j.strip() for j in a.judges.split(",") if j.strip()]
    if a.aggregate:
        return aggregate(a.mode)
    return run(a)

if __name__ == "__main__":
    sys.exit(main())
