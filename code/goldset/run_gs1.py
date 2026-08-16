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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleep", type=float, default=2.0)
    args = ap.parse_args()

    print("==> build_gs1_ia.py", flush=True)
    r = subprocess.run([PY, BUILD, "--sleep", str(args.sleep)])

    print("==> judge_gs1.py (resumable, sequential; this may take many hours)", flush=True)
    r = subprocess.run([PY, JUDGE, "--workers", "1", "--sleep", "10"])
    print(f"judge exit={r.returncode} — check data/gold/gold_set_gs1_summary.csv", flush=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
