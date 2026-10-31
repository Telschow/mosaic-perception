"""
Mosaic Streamlit workbench.

Uses the shared experiment runner so the UI and CLI execute the same pipeline.
All rendering data is built by ``data_prep`` (browser-free, unit-tested); this
module only wires it to widgets.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# ``streamlit run app/streamlit_app.py`` executes this file as a script, so
# this directory is not importable until it is added to sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_prep import (  # noqa: E402
    DEFAULT_SEED,
    LIMITATIONS_LINES,
    LIMITATIONS_NOTE,
    MAX_DEV_SEED,
    SIMULATED_LABEL,
    build_scene_figure,
    metrics_frame,
    scenario_summary,
    visible_methods,
)

from mosaic_perception.experiment import run_pair
from mosaic_perception.scenarios import available_scenarios, resolve_scenario

st.set_page_config(page_title="Mosaic Perception Workbench", layout="wide")

st.title("Mosaic: Multi-Sensor Perception Workbench")
st.markdown("*A reproducible workbench for investigating when sensor fusion helps or hurts.*")
st.caption(SIMULATED_LABEL)

st.sidebar.header("Configuration")
scenario_name = st.sidebar.selectbox("Scenario", available_scenarios())
seed = st.sidebar.slider("Development seed", 0, MAX_DEV_SEED, DEFAULT_SEED)
duration = st.sidebar.slider("Duration (s)", 2.0, 20.0, 5.0)
num_objects = st.sidebar.slider("Number of objects", 1, 5, 3)
run_button = st.sidebar.button("Run simulation")

if run_button:
    with st.spinner("Running simulation..."):
        scenario = resolve_scenario(
            scenario_name,
            seed=seed,
            duration=duration,
            num_objects=num_objects,
        )
        pair = run_pair(scenario, include_bias_estimation=True)
        st.session_state["results"] = pair

if "results" in st.session_state:
    pair = st.session_state["results"]
    methods = visible_methods(pair)

    st.subheader("Metrics")
    st.caption(f"{SIMULATED_LABEL} {LIMITATIONS_NOTE}")
    st.dataframe(metrics_frame(methods), use_container_width=True)
    st.caption(
        "Position RMSE appears twice: `position_rmse_m` under the headline "
        "continuity-preferring matcher, `position_rmse_distance_only_m` under "
        "distance-only matching. `N/A` means undefined, never zero."
    )

    st.subheader("Scene")
    st.caption(f"{SIMULATED_LABEL} {LIMITATIONS_NOTE}")
    st.plotly_chart(build_scene_figure(pair, methods), use_container_width=True)

    st.subheader("Scenario")
    st.info(scenario_summary(pair))
    with st.expander("Known limitations"):
        st.markdown(
            f"{LIMITATIONS_NOTE}\n\n" + "\n".join(f"- {line}" for line in LIMITATIONS_LINES)
        )
        st.markdown("Full text: [`docs/limitations.md`](docs/limitations.md)")
else:
    st.info("Configure parameters in the sidebar and click 'Run simulation'.")
