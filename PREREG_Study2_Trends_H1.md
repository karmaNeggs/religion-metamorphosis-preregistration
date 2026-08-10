# PREREGISTRATION — Study 2 (H1, demand side): Google Trends divergence test

**Project:** Religion Metamorphosis — Discovery Paper (STUDY_PLAN_TwoPapers.md §3, Study 2)
**Protocol version:** v1.0 — **FROZEN 2026-08-09** for OSF registration
**Companion registration:** PREREG_Study1_Ngram_H1.md (supply side, same hypothesis family)
**OSF registration URL/DOI:** *[to be inserted after upload — see OSF_Checklist.md]*
**File status rule:** This file is frozen at v1.0. Post-registration changes are permitted ONLY as dated entries in the Deviations Log (§10). No silent edits.

---

## 1. COMMITMENT STATEMENT

1. Analyses run exactly as specified in §5 on data collected exactly as specified in §3, before inspecting the primary outcome series.
2. Query sets are frozen at registration (codebook §2); no query added or dropped after registration.
3. All results — including nulls — are reported, labeled "Preregistered Analysis" or "Exploratory Analysis."
4. Raw CSVs (all fetch repetitions), retrieval scripts, and any pytrends session logs are archived in the OSF project; deviations are logged in §10.

---

## 2. RESEARCH QUESTION AND HYPOTHESES

**RQ2:** Did online search demand for self-spirituality/self-improvement diverge upward from demand for religious practice in the United States, 2004–2026? (The *demand* side of the same migration claim H1.)

### 2.1 Primary hypothesis

**H2a:** The divergence index D_t = ln(B_t / A_t) increases over the study window.
- A_t = mean of the 4 Group-A monthly indices (religious practice: `church, prayer, bible, church service`) for month t.
- B_t = mean of the 5 Group-B monthly indices (self-spirituality: `meditation, mindfulness, manifestation, chakras, astrology`).
- Primary series for the slope test: calendar-year means (seasonality control). Monthly series retained for breakpoints.
- Test: OLS slope of annual D_t on year, one-sided (positive), α = 0.05, HAC SEs. Robustness: Mann–Kendall τ.

### 2.2 Breakpoint hypotheses

**H2b:** PELT change-point detection (annual D_t) finds a breakpoint in the window **2010–2014** (the mindfulness wave) and a breakpoint in the window **2019–2023** (the manifestation boom).
- Windows, not exact years, are pre-committed. Change-point detection is run after the slope test; both windows must contain a detected breakpoint for H2b to pass in full. One of two windows → partial support.
- Note: exact-year predictions would be a form of post-hoc curve fitting; windows are the honest commitment given Trends sampling noise.

### 2.3 Crossing hypothesis (secondary)

**H2c:** D_t > 0 (self-spirituality demand above religious-practice demand) sustained for ≥ 12 consecutive months at some point during 2016–2025. Reported regardless; this is a secondary claim, not required for H2a.

### 2.4 State-level hypotheses

**H2d:** State-level aggregate search interest in Group B correlates negatively with state religiosity.
- Predictor: Pew Religious Landscape Study 2014, % of state adults "highly religious" (n = 50 + DC).
- Test: Spearman ρ, one-sided (negative), α = 0.05.

**H2e:** Controlling for state religiosity, state-level Group-B interest correlates positively with population-level poor mental health.
- Predictor: CDC PLACES average mentally/physically unhealthy days (2020–2023 average) — or BRFSS if PLACES is unavailable.
- Test: partial Spearman ρ (B | religiosity), one-sided (positive), α = 0.05. Rationale for the partial: religiosity and poor-mental-days are themselves correlated (both elevated in the South/Appalachia), so the simple correlation would be confounded; the partial isolates the wellness-demand–distress association within comparable states.
- Simple (unpartialled) ρ(B, poor-mental-days) is reported descriptively with the confound stated.

**H2f (validation context):** Group-A state interest correlates positively with state religiosity (checks that A behaves as a religiosity-proxy measure). One-sided (positive), α = 0.05.

### 2.5 Robustness hypotheses

