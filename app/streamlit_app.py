"""
Mosaic Streamlit workbench.

Uses the shared experiment runner so the UI and CLI execute the same pipeline.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from mosaic_perception.domain.models import TrackStatus
from mosaic_perception.experiment import run_pair
from mosaic_perception.scenarios import available_scenarios, resolve_scenario

st.set_page_config(page_title="Mosaic Perception Workbench", layout="wide")

st.title("Mosaic: Multi-Sensor Perception Workbench")
st.markdown("*A reproducible workbench for investigating when sensor fusion helps or hurts.*")

st.sidebar.header("Configuration")
scenario_name = st.sidebar.selectbox("Scenario", available_scenarios())
seed = st.sidebar.slider("Random seed", 0, 100, 42)
duration = st.sidebar.slider("Duration (s)", 2.0, 20.0, 5.0)
num_objects = st.sidebar.slider("Number of objects", 1, 5, 3)
show_fused = st.sidebar.checkbox("Show fused method", value=True)
run_button = st.sidebar.button("Run simulation")


def format_metric(value: float | None, digits: int = 3) -> str:
    return "N/A" if value is None else f"{value:.{digits}f}"


if run_button:
    with st.spinner("Running simulation..."):
        scenario = resolve_scenario(
            scenario_name,
            seed=seed,
            duration=duration,
            num_objects=num_objects,
        )
        pair = run_pair(scenario)
        st.session_state["results"] = pair
        st.session_state["scenario_name"] = scenario_name
        st.session_state["seed"] = seed
        st.session_state["num_objects"] = num_objects

if "results" in st.session_state:
    pair = st.session_state["results"]
    methods = [("range_only", pair.range_only)]
    if show_fused:
        methods.append(("fused", pair.fused))

    st.subheader("Metrics")
    rows = []
    for method_name, record in methods:
        result = record.result
        rows.append(
            {
                "method": method_name,
                "position_rmse_m": result.position_rmse,
                "velocity_rmse_mps": result.velocity_rmse,
                "recall": result.recall,
                "precision": result.precision,
                "coverage_95": result.position_coverage_95,
                "matched_samples": result.matched_samples,
                "ground_truth_samples": result.ground_truth_samples,
                "confirmed_track_samples": result.confirmed_track_samples,
                "confirmed_tracks": result.num_confirmed_tracks,
                "false_tracks": result.num_false_tracks,
                "mean_aoi_s": result.mean_age_of_information,
                "rejected_out_of_sequence": result.rejected_out_of_sequence,
                "pending_observations": result.pending_observations,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.caption(
        "Accuracy metrics use one-to-one gated matching at each timestamp. "
        "Recall is relative to all ground-truth object samples; precision is "
        "relative to all confirmed/coasting track samples. `track_fragmentation` "
        "is not implemented and is omitted rather than reported as zero."
    )

    st.subheader("Scene")
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

    symbols = {"range_only": "square", "fused": "triangle-up"}
    for method_name, record in methods:
        for track in record.tracker.tracks.values():
            if track.status not in {TrackStatus.CONFIRMED, TrackStatus.COASTING}:
                continue
            figure.add_trace(
                go.Scatter(
                    x=[track.position()[0]],
                    y=[track.position()[1]],
                    mode="markers",
                    name=f"{method_name} {track.track_id}",
                    marker={"size": 10, "symbol": symbols[method_name]},
                )
            )
    figure.update_layout(
        title="Ground truth (dashed) and final confirmed/coasting tracks",
        xaxis_title="X (m)",
        yaxis_title="Y (m)",
        height=600,
    )
    st.plotly_chart(figure, use_container_width=True)

    st.subheader("Scenario")
    st.info(
        f"**Scenario:** {st.session_state['scenario_name']} | "
        f"**Seed:** {st.session_state['seed']} | "
        f"**Objects:** {st.session_state['num_objects']} | "
        f"**Observer trajectory:** {pair.scenario.observer_trajectory}"
    )
    with st.expander("Known limitations"):
        st.markdown(
            "- Synthetic 2-D world; simplified sensor models.\n"
            "- Vision-only track initiation is unsupported.\n"
            "- Observations older than one tracker epoch are rejected and counted, "
            "not replayed.\n"
            "- `track_fragmentation` is not implemented.\n"
            "- Results are not evidence of real-world or hardware performance."
        )
else:
    st.info("Configure parameters in the sidebar and click 'Run simulation'.")
