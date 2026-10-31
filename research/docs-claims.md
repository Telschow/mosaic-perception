# Documentation and claim consistency audit (issue #42)

Source-level verification at `d3e88d9` (main) on branch `research/docs-claims`.
No documentation or code was modified; this file is the only addition.

Scope read: `README.md`; `docs/` implementation-status, metrics, limitations,
measurement-models, architecture, technical-walkthrough, demo-script,
demo-walkthrough, audit-report, core-validity-audit, release-checklist, roadmap,
evaluation-protocol; `app/streamlit_app.py`, `app/data_prep.py`; cross-checked
against `src/`, `tests/`, `.github/workflows/ci.yml`, `Makefile`,
`artifacts/benchmark/{report.md,benchmark.json}`. Line numbers are per file.

## Summary

- Headline counts in the README (1/6/8 and 7/3/5 RMSE tallies, precision 14/15,
  MOTA and GOSPA 14/16, recall 12/16, IDF1 2/5/9, NEES 15/15, NIS 13/14, identity
  switch sums 388.5 -> 241.8, duplicate-track figures, gate-rejection figures,
  retrodiction figures) **are confirmed** against `benchmark.json`.
- **One defect class matters most (F1):** the committed `report.md` was rendered at
  an older commit than `benchmark.json`. Every bias-estimation number in the README
  and technical walkthrough comes from the stale report and disagrees with the
  committed JSON, which a fresh run at HEAD reproduces. `make provenance-check`
  passes anyway.
- Other findings: CI trigger wording (F2), seed 42 (a reserved held-out seed)
  used as the default everywhere (F3), a historical audit still asserting
  that fragmentation is unsupported (F4), and several stale or over-strong sentences
  (F5-F14).

Legend: status = confirmed / stale / contradictory / unverifiable. Kind =
defect (D), hypothesis (H), unimplemented feature (U). Confidence H/M/L.

## Findings

### F1. Committed `report.md` is stale relative to `benchmark.json`; README quotes the stale values (P1, D, confidence H)

- Locations: `artifacts/benchmark/report.md:10`, `artifacts/benchmark/benchmark.json:3`,
  `README.md:198-211`, `docs/technical-walkthrough.md:88-94,246`.
- Observed: `report.md` says `Git commit: 9bdeccdd...`; `benchmark.json` says
  `e433b841...`. `git diff --stat 9bdeccd e433b84 -- src` touches 5 files
  (`tracker.py`, `association.py`, `experiment.py`, `markdown.py`, `cli/main.py`;
  commit message: "group-frozen bias correction ... configured bias only for
  vision methods"). `per_seed.csv` and `benchmark.json` were regenerated;
  `report.md` was not.
- Reproduction: ran `mosaic benchmark --scenario
  sensor_disagreement_within_gate_low,sensor_disagreement_within_gate,
  sensor_disagreement_within_gate_high,sensor_disagreement_large_bias --seeds 0-24
  --duration 10.0` at HEAD. Every `aggregate` field matches the committed
  `benchmark.json` to 1e-9 (0 differing keys, 12 method/scenario pairs), and the
  rendered `fused_bias_estimated` rows differ from the committed `report.md`
  in all four scenarios (115 differing report lines in total, all in
  `fused_bias_estimated` rows or the bias-vs-fused paired table).
  A full 16-scenario regeneration was started but not completed (too slow here), so
  the other 12 scenarios' bias-estimated rows are expected, not shown, to be stale.
- Claim vs evidence (README -> committed JSON, HEAD run identical to JSON):

  | Claim (README) | README | JSON / HEAD |
  |---|---|---|
  | Final bias estimates (0.010/0.015/0.020) | 0.0100, 0.0149, 0.0198 | 0.0101, 0.0149, 0.0199 |
  | RMSE gain vs fused | 0.075, 0.117, 0.198 | 0.073, 0.113, 0.192 |
  | Precision gain vs fused | 0.056, 0.122, 0.139 | 0.064, 0.110, 0.131 |
  | MOTA gain vs fused | 0.134, 0.320, 0.378 | 0.155, 0.297, 0.359 |
  | Bias-est. precision | 0.673, 0.683, 0.674 | 0.681, 0.671, 0.666 |
  | Bias-est. MOTA | 0.467, 0.489, 0.470 | 0.487, 0.466, 0.450 |
  | Bias-est. distance-only RMSE | 0.200, 0.202, 0.207 | 0.202, 0.206, 0.215 |
  | Updates/seed at 0.12 rad | about 1.4 | 1.28 (1.3) |

  The README sentence "distance-only RMSE ... is slightly lower than range-only's
  0.213" (`README.md:207`) is **false at HEAD for the 0.020 rad case** (0.215 > 0.213).
  The report's own Findings bullet (`report.md:1088`, "MOTA better in 3, worse in 0,
  inconclusive in 13; precision worse in 0") also differs from JSON (MOTA worse in 1,
  inconclusive 12; precision worse in 1, inconclusive 11).
