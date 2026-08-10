#!/usr/bin/env python3
"""Study 1 — Ngram retrieval (pre-registration PREREG_Study1_Ngram_H1.md §3.1).

Fetches the 20 frozen lexicon terms from the Google Books Ngram JSON API
(eng-2019, case-insensitive, unsmoothed, 1800-2019). Caches raw JSON verbatim;
existing files are skipped (idempotent re-runs). Rate-limit handling: 2s sleep
between requests, exponential backoff on HTTP 429 (max 180s), retries <= 10.

Verified 2026-08-09: the API ignores sub-corpus codes (eng_fiction_2019 etc.
fall back to eng-2019), so this script requests eng-2019 only; the genre split
(H1d) is handled separately by retrieve_genre.py.
"""
import json
import pathlib
import time

import requests

URL = "https://books.google.com/ngrams/json"
YEAR_START, YEAR_END = 1800, 2019
CORPUS = "eng-2019"
TERMS = [
    # Religious group R (10)
    "sin", "salvation", "damnation", "repentance", "grace", "faith", "worship",
    "eternal life", "church attendance", "prayer",
    # Self-religion group S (10)
    "self-esteem", "self-improvement", "self-care", "personal development",
    "mindfulness", "well-being", "self-actualization", "manifestation",
    "inner peace", "positive thinking",
]
OUT = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw" / "ngram"


def slug(term: str) -> str:
    return term.replace(" ", "_").replace("-", "_")


def fetch(term: str) -> dict:
    params = {
        "content": term,
        "year_start": YEAR_START,
        "year_end": YEAR_END,
        "corpus": CORPUS,
        "smoothing": 0,
        # NB: must be the lowercase string "true" — requests serializes Python
        # True as "True", which the API silently ignores (verified 2026-08-10)
        "case_insensitive": "true",
    }
    for attempt in range(1, 11):
        try:
            r = requests.get(URL, params=params, timeout=60)
        except requests.RequestException as exc:
            print(f"  [{attempt}] network error: {exc}")
            time.sleep(min(2 ** attempt, 60))
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            wait = min(5 * 2 ** attempt, 180)
            print(f"  [{attempt}] HTTP 429, backing off {wait}s")
            time.sleep(wait)
        else:
            print(f"  [{attempt}] HTTP {r.status_code}")
            time.sleep(2)
    raise RuntimeError(f"failed after 10 attempts: {term!r}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i, term in enumerate(TERMS, start=1):
        path = OUT / f"{slug(term)}.json"
        if path.exists():
            print(f"[{i}/20] {term!r}: cached, skipping")
            continue
        print(f"[{i}/20] {term!r}: fetching...")
        record = {
            "term": term,
            "corpus": CORPUS,
            "year_start": YEAR_START,
            "year_end": YEAR_END,
            "smoothing": 0,
            "case_insensitive": "true",
            "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "response": fetch(term),
        }
        path.write_text(json.dumps(record, indent=1))
        time.sleep(2)
    print("done")


if __name__ == "__main__":
    main()
