#!/usr/bin/env python3
"""GS-1 orchestrator — fully autonomous: build → judge → summarize.

Source: Internet Archive (Google Books anonymous quota permanently exhausted;
deviation 2026-08-12 in PREREG_Study1 §10). Runs build_gs1_ia.py (resumable,
incremental), then judge_gs1.py (resumable, sequential), then reports. Safe to
restart at any point: every step resumes from disk.

Usage:
  .venv/bin/python code/goldset/run_gs1.py
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
BUILD = os.path.join(ROOT, "code", "goldset", "build_gs1_ia.py")
JUDGE = os.path.join(ROOT, "code", "goldset", "judge_gs1.py")
SNIPPETS = os.path.join(ROOT, "data", "gold", "gold_set_gs1_snippets.csv")


def cells_done():
    import csv
    if not os.path.exists(SNIPPETS):
        return 0
    with open(SNIPPETS, encoding="utf-8") as f:
        return len({(r["term"], r["era"]) for r in csv.DictReader(f)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--max-build-runs", type=int, default=5)
    args = ap.parse_args()

    for run in range(1, args.max_build_runs + 1):
        print(f"==> build_gs1_ia.py (run {run}, {cells_done()}/40 cells on disk)", flush=True)
        r = subprocess.run([PY, BUILD, "--sleep", str(args.sleep)])
        if r.returncode == 0 or cells_done() >= 40:
            break
        print(f"build run {run} left {cells_done()}/40 cells; retrying", flush=True)

    missing = 40 - cells_done()
    if missing > 0:
        print(f"BUILD INCOMPLETE: {missing} cells missing — stopping before judge.", flush=True)
        sys.exit(2)
    print(f"build complete ({cells_done()}/40 cells)", flush=True)

    print("==> judge_gs1.py (resumable, sequential; this may take many hours)", flush=True)
    r = subprocess.run([PY, JUDGE, "--workers", "1", "--sleep", "10"])
    print(f"judge exit={r.returncode} — check data/gold/gold_set_gs1_summary.csv", flush=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
