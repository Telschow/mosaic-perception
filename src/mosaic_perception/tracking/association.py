"""
Data association for tracking.

Association is performed **per measurement group** (range-bearing and
vision-bearing). Within a group, each observation is assigned to at most one
track and each track receives at most one observation; the assignment is a
gated minimum-total-Mahalanobis Hungarian assignment. Because groups are
processed separately, the same track may receive one range-bearing and one
vision-bearing observation in the same epoch and the tracker can apply both
updates sequentially.

The deterministic policy for two observations from the same group is: assign
the pair with the lowest total gated Mahalanobis cost; all remaining
observations from that group are unmatched and are eligible for track
initiation only if they are range-bearing observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import chi2

from ..domain.models import SensorObservation, TrackEstimate, wrap_angle
from .ekf import ExtendedKalmanFilter


@dataclass
class GroupAssociation:
    """Result of associating one homogeneous measurement group."""

    matches: dict[str, SensorObservation] = field(default_factory=dict)
    unmatched: list[SensorObservation] = field(default_factory=list)
    # Subsets of ``unmatched`` explaining why an observation was not assigned:
    # gate_rejected: at least one track was evaluated and none passed the gate;
    # lost_competition: passed the gate for some track but lost the one-to-one
    # assignment. Unmatched observations in neither list had no evaluable
    # candidate (e.g. no tracks existed or every pair was numerically invalid).
    gate_rejected: list[SensorObservation] = field(default_factory=list)
    lost_competition: list[SensorObservation] = field(default_factory=list)
    invalid: list[tuple[SensorObservation, str]] = field(default_factory=list)


# 95% chi-square gates with degrees of freedom equal to the measurement
# dimension: bearing-only is 1-DOF, range/bearing is 2-DOF,
# range/bearing/range-rate is 3-DOF. Keys are "group:dimension". There is
# deliberately no dimension-less fallback: a measurement whose dimension has no
# configured gate raises instead of silently using a different DOF.
DEFAULT_GATES: dict[str, float] = {
    "range_bearing:2": float(chi2.ppf(0.95, 2)),
    "range_bearing:3": float(chi2.ppf(0.95, 3)),
    "vision_bearing:1": float(chi2.ppf(0.95, 1)),
}


class GatedHungarianAssociator:
    """Gated one-to-one nearest-neighbour association within a group."""

    def __init__(self, gates: dict[str, float] | None = None):
        self.gates = dict(DEFAULT_GATES)
        if gates:
            self.gates.update({key: float(value) for key, value in gates.items()})

    def gate_for(self, measurement_group: str, dimension: int) -> float:
        """Return the gate for a measurement group and measurement dimension."""
        key = f"{measurement_group}:{dimension}"
        if key not in self.gates:
            raise ValueError(f"no association gate configured for {key!r}")
        return self.gates[key]

    @staticmethod
    def _measurement(
        observation: SensorObservation,
    ) -> tuple[np.ndarray, tuple[int, ...], str]:
        """Validate one observation and return its measurement and group."""
        group = observation.measurement_group()
        covariance = observation.get_measurement_cov()
        if covariance is None:
            raise ValueError("observation has no measurement covariance")

        if group == "range_bearing":
            if "range" not in observation.measurements or "bearing" not in observation.measurements:
                raise ValueError("range-bearing observation is missing range or bearing")
            if "range_rate" in observation.measurements:
                measurement = np.array(
                    [
                        observation.measurements["range"],
                        observation.measurements["bearing"],
                        observation.measurements["range_rate"],
                    ]
                )
            else:
                measurement = np.array(
                    [
                        observation.measurements["range"],
                        observation.measurements["bearing"],
                    ]
                )
        elif group == "vision_bearing":
            measurement = np.array([observation.measurements["bearing"]])
        else:
            raise ValueError(f"unsupported measurement group {group!r}")

        if covariance.shape != (measurement.size, measurement.size):
            raise ValueError("measurement covariance shape does not match measurement")
        if not np.all(np.isfinite(measurement)):
            raise ValueError("measurement contains non-finite values")
        if not np.all(np.isfinite(covariance)):
            raise ValueError("measurement covariance contains non-finite values")
        if not np.allclose(covariance, covariance.T, atol=1e-12):
            raise ValueError("measurement covariance must be symmetric")
        if float(np.min(np.linalg.eigvalsh(covariance))) < -1e-12:
            raise ValueError("measurement covariance must be positive semidefinite")
        angle_indices = (1,) if group == "range_bearing" else (0,)
        return measurement, angle_indices, group

    def associate(
        self,
        tracks: list[TrackEstimate],
        observations: list[SensorObservation],
        ekf: ExtendedKalmanFilter,
        bearing_correction: float = 0.0,
    ) -> GroupAssociation:
        """Associate one measurement group and return the one-to-one matching.

        ``bearing_correction`` (rad) is subtracted from vision bearings before gating, so
        an estimated sensor bias can be removed; it is ignored for range-bearing groups.
        """
        result = GroupAssociation()
        if not observations:
            return result

        observations = sorted(
            observations,
            key=lambda obs: (obs.delivery_time, obs.capture_time, obs.observation_id),
        )
        tracks = sorted(tracks, key=lambda track: track.track_id)

        valid_observations: list[SensorObservation] = []
        valid_measurements: list[np.ndarray] = []
        valid_angles: list[tuple[int, ...]] = []
        group_name: str | None = None

        for observation in observations:
            try:
                pose = observation.observer_pose
                if pose is None:
                    raise ValueError("observation has no observer pose at capture time")
                measurement, angle_indices, group = self._measurement(observation)
                if group == "vision_bearing" and bearing_correction:
                    measurement = np.array([wrap_angle(float(measurement[0]) - bearing_correction)])
                if group_name is None:
                    group_name = group
                elif group != group_name:
                    raise ValueError("associate() received mixed measurement groups")
                valid_observations.append(observation)
                valid_measurements.append(measurement)
                valid_angles.append(angle_indices)
            except ValueError as exc:
                result.invalid.append((observation, str(exc)))

        if not valid_observations or not tracks:
            result.unmatched.extend(valid_observations)
            return result

        # The gate is chosen per observation from its own validated measurement
        # dimension, so 2-D and 3-D range/bearing observations may coexist.
        gates = [
            self.gate_for(group_name or "range_bearing", measurement.size)
            for measurement in valid_measurements
        ]
        evaluated = np.zeros(len(valid_observations), dtype=bool)
        cost_matrix = np.full((len(tracks), len(valid_observations)), np.inf)

        for row, track in enumerate(tracks):
            state = track.state_array()
            covariance = track.cov_array()
            for column, observation in enumerate(valid_observations):
                try:
                    pose = observation.observer_pose
                    assert pose is not None  # validated above
                    measurement = valid_measurements[column]
                    angle_indices = valid_angles[column]
                    group = observation.measurement_group()
                    if group == "range_bearing":
                        has_range_rate = "range_rate" in observation.measurements
                        predicted = ekf.measurement_range_bearing(state, pose)
                        if not has_range_rate:
                            predicted = predicted[:2]
                        jacobian = ekf.jacobian_range_bearing(state, pose)
                        if not has_range_rate:
                            jacobian = jacobian[:2, :]
                    else:
                        predicted = ekf.measurement_bearing(state, pose)
                        jacobian = ekf.jacobian_bearing(state, pose)
                    covariance_measurement = observation.get_measurement_cov()
                    if covariance_measurement is None:
                        raise ValueError("observation has no measurement covariance")
                    residual, innovation_covariance = ekf.innovation(
                        state,
                        covariance,
                        measurement,
                        predicted,
                        jacobian,
                        covariance_measurement,
                        angle_indices,
                    )
                    mahalanobis = float(
                        residual.T @ np.linalg.solve(innovation_covariance, residual)
                    )
                    if np.isfinite(mahalanobis):
                        evaluated[column] = True
                    if np.isfinite(mahalanobis) and mahalanobis <= gates[column]:
                        cost_matrix[row, column] = mahalanobis
                except (ValueError, np.linalg.LinAlgError):
                    # A numerically invalid pair cannot be associated. The
                    # observation remains unmatched and is handled explicitly
                    # by the tracker; it is not silently dropped here.
                    continue

        finite = np.isfinite(cost_matrix)
        if np.any(finite):
            assignment_cost = np.where(finite, cost_matrix, 1e12)
            rows, columns = linear_sum_assignment(assignment_cost)
            assigned_columns: set[int] = set()
            for assigned_row, assigned_column in zip(rows, columns, strict=True):
                if finite[assigned_row, assigned_column]:
                    track_id = tracks[assigned_row].track_id
                    result.matches[track_id] = valid_observations[assigned_column]
                    assigned_columns.add(int(assigned_column))
            for index, observation in enumerate(valid_observations):
                if index in assigned_columns:
                    continue
                result.unmatched.append(observation)
                if finite[:, index].any():
                    result.lost_competition.append(observation)
                elif evaluated[index]:
                    result.gate_rejected.append(observation)
        else:
            result.unmatched.extend(valid_observations)
            result.gate_rejected.extend(
                obs for index, obs in enumerate(valid_observations) if evaluated[index]
            )

        return result
