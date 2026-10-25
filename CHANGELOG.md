# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - correctness and evaluation repair

This branch repairs the published v0.1.0 implementation. It is not a feature
release. The v0.1.0 benchmark numbers are invalid and have been replaced; see
`docs/core-validity-audit.md` for the reproduced defects.

### Fixed

- **Association**: replaced one global one-to-one assignment with independent
  per-measurement-group gated Hungarian assignments. A track can now receive one
  range-bearing and one vision update in the same epoch, applied sequentially.
- **Range-only isolation**: `range_only` no longer enqueues or associates vision
  observations, so the baseline cannot be influenced by the sensor it is meant
  to exclude.
- **Measurement frame**: sensors, EKF, gating and track initiation now share one
  explicit convention: bearings are in the sensor frame (world line-of-sight
  angle minus observer heading, wrapped to `[-pi, pi]`), and range rate is
  relative to observer velocity.
- **Observer motion**: `Pose2D` carries velocity; moving observers use analytic
  position, heading and velocity, and the previous vacuous moving-observer test
  was replaced with real assertions.
- **EKF**: constant-velocity discrete white-noise-acceleration process noise,
  wrapped angular innovations, Joseph-form updates, Cholesky checks on
  innovation covariance, covariance symmetrisation and PSD rejection.
- **Track lifecycle**: hits are counted only when an observation is actually
  applied; misses are counted for tracks with no accepted update in an epoch.
  Rejected or failed updates do not count as hits and do not reset misses.
- **Delivery timing**: observations are held in a pending queue until their
  delivery time. Observations older than one epoch (`dt + 1e-6`) are explicitly
  rejected with a logged stale reason and counted. No future observation is
  silently dropped.
- **Frame rate**: sensors now honour `frame_rate` instead of emitting on every
  simulation step.
- **Scenarios**: scenario names now resolve to real sensor/observer overrides;
  added `delivery_delay`, `out_of_sequence` and `moving_observer` presets.
- **Evaluation**: evaluation uses per-epoch track snapshots, confirmed/coasting
  tracks only, and one-to-one gated Hungarian matching at each timestamp. The
  hard-coded 0.85 coverage was replaced with χ²(2, 0.95) = 5.991. Recall and
  precision denominators are explicit; identity switches, false tracks and
  coverage sample counts are computed.
- **Unsupported metrics**: `track_fragmentation` is explicitly `None`/`N/A`, not
  a fabricated zero. Unimplemented metrics are no longer defaulted to plausible
  values.
- **Determinism**: deterministic sensor observation IDs and track IDs replace
  `uuid4`; benchmark artifacts contain no wall-clock timestamps.
- **Fair comparison**: a shared runner executes paired range-only and fused runs
  on the same world states and the same range-sensor random streams.
- **CLI**: implemented `mosaic evaluate`; added seed-range parsing, scenario
  validation, canonical JSON/CSV/Markdown artifacts and delivery statistics.
- **CI**: locked `uv` install, ruff check, format check, tests and a CLI smoke
  test now run in CI. Added `uv.lock`.
- **Tests**: 77 tests, including hand-constructed evaluator cases, gating,
  sequential fusion, range-only isolation, frame timing, pending/OOS policy,
  finite-difference Jacobians, angle wrapping, covariance PSD and end-to-end
  moving-observer accuracy.

### Changed

- The method identifier remains `range_only`, but it now explicitly means
  "range-bearing sensor only; vision ignored entirely".
- Canonical artifacts are `artifacts/benchmark/benchmark.json`,
  `per_seed.csv` and `report.md`. The duplicate `summary.json` and
  `benchmark_report.md` aliases were removed.
- The checked-in benchmark uses all 10 scenarios and development seeds 1–5 at
  10 s. Held-out seeds 25–49 are reserved and were **not** run.

### Documentation

- README, metrics, evaluation protocol, measurement models, scenarios,
  limitations, architecture, design decisions, walkthrough, FAQ, roadmap and
  demo documents were updated to describe the implemented behavior.
- The old audit report and release checklist are retained only as historical
  documents and are marked as superseded.
- The core validity audit now records the resolution status of each finding.

## [0.1.0] - 2026-10-25

> **Historical release note.** The implementation in this release contained the
> core defects documented in `docs/core-validity-audit.md`. Its benchmark
> numbers are invalid as a fusion comparison and are superseded by the
> regenerated development benchmark. They are not reproduced or preserved as a
> baseline here.

### Added

- Synthetic 2D world with deterministic ground truth trajectories
- Range-bearing sensor model (range, bearing, range-rate) with configurable noise/delays/dropouts/false alarms
- Vision-bearing sensor model (bearing + class probabilities) with configurable behavior
- EKF-based tracking with constant velocity motion model and nonlinear measurement updates
- Gated nearest-neighbor data association
- Range-only baseline and fused tracking (sequential updates)
- Observer-pose propagation for correct measurements under motion
- Per-epoch track miss counting and explicit track lifecycle
- Evaluation metrics (position/velocity RMSE, track counts)
- CLI commands: `run`, `compare`, `benchmark`, `version`
- Reproducible benchmark workflow generating JSON, CSV, and Markdown reports
- Streamlit interactive workbench
- Comprehensive documentation (architecture, metrics, measurement models, limitations, technical walkthrough, FAQ, design decisions)
- Unit and integration tests (14 tests at release)

### Changed

- Hardened EKF with canonical update path, Joseph-form covariance correction, and angle wrapping
- Migrated Pydantic models to v2 ConfigDict
- Improved observer-pose handling throughout pipeline

### Notes

- Synthetic simulation only - no raw image processing, no real hardware/field validation
- Vision-only track initiation not performed (bearing alone insufficient for unique 2D position)
- Fusion does not universally improve performance; results depend on conditions
