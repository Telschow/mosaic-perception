# Design Decisions

- **Synthetic observations first**: start at detector outputs (range, bearing,
  range rate, class probabilities) rather than raw images or waveforms, so the
  workbench can focus on estimation, association, fusion and evaluation.
- **Range-bearing-only baseline**: the method identifier stays `range_only` for
  continuity, but the semantics are now explicit: vision observations are not
  enqueued or associated at all. The baseline cannot be influenced by the
  modality it is meant to exclude.
- **One measurement-frame convention**: bearings are sensor-frame angles (world
  line-of-sight minus observer heading, wrapped to `[-π, π]`); range rate is
  relative to observer velocity. Sensors, EKF, gating and initiation all use
  the same convention.
- **Observer pose at capture time**: observations carry position, heading and
  velocity. This is platform metadata, not object ground truth. It makes
  moving-observer measurement models correct and testable.
- **Per-group association**: range-bearing and vision groups are associated
  independently with gated Hungarian assignment. This permits one observation
  per group per track per epoch and makes sequential fusion possible, while
  preserving one-to-one matching inside each group.
- **Range first, then vision**: range-bearing updates establish/refresh tracks
  before bearings refine them. Only range-bearing observations may initiate
  tracks, because a bearing alone does not determine 2-D range.
- **One hit/miss accounting per epoch**: a track updated by either or both
  groups gets one hit; a track with no accepted update gets one miss. This
  avoids double-counting sensor updates and prevents failed updates from
  resetting misses.
- **Bounded-staleness queue**: observations are queued until delivery and
  applied at the next tracker epoch if their age is at most `dt + 1e-6`.
  Older observations are rejected with a logged reason and counted. Full
  out-of-sequence replay is deliberately not implemented rather than left
  ambiguous.
- **Canonical EKF**: single update path with analytic Jacobians, wrapped angle
  innovations, Joseph form, Cholesky innovation checks, covariance
  symmetrisation and PSD rejection.
- **Snapshot evaluation**: track snapshots are recorded during the run; the
  evaluator never reuses final states for historical timestamps.
- **One-to-one matching with an explicit gate**: at each timestamp, confirmed
  and coasting tracks are Hungarian-matched one-to-one to ground-truth objects
  with a 2.0 m Euclidean gate. This is simple, documented and testable.
- **Honest metrics**: recall and precision have explicit denominators;
  identity switches and unmatched confirmed tracks are computed; `track_fragmentation` is
  computed with a documented definition (matched-frame gaps); undefined metrics are
  `N/A`, never zero.
- **Chi-square coverage**: 95% coverage uses χ²(2, 0.95) = 5.991, not a
  hard-coded 0.85.
- **Determinism**: explicit seeds, deterministic IDs, paired runs, no
  wall-clock timestamps in artifacts, generated Markdown.
- **Development versus held-out seeds**: the checked-in benchmark uses
  development seeds 0–24. Held-out seeds 25–49 are reserved and were not run;
  no held-out claim is made.
- **Honest limitations**: document what is not modeled (raw sensing, occlusion,
  full out-of-sequence replay, advanced association, real calibration) rather
  than hiding it.
