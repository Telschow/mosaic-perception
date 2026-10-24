"""
Multi-sensor tracker.
"""

from __future__ import annotations

import uuid
import numpy as np

from ..domain.models import (
    TrackEstimate, TrackStatus, SensorObservation, ObjectClass
)
from .ekf import ExtendedKalmanFilter
from .association import GatedNearestNeighbor


class MultiSensorTracker:
    """
    Tracker supporting range-only and fused tracking.
    """
    
    def __init__(self, dt: float = 0.1, use_vision: bool = False):
        self.dt = dt
        self.use_vision = use_vision
        self.ekf = ExtendedKalmanFilter(dt=dt)
        self.associator = GatedNearestNeighbor(gate_threshold=9.21)
        
        self.tracks: dict[str, TrackEstimate] = {}
        self.next_track_id = 0
        
        # Track management parameters
        self.min_hits_confirm = 3
        self.max_misses_coast = 5
        self.max_misses_delete = 10
    
    def process_observations(
        self,
        observations: list[SensorObservation],
        current_time: float,
        sensor_pos: np.ndarray = None
    ) -> dict[str, TrackEstimate]:
        """Process observations and update tracks."""
        if sensor_pos is None:
            sensor_pos = np.array([0.0, 0.0])
        
        # Filter observations by delivery time
        valid_obs = [obs for obs in observations if obs.delivery_time <= current_time + 1e-6]
        
        # Predict all tracks
        for track_id in list(self.tracks.keys()):
            track = self.tracks[track_id]
            if track.status == TrackStatus.DELETED:
                continue
            x_pred, P_pred = self.ekf.predict(track.state_array(), track.cov_array())
            track.state = x_pred.tolist()
            track.covariance = P_pred.tolist()
            track.misses += 1
        
        # Associate observations to tracks (gated nearest neighbor)
        track_list = [t for t in self.tracks.values() if t.status != TrackStatus.DELETED]
        associations = self.associator.associate(track_list, valid_obs, self.ekf, sensor_pos)
        
        # Update associated tracks
        for track_id, obs_ids in associations.items():
            if track_id not in self.tracks:
                continue
            track = self.tracks[track_id]
            if track.status == TrackStatus.DELETED:
                continue
            
            # Get observations for this track
            track_obs = [obs for obs in valid_obs if obs.observation_id in obs_ids]
            if not track_obs:
                continue
            
            # Update with observations (sequential update for fusion)
            x = track.state_array()
            P = track.cov_array()
            
            for obs in track_obs:
                # Skip vision if not using fusion
                if obs.sensor_type == "vision_bearing" and not self.use_vision:
                    continue
                # Only use vision if in fusion mode
                if obs.sensor_type == "vision_bearing" and self.use_vision:
                    try:
                        z = np.array([obs.measurements["bearing"]])
                        h = self.ekf.h_bearing(x, sensor_pos)
                        H = self.ekf.H_bearing(x, sensor_pos)
                        R = obs.get_measurement_cov()
                        if R is None:
                            R = np.array([[1e-5]])
                        # Normalize innovation
                        y = z - h
                        y[0] = np.arctan2(np.sin(y[0]), np.cos(y[0]))
                        S = H @ P @ H.T + R
                        K = P @ H.T @ np.linalg.inv(S)
                        x = x + K @ y
                        P = (np.eye(4) - K @ H) @ P
                        P = (P + P.T) / 2
                        track.associated_observations.append(obs.observation_id)
                    except Exception:
                        continue
                elif obs.sensor_type in ["range_bearing", "range_bearing_nonlinear"]:
                    try:
                        z = np.array([obs.measurements["range"], obs.measurements["bearing"], obs.measurements.get("range_rate", 0.0)])
                        h = self.ekf.h_range_bearing(x, sensor_pos)
                        H = self.ekf.H_range_bearing(x, sensor_pos)
                        R = obs.get_measurement_cov()
                        if R is None:
                            R = np.diag([0.25, 1e-4, 0.01])
                        y = z - h
                        y[1] = np.arctan2(np.sin(y[1]), np.cos(y[1]))
                        S = H @ P @ H.T + R
                        K = P @ H.T @ np.linalg.inv(S)
                        x = x + K @ y
                        P = (np.eye(4) - K @ H) @ P
                        P = (P + P.T) / 2
                        track.associated_observations.append(obs.observation_id)
                    except Exception:
                        continue
            
            track.state = x.tolist()
            track.covariance = P.tolist()
            track.hits += len(track_obs)
            track.misses = 0
            track.last_update_time = current_time
            track.age += 1
            
            # Update status
            if track.status == TrackStatus.TENTATIVE and track.hits >= self.min_hits_confirm:
                track.status = TrackStatus.CONFIRMED
            elif track.status == TrackStatus.COASTING and track.hits >= 1:
                track.status = TrackStatus.CONFIRMED
            
            obs.associated_track_id = track_id
        
        # Initiate new tracks from unassociated observations
        associated_obs_ids = set()
        for obs_ids in associations.values():
            associated_obs_ids.update(obs_ids)
        
        unassociated = [obs for obs in valid_obs if obs.observation_id not in associated_obs_ids]
        
        # Group unassociated observations - need enough for initiation
        # For range-bearing, can initiate; for vision-only, need to be careful
        for obs in unassociated:
            if obs.sensor_type in ["range_bearing", "range_bearing_nonlinear"]:
                # Can initiate with range-bearing
                self._initiate_track(obs, current_time, sensor_pos)
            elif obs.sensor_type == "vision_bearing" and self.use_vision:
                # For vision-only initiation, we need range estimate - but problem says
                # "Do not pretend that one camera bearing measurement uniquely determines
                # the two-dimensional range and position of a previously unknown object"
                # So we'll be cautious about initiating from vision alone
                pass  # Skip vision-only initiation for now
        
        # Update track status based on misses
        for track in self.tracks.values():
            if track.status == TrackStatus.DELETED:
                continue
            if track.misses >= self.max_misses_delete:
                track.status = TrackStatus.DELETED
            elif track.misses >= self.max_misses_coast and track.status == TrackStatus.CONFIRMED:
                track.status = TrackStatus.COASTING
        
        return {k: v for k, v in self.tracks.items() if v.status != TrackStatus.DELETED}
    
    def _initiate_track(self, obs: SensorObservation, current_time: float, sensor_pos: np.ndarray):
        """Initiate a new track from an observation."""
        try:
            if obs.sensor_type in ["range_bearing", "range_bearing_nonlinear"]:
                r = obs.measurements["range"]
                bearing = obs.measurements["bearing"]
                # Convert to Cartesian in world frame (assuming sensor at origin aligned)
                px = sensor_pos[0] + r * np.cos(bearing)
                py = sensor_pos[1] + r * np.sin(bearing)
                x_init = np.array([px, py, 0.0, 0.0])  # Assume zero velocity initially
            else:
                return
            
            # Initial covariance
            P_init = np.diag([10.0, 10.0, 5.0, 5.0])
            
            track = TrackEstimate(
                track_id=str(uuid.uuid4()),
                status=TrackStatus.TENTATIVE,
                time=current_time,
                last_update_time=current_time,
                state=x_init.tolist(),
                covariance=P_init.tolist(),
                hits=1,
                misses=0,
                age=1,
                associated_observations=[obs.observation_id],
                initiating_sensor=obs.sensor_id,
            )
            self.tracks[track.track_id] = track
            obs.associated_track_id = track.track_id
        except Exception:
            pass
    
    def reset(self):
        """Reset tracker state."""
        self.tracks = {}
        self.next_track_id = 0
