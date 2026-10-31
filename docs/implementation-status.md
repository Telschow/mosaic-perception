# Implementation Status

The single source of truth for what this repository actually contains today,
per subsystem, with the evidence behind each claim. Origin: an external audit
could not inspect the code and asked for one place that answers "what is
implemented, and how do you know". Historical audit documents are superseded
by this one and point here. The current verification of these claims against
the code, tests and artifacts is the
[comprehensive audit](audits/mosaic-perception-comprehensive-audit.md), pinned
to a commit; where the audit finds a claim here wrong, the audit's finding
stands until the claim is corrected.

## How to read this document

Every subsystem is in exactly one of three states:

- **Implemented** — the behaviour exists and is backed by a named test or a
  committed artifact. If the backing cannot be located, the claim is wrong:
  file an issue rather than trusting it.
- **Planned** — intended but absent, tracked by an open issue (linked by
  number). Planned work never appears under Implemented.
- **Out of scope** — deliberately not attempted; the reason is stated.

Limitations are not listed inline here; each subsystem links the document that
carries them. Nothing in this file is asserted from memory: every test name
below exists in the suite (`make test`), every artifact path is committed.

## Subsystems

### Simulation — **Implemented**

Deterministic 2-D synthetic worlds with known ground truth, optional moving
observer, scenario presets with preregistered parameters.

- Evidence: `test_world.py` (12 tests, including `test_world_deterministic`),
  `test_scenarios.py` (11 tests, including
  `test_within_gate_bias_sweep_uses_only_the_preregistered_values`), integration
  `test_paired_run_is_deterministic_and_uses_same_world`.
- Limitations: [docs/limitations.md](limitations.md) — Scope; synthetic worlds
  only, no real sensor data.
- Planned: none specific to simulation.

### Sensors — **Implemented**

Range-bearing sensor (range, sensor-frame bearing, range rate), vision-bearing
sensor (bearing plus class probabilities), constant bias injection, sensor
frame rates, observer pose at capture time.

- Vision bias estimation is implemented as the third method
  (`fused_bias_estimated`): a global scalar Kalman filter on vision-bearing
  innovations anchored by range-bearing states, subtracted from vision bearings
  before gating and updating. Off by default; requested via
  `run_pair(..., include_bias_estimation=True)`.
- Evidence: `test_sensors.py` (6 tests, including
  `test_sensor_bias_is_applied_in_sensor_units` and
  `test_false_alarms_are_emitted_and_use_sensor_frame_metadata`),
  `test_observer_pose.py` (3 tests), vision/range gating and bias-estimation
  tests in `test_fusion.py` (35 tests, including
  `test_large_vision_bias_is_gate_rejected_without_touching_track`,
  `test_bias_estimation_is_off_by_default` and
  `test_bias_estimate_converges_to_a_gate_passing_bias_using_the_range_bearing_anchor`),
  integration `test_bias_estimated_method_runs_and_reports_its_estimate`,
  and the bias-estimate column in
  [artifacts/benchmark/report.md](../artifacts/benchmark/report.md).
- Limitations: [docs/limitations.md](limitations.md) — Estimation and
  association; classification is generated but not evaluated, vision cannot
  initiate tracks. The estimate assumes a constant bias and an unbiased
  range-bearing sensor.

### Tracking — **Implemented**

Constant-velocity EKF with sensor-frame measurement models, Joseph-form
covariance updates, wrapped angular innovations, per-group gated Hungarian
association, pending delivery queue with a documented one-epoch staleness
policy, deterministic track lifecycle.

- One-step-lag retrodiction is implemented and opt-in
  (`delayed_update="retrodiction"`, scenario `delivery_delay_retrodiction`):
  the tracker stores the pre-prediction posterior and replays the epoch in
  capture-time order before predicting to the processing time, for
  observations at most one epoch old.
- Evidence: `test_ekf.py` (13 tests, including
  `test_range_bearing_jacobian_matches_finite_differences`),
  `test_timing.py` (18 tests, including
  `test_observation_older_than_one_epoch_is_rejected_and_counted`,
  `test_delayed_observation_is_applied_to_delivery_time_state_not_rewound` and
  `test_retrodiction_equals_the_time_ordered_replay_of_the_delayed_observation`),
  `test_fusion.py` (35 tests), `test_tracking.py`,
  `test_ground_truth_isolation.py` (3 tests proving ground truth cannot reach
  the estimator).
- Limitations: [docs/limitations.md](limitations.md) — Timing and delivery;
  observations older than one epoch are rejected, not replayed, in the default
  mode; retrodiction covers only the one-epoch lag, gates against the
  delivery-time state, is off by default, and its benchmark effect on
  identity switches and MOTA is worse and its cause is undiagnosed.
- Planned: none specific to tracking.

### Evaluation — **Implemented**

Snapshot-based per-frame matching with a continuity-preferring headline
matcher, CLEAR-MOT accuracy, ID metrics, GOSPA, coverage, NEES/NIS,
class accuracy, paired statistics across seeds.

