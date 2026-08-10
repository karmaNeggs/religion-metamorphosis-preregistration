# LEXICONS & CODEBOOK — v1.0 (2026-08-09)

**Status:** §1 (Ngram 20-term lexicon) and §2 (Trends query groups) are **FROZEN for OSF registration** — they are part of PREREG_Study1_Ngram_H1.md and PREREG_Study2_Trends_H1.md. §3 (H2 lexicons) and §4 (future codebooks) are DRAFT for later phases and are NOT part of any registration.
**File status rule:** frozen sections are edited only via the deviations logs of the corresponding registrations.

Coding conventions used throughout: each entry states the **intended sense**, the **major off-senses**, an **ambiguity flag** (LOW / MODERATE / HIGH), and the **validation expectation** used in gold-set work (GOLD_SET_Plan.md).

---

## 1. NGRAM LEXICON — 20 TERMS (FROZEN)

Retrieved from the Google Books Ngram JSON API, eng-2019, case-insensitive, unsmoothed, 1800–2019. Hyphenated compounds (`self-esteem`, `well-being`) are single tokens in Google's tokenization; multi-word phrases (`eternal life`, etc.) are exact phrase matches.

### 1.1 Religious terms R (10)

| Term | Intended sense | Major off-senses | Ambiguity | Notes |
|---|---|---|---|---|
| `sin` | Theological transgression against divine law | Colloquial indulgence ("sinful dessert"), sports/health humor | MODERATE | Historically dominant sense is theological; colloquial uses rise after ~2000 — check era split in gold set |
| `salvation` | Deliverance from sin/eternal damnation by grace | Secular metaphors ("salvation of the economy") | MODERATE | Secularized uses common from the 19th c.; flag candidate |
| `damnation` | Eternal punishment | Mild profanity ("damnation!"), hyperbole | LOW | Near-exclusively religious |
| `repentance` | Remorse and turning from sin | Occasional non-religious moral regret | LOW | Near-exclusively religious |
| `grace` | Divine unmerited favor | Grace period, gracefulness, "saving grace" metaphor, given name | HIGH | Expected LOW precision — prime flag candidate; kept because the plan's lexicon requires it and the flag rule handles it |
| `faith` | Religious belief/trust in God | Secular trust ("faith in the system"), brand names, academic "faith and reason" | MODERATE | |
| `worship` | Religious devotion (of deity) | "Celebrity worship," "hero worship" metaphors | LOW | |
| `eternal life` | Afterlife | None material | LOW | Phrase; near-exclusively religious |
| `church attendance` | Participation in religious services | None material | LOW | The plan's practice-metric term; unambiguous |
| `prayer` | Communication with the divine | Political/institutional invocations (still religious sense) | LOW | |

### 1.2 Self-religion terms S (10)

| Term | Intended sense | Major off-senses | Ambiguity | Notes |
|---|---|---|---|---|
| `self-esteem` | Psychological self-evaluation (Maslow lineage) | Academic psychology literature itself | MODERATE | **Academic-inflation flag** — H1e sensitivity drops it; surges with 1980s–90s self-esteem research |
| `self-improvement` | Deliberate betterment of the self | None material | LOW | |
| `self-care` | Personal wellness maintenance | Medical self-management of disease | MODERATE | Pre-2015 uses skew medical; post-2016 surge is the self-religion sense |
| `personal development` | Self-help category (career/character growth) | Corporate HR usage | LOW-MODERATE | |
| `mindfulness` | Meditative attention practice (Buddhist-derived, secularized) | Scholarly clinical literature | LOW-MODERATE | Near-zero before ~1980; the ~2010s wave is the claim's signal |
| `well-being` | Subjective welfare/wellness | Economics/policy ("well-being" in GDP debates, "child well-being" in social work) | HIGH | **Flag candidate** — largest-count S term; off-senses are systemic, not self-religious |
| `self-actualization` | Maslow's need-hierarchy apex | Psychology textbook usage | LOW-MODERATE | Psychology-derived by design |
| `manifestation` | New Age "attracting reality through intention" | Mundane "manifestation of X" (symptom, phenomenon, legal/tech usage) | HIGH | **Flag candidate** — the New Age sense dominates only post-2015; earlier mass is off-sense |
| `inner peace` | New Age/self-help calm | None material | LOW | |
| `positive thinking` | Self-help affirmative mindset (Peale lineage) | Clinical "positive thinking" research | LOW-MODERATE | |

### 1.3 Frozen rules

- Exactly these 20 strings, no additions, no re-spellings.
- H1f flag rule (precision < 0.70 in the sense-validation gold set) is the ONLY removal path; removals are applied to a reduced-lexicon rerun, both versions reported.

---

## 2. TRENDS QUERY GROUPS — 9 QUERIES (FROZEN)

US, Web search, All categories, 2004-01 → collection date, monthly. Queries are compared only within anchored fetches (anchor `prayer`, sensitivity anchor `church`; see registration §3.2).

### 2.1 Group A — religious practice

| Query | Intended sense | Off-senses / noise | Ambiguity |
|---|---|---|---|
| `church` | Religious congregation/building | "Church" surnames/org names, "The Church" institutional brands | MODERATE |
| `prayer` | Religious communication | (anchor term; also matches devotional content) | LOW |
| `bible` | The religious text | Bible apps, study-program brands | LOW |
| `church service` | Religious services | Minimal | LOW |

