# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-25

### Added
- Synthetic 2D world with deterministic ground truth trajectories
- Range-bearing sensor model (range, bearing, range-rate) with configurable noise/delays/dropouts/false alarms
- Vision-bearing sensor model (bearing + class probabilities) with configurable behavior
- EKF-based tracking with constant velocity motion model and nonlinear measurement updates
- Gated nearest-neighbor data association
- Range-only baseline and fused tracking (sequential updates)
- Observer-pose propagation for correct measurements under motion
- Per-epoch track miss counting and explicit track lifecycle
- Evaluation metrics (position/velocity RMSE, track counts)
- CLI commands: `run`, `compare`, `benchmark`, `version`
- Reproducible benchmark workflow generating JSON, CSV, and Markdown reports
- Streamlit interactive workbench
- Comprehensive documentation (architecture, metrics, measurement models, limitations, technical walkthrough, FAQ, design decisions)
- Unit and integration tests (14 tests passing)

### Changed
- Hardened EKF with canonical update path, Joseph-form covariance correction, and angle wrapping
- Migrated Pydantic models to v2 ConfigDict
- Improved observer-pose handling throughout pipeline

### Notes
- Synthetic simulation only - no raw image processing, no real hardware/field validation
- Vision-only track initiation not performed (bearing alone insufficient for unique 2D position)
- Fusion does not universally improve performance; results depend on conditions
