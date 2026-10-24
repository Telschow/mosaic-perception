# Evaluation Protocol

## Objectives
Determine when sensor fusion improves tracking performance and when it degrades it.

## Hypotheses
1. Under nominal conditions with good data association, fusion should improve or match range-only performance
2. With vision dropouts or poor calibration, fusion may degrade performance
3. Uncertainty calibration matters as much as accuracy
4. Data association errors can make fusion worse than single-sensor

## Experimental Design
- **Development seeds**: 0-24 (for debugging and tuning)
- **Held-out seeds**: 25-49 (for final evaluation)
- **Multiple runs required**: Report statistics across seeds
- **Paired comparisons**: Same scenarios for all methods

## Procedure
1. Generate deterministic world with fixed seed
2. Generate sensor observations for all sensors
3. Run range-only tracker
4. Run fused tracker on same observations
5. Evaluate both against ground truth
6. Compute metrics and compare
7. Repeat for multiple seeds

## Reporting
- All configurations recorded
- Seeds documented
- Git commit/version recorded
- Results are synthetic - clearly labeled
- Failed hypotheses reported, not hidden
- Can regenerate all results from saved configs
