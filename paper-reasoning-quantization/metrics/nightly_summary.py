#!/usr/bin/env python3
"""Nightly digest: one markdown page summarising what the night produced.

Reads the artifacts that run_nightly.sh writes and prints (also appends via
tee) a compact report; writes results/nightly_summary.md.

Usage: nightly_summary.py [--log PATH] [--out results/nightly_summary.md]
"""
import argparse, csv, json, re, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FB_CONDS = ["F_C5_local_nvfp4_think_off", "F_C6_local_nvfp4_think_on",
            "F_T00_local_nvfp4_t00_think_off", "F_T00_local_nvfp4_t00_think_on"]
FB_FIXTURES = ["F1_config", "F2_security", "F3_disks", "F4_network-servers", "F5_firewalls"]
DEFECT_COLS = [("code_missing", "D3 code"), ("term_missing_nc", "D5nc term"),
               ("contam_nc", "D7nc contr"), ("num_lost", "D4 num"),
               ("echo", "D6 echo"), ("fail", "FAIL")]


def read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def mean(rows, key):
    vals = []
    for r in rows:
        v = r.get(key)
        if v in (None, "", "None"):
            continue
        try:
            vals.append(float(v))
        except ValueError:
            continue
    return statistics.mean(vals) if vals else None


def runs_section(lines):
    lines.append("## P-005 runs (FreeBSD domain)\n")
    lines.append("| condition | runs | expected | wall mean, s | exit≠0 |")
    lines.append("|---|---|---|---|---|")
    total = 0
    for cond in FB_CONDS:
        d = ROOT / "runs" / cond
        n = len(list(d.glob("*/rep*.md"))) if d.is_dir() else 0
        total += n
        walls, bad = [], 0
        for logf in d.glob("*/rep*.log") if d.is_dir() else []:
            txt = logf.read_text(errors="replace")
            bad += 1 if re.search(r"\[error\]", txt) else 0
        logp = ROOT / "runs/runlog.txt"
        if logp.exists():
            for m in re.finditer(rf"^(\S+) {re.escape(cond)} \S+ rep\d+ exit=(\d+) wall=(\d+)s",
                                 logp.read_text(), re.M):
                walls.append(int(m.group(3)))
                bad += 1 if int(m.group(2)) != 0 else 0
        wm = f"{statistics.mean(walls):.1f}" if walls else "—"
        lines.append(f"| {cond} | {n} | 15 | {wm} | {bad} |")
    lines.append(f"\n**Total: {total}/60 runs.**\n")

    lines.append("## P-007 reasoning traces\n")
    tr = sorted((ROOT / "runs_trace").glob("TRACE_*/" + "*" + "/rep*.trace.json"))
    if not tr:
        lines.append("_no traces yet_\n")
    else:
        lines.append("| condition | fixture | rep | requests | reasoning chars | content chars | wall, s |")
        lines.append("|---|---|---|---|---|---|---|")
        for p in tr:
            try:
                d = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            lines.append(f"| {d.get('condition')} | {d.get('fixture')} | {d.get('rep')} | "
                         f"{d.get('requests')} | {d.get('reasoning_chars_total')} | "
                         f"{d.get('content_chars_total')} | {d.get('wall_s')} |")
        lines.append("")


def defects_section(lines):
    rows = read_csv(ROOT / "results/defects_freebsd.csv")
    lines.append("## Defect metrics (FreeBSD, per run)\n")
    if not rows:
        lines.append("_results/defects_freebsd.csv not found — run stage_metrics_\n")
        return
    lines.append("| condition | " + " | ".join(lbl for _, lbl in DEFECT_COLS) + " | wall, s |")
    lines.append("|" + "---|" * (len(DEFECT_COLS) + 2))
    by = defaultdict(list)
    for r in rows:
        by[r["condition"]].append(r)
    for cond in FB_CONDS:
        rs = by.get(cond, [])
        if not rs:
            continue
        cells = []
        for key, _ in DEFECT_COLS:
            m = mean(rs, key)
            cells.append(f"{m:.2f}" if m is not None else "—")
        wall = mean(rs, "wall")
        wall_cell = f"{wall:.1f}" if wall is not None else "—"
        lines.append(f"| {cond} | " + " | ".join(cells) + f" | {wall_cell} |")
    lines.append("")


def chrf_section(lines):
    lines.append("## chrF vs official RU reference\n")
    md = ROOT / "results/chrf_freebsd.md"
    if md.exists():
        body = md.read_text(encoding="utf-8").strip().splitlines()
        lines.extend(body[1:] if body else [])
    else:
        lines.append("_results/chrf_freebsd.md not found_")
    lines.append("")


def judge_section(lines):
    rows = read_csv(ROOT / "results/judge_absolute_freebsd.csv")
    lines.append("## MQM absolute (FreeBSD)\n")
    if not rows:
        lines.append("_not judged yet — run `bash run_nightly.sh --judge-only`_\n")
        return
    by = defaultdict(list)
    for r in rows:
        if r.get("condition") not in FB_CONDS:  # skip reference-calibration rows
            continue
        try:
            by[r["condition"]].append(float(r["score"]))
        except (KeyError, ValueError):
            continue
    if not by:
        lines.append("_no P-005 conditions judged yet — run `bash run_nightly.sh --judge-only`_\n")
        return
    lines.append("| condition | n | MQM mean | sd |")
    lines.append("|---|---|---|---|")
    for cond, v in sorted(by.items()):
        lines.append(f"| {cond} | {len(v)} | {statistics.mean(v):.1f} | "
                     f"{(statistics.stdev(v) if len(v) > 1 else 0):.1f} |")
    lines.append("")
    eff = ROOT / "results/judge_effects_freebsd.md"
    if eff.exists():
        lines.append("Paired effects: `results/judge_effects_freebsd.md`\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="")
    ap.add_argument("--out", default="results/nightly_summary.md")
    a = ap.parse_args()

    lines = ["# Nightly run summary", ""]
    if a.log:
        lines.append(f"Log: `{a.log}`")
    logp = ROOT / a.log if a.log else None
    if logp and logp.exists():
        tail = [l for l in logp.read_text(errors="replace").splitlines()
                if "ALL DONE" in l or "PREFLIGHT FAIL" in l or "WARN" in l]
        if tail:
            lines.append("")
            lines.append("Notable log lines:")
            lines.extend(f"- {t}" for t in tail[-10:])
    lines.append("")
    runs_section(lines)
    defects_section(lines)
    chrf_section(lines)
    judge_section(lines)
    text = "\n".join(lines)
    out = ROOT / a.out
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