- Evidence: `test_evaluation.py` (33 tests), `test_frame_metrics.py` (24
  tests), `test_registry.py` (9 tests, including
  `test_every_declared_metric_is_documented`), `test_paired.py` (7 tests),
  and the TrackEval cross-check: `test_trackeval_crosscheck.py` compares MOTA,
  IDF1/IDP/IDR and the CLEAR counts against TrackEval's reference
  implementation on four fixed sequences (one comparison per sequence, plus a
  guard that the recorded reference still matches the pinned TrackEval), with
  the pinned reference numbers in `tests/crosscheck/trackeval_reference.json`.
- Cross-check status: MOTA, IDF1, IDP, IDR, misses, false positives and
  identity switches are cross-checked and agree exactly; GOSPA, NEES/NIS,
  coverage, fragmentation and class accuracy are not (hand-computed tests
  only). Details and definitional boundaries: [docs/metrics.md](metrics.md).
- Limitations: [docs/metrics.md](metrics.md) Reporting rules;
  [docs/limitations.md](limitations.md) — Evaluation; development seeds only
  unless an artifact states otherwise.
- Planned: run the held-out evaluation once on frozen code → #7.

### Reporting and CLI — **Implemented**

Markdown/CSV/JSON reports from one metric registry, `mosaic run / compare /
evaluate / benchmark` commands, canonical artifacts regenerated from code.

- Evidence: `test_report.py` (12 tests, including
  `test_render_report_is_deterministic`), integration tests
  `test_evaluate_cli_is_reproducible` and `test_cli_rejects_unknown_scenario`,
  the committed benchmark artifacts `artifacts/benchmark/` verified in CI by
  `scripts/check_artifact_provenance.py`, and the golden small benchmark
  `artifacts/benchmark-golden/` verified byte-for-byte by
  `scripts/check_benchmark_golden.py` (see
  [docs/evaluation-protocol.md](evaluation-protocol.md)).
- Limitations: [docs/limitations.md](limitations.md) — Reproducibility
  boundaries; artifacts record development seeds, no wall-clock timestamps.
- Planned: none; the static documentation site is a publishing concern → #34.

### App (Streamlit workbench) — **Implemented**

Interactive workbench over the shared experiment runner: metrics table
(headline and distance-only accuracy), scene view, simulated-data labelling on
every view, links to known limitations. Renders every method the experiment
runner exposes: `range_only`, `fused` and `fused_bias_estimated`.

- Evidence: `test_app_data_prep.py` (5 tests over the browser-free data
  preparation on a short scenario), `test_app_smoke.py` (renders and runs the
  app in-process without a browser).
- Limitations: the app is a view over synthetic results, not an analysis tool;
  same limitations as Evaluation.
- The app runs all three methods (`range_only`, `fused`,
  `fused_bias_estimated`) on the same world in one click.
- Planned: none.

### CI — **Implemented**

Locked dependency install, Ruff lint and format check, mypy, the full test
suite, CLI smoke tests, a pinned secret scan over full history, artifact
provenance and golden-benchmark checks. Least-privilege permissions, all
actions pinned to commit SHAs.

- Evidence: `.github/workflows/ci.yml` (uv pinned to 0.13.6): jobs `test`, `secret-scan`,
  `artifact-checks`. CI invokes the tools directly rather than through `make`,
  on the same paths as the Make targets: `ruff check src tests scripts app`
  (`make lint`), `ruff format --check src tests scripts app`
  (`make format-check`), `mypy src`, `pytest`, then `scripts/check_artifact_provenance.py` and
  `scripts/check_benchmark_golden.py` (the `make provenance-check` and
  `make benchmark-golden-check` targets). Secret-scan result recorded on issue #29 (gitleaks
  8.30.1, 46 commits, no leaks).
- Limitations: [docs/limitations.md](limitations.md) — Type checking and CI;
  mypy covers `src/` only, tests are linted but not type-checked.
- Planned: none.

## Planned work (tracked by open issues)

| Issue | Subsystem | What it adds |
|---|---|---|
| #7 | Evaluation | The one held-out evaluation run on frozen code (blocked by the remaining evaluation work) |
| #34 | Reporting | Static documentation site published with GitHub Pages |

Open issues are not implemented work. The live list is the issue tracker
(`gh issue list --state open`); the table above is the curated subset that
changes subsystem behaviour.

## Out of scope

From [docs/roadmap.md](roadmap.md): real sensor integration, deep learning,
military/tactical applications, ego-navigation, C2/operator systems, optional
3-D extension, performance profiling separate from correctness claims.

## Superseded documents

The following describe older states of this repository and must not be read as
current (the current audit is
[audits/mosaic-perception-comprehensive-audit.md](audits/mosaic-perception-comprehensive-audit.md)):
[audit-report.md](audit-report.md),
[core-validity-audit.md](core-validity-audit.md),
[release-checklist.md](release-checklist.md) and the superseded sections of
[roadmap.md](roadmap.md). For current state, use this document.