- Why the gate misses it: `scripts/check_artifact_provenance.py` reads only
  `benchmark.json`; it passes ("artifact from e433b8411bf2 ... source unchanged")
  while `report.md` and `README.md` are out of date.
  `docs/evaluation-protocol.md:105-113` describes the check as guaranteeing the
  artifact "describes this tree"; that holds for the JSON, not the report.
- Recommended: regenerate `artifacts/benchmark` (`make benchmark`), re-read every
  bias-estimation sentence in README and technical-walkthrough from the new report,
  and make the provenance check compare the commit recorded in `report.md` (and the
  CSV, if it records one) with `benchmark.json`.

### F2. "CI on every push" is not what the workflow does (P2, D, confidence H)

- Locations: `README.md:23,42`, `docs/evaluation-protocol.md:91`, issue #29 comment
  ("runs on every push and pull request"); evidence `.github/workflows/ci.yml:3-7`.
- Observed: triggers are `push: branches: [main]` and `pull_request: branches: [main]`.
  A push to any other branch does not run CI unless a PR to main is open.
- Expected: wording "on every push to main and every pull request to main".
- Status: contradictory. Not executed (reading the workflow file is sufficient).

### F3. Reserved held-out seed 42 is the default in quickstart, demo and the app (P2, D, confidence H)

- Locations: `README.md:60`, `docs/demo-walkthrough.md:17`,
  `app/streamlit_app.py:40` (slider 0-100, default 42), label
  `app/data_prep.py:17` ("development seeds only").
- Observed: held-out range is 25-49 (`README.md:9,138`; `evaluation-protocol.md:24`).
  `mosaic run --scenario nominal --seed 42` and the app's default run use a reserved
  seed. The app slider also permits the whole reserved range and seeds above 49, yet
  every view is captioned "development seeds only".
- Impact: contradicts the "no held-out seed has been run" wording in letter, and weakens
  the freeze discipline the README relies on (`README.md:139-141`). Not a
  benchmark-artifact issue: these are single ad-hoc runs.
- Recommended: use a development seed (for example 1) in README, demo walkthrough and app
  default, constrain the app slider to 0-24 or relabel it.

### F4. `core-validity-audit.md` asserts fragmentation is unsupported (stale) and other superseded facts in present tense (P2, D, confidence H)

- Location: `docs/core-validity-audit.md` V10 resolution row (line 55): "`track_fragmentation`
  is explicitly unsupported (`None`/`N/A`)". Code: `evaluation/metrics.py:149-170`
  (`interruptions`) computes it; `README.md:127-129`, `roadmap.md:32`,
  `limitations.md:28-32` say computed.
- Same file, other stale present-tense statements: V8 "There are 10 presets" (line 53;
  16 exist, `available_scenarios()` returns 16); "Current verification (local branch)
  ... 77 passed" (lines 59-64; `pytest --collect-only` reports 222); V6 cites
  `test_out_of_sequence_observations_are_explicitly_rejected` (line 51), which does not
  exist in `tests/` (grep for `def test_out_of_sequence_observations_are_explicitly_rejected`).
- The banner (lines 3-6) says "historical", but the "Resolution status" and "Current
  verification" headings read as current. The README links this file as
  authoritative for the v0.1.0 defects (`README.md:249-253,286`).
- Recommended: add a dated note to V10 ("later superseded: fragmentation implemented"),
  rename the two headings to "at the time of the fix", fix or drop the missing test name.

### F5. `limitations.md` quotes miscalibration coverage that does not match the report (P2, D, confidence H)

- Location: `docs/limitations.md:166-168`: "95% coverage is roughly 0.12-0.14".
- Observed: `uncertainty_miscalibration` Cov95 = 0.089 (range-only), 0.106 (fused),
  0.091 (bias-estimated) in `report.md` and JSON.
- Expected: "roughly 0.09-0.11". Claim direction (far below 0.95) holds.

### F6. "Every scenario with defined precision" and "often slightly lower RMSE" overstate (P2, D, confidence H)

- `docs/limitations.md:169-170`: "fused precision is lower in every scenario with defined
  precision". Observed (JSON tally): worse in 14, interval includes zero in 1
  (`sensor_disagreement_large_bias`), 1 undefined. README says 14 of 15.
