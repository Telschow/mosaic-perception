"""
Extended Kalman Filter for 2D tracking with nonlinear measurements.
"""

from __future__ import annotations

import numpy as np


def wrap_angle(angle: float) -> float:
    """Normalize angle to [-pi, pi]."""
    return float(np.arctan2(np.sin(angle), np.cos(angle)))


class ExtendedKalmanFilter:
    """
    EKF for tracking with constant velocity motion model.
    State vector: [x, y, vx, vy]
    """

    def __init__(self, dt: float = 0.1, q_pos: float = 1.0, q_vel: float = 1.0):
        self.dt = float(dt)
        # Process noise
        self.Q = np.diag([q_pos**2, q_pos**2, q_vel**2, q_vel**2])

        # Motion model
        self.F = np.array(
            [
                [1.0, 0.0, self.dt, 0.0],
                [0.0, 1.0, 0.0, self.dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

    def predict(self, x: np.ndarray, P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Predict step."""
        x = np.asarray(x).reshape(-1)
        P = np.asarray(P)
        x_pred = self.F @ x
        P_pred = self.F @ P @ self.F.T + self.Q
        # Ensure symmetry
        P_pred = (P_pred + P_pred.T) / 2.0
        return x_pred, P_pred

    def h_range_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Measurement model for range, bearing, range_rate."""
        x = np.asarray(x).reshape(-1)
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        sensor_pos = np.asarray(sensor_pos).reshape(-1)
        px, py, vx, vy = float(x[0]), float(x[1]), float(x[2]), float(x[3])
        dx = px - float(sensor_pos[0])
        dy = py - float(sensor_pos[1])
        range_ = float(np.sqrt(dx * dx + dy * dy))
        if range_ < 1e-6:
            range_ = 1e-6
        bearing = float(np.arctan2(dy, dx))
        range_rate = float((dx * vx + dy * vy) / range_)
        return np.array([range_, bearing, range_rate])

    def H_range_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Jacobian of measurement model for range, bearing, range_rate."""
        x = np.asarray(x).reshape(-1)
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        sensor_pos = np.asarray(sensor_pos).reshape(-1)
        px, py, vx, vy = float(x[0]), float(x[1]), float(x[2]), float(x[3])
        dx = px - float(sensor_pos[0])
        dy = py - float(sensor_pos[1])
        range_ = float(np.sqrt(dx * dx + dy * dy))
        if range_ < 1e-6:
            range_ = 1e-6
        range2 = range_ * range_

        H = np.zeros((3, 4))
        # dr/drange
        H[0, 0] = dx / range_
        H[0, 1] = dy / range_
        H[0, 2] = 0.0
        H[0, 3] = 0.0
        # dr/dbearing
        H[1, 0] = -dy / range2
        H[1, 1] = dx / range2
        H[1, 2] = 0.0
        H[1, 3] = 0.0
        # dr/drange_rate
        H[2, 0] = (vx * range2 - dx * (dx * vx + dy * vy)) / (range2 * range_)
        H[2, 1] = (vy * range2 - dy * (dx * vx + dy * vy)) / (range2 * range_)
        H[2, 2] = dx / range_
        H[2, 3] = dy / range_
        return H

    def h_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Measurement model for bearing only."""
        x = np.asarray(x).reshape(-1)
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        sensor_pos = np.asarray(sensor_pos).reshape(-1)
        px, py = float(x[0]), float(x[1])
        dx = px - float(sensor_pos[0])
        dy = py - float(sensor_pos[1])
        bearing = float(np.arctan2(dy, dx))
        return np.array([bearing])

    def H_bearing(self, x: np.ndarray, sensor_pos: np.ndarray = None) -> np.ndarray:
        """Jacobian for bearing only."""
        x = np.asarray(x).reshape(-1)
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        sensor_pos = np.asarray(sensor_pos).reshape(-1)
        px, py = float(x[0]), float(x[1])
        dx = px - float(sensor_pos[0])
        dy = py - float(sensor_pos[1])
        range2 = dx * dx + dy * dy
        if range2 < 1e-12:
            range2 = 1e-12
        H = np.zeros((1, 4))
        H[0, 0] = -dy / range2
        H[0, 1] = dx / range2
        H[0, 2] = 0.0
        H[0, 3] = 0.0
        return H

    def update(
        self,
        x_pred: np.ndarray,
        P_pred: np.ndarray,
        z: np.ndarray,
        H: np.ndarray,
        R: np.ndarray,
        h_pred: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Canonical EKF update. Uses provided predicted measurement when given."""
        x_pred = np.asarray(x_pred).reshape(-1)
        P_pred = np.asarray(P_pred)
        z = np.asarray(z).reshape(-1)
        H = np.asarray(H)
        R = np.asarray(R)

        if h_pred is None:
            # Try to compute from model if possible; otherwise require caller to pass h_pred
            raise ValueError("h_pred must be provided for nonlinear measurement updates")

        h_pred = np.asarray(h_pred).reshape(-1)
        y = z - h_pred
        # Normalize angles where present
        if len(y) == 1:
            y[0] = wrap_angle(float(y[0]))
        elif len(y) == 3:
            y[1] = wrap_angle(float(y[1]))

        S = H @ P_pred @ H.T + R
        # Use solve for numerical stability
        try:
            K = P_pred @ H.T @ np.linalg.solve(S, np.eye(S.shape[0])).T
        except Exception:
            K = P_pred @ H.T @ np.linalg.inv(S)
        x_upd = x_pred + K @ y
        # Joseph form for better numerical stability
        I_KH = np.eye(P_pred.shape[0]) - K @ H
        P_upd = I_KH @ P_pred @ I_KH.T + K @ R @ K.T
        P_upd = (P_upd + P_upd.T) / 2.0
        return x_upd, P_upd
