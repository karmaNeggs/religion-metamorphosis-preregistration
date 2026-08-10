#!/usr/bin/env python3
"""Study 2 — Trends analysis. Executes the pre-registered plan in fixed order
(PREREG_Study2_Trends_H1.md §5). DO NOT RUN until GS-1 (protocol §6.5 — gold
sets precede ALL analysis). Missing state-level predictor CSVs (Pew 2014, CDC
PLACES) make H2d-H2f skip with an explicit note rather than failing.

Outputs:
  study2_trends_results.md / study2_trends_variants.csv
"""
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

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "trends"
OUT = ROOT / "data" / "results"

GROUP_A = ["church", "prayer", "bible", "church service"]
GROUP_B = ["meditation", "mindfulness", "manifestation", "chakras", "astrology"]
GROUP_C = ["self help", "therapy", "coaching"]


def load_group(group: str, anchor: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / f"group_{group}_median.csv", parse_dates=[0], index_col=0)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    a = df[anchor]
    return df.div(a, axis=0).drop(columns=[anchor])  # anchor units


def build_d(anchor: str = "prayer") -> pd.DataFrame:
    a = load_group("A", anchor)
    b1 = load_group("B1", anchor)
    b2 = load_group("B2", anchor)
    a_t = a[GROUP_A].mean(axis=1)
    b_t = pd.concat([b1[["meditation", "mindfulness", "manifestation", "chakras"]], b2[["astrology"]]],
                    axis=1).mean(axis=1)
    out = pd.DataFrame({"A": a_t, "B": b_t})
    out["D"] = np.log(out["B"] / out["A"])
    return out


def annual_d(d: pd.DataFrame) -> pd.DataFrame:
    return d.groupby(d.index.year).mean()


def hac_slope(y: np.ndarray, years: np.ndarray, maxlags: int = 1) -> dict:
    X = sm.add_constant(years)
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    beta, se = model.params[1], model.bse[1]
    t = beta / se
    p_two = 2 * sps.t.sf(abs(t), model.df_resid)
    return {"beta": beta, "se": se, "t": t, "p_one_sided": p_two / 2, "ci": model.conf_int().iloc[1].tolist(),
            "r2": model.rsquared}


def crossing_run(d: pd.DataFrame, start: int = 2016, end: int = 2025, k: int = 12) -> str | None:
    sub = d[d.index.year.between(start, end)]
    pos = (sub["D"] > 0).astype(int)
    for i in range(len(pos) - k + 1):
        if pos.iloc[i:i + k].sum() == k:
            return str(sub.index[i].date())
    return None


def breakpoints(d_annual: pd.DataFrame) -> list[int]:
    vals = d_annual["D"].values
    pen = np.log(len(vals))
    return [int(d_annual.index[i]) for i in
            Pelt(model="l2", min_size=2).fit(vals).predict(pen=pen)[:-1]]


