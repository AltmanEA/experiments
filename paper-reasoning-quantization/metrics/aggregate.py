#!/usr/bin/env python3
"""Aggregate D1-D8 + judge results into results/ CSV+tables. PLAN.md §6.3.

Usage: aggregate.py [--root .]
Reads runs/<cond>/<fix>/rep<k>.{md,log}, calls defects.py per run, writes
results/defects.csv and results/summary.md (mean per condition +/- rep-noise).
"""
import csv, json, re, statistics, subprocess, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else Path(".")
GLOSS = ROOT / "../../docs/en/glossary/index.md"
CONDS = sorted(p.name for p in (ROOT / "runs").iterdir()
               if p.is_dir() and not p.name.startswith((".", "_")))
FIXES = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]

def run_log_wall(cond, fix):
    """wall time from runs/runlog.txt lines 'TS cond fix repK exit=.. wall=..s'.

    Post-processed conditions (``<base>_clean``) were produced by reprocessing
    existing runs, so they have no own runlog lines: inherit the base
    condition's wall/exit (the model's generation cost is unchanged)."""
    out = {}
    p = ROOT / "runs/runlog.txt"
    if not p.exists():
        return out
    text = p.read_text()
    base = cond[:-len("_clean")] if cond.endswith("_clean") else cond
    for m in re.finditer(rf"^(\S+) {re.escape(base)} {fix} rep(\d+) exit=(\d+) wall=(\d+)s",
                         text, re.M):
        out[int(m.group(2))] = {"wall": int(m.group(4)), "exit": int(m.group(3))}
    return out

def per_run(cond, fix):
    recs = []
    d = ROOT / "runs" / cond / fix
    if not d.is_dir():
        return recs
    for md in sorted(d.glob("rep*.md")):
        k = int(md.stem[3:])
        log = md.with_suffix("").with_suffix(".log") if False else d / f"rep{k}.log"
        out = d / f"rep{k}.json"
        r = subprocess.run([sys.executable, str(ROOT / "metrics/defects.py"),
                            "--en", str(ROOT / "corpus" / f"{fix}.md"),
                            "--ru", str(md), "--log", str(log),
                            "--glossary", str(GLOSS), "--json", str(out)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            j = json.loads(out.read_text())
            j["rep"] = k
            w = run_log_wall(cond, fix).get(k, {})
            j["wall"] = w.get("wall"); j["exit"] = w.get("exit")
            recs.append(j)
    return recs

def scalarize(j):
    return {
        "linecount_fb": j["D1_linecount_fb"],
        "fix": j["D2_fix"], "fuzz": j["D2_fuzz_fix"], "path": j["D2_path_fix"], "fail": j["D2_fail"],
        "code_missing": len(j["D3_code_missing"]),
        "num_lost": sum(j["D4_num_lost"].values()),
        "term_missing": len(j["D5_terms_missing"]),
        "term_missing_nc": len(j.get("D5_nc_terms_missing", [])),
        "echo": len(j["D6_echo"]), "markers_lost": sum(j["D6_markers_lost"].values()),
        "contam": len(j["D7_contaminants"]),
        "contam_nc": len(j.get("D7_nc_contaminants", [])),
        "wall": j.get("wall"),
    }

def main():
    rows = []
    for c in CONDS:
        for f in FIXES:
            for j in per_run(c, f):
                row = {"condition": c, "fixture": f}
                row.update(scalarize(j))
                rows.append(row)
    if not rows:
        print("no runs yet"); return 0
    keys = list(rows[0])
    (ROOT / "results").mkdir(exist_ok=True)
    with open(ROOT / "results/defects.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)

    # summary: per-condition means; noise = max stdev across conditions (per metric)
    by_c = defaultdict(list)
    for r in rows:
        by_c[r["condition"]].append(r)
    metrics = [k for k in keys if k not in ("condition", "fixture", "rep", "exit")]
    lines = ["| condition | " + " | ".join(metrics) + " |", "|" + "---|" * (len(metrics) + 1)]
    for c in CONDS:
        rs = by_c.get(c, [])
        cells = []
        for m in metrics:
            vals = [r[m] for r in rs if r.get(m) is not None]
            cells.append(f"{statistics.mean(vals):.2f}" if vals else "—")
        lines.append(f"| {c} | " + " | ".join(cells) + " |")
    (ROOT / "results/summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote results/defects.csv ({len(rows)} rows), results/summary.md")

if __name__ == "__main__":
    main()
