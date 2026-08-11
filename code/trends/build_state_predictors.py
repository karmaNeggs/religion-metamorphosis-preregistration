#!/usr/bin/env python3
"""Build the two state-level predictor files for H2d/H2e/H2f.

pew_religiosity_2014.csv   — Pew RLS 2014, % of state adults "highly religious"
                            (the "High" column of the published 2016 index tables:
                            https://www.pewforum.org/wp-content/uploads/sites/7/2016/02/
                            how-religious-is-your-state-tables.pdf)
cdc_places_mental.csv      — BRFSS state-level mental distress prevalence, mean over
                            available years 2022–2024 (prereg H2e allows BRFSS fallback
                            "if PLACES is unavailable"; PLACES has no state-level file).
                            Source: CDC Socrata dataset 5eh7-pjx8 ("BRFSS - Mental
                            Health Indicators"), question = mental health not good
                            (frequent mental distress, >=14 days), demographics = Total.

Both CSVs: index = state name (matching pytrends interest_by_region labels), one column.
"""
import csv
import io
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "data", "raw", "trends", "states")
PEW_PDF = "https://www.pewforum.org/wp-content/uploads/sites/7/2016/02/how-religious-is-your-state-tables.pdf"
BRFSS_API = ("https://chronicdata.cdc.gov/resource/5eh7-pjx8.json?"
             "$where=question%20like%20%27%25mental%20health%20not%20good%25%27"
             "%20AND%20demographics_type%3D%27Total%27%20AND%20demographics_value%3D%27Total%27"
             "&$select=year,area,percent&$order=area,year")

STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
}

LINE_RE = re.compile(r"^([A-Za-z][A-Za-z ]+?)\s+(\d+)\s+(\d+)\s+(\d+)")


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def pew_state_highly_religious():
    import pdfplumber
    pdf_bytes = get(PEW_PDF)
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page1 = pdf.pages[0].extract_text() or ""
    out = {}
    for line in page1.splitlines():
        m = LINE_RE.match(line.strip())
        if m and m.group(1) in STATES:
            out[m.group(1)] = int(m.group(4))
    return out


def brfss_mental_by_state():
    import json
    data = json.loads(get(BRFSS_API))
    vals = {}
    for r in data:
        if r["area"] in STATES and r.get("percent") not in (None, "Data Unavailable"):
            try:
                vals.setdefault(r["area"], []).append(float(r["percent"]))
            except ValueError:
                continue
    return {s: sum(v) / len(v) for s, v in vals.items()}


def write_csv(name, d, col):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["state", col])
        for s in sorted(d):
            w.writerow([s, d[s]])
    print(f"WROTE {path}: {len(d)} states")
    return path


def main():
    pew = pew_state_highly_religious()
    missing = sorted(STATES - set(pew))
    if missing:
        print(f"ERROR: Pew parse missing states: {missing}", file=sys.stderr)
        sys.exit(1)
    write_csv("pew_religiosity_2014.csv", pew, "religiosity")

    brfss = brfss_mental_by_state()
    missing = sorted(STATES - set(brfss))
    if missing:
        print(f"WARNING: BRFSS missing states: {missing}", file=sys.stderr)
    write_csv("cdc_places_mental.csv", brfss, "mental")


if __name__ == "__main__":
    main()
