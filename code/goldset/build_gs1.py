#!/usr/bin/env python3
"""GS-1 snippet builder — Google Books API, era-split sampling.

Per the Study 1 registration §6 + §10 deviations (2026-08-10):
- per term, two era queries via the publishedDate filter (1500-1950 / 1950-2026)
- first 25 unique snippets WITH a textSnippet field per era
- dedupe on normalized snippet text
- writes data/gold/gold_set_gs1_snippets.csv (anonymized: term, era, id, text only)

Usage:
  python code/goldset/build_gs1.py [--sleep S] [--per-era N] [--max-pages M]
"""
import argparse
import csv
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_CSV = os.path.join(ROOT, "data", "gold", "gold_set_gs1_snippets.csv")

TERMS = [
    "sin", "salvation", "damnation", "repentance", "grace", "faith", "worship",
    "eternal life", "church attendance", "prayer",
    "self-esteem", "self-improvement", "self-care", "personal development",
    "mindfulness", "well-being", "self-actualization", "manifestation",
    "inner peace", "positive thinking",
]

ERAS = [("pre1950", "1500-1950"), ("post1950", "1950-2026")]

API = "https://www.googleapis.com/books/v1/volumes"


QUOTA_EXIT = 3


class QuotaError(RuntimeError):
    pass


def fetch_json(url, attempts=3, base_wait=20):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                if i == attempts - 1:
                    raise QuotaError("Google Books API quota exhausted — resume later")
                wait = base_wait * (2 ** i)
                print(f"  429 quota: sleeping {wait}s (attempt {i + 1}/{attempts})", flush=True)
                time.sleep(wait)
            else:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"  network error: {e}; retrying in 15s", flush=True)
            time.sleep(15)
    raise RuntimeError("unreachable")


def normalize(text):
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def collect(term, era_label, era_range, per_era, max_pages, sleep):
    seen = set()
    out = []
    for page in range(max_pages):
        params = {
            "q": f'"{term}"',
            "langRestrict": "en",
            "publishedDate": era_range,
            "printType": "books",
            "country": "US",
            "maxResults": 40,
            "startIndex": page * 40,
        }
        url = API + "?" + urllib.parse.urlencode(params)
        print(f"[{term} | {era_label}] page {page + 1}", flush=True)
        data = fetch_json(url)
        items = data.get("items") or []
        if not items:
            break
        for v in items:
            snippet = (v.get("searchInfo") or {}).get("textSnippet")
            if not snippet:
                continue
            text = normalize(snippet)
            if len(text) < 15:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            sid = hashlib.sha256(f"{term}|{era_label}|{text}".encode()).hexdigest()[:12]
            out.append({"term": term, "era": era_label, "snippet_id": sid, "text": text})
            if len(out) >= per_era:
                return out
        if len(items) < 40:
            break
        if sleep:
            time.sleep(sleep)
    return out


def load_done(out_csv):
    if not os.path.exists(out_csv):
        return set()
    with open(out_csv, encoding="utf-8") as f:
        return {(r["term"], r["era"]) for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleep", type=float, default=1.5, help="seconds between API calls")
    ap.add_argument("--per-era", type=int, default=25)
    ap.add_argument("--max-pages", type=int, default=5)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    done = load_done(OUT_CSV)
    rows = []
    total = 0
    try:
        for term in TERMS:
            for era_label, era_range in ERAS:
                if (term, era_label) in done:
                    print(f"[{term} | {era_label}] already done — skipping", flush=True)
                    continue
                found = collect(term, era_label, era_range, args.per_era, args.max_pages, args.sleep)
                rows.extend(found)
                total += len(found)
                print(f"[{term} | {era_label}] {len(found)} snippets", flush=True)
                with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=["term", "era", "snippet_id", "text"])
                    if total == len(found):
                        w.writeheader()
                    w.writerows(found)
    except QuotaError as e:
        print(f"QUOTA: {e} — {len(rows)} snippets collected this run, already-saved "
              f"terms are on disk; resume with the same command", flush=True)
        sys.exit(QUOTA_EXIT)

    print(f"WROTE {OUT_CSV}: {total} new snippets", flush=True)
    if total < len(TERMS) * len(ERAS) * args.per_era:
        print("NOTE: sample short of target — quota or coverage limits; reported per protocol.", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
