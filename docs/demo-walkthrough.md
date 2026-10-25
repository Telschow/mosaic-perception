# Demo Walkthrough (2-3 minutes)

This walkthrough demonstrates the core capability of Mosaic: showing when sensor fusion helps and when it hurts.

## Prerequisites
```bash
cd mosaic-perception
uv sync  # or pip install -e ".[dev]"
```

## Step 1: Quick CLI test (30 seconds)
Run a single scenario to see basic functionality:
```bash
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['run', '--scenario', 'nominal', '--seed', '42', '--duration', '10.0'])"
```

You'll see a comparison table showing position RMSE for range-only vs fused tracking.

## Step 2: Multi-seed comparison (45 seconds)
Run across multiple seeds to see variability:
```bash
PYTHONPATH=src python3 -c "from mosaic_perception.cli.main import app; app(['compare', '--scenario', 'nominal', '--seeds', '1,5,10,20,30', '--duration', '10.0'])"
```

Notice that sometimes fusion improves (negative delta), sometimes degrades (positive delta). This is the key insight!

## Step 3: Interactive exploration (60 seconds)
Launch the Streamlit workbench:
```bash
streamlit run app/streamlit_app.py
```

1. Try different seeds - see how results change
2. Look at the 2D plot showing ground truth (dashed) vs tracks (markers)
3. Compare the metrics between range-only and fused
4. Notice that fusion can create more tracks or different behavior

## Key Takeaways
- **Fusion isn't always better** - depends on conditions, data association, calibration
- **Reproducible** - same seed gives same results
- **Transparent** - can see individual tracks and understand behavior
- **Synthetic but rigorous** - controlled environment to study trade-offs

## Limitations to Note
- This is synthetic data only - not real sensor performance
- Vision-only track initiation is not performed (bearing alone doesn't determine range)
- Observer is currently assumed static at origin in this implementation
- Simple gated nearest-neighbor association
