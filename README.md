# Mosaic

**A reproducible workbench for multi-sensor perception, object tracking and uncertainty.**

Mosaic is a modular, deterministic synthetic workbench for investigating: *When does combining noisy, asynchronous sensor observations improve an estimate of a moving object's state, and when can fusion make the result worse?*

## The Question

Combining multiple sensor modalities should improve state estimates - but fusion isn't guaranteed to help. Timing issues, missed detections, sensor disagreements, miscalibrated uncertainties, or poor data association can all make fused estimates worse than single-sensor alternatives. Mosaic provides a controlled environment to study these trade-offs.

## Architecture

Mosaic implements an end-to-end synthetic perception pipeline:

1. **Synthetic World** - Deterministic 2D scenes with known ground truth trajectories
2. **Sensor Simulation** - Multiple complementary sensors with configurable noise, dropouts, delays, and biases  
3. **Data Association** - Gated nearest-neighbor association between observations and tracks
4. **Tracking & Fusion** - EKF-based tracking with single-sensor and multi-sensor fusion
5. **Evaluation** - Rigorous metrics including accuracy and uncertainty calibration
6. **Visualization** - Interactive workbench for exploring failure modes

## Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/Telschow/mosaic-perception.git
cd mosaic-perception

# Install dependencies with uv
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Run a basic scenario

```bash
# Run nominal scenario
mosaic run --scenario nominal --seed 42

# Compare methods
mosaic compare --scenario nominal --seeds 1,2,3

# Launch the interactive workbench
streamlit run app/streamlit_app.py
```

### Generate results

```bash
# Generate evaluation report
mosaic evaluate --scenario nominal --seeds 0-9 --output results/
```

## Implemented Methods

- **Range-only tracking**: EKF with nonlinear range/bearing/radial-velocity measurements
- **Fused tracking**: Sequential updates incorporating both range-bearing and vision-like bearing observations

Both methods use the same track management, gating, and association logic for fair comparison.

## Evaluation Metrics

- **Accuracy**: Position RMSE, velocity RMSE (for matched tracks)
- **Association**: Precision/recall, identity switches, track fragmentation
- **Timing**: Age of information, measurement-to-output latency
- **Uncertainty**: Empirical coverage of reported confidence regions (e.g., 95% ellipses)

## Reproducibility

- All stochastic elements controlled by explicit random seeds
- Separate development and held-out seed groups
- Configuration, seeds, and versions recorded in all outputs
- All results can be regenerated from saved configurations

## Limitations

This is a **synthetic workbench only**. It does not simulate:
- Real sensor hardware or raw image processing
- Complex real-world environments or occlusions
- Military/tactical scenarios or operational constraints
- Actual flight dynamics or navigation systems

See [docs/limitations.md](docs/limitations.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Note: The `mosaic evaluate` command shown above is planned for future implementation. Use `mosaic run` and `mosaic compare` for current functionality.*

## Implementation notes (v0.1 hardening)

- **Observer pose**: The tracker uses observer/sensor pose from observations/world context (passed via `sensor_pos` or `observation.observer_pose`). For moving observers this is required for correct range/bearing in world frames.
- **EKF updates**: A single canonical `ExtendedKalmanFilter.update(x_pred, P_pred, z, H, R, h_pred=...)` is used; the tracker relies on it. Angular residuals are wrapped.
- **Track lifecycle**: Misses are counted per tracking epoch (after prediction/association/updates) — tracks not updated in an epoch increment misses once. Multiple updates in the same epoch count as one successful update event for miss-reset purposes as implemented.
- **Vision-only initiation**: A single vision-bearing observation does not uniquely determine 2D range/position; the tracker does **not** initiate tracks from vision-only observations. Vision can update existing tracks when fusion is enabled.
- **Timing**: Observations are filtered by `delivery_time <= current_time + eps`. Proper out-of-sequence historical replay is not implemented in v0.1; behavior is explicit and tested.

## Reproducible benchmark
Generate a full benchmark with report and artifacts:
```bash
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['benchmark','--scenario','nominal','--seeds','1,2,3,4,5','--duration','10.0','--output','artifacts/benchmark'])"
```
See `artifacts/benchmark/report.md` for results. All values are generated from code.

## Demo
See [docs/demo-script.md](docs/demo-script.md) for a 2-minute walkthrough using actual artifacts.
