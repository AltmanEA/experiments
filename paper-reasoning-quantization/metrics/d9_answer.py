#!/usr/bin/env python3
"""B1 v4: record answers to the paragraph-grounded verification cards.

Answers live in annotation/d9/v4/answers.csv (append-only) + answers.log (transcript).
The answer key (annotation/d9/manifest_key.json) stays sealed until the CSV is frozen, so
this script never reads condition names — it only validates qid shape against items.json.

Usage:
  python3 metrics/d9_answer.py X1#1 0            # one answer
  python3 metrics/d9_answer.py --batch "X1#1=0 X1#2=0 X1#3=2 X1#4=0 X1#5=1"
  python3 metrics/d9_answer.py --status          # progress per run
  python3 metrics/d9_answer.py --freeze          # stamp sha256 before unsealing the key
"""
import argparse, csv, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "annotation" / "d9" / "v4"
CSV = OUT / "answers.csv"
LOG = OUT / "answers.log"
QID = re.compile(r"^X\d+#[1-9]$")


def valid_qids():
    d = json.loads((OUT / "items.json").read_text(encoding="utf-8"))
    return {it["qid"] for r in d for it in r["items"]}, {r["x"]: r["n"] for r in d}


def answered():
    if not CSV.exists():
        return {}
    with CSV.open(encoding="utf-8") as f:
        return {r["qid"]: r["answer"] for r in csv.DictReader(f)}


def write(rows):
    new = not CSV.exists()
    with CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "qid", "answer"])
        if new:
            w.writeheader()
        w.writerows(rows)
    with LOG.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(f"{r['ts']} {r['qid']} -> {r['answer']}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qid", nargs="?")
    ap.add_argument("answer", nargs="?")
    ap.add_argument("--batch", default="")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    a = ap.parse_args()

    if a.freeze:
        if not CSV.exists():
            sys.exit("нет ответов")
        digest = hashlib.sha256(CSV.read_bytes()).hexdigest()
        (OUT / "answers_frozen.sha256").write_text(digest + "\n", encoding="utf-8")
        print(f"заморожено: sha256={digest}")
        print("теперь можно вскрывать annotation/d9/manifest_key.json")
        return

    ok, per_run = valid_qids()
    done = answered()

    if a.status or (a.qid is None and not a.batch):
        tot = 0
        for x in sorted(per_run, key=lambda s: int(s[1:])):
            got = [q for q in done if q.startswith(x + "#")]
            tot += len(got)
            if len(got) < per_run[x]:
                miss = sorted({f"{x}#{i}" for i in range(1, per_run[x] + 1)} - set(done))
                print(f"{x}: {len(got)}/{per_run[x]} — ждёт {miss}")
        print(f"ИТОГО {tot}/{sum(per_run.values())}")
        return

    pairs = [(a.qid, a.answer)] if a.qid else [
        tuple(p.split("=", 1)) for p in re.split(r"[,\s]+", a.batch.strip()) if p]
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for qid, ans in pairs:
        qid, ans = qid.strip(), ans.strip()
        if qid not in ok:
            sys.exit(f"{qid} нет среди карточек")
        if ans not in {"0", "1", "2", "3"}:
            sys.exit(f"{qid}: ответ «{ans}» — ждём 0/1/2/3")
        if qid in done:
            print(f"⚠ {qid} уже отвечен ({done[qid]}) — перезапись")
        rows.append({"ts": ts, "qid": qid, "answer": ans})
    write(rows)
    print(f"✔ записано {len(rows)}")
    tot = len(answered())
    print(f"всего {tot}/{sum(per_run.values())}")


if __name__ == "__main__":
    main()
