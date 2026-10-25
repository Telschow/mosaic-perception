# Demo Script (2 minutes)

## Setup

```bash
cd mosaic-perception
uv sync --all-extras
uv run mosaic benchmark --scenario all --seeds 1-5 --duration 10.0
```

The canonical artifacts are written to `artifacts/benchmark/`:
`benchmark.json`, `per_seed.csv` and `report.md`.

## Script

### 1) Opening (15–20 s)

"Mosaic is a reproducible workbench for studying when combining heterogeneous
sensor observations improves object-state estimates — and when fusion can make
them worse. It compares a range-bearing-only baseline with a fused method on
paired worlds and paired range-sensor random streams."

### 2) Single scenario (30–40 s)

```bash
uv run mosaic run --scenario nominal --seed 1 --duration 10.0
```

"Both methods see the same world and the same range stream. The fused run adds
vision bearings only. The table reports position/velocity RMSE, recall,
precision, coverage, matched samples and false tracks."

### 3) Multi-seed evidence (30–40 s)

Open `artifacts/benchmark/report.md` and point to the aggregate and per-seed
tables.

"Across the 11 development scenarios and seeds 1–5, fused position RMSE is
lower in 6 scenarios, within 0.01 m in 3, and worse in 1 (a within-gate vision
bias that is actually fused). But fused precision
is lower in every scenario with defined precision, and coverage is not improved
overall. So the honest finding
is small accuracy gains with worse association quality, not 'fusion wins'."

Show the `out_of_sequence` row: accuracy is `N/A` because observations older
than one epoch are rejected and counted, not silently used.

### 4) Limitations and wrap-up (30–40 s)

"These are synthetic 2-D results with simplified sensors. Vision alone cannot
initiate tracks. Stale observations are rejected rather than replayed, so
stale-data fusion is not evaluated. Track fragmentation is not implemented and
is reported as N/A. The benchmark uses development seeds only; the reserved
held-out seeds 25–49 have not been run. And the published v0.1.0 numbers are
invalid and superseded."

## Notes

- Use the generated artifacts; do not quote old v0.1.0 numbers as a baseline.
- Do not claim fusion is universally better or worse.
- Do not claim held-out or real-world validation.
- Point out both the small accuracy differences and the precision/calibration
  regressions.
