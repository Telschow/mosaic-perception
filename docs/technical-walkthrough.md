# Technical Walkthrough (5 min)

## 1) Problem and motivation

Combining imperfect sensor observations is not automatically beneficial.
Timing, noise, dropouts, miscalibration, false alarms and poor data association
can all make fusion worse than a single-sensor baseline. Mosaic studies this
trade-off in a controlled synthetic setting with paired comparisons.

## 2) Architecture (as implemented)

1. **Synthetic world** (`simulation/world.py`) — deterministic 2-D trajectories
   on an exact time grid, with analytic observer heading/velocity.
2. **Scenarios** (`scenarios.py`) — 10 presets that override sensor parameters
   or the observer trajectory.
3. **Sensors** (`sensors/*`) — range-bearing (range, sensor-frame bearing,
   relative range rate) and vision-bearing (bearing + class probabilities).
   Observations include capture/delivery times, covariance and observer pose.
   Frame rate is honoured; IDs are deterministic.
4. **Tracking** (`tracking/*`) — constant-velocity EKF, per-group gated
   Hungarian association, pending delivery queue, sequential range-then-vision
   updates, lifecycle management and per-epoch snapshots.
5. **Evaluation** (`evaluation/metrics.py`) — one-to-one gated matching against
   ground truth using snapshots, with explicit denominators and χ² coverage.
6. **Runner/CLI/UI** (`experiment.py`, `cli/`, `app/`) — paired execution,
   reproducible artifacts and Streamlit workbench.

## 3) Technical choices and trade-offs

- **EKF**: analytic Jacobians, wrapped angle innovations, Joseph-form updates,
  Cholesky innovation checks and PSD rejection. Constant-velocity motion with
  discrete white-noise acceleration.
- **Observer pose**: each observation carries the observer pose at capture
  time, including velocity. A nonzero heading or moving observer is handled by
  the measurement model, not patched later.
- **Association**: independent gated Hungarian assignments for range-bearing
  and vision groups. One range and one vision observation may update the same
  track in one epoch. Within a group, matching is one-to-one.
- **Hit/miss accounting**: one hit per updated epoch; a miss when no update was
  accepted. Rejected or failed updates do not count as hits and do not reset
  misses.
- **Timing**: bounded one-epoch staleness. Older observations are rejected,
  logged and counted; in-flight observations are reported as pending.
- **Simplicity over completeness**: 2-D, point-measurement sensor models, no
  raw images, no occlusion, no MHT/JPDA, no full out-of-sequence replay.

## 4) Evaluation strategy

- **Paired comparison**: same world states and the same range-sensor random
  stream per seed; the fused run only adds vision observations.
- **Snapshots**: evaluation uses per-epoch track snapshots, never final states
  replayed backwards.
- **Matching**: confirmed/coasting tracks only; one-to-one Hungarian assignment
  per timestamp with a 2.0 m Euclidean gate.
- **Metrics**: position/velocity RMSE over matched samples; recall over all
  ground-truth object samples; precision over all confirmed/coasting track
  samples; identity switches; false tracks; 95%/68% coverage with χ²(2, ·)
  thresholds; delivery statistics and mean AoI.
- **Honesty**: `track_fragmentation` is `None`/`N/A`; undefined metrics are not
  fabricated zeros; the development-versus-held-out distinction is recorded.

## 5) Current development benchmark

From `artifacts/benchmark/report.md` (all 10 scenarios, development seeds 1–5,
10 s; see the artifact for the exact commit):

- Fused position RMSE is lower in 6 of the 9 scenarios with defined accuracy,
  within 0.01 m in 3, and worse in none. Differences are small.
- Fused precision is lower in every scenario with defined precision; vision
  adds more confirmed tracks than it resolves.
- Coverage is not improved overall and remains far below 0.95 under reported
  covariance miscalibration (χ²(2, 0.95) = 5.991).
- The `out_of_sequence` scenario has zero matched samples because stale
  observations are rejected; accuracy is `N/A`.
- These are development results, not a held-out evaluation. Seeds 25–49 were
  not run.

The published v0.1.0 benchmark came from code with a shared association slot
across modalities, a bearing-frame mismatch, ignored observer velocity and
final-state evaluation. Its numbers are invalid and have been superseded; see
`docs/core-validity-audit.md`.

## 6) Limitations and next steps

- Synthetic only; no hardware or field validation.
- Constant-velocity model; turning targets are approximated.
- Vision-only initiation is unsupported.
- Stale observations are rejected, not replayed; stale-data fusion is not
  evaluated.
- `track_fragmentation` is unimplemented.
- Only development seeds have been run; a future frozen-code held-out run is
  needed before any generalization claim.
- Coverage remains poor under miscalibration; calibration is an open problem.
