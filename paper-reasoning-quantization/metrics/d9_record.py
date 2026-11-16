#!/usr/bin/env python3
"""B1 v2: record one-digit answers for block cards (chat-relay mode).

The agent relays cards (metrics/d9_blocks.py output) verbatim; the human answers each with
a single digit (0/1/2/3, comma-separated for several distortions). This script appends to
answers.csv + transcript answers.log — the audited answer trail. It never generates text.

Usage:
  python3 d9_record.py X1 --batch "0 0 2 0 3 0 0 1 0"   # all blocks of X1, from block 1
  python3 d9_record.py X1 --batch "2 0" --block 5       # blocks 5..6
  python3 d9_record.py X1 3 2                           # single card
  python3 d9_record.py --status                         # progress, all runs
  python3 d9_record.py --status X1
"""
import argparse, csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "annotation" / "d9" / "v2"
CSV = OUT / "answers.csv"
LOG = OUT / "answers.log"
ANS = re.compile(r"^[0-3](,[0-3])*$")


def read_answers():
    if not CSV.exists():
        return {}
    d = {}
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[(r["x"], str(r["block"]))] = r["answer"]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("x", nargs="?")
    ap.add_argument("block", nargs="?", type=int)
    ap.add_argument("answer", nargs="?")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--batch", default="", help="ответы подряд через пробел/запятую, с блока --block (или 1)")
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    order = json.loads((OUT / "order.json").read_text(encoding="utf-8"))
    done = read_answers()

    if a.status or (a.x is None and not a.batch):
        runs = [a.x] if a.x else sorted(order, key=lambda s: int(s[1:]))
        for x in runs:
            got = sorted(int(b) for (xx, b) in done if xx == x)
            n = order[x]["n_cards"]
            print(f"{x}: {len(got)}/{n} " + ("✅" if len(got) >= n else f"ждёт блоки {sorted(set(range(1, n + 1)) - set(got))}"))
        return

    if a.x not in order:
        sys.exit(f"{a.x} нет в выборке")
    n = order[a.x]["n_cards"]

    if a.batch:
        seq = [s for s in re.split(r"[,\s]+", a.batch.strip()) if s]
        answers = [(a.block or 1 + i, s) for i, s in enumerate(seq)]
    else:
        answers = [(a.block, a.answer)]

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new = not CSV.exists()
    with CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "x", "block", "answer", "note"])
        if new:
            w.writeheader()
        for block, ans in answers:
            if not (1 <= block <= n):
                sys.exit(f"блок {block} вне 1..{n} для {a.x}")
            if not ANS.match(ans):
                sys.exit(f"ответ «{ans}» не распознан — ждём 0/1/2/3 (несколько — через запятую: 3,2)")
            if (a.x, str(block)) in done:
                print(f"⚠ {a.x} блок {block} уже отвечен ({done[(a.x, str(block))]}) — перезаписываю")
            w.writerow({"ts": ts, "x": a.x, "block": block, "answer": ans, "note": a.note})
            with LOG.open("a", encoding="utf-8") as lf:
                lf.write(f"{ts} {a.x} блок {block} -> {ans}" + (f" note={a.note}" if a.note else "") + "\n")
    got = len([k for k in read_answers() if k[0] == a.x])
    print(f"✔ {a.x}: +{len(answers)} ответов ({got}/{n})")
    if got == n:
        print(f"прогон {a.x} завершён ✅")


if __name__ == "__main__":
    main()
