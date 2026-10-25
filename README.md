# Mosaic

**A reproducible workbench for multi-sensor perception, object tracking and uncertainty.**

Mosaic is a deterministic synthetic workbench for investigating a narrow but important question: *when does combining noisy, asynchronous sensor observations improve an estimate of a moving object's state, and when can fusion make the result worse?*

It compares a **range-bearing-sensor-only baseline** (method identifier `range_only`, no vision at all) with a **fused** method that adds vision-like bearing observations. Both methods run on the same worlds and the same range-sensor random streams, so the comparison is paired rather than a comparison of two unrelated runs.

## What is implemented

- Deterministic 2-D synthetic worlds with known ground truth and optional moving observer.
- Range-bearing sensor: range, sensor-frame bearing, range rate relative to observer velocity.
- Vision-like bearing sensor: bearing plus class probabilities (classification is not evaluated).
- Per-epoch track snapshots used for evaluation; final states are never replayed backwards.
- Constant-velocity EKF with sensor-frame measurement models, wrapped angular innovations, Joseph-form covariance updates and positive-semidefinite checks.
- Per-group association: one-to-one gated Hungarian assignment **within** the range-bearing group and **within** the vision group. A track may therefore receive one range-bearing and one vision update in the same epoch, applied sequentially.
- Pending delivery queue with a documented one-epoch staleness policy. Older observations are explicitly rejected and counted, never silently dropped.
- Deterministic IDs, explicit delivery/rejection statistics, and no ground-truth identities in the tracker.
- Hand-constructed evaluator tests with exact expected values, plus end-to-end regression tests.
- Reproducible benchmark artifacts generated from code: JSON, CSV and Markdown.

## Quickstart

```bash
git clone https://github.com/Telschow/mosaic-perception.git
cd mosaic-perception
uv sync --all-extras
```

With `uv`, every command below can be run as `uv run mosaic ...`. A plain
`pip install -e ".[dev]"` also works.

### Run one scenario

```bash
uv run mosaic run --scenario nominal --seed 42
```

### Compare across seeds

```bash
uv run mosaic compare --scenario nominal --seeds 1,2,3,4,5
```

### Generate the benchmark / evaluation artifacts

```bash
uv run mosaic benchmark --scenario all --seeds 0-24 --duration 10.0
```

`mosaic evaluate` is implemented and writes the same canonical artifacts as
`benchmark` (they differ only in the recorded command name):

```bash
uv run mosaic evaluate --scenario all --seeds 0-24 --output results/
```

### Interactive workbench

```bash
uv run streamlit run app/streamlit_app.py
```

## Association and fusion semantics

For every tracker epoch:

1. Predict all active tracks once.
2. Admit due observations from the pending queue, rejecting observations older
   than `dt + 1e-6` seconds with an explicit `stale` reason.
3. Associate the range-bearing group with a gated Hungarian assignment
   (χ²(3, 0.95) gate on Mahalanobis distance) and apply updates.
4. Associate the vision group independently (χ²(1, 0.95) gate) and apply
   updates to tracks that survived step 3.
5. Count one hit for a track updated by at least one group, and count a miss
   otherwise. Rejected or failed updates do **not** count as hits and do not
   reset misses.

Unmatched range-bearing observations may initiate tracks. Vision-only
observations cannot initiate tracks because a bearing alone does not determine
range in 2-D. In `range_only` mode vision observations are not enqueued at all,
so they cannot influence association, track initiation, hits, misses, or state.

## Evaluation protocol

At every ground-truth timestamp, confirmed and coasting track **snapshots** are
matched one-to-one to ground-truth objects with a gated Hungarian assignment
(2.0 m Euclidean gate by default) that prefers each object's previous track
while it stays inside the gate; `identity_switches_distance_only` reports the
count without that preference. Tentative and deleted tracks are excluded.
Metrics and denominators:

- **Position / velocity RMSE**: over matched samples only.
- **Recall**: matched samples / all ground-truth object samples.
- **Precision**: matched samples / all confirmed-or-coasting track samples.
- **Identity switches**: changes of matched track ID for the same object
  between consecutive matched frames.