### 2.2 Group B — self-spirituality

| Query | Intended sense | Off-senses / noise | Ambiguity |
|---|---|---|---|
| `meditation` | Contemplative practice | Minimal ("meditation" in legal/civil usage is negligible in search) | LOW |
| `mindfulness` | Secular mindfulness | Minimal | LOW |
| `manifestation` | New Age law-of-attraction practice | Legal/medical/scientific senses ("manifestation determination") | HIGH |
| `chakras` | New Age energy centers | Minimal | LOW |
| `astrology` | Divination/star signs | Horoscope apps (in-sense), "astrology" memes | LOW-MODERATE |

### 2.3 Group C — self-improvement products (EXPLORATORY ONLY; no confirmatory claim)

| Query | Intended sense | Off-senses / noise | Ambiguity |
|---|---|---|---|
| `self help` | The industry category | Books/events (in-sense); "self-help groups" (AA-style, off-brand) | MODERATE |
| `therapy` | Psychological therapy | Physical therapy, occupational therapy | HIGH |
| `coaching` | Life/career coaching | Sports coaching | HIGH |

### 2.4 Frozen rules

- Exactly these 9 queries (plus anchor `church` variant for sensitivity). `self help` is frozen as written (space, no hyphen); a `self-help` sensitivity pull is allowed and labeled.
- Any query whose monthly median across pulls is zero for > 12 consecutive months is reported as a data-quality flag, not silently dropped.

---

## 3. H2 DECONVERSION-RELIEF LEXICONS (DRAFT — Phase 2, NOT pre-registered)

Working word families for the relief-vs-truth annotation of deconversion narratives (STUDY_PLAN §H2). Final versions will be frozen with a gold set before the LLM-as-judge pipeline runs. Inclusion rule: word-family stems, inflections and derivations counted; negation handling and context-window rules to be fixed in Phase 2.

- **Relief family (draft):** relief, relieved, relieve, freed, freedom, liberate, liberation, peace, calm, lighter, burden (lifted), unburdened, clarity, coherent, coherence, gratitude, thankful, healing, healed, whole (as in "I feel whole"), finally, at peace, awakened (positive sense), home (as in "I came home"), joy, hope.
- **Truth family (draft):** evidence, reason, reasoning, rational, logic, logical, facts, truth, true, real, scientific, scientifically, objective, objectively, historical, history, archaeology, archaeology-verified, contradictions, contradictions (found), errors, error, myths, myth, debunk, skeptical, skepticism, critical thinking, knowledge, verifiable.

Phase 2 will also add a **time-course annotation** (relief/truth language before vs after the narrative's switch point), a **frame taxonomy** (relief / truth / moral / trauma / other), and apostasy-fear sensitivity handling for ex-Muslim content.

---

## 4. FUTURE CODEBOOKS (DRAFT — phases 3–5, NOT pre-registered)

Placeholders with operational definitions to be frozen in their phases. Final codebooks ship with kappa tables in the methods appendix of the discovery paper.

### 4.1 H6 religious-skeleton codebook (self-help vs scripture, Phase 3)
Features per 1,000 words (definitions from STUDY_PLAN §H6):
- **Prescriptive density:** `you must / should / need to / have to` (imperative constructions).
- **Interrogative density:** `why / who / what for / how (existential)` — Job as control.
- **Blame locus:** ratio of "you" (individual) vs "system/society/conditions" (systemic) blame constructions.
- **Ritual instructions:** steps, routines, numbered protocols.
- **Guru/authority:** named masters, instructor voice, "I have been through this."
- **Community:** `we / together / community / fellowship` (congregation presence).
- **Transcendence:** `universe / energy / oneness / higher power`.
- **Scientism markers:** `quantum / vibration / neuroscience / frequency`.

### 4.2 H5 extraction codebook (guru bifurcation, Phase 4)
- **Extraction markers:** course-upsell frequency, paid-community pushes ("join my inner circle"), subscription/merch density, identity-fusion language ("you are my family"), follower monetization intensity.
- **Delivery markers:** "you don't need me," free-content generosity, outward referral, community-building.
- Scored per influencer transcript set; bimodality tested (Hartigan dip + GMM/BIC).

### 4.3 H4 blame-locus codebook (amplification/funding asymmetry, Phase 4)
- **Individualizing content:** blame/agency at the person (self-optimization, personal responsibility) — call to action = personal change.
- **Systemicizing content:** blame/agency at structures (policy, inequality, systems) — call to action = collective action.
- Gold set: 150 YouTube transcripts; judge-panel pass (3-model majority, pairwise κ + majority % reported).

---

## 5. SHARED CODING RULES

1. Every annotation task has a written codebook (this file or its phase-version), a gold set, and a 3-model judge panel (nemotron-3-ultra-free / laguna-s-2.1-free / mimo-v2.5-free) with 2-of-3 majority labels before any labels are trusted (amended 2026-08-10 by author directive: human raters dropped for all annotation — rater-bias finding in the sister project).
2. Judge-panel runs follow the sister-project safe-mode protocol: each call from a neutral directory with no project context, no chat history, no inter-judge information leakage; strict JSON output.
3. Any term/query/code that fails its validation gate is reported; the main analysis is rerun without it; both versions are reported.
4. No annotations are produced from a single model (sister-project kappa-collapse lesson); ties are resolved by the pre-specified tie-break model and reported.
