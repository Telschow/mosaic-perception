# Comprehensive audit addendum, 2026-11-01

This is an addendum. The historical audit in
[mosaic-perception-comprehensive-audit.md](mosaic-perception-comprehensive-audit.md) is not changed;
section D of the appendix reconciles each of its findings against HEAD.

## 1. Commit and scope

- Commit: `8c13e9ae40bae8e8abd7ec5d6017a86610c2cce7` (`main`, merge of PR #90). Working tree clean.
- Scope: source, tests, scripts, artifacts, docs, docs site, CI and supply chain. Read-only: no
  code was changed, the held-out seeds were not rerun.
- Method: an independent source audit with executed probes (finite-difference Jacobians,
  covariance stress, tracker timing probes, held-out reproduction of one seed at HEAD), plus a
  lead review that re-checked the P1/P2 evidence and the issue backlog. Part of the work was done
  by AI agents (Claude Code); all claims cite file and line.
- CI at HEAD: green (CI run 67 on `8c13e9a`).

## 2. Executive summary

The core of Mosaic is sound and was re-verified by execution, not only by reading: Jacobians
match finite differences (max scaled error 9.2e-09 range-bearing, 6.5e-08 bearing), bearing
innovations wrap correctly, Joseph updates stay symmetric and positive definite over 3000 cycles,
gates use the right chi-square degrees of freedom, the three methods share worlds and random
streams, and no ground truth reaches the tracker. The held-out protocol was honoured: one run at
the `held-out-freeze` tag (`8baa778`, present on the remote), and the held-out JSON has not been
edited since.

What is wrong is mostly communication: the public demo says bias estimation helps in a scenario
where it does nothing (P1), and about ten documents still say the held-out run has not happened
(P2). Neither changes a number in `artifacts/`.

## 3. Readiness

| Dimension | Assessment |
|---|---|
| Technical correctness | Strong. Measurement models, EKF, gating, metrics verified. Open P3 timing contract defects in the tracker interface that the benchmark does not reach. |
| Architecture | Good module separation; `tracking/tracker.py` (775 lines) concentrates queueing, staleness, retrodiction, bias estimation and lifecycle. |
| Experimental validity | Strong design (paired seeds, dev/held-out split, TrackEval cross-check). Weakness: prose and demo captions are not generated from artifacts. |
| Tests and CI | 297 tests; CI green; two byte-exact SVG tests fail on a second Linux x86_64 environment. |
| Security | No secrets. Least-privilege, SHA-pinned CI with secret scan. docs-site npm deps outside Dependabot (1 critical, 3 high production advisories, low exploitability for a static site). |
| Product maturity | Clear research question and honest negative result; no named user beyond "reviewer". |
| Documentation | Thorough but stale in places (held-out, age of information, CI description, published audit page). |
| Visual quality | Best asset provenance of the three repos (JSON manifest per asset); README has no image; clip not feed-ready. |
| Portfolio readiness | High after #92 and #93: the negative result plus a clean held-out run is a strong story. |

## 4. Subsystem inventory

See appendix section (b). Implemented: synthetic world, two sensor models, CV EKF, per-group
Hungarian association, delivery queue with staleness and one-step retrodiction, scalar vision
bias estimator, metrics (RMSE, NEES/NIS, coverage, MOTA, IDF1, GOSPA, fragmentation, duplicates),
paired intervals, CLI, reporting, Streamlit app (dev seeds only), Astro/Starlight site on Pages.
Not implemented and not claimed: augmented-state bias (the estimator is a separate scalar filter),
M-of-N confirmation, HOTA/OSPA(T), cross-platform determinism job, real data.
Deliberately not planned: sensor-model edge cases S-F1 to S-F5 (#71, wontfix).

## 5. Strengths worth preserving

Appendix section (c). In short: paired design, ground-truth isolation test, TrackEval
cross-check, provenance and golden checks, a held-out split that was actually honoured, and an
asset pipeline whose manifests name their data sources.

## 6 to 10. Findings

All findings with evidence are in the appendix, section (e). Register:

| ID | Sev | Class | Finding | Issue |
|---|---|---|---|---|
| MP-01 | P1 | Confirmed defect | Demo beat 4 claims bias recovery in `measurement_bias`, where the plotted recovery is -0.2% / -0.1% | #92 |
| MP-02 | P2 | Confirmed defect | Held-out run exists; ~10 docs say it was not run; `HELD_OUT.md` says no code changed after it; held-out dir outside the provenance check | #93 |
| MP-03 | P3 | Confirmed defect | Two SVG byte tests fail off the generating platform (CI green) | #97 |
| MP-04 | P2 | Confirmed defect (docs) | Age-of-information definition and alignment bound disagree with code | #94 |
| MP-05 | P2 | Confirmed gap | Site publishes the historical audit as "current" | #94 |
| MP-06 | P3 | Confirmed defect | Off-grid captures older than one epoch admitted, contrary to docstring | #95 |
| MP-07 | P3 | Confirmed defect | README CI description stale | #94 |
| MP-08 | P3 | Confirmed defect | Repeated call time adds an epoch; evaluator then rejects the snapshot | #95 |
| MP-09 | P3 | Confirmed gap | Bias estimator overconfident under scaled covariance (RMS z 2.72 in `uncertainty_miscalibration`, 12 seeds) | not ticketed: document in `limitations.md` when #94 is done |
| MP-10 | P3 | Confirmed gap | docs-site npm outside Dependabot; production advisories | #96 |
| MP-11 | P3 | Confirmed defect | Delayed-initiation track stamped with processing time | #95 |
| MP-12 | P3 | Confirmed gap | Vendored agent skills without license notice | #96 |
| MP-13 | P3 | Confirmed defect | Personal absolute path in `docs/audit-report.md:20` (value redacted) | #94 |
| MP-14 | P3 | Likely issue | Provenance cannot detect generation from a dirty tree | fold into #93 if the check is touched |
| MP-15 | P3 | Confirmed gap | pre-commit ruff pin (v0.3.0) far behind the lock | #96 |
| MP-16 | P3 | Unverified | App limitations link may not resolve (not checked in a browser) | none |

Corrections by the lead review to the appendix: MP-02 says the `held-out-freeze` tag is not in the
clone; it exists on the remote (`git ls-remote --tags origin` shows `held-out-freeze^{}` at
`8baa778`). MP-03 was P2 in the appendix; CI run 67 is green at HEAD, so it is a portability
defect, P3.

## 11. Documentation inconsistencies

MP-02, MP-04, MP-05, MP-07 above.

## 12. Product and usability

The project answers its own question honestly: fusion improved position RMSE in 1 of 15
scenarios with defined accuracy and worsened it in 6 (dev seeds). That negative result is the
product. The Streamlit app shows all three methods on dev seeds only (verified). The intended user
is a reviewer or student of tracking; stating that explicitly would sharpen the README.

## 13. Visual and portfolio presentation

Existing: `docs-site/src/assets/generated/` (scenario clip, 47 s summary GIF at 640x620,
scoreboard, RMSE and recovery panels), each with a JSON manifest. Gaps: no image in README,
no MP4 or 9:16 cut, repository description and homepage empty. Workstream: #98.

## 14. Prioritised recommendations

1. #92 (P1, S). 2. #93 (P2, S to M). 3. #94 (P2, S). 4. #98 (P2, M, after #92 and #93).
5. #95 (P3, M). 6. #96 (P3, S). 7. #97 (P3, S).

Do not build: more scenarios or methods before the above; a second docs generator; a held-out
rerun.

## 15. Existing issue mapping

No issue was open before this audit. The 62 closed issues were checked against HEAD through the
historical-audit reconciliation (appendix section d). Closed but not fully reflected in docs:
#7 (held-out run done, docs not updated, now #93). Closed as wontfix and respected: #71.

## 16. New issues

Parent #91; children #92 to #98 (native sub-issues).

## 17. Dependency graph

```
#92 ──┐
#93 ──┴──> #98
#94, #95, #96, #97 independent
```

## 18. Quality gates

Before any public post of Mosaic results: #92 and #93 closed, CI green, provenance check covering
every artifact directory.

## 19. Unverified

Branch protection and required checks; upstream licence of vendored skills; app links in a
browser; which platform generated the committed SVGs.

## 20. Handoff

Start with #92 (tdd). Run `uv sync --locked --all-extras && uv run pytest` and
`make provenance-check benchmark-golden-check` before and after. Never run seeds 25 to 49.
Probes referenced in the appendix were throwaway scripts outside the repo and are not committed.

---

## Appendix: independent source audit (verbatim)

### mosaic-perception: independent source-level audit

- Repository: `mosaic-perception` (fresh clone)
- Commit audited: `8c13e9ae40bae8e8abd7ec5d6017a86610c2cce7` (HEAD, merge of PR #90). Working tree clean before and after (caches created by the runs were removed).
- Mode: read-only. No repository file was modified, nothing was committed, GitHub was not contacted. Probes live in this scratchpad (`(audit scratch) probes/`), not in the repo.
- Platform: Linux x86_64, uv 0.11.32, Node v22.23.4. Two locked environments: Python 3.12.3 (`/tmp/mp-venv312`, matches CI) and Python 3.13.18 (`/tmp/mp-venv`). numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2 (FreeType 2.14.3).
- Severity scale (same as the repo's own audit): P0 wrong headline number, P1 likely wrong conclusion, P2 claim/behaviour mismatch that can change a number or fail on valid input, P3 robustness or wording.

## (a) Check results

| Command | Result |
|---|---|
| `UV_PROJECT_ENVIRONMENT=/tmp/mp-venv312 uv sync --locked --all-extras --python 3.12` | OK (TrackEval installed from pinned git rev `12c8791b`) |
| `ruff check src tests scripts app` | `All checks passed!` (rc 0) |
| `ruff format --check src tests scripts app` | `62 files already formatted` (rc 0) |
| `mypy src` | `Success: no issues found in 21 source files` (rc 0) |
| `python -m pytest -q -p no:cacheprovider` (Python 3.12.3) | **2 failed, 295 passed in 33.14s** (297 collected) |
| same, Python 3.13.18 | **2 failed, 295 passed in 32.84s** |
| failing tests | `tests/unit/test_make_assets.py::test_committed_panel_data_matches_artifact[scoreboard]` and `[recovery]` (see MP-03) |
| `python scripts/check_artifact_provenance.py` | `provenance OK: artifact from d57356666b2f, package 0.1.0, source unchanged` |
| `python scripts/check_benchmark_golden.py` | `golden benchmark matches (benchmark.json, per_seed.csv, report.md)` |
| docs-site, clean export of HEAD into `/tmp/ds`: `npm ci` | OK, 513 packages (puppeteer 9.1.1 deprecation warning) |
| `npm run build` | OK, `12 page(s) built`, `All internal links are valid.` |
| `npm run a11y` (pa11y) | not run (needs a browser download) |
| `npm audit` (docs-site) | all deps: 17 (1 critical, 9 high, 4 moderate, 3 low); `--omit=dev`: 7 (1 critical `astro`, 3 high `sharp`/`zod`/`zod-to-ts`, 3 low) |
| Root `package.json` | Sandcastle agent tooling only, no tests or build |

The two failures are reproducible on both Python versions with the locked dependency set, so this is not a Python-version artefact. Whether CI is red at HEAD could not be checked (no GitHub access by instruction).

## (b) Subsystem inventory

| Subsystem | Files (lines) | Role |
|---|---|---|
| Domain contracts | `src/mosaic_perception/domain/models.py` (469) | pydantic models: `WorldState`, `SensorObservation` (capture vs delivery time, sensor-frame measurements, observer pose), `TrackEstimate`, `TrackSnapshot`, `ObservationStatistics`, `EvaluationResult` (about 80 fields) |
| World | `simulation/world.py` (198) | seeded CV targets, layouts, static or circling observer |
| Sensors | `sensors/range_bearing.py` (193), `sensors/vision_bearing.py` (170) | sensor-frame range, bearing, range rate; vision bearing plus detector class scores; bias, dropout, false alarms, delivery delay, reported-covariance scale |
| EKF | `tracking/ekf.py` (310) | CV model with DWNA process noise, analytic Jacobians, wrapped innovation, Joseph update, PSD guard, `predict_over` |
| Association | `tracking/association.py` (247) | per-group gated Hungarian (chi-square 95% gate by group and dimension) |
| Tracker | `tracking/tracker.py` (775) | pending queue, staleness, delivery-time vs one-step-lag retrodiction, sequential group updates, vision bias scalar KF, initiation, lifecycle (3 hits confirm, 2 misses coast, 5 delete), snapshots, counters |
| Runner | `experiment.py` (240) | three methods on shared worlds and per-sensor RNG streams; strips `_true_object_id` |
| Evaluation | `evaluation/frames.py` (156), `metrics.py` (546), `registry.py` (169), `statistics.py` (49) | continuity-first CLEAR-style matcher, RMSE, recall/precision, MOTA, IDF1, GOSPA, NEES/NIS, coverage, fragmentation, duplicates; paired t intervals |
| Reporting and CLI | `reporting/markdown.py` (326), `reporting/tables.py` (277), `cli/main.py` (465) | benchmark payload, CSV, report rendering |
| Scenarios | `scenarios.py` (325) | 16 presets |
| App | `app/streamlit_app.py` (83), `app/data_prep.py` (134) | three-method workbench, dev seeds 0-24 only |
| Asset pipeline | `scripts/make_assets.py`, `make_clips.py`, `make_summary_clip.py`, `sync_docs_site.py` | SVG panels, GIF clips, Starlight content sync |
| Integrity scripts | `scripts/check_artifact_provenance.py`, `scripts/check_benchmark_golden.py` | artifact commit/source/report checks; tolerant golden regeneration |
| Artifacts | `artifacts/benchmark/` (commit `d5735666`), `artifacts/benchmark-golden/`, `artifacts/held-out/` (commit `8baa778e`) | committed results |
| Docs site | `docs-site/` (Astro 5.18.2, Starlight 0.34.8), `.github/workflows/docs.yml` | GitHub Pages deploy from `main` |
| Agent tooling | `.agents/skills/` (38 skills), `skills-lock.json`, `.sandcastle/` | vendored third-party agent skills; autonomous issue/merge loop |

## (c) Verified strengths (executed, not only read)

- **Measurement Jacobians.** Central differences against `ekf.jacobian_range_bearing` and `ekf.jacobian_bearing` over 3000 random states and moving, rotated observers: max scaled error 9.15e-09 (range-bearing) and 6.53e-08 (bearing). Probe: `(audit scratch) probes/probe_math.py`.
- **Frames.** Sensor (`range_bearing.py:102-108`) and EKF (`ekf.py:169-177`) both compute bearing as world line-of-sight minus observer heading, and range rate against observer velocity. Jacobians correctly do not depend on heading.
- **Angle wrapping.** Innovation wraps the angle residual (`ekf.py:269-271`): prediction 3.1415, measurement -3.1217 gives residual 0.0200. Bias correction is applied with wrap in both gating (`association.py:152-153`) and update (`tracker.py:515-517`).
- **Covariance hygiene.** 3000 predict/update cycles: max asymmetry 0.0, min eigenvalue 2.98e-03, mean NIS 2.782 for 3 DOF (slightly below 3 because the truth has no process noise). Joseph form at `ekf.py:307-309`; PSD guard at `ekf.py:136-148`.
- **Gating DOF.** `association.py:51-55` keys gates by group and dimension (chi2 0.95 with 1, 2, 3 DOF) and raises on an unknown dimension; README:99-100 matches.
- **Fair pairing.** World generated once per seed (`experiment.py:206-213`); range sensors seeded `seed + 1000 + index` and vision `seed + 2000 + index` over the full sensor list (`experiment.py:93-108`), so the range stream is identical for all three methods and vision identical for both fused methods. Seeds 0-49 cannot collide with sensor seeds. Tracker parameters identical except `use_vision` and `bias_estimation` (`experiment.py:138-143`). The configured bias reaches only the result record (`experiment.py:174-182`).
- **Ground-truth isolation.** `grep` over `tracking/` finds no use of `_true_object_id`, `true_class`, `WorldState` or `ObjectState`; the runner nulls `_true_object_id` before `process_observations` (`experiment.py:157-160`). Perfect observer pose is a documented assumption (`docs/limitations.md:188-192`).
- **Metrics.** GOSPA alpha 2 with cutoff assignment (`metrics.py:255-279`), IDF1 by global co-occurrence (`metrics.py:215-252`), MOTA with IDSW across gaps as in TrackEval (`metrics.py:146-200`), NEES/coverage reject non-PSD blocks and count skips (`metrics.py:91-117`, `:293-319`), pooled per-DOF chi-square intervals (`registry.py:50-66`, `:139-143`). The continuity-first matcher now follows TrackEval (`frames.py:50-52`, `:116-130`).
- **Provenance.** `benchmark.json` records commit, package, numpy and scipy versions; provenance check also re-renders `report.md` and compares it (`check_artifact_provenance.py:43-60`); golden check passes with field-wise tolerance.
- **Fail-loud evaluation.** Duplicate `(track, time)` snapshots and stray snapshot times now raise (`frames.py:44-45`, `:69-72`).
- **CI hygiene.** `permissions: contents: read` at workflow level, every action pinned to a 40-hex SHA, no `pull_request_target`, deploy job is the only one with `pages: write` and `id-token: write` and is gated to `main` (`docs.yml:44-50`). Dependabot for uv and actions, advisory pip-audit, pinned and checksum-verified gitleaks. No `pickle`, `yaml.load`, `eval`, `exec` or `shell=True` in tracked code. No secret pattern matched.
- **App.** Runs all three methods via the shared runner (`app/streamlit_app.py:55`), default seed 1, slider capped at 24 (`app/data_prep.py:17-18`).

## (d) Historical audit reconciliation (`docs/audits/mosaic-perception-comprehensive-audit.md`, audited at `d3e88d9`)

| Finding | Status at HEAD | Evidence |
|---|---|---|
| R-F2 / D-F1 stale `report.md`, README bias numbers | Fixed | `41db690`, `68960de`, `7845140`; provenance check re-renders report and passes; README:205-213 now quotes 0.0101/0.0149/0.0199, 0.073/0.113/0.192, "about 1.3 updates" |
| E-F1 matcher not TrackEval-like | Fixed | `029b9b5`; `frames.py:50-52,116-130` continuity bonus outranks match count |
| A-F1 retrodiction drops same-time updates | Fixed | `3bd50f6`; `tracker.py:165-167`; probe: trace(P) 1.4789 to 1.0676 in retrodiction (was rising) |
| A-F4 unknown class raises after update | Fixed | `83ac125`; `tracker.py:208-211`; probe logs `unknown class names ['bogus']`, no exception |
| R-F3 provenance reads only JSON | Partly fixed | report commit and render now checked (`check_artifact_provenance.py:16-18,100-105`); `per_seed.csv` and `artifacts/held-out/` still unchecked (MP-02) |
| D-F2 "CI on every push" | Fixed | README:23,42 say "every push to `main` and every pull request to `main`" |
| D-F3 seed 42 default | Fixed | `3d3837f`; `app/data_prep.py:17-18`, README:60 seed 1 |
| D-F4 core-validity-audit stale facts | Fixed | `core-validity-audit.md:3-6` historical banner, `:56` "10 presets at the time (16 now)", `:58` "Later superseded" |
| D-F5, D-F6 coverage range, "every scenario", "often lower", "two scenarios" | Fixed | `limitations.md:153` "four", `:174-179` 0.089/0.106/0.091 and "14 of the 15"; `demo-walkthrough.md:67-70` "better in 1 of 15 and worse in 6" |
| R-F1 / D-F12 golden byte-exact | Fixed (by #49) | `evaluation-protocol.md:104-112`; check passes here. README wording still says byte-for-byte (MP-07) |
| R-F10 no dependency monitoring | Fixed for Python and actions | `03f6ba1`; `.github/dependabot.yml:4,12`; `ci.yml` `dependency-audit`. npm not covered (MP-10) |
| R-F9 branch protection | Unverified | no GitHub access |
| D-F7 retrodiction "improves accuracy" | Fixed | README:215-222 now range-only only, fused "slightly worse" |
| S-F1 range floor before bias | Open, documented | probe: true 0.2 m + bias 0.3 gives mean 0.653, 41% at floor+bias; `range_bearing.py:110-111`; disclosed `measurement-models.md:31-34` |
| S-F2 frame-rate tick quantisation | Open, documented | probe: 30 Hz on 100 Hz ticks emits 75 frames in 3 s; `range_bearing.py:40-49`; disclosed `measurement-models.md:34-37` |
| S-F3 1e-6 vs 1e-9 thresholds | Open (unchanged) | `range_bearing.py:99`, `ekf.py:172` |
| S-F5 `wrap_angle` edges | Open | probe: `wrap_angle(3*pi)=3.1415926535897927`, `wrap_angle(nan)=nan` |
| S-F6 docs omit floor/skip/quantisation | Fixed | `measurement-models.md:31-37` |
| A-F2 repeated time adds an epoch | Open, now worse (evaluator raises) | MP-08 |
| A-F3 age uses processing time | Fixed in code; docs half-updated | `2dcf237`, `tracker.py:189`; probe ages 0.01 and 0 stale rejections; `metrics.md:178` still states the old definition (MP-04) |
| A-F5 duplicate id mid-batch raises | Fixed | `tracker.py:447-454`; probe: rejected as invalid, no exception |
| A-F6 dropped vision in range-only moves no counter | Open by design | `tracker.py:444-446` |
| E-F2 docs contradict on per-timestamp independence | Fixed | `metrics.md:27-29` |
| E-F3 garbled Findings sentence | Fixed | `b286320` |
| E-F4 shared baseline and multiplicity unstated | Fixed | `markdown.py:251-263`; `limitations.md:165-171` |
| E-F5 silent snapshot drop / overwrite | Fixed (now raises) | `frames.py:44-45,69-72` |
| R-F4 held-out by convention | Open by design | held-out has since been run; see MP-02 |
| R-F6 unpinned `>=`, versions not recorded | Partly fixed | numpy/scipy recorded (`e5100a7`, `benchmark.json` `code`); `pyproject.toml` still `>=`, CI matrix 3.12 only |
| R-F7 CI lints only `src tests` | Fixed | `d573566`; `ci.yml:33,35` include `scripts app` |
| D-F8 "10 named presets" | Fixed | `architecture.md:38` "16 named presets" |
| D-F9 fragmentation wording | Fixed in `metrics.md:66`; evaluator note still says "frames where" (`metrics.py:504-507`), minor |
| D-F10 roadmap/release-checklist stale | Fixed | `roadmap.md:3,23,40`; `release-checklist.md:5` |
| D-F11 CI never calls `make` | Open (wording) | README:23 still says CI "verifies ... with `make provenance-check benchmark-golden-check`"; CI calls the scripts directly |
| D-F13 `mosaic run` two methods undocumented | Fixed | README:63-64 |
| H-1 bias estimator overconfident with scaled covariance | Confirmed in the real tracker | MP-09 |
| H-2 delayed initiation stamped `now` | Confirmed, open | MP-11 |
| H-3 continuity tie-break effect | Obsolete | E-F1 fixed and artifacts regenerated (`8ce0d42`) |
| H-4 indefinite covariance accepted | Fixed | `1bcde4b`; `metrics.py:91-102` |
| H-5 zero-width interval read as excluding zero | Fixed (flagged) | `markdown.py:21-22,58,150` |
| H-6 perfect observer pose undocumented | Fixed (documented) | `limitations.md:188-192` |
| H-7 gitleaks same-origin checksum, unpinned uv | Partly fixed | uv pinned `0.13.6` in `ci.yml`; checksum still fetched from the same release |
| H-8 "preregistered" values | Unverifiable from repo | unchanged |
| H-9 required status checks | Unverified | no GitHub access |
| U-1 dependency monitoring | Implemented | see R-F10 |
| U-2 held-out guard in code | Open | `cli/main.py` only labels `seed_group` `custom_or_held_out` |
| U-3 M-of-N confirmation | Open | `tracker.py:743` counts total hits |
| U-4 initiation gating / merging | Open by design | `tracker.py:253-258` initiates from every unmatched range observation |
| U-5 reference cross-checks beyond CLEAR/ID | Open | `implementation-status.md:112-115` |
| U-6 HOTA, MT/ML, OSPA(T) | Open, not claimed | none |
| U-7 cross-platform determinism job | Open | MP-03 is a live example |
| U-8 held-out run (#7), docs site (#34) | Both done | `artifacts/held-out/`, `docs.yml`; docs not updated for #7 (MP-02) |

## (e) Findings

### MP-01. Published demo says bias estimation helps in `measurement_bias`; the plotted data shows it does nothing
- Classification: Confirmed defect. Severity: **P1** (the public demo leads a viewer to a wrong conclusion). Confidence: high.
- Evidence:
  - `scripts/make_assets.py:44`: `RECOVERY_SCENARIO = "measurement_bias"`.
  - `src/mosaic_perception/scenarios.py:113-121`: `measurement_bias` is `"Constant range bias of +1.5 m and range-rate bias of +0.3 m/s."` with `range_overrides={"bias": {"range": 1.5, "range_rate": 0.3}}`. The vision sensor is unbiased, and the bias estimator assumes an unbiased range sensor (`tracker.py:316-319`), so it has nothing correct to learn.
  - `docs/demos.md:41`: `"4. The one scenario where it helps: a miscalibrated sensor (measurement bias), where the bias-estimated method recovers part of the loss."`
  - Landing-page alt text `docs-site/src/content/docs/index.mdx:23`: "Four: in the one scenario with a miscalibrated sensor, estimating the bias recovers part of fusion's loss."
  - The committed panel text (`docs-site/src/assets/generated/measurement_bias_recovery.svg`): "recovered -0.2% of fused's loss" (precision 0.715/0.599/0.598) and "recovered -0.1% of fused's loss" (MOTA 0.494/0.255/0.255).
  - `benchmark.json`, `measurement_bias`, `bias_estimated_vs_fused`: precision mean -0.000178, 95% CI [-0.01278, 0.01242]; MOTA mean -0.000264, CI [-0.0346, 0.0341]; mean bias estimate 8.1e-05.
  - By contrast `sensor_disagreement_within_gate`: precision +0.110 [0.076, 0.145], MOTA +0.297 [0.215, 0.378].
  - "Miscalibrated sensor" is also the name of a different preset (`uncertainty_miscalibration`, covariance scale), so the caption conflates two scenarios.
- Observed vs expected: the caption and alt text claim recovery; the data in the same frame shows none. Expected: beat 4 uses a within-gate vision-bias scenario (where README:201-211 documents recovery), or the caption says that estimation does not help under a range bias.
- Reproduction: `uv run python -c "import sys; sys.path.insert(0,'scripts'); import make_assets as ma, json; print(json.dumps(ma.load_recovery_data(ma.BENCHMARK), indent=1))"`.
- Recommended fix: set `RECOVERY_SCENARIO = "sensor_disagreement_within_gate"` (or one of the three), regenerate panels and clip, rewrite beat 4 and the alt text, and add a test that the recovery scenario's `recovered_share` is positive with an interval excluding zero before the caption may say "recovers".
- Acceptance: panel, clip, `demos.md:41` and alt text name the same scenario; the test fails if the plotted share is not positive.

### MP-02. Held-out seeds 25-49 were run, but ten documents say they were not; the held-out artifact no longer reproduces at HEAD
- Classification: Confirmed defect. Severity: **P2**. Confidence: high.
- Evidence:
  - `artifacts/held-out/` (commit `0907c92`, "add the single held-out run, seeds 25-49 (#7)") holds `benchmark.json`, `report.md`, `HELD_OUT.md`.
  - Contradicting statements at HEAD: `README.md:9` "The reserved held-out range 25-49 has not been run"; `README.md:141-142`; `README.md:271`; `docs/evaluation-protocol.md:24-25` "They have **not** been run"; `docs/limitations.md:128-130`; `docs/design-decisions.md:49-51`; `docs/demo-walkthrough.md:84-85`; `docs/demo-script.md:55-56`; `docs/implementation-status.md:119` "Planned: run the held-out evaluation once on frozen code" and `:203` lists #7 as planned; `docs/roadmap.md:45` unchecked. Only `docs/demos.md:24,75` acknowledge the run.
  - `artifacts/held-out/HELD_OUT.md:5-6`: "The code was merged and frozen before the run; no code or scenario change followed it." But `git diff --stat 8baa778 HEAD -- src` touches `tracking/tracker.py` (`2dcf237`, age redefined as delivery latency), `evaluation/registry.py`, `reporting/markdown.py`.
  - Probe `(audit scratch) probes/probe_heldout.py` (seed 25): `delivery_delay` `mean_age_of_information` is 0.0996 (range_only) in the artifact vs 0.0508 at HEAD; 0.0998 vs 0.0520 (fused). RMSE agrees to 1e-15.
  - The provenance check only reads `artifacts/benchmark/` (`check_artifact_provenance.py:34-36`). `per_seed.csv` for the held-out run is not committed because `.gitignore:32-34` ignores `*.csv` except the two benchmark files.
  - The `held-out-freeze` tag cited in `HELD_OUT.md:5` is not in this clone (`git tag -l` empty); unverified on the remote.
- Observed vs expected: first-screen README says no held-out run exists; it does, and it describes code that has since changed. Expected: one consistent statement of the held-out status, and an artifact either tied to its frozen commit explicitly or regenerated.
- Reproduction: `ls artifacts/held-out; grep -rn "not been run\|were not run" README.md docs/*.md; git diff --stat 8baa778 HEAD -- src`.
- Recommended fix: maintainer decision on wording; update the ten locations to say "run once at `8baa778`, consistent with development, inconclusive"; reword `HELD_OUT.md` to "no change was made in response to the results" and list later src commits; extend the provenance check to every artifact directory with an explicit "frozen at" allowance; un-ignore `artifacts/held-out/per_seed.csv`.
- Acceptance: `grep -rn "has not been run" README.md docs` is empty or qualified; provenance check reports held-out commit and the src delta since it.

### MP-03. The test suite fails on a clean x86_64 Linux checkout: byte-exact SVG panel test is platform-dependent
- Classification: Confirmed defect. Severity: **P2** (`uv run pytest`, the second "reproduce" command at README:19, fails). Confidence: high on the failure; CI status unverified.
- Evidence:
  - `tests/unit/test_make_assets.py:92-100`: `assert path.read_bytes() == render(load(ma.BENCHMARK))`. The embedded `<desc>` JSON check on the line before passes, so the data is current.
  - Only geometry differs: committed `scoreboard.svg` has `x="185.38"` where HEAD renders `x="181.83625"`; all 30 `<text>` strings are identical. 298 changed lines in `scoreboard.svg`, 224 in `measurement_bias_recovery.svg`.
  - Rendering with the script as of `cb985e0`, `9ec1a66` and `8a5656f` all mismatch, so it is not a code change. Forcing matplotlib's bundled DejaVu (system fonts removed from the font list) still mismatches. Fails on Python 3.12.3 and 3.13.18 with the locked matplotlib 3.11.2.
  - `scripts/make_assets.py:9`: "The output is byte-deterministic: bundled font, ...". `position_rmse_paired.svg` does match, so the generating platform differs for the two newer panels.
  - `.sandcastle/merge-prompt.md:18`: "Do not run the full pytest suite. CI runs it on `main` after the push." so the agent merger cannot catch this before merge.
- Observed vs expected: 2 failed, 295 passed. Expected: green suite on Linux x86_64 with the lock.
- Reproduction: `uv sync --locked --all-extras && uv run pytest tests/unit/test_make_assets.py -q`.
- Recommended fix: compare structure (desc JSON plus text content plus element count) instead of bytes, or regenerate in CI's environment and document that SVG bytes are platform-specific; record the generating platform in the SVG metadata.
- Acceptance: suite green on ubuntu x86_64 and on the maintainer's platform from the same committed SVGs.

### MP-04. Age-of-information definition in `metrics.md` contradicts the code, and the alignment-error bound uses the wrong interval
- Classification: Confirmed defect (docs). Severity: **P2** (the reported number reads about half of what the doc says in `delivery_delay`). Confidence: high.
- Evidence:
  - Code: `tracker.py:189` `age = observation.delivery_time - observation.capture_time` (since `2dcf237`).
  - `docs/metrics.md:178`: "`mean_age_of_information` | mean of `processing_time - capture_time` ...".
  - `README.md:128`: "**Age of information**: mean processing age of observations".
  - `docs/measurement-models.md:107-112` correctly says delivery latency, so docs disagree with each other.
  - Alignment bound: `measurement-models.md:103-104` "displacement between capture and delivery is approximately `speed x observation_age`" and `README.md:267-268` "approximation of scale ~speed x age". The delivery-time update is applied to the state at processing time (`tracker.py:412-427`, then `:571-573`), so the misalignment interval is processing minus capture. In the runner, captures are on ticks and delivery in (capture, capture+dt], so the interval is always one dt (0.1 s) while the reported age in `delivery_delay` is about 0.05 s (probe: 0.0508).
- Observed vs expected: docs describe a quantity that is no longer reported and understate the alignment error by about 2x.
- Reproduction: `(audit scratch) probes/probe_tracker.py` (A-F3 lines: capture 0.0, delivery 0.01, processed 0.1 reports 0.01).
- Recommended fix: fix `metrics.md:178` and README:128 to "delivery latency"; state the alignment bound as `speed x (processing_time - capture_time)`, at most one tick after delivery.
- Acceptance: the three documents agree with `tracker.py:189`.

### MP-05. The published "Audit" page is a stale defect list presented as current
- Classification: Confirmed gap. Severity: **P2**. Confidence: high.
- Evidence: `scripts/sync_docs_site.py:28` publishes `docs/audits/mosaic-perception-comprehensive-audit.md` as the site's "Audit" page (`astro.config.mjs` sidebar). The file opens "The current, evidence-backed audit of this repository" (`:3`) and is pinned to `d3e88d9`. `git log -- docs/audits/` shows one commit (`4b73edf`); about 20 fix commits followed (section d), so most listed defects are fixed.
- Observed vs expected: a reader of the public site sees fixed defects as open. Expected: a status column or banner, as `core-validity-audit.md:3-6` has.
- Reproduction: `git log --oneline -- docs/audits/; git log --oneline 4b73edf..HEAD -- src docs | wc -l`.
- Recommended fix: add a "Status at <commit>" column (table (d) above can seed it) and a historical banner, or publish a short current status page instead.
- Acceptance: each finding row states fixed/open with a commit.

### MP-06. Off-grid observations older than one epoch are admitted, contrary to the tracker docstring
- Classification: Confirmed defect (API contract). Severity: **P3** (the runner always captures on ticks, so the benchmark does not reach it). Confidence: high.
- Evidence: `tracker.py:6-9` "An observation whose capture time is at most one tracker epoch (``dt``) in the past may be applied". The rule is now on latency (`tracker.py:189-190`). Probe: capture 0.05, delivery 0.149, processed 0.2 (0.15 s old) gives `stale=0 delivered=2`. In retrodiction, `_replay_epoch` clamps the gap to zero (`tracker.py:607-610`), so the measurement is applied at 0.1, not 0.05.
- Recommended fix: either reject when `now - capture_time > dt + eps`, or reword the docstring and `limitations.md:72-75` to the latency rule plus "applied at most one tick after delivery".
- Acceptance: a test pins whichever rule is chosen.

### MP-07. README CI description is stale
- Classification: Confirmed defect (wording). Severity: **P3**. Confidence: high.
- Evidence: `README.md:42-44` "Ruff lint (`src tests`) and format check (full tree) ... byte-level artifact provenance and golden-benchmark checks". CI lints and format-checks `src tests scripts app` (`ci.yml:33,35`), not the full tree. `README.md:23` "comparing it byte-for-byte with the committed golden files", but JSON and CSV are compared with rtol 1e-9 (`evaluation-protocol.md:104-112`); only `report.md` is byte-compared. README:23 also says CI uses `make provenance-check benchmark-golden-check`; CI runs the scripts.
- Recommended fix: reword both paragraphs from `ci.yml`.
- Acceptance: README matches `ci.yml` and `evaluation-protocol.md`.

### MP-08. A repeated call time runs a second epoch and emits a duplicate snapshot that the evaluator then rejects (historical A-F2)
- Classification: Confirmed defect. Severity: **P3** (runner never repeats a time). Confidence: high.
- Evidence: `tracker.py:165-167` keeps `_epoch_applied` for a repeated time (the A-F1 fix treats it as the same epoch), but `_finish_epoch` still runs and `self.epoch += 1` (`tracker.py:260-262`). Probe: after calls at 0.0, 0.1, 0.1: `hits=3 age=3 epoch=3`, 2 snapshots at t=0.1. `frames.py:44-45` then raises `duplicate snapshot for track ... at time 0.1`.
- Observed vs expected: the API accepts a repeated time (docstring: "monotonically non-decreasing", `tracker.py:154-155`) but the output cannot be evaluated. Expected: a repeated time either merges into the epoch (replace the snapshot, no extra hit/age) or is rejected.
- Reproduction: `(audit scratch) probes/probe_tracker.py`, first block, then pass `tr.snapshots` to `TrackingEvaluator().evaluate`.
- Recommended fix: treat `now == last_time` as a continuation: skip hit/miss/age accounting for tracks already counted, replace snapshots. Or require strictly increasing time.
- Acceptance: test with a repeated time evaluates without error and with the same hits as one combined call.

### MP-09. Vision bias estimator ignores its own uncertainty in the track update and is overconfident when reported covariance is scaled (historical H-1, now confirmed)
- Classification: Confirmed gap. Severity: **P3**. Confidence: high on the measurement, medium on impact.
- Evidence: the bias is a separate scalar filter (`tracker.py:309-350`), not an augmented state. The corrected vision bearing updates the track with the reported `R` only (`tracker.py:514-519`, `:539-547`); `_bias_var` (prior 0.05^2, `tracker.py:39`) is never added, and no track-bias cross-covariance is kept, although the same vision observation updates both (`tracker.py:577-581`). The bias measurement variance is the reported `R_vision + R_range` (`tracker.py:346`). Probe `(audit scratch) probes/probe_bias.py`, 12 seeds, 10 s, final `(estimate - configured)/sqrt(var)`: RMS z 1.02 (`nominal`), 1.21 (`sensor_disagreement_within_gate`), **2.72** (`uncertainty_miscalibration`, max |z| 5.27). The gate also truncates the innovations that reach the estimator, a selection effect not discussed. Not documented in `limitations.md:48-68`.
- Recommended fix: document; optionally inflate the vision `R` by `_bias_var` in gating and update (Schmidt-style consider term), and report bias z-score.
- Acceptance: limitations entry; if implemented, early-epoch vision NIS stays within its interval in the within-gate scenarios.

### MP-10. docs-site npm dependencies are outside Dependabot and carry production advisories
- Classification: Confirmed gap. Severity: **P3** (static build from author-controlled content; the reported Astro issues concern `define:vars` and server islands). Confidence: high on the facts, low on exploitability.
- Evidence: `.github/dependabot.yml:4,12` cover only `uv` and `github-actions`. `npm audit --omit=dev` in `docs-site`: 7 (critical `astro` 5.18.2, "range <=7.3.1"; high `sharp`, `zod`, `zod-to-ts`; low `@astrojs/mdx`, `@astrojs/starlight`, `esbuild`). Dev: `pa11y-ci` 3.1.0 pulls deprecated `puppeteer` 9.1.1. Root `package.json` (Sandcastle) is also uncovered.
- Recommended fix: add `npm` ecosystems for `/docs-site` and `/`; add `npm audit --omit=dev` as an advisory step in `docs.yml`.
- Acceptance: Dependabot opens npm PRs; audit step present.

### MP-11. Track initiated from a delayed observation keeps the capture-time position but is stamped with the processing time (historical H-2)
- Classification: Confirmed defect. Severity: **P3** (bounded by one epoch). Confidence: high.
- Evidence: `tracker.py:636-639` position from capture-time geometry; `:682-684` `time=now`. Probe: capture 0.0, processed 0.1, range rate 5: `time=0.1 x=10.000 vx=5.000` (expected about 10.5 at 0.1).
- Recommended fix: initiate then `predict_over(now - capture_time)`.
- Acceptance: test shows the initiated position equals capture position plus velocity times age.

### MP-12. Vendored third-party agent skills have no license notice
- Classification: Confirmed gap. Severity: **P3**. Confidence: high on absence; upstream license unverified.
- Evidence: 38 skills under `.agents/skills/`; `skills-lock.json` lists every one as `"source": "mattpocock/skills"` with a content hash but no commit. `git grep -iE "MIT License|SPDX|copyright" -- .agents` finds nothing; README, LICENSE and CLAUDE.md do not mention them. The repo `LICENSE` is MIT for Telschow, which a reader may assume covers the vendored text. `.agents/skills/pr/CREDITS.md` credits text "reproduced almost word for word" from `humanlayer/humanlayer` without a license line. Several skills are unrelated to this project (for example `migrate-to-shoehorn`, `setup-ts-deep-modules`, `wizard`).
- Recommended fix: add `.agents/skills/LICENSE` or `THIRD_PARTY_NOTICES` with upstream license texts and pinned commits; record the upstream commit in `skills-lock.json`; drop unused skills.
- Acceptance: each vendored source has a license file and a commit.

### MP-13. Personal absolute path in a committed doc
- Classification: Confirmed defect. Severity: **P3**. Confidence: high.
- Evidence: `docs/audit-report.md:20` `**Repository:** /Users/<user>/Development/mosaic-perception` (user name redacted here). It is published via GitHub, not the docs site.
- Recommended fix: replace with the repo name.

### MP-14. Provenance cannot detect an artifact generated from a dirty tree
- Classification: Likely issue. Severity: **P3**. Confidence: medium.
- Evidence: `experiment.py:72-85` records `git rev-parse HEAD` only, no dirty flag. `check_artifact_provenance.py:7-8` claims the check shows the artifact was not generated "from an uncommitted tree". If `src/` edits were present at generation and then discarded, the recorded commit and `src/` diff are clean and the check passes; only the small golden configuration would notice.
- Recommended fix: record `git status --porcelain -- src` (or a hash of `src/`) in `benchmark.json` and refuse a dirty value in the check.
- Acceptance: a test that generates with a modified `src` file and expects the check to fail.

### MP-15. Pre-commit hooks pin tools far behind the lock
- Classification: Confirmed defect. Severity: **P3**. Confidence: high.
- Evidence: `.pre-commit-config.yaml:3` `rev: v0.3.0` (ruff), `:10` `rev: v1.8.0` (mypy); `uv.lock:2082-2083` ruff `0.17.3`. Local hooks can format or lint differently from CI.
- Recommended fix: use local hooks that run `uv run ruff` and `uv run mypy`, or bump revs and let Dependabot track `pre-commit`.

### MP-16. App limitations link is relative and will not resolve in Streamlit
- Classification: Unverified (not opened in a browser). Severity: **P3**. Confidence: medium.
- Evidence: `app/streamlit_app.py:81` `[`docs/limitations.md`](docs/limitations.md)`; Streamlit serves no repo files at that path.
- Recommended fix: link to the GitHub blob or the docs-site URL.

### Not defects (checked)
- Association uses a 1e12 sentinel for out-of-gate pairs (`association.py:225`), which maximises gated matches then minimises cost. This is standard GNN behaviour and documented.
- Range-only runs never see vision (`tracker.py:444-446`); vision cannot initiate tracks; per-group one-to-one assignment matches README:93-109.
- The `Sixty-second summary` is 46.8 s (`summary_clip.json:12`); the acceptance is "under 60 s" (`demos.md:46`).

## (f) Architecture candidates

1. **Strong: a "claims" module between artifacts and prose.** Hot spots in the last 100 commits: `docs/limitations.md` 25 changes, `README.md` 21, `docs/metrics.md` 19, `docs/technical-walkthrough.md` 13, `docs/demo-script.md` 10. Most fix commits since the audit are hand edits of numbers and status sentences (R-F2, D-F5, D-F6, D-F7, and now MP-01, MP-02, MP-04). Today every document is a shallow consumer that re-types facts from `benchmark.json`. A deep module (`reporting/claims.py`) with a small interface (named facts such as `held_out_status`, `recovery_scenario`, tallies, quoted values) and markers rendered into Markdown, plus one check in CI, gives locality (a fact changes in one place) and leverage (all pages, the clip captions and the alt text read the same seam). `contested-nav` already uses this pattern (`scripts/metrics.py` markers plus `tests/test_quoted_numbers.py`).
2. **Worth exploring: an artifact-set module owning write and verify.** `cli/main.py` (22 changes) builds the payload, CSV and report inline in `_run_experiment` (`cli/main.py:222-332`), while verification lives in two scripts that know only `artifacts/benchmark/` and `artifacts/benchmark-golden/`. The held-out directory has no adapter at all (MP-02) and `per_seed.csv` is outside every check. One module with `write(runs) -> ArtifactSet` and `verify(path) -> Report`, applied to every artifact directory and recording platform and dirty state, would close MP-02 and MP-14 at one seam and make the CLI a thin adapter.
3. **Worth exploring: an epoch/delivery policy module inside the tracker.** `MultiSensorTracker` (775 lines) mixes queueing, staleness, retrodiction replay, bias estimation, initiation, lifecycle and twelve counters. A-F1, A-F2, A-F3, H-2 and MP-06 are all time-handling defects in the same class. Extracting a `DeliveryPolicy` (interface: `admit(observations, now) -> EpochBatch` with explicit capture, delivery and processing times) and a `BiasEstimator` adapter would let each be tested on its own and make MP-08 and MP-09 local fixes.
4. **Speculative: structural asset comparison.** Byte equality of matplotlib output across platforms (MP-03) is a brittle seam. A small SVG normaliser (data, text, element count) as the comparison interface would keep the drift check while dropping platform coupling.

## (g) Open questions

1. Is CI green at `8c13e9a`? If the SVG test fails on `ubuntu-latest`, `main` is red; if it passes, which platform generated the panels and why does it differ from x86_64 Linux with the same lock?
2. Maintainer decision: is `artifacts/held-out/` the canonical held-out result for `8baa778`, to be cited as such, or must it be rerun after the tracker change? Does the `held-out-freeze` tag exist on the remote?
3. Are `test`, `secret-scan` and `artifact-checks` required status checks on `main` (H-9)?
4. What license does `mattpocock/skills` (and the reproduced `humanlayer` text) carry, and at which commit were the 38 skills vendored?
5. Should the bias estimator remain a decoupled scalar filter (documented approximation) or become a consider/augmented state?
6. Should the tracker API reject off-grid captures older than one epoch (MP-06) or document the latency rule?

## Probe files (scratchpad, not in the repo)

- `(audit scratch) probes/probe_math.py`
- `(audit scratch) probes/probe_tracker.py`
- `(audit scratch) probes/probe_bias.py`
- `(audit scratch) probes/probe_heldout.py`
- logs: `pytest312.txt`, `pytest.txt`, `ruff.txt`, `fmt.txt`, `mypy.txt` in the same `audit/` folder