- **Unmatched confirmed tracks** (`num_unmatched_confirmed_tracks`): confirmed tracks that were never matched to a true object. Many appear to be duplicates near true objects, so this is not a count of spurious objects.
- **95% / 68% coverage**: matched position errors against the reported 2×2
  position covariance, using χ²(2, 0.95) = 5.991 and χ²(2, 0.68) ≈ 2.279.
- **Age of information**: mean processing age of observations admitted by the
  staleness policy.
- **Track fragmentation**: interruptions in an object's matched frames (a gap
  of one or more frames between two matched frames counts once), summed over
  objects; `N/A` if no object is ever matched, never a fabricated zero.

Full definitions, matching rules and denominators are in
[docs/metrics.md](docs/metrics.md) and
[docs/evaluation-protocol.md](docs/evaluation-protocol.md).

## Current development benchmark

The checked-in benchmark is generated with `--scenario all --seeds 0-24
--duration 10.0`, i.e. **all 25 development seeds and no held-out seed**. The reserved held-out range
25–49 has **not** been run, and no held-out claim is made. When it is run, it
will only be as blind as the freeze discipline around it: the reserved seeds
come from the same generator and code, so it is not a hidden test set.

See [artifacts/benchmark/report.md](artifacts/benchmark/report.md) for the
generated tables and [artifacts/benchmark/benchmark.json](artifacts/benchmark/benchmark.json)
for the machine-readable record (protocol, per-seed metrics, git commit).
Headline observations from the current development benchmark:

- **Accuracy depends on the matcher.** Paired position-RMSE differences (fused
  minus range-only, 25 seeds, 95% t interval over seeds) under the headline
  continuity-preferring matcher: the interval excludes zero in favour of fusion
  in 1 of the 14 scenarios with defined accuracy, against fusion in 5, and
  includes zero in 8. Under a distance-only matcher (reported alongside as
  `position_rmse_distance_only`) it favours fusion in 7, goes against it in 3
  and includes zero in 4. The continuity preference can keep an object paired
  with a farther duplicate track, which fused runs have more of, so neither
  matcher settles whether fusion improves accuracy. No macro mean over
  scenarios is reported.
- **Association quality is worse for fusion under both matchers.** Fused
  precision, MOTA and GOSPA are worse (interval excludes zero) in 13 of the 14
  scenarios with defined values, and the remaining one or two are inconclusive.
  Recall is better for fusion in 11 and inconclusive in 4. IDF1 favours fusion
  in 2, goes against it in 5 and is inconclusive in 8. Precision is sample-based
  (matched samples / all confirmed-or-coasting track samples), and the extra
  "unmatched confirmed tracks" are confirmed tracks never matched to a true
  object. The report's `Duplicate tracks` column counts those that were left
  unmatched while a true object lay inside the 2 m matching gate: most are
  duplicates in most scenarios (for example 38.9 of 39.3 per seed in
  `uncertainty_miscalibration`), but in `dense_clutter` only 8.6 of 73.4.
- Identity switches also depend on the matcher: the continuity preference cuts
  the summed per-seed mean from 351.6 to 217.6 (about 38%) and changes the
  fused-versus-range ordering in some scenarios (for example `nominal`: 6.1 for
  range-only and 4.7 for fused with continuity, 8.9 and 10.6 distance-only).
- **Consistency.** Position NEES per degree of freedom is above its 95% interval
  in all 14 scenarios for both methods (overconfident; for example 1.85 range-only
  and 2.48 fused in `nominal`, 72.99 fused in `measurement_bias`); velocity NEES
  is above in 13. NIS per degree of freedom is below its interval in 13 for both
  methods, as expected for gated updates (0.81 and 0.77 in `nominal`). Intervals
  assume independent samples and are optimistic.
