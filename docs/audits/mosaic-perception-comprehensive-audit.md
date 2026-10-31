# Mosaic Perception: Comprehensive Audit

The current, evidence-backed audit of this repository. It is assembled from five
source-level research findings (issues #38 to #42) under map #36. No defect is
fixed here and no benchmark artifact was regenerated. Fix tickets are a
separate step (#46).

## Pinned commit and scope

- **Audited commit:** `d3e88d9832095b380a3f38d7a7b9d3947461d8c5` (`main` after
  PR #35). All five research reports were written against this commit, and every
  file:line below refers to it.
- **Assembled at:** `356d032` plus the `c361998` Sandcastle chore commit. Since
  `d3e88d9` the following changed: `scripts/check_benchmark_golden.py`,
  `tests/unit/test_check_benchmark_golden.py`, `docs/evaluation-protocol.md`
  (#49, golden check made platform-tolerant) and `.sandcastle/`, `package*.json`.
  `git diff d3e88d9 HEAD --stat -- src artifacts pyproject.toml uv.lock` is empty,
  so no source, artifact or dependency finding is affected. Where a finding is
  affected by #49, it says so.
- **Evidence standard:** every finding has file:line, a reproduction, observed vs
  expected, confidence and severity. Severity: P0 wrong headline number, P1
  likely wrong conclusion, P2 claim/behaviour mismatch that can change a number
  or fail on valid input, P3 robustness or wording. Confidence is copied from the
  research report; "not stated" means that report gave none, and no value has
  been invented.

## Research sources

| Ticket | Area | Findings file | Branch | Commit |
|---|---|---|---|---|
| #38 | Sensors and EKF mathematics | `docs/research/sensor-ekf-math.md` (plus four probe scripts) | [`research/sensor-ekf-math`](https://github.com/Telschow/mosaic-perception/tree/research/sensor-ekf-math) | `eb941cc` |
| #39 | Association, timing, lifecycle | `docs/research/association-timing.md` | [`research/association-timing`](https://github.com/Telschow/mosaic-perception/tree/research/association-timing) | `9ff9641` |
| #40 | Evaluator, metrics, statistics | `docs/research/evaluator-metrics.md` | [`research/evaluator-metrics`](https://github.com/Telschow/mosaic-perception/tree/research/evaluator-metrics) | `b3c165d` |
| #41 | Reproducibility, CI, security | `docs/research/repro-ci-security.md` | [`research/repro-ci-security`](https://github.com/Telschow/mosaic-perception/tree/research/repro-ci-security) | `b07393a` |
| #42 | Documentation and claims | `research/docs-claims.md` | [`research/docs-claims`](https://github.com/Telschow/mosaic-perception/tree/research/docs-claims) | `876578c` |

Parent map: #36. Downstream: #46 (disposition into backlog), #47 (demonstrations).
Related open issues: #7 (held-out evaluation), #34 (docs site), #44 (dependency
monitoring). Finding IDs below are `<area>-F<n>`, using the area letters S, A, E,
R, D and the numbering of the source report, so each can be looked up there.

## Summary

| ID | Sev | Kind | One line |
|---|---|---|---|
| R-F2 / D-F1 | P1 | Defect | `artifacts/benchmark/report.md` is stale against `benchmark.json`; README and walkthrough quote it |
| E-F1 | P2 | Defect | Continuity matcher maximises match count first; documented as TrackEval CLEAR |
| A-F1 | P2 | Defect | Retrodiction drops earlier updates on a repeated `current_time` |
| A-F4 | P2 | Defect | Unknown class name in `class_probs` raises after the state update |
| R-F3 | P2 | Defect | Provenance check reads only `benchmark.json` |
| D-F2 | P2 | Defect | "CI on every push" is wrong |
| D-F3 | P2 | Defect | Reserved held-out seed 42 is the default in README, demo and app |
| D-F4 | P2 | Defect | `core-validity-audit.md` V10 still says fragmentation is unsupported |
| D-F5, D-F6 | P2 | Defect | Wrong coverage range, "every scenario" precision and "often lower" RMSE wording |
| R-F1 / D-F12 | P2 | Defect, resolved at HEAD by #49 | Golden check was byte-exact on floats |
| R-F10 | P2 | Unimplemented | No dependency-vulnerability monitoring |
| R-F9 | P2 | Hypothesis | Branch protection on the CI jobs could not be checked |

No P0 finding was reported. The verified-correct list (next section) is as
important as the defects: the core maths, GOSPA, paired intervals and
ground-truth isolation held up.

## Verified correct

These were executed or recomputed, not only read.

- **Sensor and EKF maths (#38).**
  - Range, bearing and range-rate equations match `docs/measurement-models.md`.
    The sensor and the EKF agree to 1e-8 with noise off, a moving observer and
    heading 2.9 rad.
  - Analytical Jacobians match central differences. The maximum relative error
    over 2000 random states is 1.0e-8 (range-bearing) and 9.8e-10 (bearing).
  - Mean NIS over 4000 draws is 2.98 (expected 3).
  - Joseph form: asymmetry 0.0 and minimum eigenvalue 3.4e-3 after 3000
    predict-update cycles. Near-singular R (1e-12) and a 1e6-variance prior stay PSD.
  - Innovation wraps the residual, so the bearing discontinuity at the cut does
    not reach the update. Coincident geometry raises `ValueError`.
  - 22 tests (`test_ekf`, `test_sensors`, `test_observer_pose`) and 13 bias tests
    in `test_fusion.py` pass.
- **Association and lifecycle (#39).**
  - Per-group gates, Hungarian assignment within a group, range-then-vision
    order, no cross-group competition, range-only ignoring vision, and vision
    unable to initiate tracks all behave as documented.
  - Pending-queue ordering, one-epoch staleness, retrodiction opt-in and
    delivery-time gating match the docs. Lifecycle thresholds are 3 hits to
    confirm, 2 misses to coast and 5 misses to delete.
  - `tracking/` never reads `_true_object_id` or true class. 60 tests in the four
    named files pass.
- **Evaluator (#40).**
  - GOSPA matches brute force to 4.4e-16 over 200 random frames. Paired 95% t
    intervals match scipy to 1e-15.
  - Every Findings tally in `report.md` recomputes from `per_seed.csv`.
  - Denominators and `None` handling match `docs/metrics.md`. chi-square
    thresholds are correct.
  - The TrackEval pin is upstream master HEAD (`12c8791b`) and the live
    cross-check passes (5 tests).
  - No ground truth reaches the estimator.
- **Reproducibility and CI (#41).**
  - The locked install, ruff, format, mypy, the full suite (222 passed) and the
    provenance check all pass.
  - Determinism: two local runs are byte-identical.
  - The artifact commit `e433b84` is an ancestor of HEAD with `src/` unchanged.
    Seeds are 0 to 24 (development) and 25 to 49 were never run.
  - `ci.yml` has `permissions: contents: read`. Both actions are pinned to SHAs
    matching their version comments. A regex sweep of history found no secrets.
- **Documentation (#42).**
  - The README headline counts match `benchmark.json`: RMSE 1/6/8 and 7/3/5,
    precision 14 of 15, MOTA and GOSPA 14 of 16, recall 12 of 16, IDF1 2/5/9,
    the NEES/NIS tallies, identity switches 388.5 to 241.8, and the duplicate-track
    and gate-rejection figures.
  - Method names, per-file test counts, the 42 test names cited in
    `implementation-status.md` (one exception, D-F4) and the TrackEval scope
    statement are consistent.
  - The app labels simulated data on every view.

## 1. Confirmed defects

### R-F2 / D-F1. `report.md` is stale; README quotes it (P1)

- **Where:** `artifacts/benchmark/report.md:10` (commit `9bdeccdd`),
  `artifacts/benchmark/benchmark.json:3` (commit `e433b841`),
  `README.md:198-211`, `docs/technical-walkthrough.md:88-94,246`.
- **Reproduction:** `grep -o '[0-9a-f]\{40\}' artifacts/benchmark/*` shows
  differing commits across the three outputs of one run. `git diff --stat 9bdeccd
  e433b84 -- src` touches 5 files (the group-frozen bias correction). #41
  regenerated the full benchmark (13 min 22 s) and #42 regenerated the four
  sensor-disagreement scenarios (seeds 0 to 24, 10 s) with `mosaic benchmark`. Both
  match `benchmark.json` and `per_seed.csv` and not `report.md`.
- **Observed vs expected:** `crossing_targets / fused_bias_estimated` position RMSE
  is 0.166 ± 0.060 in `report.md` against 0.164 ± 0.054 in the CSV and in the
  regenerated report (also IDF1 0.792 vs 0.801, GOSPA 1.570 vs 1.576). The
  regenerated full report differs from the committed one in 481 lines. README
  bias-estimation numbers differ from the JSON:

  | Claim (README) | README | JSON / HEAD run |
  |---|---|---|
  | Final bias estimates (0.010/0.015/0.020) | 0.0100, 0.0149, 0.0198 | 0.0101, 0.0149, 0.0199 |
  | RMSE gain vs fused | 0.075, 0.117, 0.198 | 0.073, 0.113, 0.192 |
  | Precision gain vs fused | 0.056, 0.122, 0.139 | 0.064, 0.110, 0.131 |
  | MOTA gain vs fused | 0.134, 0.320, 0.378 | 0.155, 0.297, 0.359 |
  | Bias-estimated precision | 0.673, 0.683, 0.674 | 0.681, 0.671, 0.666 |
  | Bias-estimated MOTA | 0.467, 0.489, 0.470 | 0.487, 0.466, 0.450 |
  | Bias-estimated distance-only RMSE | 0.200, 0.202, 0.207 | 0.202, 0.206, 0.215 |
  | Updates/seed at 0.12 rad | about 1.4 | 1.28 |

  `README.md:207` says bias-estimated distance-only RMSE is below range-only's
  0.213; for the 0.020 rad case it is 0.215. The report's own Findings bullet
  ("MOTA better in 3, worse in 0, inconclusive in 13; precision worse in 0") also
  disagrees with the JSON (MOTA worse in 1, inconclusive 12; precision worse in 1,
  inconclusive 11).
- **Confidence:** high (both reports). Shown for 4 of 16 scenarios by #42; the
  other 12 are expected to be stale, shown for the whole report only by #41's
  line diff.
- **Whether a published headline is invalidated:** the README tallies that
  were checked against the JSON are unaffected. The bias-estimation prose and
  figures above are.
- **Proposed:** regenerate `artifacts/benchmark` with one run, re-quote every
  bias-estimation sentence, and see R-F3.

### E-F1. Continuity matcher differs from the TrackEval behaviour it cites (P2)

- **Where:** `evaluation/frames.py:47-49` (comment), `:60`, `:114`;
  `evaluation/metrics.py:338`; `docs/metrics.md:14-16,95`.
- **Reproduction:** two frames. Frame 0: A-T1 at 0 m, B-T2 at 10 m. Frame 1: A at
  0, B at 1.5, T1 at 0.5 (inside both gates), T2 at -1.8 (inside A's gate only).
  Built with the `tests/crosscheck` helpers and `BOX_SIZE=6`.
- **Observed vs expected:** ours gives `matched=4, fn=0, fp=0, idsw=2`. TrackEval
  gives `clr_tp=3, clr_fn=1, clr_fp=1, idsw=0`. The out-of-gate sentinel (1e9) is
  applied after the 1000 continuity bonus, so the solve maximises in-gate pairs
  first and continuity second. TrackEval keeps a valid previous pairing even at
  the cost of another match.
- **Confidence:** high. **Not measured:** how often this occurs in the benchmark,
  so the effect on `identity_switches` and `position_rmse` is a hypothesis (see
  H-3). The four fixed cross-check sequences cannot reach this case, so "Differences
  found: none" (`metrics.md:95`) holds only for those inputs.

### A-F1. Retrodiction loses earlier updates on a repeated time (P2)

- **Where:** `tracking/tracker.py:161` (resets `_epoch_applied`), `:396` (early
  return for a repeated time), `:581-595` (`_replay_epoch`).
- **Reproduction:** confirmed track, `r0` at t=0, `r1` on time at t=0.1, then a
  second call at t=0.1 delivering a delayed vision observation captured at t=0.
- **Observed vs expected:** trace(P) goes 0.7906 to 1.227 in `retrodiction` mode,
  where the update should shrink it (0.6634 in `delivery_time` mode). `r1` is
  dropped from the replay, but `track.associated_observations` still lists it.
- **Confidence:** high on mechanism and repro. **Not verified:** whether the
  runner or sensors ever call twice at one time (section 4).

### A-F4. Unknown class name raises out of `process_observations` (P2)

- **Where:** `tracker.py:656`, `:692`; reached at `:230` after the state update.
- **Reproduction:** `class_probs={"bogus": 1.0}` raises
  `ValueError: 'bogus' is not a valid ObjectClass`.
- **Observed vs expected:** the batch aborts, `_finish_epoch` is skipped, the
  track stays updated, hit/miss accounting does not run and `_last_time` does not
  advance. Other malformed input is rejected via `_reject_invalid`.
- **Confidence:** confirmed by repro. **Not verified:** whether the shipped
  sensors can emit non-enum names, so this is a robustness defect, not a known
  production failure.

### R-F3. Provenance check validates one file (P2)

- **Where:** `scripts/check_artifact_provenance.py:28,30-43`.
- **Reproduction:** `make provenance-check` prints "provenance OK: artifact from
  e433b8411bf2, package 0.1.0, source unchanged" (re-run at `356d032` for this
  audit) while R-F2 holds.
- **Observed vs expected:** it never opens `report.md` or `per_seed.csv`.
  `SOURCE_PATHS = ("src/",)` also excludes `uv.lock` and `pyproject.toml`.
  `docs/evaluation-protocol.md:105-113` says the check guarantees the artifact
  "describes this tree"; that holds for the JSON only.
- **Confidence:** high.

### D-F2. "CI on every push" (P2)

`README.md:23,42`, `docs/evaluation-protocol.md:91` and the #29 comment say CI
runs on every push. `.github/workflows/ci.yml:3-7` triggers on pushes to `main`
and pull requests to `main` only. Not executed; reading the workflow suffices.
Confidence high. Expected wording: "every push to main and every pull request to main".

### D-F3. Reserved held-out seed 42 is the default (P2)

- **Where:** `README.md:60`, `docs/demo-walkthrough.md:17`,
  `app/streamlit_app.py:40` (slider 0 to 100, default 42), label
  `app/data_prep.py:17` ("development seeds only").
- **Observed vs expected:** the held-out range is 25 to 49
  (`README.md:9,138`, `evaluation-protocol.md:24`). The default quickstart run and
  the app's default run use a reserved seed, and the slider allows the whole
  reserved range, while every view is captioned "development seeds only". These
  are single ad-hoc runs, not benchmark artifacts. Confidence high.

### D-F4. `core-validity-audit.md` states superseded facts as current (P2)

`docs/core-validity-audit.md:55` says `track_fragmentation` is unsupported
(`evaluation/metrics.py:149-170` computes it). The same file says 10 presets
(`:53`; `available_scenarios()` returns 16), "77 passed" (`:59-64`; 222 collected)
and cites `test_out_of_sequence_observations_are_explicitly_rejected` (`:51`),
which does not exist in `tests/`. The banner says "historical", but the
"Resolution status" and "Current verification" headings read as current, and the
README links the file as authoritative (`README.md:249-253,286`). Confidence high.

### D-F5, D-F6. Wrong or overstated figures in `limitations.md` and `demo-walkthrough.md` (P2)

- `docs/limitations.md:166-168` gives miscalibration coverage as 0.12 to 0.14. The
  report has 0.089 (range-only), 0.106 (fused), 0.091 (bias-estimated).
- `limitations.md:169-170` says fused precision is lower "in every scenario with
  defined precision". It is worse in 14, inconclusive in 1, undefined in 1
  (README says 14 of 15).
- `demo-walkthrough.md:67-70` says fused RMSE is "often slightly lower". Under the
  headline matcher it favours fusion in 1 of 15 scenarios and goes against it in
  6. Only the distance-only matcher favours fusion (7 of 15).
- `limitations.md:153` mentions two sensor-disagreement scenarios; there are four.
  Confidence high (P3 for the last item).

### D-F7. Retrodiction "improves position accuracy" (P3)

`README.md:213-216` and `limitations.md:113-118`. The numbers are correct (0.308
to 0.283 range-only; 0.329 to 0.335 fused), but fused RMSE gets worse, so the
sentence is true for range-only only. Also `README.md:217` is the only document
in first person, and `implementation-status.md:91` says "diagnosed as worse and
unexplained", which reads as a diagnosis. Confidence high.

### R-F1 / D-F12. Golden check failed across platforms (P2, resolved at HEAD)

`scripts/check_benchmark_golden.py:68` compared bytes after normalising only
40-hex hashes. On aarch64 `per_seed.csv` differed in 117 cells (last 1 to 3
digits), and a full regeneration differed from the committed CSV in 11 811 cells
with maximum relative difference 2.8e-12, with no discrete metric different.
**Status:** fixed by #49 (closed). Re-run for this audit at `356d032`: `make
benchmark-golden-check` prints "golden benchmark matches (benchmark.json,
per_seed.csv, report.md)". `README.md:23` and `evaluation-protocol.md:93-103`
should be re-read against the new tolerance semantics (section 4). The claim that
results are scientifically but not byte-reproduced across platforms still stands.

### P3 defects

| ID | Where | Observed vs expected | Source confidence |
|---|---|---|---|
| S-F1 | `sensors/range_bearing.py:110-111` | Range floor 0.1 m is applied before bias, so at 0.2 m, sigma 0.5, bias 0.3 the mean range is 0.651 against 0.5, and 42% of 5000 draws sit at 0.4. Noise is no longer Gaussian, so reported covariance is wrong inside about 1 m. Repro `probe_sensor_model.py` item 3 | confirmed; confidence not stated |
| S-F2 | `range_bearing.py:40-47`, `vision_bearing.py:38-45` | `_due` resets to the current time, so a 30 Hz sensor on a 100 Hz sim emits 75 frames in 3 s (25 Hz) and 10 Hz on 0.07 s ticks emits 50 in 7 s (expected 70). Harmless at the 10 Hz / 0.1 s defaults | confirmed |
| S-F3 | `range_bearing.py:99`, `vision_bearing.py:88`, `ekf.py:172,188,216,226` | Sensors skip below 1e-6 m, the EKF raises below 1e-9 m. Between them dbearing/dy is 1e6. `association.py:161,217` catch `ValueError`, but a tracker was not run through a coincident state | confirmed for thresholds; handling read, not executed |
| S-F5 | `domain/models.py:32-34` | `wrap_angle(nan)` returns nan, `wrap_angle(3*pi)` returns 3.1415926535897927, `wrap_angle(±pi)` keeps its sign. The EKF rejects non-finite inputs first | confirmed |
| S-F6 | `docs/measurement-models.md` | Omits the 0.1 m range floor, floor-before-bias, the 1e-6 skip and tick-quantised frame rate | confirmed |
| A-F2 | `tracker.py:250-252` | Same call time twice runs a full extra epoch: `misses 0, age 1, epoch 1` becomes `misses 1, age 2, epoch 2` with a duplicate snapshot. Same root cause as A-F1 | confirmed |
| A-F3 | `tracker.py:183,202`; `docs/measurement-models.md:121` | Staleness and age of information use processing time. Capture 0.0 / delivery 0.01 processed at 0.1 reports 0.1 not 0.01. Capture 0.99 / delivery 1.01 processed at 1.1 is rejected as stale (age 0.11) | confirmed |
| A-F5 | `tracker.py:162-163,429-430` | A duplicate observation id mid-batch raises after earlier items were queued and tracks were advanced. A retry fails on the same id | confirmed |
| A-F6 | `tracker.py:426-428` | Vision dropped in range-only mode moves no counter, so `vision_generated` exceeds the delivered buckets with no bucket for the difference. Intended isolation. Runner reporting not read | confirmed; design choice |
| E-F2 | `docs/metrics.md:23-24` vs `:14-19`, `frames.py:66,85` | Docs contradict each other on whether matching is independent per timestamp. The code carries the previous pairing | high |
| E-F3 | `reporting/markdown.py:241-243` | Garbled sentence in the `sensor_disagreement_within_gate` Findings bullet ("on / results"). Two bullets are static text, not derived from numbers | high |
| E-F4 | `reporting/markdown.py:21-41` | Six scenarios share a bit-identical `range_only` baseline, so tallies count it repeatedly. No multiplicity correction over 16 x 7 intervals. `n == 0` scenarios (`stale_rejection`) are skipped in every count, so 8 inconclusive sums to 15 of 16 unstated. Wording is hedged, so no claim is false | facts confirmed; wording is judgement |
| E-F5 | `evaluation/frames.py:38-44,69-71` | A snapshot more than 1e-9 off every world-state time is dropped silently (`recall=0.0, precision=None`, yet `num_confirmed_tracks=1`). Two snapshots with the same `(track_id, time)` overwrite each other. The benchmark does not hit either path | high |
| R-F4 (caveat) | `docs/evaluation-protocol.md:27-35` | Held-out separation is by convention: nothing rejects a run over 25 to 49 or records that it was consumed. Docs say so | high |
| R-F6 | `pyproject.toml:22-31` | Only `>=` bounds, so `pip install` users are unpinned; CI tests only Python 3.12. The artifact does not record numpy/scipy versions, which matter at the 1e-12 level | stated |
| R-F7 | `.github/workflows/ci.yml:30`, `Makefile:11` | CI lints `src tests` but not `scripts/` or `app/` (`ruff check scripts` passes when run). `ruff format --check .` covers the whole tree and `make format-check` does not (D-F11) | stated |
| D-F8 | `docs/architecture.md:38` | "10 named presets"; 16 exist | high |
| D-F9 | `docs/metrics.md:61` | Fragmentation wording can be read as counting frames; code counts one interruption per gap (`metrics.py:149-170`) | medium |
| D-F10 | `docs/roadmap.md:19,36,48`; `docs/release-checklist.md:11` | Roadmap says "current branch, unreleased" and "77 tests" and leaves multi-object scenarios unchecked though they exist. Release checklist says the branch must not be pushed though PR #35 merged. `roadmap.md` has no pointer to `implementation-status.md`, which says historical documents "point here" | high |
| D-F11 | `docs/implementation-status.md:157-159`, `limitations.md:205-210` | CI never invokes `make`; `ruff format --check .` (whole tree) differs from `make format-check` (`src tests`). `ruff check` in CI covers `src tests` only | medium |
| D-F13 | `cli/main.py:341` | `mosaic run` evaluates two methods; `compare`, `evaluate`, `benchmark` and the app run three. README does not say so | wording |

## 2. Hypotheses

| ID | Statement | Evidence so far | What would settle it |
|---|---|---|---|
| H-1 (S-F4, P3) | The global bias estimator uses reported covariance, so it is overconfident when `reported_cov_scale < 1`. It lives in `tracker.py:299-340` (measurement noise at `:336`), not `ekf.py` | Scalar replica, 300 seeds, 3000 updates: scale 1.0 gives RMS 0.00072 vs reported sd 0.00106 (consistent); scale 0.1 gives RMS 0.00131 vs 0.00059 (2.2x overconfident). A range-bearing bearing bias leaks 1:1 into the vision estimate (-0.004997 for 0.005), which the docstring states | Tracker with `reported_cov_scale=0.1` on vision, compare `vision_bias_estimate` error with `_bias_var` |
| H-2 (A-F9, P3) | Tracks initiated from a delayed observation take the capture-time position but are stamped `time=now`, with no prediction over the age | Repro J: a track initiated at t=0.1 from a t=0.0 observation reports `time=0.1` and the capture-time position. No stored posterior, so a later delayed observation takes the delivery-time path even under retrodiction. Bounded by one epoch | Measure the magnitude in a delayed scenario |
| H-3 (E-F1 impact) | The continuity tie-break may move headline `identity_switches` and `position_rmse` | The report already shows the RMSE tally depends on the matcher (1/6/8 vs 7/3/5) | Instrument `match_frame` or re-run with a TrackEval-style matcher |
| H-4 (E-F6, P3) | Coverage and NEES accept an indefinite but invertible covariance (`diag(1,-1,1,1)` gives `coverage_samples=1, position_coverage_95=1.0`), and `nees_sums` drops a valid position sample when the velocity block is singular (`coverage_samples=1, nees_samples=0`). Sample skips are not counted | `metrics.py:96-102,292-303`, probes in #40 | Show the tracker can emit a non-PSD covariance |
| H-5 (E-F7, P3) | Identical non-zero paired differences give a zero-width interval that the tally reads as "excludes zero" | `statistics.py:48`; `test_identical_differences_give_a_degenerate_interval` pins it; the all-zero case is classed inconclusive | Intentional but unflagged in the report |
| H-6 (E-F8, P3) | Perfect observer pose is passed to the estimator (`range_bearing.py:144-148`, `vision_bearing.py:129,163`). `WorldState` docs say the world state "must never leak into estimator inputs" (`models.py:98`). Not stated in `limitations.md` | Design choice that limits transfer to real systems | Add to `limitations.md` or confirm as intended |
| H-7 (R-F8, P3) | Gitleaks checksums come from the same release URL, so they guard corruption not a compromised release. `uv` and `uv python` are unpinned | `ci.yml` read | Pin `version:` for setup-uv |
| H-8 (D-F14) | "Preregistered" within-gate bias values (`README.md:190`, `implementation-status.md:29`, `limitations.md:156`) | Scenarios added in `43b6e4a`; the 0.015 value pre-dated it; no timestamped plan separates "chosen before results" from code history | Cannot be settled from the repository |
| H-9 (R-F9, P2) | `test`, `secret-scan` and `artifact-checks` may not be required status checks | `gh api .../branches/main/protection` returned 403 | Repository admin check |

## 3. Unimplemented features

| ID | Feature | Evidence |
|---|---|---|
| U-1 (R-F10, P2) | Dependency-vulnerability monitoring. `.github/` holds only `workflows/ci.yml`; no Dependabot, Renovate, `pip-audit` or OSV step; ~76 locked packages. Tracked by #44. Recommendation from #41: Dependabot (or Renovate, which handles the git-rev TrackEval pin better) for `uv` and `github-actions` weekly; a scheduled and PR `pip-audit` job on `uv export --locked`; GitHub secret scanning and push protection. Pair with the tolerant golden check, which #49 has since delivered | `ls .github`, `ci.yml` |
| U-2 (R-F4) | Held-out protection in code: nothing rejects a run on seeds 25 to 49 or records it. Docs state this is by convention | `evaluation-protocol.md:27-35` |
| U-3 (A-F7, P3) | An M-of-N or consecutive-hit confirmation rule. Confirmation counts total hits (`tracker.py:718`), so hit, miss, hit, miss, hit confirms at epoch 5. This matches the `TrackEstimate.hits` docs; `architecture.md:65-67` does not say which rule is used | Repro E |
| U-4 (A-F8, P3) | Track initiation gating, minimum separation from existing tracks and merging. Duplicate tracks follow from the documented same-group policy (`association.py:12-16`, `limitations.md:33,132-151`), and `test_same_group_policy_assigns_one_observation_and_initiates_from_the_other` pins it | Repro D |
| U-5 | Cross-checks against a reference implementation for GOSPA, NEES/NIS, coverage, fragmentation, class accuracy, distance-only variants and duplicate-track metrics (already stated in `metrics.md:109-121`). GOSPA was brute-force checked in #40 | `metrics.md` |
| U-6 | HOTA, MT/ML/PT, OSPA(T); none are claimed | #40 |
| U-7 | Cross-process or cross-platform determinism test (only in-process byte equality exists, `tests/integration/test_pipeline.py:88-113`); a scheduled regenerate-and-compare job | #41 |
| U-8 | Held-out evaluation (#7) and the documentation site (#34); both out of scope here | `implementation-status.md` |

## 4. Unresolved questions and what was not verified

Each item names the missing finding and the reason. No gap was filled from memory.

| Area | Not verified | Why |
|---|---|---|
| #38 | Linearisation error at close range or large P; the real tracker bias loop; full-filter consistency over a scenario (NIS checked for the sensor/EKF pair only); the full suite | Out of the ticket's execution budget; the tracker belongs to #39 |
| #39 | Whether the runner or sensors trigger A-F1, A-F2 or A-F4; how the vision sensor builds `class_probs`; multi-epoch gaps under retrodiction (reasoned from `tracker.py:407-413`); benchmark and golden output; the full suite | Runner and sensor code were outside the ticket's reading; source change not allowed |
| #40 | Frequency of E-F1 in the benchmark; whether the tracker can emit non-PSD covariances; reproduction of the benchmark numbers; NIS/ANIS internals | Needs instrumentation (a source change) or a longer experiment |
| #41 | Branch protection (API 403); gitleaks run (not installed); CI behaviour on x86 beyond run history; whether the committed artifact was ever byte-reproducible on its generating platform; the cause of the 1e-12 drift (BLAS/libm is a hypothesis) | No admin token, no local x86 machine, no network install |
| #42 | A full 16-scenario regeneration at HEAD (aborted, too slow); GitHub Actions behaviour; the Streamlit link in a real browser; whether preregistration preceded results | No browser or CI access; repository history cannot answer the last |
| This audit | Fresh execution of the research probes: findings are carried from the five reports. Only `make provenance-check` and `make benchmark-golden-check` were re-run, at `356d032` | Single-ticket scope; the numeric claims are those of the research reports |
| This audit | Whether #49's tolerant comparison changes any other claim in `README.md:23` and `evaluation-protocol.md` | The golden script was not re-read; only its pass at HEAD was observed |
| This audit | The ticket asks for the research files to be linked. All five branches are on the remote at the commits above. The 403 push failures recorded in earlier comments on #38 to #42 were later resolved by Sandcastle pushes | `git ls-remote`, `git log origin/research/*` |

Open decisions (not defects), from map #36: whether any finding invalidates a
published benchmark headline or requires regenerating `artifacts/benchmark/`
(R-F2 does for the bias-estimation rows; the other README tallies were confirmed);
the final treatment of the historical audit documents; and whether dependency
monitoring should block CI (#44).

## Appendix A. Commands run

Collected from the five reports. Environment differed: #38, #39 and #41 ran in
scratch venvs or aarch64 sandboxes (#41: Linux aarch64, Python 3.12.13, numpy
2.5.4).

```
# #38 (PYTHONPATH=src, package not installed)
python docs/research/sensor-ekf-math/probe_sensor_model.py
python docs/research/sensor-ekf-math/probe_ekf_jacobian_wrap_psd.py
python docs/research/sensor-ekf-math/probe_psd_edges.py
python docs/research/sensor-ekf-math/probe_bias_estimator_scalar.py
pytest tests/unit/test_ekf.py tests/unit/test_sensors.py tests/unit/test_observer_pose.py   # 22 passed
pytest tests/unit/test_fusion.py -k bias                                                    # 13 passed
# #39 (repro script outside the repo, PYTHONPATH=.:src)
python /tmp/repro/r.py
pytest tests/unit/test_tracking.py tests/unit/test_timing.py tests/unit/test_fusion.py tests/unit/test_ground_truth_isolation.py   # 60 passed
rg "true_" src/mosaic_perception/tracking/
# #40
pytest tests/unit/test_trackeval_crosscheck.py        # 5 passed, none skipped
git ls-remote <TrackEval upstream>                    # pin == master HEAD
# throwaway scripts: GOSPA brute force, scipy t interval, per_seed.csv tallies, matcher repro
# #41
uv sync --locked --all-extras; uv lock --check
ruff check src tests; ruff check scripts; ruff format --check .; mypy src
uv run pytest -q                                      # 222 passed, 82 s
uv run python scripts/check_artifact_provenance.py    # pass
uv run python scripts/check_benchmark_golden.py       # FAIL on aarch64 (before #49)
mosaic benchmark --scenario all --seeds 0-24 --duration 10.0   # 13 m 22 s
gh run list; gh api repos/.../branches/main/protection         # 403
git log --all -G'<AKIA|ghp_|sk-|BEGIN PRIVATE KEY|xox[bp]->'    # 0 matches
# #42
python -m pytest --collect-only -q                    # 222 tests
python -m pytest -q tests/unit/test_trackeval_crosscheck.py tests/unit/test_app_smoke.py tests/unit/test_app_data_prep.py -rs   # 11 passed
make provenance-check; make benchmark-golden-check
ruff format --check .; ruff check app scripts
mosaic benchmark --scenario sensor_disagreement_within_gate_low,sensor_disagreement_within_gate,sensor_disagreement_within_gate_high,sensor_disagreement_large_bias --seeds 0-24 --duration 10.0 --output /tmp/wg
# This audit (at 356d032)
git diff d3e88d9 HEAD --stat -- src artifacts pyproject.toml uv.lock   # empty
make provenance-check            # provenance OK: artifact from e433b8411bf2, package 0.1.0, source unchanged
make benchmark-golden-check      # golden benchmark matches (benchmark.json, per_seed.csv, report.md)
```

## Appendix B. Documentation claims table (from #42)

| # | Claim | Location | Evidence | Status | Correction |
|---|---|---|---|---|---|
| 1 | Bias estimates 0.0100/0.0149/0.0198, gains 0.075/0.117/0.198 etc. | README:198-211; tech-walkthrough:88-94 | JSON and HEAD run: 0.0101/0.0149/0.0199, 0.073/0.113/0.192 | stale | Regenerate report, re-quote (R-F2) |
| 2 | Distance-only bias-estimated RMSE below range-only's 0.213 | README:207 | high case 0.215 | contradictory | R-F2 |
| 3 | About 1.4 updates/seed at 0.12 rad | README:210; tech-walkthrough:94 | 1.28 | stale | R-F2 |
| 4 | Report commit is the artifact commit | report.md:10 vs benchmark.json:3 | 9bdeccd vs e433b84 | contradictory | Regenerate; extend provenance check |
| 5 | CI on every push | README:23,42; eval-protocol:91 | ci.yml:3-7, main only | contradictory | Reword |
| 6 | Golden check byte-for-byte | README:23; eval-protocol:93-103 | failed on 1-ulp noise locally before #49 | resolved by #49; re-read wording | See R-F1 |
| 7 | "Development seeds only" while seed 42 is the default | data_prep:17; app:40; README:60 | 42 is in reserved 25-49 | contradictory | D-F3 |
| 8 | Fragmentation unsupported | core-validity-audit:55 | metrics.py:149 | stale | D-F4 |
| 9 | 10 presets | architecture:38; core-validity:53 | 16 | stale | D-F4, D-F8 |
| 10 | 77 tests passing | roadmap:36; core-validity:64 | 222 collected | stale | D-F4, D-F10 |
| 11 | Coverage 0.12-0.14 | limitations:166-168 | 0.089-0.106 | contradictory | D-F5 |
| 12 | Precision lower in every scenario | limitations:170; demo-walkthrough:68 | 14 of 15 | contradictory | D-F6 |
| 13 | Fused RMSE often slightly lower | demo-walkthrough:68 | 1 of 15 headline | contradictory | D-F6 |
| 14 | Two sensor-disagreement scenarios | limitations:153 | four | stale | D-F6 |
| 15 | Retrodiction improves position accuracy | README:213; limitations:113 | fused 0.329 to 0.335 | contradictory (partial) | D-F7 |
| 16 | Historical docs "point here" | implementation-status:6 | roadmap has no pointer | contradictory | D-F10 |
| 17 | RMSE tallies 1/6/8, 7/3/5; precision 14; MOTA/GOSPA 14/16; recall 12/16; IDF1 2/5/9 | README:148-170 | JSON tally | confirmed | none |
| 18 | NEES above in 15 (velocity 14), NIS below 13/14 | README:178-184 | JSON | confirmed | none |
| 19 | Identity switches 388.5 to 241.8 | README:170-177; limitations:137-141 | JSON sum 388.52/241.80 | confirmed | none |
| 20 | Duplicate tracks 38.9/39.3, 8.6/73.4; gates 34.2/38.9/39.3; 0.0/1.8/5.7 | README:166-169; limitations:33-37 | JSON | confirmed | none |
| 21 | Gate rejection 264.7/275.2, 10.2 applied; 20.8/30.8/52.8 | README:186-193 | JSON | confirmed | none |
| 22 | TrackEval: MOTA, IDF1/IDP/IDR, counts, IDSW agree on 4 sequences | metrics:72-121; impl-status:108 | pytest 5 passed | confirmed | none |
| 23 | Three methods in app; N/A not zero | impl-status:131-146; app | data_prep, tests pass | confirmed | none |
| 24 | Seeds 25-49 not run | README:9,138 | report.md:11, JSON seeds | confirmed | none |
| 25 | "Preregistered" bias values | README:190 | no timestamped plan | unverifiable | none (H-8) |
