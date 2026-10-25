"""
Tracking evaluation against ground truth.

Evaluation uses per-epoch :class:`TrackSnapshot` records produced during the
run. It never reconstructs history from final track states. At each world
timestamp, confirmed/coasting tracks are matched one-to-one to ground-truth
objects with a gated Hungarian assignment (default Euclidean gate 2.0 m); see
``frames.py``. Every metric below is a function of the resulting list of
:class:`FrameMatch`, so metrics can be tested on hand-built frames. Metrics and
their denominators are documented in ``docs/metrics.md``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import chi2

from ..domain.models import (
    EvaluationResult,
    ObjectClass,
    ObservationStatistics,
    TrackSnapshot,
    WorldState,
)
from .frames import EVALUATED_STATUSES, FrameMatch, index_snapshots, match_frames
from .registry import DUPLICATE_SENSITIVITY_GATES_M, gate_label

# GOSPA parameters, fixed before any run (issue #14): cut-off equal to the matching
# gate, alpha = 2, p in {1, 2}.
GOSPA_CUTOFF_M = 2.0
_COVERAGE_95 = float(chi2.ppf(0.95, 2))  # 5.991 for two-dimensional position
_COVERAGE_68 = float(chi2.ppf(0.68, 2))


@dataclass(frozen=True)
class SampleCounts:
    ground_truth: int
    evaluated_tracks: int
    matched: int
    unmatched_ground_truth: int
    unmatched_tracks: int


@dataclass(frozen=True)
class Errors:
    """Squared position and velocity errors over all matched samples."""

    position_squared: list[float]
    velocity_squared: list[float]


@dataclass(frozen=True)
class Coverage:
    samples: int
    hits_95: int
    hits_68: int


@dataclass(frozen=True)
class ClassCounts:
    classified: int
    correct: int


def sample_counts(frames: list[FrameMatch]) -> SampleCounts:
    return SampleCounts(
        ground_truth=sum(len(frame.objects) for frame in frames),
        evaluated_tracks=sum(len(frame.tracks) for frame in frames),
        matched=sum(len(frame.matched_pairs) for frame in frames),
        unmatched_ground_truth=sum(frame.unmatched_objects for frame in frames),
        unmatched_tracks=sum(frame.unmatched_tracks for frame in frames),
    )


def matched_errors(frames: list[FrameMatch]) -> Errors:
    position_squared: list[float] = []
    velocity_squared: list[float] = []
    for frame in frames:
        for snapshot, truth in frame.matched_pairs:
            error = snapshot.position() - truth.position.to_array()
            velocity_error = snapshot.velocity() - truth.velocity.to_array()
            position_squared.append(float(error @ error))
            velocity_squared.append(float(velocity_error @ velocity_error))
    return Errors(position_squared, velocity_squared)


def coverage_counts(frames: list[FrameMatch]) -> Coverage:
    samples = hits_95 = hits_68 = 0
    for frame in frames:
        for snapshot, truth in frame.matched_pairs:
            error = snapshot.position() - truth.position.to_array()
            try:
                mahalanobis_sq = float(error @ np.linalg.solve(snapshot.position_cov(), error))
            except np.linalg.LinAlgError:
                continue
            if np.isfinite(mahalanobis_sq) and mahalanobis_sq >= 0.0:
                samples += 1
                hits_95 += int(mahalanobis_sq <= _COVERAGE_95)
                hits_68 += int(mahalanobis_sq <= _COVERAGE_68)
    return Coverage(samples, hits_95, hits_68)


def class_counts(frames: list[FrameMatch]) -> ClassCounts:
    """Matched samples whose track estimate and true class are both known."""
    classified = correct = 0
    for frame in frames:
        for snapshot, truth in frame.matched_pairs:
            if (
                snapshot.class_estimate != ObjectClass.UNKNOWN
                and truth.true_class != ObjectClass.UNKNOWN
            ):
                classified += 1
                correct += int(snapshot.class_estimate == truth.true_class)
    return ClassCounts(classified, correct)


def matched_track_ids(frames: list[FrameMatch]) -> set[str]:
    return {snapshot.track_id for frame in frames for snapshot, _ in frame.matched_pairs}


def duplicate_track_ids(frames: list[FrameMatch]) -> set[str]:
    return {track.track_id for frame in frames for track in frame.duplicate_tracks}


def duplicate_track_samples(frames: list[FrameMatch]) -> int:
    return sum(len(frame.duplicate_tracks) for frame in frames)


def identity_switches(frames: list[FrameMatch]) -> int | None:
    """Track ID changes between consecutive matched frames of the same object."""
    assignments: dict[str, list[tuple[float, str]]] = {}
    for frame in frames:
        for snapshot, truth in frame.matched_pairs:
            assignments.setdefault(truth.object_id, []).append((frame.time, snapshot.track_id))
    if not assignments:
        return None
    switches = 0
    for object_assignments in assignments.values():
        ordered = sorted(object_assignments, key=lambda item: item[0])
        for (_t0, track0), (_t1, track1) in zip(ordered[:-1], ordered[1:], strict=True):
            if track0 != track1:
                switches += 1
    return switches


def interruptions(frames: list[FrameMatch]) -> float | None:
    """Matched-to-unmatched-to-matched interruptions, summed over objects.

    An object contributes one interruption per gap of at least one evaluated
    frame between two of its matched frames. Leading and trailing unmatched
    frames are not interruptions.
    """
    matched_frames: dict[str, list[int]] = {}
    for frame in frames:
        for _snapshot, truth in frame.matched_pairs:
            matched_frames.setdefault(truth.object_id, []).append(frame.index)
    if not matched_frames:
        return None
    total = 0
    for indices in matched_frames.values():
        ordered = sorted(indices)
        total += sum(
            1
            for previous, current in zip(ordered[:-1], ordered[1:], strict=True)
            if current - previous > 1
        )
    return float(total)


def mota(frames: list[FrameMatch]) -> float | None:
    """CLEAR-MOT accuracy: 1 - (misses + false positives + identity switches) / ground truth.

    Misses are unmatched ground-truth samples, false positives are unmatched
    evaluated track samples (duplicates included) and identity switches are
    counted as in :func:`identity_switches`. Can be negative; undefined without
    ground truth.
    """
    counts = sample_counts(frames)
    if counts.ground_truth == 0:
        return None
    switches = identity_switches(frames) or 0
    errors = counts.unmatched_ground_truth + counts.unmatched_tracks + switches
    return 1.0 - errors / counts.ground_truth


@dataclass(frozen=True)
class IdScores:
    """Trajectory-level identity scores (Ristani et al., 2016)."""

    idtp: int
    idfn: int
    idfp: int
    idp: float | None
    idr: float | None
    idf1: float | None


def idf1_scores(frames: list[FrameMatch], gate_m: float) -> IdScores:
    """IDF1, IDP and IDR from the best global pairing of tracks to ground-truth objects.

    A ground-truth object and a track co-occur in a frame when their distance is
    within ``gate_m``. The global assignment maximises total co-occurrences
    (equivalent to minimising identity false negatives plus false positives).
    """
    object_ids: dict[str, int] = {}
    track_ids: dict[str, int] = {}
    pair_counts: dict[tuple[int, int], int] = {}
    object_detections = 0
    track_detections = 0
    for frame in frames:
        object_detections += len(frame.objects)
        track_detections += len(frame.tracks)
        for obj in frame.objects:
            object_ids.setdefault(obj.object_id, len(object_ids))
        for track in frame.tracks:
            track_ids.setdefault(track.track_id, len(track_ids))
        for track in frame.tracks:
            for obj in frame.objects:
                if np.linalg.norm(track.position() - obj.position.to_array()) <= gate_m:
                    key = (object_ids[obj.object_id], track_ids[track.track_id])
                    pair_counts[key] = pair_counts.get(key, 0) + 1
    idtp = 0
    if pair_counts:
        overlap = np.zeros((len(object_ids), len(track_ids)))
        for (row, column), count in pair_counts.items():
            overlap[row, column] = count
        rows, columns = linear_sum_assignment(-overlap)
        idtp = int(overlap[rows, columns].sum())
    idfn = object_detections - idtp
    idfp = track_detections - idtp
    idp = idtp / (idtp + idfp) if (idtp + idfp) else None
    idr = idtp / (idtp + idfn) if (idtp + idfn) else None
    denominator = 2 * idtp + idfp + idfn
    idf1 = 2 * idtp / denominator if denominator else None
    return IdScores(idtp, idfn, idfp, idp, idr, idf1)


def gospa(frames: list[FrameMatch], cutoff_m: float, p: int, alpha: int = 2) -> float | None:
    """Mean per-frame GOSPA distance (Rahmathullah et al., 2017) with alpha = 2.

    Per frame: ``(sum over assigned pairs of min(d, c)^p + c^p / 2 * (m + n - 2k))^(1/p)``
    where ``k = min(m, n)`` pairs are assigned by the optimal assignment. Frames
    with no objects and no tracks contribute 0. ``None`` without frames.
    """
    if alpha != 2:
        raise ValueError("only alpha = 2 is implemented")
    if not frames:
        return None
    values: list[float] = []
    for frame in frames:
        m, n = len(frame.objects), len(frame.tracks)
        total = 0.0
        if m and n:
            truth = np.array([obj.position.to_array() for obj in frame.objects])
            estimates = np.array([track.position() for track in frame.tracks])
            distances = np.linalg.norm(truth[:, None, :] - estimates[None, :, :], axis=2)
            cost = np.minimum(distances, cutoff_m) ** p
            rows, columns = linear_sum_assignment(cost)
            total += float(cost[rows, columns].sum())
        total += (cutoff_m**p / 2.0) * abs(m - n)
        values.append(total ** (1.0 / p))
    return float(np.mean(values))


@dataclass(frozen=True)
class NeesSums:
    """Sums of normalised estimation error squared over matched samples."""

    samples: int
    position: float  # sum of 2-DOF position NEES
    velocity: float  # sum of 2-DOF velocity NEES


def nees_sums(frames: list[FrameMatch]) -> NeesSums:
    """NEES of matched samples, position and velocity from their own covariance blocks.

    Only matched samples contribute (those inside the matching gate), so the
    statistic is conditioned on that gate; samples with a singular or non-finite
    covariance are skipped. Samples within one track are correlated.
    """
    samples = 0
    position_sum = velocity_sum = 0.0
    for frame in frames:
        for snapshot, truth in frame.matched_pairs:
            error = snapshot.position() - truth.position.to_array()
            velocity_error = snapshot.velocity() - truth.velocity.to_array()
            covariance = np.asarray(snapshot.covariance, dtype=float)
            try:
                position_nees = float(error @ np.linalg.solve(covariance[:2, :2], error))
                velocity_nees = float(
                    velocity_error @ np.linalg.solve(covariance[2:4, 2:4], velocity_error)
                )
            except np.linalg.LinAlgError:
                continue
            if (
                np.isfinite(position_nees)
                and np.isfinite(velocity_nees)
                and position_nees >= 0.0
                and velocity_nees >= 0.0
            ):
                samples += 1
                position_sum += position_nees
                velocity_sum += velocity_nees
    return NeesSums(samples, position_sum, velocity_sum)


def per_frame_metrics(frames: list[FrameMatch]) -> list[dict]:
    rows: list[dict] = []
    for frame in frames:
        errors = [
            float(np.linalg.norm(snapshot.position() - truth.position.to_array()))
            for snapshot, truth in frame.matched_pairs
        ]
        rows.append(
            {
                "time": frame.time,
                "ground_truth_objects": len(frame.objects),
                "evaluated_tracks": len(frame.tracks),
                "matched": len(frame.matched_pairs),
                "unmatched_ground_truth": frame.unmatched_objects,
                "unmatched_tracks": frame.unmatched_tracks,
                "mean_position_error_m": float(np.mean(errors)) if errors else None,
            }
        )
    return rows


class TrackingEvaluator:
    """Evaluate per-epoch track snapshots against world ground truth."""

    def __init__(self, match_gate_m: float = 2.0, continuity: bool = True):
        if match_gate_m <= 0:
            raise ValueError("match_gate_m must be positive")
        self.match_gate_m = float(match_gate_m)
        # Prefer each object's previous track while it stays inside the gate (as TrackEval's
        # CLEAR matching does). Adopted as the headline after measuring that a distance-only
        # matcher inflates identity switches (issue #17); distance-only switches are still
        # reported as identity_switches_distance_only.
        self.continuity = continuity

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
            matching_continuity=self.continuity,
            config=config or {},
            git_commit=git_commit,
        )
        if statistics is not None:
            _copy_observation_statistics(result, statistics)

        snapshots_by_time = index_snapshots(snapshots)
        all_track_ids = {snapshot.track_id for snapshot in snapshots}
        ever_confirmed = {
            snapshot.track_id for snapshot in snapshots if snapshot.status in EVALUATED_STATUSES
        }
        frames = match_frames(
            snapshots_by_time, world_states, self.match_gate_m, continuity=self.continuity
        )

        counts = sample_counts(frames)
        result.evaluated_frames = len(world_states)
        result.matched_samples = counts.matched
        result.ground_truth_samples = counts.ground_truth
        result.confirmed_track_samples = counts.evaluated_tracks
        result.unmatched_ground_truth_samples = counts.unmatched_ground_truth
        result.unmatched_track_samples = counts.unmatched_tracks
        result.per_frame_metrics = per_frame_metrics(frames)

        errors = matched_errors(frames)
        if errors.position_squared:
            result.position_rmse = float(np.sqrt(np.mean(errors.position_squared)))
            result.velocity_rmse = float(np.sqrt(np.mean(errors.velocity_squared)))
        if counts.ground_truth:
            result.recall = counts.matched / counts.ground_truth
        if counts.evaluated_tracks:
            result.precision = counts.matched / counts.evaluated_tracks

        coverage = coverage_counts(frames)
        result.coverage_samples = coverage.samples
        if coverage.samples:
            result.position_coverage_95 = coverage.hits_95 / coverage.samples
            result.position_coverage_68 = coverage.hits_68 / coverage.samples

        classes = class_counts(frames)
        result.class_classified_samples = classes.classified
        result.class_correct_samples = classes.correct
        if classes.classified:
            result.class_accuracy = classes.correct / classes.classified

        nees = nees_sums(frames)
        result.nees_samples = nees.samples
        result.nees_position_sum = nees.position
        result.nees_velocity_sum = nees.velocity
        if nees.samples:
            result.anees_position = nees.position / nees.samples
            result.anees_velocity = nees.velocity / nees.samples
        result.identity_switches = identity_switches(frames)
        if self.continuity:
            distance_only = match_frames(snapshots_by_time, world_states, self.match_gate_m)
            result.identity_switches_distance_only = identity_switches(distance_only)
            plain_errors = matched_errors(distance_only)
            if plain_errors.position_squared:
                result.position_rmse_distance_only = float(
                    np.sqrt(np.mean(plain_errors.position_squared))
                )
        else:
            result.identity_switches_distance_only = result.identity_switches
            result.position_rmse_distance_only = result.position_rmse
        result.mota = mota(frames)
        ids = idf1_scores(frames, self.match_gate_m)
        result.idf1, result.idp, result.idr = ids.idf1, ids.idp, ids.idr
        result.gospa_p1 = gospa(frames, GOSPA_CUTOFF_M, 1)
        result.gospa_p2 = gospa(frames, GOSPA_CUTOFF_M, 2)
        result.track_fragmentation = interruptions(frames)

        result.num_tracks = len(all_track_ids)
        result.num_confirmed_tracks = len(ever_confirmed)
        unmatched_confirmed = ever_confirmed - matched_track_ids(frames)
        result.num_unmatched_confirmed_tracks = len(unmatched_confirmed)
        result.duplicate_track_samples = duplicate_track_samples(frames)
        result.num_duplicate_tracks = len(unmatched_confirmed & duplicate_track_ids(frames))
        duplicate_counts = {
            gate: (
                result.num_duplicate_tracks
                if gate == self.match_gate_m
                else _duplicates_at_gate(
                    gate, snapshots_by_time, world_states, ever_confirmed, self.continuity
                )
            )
            for gate in DUPLICATE_SENSITIVITY_GATES_M
        }
        result.num_duplicate_tracks_by_gate = {
            gate_label(gate): count for gate, count in duplicate_counts.items()
        }

        result.notes.extend(
            [
                "Matching: one-to-one Hungarian assignment per timestamp with a "
                f"{self.match_gate_m:.2f} m Euclidean gate"
                + (
                    ", preferring each object's previous track while it stays inside the gate."
                    if self.continuity
                    else " (distance only)."
                ),
                "identity_switches_distance_only and position_rmse_distance_only: the same "
                "metrics under distance-only matching, shown to expose how much the matcher "
                "choice matters (a continuity preference can pair an object with a farther "
                "track, which raises RMSE; distance-only picks the nearest).",
                "Evaluated tracks: confirmed and coasting snapshots only; "
                "tentative and deleted tracks are excluded.",
                "Recall denominator: every ground-truth object in every simulated frame.",
                "Precision denominator: every confirmed/coasting track snapshot in every frame.",
                "Class accuracy: matched samples whose track class estimate and ground-truth "
                "class are both known (not UNKNOWN); correct / classified. None if no sample "
                "qualifies, so a range-only run never reports a fabricated zero.",
                "Duplicate track sample: an evaluated track left unmatched in a frame while "
                f"a ground-truth object lay within the {self.match_gate_m:.2f} m matching gate "
                "(the object was claimed by another track). A duplicate track is a confirmed "
                "track that was never matched in any frame and has at least one duplicate "
                "sample.",
                "Coverage: matched position errors against the reported 2x2 covariance; "
                f"95% threshold chi2(2,0.95)={_COVERAGE_95:.3f}.",
                "MOTA = 1 - (misses + false positives + identity switches) / ground-truth "
                "samples (can be negative; None without ground truth). IDF1, IDP and IDR "
                "use the best global track-to-object pairing by co-occurrence within the "
                "matching gate. GOSPA (alpha=2, cut-off "
                f"{GOSPA_CUTOFF_M:.1f} m, p=1 and p=2) is the mean per-frame distance over "
                "frames, where each missed object or false track costs c^p/2.",
                "track_fragmentation: total interruptions, i.e. frames where a matched "
                "object goes unmatched and is matched again later, summed over objects "
                "(None if no object was ever matched). identity_switches counts track ID "
                "changes between consecutive matched frames and is independent of gaps.",
            ]
        )
        return result


def _duplicates_at_gate(
    gate_m: float,
    snapshots_by_time: dict[float, dict[str, TrackSnapshot]],
    world_states: list[WorldState],
    ever_confirmed: set[str],
    continuity: bool,
) -> int:
    """Duplicate-track count at another matching gate, via matching only."""
    frames = match_frames(snapshots_by_time, world_states, gate_m, continuity=continuity)
    return len((ever_confirmed - matched_track_ids(frames)) & duplicate_track_ids(frames))


def _copy_observation_statistics(
    result: EvaluationResult, statistics: ObservationStatistics
) -> None:
    result.delivered_observations = statistics.delivered_observations
    result.rejected_observations = statistics.rejected_observations
    result.rejected_out_of_sequence = statistics.rejected_out_of_sequence
    result.rejected_invalid = statistics.rejected_invalid
    result.pending_observations = statistics.pending_observations
    result.age_samples = statistics.age_samples
    result.mean_age_of_information = statistics.mean_age_of_information
    result.vision_generated = statistics.vision_generated
    result.vision_delivered = statistics.vision_delivered
    result.vision_gate_rejected = statistics.vision_gate_rejected
    result.vision_lost_competition = statistics.vision_lost_competition
    result.vision_unassigned_other = statistics.vision_unassigned_other
    result.vision_applied = statistics.vision_applied
    result.vision_invalid_or_stale = statistics.vision_invalid_or_stale
    result.nis_sum = statistics.nis_sum
    result.nis_dof_sum = statistics.nis_dof_sum
    result.nis_updates = statistics.nis_updates
    if statistics.nis_dof_sum:
        result.anis = statistics.nis_sum / statistics.nis_dof_sum
