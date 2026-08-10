# GOLD SET PLAN — Phase 0 + future phases

**Status:** GS-1 (sense validation) is part of the Phase 0 registration family and must be built before any Ngram analysis runs. GS-2…GS-4 are scheduled for their phases; the *procedure* below is fixed now, the *content* is frozen per phase.

**The panel rule (replaces the former two-human-coder rule, README §10.5; amended 2026-08-10 by author directive — human raters infuse annotation bias, empirically observed in the sister project; human raters are dropped for ALL annotation in this project):** every annotation runs through a 3-model LLM judge panel — `nemotron-3-ultra-free` (tie-break) + `laguna-s-2.1-free` + `mimo-v2.5-free` (three distinct model families, opencode gateway free tier, invoked as `opencode run --model <id>` via the opencode CLI v1.18.16). Each judge runs blind from a neutral directory with no project context (enforced per call with the CLI `--dir` flag; sister-project safe-mode rule), single-shot default sampling, strict JSON output, 2-of-3 majority label; ties broken by nemotron-3-ultra-free; no majority → dropped from precision, kept in the agreement table. No manual intervention anywhere in the pipeline.

---

## GS-1 — Ngram term-sense validation (Phase 0, ~1,000 snippets)

- **Purpose:** estimate sense-precision of each of the 20 Ngram lexicon terms (LEXICONS_Codebook §1); feed the H1f flag rule (precision < 0.70 → flag, reduced-lexicon rerun).
- **Sampling:** per term, up to 50 short book snippets containing the term via the Google Books API (q="{term}", `langRestrict=en`, first 50 unique snippets; re-weight to include up to 25 pre-1950 snippets if available).
- **Coding scheme:** TARGET (intended sense) / OFF (different sense) / AMBIG (indeterminate).
- **Coders:** 3-model LLM judge panel (see panel rule above); each judge labels every snippet independently; 2-of-3 majority decides.
- **Metric:** precision = TARGET/(TARGET + OFF); AMBIG excluded. Inter-judge agreement (pairwise Cohen's κ across the three judge pairs + majority %) is reported alongside precision; agreement is not a gate (majority is the gold label by design, mirroring human adjudication).
- **Timing rule:** built and results archived (GitHub repo + timestamped snapshot) BEFORE any Ngram analysis (Study 1 registration §6.5).
- **Products:** `gold_set_gs1_snippets.csv` (anonymized), `gold_set_gs1_labels_judges.csv` (per-judge labels + majority), `gold_set_gs1_summary.csv` (per-term precision, pairwise κ, majority %, flag list).

## GS-2 — H2 relief/truth narrative gold set (Phase 2, 150 docs)

- **Purpose:** validate the relief-vs-truth annotation for deconversion narratives (Study 3).
- **Sampling:** 150 documents — ~100 YouTube deconversion-transcript excerpts ("I left the church" testimonies across ex-Christian / ex-Muslim / ex-Hindu / ex-Mormon channels) + ~50 memoir/blog excerpts (public domain + Wayback Machine). Stratified by tradition.
- **Coding scheme:** primary frame per document (relief / truth / mixed / other); time-course tags (relief/truth language before vs after the narrative's switch point); ex-Muslim apostasy-fear flag.
- **Coders:** 3-model LLM judge panel (panel rule above); majority label per document; pairwise κ + majority % reported.
- **Fallback (pre-registered in STUDY_PLAN H2):** if < 100 usable docs after cleaning, Study 3 is dropped from the discovery paper and H2 becomes literature-only.

## GS-3 — H6 religious-skeleton codebook set (Phase 3, 30 excerpts)

- 30 excerpts: 15 self-help (5 public-domain classics — Carnegie, Peale, Wattles, Dale + 1 more — and 10 fair-use excerpts from NYT-best-seller lists) × 15 scripture (KJV, Gita, Dhammapada).
- One judge-panel pass per codebook feature (8 features, LEXICONS_Codebook §4.1); feature-level majority labels; pairwise κ + majority % per feature reported.

## GS-4 — H5/H4 code sets (Phase 4)

- H5: 40 influencer transcripts (20 predicted-extraction-heavy, 20 predicted-delivery-heavy — sampled blind to scores) × extraction/delivery markers; judge-panel pass per marker.
- H4: 150 YouTube transcripts × blame-locus (individualizing/systemicizing); judge-panel pass (majority labels, pairwise κ + majority %).

---

## JUDGE-PANEL LOGISTICS (all gold sets)

1. **Models:** `nemotron-3-ultra-free` (tie-break), `laguna-s-2.1-free`, `mimo-v2.5-free` (opencode gateway free tier; CLI v1.18.16; selected 2026-08-10 on handcrafted test snippets — strict JSON 3/3 + correct 3/3 on target/off spot-checks, before any gold-set data existed). If a model is unavailable at run time, the run FAILS OPEN: that judge's labels are marked missing and the majority is computed over the remaining judges; a two-way tie is resolved by the pre-specified tie-break model (nemotron-3-ultra-free), and any snippet with no majority is dropped from precision but kept in the agreement table.
2. **Blinding:** each judge call runs from a fresh neutral directory (CLI `--dir` flag) with no project files, no chat history (`--session` never used), and no other judges' labels in the prompt.
3. **Order of operations:** codebook freeze → gold-set sample → independent judge calls → majority → precision/use → analyses. Never the reverse.
4. **Storage:** all gold sets live in `data/gold/` with version hashes recorded in the deviation logs of the relevant registrations; archives pushed to the public repo.
5. **In the papers:** pairwise κ + majority % tables and per-feature precision go in the methods appendix; a one-line statement "all annotations were majority labels from a 3-model LLM judge panel (nemotron-3-ultra-free / laguna-s-2.1-free / mimo-v2.5-free)" in the main text.
