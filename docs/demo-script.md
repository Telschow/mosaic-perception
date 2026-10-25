# Demo Script (2 minutes)

## Setup
```bash
cd /Users/daniel/Development/mosaic-perception
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['benchmark','--scenario','nominal','--seeds','1,2,3,4,5','--duration','10.0','--output','artifacts/benchmark'])"
```

## Script

### 1) Opening (15-20s)
"Mosaic is a reproducible workbench for studying when combining heterogeneous sensor observations improves object-state estimates — and when fusion can make them worse. It compares a range-only baseline against a fused method under controlled synthetic conditions."

### 2) Nominal case (30-40s)
Run a quick single scenario:
```bash
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['run','--scenario','nominal','--seed','1','--duration','10.0'])"
```
"On seed 1, we see range-only and fused results. Fusion can help in some cases, hurt in others — that's the point we're investigating."

### 3) Multi-seed evidence (30-40s)
Show the benchmark results from artifacts/benchmark/report.md. Point to per-seed variation and aggregate.
"Across multiple seeds, fusion improves in some runs and degrades in others. The aggregate shows the trade-off clearly."

### 4) Limitations & wrap-up (30-40s)
"These are synthetic 2D results with simplified sensors. Vision-only track initiation isn't performed (bearing alone doesn't determine range). Observer pose is handled correctly, but timing/out-of-sequence handling is limited in v0.1. The goal is to reason about fusion behavior, not claim real-world performance."

## Notes
- Use actual generated artifacts, not fabricated numbers
- Don't claim fusion is universally better
- Show both positive and negative deltas
