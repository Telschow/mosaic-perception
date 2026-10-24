# Limitations

## What This Project Does

- Synthetic 2D environment with known ground truth
- Simplified sensor models for range-bearing and vision-like bearing
- EKF-based tracking with gated nearest-neighbor association
- Comparison of range-only vs fused approaches
- Evaluation with accuracy and basic uncertainty metrics

## What This Project Does NOT Do

- **Real sensors**: No raw image processing, no actual radar/LiDAR models
- **Complex environments**: No occlusion, clutter modeling, or realistic backgrounds
- **3D**: Only 2D tracking in this initial version
- **Advanced tracking**: No MHT, JPDA, or deep learning approaches
- **Navigation**: No ego-state estimation or SLAM (see contested-nav for that)
- **Military/tactical**: No weapon systems, threat assessment, or classified scenarios
- **Real-world validation**: All results are synthetic

## Known Issues

- Vision-only track initiation is disabled (by design - bearing alone doesn't determine range)
- Uncertainty coverage metrics are simplified in initial implementation
- Association is basic gated nearest-neighbor
- No correlation modeling between sensors
- Turning trajectories have simplified integration

## Assumptions

- Constant velocity motion model
- Known sensor positions/orientations
- Gaussian measurement noise (approximation)
- Linear data association in most cases
- Independent sensor errors (no correlation modeled)

All experiments should be interpreted in light of these limitations.
