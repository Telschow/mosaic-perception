# Evaluation Protocol

## Objective

Determine, under controlled synthetic conditions, when adding vision-like
bearings to a range-bearing tracker improves state estimation, association
quality or uncertainty calibration, and when it does not.

## Hypotheses

1. With calibrated sensors and adequate detections, vision bearings may reduce
   position error relative to the range-bearing baseline.
2. Dropouts, systematic bias, miscalibrated covariance and false alarms can
   reverse or erase that benefit.
3. Improved accuracy does not imply improved association precision or
   calibration; those must be reported separately.
4. Rejecting stale observations rather than replaying them can make a
   timing-degraded scenario unscoreable on accuracy. That is a valid outcome,
   not a result to hide.

## Seeds

- **Development seeds**: 0–24. The checked-in benchmark uses **all 25** (0–24).
- **Reserved held-out seeds**: 25–49. They have **not** been run for this
  repair. No held-out result or generalization claim is made.
- The benchmark artifact records its seed group and the exact seed list.

Development results include choices made while repairing the code. They are
useful for debugging and regression detection, not for a confirmatory claim.
A future release should run the reserved seeds once, after the code and
protocol are frozen, and report them separately.

## Paired design

For each scenario and seed:

1. Generate one deterministic world (ground truth plus observer trajectory).
2. Build independent sensor random streams. The range-sensor stream is reused
   for both methods.
3. Run the `range_only` tracker (vision observations not enqueued).
4. Run the `fused` tracker (range plus vision observations).
5. Evaluate both against the same ground-truth states using per-epoch
   snapshots.
6. Repeat over seeds and aggregate with mean and sample standard deviation;
   also report per-metric paired differences (fused minus range-only) with a
   two-sided 95% t interval over seeds. The interval describes seed-to-seed
   variation, not generalisation, and macro means across heterogeneous
   scenarios are not reported.

The fused run adds vision observations only; it does not receive a different
world or a different range-sensor stream. Tracker management parameters are
identical between methods.

## Evaluation

- Candidate tracks: `CONFIRMED` and `COASTING` snapshots only.
- Matching: one-to-one Hungarian assignment per timestamp with a 2.0 m
  Euclidean gate.
- Accuracy: position and velocity RMSE over matched samples.
- Association: recall over all ground-truth object samples; precision over all
  confirmed/coasting track samples; identity switches and unmatched confirmed tracks.
- Calibration: 95% and 68% empirical coverage using χ²(2, ·) thresholds.
- Delivery: delivered, rejected, out-of-sequence, invalid, pending and mean AoI.

Definitions and denominators are in [metrics.md](metrics.md).

## Reporting

- Every artifact records package version, git commit, scenario configuration,
  seed list, duration, step size, object count, methods, gates and protocol.
- No wall-clock timestamps are written; repeated runs with the same commit and
  seed list are byte-identical.
- `N/A` is used for undefined metrics. Undefined metrics, such as
  `track_fragmentation` when no object is ever matched, are explicitly `None`.
- Canonical artifacts are `benchmark.json`, `per_seed.csv` and `report.md` under
  the output directory (default `artifacts/benchmark/`).
- The report states whether the seeds are development or held-out and whether
  the held-out range was run.

## What this protocol does not establish

- Real-sensor, hardware or field performance.
- Generalization beyond the synthetic world and the tested scenarios.
- That fusion is universally better or worse.
- That the reported covariances are calibrated outside the measured scenarios.

The published v0.1.0 benchmark violated this protocol (single assignment slot
shared by modalities, frame mismatch, final-state evaluation). Its numbers are
superseded and must not be cited as a baseline.