def state_analysis() -> dict:
    """H2d/H2e/H2f — requires external predictor CSVs; skips with a note if absent."""
    region = RAW / "states"
    b_terms = ["meditation", "mindfulness", "manifestation", "chakras", "astrology"]
    a_terms = ["church", "prayer", "bible", "church service"]
    pew = region / "pew_religiosity_2014.csv"
    cdc = region / "cdc_places_mental.csv"
    if not (pew.exists() and cdc.exists()):
        return {"state_level": "skipped — pew_religiosity_2014.csv and/or cdc_places_mental.csv missing"}
    frames = {}
    for term in a_terms + b_terms:
        f = region / f"{term.replace(' ', '_')}_region.csv"
        if not f.exists():
            return {"state_level": f"skipped — missing {f.name}"}
        frames[term] = pd.read_csv(f, index_col=0).iloc[:, 0]
    b_state = pd.concat([frames[t] for t in b_terms], axis=1).mean(axis=1)
    a_state = pd.concat([frames[t] for t in a_terms], axis=1).mean(axis=1)
    df = pd.DataFrame({"B": b_state, "A": a_state})
    df = df.join(pd.read_csv(pew, index_col=0)).join(pd.read_csv(cdc, index_col=0))

    def rho(x, y):
        valid = df[[x, y]].dropna()
        return sps.spearmanr(valid[x], valid[y]).statistic, sps.spearmanr(valid[x], valid[y]).pvalue

    rho_ba = rho("B", "A")
    rho_bp = rho("B", "religiosity")
    rho_ap = rho("A", "religiosity")
    resid_b = df["B"] - sm.OLS(df["B"], sm.add_constant(df["religiosity"])).fit().predict(sm.add_constant(df["religiosity"]))
    resid_mh = df["mental"] - sm.OLS(df["mental"], sm.add_constant(df["religiosity"])).fit().predict(sm.add_constant(df["religiosity"]))
    rho_part = sps.spearmanr(resid_b, resid_mh)
    return {"state_n": int(len(df.dropna())), "rho_B_A": rho_ba, "rho_B_religiosity": rho_bp,
            "rho_A_religiosity": rho_ap, "partial_rho_B_mental|religiosity": rho_part.statistic,
            "partial_rho_p": rho_part.pvalue}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = build_d("prayer")
    d_ann = annual_d(d)
    years = d_ann.index.values

    rows = []
    slope = hac_slope(d_ann["D"].values, years, maxlags=1)
    mk = mann_kendall(d_ann["D"].values)
    rows.append({"variant": "H2a_primary_annual_full", **{f"slope_{k}": v for k, v in slope.items()},
                 "mk_tau": mk.Tau, "mk_p": mk.p})
    d08 = d_ann[d_ann.index >= 2008]
    slope08 = hac_slope(d08["D"].values, d08.index.values, maxlags=1)
    rows.append({"variant": "H2i_2008_2026", **{f"slope_{k}": v for k, v in slope08.items()}})

    bkps = breakpoints(d_ann)
    rows.append({"variant": "H2b_breakpoints_annual_D", "bkps": bkps,
                 "win_2010_2014_hit": any(2010 <= b <= 2014 for b in bkps),
                 "win_2019_2023_hit": any(2019 <= b <= 2023 for b in bkps)})

    rows.append({"variant": "H2c_crossing_D>0_12mo", "crossing_date": crossing_run(d)})

    # H2g reduced groups; H2h church anchor
    dg = build_d("prayer")
    red_b = pd.concat([dg[["meditation", "manifestation", "chakras"]]], axis=1)
    a_red = pd.concat([dg[["church service", "prayer", "bible"]]], axis=1)
    d_red = np.log(red_b.mean(axis=1) / a_red.mean(axis=1))
    dg_ann = d_red.groupby(d_red.index.year).mean()
    s = hac_slope(dg_ann.values, dg_ann.index.values, maxlags=1)
    rows.append({"variant": "H2g_reduced_groups", **{f"slope_{k}": v for k, v in s.items()}})

    try:
        dch = build_d("church")
        dch_ann = annual_d(dch)
        s = hac_slope(dch_ann["D"].values, dch_ann.index.values, maxlags=1)
        rows.append({"variant": "H2h_church_anchor", **{f"slope_{k}": v for k, v in s.items()}})
    except FileNotFoundError as exc:
        rows.append({"variant": "H2h_church_anchor", "note": f"not run — {exc} (run retrieve_trends.py again)"})

    rows.append(state_analysis())

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "study2_trends_variants.csv", index=False)
    (OUT / "study2_trends_results.md").write_text(
        "# Study 2 — Trends results (pre-registered pipeline; DO NOT interpret before GS-1)\n\n"
        + df.to_markdown(index=False) + "\n")
    print(df.to_markdown(index=False))
    print(f"\nwritten to {OUT}")


if __name__ == "__main__":
    main()
