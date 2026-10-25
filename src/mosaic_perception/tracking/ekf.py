"""
Extended Kalman filter for 2-D tracking with nonlinear measurements.

Measurement-frame convention
----------------------------
The state is ``[x, y, vx, vy]`` in the world frame. Sensor measurements are
reported in the **sensor frame**:

* range is Euclidean distance from the observer,
* bearing is the world line-of-sight angle **minus the observer heading**, and
* range rate is the line-of-sight range rate **relative to observer velocity**.

Every measurement function therefore needs the observer pose at capture time.
The observer pose is metadata on each observation; it is not ground-truth
object state and carries no identity information.
"""

from __future__ import annotations

import numpy as np

from ..domain.models import Pose2D, wrap_angle

__all__ = ["ExtendedKalmanFilter", "wrap_angle"]


def _observer_arrays(observer: Pose2D | None) -> tuple[np.ndarray, float, np.ndarray]:
    """Return validated observer position, heading and velocity arrays."""
    pose = observer if observer is not None else Pose2D()
    position = pose.position.to_array()
    velocity = pose.velocity.to_array()
    if position.shape != (2,) or velocity.shape != (2,):
        raise ValueError("observer position and velocity must be 2-D")
    if not np.all(np.isfinite(position)) or not np.all(np.isfinite(velocity)):
        raise ValueError("observer pose must be finite")
    return position, float(pose.heading), velocity