- The sensor-disagreement scenarios test different things.
  `sensor_disagreement_large_bias` (0.12 rad) is a **gate-rejection**
  experiment: about 96% of delivered vision observations were rejected by the
  gate (mean 264.7 of 275.2 per seed; 10.2 still applied), and the paired RMSE
  interval includes zero under both matchers. The **within-gate** scenarios
  apply a bias small enough to be fused. At the three preregistered values the
  gate rejected a mean 20.8, 30.8 and 52.8 of 275.2 observations per seed
  (0.010, 0.015, 0.020 rad). Fused precision is 0.617, 0.560 and 0.535 against
  0.826 for range-only, MOTA 0.332, 0.169 and 0.092 against 0.746, and the
  paired RMSE interval goes against fusion under both matchers (headline
  +0.101, +0.148, +0.233 m; distance-only +0.042, +0.060, +0.065 m). This is a
  single synthetic world with development seeds; it does not establish
  real-world fusion performance.
- `crossing_targets` (one crossing of three targets) and `dense_clutter` are
  tested under global-nearest-neighbour association only. In `crossing_targets`
  fused has 0.8 identity switches per seed against 1.2 for range-only with
  continuity (6.8 against 4.4 distance-only), lower MOTA (0.573 against 0.804)
  and a paired RMSE interval that includes zero. In `dense_clutter` fused
  precision is 0.338 against 0.816, MOTA -0.977 against 0.732, with 73.4
  unmatched confirmed tracks per seed (8.6 of them duplicates). No claim is made
  about other associators.
- 95% coverage is not improved by fusion overall, and remains far below the
  nominal 0.95 in the miscalibration scenario.
- The `out_of_sequence` scenario has no matched samples: observations older
  than the one-epoch staleness bound are rejected and counted. Its accuracy
  metrics are `N/A`, not zero.

These statements are deliberately weaker than "fusion works". The benchmark is
a development result on a synthetic world, not evidence of real-world or
hardware performance.

## Reproducibility

- Explicit seeds control world generation and independent sensor streams.
- A paired run reuses the same world states and the same range-sensor random
  stream for both methods.
- No wall-clock timestamps are stored in benchmark artifacts, so repeated runs
  with the same seed set and code commit are byte-identical.
- Artifacts record the package version, git commit, protocol, seeds and config.
- The canonical artifacts are `benchmark.json`, `per_seed.csv` and `report.md`
  under `artifacts/benchmark/`.

The published v0.1.0 benchmark numbers were produced with the defects listed in
[docs/core-validity-audit.md](docs/core-validity-audit.md), including
single-observation-per-epoch association, sensor/world bearing mismatch and an
evaluator that reused final track states. **Those numbers are invalid and have
been superseded; they are not preserved as a baseline for comparison.**

## Limitations (summary)

- Synthetic 2-D world with simplified point-measurement sensors; no raw data,
  occlusion, clutter maps or hardware validation.
- Constant-velocity motion model; turning objects are approximated.
- Vision-only track initiation is unsupported by design.
- Observations older than one tracker epoch are rejected, not replayed; the
  stale-data fusion case is not evaluated. Admitted delayed observations are
  applied to the delivery-time state (not rewound to capture time), an
  approximation whose displacement scale is ~speed x age under constant
  velocity, not a strict bound.
- Association is gated Hungarian within each measurement group, not MHT/JPDA.
- Only development seeds have been run; no held-out evaluation is claimed.
- Reported covariance and empirical coverage can disagree; calibration is
  measured, not assumed.

See [docs/limitations.md](docs/limitations.md) for the full list.

## Documentation

- [Architecture](docs/architecture.md)
- [Measurement models](docs/measurement-models.md)
- [Metrics](docs/metrics.md)
- [Evaluation protocol](docs/evaluation-protocol.md)
- [Scenarios](docs/scenarios.md)
- [Design decisions](docs/design-decisions.md)
- [Limitations](docs/limitations.md)
- [Technical walkthrough](docs/technical-walkthrough.md)
- [Technical FAQ](docs/technical-faq.md)
- [Core validity audit](docs/core-validity-audit.md)

## License

MIT License - see [LICENSE](LICENSE) for details.
