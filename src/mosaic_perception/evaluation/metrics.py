"""
Tracking evaluation against ground truth.

Evaluation uses per-epoch :class:`TrackSnapshot` records produced during the
run. It never reconstructs history from final track states. At each world
timestamp, confirmed/coasting tracks are matched one-to-one to ground-truth
objects with a gated Hungarian assignment (default Euclidean gate 2.0 m).
Metrics and their denominators are documented in ``docs/metrics.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import chi2

from ..domain.models import (
    EvaluationResult,
    ObservationStatistics,
    TrackSnapshot,
    TrackStatus,
    WorldState,
)

_COVERAGE_95 = float(chi2.ppf(0.95, 2))  # 5.991 for two-dimensional position
_COVERAGE_68 = float(chi2.ppf(0.68, 2))
_EVALUATED_STATUSES = {TrackStatus.CONFIRMED, TrackStatus.COASTING}


@dataclass(frozen=True)
class _FrameMatch:
    time: float
    matched_pairs: list[tuple[TrackSnapshot, str]]
    unmatched_tracks: int
    unmatched_objects: int
    # Unmatched evaluated tracks that had a ground-truth object inside the
    # matching gate: the object was claimed by another track (a duplicate).
    duplicate_tracks: list[TrackSnapshot] = field(default_factory=list)


class TrackingEvaluator:
    """Evaluate per-epoch track snapshots against world ground truth."""

    def __init__(self, match_gate_m: float = 2.0):
        if match_gate_m <= 0:
            raise ValueError("match_gate_m must be positive")
        self.match_gate_m = float(match_gate_m)

    def evaluate(
        self,
        snapshots: list[TrackSnapshot],
        world_states: list[WorldState],
        scenario_name: str = "nominal",
        seed: int = 42,
        method_name: str = "range_only",
        statistics: ObservationStatistics | None = None,
        config: dict | None = None,
        git_commit: str | None = None,
    ) -> EvaluationResult:
        """Compute accuracy, association, coverage and timing metrics."""
        result = EvaluationResult(
            scenario_name=scenario_name,
            seed=seed,
            method_name=method_name,
            matching_gate_m=self.match_gate_m,
            config=config or {},
            git_commit=git_commit,
        )
        if statistics is not None:
            result.delivered_observations = statistics.delivered_observations
            result.rejected_observations = statistics.rejected_observations
            result.rejected_out_of_sequence = statistics.rejected_out_of_sequence
            result.rejected_invalid = statistics.rejected_invalid
            result.pending_observations = statistics.pending_observations
            result.age_samples = statistics.age_samples
            result.mean_age_of_information = statistics.mean_age_of_information
            # Vision-specific observation acceptance
            result.vision_generated = statistics.vision_generated
            result.vision_delivered = statistics.vision_delivered
            result.vision_gate_rejected = statistics.vision_gate_rejected
            result.vision_lost_competition = statistics.vision_lost_competition
            result.vision_unassigned_other = statistics.vision_unassigned_other
            result.vision_applied = statistics.vision_applied
            result.vision_invalid_or_stale = statistics.vision_invalid_or_stale

        snapshots_by_time: dict[float, dict[str, TrackSnapshot]] = {}
        all_track_ids: set[str] = set()
        ever_confirmed: set[str] = set()
        for snapshot in snapshots:
            all_track_ids.add(snapshot.track_id)
            if snapshot.status in _EVALUATED_STATUSES:
                ever_confirmed.add(snapshot.track_id)
            key = round(float(snapshot.time), 9)
            snapshots_by_time.setdefault(key, {})[snapshot.track_id] = snapshot

        position_squared_errors: list[float] = []
        velocity_squared_errors: list[float] = []
        coverage_hits_95 = 0
        coverage_hits_68 = 0
        coverage_samples = 0
        matched_samples = 0
        ground_truth_samples = 0
        confirmed_track_samples = 0
        unmatched_ground_truth_samples = 0
        unmatched_track_samples = 0
        matched_track_ids: set[str] = set()
        duplicate_track_ids: set[str] = set()
        duplicate_track_samples = 0
        assignments_by_object: dict[str, list[tuple[float, str]]] = {}
        matched_frames_by_object: dict[str, list[int]] = {}

        result.evaluated_frames = len(world_states)
        for frame_index, world_state in enumerate(world_states):
            key = round(float(world_state.time), 9)
            frame_tracks = [
                snapshot
                for snapshot in snapshots_by_time.get(key, {}).values()
                if snapshot.status in _EVALUATED_STATUSES
            ]
            frame_objects = list(world_state.objects.values())
            ground_truth_samples += len(frame_objects)
            confirmed_track_samples += len(frame_tracks)

            frame = self._match_frame(float(world_state.time), frame_tracks, frame_objects)
            unmatched_track_samples += frame.unmatched_tracks
            unmatched_ground_truth_samples += frame.unmatched_objects
            matched_samples += len(frame.matched_pairs)
            duplicate_track_samples += len(frame.duplicate_tracks)
            duplicate_track_ids.update(track.track_id for track in frame.duplicate_tracks)

            frame_errors: list[float] = []
            for snapshot, object_id in frame.matched_pairs:
                matched_track_ids.add(snapshot.track_id)
                truth = world_state.objects[object_id]
                error = snapshot.position() - truth.position.to_array()
                velocity_error = snapshot.velocity() - truth.velocity.to_array()
                squared_position = float(error @ error)
                position_squared_errors.append(squared_position)
                velocity_squared_errors.append(float(velocity_error @ velocity_error))
                frame_errors.append(float(np.sqrt(squared_position)))
                assignments_by_object.setdefault(object_id, []).append(
                    (float(world_state.time), snapshot.track_id)
                )
                matched_frames_by_object.setdefault(object_id, []).append(frame_index)

                covariance = snapshot.position_cov()
                try:
                    mahalanobis_sq = float(error @ np.linalg.solve(covariance, error))
                except np.linalg.LinAlgError:
                    continue
                if np.isfinite(mahalanobis_sq) and mahalanobis_sq >= 0.0:
                    coverage_samples += 1
                    if mahalanobis_sq <= _COVERAGE_95:
                        coverage_hits_95 += 1
                    if mahalanobis_sq <= _COVERAGE_68:
                        coverage_hits_68 += 1

            result.per_frame_metrics.append(
                {
                    "time": float(world_state.time),
                    "ground_truth_objects": len(frame_objects),
                    "evaluated_tracks": len(frame_tracks),
                    "matched": len(frame.matched_pairs),
                    "unmatched_ground_truth": frame.unmatched_objects,
                    "unmatched_tracks": frame.unmatched_tracks,
                    "mean_position_error_m": (
                        float(np.mean(frame_errors)) if frame_errors else None
                    ),
                }
            )

        result.matched_samples = matched_samples
        result.ground_truth_samples = ground_truth_samples
        result.confirmed_track_samples = confirmed_track_samples
        result.unmatched_ground_truth_samples = unmatched_ground_truth_samples
        result.unmatched_track_samples = unmatched_track_samples
        result.coverage_samples = coverage_samples
        result.duplicate_track_samples = duplicate_track_samples

        if position_squared_errors:
            result.position_rmse = float(np.sqrt(np.mean(position_squared_errors)))
            result.velocity_rmse = float(np.sqrt(np.mean(velocity_squared_errors)))
        if ground_truth_samples:
            result.recall = matched_samples / ground_truth_samples
        if confirmed_track_samples:
            result.precision = matched_samples / confirmed_track_samples
        if coverage_samples:
            result.position_coverage_95 = coverage_hits_95 / coverage_samples
            result.position_coverage_68 = coverage_hits_68 / coverage_samples

        result.identity_switches = self._count_identity_switches(assignments_by_object)
        result.track_fragmentation = self._count_interruptions(matched_frames_by_object)

        result.num_tracks = len(all_track_ids)
        result.num_confirmed_tracks = len(ever_confirmed)
        unmatched_confirmed = ever_confirmed - matched_track_ids
        result.num_unmatched_confirmed_tracks = len(unmatched_confirmed)
        result.num_duplicate_tracks = len(unmatched_confirmed & duplicate_track_ids)

        result.notes.extend(
            [
                "Matching: one-to-one Hungarian assignment per timestamp with a "
                f"{self.match_gate_m:.2f} m Euclidean gate.",
                "Evaluated tracks: confirmed and coasting snapshots only; "
                "tentative and deleted tracks are excluded.",
                "Recall denominator: every ground-truth object in every simulated frame.",
                "Precision denominator: every confirmed/coasting track snapshot in every frame.",
                "Duplicate track sample: an evaluated track left unmatched in a frame while "
                f"a ground-truth object lay within the {self.match_gate_m:.2f} m matching gate "
                "(the object was claimed by another track). A duplicate track is a confirmed "
                "track that was never matched in any frame and has at least one duplicate "
                "sample.",
                "Coverage: matched position errors against the reported 2x2 covariance; "
                f"95% threshold chi2(2,0.95)={_COVERAGE_95:.3f}.",
                "track_fragmentation: total interruptions, i.e. frames where a matched "
                "object goes unmatched and is matched again later, summed over objects "
                "(None if no object was ever matched). identity_switches counts track ID "
                "changes between consecutive matched frames and is independent of gaps.",
            ]
        )
        return result

    def _match_frame(
        self,
        time: float,
        tracks: list[TrackSnapshot],
        objects: list,
    ) -> _FrameMatch:
        if not tracks or not objects:
            return _FrameMatch(time, [], len(tracks), len(objects))

        track_positions = np.array([track.position() for track in tracks])
        object_positions = np.array([obj.position.to_array() for obj in objects])
        distances = np.linalg.norm(
            track_positions[:, None, :] - object_positions[None, :, :], axis=2
        )
        finite = distances <= self.match_gate_m
        if not np.any(finite):
            return _FrameMatch(time, [], len(tracks), len(objects))

        assignment_cost = np.where(finite, distances, 1e9)
        rows, columns = linear_sum_assignment(assignment_cost)
        paired_rows: set[int] = set()
        paired_columns: set[int] = set()
        matched_pairs: list[tuple[TrackSnapshot, str]] = []
        for row, column in zip(rows, columns, strict=True):
            if finite[row, column]:
                paired_rows.add(int(row))
                paired_columns.add(int(column))
                matched_pairs.append((tracks[row], objects[column].object_id))
        claimed_columns = np.zeros(len(objects), dtype=bool)
        claimed_columns[list(paired_columns)] = True
        duplicates = [
            tracks[row]
            for row in range(len(tracks))
            if row not in paired_rows and bool(np.any(finite[row] & claimed_columns))
        ]
        return _FrameMatch(
            time,
            matched_pairs,
            len(tracks) - len(paired_rows),
            len(objects) - len(paired_columns),
            duplicate_tracks=duplicates,
        )

    @staticmethod
    def _count_interruptions(matched_frames_by_object: dict[str, list[int]]) -> float | None:
        """Count matched-to-unmatched-to-matched interruptions summed over objects.

        An object contributes one interruption per gap of at least one evaluated
        frame between two of its matched frames. Leading and trailing unmatched
        frames are not interruptions.
        """
        if not matched_frames_by_object:
            return None
        interruptions = 0
        for frames in matched_frames_by_object.values():
            ordered = sorted(frames)
            interruptions += sum(
                1
                for previous, current in zip(ordered[:-1], ordered[1:], strict=True)
                if current - previous > 1
            )
        return float(interruptions)

    @staticmethod
    def _count_identity_switches(
        assignments_by_object: dict[str, list[tuple[float, str]]],
    ) -> int | None:
        if not assignments_by_object:
            return None
        switches = 0
        for assignments in assignments_by_object.values():
            ordered = sorted(assignments, key=lambda item: item[0])
            for (_t0, track0), (_t1, track1) in zip(ordered[:-1], ordered[1:], strict=True):
                if track0 != track1:
                    switches += 1
        return switches
