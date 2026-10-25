# Scenarios

Mosaic supports configurable scenarios to test different conditions.

## Implemented Scenarios

### nominal
Baseline scenario with realistic sensor noise and occasional missed detections.
- Detection probability: ~95% for range, ~90% for vision
- False alarm rate: low
- No additional degradation

## Planned Scenarios (from project brief)

1. **vision_dropout**: Higher rate of missed vision observations
2. **range_dropout**: Intermittent missing range-sensor observations  
3. **measurement_bias**: Controlled bias affecting a measurement stream
4. **delivery_delay**: Delayed observations and differing capture/delivery times
5. **false_observations**: Synthetic false detections that may create or corrupt tracks
6. **uncertainty_miscalibration**: Reported covariance doesn't represent actual error
7. **sensor_disagreement**: Observations from modalities disagree under controlled conditions

## Usage

```bash
mosaic run --scenario nominal --seed 42
mosaic compare --scenario nominal --seeds 1,2,3
```

In the Streamlit app, scenarios can be selected from the sidebar.
