# Evaluation Metrics

## Accuracy Metrics
- **Position RMSE**: Root mean square error of position estimates for matched tracks
- **Velocity RMSE**: RMSE of velocity estimates where velocity is observable

## Detection and Association Metrics
- **Precision**: Fraction of tracks that correspond to real objects
- **Recall**: Fraction of real objects that are tracked
- **Identity Switches**: Number of times track identity changes for the same object
- **Track Fragmentation**: Measures track continuity

## Timing Metrics
- **Age of Information (AoI)**: Time between measurement capture and delivery/processing
- **Measurement-to-output latency**: End-to-end processing delay

## Uncertainty Calibration
- **Empirical Coverage**: Fraction of true states within reported confidence region
- For 2D position with Gaussian uncertainty, 95% confidence ellipse uses chi-square threshold χ²(2, 0.95) ≈ 5.991
- Coverage should match nominal confidence level for well-calibrated filters

## Important Notes
- Classification confidence is NOT the same as state estimation uncertainty
- Detection accuracy is NOT the same as tracking accuracy
- Single runs are not sufficient - use multiple seeds
- Metrics may be unavailable in some scenarios (reported as N/A with explanation)