- **H2g:** H2a holds with reduced groups A' = {`church service, prayer, bible`} and B' = {`meditation, manifestation, chakras`}.
- **H2h:** H2a holds under the alternative anchor `church` (§3.3).
- **H2i:** H2a holds on the 2008–2026 sub-window (pre-2008 Trends data are sparse/noisy; conclusions rest primarily on 2008+).
- Sign flips under any robustness variant → verdict "ambiguous," reported.

### 2.6 Boundary (pre-registered)

- Group C (`self help, therapy, coaching`) is **exploratory only** (D2_t = ln(C_t/A_t) reported descriptively); no confirmatory claim is attached to it.
- This study tests search *demand*, not belief or consumption. State-level results are cross-sectional aggregates, not time series.

---

## 3. DATA COLLECTION

### 3.1 Tool

- Primary: Google Trends web UI CSV export (documented screenshots + CSVs archived). Scriptable fallback: pytrends (unofficial client; access stability caveats disclosed in §9). Both are subject to the same query sets and chained-scaling protocol below.
- Settings (fixed): geo = US; category = All; gprop = Web search (empty); timeframe = 2004-01-01 to the last complete month before data collection (window end recorded at collection; a trailing month may be added at final pull if the paper's data cut requires it — flagged in §10 if so); resolution = monthly (Trends returns monthly for multi-year ranges).

### 3.2 Chained scaling (the critical protocol)

Google Trends normalizes each fetch relative to its own maximum and limits comparisons to 5 terms per request. Terms in different fetches are NOT directly comparable. Protocol:

- Every fetch contains the **anchor term `prayer`** (member of Group A), chosen for high volume and zero cost, so all terms are placed on one common scale.
- Fetch A: `church, prayer, bible, church service` (4 terms; anchor included).
- Fetch B1: `prayer, meditation, mindfulness, manifestation, chakras` (5 terms).
- Fetch B2: `prayer, astrology` (2 terms).
- Within each fetch, take the anchor's monthly values as the scale reference; for every term, value_on_common_scale = fetch_value × (anchor_scale / fetch_anchor_value) where anchor_scale is set once, e.g., to the anchor's own raw series from Fetch A. D_t = ln(B/A) is scale-invariant, so any consistent anchor reference works.
- **No cross-fetch comparison is ever made without the anchor correction.**
- Sensitivity anchor: the entire protocol is repeated with anchor `church` (H2h).

### 3.3 Sampling-noise protocol

Trends values are sampled estimates; repeated pulls differ. Protocol: each fetch is repeated 5 times, spread over ≥ 2 different days. Per term-month, the **median** of the 5 pulls is the analysis value. Per term-month interquartile range (IQR) is stored and reported for the anchor and for `manifestation` (highest-ambiguity primary term). If a pull returns all-zero or partial series, it is discarded and redone (retries ≤ 5); a documented failure leaves the median of the successful pulls.

### 3.4 State-level data

- pytrends `interest_by_region(resolution="REGION", inc_low_vol=True)` with geo = US for each of the 9 Group A∪B queries (fetched in the same anchored groups; state shares are within-query relative indices, aggregated as the mean of the group's terms per state). These are whole-period aggregates, not time series — analysis is cross-sectional (n = 51).
- Predictors: Pew 2014 state religiosity (% highly religious, published state tables); CDC PLACES poor-mental-health-days state averages (2020–2023); note in paper if PLACES version differs.

---

## 4. QUERY SETS (frozen)

- **Group A (religious practice):** `church, prayer, bible, church service`
- **Group B (self-spirituality):** `meditation, mindfulness, manifestation, chakras, astrology`
- **Group C (self-improvement products; exploratory):** `self help, therapy, coaching`

Sense definitions, ambiguity flags, and per-query validation notes: LEXICONS_Codebook.md §2. No query added, dropped, or re-spelled after registration.

---

## 5. ANALYSIS PLAN (fixed order)

1. **Preprocessing.** Median-pool the 5 pulls; monthly series per term; annual means A_t, B_t; D_t = ln(B_t/A_t) annual and monthly.
2. **H2a (primary).** OLS of annual D_t on year, HAC SEs (annual series), one-sided β > 0, α = 0.05; report β, SE, t, p, 95% CI, R². Robustness: Mann–Kendall τ; also the 2008–2026 slope (H2i).
3. **H2b.** PELT (ruptures, penalty BIC, min segment 2 years) on annual D_t; compare detected breakpoints to the pre-committed windows.
4. **H2c.** First month where monthly D_t > 0 for ≥ 12 consecutive months; report the run start (or "none").
5. **H2d / H2e / H2f.** Spearman and partial Spearman correlations at state level (n = 51).
6. **H2g / H2h.** Rerun step 2 with reduced groups and with anchor `church`.
7. **Exploratory (labeled):** D_t monthly trajectory figure with seasonality decomposition (STL); A_t and B_t separately; Group C descriptives (D2_t); per-term annual means.
8. **Reporting table.** Master table of slope variants (full/reduced groups × anchors × windows) and state correlations; interpretations on the primary specification; all variants shown.

---

## 6. FALSIFICATION / INTERPRETATION RULES

- H2a falsified if the one-sided slope test does not reject β ≤ 0 at α = 0.05 on the primary (annual, full-group, anchor-`prayer`) specification.
- H2b: pass = both windows contain a detected breakpoint; partial = one; fail = none.
- H2c reported regardless (secondary).
- H2d falsified if ρ(B, religiosity) ≥ 0; H2e falsified if partial ρ ≤ 0; H2f falsified if ρ(A, religiosity) ≤ 0.
- H2g/H2h/H2i are robustness; sign flips → "ambiguous" verdict, reported.
- No hypothesis retrofitted; exploratory results labeled.

---

## 7. REPORTING PLAN

- Figure 3: D_t annual and monthly (STL-corrected), breakpoints marked, crossing band shown.
- Figure 4: state-level map/scatter (B-state index vs religiosity; B vs poor-mental-days).
- Table 3: slope variants (step 8).
- Table 4: state correlations (simple + partial).
- Table 5: term-level medians and IQRs across pulls (noise report).
- Appendix: exact query strings, timestamps of pulls, pytrends version, UI screenshots for manual exports, archived CSVs.

---

## 8. DATA-MARKET COMPANION (same registration family, exploratory)

Market-size series ($51B 2025 → ~$80B 2033, Grand View Research) and meditation-app download/revenue series are reported alongside D_t as context in the paper, not as part of the pre-registered hypothesis tests.

---

## 9. KNOWN LIMITATIONS (pre-registered, published as-is)

1. Trends is a relative (0–100) index; query choice sensitivity is controlled by freezing query sets and by robustness variants — not eliminated.
2. Query polysemy: `church` (building/institution), `therapy` (physical vs psychological), `coaching` (sports vs life), `manifestation` (New Age vs mundane senses) — flagged in the codebook; not resolvable from Trends data itself.
3. Sampling noise: mitigated by median-of-5, not eliminated; IQRs reported.
4. Seasonality: handled by annual-mean primary series; monthly retained only for breakpoints.
5. Pre-2008 data are sparse; conclusions rest on 2008+ (H2i).
6. State-level: cross-sectional aggregates, whole-period, not time series; low-volume states may be noisy (inc_low_vol=True mitigates but does not fix).
7. Demand ≠ belief, and search demand ≠ consumption: the study is a demand proxy only.
8. WEIRD scope: US only; India is a separate registered hypothesis family (H8, not part of this registration).
9. pytrends is an unofficial client; if Google changes access, the manual-export path is the fallback (documented, §3.1).

---

## 10. DEVIATIONS LOG (empty at registration)

| Date | Deviation | Reason | Impact |
|---|---|---|---|
| 2026-08-10 | GS-1 annotation method amended per Study 1 §10 deviation (2026-08-10): human dual-coding replaced by 3-model LLM majority; human raters dropped for all annotation. | Author directive (rater bias; see Study 1 log). | Only affects shared gold-set infrastructure, not this protocol's own hypotheses. |
| 2026-08-10 | Trends noise protocol: Google 429 rate-limiting left 23/39 pulls uncollected on the first collection day (reps 1–3 for groups A/B1/B2/C, reps 1–2 for CHB1/CHB2). Median-of-5 becomes median-of-N with N reported (protocol §3.3 allows "the median of the successful pulls"). Remaining reps to be collected on a later day, re-medianed; this entry stays as the record. | Google Trends rate limits (HTTP 429). | D_t computed from median-of-3 for A/B1/B2/C and median-of-2 for CHB1/CHB2 at interim; finalized once quota resets. Noise reported via IQRs per protocol. |
