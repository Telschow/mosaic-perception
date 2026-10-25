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
  MHT, JPDA, random-finite-set or learned association; those are out of scope
  for this workbench. The `crossing_targets` (one crossing of a few targets)
  and `dense_clutter` scenarios exercise ambiguity and clutter, but only for
  global-nearest-neighbour association, so no claim is made about how other
  associators would compare. The other scenarios use sparse, well-separated
  targets, and their association results should be read as such.
- Track initiation uses range-bearing observations only, with a simple
  velocity guess from range rate and observer velocity. Vision-only initiation
  is unsupported because a bearing does not determine range.
- `track_fragmentation` counts gaps in an object's matched frames (not track
  breaks as such): a gap of one or more evaluated frames between two matched
  frames is one interruption, regardless of which track resumes. It is `N/A`
  when no object is ever matched and says nothing about identity (see
  `identity_switches`).
- Duplicate-track counts depend on the matching gate. In the development
  benchmark the fused count in `uncertainty_miscalibration` was 34.2, 38.9 and
  39.3 per seed at 1, 2 and 3 m, but in `measurement_bias` it was 0.0, 1.8 and
  5.7, so the choice of gate changes both the size and the ranking of the
  effect. None of the gates is validated as the right one.
- Class accuracy is evaluated over matched samples with a known estimate and a
  known true class only. Classes come from a synthetic confusion model, so the
  number says nothing about real classifiers; range-only runs have no class
  information (`N/A`). The scenario value is an unweighted mean of per-seed
  accuracies and can rest on very few samples: in
  `sensor_disagreement_large_bias` only 12.8 samples per seed are classified
  (7 of 25 seeds have any, 4.3% of matched samples), so its unweighted 0.429 is
  not a precise estimate; the pooled value is 0.320. The report shows the
  unweighted mean, the pooled accuracy and the classified fraction side by side.

## Timing and delivery

- Observations older than one tracker epoch (`dt + 1e-6`) are explicitly
  rejected and counted; they are not replayed against historical state, in
  either update mode. Fusion of observations older than one epoch is therefore
  not measured.
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
  - Measured effect of acceleration (deterministic test, age 0.1 s, target at
    5 m/s accelerating laterally): the stale capture-time measurement leaves a
    0.25 m along-track error against truth at the processing epoch, about half
    of speed x age, for every acceleration tested (0 to 100 m/s²). Unmodelled
    lateral acceleration adds a lateral position error of a·τ²/2 (0.02 m at
    4 m/s², 0.5 m at 100 m/s²) and a velocity error of a·τ. For this age,
    acceleration only exceeds the along-track term above about 50 m/s². These
    are results for one geometry and one covariance, not a bound.
  - **Opt-in one-step-lag retrodiction** (`delayed_update="retrodiction"`, scenario
    `delivery_delay_retrodiction`): the tracker stores each track's posterior from
    before the last prediction step and, when a delayed observation is applied,
    replays that epoch in capture-time order (predicting over the exact intervals
    between observations) before predicting to the processing time. For the
    observations it admits (age up to one epoch) this removes the delivery-time
    approximation: a hand-built test reproduces the independently computed replay
    exactly and removes the 0.25 m along-track error, leaving only the unmodelled
    acceleration. It still gates the observation against the delivery-time state
    (association is not retrodicted), it is off by default, and it covers only the
    one-epoch lag, so it is not general out-of-sequence measurement fusion.
- Processing occurs on the discrete tracker epoch grid. Mean age of information
  is quantised by `dt` and is not a sub-epoch latency measurement.
- `delivery_delay` with a 0.05 s mean is generally applied at the next 0.1 s
  epoch, so its reported AoI is around 0.1 s.
- In-flight observations at the end of a run are reported as pending; they are
  not forced into the final state.

## Evaluation

- The checked-in benchmark uses **development seeds 0–24 only**. Seeds 25–49 are
  reserved and have not been run, so no held-out or generalization claim is
  made.
- Position RMSE also depends on the matcher: the continuity preference can keep an
  object paired with a farther duplicate track, which raises RMSE, while a
  distance-only matcher picks the nearest track and flatters accuracy when
  duplicates exist. Both are reported (`position_rmse`,
  `position_rmse_distance_only`) with paired differences, and neither matcher
  is ground truth.
- Identity switches depend on the matcher: a distance-only matcher flipped between
  nearby tracks and reported about 38% more switches than the continuity-preferring
  matcher adopted as the headline (351.6 vs 217.6, summed per-seed means over the 15
  development scenarios and both methods), and it reversed the fused-versus-range
  ordering in some scenarios. Both counts are reported; neither is ground truth
  about the tracker's identity behaviour.
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
- Estimator consistency is reported as NEES (matched samples only, so conditioned
  on the 2 m gate) and NIS (every applied update, truncated by gating), each per
  degree of freedom with a chi-square interval. The intervals treat samples as
  independent although samples within a track are correlated, so they are
  optimistic; the report shows how many ground-truth samples the gate excludes.
- Coverage is empirical and only defined over matched samples. It is not a
  detection or association calibration metric.
- Reported covariance can be badly miscalibrated. In the checked-in
  `uncertainty_miscalibration` scenario, 95% coverage is roughly 0.12–0.14
  rather than 0.95.
- The benchmark shows only small position-RMSE differences between methods,
  while fused precision is lower in every scenario with defined precision.
  Accuracy alone is not
  evidence that fusion improved the tracker.
- The `stale_rejection` scenario has no matched samples because its observations
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
  `benchmark` (the last two check that the three canonical artifacts are
  written; `benchmark` runs three scenarios, checks each appears in the report
  and checks that an unknown scenario name is rejected).
- Type checking uses `scipy-stubs` from the dev dependencies; no
  `type: ignore` comments or config-level suppressions are used for the source
  package.
