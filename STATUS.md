# PROJECT STATUS — "Religion Metamorphosis" Discovery Paper (H1)

_Last updated: 2026-08-17 08:45 CEST_

## What this project is
Two-paper plan; Phase 1 runs Studies 1–2 (H1): the rise of self-religious language vs
religious language — Google Books Ngram (supply side, 1800–2019) and Google Trends
(demand side, 2004–2026, US). Everything is pre-registered, automated, zero manual steps,
zero human raters (author directive: human raters infuse bias).

## Done
- **Pre-registration (frozen 2026-08-09):** PREREG_Study1 (Ngram, H1a–f), PREREG_Study2
  (Trends, H2a–i), LEXICONS_Codebook, GOLD_SET_Plan — all v1.0 in `phase0_preregistration/`.
  Anchored by OpenTimestamps (Bitcoin blocks 961644/961645/961661 — verified), public GitHub
  repo `karmaNeggs/religion-metamorphosis-preregistration`, Software Heritage snapshot
  `swh:1:snp:d81428287f2f8c38edda0d346dae7e13ba527069`. No OSF DOI (disclosed in papers).
  All changes live in §10 deviation logs (8 entries total, incl. Internet Archive source
  substitution 2026-08-12 and BRFSS predictor fallback).
- **Annotation infrastructure:** human raters → 3-model LLM judge panel via the opencode CLI
  (free tier): `nemotron-3-ultra-free` (tie-break) / `laguna-s-2.1-free` / `mimo-v2.5-free`.
  Blind neutral-directory calls, strict JSON, 2-of-3 majority, pairwise κ + majority %
  reported. Panel empirically selected before any gold-set data; 5 other models rejected.
- **Data (all collected):**
  - Ngram: 20 terms × 220 years (1800–2019), verified, `data/raw/ngram/`.
  - Trends: 6 query groups (A 4/5 reps, B1/B2/C/CHB1/CHB2 5/5), medians written;
    9 state region files; predictors `pew_religiosity_2014.csv` (Pew RLS 2014,
    % highly religious) + `cdc_places_mental.csv` (BRFSS mental distress 2022–24 mean).
    51-state join verified.
  - GS-1 gold-set snippets: **built — 861 snippets, 37/40 cells** from Internet Archive
    (Google Books anonymous quota proved permanently dead). Six pre-1950 cells short by
    construction (terms barely existed then); reported per protocol. Pushed to repo.

## In progress
- **GS-1 judge panel: RUNNING** (background, pid in `ps`; log `/tmp/gs1_judge.log`).
  **208/2,583 judge calls** as of the timestamp above (~70/861 snippets fully labeled;
  labels flowing; overnight the free tier recovered and throughput jumped from ~1/min to
  sustained). Resumable JSONL logs in `data/gold/judge_logs/`; missing/noncompliant
  responses are retried or fails-open per the pre-registered logistics.

## Queued (automatic, no inputs needed)
1. Judge completes → `gold_set_gs1_labels_judges.csv` + `gold_set_gs1_summary.csv`
   (per-term precision, flags <0.70, pairwise κ, majority %).
2. Archive gold set: OTS stamp + repo push (per GOLD_SET_Plan timing rule).
3. Run `code/ngram/analyze_ngram.py` + `code/trends/analyze_trends.py` (gated on GS-1).
4. Write up results for the discovery paper.

## Key files
- Protocols: `phase0_preregistration/` (PREREG_Study1/2, LEXICONS_Codebook, GOLD_SET_Plan,
  README_Phase0, timestamp/).
- Code: `code/goldset/` (build_gs1_ia.py, judge_gs1.py, run_gs1.py),
  `code/ngram/`, `code/trends/` (retrieve/analyze/build_state_predictors).
- Data: `data/raw/ngram/`, `data/raw/trends/` (+`states/`), `data/gold/`.
- Repo: github.com/karmaNeggs/religion-metamorphosis-preregistration (live docs + data).