class ExtendedKalmanFilter:
    """
    Constant-velocity EKF for the state ``[x, y, vx, vy]``.

    Process noise is the standard discrete white-noise-acceleration model with
    standard deviation ``accel_noise_std`` (m/s^2), rather than independent
    position/velocity diagonal terms. All covariance updates use the Joseph
    form and are symmetrised; a covariance that is not positive semidefinite
    is rejected instead of silently used.
    """

    def __init__(self, dt: float = 0.1, accel_noise_std: float = 0.5):
        if dt <= 0:
            raise ValueError("dt must be positive")
        if accel_noise_std < 0:
            raise ValueError("accel_noise_std must be non-negative")
        self.dt = float(dt)
        self.accel_noise_std = float(accel_noise_std)

        dt2 = self.dt * self.dt
        dt3 = dt2 * self.dt
        dt4 = dt2 * dt2
        q = self.accel_noise_std**2
        self.process_noise = q * np.array(
            [
                [dt4 / 4.0, 0.0, dt3 / 2.0, 0.0],
                [0.0, dt4 / 4.0, 0.0, dt3 / 2.0],
                [dt3 / 2.0, 0.0, dt2, 0.0],
                [0.0, dt3 / 2.0, 0.0, dt2],
            ]
        )
        self.transition = np.array(
            [
                [1.0, 0.0, self.dt, 0.0],
                [0.0, 1.0, 0.0, self.dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

    @staticmethod
    def _as_state(state: np.ndarray) -> np.ndarray:
        x = np.asarray(state, dtype=float).reshape(-1)
        if x.shape != (4,):
            raise ValueError(f"state must have shape (4,), got {x.shape}")
        if not np.all(np.isfinite(x)):
            raise ValueError("state contains non-finite values")
        return x

    @staticmethod
    def _as_covariance(covariance: np.ndarray) -> np.ndarray:
        cov = np.asarray(covariance, dtype=float)
        if cov.shape != (4, 4):
            raise ValueError(f"covariance must have shape (4, 4), got {cov.shape}")
        if not np.all(np.isfinite(cov)):
            raise ValueError("covariance contains non-finite values")
        if not np.allclose(cov, cov.T, atol=1e-9):
            raise ValueError("covariance must be symmetric")
        return np.asarray(0.5 * (cov + cov.T), dtype=float)

    @staticmethod
    def _ensure_positive_semidefinite(covariance: np.ndarray) -> np.ndarray:
        """Symmetrise and reject materially indefinite covariance matrices."""
        cov = 0.5 * (covariance + covariance.T)
        eigenvalues = np.linalg.eigvalsh(cov)
        scale = max(1.0, float(np.max(np.abs(eigenvalues))))
        if float(eigenvalues[0]) < -1e-8 * scale:
            raise ValueError(
                f"covariance is not positive semidefinite (min eigenvalue {eigenvalues[0]:.3e})"
            )
        if eigenvalues[0] < 0.0:
            cov = cov + np.eye(cov.shape[0]) * (-float(eigenvalues[0]))
        return np.asarray(0.5 * (cov + cov.T), dtype=float)

    def predict(self, state: np.ndarray, covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Predict one nominal time step."""
        x = self._as_state(state)
        cov = self._as_covariance(covariance)
        x_pred = self.transition @ x
        cov_pred = self.transition @ cov @ self.transition.T + self.process_noise
        return x_pred, self._ensure_positive_semidefinite(cov_pred)

    def measurement_range_bearing(
        self, state: np.ndarray, observer: Pose2D | None = None
    ) -> np.ndarray:
        """
        Predicted ``[range, bearing, range_rate]`` in the sensor frame.

        Bearing is wrapped to ``[-pi, pi]`` after subtracting observer heading.
        Range rate uses object velocity minus observer velocity.
        """
        x = self._as_state(state)
        observer_pos, heading, observer_vel = _observer_arrays(observer)
        dx = float(x[0] - observer_pos[0])
        dy = float(x[1] - observer_pos[1])
        distance = float(np.hypot(dx, dy))
        if distance < 1e-9:
            raise ValueError("range is undefined for coincident object and observer")
        bearing = wrap_angle(float(np.arctan2(dy, dx)) - heading)
        relative_velocity = np.array([x[2] - observer_vel[0], x[3] - observer_vel[1]])
        range_rate = float((dx * relative_velocity[0] + dy * relative_velocity[1]) / distance)
        return np.array([distance, bearing, range_rate])

    def jacobian_range_bearing(
        self, state: np.ndarray, observer: Pose2D | None = None
    ) -> np.ndarray:
        """Jacobian of ``measurement_range_bearing`` with respect to the state."""
        x = self._as_state(state)
        observer_pos, _heading, observer_vel = _observer_arrays(observer)
        dx = float(x[0] - observer_pos[0])
        dy = float(x[1] - observer_pos[1])
        distance = float(np.hypot(dx, dy))
        if distance < 1e-9:
            raise ValueError("range is undefined for coincident object and observer")
        distance_sq = distance * distance
        relative_velocity = np.array([x[2] - observer_vel[0], x[3] - observer_vel[1]])
        radial_velocity = dx * relative_velocity[0] + dy * relative_velocity[1]

        jacobian = np.zeros((3, 4))
        jacobian[0, 0] = dx / distance
        jacobian[0, 1] = dy / distance
        jacobian[1, 0] = -dy / distance_sq
        jacobian[1, 1] = dx / distance_sq
        jacobian[2, 0] = relative_velocity[0] / distance - radial_velocity * dx / (
            distance_sq * distance
        )
        jacobian[2, 1] = relative_velocity[1] / distance - radial_velocity * dy / (
            distance_sq * distance
        )
        jacobian[2, 2] = dx / distance
        jacobian[2, 3] = dy / distance
        return jacobian

    def measurement_bearing(self, state: np.ndarray, observer: Pose2D | None = None) -> np.ndarray:
        """Predicted sensor-frame bearing."""
        x = self._as_state(state)
        observer_pos, heading, _observer_vel = _observer_arrays(observer)
        dx = float(x[0] - observer_pos[0])
        dy = float(x[1] - observer_pos[1])
        if np.hypot(dx, dy) < 1e-9:
            raise ValueError("bearing is undefined for coincident object and observer")
        return np.array([wrap_angle(float(np.arctan2(dy, dx)) - heading)])

    def jacobian_bearing(self, state: np.ndarray, observer: Pose2D | None = None) -> np.ndarray:
        """Jacobian of ``measurement_bearing`` with respect to the state."""
        x = self._as_state(state)
        observer_pos, _heading, _observer_vel = _observer_arrays(observer)
        dx = float(x[0] - observer_pos[0])
        dy = float(x[1] - observer_pos[1])
        distance_sq = dx * dx + dy * dy
        if distance_sq < 1e-18:
            raise ValueError("bearing is undefined for coincident object and observer")
        jacobian = np.zeros((1, 4))
        jacobian[0, 0] = -dy / distance_sq
        jacobian[0, 1] = dx / distance_sq
        return jacobian

    def innovation(
        self,
        state: np.ndarray,
        covariance: np.ndarray,
        measurement: np.ndarray,
        predicted_measurement: np.ndarray,
        jacobian: np.ndarray,
        measurement_covariance: np.ndarray,
        angle_indices: tuple[int, ...] = (),
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return the wrapped innovation and its covariance."""
        x = self._as_state(state)
        cov = self._as_covariance(covariance)
        z = np.asarray(measurement, dtype=float).reshape(-1)
        h = np.asarray(predicted_measurement, dtype=float).reshape(-1)
        jac = np.asarray(jacobian, dtype=float)
        noise = np.asarray(measurement_covariance, dtype=float)

        if z.shape != h.shape:
            raise ValueError("measurement and predicted measurement shapes differ")
        if jac.shape != (z.size, x.size):
            raise ValueError("measurement Jacobian has an incompatible shape")
        if noise.shape != (z.size, z.size):
            raise ValueError("measurement covariance has an incompatible shape")
        if not (
            np.all(np.isfinite(z))
            and np.all(np.isfinite(h))
            and np.all(np.isfinite(jac))
            and np.all(np.isfinite(noise))
        ):
            raise ValueError("measurement quantities must be finite")
        if not np.allclose(noise, noise.T, atol=1e-12):
            raise ValueError("measurement covariance must be symmetric")
        if np.min(np.linalg.eigvalsh(noise)) < -1e-12:
            raise ValueError("measurement covariance must be positive semidefinite")

        residual = z - h
        for index in angle_indices:
            residual[index] = wrap_angle(float(residual[index]))
        innovation_cov = jac @ cov @ jac.T + noise
        innovation_cov = 0.5 * (innovation_cov + innovation_cov.T)
        try:
            np.linalg.cholesky(innovation_cov)
        except np.linalg.LinAlgError as exc:
            raise ValueError("innovation covariance is not positive definite") from exc
        return residual, innovation_cov

    def update(
        self,
        state: np.ndarray,
        covariance: np.ndarray,
        measurement: np.ndarray,
        jacobian: np.ndarray,
        measurement_covariance: np.ndarray,
        predicted_measurement: np.ndarray,
        angle_indices: tuple[int, ...] = (),
    ) -> tuple[np.ndarray, np.ndarray]:
        """Apply one EKF measurement update using the Joseph form."""
        x = self._as_state(state)
        cov = self._as_covariance(covariance)
        residual, innovation_cov = self.innovation(
            x,
            cov,
            measurement,
            predicted_measurement,
            jacobian,
            measurement_covariance,
            angle_indices,
        )
        jac = np.asarray(jacobian, dtype=float)
        noise = np.asarray(measurement_covariance, dtype=float)
        gain = np.linalg.solve(innovation_cov, jac @ cov).T
        x_updated = x + gain @ residual

        identity = np.eye(cov.shape[0])
        residual_operator = identity - gain @ jac
        cov_updated = residual_operator @ cov @ residual_operator.T + gain @ noise @ gain.T
        return x_updated, self._ensure_positive_semidefinite(cov_updated)
