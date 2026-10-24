"""
Mosaic Streamlit workbench.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from mosaic_perception.simulation.world import SyntheticWorld
from mosaic_perception.sensors import RangeBearingSensor, VisionBearingSensor
from mosaic_perception.domain.models import SensorConfig
from mosaic_perception.tracking import MultiSensorTracker
from mosaic_perception.evaluation.metrics import TrackingEvaluator

st.set_page_config(page_title="Mosaic Perception Workbench", layout="wide")

st.title("🔍 Mosaic: Multi-Sensor Perception Workbench")
st.markdown("*A reproducible workbench for investigating when sensor fusion helps or hurts.*")

# Sidebar
st.sidebar.header("Configuration")

scenario = st.sidebar.selectbox("Scenario", ["nominal", "vision_dropout", "range_dropout", "false_observations"])
seed = st.sidebar.slider("Random Seed", 0, 100, 42)
duration = st.sidebar.slider("Duration (s)", 5.0, 20.0, 10.0)
num_objects = st.sidebar.slider("Number of Objects", 1, 5, 3)
use_vision = st.sidebar.checkbox("Enable Vision Fusion", value=True)

if st.sidebar.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        # Create world
        world = SyntheticWorld(seed=seed, duration=duration, dt=0.1, num_objects=num_objects)
        
        # Configure sensors
        rng_sensor = np.random.RandomState(seed + 1000)
        range_config = SensorConfig(
            sensor_id="range1", sensor_type="range_bearing", frame_rate=10.0,
            noise_std={"range": 0.5, "bearing": 0.01, "range_rate": 0.1},
            detection_probability=0.95 if scenario != "range_dropout" else 0.6,
            false_alarm_rate=0.01 if scenario != "false_observations" else 0.1,
        )
        range_sensor = RangeBearingSensor(range_config, rng_sensor)
        
        vision_config = SensorConfig(
            sensor_id="vision1", sensor_type="vision_bearing", frame_rate=10.0,
            noise_std={"bearing": 0.005},
            detection_probability=0.9 if scenario != "vision_dropout" else 0.4,
            false_alarm_rate=0.02 if scenario != "false_observations" else 0.15,
        )
        vision_sensor = VisionBearingSensor(vision_config, np.random.RandomState(seed + 2000))
        
        states = world.get_all_states()
        
        # Run range-only
        tracker_range = MultiSensorTracker(dt=0.1, use_vision=False)
        for world_state in states:
            obs = range_sensor.generate_observations(world_state, world_state.time)
            for o in obs: o._true_object_id = None
            tracker_range.process_observations(obs, world_state.time)
        
        # Run fused
        tracker_fused = MultiSensorTracker(dt=0.1, use_vision=use_vision)
        for world_state in states:
            obs_range = range_sensor.generate_observations(world_state, world_state.time)
            obs_vision = vision_sensor.generate_observations(world_state, world_state.time)
            obs = obs_range + obs_vision
            for o in obs: o._true_object_id = None
            tracker_fused.process_observations(obs, world_state.time)
        
        # Evaluate
        evaluator = TrackingEvaluator()
        result_range = evaluator.evaluate(tracker_range.tracks, states, scenario, seed, "range_only")
        result_fused = evaluator.evaluate(tracker_fused.tracks, states, scenario, seed, "fused")
        
        st.session_state['results'] = {
            'world': world,
            'states': states,
            'tracker_range': tracker_range,
            'tracker_fused': tracker_fused,
            'result_range': result_range,
            'result_fused': result_fused,
            'scenario': scenario
        }

# Display results
if 'results' in st.session_state:
    res = st.session_state['results']
    
    # Metrics table
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Range-Only Tracking")
        st.metric("Position RMSE", f"{res['result_range'].position_rmse:.3f} m" if res['result_range'].position_rmse else "N/A")
        st.metric("Confirmed Tracks", res['result_range'].num_confirmed_tracks)
        st.metric("Total Tracks", res['result_range'].num_tracks)
    
    with col2:
        st.subheader("Fused Tracking")
        st.metric("Position RMSE", f"{res['result_fused'].position_rmse:.3f} m" if res['result_fused'].position_rmse else "N/A")
        st.metric("Confirmed Tracks", res['result_fused'].num_confirmed_tracks)
        st.metric("Total Tracks", res['result_fused'].num_tracks)
    
    # Scene visualization
    st.subheader("2D Scene Visualization")
    
    fig = go.Figure()
    
    # Plot ground truth
    states = res['states']
    for i, obj_id in enumerate(states[0].objects.keys()):
        xs = [s.objects[obj_id].position.x for s in states]
        ys = [s.objects[obj_id].position.y for s in states]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name=f'GT {obj_id}', 
                                line=dict(dash='dash', width=2)))
    
    # Plot range-only tracks
    for track_id, track in res['tracker_range'].tracks.items():
        if track.status.value == 'confirmed':
            fig.add_trace(go.Scatter(x=[track.position()[0]], y=[track.position()[1]], 
                                    mode='markers', name=f'Range Track {track_id[:8]}',
                                    marker=dict(size=10, symbol='square')))
    
    # Plot fused tracks
    for track_id, track in res['tracker_fused'].tracks.items():
        if track.status.value == 'confirmed':
            fig.add_trace(go.Scatter(x=[track.position()[0]], y=[track.position()[1]], 
                                    mode='markers', name=f'Fused Track {track_id[:8]}',
                                    marker=dict(size=10, symbol='triangle-up')))
    
    fig.update_layout(
        title="Ground Truth (dashed) vs Tracks (markers)",
        xaxis_title="X (m)",
        yaxis_title="Y (m)",
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Scenario info
    st.subheader("Scenario Information")
    st.info(f"**Scenario:** {res['scenario']} | **Seed:** {seed} | **Objects:** {num_objects} | "
            f"This is synthetic data - not representative of real-world performance.")
else:
    st.info("Configure parameters in the sidebar and click 'Run Simulation' to start.")
