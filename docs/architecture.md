# Architecture

## Overview

Mosaic is a layered synthetic perception pipeline with explicit contracts
between simulation, sensing, tracking, evaluation and reporting. The same
runner is used by the CLI, the Streamlit app and the tests.

## Components

### Domain layer (`src/mosaic_perception/domain/models.py`)

Pydantic contracts for vectors, poses, world state, sensor configuration,
observations, track estimates, per-epoch snapshots, delivery statistics,
scenario configuration and evaluation results.

Key properties:

- `Pose2D` carries position, heading and velocity; observations carry the
  observer pose at capture time.
- Ground truth lives in `WorldState`; `SensorObservation._true_object_id` is
  evaluator/simulator metadata and is cleared before estimation.
- `TrackSnapshot` records status, state, covariance, hit/miss counts and
  whether the track was updated in that epoch.
- `EvaluationResult` stores explicit sample counts and previously unsupported
  metrics as `None`, never as fabricated defaults.
- Angles are wrapped with `wrap_angle`.

### Simulation layer (`simulation/world.py`)

- Deterministic exact time grid (`0, dt, 2dt, ...`).
- Closed-form constant-velocity and circular trajectories.
- Analytic observer heading and velocity for moving observers.
- Unknown trajectory names are rejected.

### Scenario layer (`scenarios.py`)

- 10 named presets with sensor and observer overrides.
- Resolution into a fully expanded `ScenarioConfig` with independent copies of
  nested noise/bias dictionaries.
- Scenario names are validated by the CLI; ships no unused config files.

### Sensor layer (`sensors/`)

- `RangeBearingSensor`: range, sensor-frame bearing, range rate relative to
  observer velocity, covariance, optional bias and Poisson false alarms.
- `VisionBearingSensor`: sensor-frame bearing, class probabilities, detection
  confidence and Poisson false alarms.
- Both honour `frame_rate`, emit deterministic observation IDs
  (`<sensor_id>-000000`) and attach observer pose at capture time.
- Reported covariance scaling affects only what the filter is told, not the
  noise actually applied.

### Tracking layer (`tracking/`)

- `ekf.py`: constant-velocity EKF with discrete white-noise acceleration,
  sensor-frame measurement models, analytic Jacobians, wrapped innovations,
  Cholesky validation, Joseph-form updates and PSD checks.
- `association.py`: per-group gated Hungarian assignment. Range-bearing and
  vision groups are matched independently, one-to-one within each group.
- `tracker.py`:
  - pending delivery queue with bounded staleness and explicit rejection log;
  - prediction once per epoch, range-bearing association/update first, then
    vision association/update;
  - one hit per epoch if at least one observation was applied, one miss
    otherwise; rejected/failed updates do not count as hits;
  - deterministic track IDs, lifecycle confirm/coast/delete, per-epoch
    snapshots and delivery statistics;
  - no broad exception swallowing and no ground-truth identity use.

### Evaluation layer (`evaluation/frames.py`, `evaluation/metrics.py`)

`frames.py` matches evaluated tracks to ground truth once per frame and returns
one `FrameMatch` per world state. Every metric in `metrics.py` is a function of
that list, so a metric can be tested on hand-built frames; `TrackingEvaluator`
only orchestrates them.

- Snapshot-based, not final-state-based.
- One-to-one gated Hungarian matching per timestamp; confirmed/coasting only.
- Accuracy, recall/precision with explicit denominators, identity switches,
  unmatched confirmed tracks, coverage with χ²(2, 0.95) = 5.991 and χ²(2, 0.68), delivery
  statistics and per-frame diagnostics.
- `track_fragmentation` counts matched-to-unmatched-to-matched interruptions
  per ground-truth object, summed over objects.

### Experiment runner (`experiment.py`)

- Builds one world, then runs `range_only` and `fused` on the same states.
- Reuses the same range-sensor random stream; fused adds vision only.
- Clears evaluator-only object IDs before processing.
- Wraps the evaluator and optional git-commit metadata.

### Metric declarations (`evaluation/registry.py`, `reporting/tables.py`)

Every per-run metric is declared once (name and display precision) in
`registry.py`. The CSV columns, the cross-seed aggregates and the report
columns are derived from those declarations, and `reporting/tables.py` lists
the report tables as data. Adding a metric means one declaration, the code that
computes it, and a row in `docs/metrics.md` (a test fails if a declared metric
is undocumented).

### Reporting (`reporting/markdown.py`)

`render_report(payload)` is a pure function from the benchmark payload to
Markdown, independent of the command-line layer and testable on a hand-built
payload.

### CLI (`cli/main.py`)

- Commands: `run`, `compare`, `benchmark`, `evaluate`, `version`.
- Seed lists and ranges (`1,2,3`, `1-5`), scenario lists and `all`.
- Canonical output: `benchmark.json`, `per_seed.csv`, `report.md`.
- Deterministic JSON (sorted keys, no wall-clock timestamps).

### App (`app/streamlit_app.py`)

- Streamlit workbench using the shared `run_pair` runner and the same
  metrics/snapshots as the CLI.
- Shows ground truth and final confirmed/coasting tracks; it does not invent a
  separate evaluation path.

## Design principles

1. **Separation of concerns**: simulation, sensing, estimation and evaluation
   are independent and composable.
2. **Determinism**: explicit seeds, deterministic IDs, no UUIDs or wall-clock
   timestamps in artifacts.
3. **Explicit contracts and failure**: invalid inputs raise; stale and invalid
   observations are counted and logged.
4. **Ground-truth isolation**: truth is used by the simulator and evaluator, not
   by the tracker.
5. **Fair comparison**: paired worlds and random streams, identical management
   logic.
6. **Honesty about unsupported metrics and limitations**: `None`/`N/A` rather
   than plausible zeros.

## Data flow

```
SyntheticWorld (ground truth + observer pose/velocity)
        |
Sensors (observations: sensor-frame measurements, covariance, timing, pose)
        |
Pending queue (bounded staleness; explicit rejection)
        |
Tracker (predict -> range-bearing association/update -> vision -> lifecycle)
        |
Per-epoch TrackSnapshots + delivery statistics
        |
Evaluator (one-to-one gated matching against WorldState)
        |
JSON / CSV / Markdown / Streamlit
```
