"""
Data association for tracking.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from ..domain.models import SensorObservation, TrackEstimate


class GatedNearestNeighbor:
    """
    Gated nearest neighbor data association.
    """
    
    def __init__(self, gate_threshold: float = 9.21):  # chi-square for 95% confidence, 2 DOF
        self.gate_threshold = gate_threshold
    
    def associate(
        self,
        tracks: list[TrackEstimate],
        observations: list[SensorObservation],
        ekf,
        sensor_pos: np.ndarray = None
    ) -> dict[str, list[str]]:
        """
        Associate observations to tracks.
        Returns dict mapping track_id to list of observation_ids.
        """
        if not tracks or not observations:
            return {t.track_id: [] for t in tracks}
        
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        
        # Build cost matrix
        n_tracks = len(tracks)
        n_obs = len(observations)
        cost_matrix = np.full((n_tracks, n_obs), np.inf)
        
        for i, track in enumerate(tracks):
            x = track.state_array()
            P = track.cov_array()
            
            for j, obs in enumerate(observations):
                try:
                    if obs.sensor_type in ["range_bearing", "range_bearing_nonlinear"] and "range" in obs.measurements:
                        z = np.array([obs.measurements["range"], obs.measurements["bearing"], obs.measurements.get("range_rate", 0.0)])
                        h = ekf.h_range_bearing(x, sensor_pos)
                        H = ekf.H_range_bearing(x, sensor_pos)
                        R = obs.get_measurement_cov()
                        if R is None:
                            R = np.diag([0.25, 1e-4, 0.01])
                    elif obs.sensor_type in ["vision_bearing"] or ("range" not in obs.measurements and "bearing" in obs.measurements):
                        z = np.array([obs.measurements["bearing"]])
                        h = ekf.h_bearing(x, sensor_pos)
                        H = ekf.H_bearing(x, sensor_pos)
                        R = obs.get_measurement_cov()
                        if R is None:
                            R = np.array([[1e-5]])
                    else:
                        continue
                    
                    y = z - h
                    # Normalize bearing
                    if len(y) == 1:
                        y[0] = np.arctan2(np.sin(y[0]), np.cos(y[0]))
                    elif len(y) == 3:
                        y[1] = np.arctan2(np.sin(y[1]), np.cos(y[1]))
                    
                    S = H @ P @ H.T + R
                    # Check if S is invertible
                    try:
                        S_inv = np.linalg.inv(S)
                    except Exception:
                        continue
                    mahal = float(y.T @ S_inv @ y)
                    
                    if mahal < self.gate_threshold:
                        cost_matrix[i, j] = mahal
                except Exception:
                    continue
        
        # Check if any finite costs
        if not np.any(np.isfinite(cost_matrix)):
            return {t.track_id: [] for t in tracks}
        
        # Replace inf with large value for assignment
        cost_matrix_safe = np.where(np.isfinite(cost_matrix), cost_matrix, 1e9)
        
        try:
            row_ind, col_ind = linear_sum_assignment(cost_matrix_safe)
        except Exception:
            return {t.track_id: [] for t in tracks}
        
        associations = {t.track_id: [] for t in tracks}
        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < np.inf and cost_matrix[r, c] < self.gate_threshold:
                associations[tracks[r].track_id].append(observations[c].observation_id)
        
        return associations
