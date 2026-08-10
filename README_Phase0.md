# PHASE 0 — INDEX & STATUS

**Phase 0 (STUDY_PLAN_TwoPapers.md §6, weeks 1–3):** pre-register the Ngram + Trends protocols on OSF; write lexicons/codebooks; build gold sets.

**Status:** documents drafted and frozen at v1.0 (2026-08-09). **OSF was skipped by the author; pre-registration was executed instead via an automated alternative (2026-08-09):** OpenTimestamps (Bitcoin-anchored) + public GitHub repo + Software Heritage permanent archive. Full proof: `timestamp/TIMESTAMP_PROOF.md`. Nothing may be pulled or analyzed until `ots upgrade` has resolved the attestations (follow-up item) — the proofs exist and are pending Bitcoin confirmation, which is normal.

## Files in this folder

| File | Status | Purpose |
|---|---|---|
| `PREREG_Study1_Ngram_H1.md` | FROZEN v1.0 | Study 1 (H1 supply side): Ngram relative-share, log-odds, crossover, acceleration, robustness, H1f sense-validation rule, falsification, limitations, deviations log |
| `PREREG_Study2_Trends_H1.md` | FROZEN v1.0 | Study 2 (H1 demand side): Trends chained-scaling protocol, noise protocol, D_t divergence, breakpoint windows, state-level correlations, robustness, falsification |
| `LEXICONS_Codebook.md` | §1–§2 FROZEN; §3–§4 draft | 20-term Ngram lexicon + 9 Trends queries with sense definitions and ambiguity flags; H2 relief/truth lexicons (draft); H6/H5/H4 codebook skeletons (draft) |
| `GOLD_SET_Plan.md` | Procedure fixed | GS-1 sense validation (Phase 0, mandatory before Ngram analysis); GS-2/3/4 scheduled for later phases; dual-coder rules |
| `OSF_Checklist.md` | **SUPERSEDED 2026-08-09** | Original manual OSF plan — replaced by the automated OpenTimestamps + GitHub + Software Heritage route (see `timestamp/TIMESTAMP_PROOF.md`). Kept for the record; the discovery paper discloses the deviation (no OSF DOI). |

## Key technical findings locked during Phase 0 (2026-08-09)

1. **Ngram JSON API ignores sub-corpus codes** — verified empirically: `corpus=eng_fiction_2019` and `eng_nonfiction_2019` return the same series as `eng-2019`. Consequence: the genre split (H1d) must use the raw v3 datasets (20200217), not the API. This is documented inside the frozen protocol (§3.1–3.2).
2. **Ngram API returns relative frequencies only** (no raw counts) — fine: frequencies share one denominator (total 1-grams per corpus-year), so summing across terms of mixed n-gram length is valid.
3. **Case-insensitive searches return the aggregated `(All)` series** — used as the analysis series.
4. **Trends 5-term limit** → chained scaling with anchor `prayer` (sensitivity anchor `church`), median-of-5 pulls (protocol §3.2–3.3).

## Blocking items

1. ~~OSF account → registrations~~ **Replaced 2026-08-09 by automated timestamping** — GitHub repo `karmaNeggs/religion-metamorphosis-preregistration` + Software Heritage snapshot `swh:1:snp:d81428287f2f8c38edda0d346dae7e13ba527069` + OpenTimestamps proofs **confirmed at Bitcoin blocks 961644/961645/961661 (2026-08-10)**. Amendments snapshot (deviation-logged docs) stamped 2026-08-10, pending block confirmation.
2. ~~Second human rater for GS-1 dual-coding~~ **RESOLVED 2026-08-10** — author directive: human raters dropped for ALL annotation. Replacement: 3-model LLM judge panel `nemotron-3-ultra-free` (tie-break) / `laguna-s-2.1-free` / `mimo-v2.5-free` via `opencode run` (free opencode gateway models), blind neutral-directory calls, 2-of-3 majority; pairwise κ + majority % reported instead of human κ. Panel selected empirically on handcrafted snippets BEFORE any gold-set data (strict JSON 3/3, correct 3/3); deepseek-v4-flash-free, longcat-2.0-free, north-mini-code-free, big-pickle-free excluded (drift/timeouts/empty).
3. **Google Books API anonymous quota exhausted (429) on 2026-08-10** — GS-1 snippet fetch deferred until the daily quota resets (midnight PT); `code/goldset/build_gs1.py` is resumable.

## Phase 1 status (2026-08-10)

- Ngram retrieval: **complete** — 20 terms × 220 years (1800–2019), `CASE_INSENSITIVE (All)` series, cached in `data/raw/ngram/` (fixed a param bug: API requires lowercase `"true"` for `case_insensitive`; verified).
- Trends retrieval: **partial (16/39 pulls)** — A/B1/B2/C ×3 reps, CHB1/CHB2 ×2 reps in `data/raw/trends/`. Google 429 rate-limited the rest; remaining reps + `--states` pulls to run on a later day (protocol §3.3 mandates pulls spread over ≥2 days; median-of-N covers fewer reps).
- Analysis scripts `code/ngram/analyze_ngram.py` + `code/trends/analyze_trends.py`: **written, NOT executed** (gated on GS-1, protocol §6.5). State analysis additionally needs `data/raw/trends/states/pew_religiosity_2014.csv` + `cdc_places_mental.csv` (Pew 2014 Landscape table + CDC PLACES; one-time downloads, no accounts).
- GS-1 pipeline (2026-08-10): `code/goldset/build_gs1.py` (era-split fetch via Google Books API `publishedDate` 1500–1950 / 1950–2026, first 25 unique per era per term) + `code/goldset/judge_gs1.py` (3-model panel, resumable JSONL logs, 2-of-3 majority, tie-break, pairwise κ + majority % + per-term precision, flag < 0.70). Pipeline verified end-to-end on handcrafted snippets (15/15 judge calls clean, 3/3 correct spot-checks) before any real data; free tier throttles under sustained load → run sequentially (`--workers 1`), resume anytime.
- H1d genre split (fiction/nonfiction): optional heavy download of raw v3 datasets (~10–25 GB/corpus) via `code/ngram/retrieve_genre.py`; protocol §3.2 fallback (report as not run) is acceptable.

## Not in Phase 0 (do not start yet)

- Any Ngram/Trends data pull or analysis (Phase 1, after registrations exist).
- H2/H5/H6/H4/H8 data work (phases 2–5).
