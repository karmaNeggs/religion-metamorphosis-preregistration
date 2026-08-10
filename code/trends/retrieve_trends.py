#!/usr/bin/env python3
"""Study 2 — Google Trends retrieval (pre-registration PREREG_Study2_Trends_H1.md §3).

Chained scaling: the anchor query `prayer` is present in every fetch; all values
are converted to anchor units (value / anchor value within the same fetch), which
makes every term comparable on one scale regardless of Google's per-fetch
normalization. Sampling-noise protocol: each fetch is repeated 5 times across
>=2 days; the per-term-month MEDIAN is the analysis value; raw pulls are cached.

Groups (frozen): A = church, prayer, bible, church service
                 B1 = prayer, meditation, mindfulness, manifestation, chakras
                 B2 = prayer, astrology
                 C  = prayer, self help, therapy, coaching   (exploratory only)
Sensitivity anchor `church` (H2h, protocol §3.3): B terms refetched with
`church` as anchor — CHB1 / CHB2. Group A needs no refetch: both anchors are
members of A, and A is computed in anchor units relative to its own anchor.

State-level: interest_by_region (US REGION, whole-period aggregate) per query.

Usage:
  python retrieve_trends.py            # time series (5 reps, medians)
  python retrieve_trends.py --states   # also fetch state-level region data
"""
import argparse
import pathlib
import statistics
import time

import numpy as np
import pandas as pd
from pytrends.request import TrendReq

ANCHOR = "prayer"
GEO = "US"
TIMEFRAME = "2004-01-01 2026-07-31"  # last complete month at collection (2026-08-10)
REPS = 5
GROUPS = {
    "A": ["church", "prayer", "bible", "church service"],
    "B1": ["prayer", "meditation", "mindfulness", "manifestation", "chakras"],
    "B2": ["prayer", "astrology"],
    "C": ["prayer", "self help", "therapy", "coaching"],
    "CHB1": ["church", "meditation", "mindfulness", "manifestation", "chakras"],
    "CHB2": ["church", "astrology"],
}
OUT = pathlib.Path(__file__).resolve().parents[2] / "data" / "raw" / "trends"


def pull(kw_list: list[str], timeframe: str, max_attempts: int = 7) -> pd.DataFrame:
    """One build_payload + interest_over_time call with 429 backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            pt = TrendReq(hl="en-US", tz=0)
            pt.build_payload(kw_list, timeframe=timeframe, geo=GEO, gprop="")
            df = pt.interest_over_time()
            if df is None or df.empty:
                raise RuntimeError("empty response")
            return df.drop(columns=["isPartial"])
        except Exception as exc:
            wait = min(10 * 2 ** attempt, 180)
            print(f"  pull failed ({exc}); retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"pull failed after {max_attempts} attempts: {kw_list}")


def state_pull(term: str, max_attempts: int = 7) -> pd.DataFrame:
    for attempt in range(1, max_attempts + 1):
        try:
            pt = TrendReq(hl="en-US", tz=0)
            pt.build_payload([term], timeframe=TIMEFRAME, geo=GEO, gprop="")
            reg = pt.interest_by_region(resolution="REGION", inc_low_vol=True)
            return reg
        except Exception as exc:
            wait = min(10 * 2 ** attempt, 180)
            print(f"  state pull {term!r} failed ({exc}); retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"state pull failed for {term!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", action="store_true", help="also fetch state-level region data")
    parser.add_argument("--reps", type=int, default=REPS, help="number of pulls per group")
    parser.add_argument("--max-attempts", type=int, default=7, help="429 retries per pull (lower = fail fast on rate-limit blocks)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    pulled: dict[str, list[pd.DataFrame]] = {g: [] for g in GROUPS}
    for rep in range(1, args.reps + 1):
        for group, kws in GROUPS.items():
            path = OUT / f"group_{group}_rep{rep}.csv"
            if path.exists():
                print(f"[rep {rep}/{args.reps}] group {group}: cached, skipping")
                pulled[group].append(pd.read_csv(path, parse_dates=[0], index_col=0))
                continue
            print(f"[rep {rep}/{args.reps}] group {group}: {kws}")
            try:
                df = pull(kws, TIMEFRAME, max_attempts=args.max_attempts)
            except RuntimeError as exc:
                print(f"  FAILED (rate limit) — {exc}; rep left missing, continuing (resume later)")
                continue
            df.to_csv(path)
            pulled[group].append(df)
            time.sleep(20)  # rate-limit courtesy between pulls

    # median-pool per term-month across reps
    for group, frames in pulled.items():
        med = pd.concat([f.assign(rep=r) for r, f in enumerate(frames)])
        med = med.groupby(level=0).median()
        med.to_csv(OUT / f"group_{group}_median.csv")
        print(f"group {group}: median series written")

    if args.states:
        state_dir = OUT / "states"
        state_dir.mkdir(exist_ok=True)
        for term in ["church", "prayer", "bible", "church service", "meditation",
                     "mindfulness", "manifestation", "chakras", "astrology"]:
            print(f"state pull: {term!r}")
            reg = state_pull(term, max_attempts=args.max_attempts)
            reg.to_csv(state_dir / f"{term.replace(' ', '_')}_region.csv")
            time.sleep(15)


if __name__ == "__main__":
    main()
