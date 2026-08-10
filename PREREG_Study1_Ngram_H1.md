# PREREGISTRATION — Study 1 (H1, supply side): Ngram cultural-prominence test

**Project:** Religion Metamorphosis — Discovery Paper (STUDY_PLAN_TwoPapers.md §3, Study 1)
**Protocol version:** v1.0 — **FROZEN 2026-08-09** for OSF registration
**Companion registration:** PREREG_Study2_Trends_H1.md (demand side, same hypothesis family)
**OSF registration URL/DOI:** *[to be inserted after upload — see OSF_Checklist.md]*
**File status rule:** This file is frozen at v1.0. Post-registration changes are permitted ONLY as dated entries in the Deviations Log (§10). No silent edits.

---

## 1. COMMITMENT STATEMENT

By registering this protocol, we commit to:
1. Running the analyses exactly as specified in §5, on data collected exactly as specified in §3, before inspecting the outcome series of the primary metrics.
2. Not adding, removing, or redefining lexicon terms after registration, except under the H1f flag rule (§6).
3. Reporting every result below — including failures and nulls — in the paper, with "Preregistered Analysis" and "Exploratory Analysis" labels.
4. Uploading the retrieval code and raw data snapshots to the OSF project alongside the registration, and logging any deviation in §10.

---

## 2. RESEARCH QUESTION AND HYPOTHESES

**RQ1:** Did the cultural prominence of self-religious language overtake religious language in the published English-language book record (the *supply* side of culture)?

### 2.1 Primary hypothesis

**H1a:** The relative-share trajectory R_t = S_t / (S_t + R_t) — equivalently the log-odds L_t = ln(S_t / R_t) — increases over 1800–2019 in the eng-2019 corpus.
- S_t = sum over the 10 self-religion terms (§4) of their per-year relative frequencies in year t.
- R_t = sum over the 10 religious terms (§4), same units.
- Test: slope of L_t on year, 1800–2019, one-sided (positive), α = 0.05, HAC/Newey-West standard errors.

### 2.2 Crossover hypothesis (graded)

**H1b:** There exists a *sustained crossover year* t* — the first year t such that S > R (share > 0.5) for all of t…t+4 — with the graded interpretation:
- **Strong support** (claim "crossing began before the internet"): t* ∈ [1960, 1989].
- **Weak support** (crossing coincides with the internet era): t* ∈ [1990, 2010].
- **Partial support only**: t* ∈ [2011, 2019] (post-internet-only crossing; the "pre-internet rise" claim fails, the "overtaking" claim stands).
- **H1b falsified**: no sustained crossover by 2019. We then report the ratio trajectory descriptively; the paper's "overtook" claim is downgraded to "converged and continued rising."

### 2.3 Acceleration hypothesis

**H1c:** The slope of L_t over 2000–2019 exceeds the slope over 1900–1999 (post-internet acceleration).
- Test: OLS interaction (year × post-2000 indicator), HAC SEs. Regime check: also report the 2000–2008 slope alone, because books 2009–2019 come from a different scan program (known Ngram dataset regime change; see §9).

### 2.4 Robustness hypotheses

- **H1d:** H1a holds directionally in the fiction and non-fiction sub-corpora (see §3.2 for the genre-split procedure).
- **H1e:** H1a holds with `self-esteem` removed from S (academic-inflation check; see codebook).
- **H1f:** every lexicon term passes the sense-validation gate (precision ≥ 0.70, §6). Flagged terms are excluded from a rerun of all primary analyses; both versions are reported.

### 2.5 What this study is NOT testing (pre-registered boundary)

- Not a test of individual substitution (no person-level data; ecological inference only).
- Not a test of belief — books are a *publishing/supply* measure; claims are restricted to "cultural prominence."
- Not a test of the demand side — that is Study 2 (Trends registration).

---

## 3. DATA SOURCE AND RETRIEVAL

### 3.1 Primary source: Google Books Ngram JSON API (eng-2019)

- Endpoint: `https://books.google.com/ngrams/json?content={term}&year_start=1800&year_end=2019&corpus={corpus}&smoothing=0&case_insensitive=true`
- Parameters (fixed): `year_start=1800`, `year_end=2019`, `smoothing=0`, `case_insensitive=true`.
- Response: JSON; we use the aggregated `CASE_INSENSITIVE` series (returned as `{term} (All)`); per-year values are relative frequencies (match count / total 1-grams in that corpus-year — the same denominator for all n-grams, so summing across terms of mixed length is valid).
- No smoothing in any analysis. `smoothing=3` is applied ONLY in figures, where it is labeled.
- **Verified behavior (2026-08-09):** the endpoint currently returns the eng-2019 (all-English) series regardless of the `corpus` parameter value — sub-corpus codes such as `eng_fiction_2019` are accepted but silently fall back. This is documented here so the genre split is implemented via raw datasets (§3.2), not via the API.
- **Rate limiting:** the API is undocumented and rate-limited (HTTP 429 observed in the literature). Retrieval script: one term per request, sleep ≥ 2 s between requests, exponential backoff on 429, retries ≤ 10. All raw JSON responses are written verbatim to `data/raw_ngram/` with timestamps; analysis reads only from that cache.
- **Provenance:** Michel et al. 2011 (Science); Lin et al. 2012 (Literary and Linguistic Computing); Ngram dataset v3 (20200217) for the raw-data sensitivity runs.

