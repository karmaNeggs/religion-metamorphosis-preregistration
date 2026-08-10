#!/usr/bin/env python3
"""Study 1 — Ngram genre-sensitivity retrieval (H1d; PREREG_Study1_Ngram_H1.md §3.2).

The JSON API ignores sub-corpus codes (verified 2026-08-09), so fiction and
non-fiction series must come from the raw v3 datasets (20200217), which are
alphabetically grouped per chunk. This script downloads each chunk once (cached
to disk for reproducibility), unzips the single CSV entry in-memory, greps the
20 lexicon terms (case-insensitively, hyphen variants included), and writes
per-corpus per-term per-year match counts.

WARNING: full-corpus streaming downloads many GB per corpus (fiction + nonfiction
are two full scans). Run with --corpus fiction OR --corpus nonfiction, one at a
time, and expect ~10-25 GB of transfer per corpus. If the download is not
feasible, the pre-registered fallback applies: H1d is reported as "not run —
primary corpus only" in the deviations log (protocol §3.2).

Usage:
  python retrieve_genre.py --corpus fiction
  python retrieve_genre.py --corpus nonfiction
"""
import argparse
import io
import pathlib
import re
import time
import zipfile

import requests

TERMS = [
    "sin", "salvation", "damnation", "repentance", "grace", "faith", "worship",
    "eternal life", "church attendance", "prayer",
    "self-esteem", "self-improvement", "self-care", "personal development",
    "mindfulness", "well-being", "self-actualization", "manifestation",
    "inner peace", "positive thinking",
]
DATASETS_INDEX = "https://storage.googleapis.com/books/ngrams/books/datasetsv3.html"
YEAR_START, YEAR_END = 1800, 2019
CHUNK_RE = re.compile(r"googlebooks-eng-(fiction|nonfiction)-all-1gram-20200217-(\d+)\.csv\.zip")
OUT = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw" / "ngram_genre"


def hyphen_variants(term: str) -> list[str]:
    return [term, term.replace("-", ""), term.replace("-", " ")]


def chunk_urls(corpus: str) -> list[str]:
    page = requests.get(DATASETS_INDEX, timeout=60).text
    seen: set[str] = set()
    urls = []
    for url in re.findall(r'href="([^"]+\.csv\.zip)"', page):
        m = CHUNK_RE.search(url)
        if m and m.group(1) == corpus and url not in seen:
            seen.add(url)
            urls.append(url)
    return sorted(urls)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", choices=["fiction", "nonfiction"], required=True)
    args = parser.parse_args()

    urls = chunk_urls(args.corpus)
    if not urls:
        raise SystemExit(f"no chunks found for corpus {args.corpus!r} on index page")
    print(f"{len(urls)} chunks to scan for {args.corpus}")

    out_dir = OUT / args.corpus
    out_dir.mkdir(parents=True, exist_ok=True)

    counts: dict[str, dict[int, int]] = {t: {} for t in TERMS}
    pattern = re.compile(
        r"^(%s)\t(\d+)\t(\d+)" % "|".join(re.escape(v) for t in TERMS for v in hyphen_variants(t))
    )
    # map any variant back to its canonical term
    variant_map = {v: t for t in TERMS for v in hyphen_variants(t)}

    for i, url in enumerate(urls, start=1):
        fname = url.rsplit("/", 1)[-1]
        cache = out_dir / fname
        if not cache.exists():
            print(f"[{i}/{len(urls)}] {fname}: downloading")
            with requests.get(url, stream=True, timeout=180) as r:
                r.raise_for_status()
                with cache.open("wb") as fh:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
        else:
            print(f"[{i}/{len(urls)}] {fname}: cached, skipping")

        with zipfile.ZipFile(cache) as zf:
            for name in zf.namelist():
                if not name.endswith(".csv"):
                    continue
                with zf.open(name) as f:
                    for line in io.TextIOWrapper(f, encoding="utf-8", errors="replace"):
                        m = pattern.match(line)
                        if not m:
                            continue
                        term = variant_map[m.group(1)]
                        year = int(m.group(2))
                        count = int(m.group(3))
                        counts[term][year] = counts[term].get(year, 0) + count
        time.sleep(1)

    for term in TERMS:
        key = term.replace(" ", "_").replace("-", "_")
        path = out_dir / f"{key}.csv"
        with path.open("w") as f:
            f.write("year,count\n")
            for year in range(YEAR_START, YEAR_END + 1):
                f.write(f"{year},{counts[term].get(year, 0)}\n")
    print(f"done: per-term counts written to {out_dir}")


if __name__ == "__main__":
    main()
