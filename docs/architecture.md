# Architecture

## Overview

Mosaic follows a modular pipeline architecture with clear separation between simulation, sensing, tracking, evaluation, and visualization components.

## Components

### Domain Layer (`src/mosaic_perception/domain/`)
- **models.py**: Core data contracts using Pydantic
- Enforces separation between ground truth and estimator inputs
- Explicit timing (capture vs delivery), uncertainty, and metadata

### Simulation Layer (`src/mosaic_perception/simulation/`)
- **world.py**: Deterministic synthetic environment
- Generates known ground truth trajectories
- Configurable scenarios and random seeds

### Sensors Layer (`src/mosaic_perception/sensors/`)
- **range_bearing.py**: Range, bearing, radial velocity sensor model
- **vision_bearing.py**: Vision-like bearing-only detector
- Configurable noise, dropouts, delays, biases, false alarms

### Tracking Layer (`src/mosaic_perception/tracking/`)
- **ekf.py**: Extended Kalman Filter with constant velocity model
- **association.py**: Gated nearest-neighbor data association
- **tracker.py**: Multi-sensor tracker supporting range-only and fused modes

### Evaluation Layer (`src/mosaic_perception/evaluation/`)
- **metrics.py**: Tracking performance metrics
- Accuracy, association quality, timing, uncertainty calibration

### Reporting Layer (`src/mosaic_perception/reporting/`)
- Report generation (to be expanded)

### CLI (`src/mosaic_perception/cli/`)
- Command-line interface for running experiments

### App (`app/`)
- Streamlit interactive workbench

## Design Principles

1. **Separation of concerns**: Simulation, estimation, and evaluation are independent
2. **Determinism**: All randomness controlled by explicit seeds
3. **Explicit contracts**: Strong typing and validation prevent misuse
4. **Ground truth isolation**: True object identities never leak to tracker
5. **Reproducibility**: All configurations and seeds recorded
6. **Honest about limitations**: Synthetic only, assumptions documented

## Data Flow

```
SyntheticWorld (ground truth)
    ↓
Sensors (observations with noise/delays)
    ↓
Tracker (association + estimation)
    ↓
Evaluator (compare to ground truth)
    ↓
Reports/Visualizations
```