### 3.2 Genre sensitivity source: raw Ngram v3 datasets

- Files (downloaded once, hashed and archived): `googlebooks-eng-fiction-all-1gram-20200217-*.csv.zip` and `googlebooks-eng-nonfiction-all-1gram-20200217-*.csv.zip`, plus their `total_counts` files.
- Because v3 files are alphabetically grouped, only the chunks containing the 20 lexicon terms are downloaded (range requests); the 20 terms are sparse in the files, so full download is unnecessary.
- Per-corpus per-year match counts are extracted and normalized by that corpus-year's `total_counts` to relative frequencies, matching the API convention.
- **Fallback (pre-registered):** if the raw datasets cannot be downloaded (bandwidth/size), H1d is reported as "not run — primary corpus only," and this is listed in §10 rather than silently dropped.

---

## 4. LEXICON (exactly 20 terms — frozen)

Religious terms R (10): `sin, salvation, damnation, repentance, grace, faith, worship, eternal life, church attendance, prayer`
Self-religion terms S (10): `self-esteem, self-improvement, self-care, personal development, mindfulness, well-being, self-actualization, manifestation, inner peace, positive thinking`

Full definitions, intended senses, ambiguity flags, and per-term validation expectations: LEXICONS_Codebook.md §1. No term may be added, removed, or re-spelled after registration (H1f flag rule excepted).

---

## 5. ANALYSIS PLAN (executed in this order; no result-dependent branching)

1. **Series construction.** For each corpus (eng-2019 primary; fiction, non-fiction for H1d): S_t = Σ self-term frequencies; R_t = Σ religious-term frequencies; share_t = S/(S+R); L_t = ln(S_t/R_t). If a year has S_t = 0 or R_t = 0, that year is dropped (not expected for these terms in eng-2019; would be recorded if it occurs).
2. **H1a (primary).** OLS of L_t on year, 1800–2019, Newey-West (HAC) SEs with lag 1; one-sided test of β > 0; report β, SE, t, p, 95% CI, R². Robustness: Mann–Kendall τ on L_t.
3. **H1b.** Sustained-crossover algorithm (§2.2). Report t* or "none."
4. **H1c.** Slopes on 1900–1999 and 2000–2019 (and 2000–2008 alone as regime check); interaction test with HAC SEs.
5. **H1d / H1e.** Re-run 1–4 on the fiction and non-fiction series (H1d, primary corpus engine replaced by raw datasets) and on S minus `self-esteem` (H1e).
6. **Exploratory (labeled "Exploratory Analysis," not part of confirmatory claims):** PELT change-point detection (ruptures package, penalty = BIC, min segment length = 5 years) on L_t; per-term normalized trajectories; decadal share table; term-level crossover years (first year each S-term individually exceeds... — no, per-term trajectories only).
7. **Reporting table.** One master table with all corpus × lexicon variants of β, t*, and slopes; interpretations rest on the primary specification (eng-2019, full lexicon); all variants are shown, never selected from.

---

## 6. SENSE-VALIDATION GOLD SET (H1f) — procedure pre-registered

Purpose: estimate the share of each term's occurrences that carry the intended sense (religious / self-religious), because several terms are polysemous (`grace`, `faith`, `manifestation`, `well-being`, `self-care` — see codebook).

1. **Sampling.** Per term, up to 50 short book snippets containing the term, retrieved via the Google Books API (q="{term}", `langRestrict=en`), taking the first 50 unique snippets; if any snippet dates pre-1950, the sample is re-weighted to include up to 25 pre-1950 items (books of both eras are in the corpus).
2. **Coding.** Three categories per snippet: TARGET (intended sense), OFF (different sense), AMBIG (indeterminate). Two independent human coders, blind to each other's labels. Cohen's κ ≥ 0.70 required; disagreements resolved by a third coder (adjudication), with the adjudicated label final.
3. **Metric.** precision = TARGET / (TARGET + OFF); AMBIG excluded from the denominator. Flag rule: precision < 0.70 → term is flagged.
4. **Use.** All primary analyses are rerun with flagged terms excluded (H1e covers `self-esteem` explicitly; the flag rule extends it to any term); both full-lexicon and reduced-lexicon results are reported side by side.
5. **Timing.** The gold set is built and its results stored in the OSF project BEFORE any analysis in §5 is run (the procedure is frozen in this registration; the results are uploaded as files, not as an amendment to the protocol).
6. **Rater logistics.** Second human rater required (README §10.5; sister-project lesson: single-annotator gold sets were the root of months of problems). Full logistics: GOLD_SET_Plan.md.

