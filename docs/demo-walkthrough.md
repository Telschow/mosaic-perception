# Demo Walkthrough (2–3 minutes)

This walkthrough demonstrates the core capability of Mosaic: a paired comparison
of range-bearing-only tracking and fused range+vision tracking, with explicit
evaluation denominators and honest reporting of unsupported metrics.

## Prerequisites

```bash
cd mosaic-perception
uv sync --all-extras
```

## Step 1: Quick CLI test (30 seconds)

```bash
uv run mosaic run --scenario nominal --seed 1 --duration 10.0
```

You will see both methods on the same world and range stream, with position and
velocity RMSE, recall, precision, coverage, matched samples and unmatched confirmed tracks.
The fused method adds vision observations only.

## Step 2: Multi-seed comparison (45 seconds)

```bash
uv run mosaic compare --scenario nominal --seeds 1-5 --duration 10.0
```

Compare the aggregate metrics. Note that small RMSE differences can coexist with
large precision and false-track differences; do not reduce the comparison to a
single number.

## Step 3: Reproducible artifacts (45 seconds)

```bash
uv run mosaic evaluate --scenario all --seeds 1-5 --duration 10.0 --output results/
```

Open `results/report.md`. The report includes:

- code commit and protocol;
- aggregate metrics with sample standard deviations;
- delivery statistics (delivered, rejected, out-of-sequence, pending, mean AoI);
- per-seed deltas;
- findings and limitations.

The checked-in canonical copy is under `artifacts/benchmark/`. Repeated runs
with the same seeds and commit are byte-identical because no wall-clock
timestamps are stored.

## Step 4: Interactive exploration (60 seconds)

```bash
uv run streamlit run app/streamlit_app.py
```

1. Select a scenario and seed.
2. Run the simulation.
3. Inspect the metrics table and the 2-D plot of ground truth and final
   confirmed/coasting tracks.
4. Try `moving_observer`, `measurement_bias`, `uncertainty_miscalibration` and
   `stale_rejection` to see different failure modes.

## Key takeaways

- **Fusion is not always better.** In the current development benchmark, fused
  position RMSE is often slightly lower, but precision is lower in every
  scenario with defined precision, coverage is not improved overall, and the
  miscalibration scenario remains badly calibrated.
- **Association is per group.** A track can receive range and vision in the
  same epoch; within each group matching is one-to-one.
- **Stale data is rejected explicitly.** The `stale_rejection` scenario reports
  `N/A` accuracy because stale observations are rejected and counted.
- **Undefined metrics are not faked.** `track_fragmentation` is `N/A` only when no object is ever matched.
- **Reproducible.** Explicit seeds, deterministic IDs and paired runs.

## Limitations to note

- Synthetic 2-D world; simplified sensor models; no hardware validation.
- Vision-only track initiation is unsupported.
- Observations older than one tracker epoch are rejected, not replayed.
- The benchmark uses development seeds 0–24 only. Held-out seeds 25–49 are
  reserved and were not run; no held-out or real-world claim is made.
- The published v0.1.0 benchmark numbers are invalid and superseded.