- `docs/demo-walkthrough.md:67-70`: "fused position RMSE is often slightly lower, but
  precision is lower in every scenario with defined precision". Observed: headline RMSE
  favours fusion in 1 of 15 scenarios and goes against it in 6; only the distance-only
  matcher favours fusion (7 of 15). "Often lower" is wrong for the headline matcher and
  hides the matcher dependence that README, technical-walkthrough and demo-script state.
- Same file `limitations.md:153`: "The two sensor-disagreement scenarios" - there are four
  (`..._within_gate_low`, `_within_gate`, `_within_gate_high`, `_large_bias`); the
  0.010 and 0.020 rad presets are not mentioned (P3, stale).

### F7. Retrodiction "improves position accuracy" is only true for range-only (P3, D, confidence H)

- `README.md:213-216`, `docs/limitations.md:113-118`: "retrodiction improves position
  accuracy and consistency (RMSE 0.308 to 0.283 range-only and 0.329 to 0.335 fused)".
  Fused headline RMSE gets **worse** (0.329 -> 0.335, report row `delivery_delay` vs
  `delivery_delay_retrodiction`); the paired table gives +0.053 [+0.031, +0.074] for
  fused-minus-range in the retrodiction scenario (fusion against). Numbers themselves are
  confirmed (JSON: 0.308/0.283, 0.329/0.335, NEES/DOF 4.94 -> 1.90 and 11.34 -> 3.31,
  switches 6.92 -> 11.12 and 5.08 -> 13.04, MOTA 0.708 -> 0.636 and 0.437 -> 0.349).
- Also `README.md:217` uses first person ("I have not diagnosed why") unlike every other
  document, and `docs/implementation-status.md:91` says the effect "is diagnosed as worse
  and unexplained", which reads as a diagnosis. Wording only.

### F8. `architecture.md` says 10 presets (P3, D, confidence H)

- `docs/architecture.md:38`: "10 named presets". `technical-walkthrough.md:168` says 16;
  `python -c "from mosaic_perception.scenarios import available_scenarios;
  print(len(available_scenarios()))"` prints 16.

### F9. `metrics.md` fragmentation definition is ambiguous (P3, D, confidence M)

- `docs/metrics.md:61`: "total interruptions: frames where a matched object goes
  unmatched and is matched again later". Code (`metrics.py:149-170`) counts one
  interruption per gap, however many frames long (also stated in
  `limitations.md:28-31` and `README.md:127-129`). The metrics.md wording can be read as
  counting frames. Recommended: reuse the limitations wording.

### F10. Roadmap and release-checklist describe an older state as current (P3, D, confidence H)

- `docs/roadmap.md:19` "current branch, unreleased"; `:36` "77 tests" (222 now);
  `:48` "Multi-object crossing scenarios and association stress tests" is still unchecked
  although `crossing_targets` and `dense_clutter` exist and are in the benchmark.
- `docs/release-checklist.md:11`: "The current branch has not been released and must not be
  pushed or tagged" - the branch was merged (PR #35).
- `docs/implementation-status.md:6-7` says historical documents "point here";
  `docs/roadmap.md` has no pointer to it (grep `implementation-status` in roadmap returns
  nothing), and implementation-status:182-188 treats only "superseded sections" of
  roadmap as stale without saying which.

### F11. CI description does not match the Makefile targets it cites (P3, D, confidence M)

- `docs/implementation-status.md:157-159` ("`make lint format-check typecheck test ...`")
  and `docs/limitations.md:205-210`. CI runs `ruff format --check .` (whole tree,
  `ci.yml` "Format check (full tree)") while `make format-check` runs
  `ruff format --check src tests`; CI never invokes `make`. Executed: `ruff format
  --check .` -> "138 files already formatted"; `ruff check app scripts` -> pass.
  `ruff check` in CI covers `src tests` only (not `app/`, `scripts/`), and the app and
  scripts are not type-checked (`mypy src`). Wording-level.

### F12. Byte-for-byte golden claim fails in this environment (P2, H for cause, confidence M)

