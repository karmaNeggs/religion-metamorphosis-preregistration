#!/usr/bin/env python3
"""Study 1 — Ngram analysis. Executes the pre-registered plan in fixed order
(PREREG_Study1_Ngram_H1.md §5). DO NOT RUN until the GS-1 sense-validation gold
set is complete and archived (protocol §6.5). All results are written to
data/results/ with the protocol's master-variant table.

Outputs:
  study1_ngram_results.md — the reporting-table version of §5.7
  study1_ngram_variants.csv — machine-readable master table
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm
    from pymannkendall import original_test as mann_kendall
    from ruptures import Pelt
    from scipy import stats as sps
except ImportError as exc:
    sys.exit(f"missing dependency: {exc}")

TERMS_R = ["sin", "salvation", "damnation", "repentance", "grace", "faith", "worship",
           "eternal life", "church attendance", "prayer"]
TERMS_S = ["self-esteem", "self-improvement", "self-care", "personal development",
           "mindfulness", "well-being", "self-actualization", "manifestation",
           "inner peace", "positive thinking"]
YEAR_START, YEAR_END = 1800, 2019
ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "ngram"
GENRE = ROOT / "data" / "raw" / "ngram_genre"
OUT = ROOT / "data" / "results"


def load_api_data() -> pd.DataFrame:
    rows = []
    for path in RAW.glob("*.json"):
        rec = json.loads(path.read_text())
        series = next(x for x in rec["response"] if x["type"] == "CASE_INSENSITIVE")["timeseries"]
        for year, freq in zip(range(YEAR_START, YEAR_END + 1), series):
            rows.append({"term": rec["term"], "year": year, "freq": float(freq)})
    return pd.DataFrame(rows)


def load_genre_data(corpus: str) -> pd.DataFrame | None:
    """Returns per-year summed frequencies for the 20 terms if genre data exist,
    else None (H1d -> 'not run' per protocol fallback)."""
    dirp = GENRE / corpus
    if not dirp.exists():
        return None
    frames = []
    for path in dirp.glob("*.csv"):
        if path.name in ("total_counts.csv",):
            continue
        df = pd.read_csv(path)
        term = path.stem.replace("_", " ")
        df["term"] = term
        frames.append(df)
    if not frames:
        return None
    return pd.concat(frames).rename(columns={"count": "freq"})


def build_series(df: pd.DataFrame, terms_r: list[str], terms_s: list[str]) -> pd.DataFrame:
    piv = df.pivot_table(index="year", columns="term", values="freq", aggfunc="sum")
    out = pd.DataFrame(index=piv.index)
    out["S"] = piv[terms_s].sum(axis=1) if terms_s else 0.0
    out["R"] = piv[terms_r].sum(axis=1) if terms_r else 0.0
    out["share"] = out["S"] / (out["S"] + out["R"])
    out["L"] = np.log(out["S"] / out["R"])
    return out


def hac_slope(y: pd.Series, years: np.ndarray) -> dict:
    X = sm.add_constant(years)
    model = sm.OLS(y.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    beta, se = model.params[1], model.bse[1]
    t = beta / se
    p_two = 2 * sps.t.sf(abs(t), model.df_resid)
    return {"beta": beta, "se": se, "t": t, "p_two_sided": p_two,
            "p_one_sided": p_two / 2, "ci": model.conf_int().iloc[1].tolist(), "r2": model.rsquared}


def sustained_crossover(share: pd.Series, years: np.ndarray, k: int = 5) -> int | None:
    hit = (share >= 0.5).astype(int)
    for i in range(len(hit) - k + 1):
        if hit.iloc[i:i + k].sum() == k:
            return int(years[i])
    return None


def acceleration_test(series: pd.DataFrame, years: np.ndarray) -> dict:
    post = (years >= 2000).astype(float)
    X = np.column_stack([np.ones(len(years)), years, post, (years - 1999) * post])
    model = sm.OLS(series["L"].values, X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    t3 = model.tvalues[3]
    return {"beta_post_minus_pre": model.params[3], "t": t3,
            "p_two_sided": 2 * sps.t.sf(abs(t3), model.df_resid),
            "slope_1900_1999": hac_slope(series.loc[1900:1999, "L"], np.arange(1900, 2000))["beta"],
            "slope_2000_2019": hac_slope(series.loc[2000:2019, "L"], np.arange(2000, 2020))["beta"],
            "slope_2000_2008": hac_slope(series.loc[2000:2008, "L"], np.arange(2000, 2009))["beta"]}


def run_variant(df: pd.DataFrame, terms_r: list[str], terms_s: list[str], label: str) -> dict:
    series = build_series(df, terms_r, terms_s)
    years = series.index.values
    slope = hac_slope(series["L"], years)
    mk = mann_kendall(series["L"])
    cross = sustained_crossover(series["share"], years)
    accel = acceleration_test(series, years)
    pelt = Pelt(model="l2", min_size=5).fit(series["L"].values).predict(pen=np.log(len(years)))
    return {"variant": label, "n_years": len(series), **{f"slope_{k}": v for k, v in slope.items()},
            "mk_tau": mk.Tau, "mk_p": mk.p, "crossover_year": cross,
            **{f"acc_{k}": v for k, v in accel.items()},
            "pelt_bkps": [int(years[i]) for i in pelt[:-1]]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    api = load_api_data()
    variants = [run_variant(api, TERMS_R, TERMS_S, "primary_eng2019_full")]

    # H1e: minus self-esteem
    variants.append(run_variant(api, TERMS_R, [t for t in TERMS_S if t != "self-esteem"],
                                "sensitivity_eng2019_no_self_esteem"))

    # H1d: genre split (fallback -> not run)
    for corpus in ("fiction", "nonfiction"):
        gdf = load_genre_data(corpus)
        if gdf is not None:
            variants.append(run_variant(gdf, TERMS_R, TERMS_S, f"sensitivity_{corpus}_full"))
        else:
            variants.append({"variant": f"sensitivity_{corpus}_full", "note": "not run — raw dataset unavailable (protocol §3.2 fallback)"})

    # 1800-2008 regime check (post-2009 scan regime; protocol §2.3)
    api_early = api[api["year"] <= 2008]
    variants.append(run_variant(api_early, TERMS_R, TERMS_S, "regime_check_1800_2008"))

    df = pd.DataFrame(variants)
    df.to_csv(OUT / "study1_ngram_variants.csv", index=False)
    md = df.to_markdown(index=False)
    (OUT / "study1_ngram_results.md").write_text(
        "# Study 1 — Ngram results (pre-registered pipeline; DO NOT interpret before GS-1)\n\n" + md + "\n")
    print(md)
    print(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
