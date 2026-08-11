#!/usr/bin/env python3
"""GS-1 orchestrator — fully autonomous: wait → build → judge → summarize.

Waits for the Google Books API anonymous quota to reset (poll with cheap probes),
runs build_gs1.py (resumable), then judge_gs1.py (resumable, sequential), then
reports. Safe to restart at any point: every step resumes from disk.

Usage:
  .venv/bin/python code/goldset/run_gs1.py [--max-wait-hours 24] [--poll-minutes 30]
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
BUILD = os.path.join(ROOT, "code", "goldset", "build_gs1.py")
JUDGE = os.path.join(ROOT, "code", "goldset", "judge_gs1.py")
SNIPPETS = os.path.join(ROOT, "data", "gold", "gold_set_gs1_snippets.csv")

PROBE = ("https://www.googleapis.com/books/v1/volumes?"
         "q=%22prayer%22&langRestrict=en&maxResults=1")


def quota_ready():
    try:
        req = urllib.request.Request(PROBE, headers={"User-Agent": "research-script/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-wait-hours", type=float, default=24)
    ap.add_argument("--poll-minutes", type=int, default=20)
    args = ap.parse_args()

    deadline = time.time() + args.max_wait_hours * 3600
    if not os.path.exists(SNIPPETS):
        print("Waiting for Google Books API quota (probe every "
              f"{args.poll_minutes} min, up to {args.max_wait_hours} h)...", flush=True)
        while not quota_ready():
            if time.time() > deadline:
                print("GAVE UP: quota did not reset in time; rerun to continue", flush=True)
                sys.exit(3)
            time.sleep(args.poll_minutes * 60)
        print("Quota is back.", flush=True)

    print("==> build_gs1.py", flush=True)
    r = subprocess.run([PY, BUILD, "--sleep", "1.5"])
    if r.returncode == 3:
        print("Build still quota-blocked; will retry later.", flush=True)
        sys.exit(3)

    print("==> judge_gs1.py (resumable, sequential; this may take many hours)", flush=True)
    r = subprocess.run([PY, JUDGE, "--workers", "1", "--sleep", "10"])
    print(f"judge exit={r.returncode} — check data/gold/gold_set_gs1_summary.csv", flush=True)


if __name__ == "__main__":
    main()
