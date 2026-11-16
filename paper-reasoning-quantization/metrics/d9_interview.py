#!/usr/bin/env python3
"""B1: deterministic interview driver for blind D9 annotation.

Prints the fixed card (rendered once by d9_sample.py — verbatim, never paraphrased),
reads short human answers, appends them to answers.csv + full transcript answers.log.
The agent may relay cards 1:1 but must not add hints; this script is the audited path.

Resume-safe: already-answered X are skipped. Answers are human-only: this script never
reads condition names or judge verdicts.

Usage:
  python3 d9_interview.py            # interactive: all pending cards
  python3 d9_interview.py X3 X7      # only these
  python3 d9_interview.py --status   # progress
"""
import csv, hashlib, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "annotation" / "d9"
CSV = OUT / "answers.csv"
LOG = OUT / "answers.log"
FIELDS = ["ts", "x", "q", "answer"]

SEV_OK = {"д", "н", "1", "2", "3", "нет", ""}


def answered():
    if not CSV.exists():
        return set()
    with CSV.open(encoding="utf-8") as f:
        return {r["x"] for r in csv.DictReader(f)}


def append(rows):
    new = not CSV.exists()
    with CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def log(line):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def ask(prompt, allow_empty=True, valid=None):
    while True:
        try:
            a = input(prompt).strip()
        except EOFError:
            raise SystemExit("  ввод прерван — ответы для этого X НЕ записаны (частичный прогон не сохраняется)")
        if not a and allow_empty:
            return a
        if valid is None or a in valid:
            return a
        print(f"  ждём один из: {' '.join(sorted(valid))}")


def interview(x):
    card = (OUT / "questions" / f"{x}.md").read_text(encoding="utf-8")
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log(f"\n{'=' * 70}\n[{x}] {ts}\n{'-' * 70}\n{card}")
    rows = []

    import json
    cands = json.loads((OUT / "candidates" / f"{x}.json").read_text(encoding="utf-8"))["candidates"]
    if cands:
        ids = " ".join(c["id"][1:] for c in cands)
        while True:
            try:
                seq = input(f"  Ответ одной строкой из {len(cands)} цифр (порядок: {ids}; "
                            "0=не дефект, 1/2/3=severity): ").strip().replace(" ", "")
            except EOFError:
                raise SystemExit("  ввод прерван — ответы для этого X НЕ записаны")
            if len(seq) == len(cands) and all(ch in "0123" for ch in seq):
                break
            print(f"  ждём ровно {len(cands)} символов из 0/1/2/3")
        for c, ch in zip(cands, seq):
            rows.append({"ts": ts, "x": x, "q": f"cand:{c['id']}", "answer": "н" if ch == "0" else "д"})
            if ch != "0":
                rows.append({"ts": ts, "x": x, "q": f"sev:{c['id']}", "answer": ch})
    free = ask("  другие искажения? (`0` = нет; иначе severity через запятую, напр. `3,2`): ")
    rows.append({"ts": ts, "x": x, "q": "free", "answer": free})
    append(rows)
    log(f"[{x}] answers: " + "; ".join(f"{r['q']}={r['answer']}" for r in rows))
    print(f"  ✔ {x} записан\n")


def main():
    args = [a for a in sys.argv[1:]]
    if args == ["--status"]:
        done = answered()
        allx = sorted((OUT / "questions").glob("X*.md"),
                      key=lambda p: int(p.stem[1:]))
        print(f"готово {len(done & {p.stem for p in allx})} из {len(allx)}")
        for p in allx:
            if p.stem not in done:
                print("  ждёт:", p.stem)
        return
    targets = args or [p.stem for p in sorted((OUT / "questions").glob("X*.md"),
                                              key=lambda p: int(p.stem[1:]))]
    done = answered()
    for x in targets:
        if x in done:
            print(f"{x} уже отвечен — пропуск (правка CSV вручную до freeze допустима)")
            continue
        interview(x)
    if CSV.exists():
        print("sha256 answers.csv:", hashlib.sha256(CSV.read_bytes()).hexdigest()[:16],
              "— зафиксируйте его перед вскрытием ключа")


if __name__ == "__main__":
    main()