- Locations: `README.md:23`, `docs/evaluation-protocol.md:93-103`; boundary
  stated at `docs/limitations.md:179-181` ("not guaranteed byte-identical across
  platforms").
- Executed: `make benchmark-golden-check` at HEAD -> `FAIL benchmark.json: differs from golden
  copy`, `FAIL per_seed.csv: differs from golden copy`. After normalising 40-hex hashes
  the only differences are last-digit float noise (for example
  `anees_position` 4.241703744751963 vs 4.2417037447519625). `numpy 2.5.4` and
  `scipy 1.18.1` equal the `uv.lock` pins and Python is 3.12.16, so the cause is probably
  CPU or BLAS differences (hypothesis, not isolated). `make provenance-check` passes.
- Impact: the "byte-for-byte" claim is unqualified in README and protocol; the CI result
  on GitHub runners could not be observed from here (unverifiable). Recommended: state the
  platform boundary next to the claim, or compare with a numeric tolerance.

### F13. Items checked and found consistent (confirmed)

- Method count and names: three methods `range_only`, `fused`, `fused_bias_estimated`
  everywhere (`METHODS` in `experiment.py`; README:7; architecture:88; app
  `METHOD_SYMBOLS`). `mosaic run` evaluates two methods only (`cli/main.py:341` calls
  `run_pair(config)` without bias estimation) while `compare`, `evaluate`, `benchmark` and the
  app run three; README does not say so (P3, wording).
- Bias estimation default off, enabled by `include_bias_estimation=True`
  (`experiment.py:200`); retrodiction opt-in `delayed_update="retrodiction"`
  (`scenarios.py:152`, `tracker.py:81`). Tests named in implementation-status
  (42 names checked) all exist except the V6 name in F4.
- Test counts per file in implementation-status (12, 11, 6, 3, 35, 13, 18, 3, 33, 24, 9,
  7, 12, 5) all match `def test_` counts.
- TrackEval scope: `tests/unit/test_trackeval_crosscheck.py` has 4 parametrised comparisons
  plus a live guard; ran `pytest tests/unit/test_trackeval_crosscheck.py` -> 5 passed (guard
  did not skip, TrackEval is installed). Pinned commit `12c8791b` equals `pyproject.toml:69`.
  "Not cross-checked" list in metrics.md:117-121 and implementation-status:108-111 agree.
- Held-out wording: consistent in README, protocol, limitations, walkthrough, demo script,
  report and `data_prep.py` (except F3).
- Gates: chi2(3/2/1, 0.95) in `tracking/association.py:52-54` match README and
  measurement-models. Staleness `dt + 1e-6` matches.
- Secret scan: gitleaks pinned 8.30.1, checksum-verified, `fetch-depth: 0`; actions pinned to SHAs; top-level
  `permissions: contents: read` (confirmed in `ci.yml`). "46 commits, no leaks" is a historical
  result recorded on #29 (repo now has 61 commits); not re-run (unverifiable offline).
- Provenance check passes at HEAD (`provenance OK`), but see F1.
- Simulated-data labelling: `SIMULATED_LABEL` is attached to the title, metrics, scene and
  scenario panels (`streamlit_app.py:36,61,70`; `data_prep.py:211`); test
  `test_views_are_labelled_as_simulated_and_link_limitations` exists. No "not implemented"
  claim appears in app or docs about live features (grep for "not implemented" only hits
  historical audit text and the deliberate no-replay design). `README` stale/N/A claims for
  `stale_rejection` are consistent: report shows RMSE/precision `N/A`; MOTA, IDF1 and recall are
  0.000 and GOSPA 3.000 (defined, not fabricated).
- Open issues cited: #7 and #34 are OPEN.

### F14. Unverifiable or low-confidence items (P3)

- "Preregistered" within-gate values (`README.md:190`, implementation-status:29,
  `limitations.md:156`): scenarios were added in `43b6e4a` ("preregistered ... closes #6"),
  but the 0.015 value existed before and no timestamped plan separates "chosen before results"
  from the code history. Cannot be verified from the repository.
- The app's "Full text: [`docs/limitations.md`]" (`streamlit_app.py:79`) is a relative link
  inside `st.markdown`; whether it resolves in a running app was not tested (no browser).
  `test_app_smoke.py` renders the page headlessly and cannot show link behaviour.
- `implementation-status.md:145-148` states the three-method behaviour twice (line 145-146 and
  again in the Evidence list); cosmetic.
- Rendered report claims in the 12 scenarios not regenerated (F1): unverified beyond the
  JSON-derived tallies above.

## Claims table

| # | Claim | Location | Evidence | Status | Correction |
|---|---|---|---|---|---|
| 1 | Bias estimates 0.0100/0.0149/0.0198, gains 0.075/0.117/0.198 etc. | README:198-211; tech-walkthrough:88-94 | JSON + HEAD run: 0.0101/0.0149/0.0199, 0.073/0.113/0.192 | stale | Regenerate report, re-quote (F1) |
| 2 | distance-only bias-est. RMSE below range-only's 0.213 | README:207 | high case 0.215 | contradictory | F1 |
| 3 | ~1.4 updates/seed at 0.12 rad | README:210; tech-walkthrough:94 | 1.28 | stale | F1 |
| 4 | Report commit is the artifact commit | report.md:10 vs benchmark.json:3 | 9bdeccd vs e433b84 | contradictory | Regenerate; extend provenance check |
| 5 | CI on every push | README:23,42; eval-protocol:91 | ci.yml:3-7 main only | contradictory | Reword |
| 6 | Golden check byte-for-byte | README:23; eval-protocol:93-103 | local run fails on 1-ulp noise | unverifiable (CI) / observed fail locally | State platform boundary |
| 7 | "development seeds only" while seed 42 default | data_prep:17; app:40; README:60 | 42 in reserved 25-49 | contradictory | F3 |
| 8 | Fragmentation unsupported | core-validity-audit:55 | metrics.py:149 | stale | F4 |
| 9 | 10 presets | architecture:38; core-validity:53 | 16 | stale | F4/F8 |
| 10 | 77 tests passing | roadmap:36; core-validity:64 | 222 collected | stale | F4/F10 |
| 11 | Coverage 0.12-0.14 | limitations:166-168 | 0.089-0.106 | contradictory | F5 |
| 12 | Precision lower in every scenario | limitations:170; demo-walkthrough:68 | 14/15 | contradictory | F6 |
| 13 | Fused RMSE often slightly lower | demo-walkthrough:68 | 1/15 headline | contradictory | F6 |
| 14 | Two sensor-disagreement scenarios | limitations:153 | four | stale | F6 |
| 15 | Retrodiction improves position accuracy | README:213; limitations:113 | fused 0.329 -> 0.335 | contradictory (partial) | F7 |
| 16 | Historical docs "point here" | implementation-status:6 | roadmap has no pointer | contradictory | F10 |
| 17 | RMSE tallies 1/6/8, 7/3/5; precision 14; MOTA/GOSPA 14/16; recall 12/16; IDF1 2/5/9 | README:148-170; walkthrough; demo-script | JSON tally script | confirmed | - |
| 18 | NEES above in 15 (vel 14), NIS below 13/14 | README:178-184 | JSON | confirmed | - |
| 19 | Identity switches 388.5 -> 241.8 | README:170-177; limitations:137-141 | JSON sum 388.52/241.80 | confirmed | - |
| 20 | Duplicate tracks 38.9/39.3, 8.6/73.4; gates 34.2/38.9/39.3; 0.0/1.8/5.7 | README:166-169; limitations:33-37 | JSON | confirmed | - |
| 21 | Gate rejection 264.7/275.2, 10.2 applied; 20.8/30.8/52.8 | README:186-193 | JSON | confirmed | - |
| 22 | TrackEval: MOTA, IDF1/IDP/IDR, counts, IDSW agree on 4 sequences | metrics:72-121; impl-status:108 | pytest 5 passed | confirmed | - |
| 23 | Three methods in app; N/A not zero | impl-status:131-146; app | data_prep, tests pass | confirmed | - |
| 24 | Seeds 25-49 not run | README:9,138; others | report.md:11 seeds 0-24; JSON seeds | confirmed | - |
| 25 | "Preregistered" bias values | README:190 | no timestamped plan | unverifiable | - |

## Commands executed

```
gh issue view 42; gh issue view 7/34; gh issue view 29 --comments
python -c "from mosaic_perception.scenarios import available_scenarios; print(len(available_scenarios()))"   # 16
python -m pytest --collect-only -q                                    # 222 tests
python -m pytest -q tests/unit/test_trackeval_crosscheck.py tests/unit/test_app_smoke.py tests/unit/test_app_data_prep.py -rs   # 11 passed
make provenance-check                                                 # OK (reads benchmark.json only)
make benchmark-golden-check                                           # FAIL, 1-ulp float noise
ruff format --check .; ruff check app scripts                         # pass
mosaic benchmark --scenario <4 sensor_disagreement scenarios> --seeds 0-24 --duration 10.0 --output /tmp/wg
```

JSON tallies were computed with a throwaway script over
`scenarios[*].paired_differences.{fused_vs_range_only,bias_estimated_vs_fused}` (interval excludes
zero on the unrounded bounds) and `aggregate.*_pooled` values against their `_low/_high`.
Rounded report tables undercount recall (8 vs the true 12) because bounds such as `+0.000` are
positive before rounding; the README uses the unrounded values correctly.

## Could not verify

- A full 16-scenario regeneration at HEAD (several minutes per scenario for `dense_clutter`;
  aborted). F1 is demonstrated for 4 of 16 scenarios.
- GitHub Actions behaviour (golden check on runners, secret scan result) - no CI access.
- Streamlit link behaviour and visual labelling in a real browser.
- Whether preregistration preceded results.
