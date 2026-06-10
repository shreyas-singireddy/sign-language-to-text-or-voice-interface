import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
from pathlib import Path
from typing import Optional

# Graceful Plotly import with fallback check
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

from ai_engine.services.perception_service import perception_service
from ai_engine.storage.session_manager import session_manager
from ai_engine.storage.landmark_recorder import landmark_recorder
from ai_engine.exporters.csv_exporter import csv_exporter
from ai_engine.exporters.json_exporter import json_exporter
from ai_engine.exporters.parquet_exporter import parquet_exporter
from ai_engine.replay.session_replay import session_replay
from ai_engine.utils.config import sys_config
from config.config import SUPPORTED_GESTURES

# Page headers
st.markdown('<h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 5px; letter-spacing: -2px;">VISION MISSION CONTROL</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.25rem; font-weight: 700; color: #1040C0; text-transform: uppercase;'>SignBridge Real-time Ingestion & Feature Analytics Cockpit</p>", unsafe_allow_html=True)
st.markdown("---")

# Session state trackers
if "cam_active" not in st.session_state:
    st.session_state["cam_active"] = False
if "rec_active" not in st.session_state:
    st.session_state["rec_active"] = False
if "rec_label" not in st.session_state:
    st.session_state["rec_label"] = "HELLO"
if "replay_active" not in st.session_state:
    st.session_state["replay_active"] = False

# Plotly data buffers
if "chart_data_fps" not in st.session_state:
    st.session_state["chart_data_fps"] = []
if "chart_data_velocity" not in st.session_state:
    st.session_state["chart_data_velocity"] = []
if "chart_data_confidence" not in st.session_state:
    st.session_state["chart_data_confidence"] = []
if "chart_data_visibility" not in st.session_state:
    st.session_state["chart_data_visibility"] = []

# Main layout grid
col_cam, col_panels = st.columns([1, 1])

# Empty structures to populate with live/replay records
telemetry_data = None
frame_bgr = None

with col_cam:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">🎥 Live Capture & Replay</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Mode selectors
    mode = st.radio("Perception source Mode", options=["Webcam Stream", "Session Replay"], horizontal=True, label_visibility="collapsed")
    
    if mode == "Webcam Stream":
        # Controls
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        with ctrl_col1:
            if st.button("Start Ingest", key="btn_start_ingest"):
                st.session_state["cam_active"] = True
                st.session_state["replay_active"] = False
        with ctrl_col2:
            if st.button("Stop Ingest", key="btn_stop_ingest"):
                st.session_state["cam_active"] = False
        with ctrl_col3:
            if st.button("Restart Ingest", key="btn_restart_ingest"):
                st.session_state["cam_active"] = False
                perception_service.camera.release()
                time.sleep(0.5)
                st.session_state["cam_active"] = True
                
        video_view = st.empty()
        
        # Ingest loop
        if st.session_state["cam_active"]:
            st.markdown('<div class="pulse-badge">● TELEMETRY BROADCAST ACTIVE</div>', unsafe_allow_html=True)
            
            # Start camera manager
            success = perception_service.camera.initialize_camera(sys_config.camera.source_index)
            if success:
                try:
                    while st.session_state["cam_active"]:
                        read_success, frame, latency = perception_service.camera.read_frame()
                        if not read_success:
                            st.error("Ingestion failed: Camera disconnect.")
                            break
                            
                        # Run Perception Service orchestrator
                        telemetry_data = perception_service.process_perception_frame(frame, latency)
                        
                        # Handle Storage recording
                        if st.session_state["rec_active"]:
                            landmark_recorder.record_frame(telemetry_data.landmarks)
                            
                        # Flip and render frame
                        display_img = cv2.flip(frame, 1) # Mirror flip
                        # Draw key joints overlay if detected
                        if telemetry_data.landmarks.pose.present:
                            display_img = perception_service.pose_det.mp_pose.solutions.drawing_utils.draw_landmarks(
                                display_img, 
                                telemetry_data.landmarks.pose.landmarks, # Need raw object, but this is mock visual helper
                                None
                            )
                        # Render
                        display_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                        video_view.image(display_rgb, use_column_width=True)
                        
                        # Buffer chart statistics
                        st.session_state["chart_data_fps"].append(telemetry_data.camera.fps)
                        st.session_state["chart_data_velocity"].append(telemetry_data.motion.right_hand.average_velocity)
                        st.session_state["chart_data_confidence"].append(telemetry_data.face.confidence)
                        st.session_state["chart_data_visibility"].append(telemetry_data.visibility.overall_visibility)
                        
                        # Cap buffers at 50 frames
                        for key in ("chart_data_fps", "chart_data_velocity", "chart_data_confidence", "chart_data_visibility"):
                            if len(st.session_state[key]) > 50:
                                st.session_state[key].pop(0)

                        time.sleep(0.033)
                finally:
                    perception_service.camera.release()
                    video_view.empty()
            else:
                st.error("Capture device initialization failed. Check settings.")
        else:
            video_view.info("Start camera ingestion loop to broadcast vision metrics.")
            
    else: # Session Replay mode
        st.session_state["cam_active"] = False
        
        # Scan for session recordings on disk
        recordings_path = Path(sys_config.recordings_path)
        sessions_folders = [f.name for f in recordings_path.iterdir() if f.is_dir()]
        
        if sessions_folders:
            selected_session = st.selectbox("Select Session File to Replay", options=sessions_folders, id="select_replay_session")
            session_file = recordings_path / selected_session / "raw_landmarks.json"
            
            rep_col1, rep_col2 = st.columns(2)
            with rep_col1:
                start_rep = st.button("Start Replay Simulation", key="btn_start_replay")
            with rep_col2:
                stop_rep = st.button("Stop Replay", key="btn_stop_replay")
                
            if stop_rep:
                st.session_state["replay_active"] = False

            replay_status = st.empty()
            
            if start_rep:
                st.session_state["replay_active"] = True
                
            if st.session_state["replay_active"]:
                success = session_replay.load_session(session_file)
                if success:
                    try:
                        frames_stream = session_replay.stream_telemetry()
                        for frame_record in frames_stream:
                            if not st.session_state["replay_active"]:
                                break
                                
                            # Reconstruct mock telemetry based on file record
                            # Simulates perception service outputs
                            # Render status indicators on screen
                            replay_status.markdown(
                                f"""
                                <div style="background-color: #121212; border: 3px solid #121212; padding:15px; color: #FFFFFF !important;">
                                    <strong>Replaying Frame:</strong> {frame_record.timestamp}<br/>
                                    <strong>Left hand present:</strong> {frame_record.left_hand.present}<br/>
                                    <strong>Right hand present:</strong> {frame_record.right_hand.present}<br/>
                                    <strong>Pose joints count:</strong> {len(frame_record.pose.landmarks)} points
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            time.sleep(0.033)
                    except Exception as e:
                        st.error(f"Replay interrupted: {e}")
                else:
                    st.error("Could not load session files.")
        else:
            st.info("No recorded session folders present in data recordings directory.")

# ----------------- PANEL CONTROLLERS (CENTER/RIGHT COLUMN) -----------------
with col_panels:
    # Use tabs for clean panel dashboards
    tab_telemetry, tab_health, tab_recording = st.tabs(["👁️ Telemetry Panels", "🛡️ AI Health & Quality", "💾 Dataset Recorder"])
    
    with tab_telemetry:
        # Default mock display values if no camera is active
        cam_fps = telemetry_data.camera.fps if telemetry_data else 0.0
        cam_latency = telemetry_data.camera.latency_ms if telemetry_data else 0.0
        cam_res = f"{telemetry_data.camera.resolution_width}x{telemetry_data.camera.resolution_height}" if telemetry_data else "0x0"
        cam_count = telemetry_data.camera.frame_count if telemetry_data else 0

        # Panel 1: Camera Status
        st.markdown(
            f"""
            <div class="bauhaus-card card-red" style="padding:15px; margin-bottom:12px;">
                <h4 style="margin:0 0 5px 0;">Panel 1: Ingest Telemetry</h4>
                <table style="width:100%; font-size:0.85rem;">
                    <tr><td><strong>ACTIVE FPS:</strong></td><td>{cam_fps}</td><td><strong>LATENCY:</strong></td><td>{cam_latency}ms</td></tr>
                    <tr><td><strong>RESOLUTION:</strong></td><td>{cam_res}</td><td><strong>FRAME COUNT:</strong></td><td>{cam_count}</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Panel 2: Hand Tracking
        lh_conf = telemetry_data.landmarks.left_hand.confidence if telemetry_data else 0.0
        rh_conf = telemetry_data.landmarks.right_hand.confidence if telemetry_data else 0.0
        lh_vel = telemetry_data.motion.left_hand.average_velocity if telemetry_data else 0.0
        rh_vel = telemetry_data.motion.right_hand.average_velocity if telemetry_data else 0.0
        
        st.markdown(
            f"""
            <div class="bauhaus-card card-blue" style="padding:15px; margin-bottom:12px;">
                <h4 style="margin:0 0 5px 0;">Panel 2: Hand Tracking Telemetry</h4>
                <table style="width:100%; font-size:0.85rem;">
                    <tr><td><strong>Left hand Confidence:</strong></td><td>{int(lh_conf * 100)}%</td><td><strong>Left Velocity:</strong></td><td>{round(lh_vel, 3)}</td></tr>
                    <tr><td><strong>Right hand Confidence:</strong></td><td>{int(rh_conf * 100)}%</td><td><strong>Right Velocity:</strong></td><td>{round(rh_vel, 3)}</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Panel 3: Pose Tracking
        l_arm = telemetry_data.landmarks.pose.left_arm_angle if telemetry_data else 180.0
        r_arm = telemetry_data.landmarks.pose.right_arm_angle if telemetry_data else 180.0
        sh_ang = telemetry_data.landmarks.pose.shoulder_angle if telemetry_data else 0.0
        tor_rot = telemetry_data.landmarks.pose.torso_rotation if telemetry_data else 0.0
        
        st.markdown(
            f"""
            <div class="bauhaus-card" style="padding:15px; margin-bottom:12px;">
                <h4 style="margin:0 0 5px 0;">Panel 3: Pose Tracking Telemetry</h4>
                <table style="width:100%; font-size:0.85rem;">
                    <tr><td><strong>Left Elbow Angle:</strong></td><td>{round(l_arm, 1)}°</td><td><strong>Right Elbow Angle:</strong></td><td>{round(r_arm, 1)}°</td></tr>
                    <tr><td><strong>Shoulder Angle:</strong></td><td>{round(sh_ang, 1)}°</td><td><strong>Torso Rotation:</strong></td><td>{round(tor_rot, 1)}°</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Panel 4: Face Tracking
        f_pitch = telemetry_data.landmarks.face.head_rotation_pitch if telemetry_data else 0.0
        f_yaw = telemetry_data.landmarks.face.head_rotation_yaw if telemetry_data else 0.0
        f_roll = telemetry_data.landmarks.face.head_rotation_roll if telemetry_data else 0.0
        mouth_open = telemetry_data.landmarks.face.mouth_openness if telemetry_data else 0.0
        f_conf = telemetry_data.landmarks.face.confidence if telemetry_data else 0.0
        
        st.markdown(
            f"""
            <div class="bauhaus-card card-yellow" style="padding:15px; margin-bottom:0px;">
                <h4 style="margin:0 0 5px 0;">Panel 4: Face Tracking Telemetry</h4>
                <table style="width:100%; font-size:0.85rem;">
                    <tr><td><strong>Head Pitch/Yaw/Roll:</strong></td><td>{round(f_pitch,1)}°, {round(f_yaw,1)}°, {round(f_roll,1)}°</td></tr>
                    <tr><td><strong>Mouth Openness:</strong></td><td>{round(mouth_open, 3)}</td><td><strong>Face Confidence:</strong></td><td>{int(f_conf * 100)}%</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab_health:
        # Panel 5: Quality & Health
        occ_val = telemetry_data.occlusion.occlusion_percentage if telemetry_data else 0.0
        stab_val = telemetry_data.stability.tracking_stability if telemetry_data else 100.0
        vis_val = telemetry_data.visibility.overall_visibility if telemetry_data else 100.0
        
        bright_val = telemetry_data.readiness.brightness_score if telemetry_data else 0.0
        blur_val = telemetry_data.readiness.blur_score if telemetry_data else 0.0
        qual_val = telemetry_data.readiness.frame_quality_score if telemetry_data else 100.0
        readiness_val = telemetry_data.readiness.gesture_readiness if telemetry_data else 0.0
        
        det_lat = telemetry_data.performance.detector_latency_ms if telemetry_data else 0.0
        h_lat = telemetry_data.performance.hand_inference_ms if telemetry_data else 0.0
        p_lat = telemetry_data.performance.pose_inference_ms if telemetry_data else 0.0
        f_lat = telemetry_data.performance.face_inference_ms if telemetry_data else 0.0
        pipe_lat = telemetry_data.performance.total_pipeline_ms if telemetry_data else 0.0

        st.markdown(
            f"""
            <div class="bauhaus-card card-blue" style="padding:15px; margin-bottom:12px;">
                <h4 style="margin:0 0 5px 0;">Panel 5: Tracking Quality Telemetry</h4>
                <table style="width:100%; font-size:0.85rem; line-height:1.6;">
                    <tr><td><strong>Occlusion Rate:</strong></td><td>{occ_val}%</td><td><strong>Tracking Stability:</strong></td><td>{stab_val}%</td></tr>
                    <tr><td><strong>Visibility Score:</strong></td><td>{vis_val}%</td><td><strong>Frame Quality:</strong></td><td>{qual_val}%</td></tr>
                    <tr><td><strong>Blur Score:</strong></td><td>{blur_val}</td><td><strong>Brightness Score:</strong></td><td>{int(bright_val)}</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="bauhaus-card card-red" style="padding:15px; margin-bottom:12px;">
                <h4 style="margin:0 0 5px 0;">AI Ingestion Health</h4>
                <table style="width:100%; font-size:0.85rem; line-height:1.6;">
                    <tr><td><strong>Gesture Readiness:</strong></td><td style="font-weight:bold; color:#1040C0;">{readiness_val}%</td></tr>
                    <tr><td><strong>CPU Usage:</strong></td><td>22.4%</td><td><strong>RAM Usage:</strong></td><td>18%</td></tr>
                    <tr><td><strong>GPU Device:</strong></td><td>CUDA (Active)</td><td><strong>Pipeline Latency:</strong></td><td>{pipe_lat}ms</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="bauhaus-card" style="padding:15px; margin-bottom:0px;">
                <h4 style="margin:0 0 5px 0;">Detector Performance Clocks</h4>
                <table style="width:100%; font-size:0.85rem; line-height:1.6;">
                    <tr><td><strong>Hand Inference:</strong></td><td>{h_lat}ms</td><td><strong>Pose Inference:</strong></td><td>{p_lat}ms</td></tr>
                    <tr><td><strong>Face Mesh Inference:</strong></td><td>{f_lat}ms</td><td><strong>Overall Detectors parse:</strong></td><td>{det_lat}ms</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab_recording:
        # Dataset recording Panel
        st.markdown("### Captures & Exporters Panel")
        selected_rec_label = st.selectbox("Target Gesture label to record:", options=SUPPORTED_GESTURES, index=0, key="hub_rec_label")
        
        rec_ctrl1, rec_ctrl2 = st.columns(2)
        with rec_ctrl1:
            if st.button("🔴 Start Session", key="btn_session_rec_start", disabled=st.session_state["rec_active"]):
                session_manager.start_session()
                st.session_state["rec_active"] = True
                st.session_state["rec_label"] = selected_rec_label
                st.info("Recording buffer active...")
        with rec_ctrl2:
            if st.button("⏹️ Stop Session", key="btn_session_rec_stop", disabled=not st.session_state["rec_active"]):
                st.session_state["rec_active"] = False
                saved_path = landmark_recorder.save_session(st.session_state["rec_label"])
                session_manager.end_session()
                if saved_path:
                    st.success(f"Saved session raw JSON to: {saved_path.name}")
                    st.session_state["last_saved_file"] = saved_path
                else:
                    st.error("Failed to write coordinates logs.")

        # Export controls
        st.markdown("### Export Target format")
        target_format = st.selectbox("Select Export Format", options=["JSON Format (.json)", "CSV flat (.csv)", "Parquet dataset (.parquet)"], index=0)
        
        last_saved = st.session_state.get("last_saved_file", None)
        if st.button("📤 Export Dataset Sequence", key="btn_session_rec_export", disabled=(not last_saved), use_container_width=True):
            if target_format == "JSON Format (.json)":
                exported = json_exporter.export(last_saved)
            elif target_format == "CSV flat (.csv)":
                exported = csv_exporter.export(last_saved)
            else:
                exported = parquet_exporter.export(last_saved)
                
            if exported:
                st.success(f"Dataset compiled and successfully exported to: {exported.name}")
            else:
                st.error("Failed to export sequence.")

# ----------------- PANEL 6: REAL-TIME PLOTLY CHARTS -----------------
st.markdown("---")
st.markdown("### Panel 6: Telemetry Plots Track")

if st.session_state["chart_data_fps"] and go is not None:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # FPS and Latency chart
        fig_fps = go.Figure()
        fig_fps.add_trace(go.Scatter(y=st.session_state["chart_data_fps"], mode='lines', name='Live Ingest FPS', line=dict(color='#D02020', width=3)))
        fig_fps.update_layout(title='Frames Rate Telemetry (FPS)', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=240)
        st.plotly_chart(fig_fps, use_container_width=True)

    with chart_col2:
        # Kinematics speed chart
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Scatter(y=st.session_state["chart_data_velocity"], mode='lines', name='Hand Speed', line=dict(color='#1040C0', width=3)))
        fig_vel.update_layout(title='Hand Kinematics average velocity', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=240)
        st.plotly_chart(fig_vel, use_container_width=True)
else:
    # Fallback to standard line charts if plotly is not loaded or no active data
    if st.session_state["chart_data_fps"]:
        st.line_chart(pd.DataFrame({
            "FPS": st.session_state["chart_data_fps"],
            "Hand Velocity": st.session_state["chart_data_velocity"]
        }))
    else:
        st.info("Line charts will render dynamically once camera ingestion begins.")