---

## 7. FALSIFICATION / INTERPRETATION RULES

- H1a is falsified if the one-sided test on the 1800–2019 slope does not reject β ≤ 0 at α = 0.05 in the primary specification.
- H1b: report t* under the graded reading in §2.2 regardless of outcome.
- H1c is falsified if the 2000–2019 slope does not exceed the 1900–1999 slope.
- H1d/H1e are robustness checks, not independent confirmations: a sign flip in a sub-corpus makes the overall verdict "ambiguous" and is reported as such, not silently ignored.
- No hypothesis is retrofitted. Exploratory results are labeled exploratory.
- Any deviation from this protocol (including fallback activations in §3.2) is logged in §10 with a date and reason.

---

## 8. REPORTING PLAN

- Figure 1: L_t and share_t over 1800–2019 (smoothed for display only), crossover marked.
- Figure 2: per-term normalized trajectories (10 religious, 10 self).
- Table 1: master variant table (§5.7).
- Table 2: sense-validation results (per-term precision, κ, flags).
- Appendix: retrieval code, raw JSON cache hashes, gold-set annotations (anonymized).
- Language for the paper: "cultural prominence (supply-side measure)" everywhere; never "belief."

---

## 9. KNOWN LIMITATIONS (pre-registered, published as-is)

1. Books are a publishing/supply measure: vocabulary prominence ≠ belief or consumption. Claim restricted to "cultural prominence."
2. Ecological: no individual-level substitution can be inferred.
3. OCR and digitization artifacts; low book counts in early 19th century; changes in book production rates.
4. 2009–2019 books derive from a different scan program (known Ngram regime change); handled via the H1c regime check and the 1800–2008 sensitivity.
5. Multi-word phrases ("eternal life," "church attendance," "inner peace," "personal development," "positive thinking") and hyphenated tokens ("self-esteem," "well-being") are treated exactly as Google tokenizes them.
6. WEIRD scope: English-language books only (mostly US/UK); the West is the declared scope of the project.
7. Polysemy is controlled, not eliminated: the H1f flag rule is the only guard; terms flagged as low-precision cannot be made precise post-hoc.

---

## 10. DEVIATIONS LOG (empty at registration)

| Date | Deviation | Reason | Impact |
|---|---|---|---|
| 2026-08-10 | H1f sense-validation: the two-human-coder requirement (κ ≥ 0.70, §6.2–6.3) is replaced by a 3-model LLM judge panel — `nemotron-3-ultra-free` (tie-break) + `laguna-s-2.1-free` + `mimo-v2.5-free` (three distinct model families, served free via the opencode gateway, invoked through the opencode CLI v1.18.16 `opencode run --model <id>`), each run blind from a neutral directory with no project context (sister-project safe-mode rule, enforced via the CLI `--dir` flag), single-shot default-sampling calls (CLI exposes no temperature parameter), strict JSON output, 2-of-3 majority label; two-way tie broken by nemotron-3-ultra-free; no majority → snippet dropped from precision, kept in the agreement table. Panel selection (2026-08-10, BEFORE any gold-set data existed, on handcrafted test snippets only): strict-JSON 3/3 + correct 3/3 on target/off spot-checks for all three panel members; evaluated and EXCLUDED: deepseek-v4-flash-free (non-compliant JSON ~30%, 90–120s+ timeouts), longcat-2.0-free (occasional conversational drift), north-mini-code-free (timeouts), big-pickle-free (empty output), ling-3.0-tiny-free (compliant but too small). | Author directive: human raters infuse annotation bias (empirically observed by the author); human raters dropped for all annotation in this project. | Precision < 0.70 → flag rule unchanged (§6.4). The reliability statistic reported in the paper changes from human Cohen's κ to inter-judge agreement (pairwise κ + majority %); this is disclosed in the methods appendix. |
| 2026-08-10 | Snippet sampling: Google Books API queries are split by era (publishedDate 1500–1950 / 1950–2026) to approximate the §6.1 pre-1950 re-weighting rule; snippets without a text snippet field are skipped; the first 25 unique per era are taken. | API constraint (no direct random sampling across eras). | Era balance preserved; per-term sample size reported (target 50, minimum accepted and reported if lower). |
