# Technical Walkthrough (5 min)

## 1) Problem and motivation
Combining imperfect sensor observations is not automatically beneficial. Timing, noise, dropouts, miscalibration, and poor data association can all make fusion worse than a single-sensor baseline. Mosaic studies this trade-off in a controlled synthetic setting.

## 2) Architecture (as implemented)
1. **Synthetic world** (`simulation/world.py`) — deterministic 2D trajectories with known ground truth.
2. **Sensors** (`sensors/*`) — range-bearing (range/bearing/range-rate) and vision-bearing (bearing + class probs). Observations include `capture_time`, `delivery_time`, measurement model, covariance, and `observer_pose` context.
3. **Tracking/Fusion** (`tracking/*`) — constant-velocity EKF with nonlinear measurement models, gated nearest-neighbor association, range-only baseline and sequential fused updates. Vision-only track initiation is disabled (bearing alone insufficient for unique 2D position).
4. **Evaluation** (`evaluation/metrics.py`) — metrics against ground truth (e.g. position RMSE), with separation between truth and estimator inputs.
5. **Reporting/CLI/UI** — reproducible benchmarks, reports, and Streamlit workbench.

## 3) Technical choices and trade-offs
- **EKF**: canonical `update(x_pred, P_pred, z, H, R, h_pred=...)` with Joseph form, wrapped angles, linear solves where possible.
- **Observer pose**: propagated via observation context or passed to tracker (correct for moving observers).
- **Miss counting**: per-epoch (tracks not updated increment misses once).
- **Association**: gated nearest-neighbor (greedy) — documented limitation.
- **Simplicity over completeness**: 2D, simplified sensors, no raw images/waveforms, limited timing/out-of-sequence handling.

## 4) Evaluation strategy
- **Fair comparison**: same seeds/worlds/sensor streams where possible; fused adds vision observations only.
- **Reproducibility**: explicit seeds, deterministic RNG streams, configuration recorded.
- **Separation**: ground truth only used by evaluator/simulator; `_true_object_id` stripped in normal paths.
- **Metrics**: position/velocity RMSE for matched tracks; denominators/samples matter.

## 5) Example finding (from verified benchmark)
From `artifacts/benchmark/report.md` (nominal, seeds 1-5, 5s): fusion improved RMSE on seeds 1,2 but worsened on 3,4,5 (aggregate ~0.870±0.183 vs 0.912±0.138). This illustrates that fusion is not universally beneficial.

## 6) Limitations and next steps
- Synthetic only, no hardware/field validation
- Simplified sensor models
- Vision-only initiation restricted
- Limited out-of-sequence/timing support
- Gated NN association only
- Need larger seed sets / held-out evaluation for stronger claims
