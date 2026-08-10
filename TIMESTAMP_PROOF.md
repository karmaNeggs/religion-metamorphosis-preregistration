# TIMESTAMP PROOF — Phase 0 pre-registration, 2026-08-09 (UTC)

**This is the record that the Ngram + Trends protocols were frozen before any data pull.**

## 1. What is protected

| Artifact | SHA-256 |
|---|---|
| `preregistration_snapshot_2026-08-09.zip` (the 6 frozen documents) | `504369823c1f0bb1c37dce532011df1ea64b0a86ba9a8a2f60b28c3d69a85b1e` |
| `MANIFEST_SHA256.txt` (per-file hashes of the 6 documents) | `fbc020eaf34a3667a2f0901e120aee9dbf9ff543d83adcbb5d303b5c989b30f3` |

Full per-file manifest: see `MANIFEST_SHA256.txt`.

## 2. Bitcoin-anchored timestamp (OpenTimestamps, no account, free)

- Submitted **2026-08-08T22:36:31Z (UTC)** to **four independent calendar servers**:
  `finney.calendar.eternitywall.com`, `bob.btc.calendar.opentimestamps.org`,
  `btc.calendar.catallaxy.com`, `alice.btc.calendar.opentimestamps.org`.
- Proofs: `preregistration_snapshot_2026-08-09.zip.ots` and `MANIFEST_SHA256.txt.ots`
  (both in this folder and in the GitHub repository).
- Status at snapshot time: submitted + pending Bitcoin confirmation (normal — calendars
  confirm into a block within ~1–2 days). The `.ots` files bind the hashes to calendar
  attestations; the Bitcoin Merkle anchor completes the chain.
- **CONFIRMED 2026-08-10:** both proofs upgraded; attestations resolved to **Bitcoin blocks
  961644, 961645, and 961661** (three independent calendar attestations, merkle roots below):
  - `afab5da2b944f7ddc28e380a536442d895865fc896a2e132e818cb4641b74176` (block 961645)
  - `ab547c0ac1e04282f11573641cbe7b5aac740bc6318834ced91601d819e802f7` (block 961661)
  - `f63d7634cad5a1a559dd869a4fee7d2644a199b1f17e7ba2ca8f9fbb33fe6feb` (block 961644)
  Verify via `ots info <file>.ots` (no Bitcoin node required; `ots verify` needs a node or
  `--no-bitcoin` for structural verification).
- **Verification (anyone):**
  ```
  pip install opentimestamps-client
  ots verify preregistration_snapshot_2026-08-09.zip -f preregistration_snapshot_2026-08-09.zip.ots
  ots verify MANIFEST_SHA256.txt -f MANIFEST_SHA256.txt.ots
  shasum -a 256 preregistration_snapshot_2026-08-09.zip   # must equal the manifest entry
  ```

## 3. Permanent public archive (Software Heritage, no account, free)

- GitHub origin: `https://github.com/karmaNeggs/religion-metamorphosis-preregistration`
  (public, created 2026-08-09 UTC via `gh` CLI).
- SWH save request: id `2413615`, **accepted → succeeded**, visit status `full`,
  visit date `2026-08-08T22:38:28.960000+00:00` (UTC).
- Snapshot SWH-ID: `swh:1:snp:d81428287f2f8c38edda0d346dae7e13ba527069`
- Browse: `https://archive.softwareheritage.org/browse/origin/https://github.com/karmaNeggs/religion-metamorphosis-preregistration/`
- Snapshot: `https://archive.softwareheritage.org/swh:1:snp:d81428287f2f8c38edda0d346dae7e13ba527069;origin=https://github.com/karmaNeggs/religion-metamorphosis-preregistration`

## 4. What this provides vs the original OSF plan

- Same evidential core: the protocol texts, lexicons, and gold-set plan are frozen and
  verifiably existed before any data collection; the files are immutable (hash-bound) and
  permanently archived by an independent institution.
- Differences (disclose in the papers): **no OSF DOI**; timestamping is Bitcoin-based rather
  than platform-based; the registration is a repository snapshot, not an OSF form. The
  discovery paper will state this as a documented deviation from STUDY_PLAN decision #8.

## 5. Follow-up checklist

- [x] `ots upgrade` both `.ots` files — **DONE 2026-08-10; confirmed at blocks 961644/961645/961661**
- [x] Paste GitHub + SWH links into README.md §10 and STUDY_PLAN_TwoPapers.md decision #8
- [ ] Keep the repo untouched from now on (any further versioning happens in separate repos/folders)
