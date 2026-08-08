# Religion Metamorphosis — Phase 0 Pre-Registration Snapshot

**Date of snapshot:** 2026-08-09 (UTC)
**Project:** "Religion Metamorphosis: The Neo-Religion of the Self" — Discovery Paper (Studies 1–2)
**Author:** Anupam Vashist

This repository is the public, time-stamped record that the Ngram and Google Trends study
protocols (H1) were **frozen before any data were pulled or analyzed**. It was created
automatically as an alternative to a manual OSF registration; the timestamping mechanism is
described below.

## Contents

- `preregistration_snapshot_2026-08-09.zip` — the frozen documents:
  - `PREREG_Study1_Ngram_H1.md` — Study 1 protocol (Google Books Ngram, 1800–2019): hypotheses
    H1a–f, exact API parameters, sense-validation flag rule, falsification rules.
  - `PREREG_Study2_Trends_H1.md` — Study 2 protocol (Google Trends, US 2004–2026): chained
    scaling via anchor query, sampling-noise protocol, breakpoint windows, state-level
    correlations, falsification rules.
  - `LEXICONS_Codebook.md` — the frozen 20-term Ngram lexicon and 9 Trends query groups with
    sense definitions and ambiguity flags.
  - `GOLD_SET_Plan.md` — gold-set construction plan (GS-1 sense validation and later phases).
  - `OSF_Checklist.md` — the original OSF upload plan (superseded by this repository).
  - `README_Phase0.md` — Phase 0 index and status.
- `MANIFEST_SHA256.txt` — SHA-256 of every frozen file and of the archive.
- `*.ots` — OpenTimestamps proofs for the archive and the manifest.

## How the timestamp works

1. `MANIFEST_SHA256.txt` records the SHA-256 hash of every frozen file and of the zip archive.
2. The zip and the manifest were submitted to **four independent OpenTimestamps calendar
   servers** on 2026-08-09 (UTC). The resulting `.ots` files bind each file's hash to a
   Merkle root that is anchored in the Bitcoin blockchain.
3. Anyone can verify, with only the files in this repository:
   ```
   ots verify preregistration_snapshot_2026-08-09.zip -f preregistration_snapshot_2026-08-09.zip.ots
   ots verify MANIFEST_SHA256.txt -f MANIFEST_SHA256.txt.ots
   ```
   (Install the client: `pip install opentimestamps-client`. If the attestation is still
   "pending confirmation," run `ots upgrade` on the `.ots` files and re-verify.)

## Verification of integrity

```
shasum -a 256 <file>   # must match MANIFEST_SHA256.txt
unzip -l preregistration_snapshot_2026-08-09.zip
```

## Deviation from the original plan

The STUDY_PLAN (2026-08-09, locked decision #8) specified pre-registration on OSF with a DOI.
OSF was skipped by the author; this Bitcoin-anchored timestamp + Software Heritage archive
(see `swh_snapshot_url.txt` when present) replaces it. The papers will disclose this as a
documented deviation: the protocols are time-stamped and immutable, but carry no OSF DOI.
