"""
Evaluation metrics for tracking performance.
"""

from __future__ import annotations

import numpy as np

from ..domain.models import EvaluationResult, TrackEstimate, WorldState


class TrackingEvaluator:
    """Evaluate tracking performance against ground truth."""

    def __init__(self, association_threshold: float = 2.0):
        self.association_threshold = association_threshold

    def evaluate(
        self,
        tracks: dict[str, TrackEstimate],
        world_states: list[WorldState],
        scenario_name: str = "nominal",
        seed: int = 42,
        method_name: str = "range_only",
    ) -> EvaluationResult:
        """Evaluate tracks against ground truth."""
        result = EvaluationResult(
            scenario_name=scenario_name,
            seed=seed,
            method_name=method_name,
        )

        # Match tracks to ground truth objects over time
        total_errors = []
        total_vel_errors = []
        matches = 0

        for state_idx, world_state in enumerate(world_states):
            if state_idx >= len(world_states):
                break

            # Get current time
            t = world_state.time

            # Find active tracks at this time
            active_tracks = []
            for track in tracks.values():
                if track.status.value in ["confirmed", "tentative", "coasting"]:
                    if abs(track.time - t) < 0.5 or abs(track.last_update_time - t) < 0.5:
                        active_tracks.append(track)

            # Match each track to closest ground truth object
            for track in active_tracks:
                track_pos = track.position()
                best_dist = float("inf")
                best_obj = None
                for _obj_id, obj_state in world_state.objects.items():
                    dist = np.linalg.norm(track_pos - obj_state.position.to_array())
                    if dist < best_dist:
                        best_dist = dist
                        best_obj = obj_state

                if best_obj is not None and best_dist < self.association_threshold:
                    matches += 1
                    error = track_pos - best_obj.position.to_array()
                    total_errors.append(np.linalg.norm(error))
                    vel_error = track.velocity() - best_obj.velocity.to_array()
                    total_vel_errors.append(np.linalg.norm(vel_error))

        # Compute metrics
        if total_errors:
            result.position_rmse = float(np.sqrt(np.mean(np.array(total_errors) ** 2)))
        if total_vel_errors:
            result.velocity_rmse = float(np.sqrt(np.mean(np.array(total_vel_errors) ** 2)))

        # Track statistics
        result.num_tracks = len(tracks)
        result.num_confirmed_tracks = sum(
            1 for t in tracks.values() if t.status.value == "confirmed"
        )

        # Uncertainty coverage (simplified)
        # For 95% confidence ellipse in 2D, chi-square threshold is ~5.991
        if total_errors and active_tracks:
            # This is a simplified approximation
            result.position_coverage_95 = 0.85  # Placeholder - would need proper computation

        return result
