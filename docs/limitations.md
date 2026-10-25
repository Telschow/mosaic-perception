# Limitations

## Scope

- Synthetic 2-D world with known ground truth.
- Point-measurement sensor abstractions: range, bearing, range rate, class
  probabilities. No raw images, waveforms, radar returns or LiDAR geometry.
- No occlusion, terrain, clutter map, multipath or realistic background.
- No hardware, field data, real-time execution or safety certification.
- The workbench studies estimation and association behavior, not operational
  perception performance.

## Estimation and association

- Constant-velocity motion model. Turning objects are approximated and can
  produce lag or bias.
- EKF linearisation and Gaussian assumptions are approximations.
- Association is gated Hungarian assignment within each measurement group, not
  MHT, JPDA or learned association. Ambiguous crossings and dense false alarms
  can still produce identity errors.
- Track initiation uses range-bearing observations only, with a simple
  velocity guess from range rate and observer velocity. Vision-only initiation
  is unsupported because a bearing does not determine range.
- `track_fragmentation` is not implemented and is reported as `None`/`N/A`.
- Class estimates are stored but not evaluated.

## Timing and delivery

- Observations older than one tracker epoch (`dt + 1e-6`) are explicitly
  rejected and counted; they are not replayed against historical state. The
  potential benefit of careful out-of-sequence fusion is therefore not
  measured.
- **Delayed-observation state alignment (bounded-staleness approximation):**
  Observations whose capture time is at most one epoch in the past are admitted
  to the tracker. When an observation is processed, the tracker has already
  predicted all tracks forward to the current processing time (the delivery
  epoch). The measurement geometry and observer pose refer to the observation's
  **capture time**, but the target state has been propagated to **delivery time**.
  The tracker applies the observation to this delivery-time state without
  rewinding to the capture time. This is a deliberate approximation, not a
  capture-time-aligned estimation.
  - Under a constant-velocity approximation, the target-state displacement
    between capture and delivery is approximately `speed × observation_age`.
    Acceleration and observer-motion effects are not accounted for in this
    approximation and require additional consideration.
  - The reported age of information (`mean_age_of_information`) reflects the
    time between capture and delivery, not the estimation alignment error.
  - Observations older than the staleness limit are rejected rather than
    replayed.
  - No claim of full out-of-sequence measurement fusion (retroactive state
    update) is justified by this implementation.
- Processing occurs on the discrete tracker epoch grid. Mean age of information
  is quantised by `dt` and is not a sub-epoch latency measurement.
- `delivery_delay` with a 0.05 s mean is generally applied at the next 0.1 s
  epoch, so its reported AoI is around 0.1 s.
- In-flight observations at the end of a run are reported as pending; they are
  not forced into the final state.

## Evaluation

- The checked-in benchmark uses **development seeds 1–5 only**. Seeds 25–49 are
  reserved and have not been run, so no held-out or generalization claim is
  made.
- Matching uses a 2.0 m Euclidean gate at each timestamp. Different gates can
  change precision, recall and the set of matched samples.
- Precision is defined per confirmed/coasting track sample, not per track
  object. The exact denominators are reported with every result.
- Precision is sample-based. Many unmatched confirmed tracks, notably in
  `uncertainty_miscalibration`, are duplicates: in at least one frame they were
  unmatched while a true object lay within the 2.0 m matching gate. The
  `num_duplicate_tracks` metric counts them. It depends on the matching gate
  and cannot tell a duplicate of the right object from a track that merely
  passed near one.
- The two sensor-disagreement scenarios are single, hand-chosen bias values on
  a synthetic world. `sensor_disagreement_large_bias` (0.12 rad) mainly tests
  gate rejection (most, but not all, biased observations are rejected: see the
  vision acceptance table). `sensor_disagreement_within_gate` (0.015 rad) was
  fixed in advance, not tuned, and measures the effect of fusing accepted
  biased observations. Neither generalizes to real sensors.
- Coverage is empirical and only defined over matched samples. It is not a
  detection or association calibration metric.
- Reported covariance can be badly miscalibrated. In the checked-in
  `uncertainty_miscalibration` scenario, 95% coverage is roughly 0.12–0.14
  rather than 0.95.
- The benchmark shows only small position-RMSE differences between methods,
  while fused precision is lower in every scenario with defined precision.
  Accuracy alone is not
  evidence that fusion improved the tracker.
- The `out_of_sequence` scenario has no matched samples because its observations
  exceed the staleness bound and are rejected. Accuracy is `N/A`; this is an
  explicit non-result, not a zero-error result.

## Reproducibility boundaries

- Results are deterministic for a fixed code commit, Python/dependency
  environment, seed set and configuration. They are not guaranteed to be
  byte-identical across dependency upgrades or platforms.
- Wall-clock timing is not recorded, so the artifacts cannot be used for
  runtime performance claims.
- The benchmark is generated from code, but its interpretation still depends on
  the documented matching gate, statuses and staleness policy.

## Superseded claims

The v0.1.0 benchmark and release checklist were produced before the correctness
repair. They contained a shared assignment slot across modalities, a
sensor/world bearing mismatch, ignored observer velocity, discarded delayed
observations and an evaluator that reused final track states. Their numbers are
invalid as a fusion comparison and are not preserved as a baseline. See
[core-validity-audit.md](core-validity-audit.md).

In particular, this project does **not** claim:

- that fusion is universally better or worse;
- that the tracker is calibrated;
- that results transfer to real sensors;
- that held-out performance has been measured.

## Type checking and CI

- Supported CI (`.github/workflows/ci.yml`) runs, on Python 3.12:
  `ruff check src tests`, `ruff format --check .` (full tree), `mypy src`,
  `pytest`, and smoke tests of `mosaic run`, `evaluate`, `compare` and
  `benchmark` (the last two also check that the three canonical artifacts are
  written).
- Type checking uses `scipy-stubs` from the dev dependencies; no
  `type: ignore` comments or config-level suppressions are used for the source
  package.
