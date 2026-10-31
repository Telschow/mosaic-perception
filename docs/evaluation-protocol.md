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
- The reserved seeds come from the same generator, scenarios and code as the
  development seeds. A held-out run is therefore only as blind as the freeze
  discipline around it (code, scenarios and metrics frozen first, run once, no
  changes afterwards); it is not blind in the sense of a hidden test set, and it
  says nothing about other generators or real data.

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
5. Run the `fused_bias_estimated` tracker (the same observations, with an estimated
   vision bearing bias removed before gating and updating).
6. Evaluate all three against the same ground-truth states using per-epoch
   snapshots.
7. Repeat over seeds and aggregate with mean and sample standard deviation;
   also report per-metric paired differences (fused minus range-only, and
   fused-bias-estimated minus fused) with a
   two-sided 95% t interval over seeds. The interval describes seed-to-seed
   variation, not generalisation, and macro means across heterogeneous
   scenarios are not reported.

The fused run adds vision observations only; it does not receive a different
world or a different range-sensor stream. Tracker management parameters are
identical between methods.

## Evaluation

- Candidate tracks: `CONFIRMED` and `COASTING` snapshots only.
- Matching: one-to-one Hungarian assignment per timestamp with a 2.0 m
  Euclidean gate, preferring each object's previous track while it stays inside
  the gate. Distance-only identity switches are reported alongside.
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

## Reproducibility checks in CI

Two checks run on every push and pull request alongside the test suite.

**Golden benchmark** (`scripts/check_benchmark_golden.py`, `make
benchmark-golden-check`). Regenerates a small fixed benchmark — scenarios
`nominal` and `sensor_disagreement_within_gate`, seeds 0 and 1, 2.0 s duration,
2 objects — into a temporary directory and compares all three outputs
(`benchmark.json`, `per_seed.csv`, `report.md`) against the committed copies in
`artifacts/benchmark-golden/`. Any nondeterminism or silent behaviour change
fails the build.

The structured outputs are compared field by field rather than byte for byte.
Integer, string, boolean and structural fields (keys, row and column counts)
must match exactly; float fields are compared with a tight relative tolerance
of `1e-9` (with a `1e-12` absolute tolerance for values at or near zero).
Byte-for-byte equality was relaxed because the same code produces
floating-point/BLAS noise in the last one or two digits on different platforms
— e.g. `anees_position` `4.2417037447519625` on Linux CI versus
`4.24170374475195` on macOS arm64. That noise is ~`1e-15` relative, six orders
of magnitude below the tolerance, so it no longer fails the check, while any
real change in a count, identity, structure or value stays far above the
tolerance and still fails. `report.md` is unstructured and its numbers are
rounded for display, so it remains a byte-for-byte comparison.

The recorded source commit differs on every commit by design, so both sides
have 40-hex commit hashes replaced by a placeholder before comparison; commit
correctness is the provenance check's job. When an output change is intended,
refresh the goldens with the one-command step `make benchmark-golden` and
commit the result.

**Artifact provenance** (`scripts/check_artifact_provenance.py`, `make
provenance-check`). Reads `artifacts/benchmark/benchmark.json` and verifies
that the recorded source commit exists and is an ancestor of `HEAD`, that no
artifact-producing source has changed since that commit, and that the recorded
package version still matches `pyproject.toml`. The artifact-producing source
set is `src/` — the package that generates the numbers. Tests, documentation,
workflows and dependency manifests are excluded because they cannot change
generated values; a dependency change that does change values is caught by the
golden benchmark check.

Either check failing means the committed benchmark artifact no longer
describes this tree: regenerate with `make benchmark` and commit the refreshed
artifacts (and, for the golden check, `make benchmark-golden` if the change is
intended).

## What this protocol does not establish

- Real-sensor, hardware or field performance.
- Generalization beyond the synthetic world and the tested scenarios.
- That fusion is universally better or worse.
- That the reported covariances are calibrated outside the measured scenarios.

The published v0.1.0 benchmark violated this protocol (single assignment slot
shared by modalities, frame mismatch, final-state evaluation). Its numbers are
superseded and must not be cited as a baseline.
