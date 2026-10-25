"""
Multi-sensor tracker with per-group association and sequential fusion.

Timing policy
-------------
Observations are held in a pending queue until ``delivery_time``. An
observation whose capture time is at most one tracker epoch (``dt``) in the
past may be applied at delivery time; this bounded-staleness approximation is
documented and tested. Older observations are explicitly rejected and counted
as ``rejected_out_of_sequence`` instead of being silently discarded. A
tracker cannot use ground truth object identities: only observations, their
observer poses, and configuration are available here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..domain.models import (
    ObjectClass,
    ObservationStatistics,
    Pose2D,
    SensorObservation,
    TrackEstimate,
    TrackSnapshot,
    TrackStatus,
    wrap_angle,
)
from .association import GatedHungarianAssociator, GroupAssociation
from .ekf import ExtendedKalmanFilter

_GROUP_ORDER = ("range_bearing", "vision_bearing")
_DELAYED_UPDATE_MODES = ("delivery_time", "retrodiction")

# Vision bearing-bias estimator (issue #20). A single global scalar per vision sensor,
# fixed in advance: prior standard deviation 0.05 rad, random walk of 1e-4 rad per epoch.
BIAS_INITIAL_VARIANCE = 0.05**2
BIAS_PROCESS_VARIANCE = (1e-4) ** 2


def _same_pose(first: Pose2D | None, second: Pose2D | None) -> bool:
    if first is None or second is None:
        return False
    return (
        abs(first.heading - second.heading) < 1e-9
        and abs(first.position.x - second.position.x) < 1e-9
        and abs(first.position.y - second.position.y) < 1e-9
    )


@dataclass(frozen=True)
class _UpdateResult:
    state: np.ndarray
    covariance: np.ndarray
    nis: float
    dof: int


class MultiSensorTracker:
    """
    Range-bearing + optional vision-bearing tracker.

    Each epoch predicts every active track once, then associates and updates
    one measurement group at a time. This allows one range-bearing and one
    vision-bearing observation to update the same track in one epoch while
    preserving one-to-one assignment inside each group.
    """

    def __init__(
        self,
        dt: float = 0.1,
        use_vision: bool = False,
        gates: dict[str, float] | None = None,
        accel_noise_std: float = 0.5,
        max_staleness: float | None = None,
        min_hits_confirm: int = 3,
        max_misses_coast: int = 2,
        max_misses_delete: int = 5,
        delayed_update: str = "delivery_time",
        bias_estimation: bool = False,
    ):
        if dt <= 0:
            raise ValueError("dt must be positive")
        if delayed_update not in _DELAYED_UPDATE_MODES:
            raise ValueError(f"delayed_update must be one of {_DELAYED_UPDATE_MODES}")
        if min_hits_confirm < 1:
            raise ValueError("min_hits_confirm must be at least 1")
        if max_misses_coast < 1 or max_misses_delete <= max_misses_coast:
            raise ValueError("miss thresholds must satisfy 1 <= coast < delete")

        self.dt = float(dt)
        # How an admitted delayed observation is applied: to the delivery-time state
        # (default, an approximation) or by replaying the epoch from the stored previous
        # posterior (one-step-lag retrodiction).
        self.delayed_update = delayed_update
        # Estimate and remove a constant vision bearing bias (single global scalar Kalman
        # filter fed by vision innovations on tracks whose predicted bearing is at least
        # as certain as the vision noise).
        self.bias_estimation = bool(bias_estimation)
        self._bias = 0.0
        self._bias_var = BIAS_INITIAL_VARIANCE
        self._bias_updates = 0
        self._now = 0.0
        self._prev_posterior: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
        self._epoch_applied: dict[str, list[SensorObservation]] = {}
        self.use_vision = bool(use_vision)
        self.ekf = ExtendedKalmanFilter(dt=self.dt, accel_noise_std=accel_noise_std)
        self.associator = GatedHungarianAssociator(gates=gates)
        self.max_staleness = float(max_staleness) if max_staleness is not None else self.dt + 1e-6
        self.min_hits_confirm = int(min_hits_confirm)
        self.max_misses_coast = int(max_misses_coast)
        self.max_misses_delete = int(max_misses_delete)

        self.tracks: dict[str, TrackEstimate] = {}
        self.snapshots: list[TrackSnapshot] = []
        self.next_track_id = 0
        self.epoch = 0
        self._last_time: float | None = None
        self._pending: list[SensorObservation] = []
        self._seen_observation_ids: set[str] = set()
        self._delivered_ages: list[float] = []
        self.rejection_log: list[tuple[str, str]] = []

        self.delivered_observations = 0
        self.rejected_observations = 0
        self.rejected_out_of_sequence = 0
        self.rejected_invalid = 0

        # Vision-specific observation acceptance counters
        self._vision_generated = 0
        self._vision_delivered = 0
        self._vision_gate_rejected = 0
        self._vision_lost_competition = 0
        self._vision_unassigned_other = 0
        self._vision_applied = 0

        # Normalised innovation squared over applied updates (consistency check)
        self._nis_sum = 0.0
        self._nis_dof_sum = 0
        self._nis_updates = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process_observations(
        self, observations: list[SensorObservation], current_time: float
    ) -> dict[str, TrackEstimate]:
        """
        Advance the tracker to ``current_time`` and ingest observations.

        ``observations`` may contain observations whose delivery time is in the
        future; they are queued and delivered in a later call. Time must be
        monotonically non-decreasing.
        """
        now = float(current_time)
        if not np.isfinite(now):
            raise ValueError("current_time must be finite")
        self._now = now
        self._epoch_applied = {}
        self._advance_time(now)
        self._enqueue(observations)
        due = self._take_due(now)

        active_tracks = [
            track for track in self.tracks.values() if track.status != TrackStatus.DELETED
        ]
        updated_track_ids: set[str] = set()
        initiated_track_ids: set[str] = set()

        valid_by_group: dict[str, list[SensorObservation]] = {}
        for observation in due:
            self.delivered_observations += 1
            if observation.sensor_type == "vision_bearing":
                self._vision_delivered += 1
            if observation.delivery_time < observation.capture_time - 1e-9:
                self._reject_invalid(observation, "delivery precedes capture")
                continue
            if observation.capture_time > now + 1e-9:
                self._reject_invalid(observation, "capture time is in the future")
                continue
            age = now - observation.capture_time
            if age > self.max_staleness + 1e-9:
                self.rejected_out_of_sequence += 1
                self.rejected_observations += 1
                self.rejection_log.append(
                    (
                        observation.observation_id,
                        f"stale: age {age:.6f}s exceeds {self.max_staleness:.6f}s",
                    )
                )
                continue
            try:
                group = observation.measurement_group()
            except ValueError as exc:
                self._reject_invalid(observation, str(exc))
                continue
            if group not in _GROUP_ORDER:
                self._reject_invalid(observation, f"unsupported measurement group {group!r}")
                continue
            self._delivered_ages.append(age)
            valid_by_group.setdefault(group, []).append(observation)

        for group in _GROUP_ORDER:
            group_observations = valid_by_group.get(group)
            if not group_observations:
                continue
            # Frozen for the whole group so gating and updating use the same correction.
            group_correction = self._bearing_correction() if group == "vision_bearing" else 0.0
            association = self.associator.associate(
                active_tracks + [self.tracks[tid] for tid in sorted(initiated_track_ids)],
                group_observations,
                self.ekf,
                bearing_correction=group_correction,
            )
            self._handle_invalid(association)
            for track_id, observation in association.matches.items():
                track = self.tracks.get(track_id)
                if track is None or track.status == TrackStatus.DELETED:
                    continue
                try:
                    self._apply_observation(track, observation, group_correction)
                except (ValueError, np.linalg.LinAlgError) as exc:
                    self._reject_invalid(observation, f"measurement update failed: {exc}")
                    continue
                updated_track_ids.add(track_id)
                observation.associated_track_id = track_id
                if observation.sensor_type == "vision_bearing":
                    self._update_class_estimate(track, observation)
                    self._vision_applied += 1

            # Split unassigned vision observations by actual cause
            if group == "vision_bearing":
                self._vision_gate_rejected += len(association.gate_rejected)
                self._vision_lost_competition += len(association.lost_competition)
                self._vision_unassigned_other += (
                    len(association.unmatched)
                    - len(association.gate_rejected)
                    - len(association.lost_competition)
                )

            if group == "range_bearing":
                for observation in association.unmatched:
                    track = self._initiate_track(observation, now)
                    if track is not None:
                        initiated_track_ids.add(track.track_id)
                        updated_track_ids.add(track.track_id)

        self._finish_epoch(now, updated_track_ids)
        self._last_time = now
        self.epoch += 1
        return {
            track_id: track
            for track_id, track in self.tracks.items()
            if track.status != TrackStatus.DELETED
        }

    def statistics(self) -> ObservationStatistics:
        """Return explicit delivery/rejection statistics for reporting."""
        mean_age = float(np.mean(self._delivered_ages)) if self._delivered_ages else None
        return ObservationStatistics(
            delivered_observations=self.delivered_observations,
            rejected_observations=self.rejected_observations,
            rejected_out_of_sequence=self.rejected_out_of_sequence,
            rejected_invalid=self.rejected_invalid,
            pending_observations=len(self._pending),
            age_samples=len(self._delivered_ages),
            mean_age_of_information=mean_age,
            vision_generated=self._vision_generated,
            vision_delivered=self._vision_delivered,
            vision_gate_rejected=self._vision_gate_rejected,
            vision_lost_competition=self._vision_lost_competition,
            vision_unassigned_other=self._vision_unassigned_other,
            vision_applied=self._vision_applied,
            vision_invalid_or_stale=self._vision_delivered
            - self._vision_gate_rejected
            - self._vision_lost_competition
            - self._vision_unassigned_other
            - self._vision_applied,
            nis_sum=self._nis_sum,
            nis_dof_sum=self._nis_dof_sum,
            nis_updates=self._nis_updates,
        )

    @property
    def vision_bias_estimate(self) -> float | None:
        """Current estimate of the vision bearing bias in rad (None when not estimating)."""
        return self._bias if self.bias_estimation else None

    @property
    def vision_bias_updates(self) -> int:
        """Number of vision updates that fed the bias estimator."""
        return self._bias_updates

    def _bearing_correction(self) -> float:
        return self._bias if self.bias_estimation else 0.0

    def _update_bias(self, track: TrackEstimate, observation: SensorObservation) -> None:
        """Scalar Kalman update of the bias from one applied vision observation.

        Measuring the bias against the track's own bearing would be coupled to the track,
        which is itself pulled toward the biased vision bearing, so the filter would become
        overconfident and stick. Instead the measurement is the difference between this
        vision bearing and the bearing of the range-bearing observation applied to the same
        confirmed track at the same capture time and observer pose. That difference does not
        depend on the track state, has expectation equal to the bias (the range-bearing
        sensor is assumed unbiased) and variance ``R_vision + R_range``. Only observations
        that passed the gate are applied, so a bias too large for the gate is never learned.
        """
        if (
            not self.bias_estimation
            or observation.measurement_group() != "vision_bearing"
            or track.status != TrackStatus.CONFIRMED
        ):
            return
        range_observation = next(
            (
                item
                for item in reversed(self._epoch_applied.get(track.track_id, []))
                if item.measurement_group() == "range_bearing"
                and abs(item.capture_time - observation.capture_time) < 1e-9
                and _same_pose(item.observer_pose, observation.observer_pose)
            ),
            None,
        )
        vision_cov = observation.get_measurement_cov()
        range_cov = range_observation.get_measurement_cov() if range_observation else None
        if range_observation is None or vision_cov is None or range_cov is None:
            return
        difference = wrap_angle(
            observation.measurements["bearing"]
            - range_observation.measurements["bearing"]
            - self._bias
        )
        measurement_variance = float(vision_cov[0, 0] + range_cov[1, 1])
        gain = self._bias_var / (self._bias_var + measurement_variance)
        self._bias += gain * difference
        self._bias_var = (1.0 - gain) * self._bias_var
        self._bias_updates += 1

    def pending_count(self) -> int:
        """Number of observations queued but not yet delivered."""
        return len(self._pending)

    def record_vision_generated(self, count: int) -> None:
        """Record the number of vision observations generated by the sensor.

        This is called by the experiment runner to track the total number of
        vision observations produced, regardless of whether they are delivered
        or queued.
        """
        self._vision_generated += count

    def reset(self) -> None:
        """Reset all tracker state, snapshots and counters."""
        self._prev_posterior = {}
        self._epoch_applied = {}
        self._now = 0.0
        self._bias = 0.0
        self._bias_var = BIAS_INITIAL_VARIANCE
        self._bias_updates = 0
        self.tracks = {}
        self.snapshots = []
        self.next_track_id = 0
        self.epoch = 0
        self._last_time = None
        self._pending = []
        self._seen_observation_ids = set()
        self._delivered_ages = []
        self.rejection_log = []
        self.delivered_observations = 0
        self.rejected_observations = 0
        self.rejected_out_of_sequence = 0
        self.rejected_invalid = 0
        self._vision_generated = 0
        self._vision_delivered = 0
        self._vision_gate_rejected = 0
        self._vision_lost_competition = 0
        self._vision_unassigned_other = 0
        self._vision_applied = 0
        self._nis_sum = 0.0
        self._nis_dof_sum = 0
        self._nis_updates = 0

    # ------------------------------------------------------------------
    # Time and delivery queue
    # ------------------------------------------------------------------
    def _advance_time(self, now: float) -> None:
        if self._last_time is None:
            self._last_time = now
            return
        if now < self._last_time - 1e-9:
            raise ValueError(f"non-monotonic tracker time: {now} < {self._last_time}")
        elapsed = now - self._last_time
        if elapsed <= 1e-9:
            return
        steps_float = elapsed / self.dt
        steps = int(round(steps_float))
        if steps < 1 or abs(steps_float - steps) > 1e-6:
            raise ValueError(f"tracker time step {elapsed} is not a multiple of dt={self.dt}")
        for step in range(steps):
            self._bias_var += BIAS_PROCESS_VARIANCE
            for track in self.tracks.values():
                if track.status == TrackStatus.DELETED:
                    continue
                if self.delayed_update == "retrodiction" and step == steps - 1:
                    # Posterior before the last prediction step, for one-step-lag replay.
                    self._prev_posterior[track.track_id] = (
                        track.state_array().copy(),
                        track.cov_array().copy(),
                        now - self.dt,
                    )
                state, covariance = self.ekf.predict(track.state_array(), track.cov_array())
                track.state = state.tolist()
                track.covariance = covariance.tolist()
                track.time = now

    def _enqueue(self, observations: list[SensorObservation]) -> None:
        for observation in observations:
            if not isinstance(observation, SensorObservation):
                raise TypeError("observations must be SensorObservation instances")
            is_vision_like = (
                "range" not in observation.measurements and "bearing" in observation.measurements
            )
            if is_vision_like and not self.use_vision:
                # Range-only mode must not be influenced by vision in any way.
                continue
            if observation.observation_id in self._seen_observation_ids:
                raise ValueError(f"duplicate observation id {observation.observation_id!r}")
            if not np.isfinite(observation.capture_time) or not np.isfinite(
                observation.delivery_time
            ):
                raise ValueError("observation times must be finite")
            self._seen_observation_ids.add(observation.observation_id)
            self._pending.append(observation)

    def _take_due(self, now: float) -> list[SensorObservation]:
        due = [
            observation for observation in self._pending if observation.delivery_time <= now + 1e-9
        ]
        self._pending = [
            observation for observation in self._pending if observation.delivery_time > now + 1e-9
        ]
        due.sort(
            key=lambda observation: (
                observation.delivery_time,
                observation.capture_time,
                observation.observation_id,
            )
        )
        return due

    # ------------------------------------------------------------------
    # Updates and track management
    # ------------------------------------------------------------------
    def _update_state(
        self,
        state: np.ndarray,
        covariance: np.ndarray,
        observation: SensorObservation,
        bias_correction: float = 0.0,
    ) -> _UpdateResult:
        """EKF update of ``state`` with one observation (capture-time observer pose)."""
        pose = observation.observer_pose
        if pose is None:
            raise ValueError("observation has no observer pose")
        covariance_measurement = observation.get_measurement_cov()
        if covariance_measurement is None:
            raise ValueError("observation has no measurement covariance")
        group = observation.measurement_group()

        if group == "range_bearing":
            if "range_rate" in observation.measurements:
                measurement = np.array(
                    [
                        observation.measurements["range"],
                        observation.measurements["bearing"],
                        observation.measurements["range_rate"],
                    ]
                )
                predicted = self.ekf.measurement_range_bearing(state, pose)
                jacobian = self.ekf.jacobian_range_bearing(state, pose)
            else:
                measurement = np.array(
                    [
                        observation.measurements["range"],
                        observation.measurements["bearing"],
                    ]
                )
                predicted = self.ekf.measurement_range_bearing(state, pose)[:2]
                jacobian = self.ekf.jacobian_range_bearing(state, pose)[:2, :]
            angle_indices: tuple[int, ...] = (1,)
        elif group == "vision_bearing":
            measurement = np.array(
                [wrap_angle(observation.measurements["bearing"] - bias_correction)]
            )
            predicted = self.ekf.measurement_bearing(state, pose)
            jacobian = self.ekf.jacobian_bearing(state, pose)
            angle_indices = (0,)
        else:
            raise ValueError(f"unsupported measurement group {group!r}")

        # Normalised innovation squared of the update about to be applied, computed
        # from the filter's own quantities only (no ground truth).
        residual, innovation_cov = self.ekf.innovation(
            state,
            covariance,
            measurement,
            predicted,
            jacobian,
            covariance_measurement,
            angle_indices,
        )
        try:
            nis = float(residual @ np.linalg.solve(innovation_cov, residual))
        except np.linalg.LinAlgError:
            nis = float("nan")  # diagnostic only: never let it break the update
        new_state, new_covariance = self.ekf.update(
            state,
            covariance,
            measurement,
            jacobian,
            covariance_measurement,
            predicted,
            angle_indices=angle_indices,
        )
        return _UpdateResult(
            state=np.asarray(new_state, dtype=float),
            covariance=np.asarray(new_covariance, dtype=float),
            nis=nis,
            dof=int(residual.size),
        )

    def _record_nis(self, result: _UpdateResult) -> None:
        if np.isfinite(result.nis):
            self._nis_sum += result.nis
            self._nis_dof_sum += result.dof
            self._nis_updates += 1

    def _is_delayed(self, observation: SensorObservation) -> bool:
        return observation.capture_time < self._now - 1e-9

    def _apply_observation(
        self, track: TrackEstimate, observation: SensorObservation, bias_correction: float = 0.0
    ) -> None:
        stored = self._prev_posterior.get(track.track_id)
        if self.delayed_update == "retrodiction" and self._is_delayed(observation) and stored:
            state, covariance = self._replay_epoch(track, observation, stored, bias_correction)
        else:
            result = self._update_state(
                track.state_array(), track.cov_array(), observation, bias_correction
            )
            self._record_nis(result)
            state, covariance = result.state, result.covariance

        track.state = np.asarray(state, dtype=float).tolist()
        track.covariance = np.asarray(covariance, dtype=float).tolist()
        track.associated_observations.append(observation.observation_id)
        self._epoch_applied.setdefault(track.track_id, []).append(observation)
        self._update_bias(track, observation)

    def _replay_epoch(
        self,
        track: TrackEstimate,
        observation: SensorObservation,
        stored: tuple[np.ndarray, np.ndarray, float],
        bias_correction: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """One-step-lag update: replay this epoch from the stored previous posterior.

        Starting from the posterior stored before this epoch's prediction, the
        observations applied so far this epoch plus the delayed one are processed in
        capture-time order, predicting over the exact interval between them, and the
        state is finally predicted to the current processing time. Only the delayed
        observation's innovation is added to the NIS statistics. Earlier observations are
        replayed with the same correction as the delayed one; this is exact because the
        vision group is applied last and a track receives at most one observation per
        group, so only a range-bearing observation can be replayed before a vision one.
        """
        state, covariance, time = stored
        ordered = sorted(
            [*self._epoch_applied.get(track.track_id, []), observation],
            key=lambda item: (item.capture_time, item.observation_id),
        )
        for item in ordered:
            state, covariance = self.ekf.predict_over(
                state, covariance, max(item.capture_time - time, 0.0)
            )
            time = max(time, item.capture_time)
            result = self._update_state(state, covariance, item, bias_correction)
            state, covariance = result.state, result.covariance
            if item is observation:
                self._record_nis(result)
        return self.ekf.predict_over(state, covariance, max(self._now - time, 0.0))

    def _initiate_track(self, observation: SensorObservation, now: float) -> TrackEstimate | None:
        """Initiate a track from an unassociated range-bearing observation."""
        if "range" not in observation.measurements or "bearing" not in observation.measurements:
            return None
        pose = observation.observer_pose
        covariance_measurement = observation.get_measurement_cov()
        if pose is None or covariance_measurement is None:
            self._reject_invalid(observation, "cannot initiate without observer pose/covariance")
            return None
        if covariance_measurement.shape not in {(2, 2), (3, 3)}:
            self._reject_invalid(observation, "initiating covariance has an invalid shape")
            return None

        distance = float(observation.measurements["range"])
        bearing = float(observation.measurements["bearing"])
        if not np.isfinite(distance) or not np.isfinite(bearing) or distance <= 0.0:
            self._reject_invalid(observation, "initiating range/bearing is invalid")
            return None

        angle = wrap_angle(float(pose.heading) + bearing)
        unit = np.array([np.cos(angle), np.sin(angle)])
        observer_position = pose.position.to_array()
        position = observer_position + distance * unit

        # Polar-to-Cartesian uncertainty from the reported range/bearing block.
        bearing_variance = float(covariance_measurement[1, 1])
        if bearing_variance < 0.0:
            self._reject_invalid(observation, "negative bearing variance")
            return None
        polar_covariance = covariance_measurement[:2, :2]
        transform = np.array(
            [
                [np.cos(angle), -distance * np.sin(angle)],
                [np.sin(angle), distance * np.cos(angle)],
            ]
        )
        position_covariance = transform @ polar_covariance @ transform.T
        position_covariance = 0.5 * (position_covariance + position_covariance.T)
        position_covariance += np.eye(2) * 1e-6

        velocity = pose.velocity.to_array().copy()
        if "range_rate" in observation.measurements and covariance_measurement.shape == (3, 3):
            range_rate = float(observation.measurements["range_rate"])
            velocity = velocity + range_rate * unit
            radial_velocity_variance = float(covariance_measurement[2, 2])
        else:
            radial_velocity_variance = 25.0
        velocity_variance = max(radial_velocity_variance, 0.0) + 4.0

        covariance = np.zeros((4, 4))
        covariance[:2, :2] = position_covariance
        covariance[2, 2] = velocity_variance
        covariance[3, 3] = velocity_variance

        class_estimate = ObjectClass.UNKNOWN
        class_confidence = 0.0
        if observation.class_probs:
            class_probs = observation.class_probs
            best_class = max(class_probs, key=lambda name: class_probs[name])
            class_estimate = ObjectClass(best_class)
            class_confidence = float(class_probs[best_class])

        track_id = self._allocate_track_id()
        track = TrackEstimate(
            track_id=track_id,
            status=TrackStatus.TENTATIVE,
            time=now,
            last_update_time=now,
            state=[float(position[0]), float(position[1]), float(velocity[0]), float(velocity[1])],
            covariance=covariance.tolist(),
            hits=0,
            misses=0,
            age=0,
            associated_observations=[observation.observation_id],
            initiating_sensor=observation.sensor_id,
            class_estimate=class_estimate,
            class_confidence=class_confidence,
        )
        self.tracks[track.track_id] = track
        observation.associated_track_id = track.track_id
        return track

    def _allocate_track_id(self) -> str:
        """Return an unused deterministic track identifier."""
        while f"track_{self.next_track_id:04d}" in self.tracks:
            self.next_track_id += 1
        track_id = f"track_{self.next_track_id:04d}"
        self.next_track_id += 1
        return track_id

    def _update_class_estimate(self, track: TrackEstimate, observation: SensorObservation) -> None:
        if not observation.class_probs:
            return
        class_probs = observation.class_probs
        best_class = max(class_probs, key=lambda name: class_probs[name])
        track.class_estimate = ObjectClass(best_class)
        track.class_confidence = float(class_probs[best_class])

    def _handle_invalid(self, association: GroupAssociation) -> None:
        for observation, reason in association.invalid:
            self._reject_invalid(observation, reason)

    def _reject_invalid(self, observation: SensorObservation, reason: str) -> None:
        self.rejected_invalid += 1
        self.rejected_observations += 1
        self.rejection_log.append((observation.observation_id, reason))
        observation.associated_track_id = None

    def _finish_epoch(self, now: float, updated_track_ids: set[str]) -> None:
        for track in list(self.tracks.values()):
            if track.status == TrackStatus.DELETED:
                continue
            if track.track_id in updated_track_ids:
                track.hits += 1
                track.misses = 0
                track.last_update_time = now
            else:
                track.misses += 1
            track.age += 1

            if track.status == TrackStatus.TENTATIVE:
                if track.hits >= self.min_hits_confirm:
                    track.status = TrackStatus.CONFIRMED
                elif track.misses >= self.max_misses_delete:
                    track.status = TrackStatus.DELETED
            elif track.status == TrackStatus.CONFIRMED:
                if track.misses >= self.max_misses_coast:
                    track.status = TrackStatus.COASTING
                if track.misses >= self.max_misses_delete:
                    track.status = TrackStatus.DELETED
            elif track.status == TrackStatus.COASTING:
                if track.track_id in updated_track_ids:
                    track.status = TrackStatus.CONFIRMED
                elif track.misses >= self.max_misses_delete:
                    track.status = TrackStatus.DELETED

        for track in list(self.tracks.values()):
            self.snapshots.append(
                TrackSnapshot(
                    time=now,
                    track_id=track.track_id,
                    status=track.status,
                    state=track.state,
                    covariance=track.covariance,
                    hits=track.hits,
                    misses=track.misses,
                    age=track.age,
                    updated_this_epoch=track.track_id in updated_track_ids,
                    class_estimate=track.class_estimate,
                )
            )
            if track.status == TrackStatus.DELETED:
                del self.tracks[track.track_id]
                self._prev_posterior.pop(track.track_id, None)
