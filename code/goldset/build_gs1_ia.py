#!/usr/bin/env python3
"""GS-1 snippet builder — Internet Archive fallback (2026-08-12 deviation).

Google Books API anonymous quota has been continuously exhausted since 2026-08-10
(shared global bucket; no reset observed in 43+ h). Per the amended Study 1 §10 log,
the sampling source is substituted: Internet Archive full-text search + "Search
Inside" (inside.php) over OCR'd books, era split by publication date.

Per term and era:
- advancedsearch.php: q=<term> AND year:[era] AND format:("Abbyy GZ") AND mediatype:texts
- for each item in search order: metadata (server/path) -> inside.php q=<term>
  -> take matched OCR lines (markers stripped) as snippets, first unique <= per_era
- dedupe on normalized text; snippet must contain the term (case-insensitive,
  word-boundary-aware); < 15 chars dropped.

Same output contract as build_gs1.py (incremental, resumable):
data/gold/gold_set_gs1_snippets.csv  (term, era, snippet_id, text)

Usage:
  python code/goldset/build_gs1_ia.py [--sleep S] [--per-era N] [--max-items M]
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

ERAS = [("pre1950", "1500 TO 1950"), ("post1950", "1950 TO 2026")]

SEARCH = "https://archive.org/advancedsearch.php"
UA = {"User-Agent": "research-script/1.0 (scholarly content analysis)"}


def get_json(url, timeout=60, attempts=4):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 30 * (i + 1)
                print(f"  429: sleeping {wait}s", flush=True)
                time.sleep(wait)
            elif e.code == 403:
                return None
            elif e.code >= 500:
                time.sleep(20 * (i + 1))
            else:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(15)
    return None


def item_ids(term, era_range, page, rows=100):
    params = {
        "q": f'"{term}" AND year:[{era_range}] AND format:("Abbyy GZ") AND mediatype:texts',
        "fl[]": "identifier",
        "rows": rows,
        "page": page,
        "output": "json",
    }
    url = SEARCH + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    d = get_json(url)
    if not d:
        return [], 0
    resp = d.get("response") or {}
    return [doc["identifier"] for doc in resp.get("docs", [])], int(resp.get("numFound", 0))


def item_meta(identifier):
    d = get_json(f"https://archive.org/metadata/{identifier}")
    if not d:
        return None
    server = d.get("server")
    dir_ = d.get("dir", "").strip("/")
    if not server or not dir_:
        return None
    return server, dir_


def inside_matches(identifier, server, dir_, term):
    url = (f"https://{server}/fulltext/inside.php?item_id={identifier}"
           f"&doc={identifier}&path=/{dir_}&q={term}")
    d = get_json(url)
    if not d:
        return []
    return [m.get("text", "") for m in (d.get("matches") or [])]


def normalize(text):
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"<IA_FTS_MATCH>|</IA_FTS_MATCH>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_marker(text):
    return re.sub(r"<IA_FTS_MATCH>|</IA_FTS_MATCH>", "", text)


def contains_term(text, term):
    low = text.lower()
    for tok in term.split():
        if not re.search(r"(^|\W)" + re.escape(tok.lower()) + r"(\W|$)", low):
            return False
    return True


def collect(term, era_label, era_range, per_era, max_items, sleep):
    seen, out = set(), []
    page = 1
    while len(out) < per_era and page <= max_items:
        ids, num_found = item_ids(term, era_range, page)
        if not ids:
            break
        for identifier in ids:
            meta = item_meta(identifier)
            if not meta:
                continue
            server, dir_ = meta
            for raw in inside_matches(identifier, server, dir_, term):
                text = normalize(raw)
                if len(text) < 15 or not contains_term(text, term):
                    continue
                key = text.lower()
                if key in seen:
                    continue
                seen.add(key)
                sid = hashlib.sha256(f"{term}|{era_label}|{text}".encode()).hexdigest()[:12]
                out.append({"term": term, "era": era_label, "snippet_id": sid, "text": text})
                if len(out) >= per_era:
                    return out
            if sleep:
                time.sleep(sleep)
        if len(ids) < 100 or page * 100 >= num_found:
            break
        page += 1
    return out


def load_done(out_csv):
    if not os.path.exists(out_csv):
        return set()
    with open(out_csv, encoding="utf-8") as f:
        return {(r["term"], r["era"]) for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--per-era", type=int, default=25)
    ap.add_argument("--max-items", type=int, default=20, help="max advancedsearch pages per era")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    done = load_done(OUT_CSV)
    rows, total = [], 0
    for term in TERMS:
        for era_label, era_range in ERAS:
            if (term, era_label) in done:
                print(f"[{term} | {era_label}] already done — skipping", flush=True)
                continue
            found = collect(term, era_label, era_range, args.per_era, args.max_items, args.sleep)
            rows.extend(found)
            total += len(found)
            print(f"[{term} | {era_label}] {len(found)} snippets", flush=True)
            with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["term", "era", "snippet_id", "text"])
                if total == len(found):
                    w.writeheader()
                w.writerows(found)

    print(f"WROTE {OUT_CSV}: {total} new snippets", flush=True)
    if total < len(TERMS) * len(ERAS) * args.per_era:
        print("NOTE: sample short of target — coverage limits; reported per protocol.", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()