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
