# Measurement Models

## Frames and conventions

- **World frame**: global 2-D coordinates used by ground truth and track state.
- **Sensor frame**: origin at the observer position, rotated by the observer
  heading.
- The tracker state is `[x, y, vx, vy]` in the world frame.
- A bearing measurement is the world line-of-sight angle **minus the observer
  heading**, wrapped to `[-π, π]`.
- Range rate is the line-of-sight relative velocity, i.e. object velocity minus
  observer velocity.
- Every observation carries the observer pose at capture time: position,
  heading and velocity. This is platform metadata, not object ground truth.

The same convention is used by sensor generation, the EKF measurement models,
gating/association and track initiation. There is no second "world bearing"
interpretation hidden in the update path.

## Range-bearing sensor

For object position `p`, observer position `s`, observer heading `ψ`, object
velocity `v` and observer velocity `v_s`:

```
r      = ||p - s||
bearing = wrap(atan2(p_y - s_y, p_x - s_x) - ψ)
range_rate = ((p - s) · (v - v_s)) / r
```

Implementation details not shown in the formulas: the measured range is floored
at 0.1 m *before* the configured range bias is added (so a floored sample sits at
0.1 m + bias and the noise is no longer Gaussian within about 1 m of the observer);
objects closer than 1e-6 m to the observer are skipped; and `frame_rate` is
quantised to the simulation tick (the sensor emits on the first tick at least one
period after its last emission, so a rate that does not divide the tick rate
emits less often than configured).

The measurement vector is `[range, bearing, range_rate]`, with a diagonal
covariance in sensor units: m², rad² and (m/s)². Gaussian noise and optional
constant bias are applied in those units.

The EKF prediction of the same vector uses the observer pose on the
observation, so a nonzero heading or a moving observer produces the correct
predicted measurement. The analytic Jacobian is checked against central finite
differences, including a moving observer with nonzero velocity.

An observation may omit `range_rate`; the tracker then uses a two-dimensional
`[range, bearing]` update with the corresponding covariance block. Track
initiation requires at least range and bearing.

## Vision-bearing sensor

The vision-like sensor reports:

```
bearing = wrap(atan2(p_y - s_y, p_x - s_x) - ψ)
```

plus class probabilities and a detection confidence. It does **not** report
range. A single bearing does not determine a unique 2-D position, so
vision-only observations never initiate tracks. When fusion is enabled they can
update an existing track; in `range_only` mode they are not even enqueued.

Classification output is not evaluated by the tracking metrics. Class
confidence is not state-estimation uncertainty.

## Reported versus true noise

`reported_cov_scale` scales only the **reported** covariance, not the noise
actually applied to measurements. This is how the `uncertainty_miscalibration`
scenario makes the filter overconfident while keeping the measurement stream
otherwise comparable.

## Timing

Each observation has:

- `capture_time`: when the measurement was taken;
- `delivery_time`: when it becomes available to the tracker.

The tracker holds observations in a pending queue until delivery. At each
epoch it processes due observations sorted by `(delivery_time, capture_time,
observation_id)`. An observation whose capture time is more than one tracker
epoch (`dt + 1e-6`) in the past is rejected with a logged stale reason and
counted in `rejected_out_of_sequence`. It is not replayed. In-flight
observations at the end of the simulation are reported as
`pending_observations`.

**Delayed-observation state alignment (bounded-staleness approximation):**
When an observation is processed, the tracker has already predicted all tracks
forward to the current processing time (the delivery epoch). The measurement
geometry and observer pose refer to the observation's **capture time**, but the
target state has been propagated to **delivery time**. The tracker applies the
observation to this delivery-time state without rewinding to the capture time.
This is a deliberate approximation, not a capture-time-aligned estimation.

An opt-in alternative, one-step-lag retrodiction (`delayed_update="retrodiction"`),
replays the epoch from the stored previous posterior in capture-time order, which
removes this approximation for observations up to one epoch old. See
`docs/limitations.md` for what it does and does not cover.

- Under a constant-velocity approximation, the target-state displacement
  between capture and delivery is approximately `speed × observation_age`.
  Acceleration and observer-motion effects are not accounted for in this
  approximation and require additional consideration.
- The reported age of information (`mean_age_of_information`) is measured at
  tracker processing time (`now - capture_time`), not at `delivery_time`, so it
  is quantised by the tick phase: capture 0.0, delivery 0.01, processed at 0.1
  reports 0.1. The one-epoch staleness rule uses the same quantity. It is not
  the estimation alignment error.
- Observations older than the staleness limit are rejected rather than
  replayed.
- No claim of full out-of-sequence measurement fusion (retroactive state
  update) is justified by this implementation.

This is a bounded-staleness approximation, not a full out-of-sequence
historical replay.

## Association gates

Association is performed separately for each measurement group, with gates
selected by the actual measurement dimension:

- range-bearing, 3-DOF (range, bearing, range rate): χ²(3, 0.95) ≈ 7.815;
- range-bearing, 2-DOF (range, bearing only): χ²(2, 0.95) ≈ 5.991;
- vision-bearing, 1-DOF (bearing only): χ²(1, 0.95) ≈ 3.841.

Within a group the assignment is a one-to-one Hungarian assignment on gated
Mahalanobis distance. The same track may receive one observation from each
group in the same epoch; updates are applied range-bearing first, then vision.
Unmatched range-bearing observations may initiate tracks. Unmatched vision
observations are unused (and are not labelled as rejected detections).
