# Demo Script (2 minutes)

## Setup

```bash
cd mosaic-perception
uv sync --all-extras
uv run mosaic benchmark --scenario all --seeds 0-24 --duration 10.0
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
precision, coverage, matched samples and unmatched confirmed tracks."

### 3) Multi-seed evidence (30–40 s)

Open `artifacts/benchmark/report.md` and point to the aggregate and per-seed
tables.

"Across the 16 development scenarios and seeds 0–24, whether fusion improves
accuracy depends on how matched samples are paired: with a distance-only matcher the
paired RMSE interval favours fusion in 7 scenarios and goes against it in 3, with the
continuity-preferring headline matcher it favours fusion in 1 and goes against it in 5.
What does not depend on the matcher is association quality: fused precision, MOTA and
GOSPA are worse in 13 of 14 scenarios, and consistency is poor, with position NEES
above its interval everywhere. So the honest finding is that fusion raises recall but
costs association quality, not 'fusion wins'."

Show the `stale_rejection` row: accuracy is `N/A` because observations older
than one epoch are rejected and counted, not silently used.

### 4) Limitations and wrap-up (30–40 s)

"These are synthetic 2-D results with simplified sensors. Vision alone cannot
initiate tracks. Stale observations are rejected rather than replayed, so
stale-data fusion is not evaluated. Track fragmentation counts gaps in matched
frames and says nothing about identity. The benchmark uses development seeds only; the reserved
held-out seeds 25–49 have not been run. And the published v0.1.0 numbers are
invalid and superseded."

## Notes

- Use the generated artifacts; do not quote old v0.1.0 numbers as a baseline.
- Do not claim fusion is universally better or worse.
- Do not claim held-out or real-world validation.
- Point out both the small accuracy differences and the precision/calibration
  regressions.
