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
uv run mosaic benchmark --scenario all --seeds 1-5 --duration 10.0
```

`mosaic evaluate` is implemented and writes the same canonical artifacts as
`benchmark` (they differ only in the recorded command name):

```bash
uv run mosaic evaluate --scenario all --seeds 1-5 --output results/
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
(2.0 m Euclidean gate by default). Tentative and deleted tracks are excluded.
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
- **Track fragmentation**: not implemented; reported as `N/A`/`None`, never as
  a fabricated zero.

Full definitions, matching rules and denominators are in
[docs/metrics.md](docs/metrics.md) and
[docs/evaluation-protocol.md](docs/evaluation-protocol.md).

## Current development benchmark

The checked-in benchmark is generated with `--scenario all --seeds 1-5
--duration 10.0`, i.e. **development seeds only**. The reserved held-out range
25–49 has **not** been run, and no held-out claim is made.

See [artifacts/benchmark/report.md](artifacts/benchmark/report.md) for the
generated tables and [artifacts/benchmark/benchmark.json](artifacts/benchmark/benchmark.json)
for the machine-readable record (protocol, per-seed metrics, git commit).
Headline observations from the current development benchmark:

- Fused position RMSE is lower in 6 of the 10 scenarios with defined accuracy,
  within 0.01 m in 3, and worse in 1 (`sensor_disagreement_within_gate`). The
  differences are generally small. Unweighted macro means over the scenarios
  where the metric is defined (development seeds, descriptive only): RMSE
  0.392 m range-only vs 0.379 m fused (n=10); recall 0.827 vs 0.881 (n=11);
  precision 0.821 vs 0.643 (n=10).
- Fused **precision is lower in every scenario with defined precision**.
  Precision is sample-based (matched samples / all confirmed-or-coasting track
  samples), and the extra "unmatched confirmed tracks" are confirmed tracks never matched to
  a true object. An ad hoc check found all of them within 5 m (median) of a
  true object, consistent with duplicate confirmed tracks rather than distant
  clutter (not part of the canonical artifacts).
- The two sensor-disagreement scenarios test different things.
  `sensor_disagreement_large_bias` (0.12 rad) is a **gate-rejection**
  experiment: about 92% of delivered vision observations were rejected by the
  gate (mean 253.8 of 276.4 per seed), and fused RMSE matched range-only
  within noise. `sensor_disagreement_within_gate` (0.015 rad) is **actually
  fused** (mean 252.0 of 276.4 applied) and *degraded* RMSE (0.285 m vs 0.229
  m range-only), precision (0.524 vs 0.804) and 95% coverage (0.497 vs 0.836).
  Neither establishes real-world fusion performance.
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
- Track fragmentation is not implemented.
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
