# Roadmap

> For current state see [implementation-status.md](implementation-status.md)
> and the [comprehensive audit](audits/mosaic-perception-comprehensive-audit.md).
> Sections below that describe an earlier state are superseded.

## v0.1.0 (published, superseded)

- [x] Synthetic world generation
- [x] Range-bearing sensor model
- [x] Vision-bearing sensor model
- [x] EKF tracking
- [x] Gated nearest-neighbor association
- [x] Range-only baseline
- [x] Fused tracking
- [x] Basic evaluation metrics
- [x] CLI interface
- [x] Streamlit workbench
- [x] Basic documentation
- [x] Unit tests
- [x] CI workflow

## Correctness and evaluation repair (current branch, unreleased)

- [x] Per-group gated Hungarian association; one track may receive range and
      vision in the same epoch
- [x] Range-only mode ignores vision completely
- [x] One explicit sensor-frame measurement convention across sensors, EKF,
      gating and initiation
- [x] Observer heading and velocity support; real moving-observer tests
- [x] Sequential EKF updates with Joseph form, wrapped angles and PSD checks
- [x] Pending delivery queue with documented stale-rejection policy
- [x] Frame-rate honoring
- [x] Snapshot-based evaluation with one-to-one gated matching
- [x] Explicit metric denominators; χ²(2, 0.95) = 5.991 coverage
- [x] `track_fragmentation` computed with a documented definition
- [x] Deterministic IDs and artifact generation
- [x] Paired same-world/same-range-stream comparison
- [x] Implemented `mosaic evaluate`
- [x] 77 tests, Ruff clean, locked CI with tests
- [x] Regenerated development benchmark; old numbers declared invalid

## Next (not done here)

- [ ] Run the reserved held-out seeds 25–49 once, after freezing code and
      protocol, and report them separately
- [ ] Add out-of-sequence historical replay and measure stale-data fusion
- [ ] Investigate why fused precision and false-track counts are worse
- [ ] Improve calibration under reported-covariance miscalibration
- [ ] Add an oracle-association diagnostic to separate association errors from
      estimation errors
- [ ] Multi-object crossing scenarios and association stress tests
- [ ] Optional 3-D extension
- [ ] Performance profiling without mixing it with correctness claims

## Out of scope

- Real sensor integration
- Deep learning
- Military/tactical applications
- Ego-navigation (see contested-nav)
- C2/operator systems (see nav-trust-c2)
