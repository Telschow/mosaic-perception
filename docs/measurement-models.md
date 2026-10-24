# Measurement Models

## Coordinate Frames

- **World frame**: Global coordinate system for the scene
- **Sensor frame**: Local frame aligned with sensor orientation
- Bearings are converted between frames as needed

## Range-Bearing Sensor

Measures:
- **Range**: $r = \sqrt{(p_x - s_x)^2 + (p_y - s_y)^2} + v_r$
- **Bearing**: $\theta = \arctan2(p_y - s_y, p_x - s_x) - \psi_s + v_\theta$
- **Range rate**: $\dot{r} = \frac{(p-s)\cdot v}{r} + v_{\dot{r}}$

Where $(p_x,p_y)$ is target position, $(s_x,s_y)$ sensor position, $\psi_s$ sensor heading.

Measurement noise: Gaussian with configurable standard deviations.
Jacobian computed for EKF linearization.

## Vision-Bearing Sensor

Measures:
- **Bearing only**: $\theta = \arctan2(p_y - s_y, p_x - s_x) - \psi_s + v_\theta$

Plus classification outputs:
- **Class probabilities**: Softmax over object classes
- **Detection confidence**: Scalar confidence score

**Important**: A single bearing measurement cannot uniquely determine range/position in 2D. Vision-only track initiation requires additional information or is not performed.

## Timing

All observations include:
- **capture_time**: When the measurement was captured
- **delivery_time**: When delivered to tracker (capture_time + delay)
- Tracker processes observations based on delivery time

## Uncertainty

Each observation includes measurement covariance $R$ where applicable.
Reported uncertainties must be calibrated - empirical coverage is evaluated.
