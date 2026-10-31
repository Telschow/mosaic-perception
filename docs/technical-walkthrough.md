# Technical Walkthrough (5 min)

## 1) Problem and motivation

Combining imperfect sensor observations is not automatically beneficial.
Timing, noise, dropouts, miscalibration, false alarms and poor data association
can all make fusion worse than a single-sensor baseline. Mosaic studies this
trade-off in a controlled synthetic setting with paired comparisons.

## 2) Architecture (as implemented)

1. **Synthetic world** (`simulation/world.py`) — deterministic 2-D trajectories
   on an exact time grid, with analytic observer heading/velocity.
2. **Scenarios** (`scenarios.py`) — 16 presets that override sensor parameters
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
  logged and counted; in-flight observations are reported as pending. Admitted
  delayed observations are applied to the delivery-time state using the
  capture-time observer pose; no rewind/replay is done (displacement scale
  ~speed x age under constant velocity, not a strict bound).
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
  samples; identity switches; unmatched confirmed tracks; 95%/68% coverage with χ²(2, ·)
  thresholds; delivery statistics and mean AoI.
- **Honesty**: `track_fragmentation` is `N/A` only when no object is ever matched; undefined metrics are not
  fabricated zeros; the development-versus-held-out distinction is recorded.

## 5) Current development benchmark

From `artifacts/benchmark/report.md` (all 16 scenarios, development seeds 0–24,
10 s; see the artifact for the exact commit):

- Accuracy depends on the matcher. Paired position-RMSE differences (fused
  minus range-only, 25 seeds, 95% t interval over seeds) under the headline
  continuity-preferring matcher: favours fusion in 1 of 15 scenarios with defined
  accuracy, goes against it in 6, includes zero in 8. Under a distance-only matcher
  (`position_rmse_distance_only`) it favours fusion in 7, goes against it in 3 and
  includes zero in 5. Neither matcher settles the accuracy question.
- Association quality is worse for fusion under both matchers: precision, MOTA and
  GOSPA are worse in 14 of the scenarios with defined values (inconclusive in 1 to 2),
  IDF1 favours fusion in 2, goes against it in 5 and is inconclusive in 9, and recall is
  better in 12 of 16. Unmatched confirmed tracks
  are mostly duplicates (38.9 of 39.3 per seed in `uncertainty_miscalibration`), but
  not in `dense_clutter` (8.6 of 73.4).
- Identity switches depend on the matcher: continuity cuts the summed per-seed mean
  from 388.5 to 241.8 (about 38%) and changes the fused-versus-range ordering in some scenarios.
- Position NEES per degree of freedom is above its 95% interval in all 15 scenarios
  with defined values for both methods (overconfident); NIS per degree of freedom is
  below its interval in 13 (fused) and 14 (range-only), as expected for gated updates.
  Intervals are optimistic (correlated samples).
- Estimating the vision bias (`fused_bias_estimated`): in the three within-gate
  scenarios the final estimate is close to the configured bias (0.0101, 0.0149, 0.0199
  rad for 0.010, 0.015, 0.020) and, against plain fused, RMSE improves by 0.073, 0.113
  and 0.192 m, precision by 0.064, 0.110 and 0.131 and MOTA by 0.155, 0.297 and 0.359.
  Association quality stays below range-only (precision about 0.67 against 0.826); in
  the other scenarios the difference is inconclusive, and for the 0.12 rad bias the gate
  leaves about 1.3 updates per seed so nothing is learned.
- One-step-lag retrodiction (`delivery_delay_retrodiction`): better position accuracy and
  consistency than `delivery_delay` (position NEES per DOF 4.9 to 1.9 range-only, 11.3
  to 3.3 fused) but worse identity switches (6.9 to 11.1 and 5.1 to 13.0) and MOTA
  (0.708 to 0.636 and 0.437 to 0.349). The cause is not diagnosed; association still
  gates delayed observations against the delivery-time state.
- **Large bias, rejected by the gate vs. smaller bias, fused.**
  `sensor_disagreement_large_bias` (0.12 rad) shows the gate working: ~265 of
  ~275 delivered vision observations per seed are gate-rejected and the paired
  RMSE interval includes zero under both matchers. The three preregistered
  within-gate biases (0.010, 0.015, 0.020 rad) pass the gate for ~222-254
  observations per seed, and in each the fused estimate is worse than range-only
  (precision 0.617, 0.560, 0.535 vs 0.826; MOTA 0.332, 0.169, 0.092 vs 0.746; paired
  RMSE interval against fusion under both matchers). The vision acceptance table
  separates generated, delivered, gate-rejected, lost-competition,
  other-unassigned, stale/invalid and applied observations. None of these
  scenarios supports a claim about real-world sensor-fusion performance.
- `crossing_targets` and `dense_clutter` exercise association ambiguity and
  clutter under GNN only: in the crossing fused has lower MOTA (0.573 vs 0.804) and
  an RMSE interval that includes zero; in dense clutter fused precision is 0.338 vs
  0.816 and MOTA -0.977 vs 0.732.
- Coverage is not improved overall and remains far below 0.95 under reported
  covariance miscalibration (χ²(2, 0.95) = 5.991).
- The `stale_rejection` scenario has zero matched samples because stale
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
- Only development seeds have been run; a future frozen-code held-out run is
  needed before any generalization claim.
- Coverage remains poor under miscalibration; calibration is an open problem.
