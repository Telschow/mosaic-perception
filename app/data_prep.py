"""Browser-free data preparation for the Streamlit workbench.

Everything the UI renders is built here so the rendering inputs can be tested
without a browser: the app module only wires these functions to Streamlit
widgets. The workbench runs every method in ``METHODS`` on the same world and
renders each record the run actually contains.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from mosaic_perception.domain.models import TrackStatus
from mosaic_perception.experiment import METHODS, PairedRun, RunRecord

SIMULATED_LABEL = "Simulated data — synthetic worlds, development seeds only."
LIMITATIONS_NOTE = (
    "Known limitations: see `docs/limitations.md`. Results are not evidence of "
    "real-world or hardware performance."
)

METHOD_SYMBOLS = {
    "range_only": "square",
    "fused": "triangle-up",
    "fused_bias_estimated": "diamond",
}

LIMITATIONS_LINES = [
    "Synthetic 2-D world; simplified sensor models.",
    "Vision-only track initiation is unsupported.",
    "Observations older than one tracker epoch are rejected and counted; "
    "one-step-lag retrodiction is opt-in.",
]


def format_metric(value: float | None, digits: int = 3) -> str:
    """Render a metric for text output; undefined metrics read N/A, never 0."""
    return "N/A" if value is None else f"{value:.{digits}f}"


def visible_methods(pair: PairedRun) -> list[tuple[str, RunRecord]]:
    """Methods in ``METHODS`` that this run contains, paired with their records."""
    records: dict[str, RunRecord | None] = {
        "range_only": pair.range_only,
        "fused": pair.fused,
        "fused_bias_estimated": pair.fused_bias_estimated,
    }
    return [(method, records[method]) for method in METHODS if records[method] is not None]


def build_metrics_rows(methods: list[tuple[str, RunRecord]]) -> list[dict]:
    """One row per method: headline accuracy plus the distance-only view."""
    rows = []
    for method_name, record in methods:
        result = record.result
        rows.append(
            {
                "method": method_name,
                "position_rmse_m": result.position_rmse,
                "position_rmse_distance_only_m": result.position_rmse_distance_only,
                "velocity_rmse_mps": result.velocity_rmse,
                "mota": result.mota,
                "idf1": result.idf1,
                "identity_switches": result.identity_switches,
                "recall": result.recall,
                "precision": result.precision,
                "coverage_95": result.position_coverage_95,
                "matched_samples": result.matched_samples,
                "ground_truth_samples": result.ground_truth_samples,
                "confirmed_track_samples": result.confirmed_track_samples,
                "num_confirmed_tracks": result.num_confirmed_tracks,
                "num_unmatched_confirmed_tracks": result.num_unmatched_confirmed_tracks,
                "mean_aoi_s": result.mean_age_of_information,
                "rejected_out_of_sequence": result.rejected_out_of_sequence,
                "pending_observations": result.pending_observations,
            }
        )
    return rows


def metrics_frame(methods: list[tuple[str, RunRecord]]) -> pd.DataFrame:
    return pd.DataFrame(build_metrics_rows(methods))


def build_scene_figure(pair: PairedRun, methods: list[tuple[str, RunRecord]]) -> go.Figure:
    """Ground truth (dashed) plus every confirmed/coasting track per method."""
    figure = go.Figure()
    states = pair.states
    for object_id in states[0].objects:
        figure.add_trace(
            go.Scatter(
                x=[state.objects[object_id].position.x for state in states],
                y=[state.objects[object_id].position.y for state in states],
                mode="lines",
                name=f"GT {object_id}",
                line={"dash": "dash", "width": 2},
            )
        )

    for method_name, record in methods:
        symbol = METHOD_SYMBOLS.get(method_name, "circle")
        for track in record.tracker.tracks.values():
            if track.status not in {TrackStatus.CONFIRMED, TrackStatus.COASTING}:
                continue
            figure.add_trace(
                go.Scatter(
                    x=[track.position()[0]],
                    y=[track.position()[1]],
                    mode="markers",
                    name=f"{method_name} {track.track_id}",
                    marker={"size": 10, "symbol": symbol},
                )
            )
    figure.update_layout(
        title="Ground truth (dashed) and final confirmed/coasting tracks (simulated)",
        xaxis_title="X (m)",
        yaxis_title="Y (m)",
        height=600,
    )
    return figure


def scenario_summary(pair: PairedRun) -> str:
    return (
        f"**Scenario:** {pair.scenario.name} | "
        f"**Seed:** {pair.scenario.seed} | "
        f"**Objects:** {pair.scenario.num_objects} | "
        f"**Observer trajectory:** {pair.scenario.observer_trajectory} | "
        f"{SIMULATED_LABEL}"
    )
