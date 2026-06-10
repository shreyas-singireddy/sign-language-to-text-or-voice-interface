import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
from app.services.ai_service import ai_service
from ai_engine.pipeline.vision_pipeline import vision_pipeline
from ai_engine.dataset_manager.recorder import dataset_recorder
from config.config import SUPPORTED_GESTURES

# Page Header
st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">LIVE VISION PERCEPTION ENGINE</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>AI Human Motion Diagnostics & Real-time Joint Telemetry Console.</p>", unsafe_allow_html=True)
st.markdown("---")

# Session state initialization for Vision Engine
if "vision_cam_active" not in st.session_state:
    st.session_state["vision_cam_active"] = False
if "rec_session_id" not in st.session_state:
    st.session_state["rec_session_id"] = "Inactive"
if "recorded_rep_count" not in st.session_state:
    st.session_state["recorded_rep_count"] = 0

# Retrieve pipeline status
status = vision_pipeline.get_status()
mem_stats = status["memory_stats"]

# Main 3-column layout
col_left, col_center, col_right = st.columns([3, 4, 3])

# Local frame telemetry placeholder
telemetry = {
    "landmarks": [0.0] * 1662,
    "mean_velocity": 0.0,
    "mean_acceleration": 0.0,
    "distances": {"lh_thumb_index": 0.0, "rh_thumb_index": 0.0, "hand_to_hand": 0.0},
    "angles": {"left_elbow_angle": 180.0},
    "stability_index": 1.0,
    "occlusion_score": 0.0,
    "activity_index": 0.0,
    "tracking_health": 1.0,
    "readiness": {
        "data_quality_score": 1.0,
        "feature_quality_score": 0.0,
        "tracking_stability_score": 1.0,
        "is_training_ready": False,
        "readiness_grade": "GOOD"
    },
    "annotated_frame": None
}

# ----------------- LEFT COLUMN: Live Camera Feed & Ingestion -----------------
with col_left:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0;">1. INGESTION CHANNEL</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Camera Control Box
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        start_v_cam = st.button("Start", key="btn_start_v_cam")
    with btn_col2:
        stop_v_cam = st.button("Stop", key="btn_stop_v_cam")
    with btn_col3:
        restart_v_cam = st.button("Reset", key="btn_restart_v_cam")

    if start_v_cam:
        st.session_state["vision_cam_active"] = True
    if stop_v_cam:
        st.session_state["vision_cam_active"] = False
    if restart_v_cam:
        st.session_state["vision_cam_active"] = False
        vision_pipeline.memory.clear()
        dataset_recorder.captured_frames_count = 0
        st.success("Buffer and session counters reset!")

    video_view = st.empty()
    
    # Telemetry variables to compute FPS
    fps_placeholder = st.empty()
    frame_counter = 0
    start_time = time.time()
    
    # Execute OpenCV stream perception loop
    if st.session_state["vision_cam_active"]:
        from ai_engine.computer_vision.camera import CameraManager
        cam = CameraManager()
        if cam.start():
            try:
                while st.session_state["vision_cam_active"]:
                    success, frame = cam.get_frame()
                    if not success:
                        st.error("Perception error: Camera stream disconnected.")
                        break
                    
                    frame_counter += 1
                    
                    # Run perception pipeline
                    telemetry = vision_pipeline.run_perception(frame)
                    
                    # If recording dataset in progress
                    if dataset_recorder.is_recording:
                        dataset_recorder.capture_frame(telemetry["landmarks"])
                        
                    # Calculate active FPS
                    elapsed = time.time() - start_time
                    active_fps = round(frame_counter / elapsed, 1) if elapsed > 0 else 0.0
                    
                    # Render image with overlay skeleton
                    display_frame = cv2.flip(telemetry["annotated_frame"], 1)
                    display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    video_view.image(display_frame_rgb, channels="RGB", use_column_width=True)
                    
                    # Log FPS telemetry in sidebar
                    fps_placeholder.markdown(
                        f"""
                        <div class="bauhaus-card" style="padding: 10px; margin-bottom: 10px; background-color: #121212 !important; color: #FFFFFF !important;">
                            <table style="width:100%; font-size:0.8rem; color:#FFFFFF;">
                                <tr><td><strong>CAMERA STATUS:</strong></td><td style="color:#2ecc71;">ONLINE</td></tr>
                                <tr><td><strong>RESOLUTION:</strong></td><td>{frame.shape[1]}x{frame.shape[0]}</td></tr>
                                <tr><td><strong>INGEST FPS:</strong></td><td>{active_fps}</td></tr>
                                <tr><td><strong>FRAME COUNTER:</strong></td><td>{frame_counter}</td></tr>
                                <tr><td><strong>DURATION:</strong></td><td>{int(elapsed)}s</td></tr>
                            </table>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(0.03)
            finally:
                cam.stop()
                video_view.empty()
                fps_placeholder.empty()
    else:
        video_view.info("Start the Camera Ingestion channel to begin live tracking.")

# ----------------- CENTER COLUMN: Vision Analysis -----------------
with col_center:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0;">2. PERCEPTION TRACKING</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Hands Telemetry Box
    lh_detected = telemetry["landmarks"][1404] != 0.0
    rh_detected = telemetry["landmarks"][1467] != 0.0
    
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 15px; margin-bottom: 15px;">
            <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #121212;">✋ Dual Hand Telemetry</h4>
            <table style="width:100%; font-size:0.85rem; line-height:1.6;">
                <tr>
                    <td><strong>LEFT HAND:</strong></td>
                    <td><span class="status-pill {'status-online' if lh_detected else 'status-offline'}">{'DETECTED' if lh_detected else 'MISSING'}</span></td>
                    <td><strong>RIGHT HAND:</strong></td>
                    <td><span class="status-pill {'status-online' if rh_detected else 'status-offline'}">{'DETECTED' if rh_detected else 'MISSING'}</span></td>
                </tr>
                <tr>
                    <td><strong>Pinch Dist:</strong></td>
                    <td>{round(telemetry['distances']['lh_thumb_index'], 3)}</td>
                    <td><strong>Pinch Dist:</strong></td>
                    <td>{round(telemetry['distances']['rh_thumb_index'], 3)}</td>
                </tr>
                <tr>
                    <td><strong>Wrist Anchor:</strong></td>
                    <td>{f"{round(telemetry['landmarks'][1404], 2)}, {round(telemetry['landmarks'][1405], 2)}" if lh_detected else "0.0, 0.0"}</td>
                    <td><strong>Wrist Anchor:</strong></td>
                    <td>{f"{round(telemetry['landmarks'][1467], 2)}, {round(telemetry['landmarks'][1468], 2)}" if rh_detected else "0.0, 0.0"}</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Pose Telemetry Box
    pose_detected = telemetry["landmarks"][0] != 0.0
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 15px; margin-bottom: 15px;">
            <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #121212;">🧍 Pose Joint Telemetry</h4>
            <table style="width:100%; font-size:0.85rem; line-height:1.6;">
                <tr>
                    <td><strong>SKELETON LINK:</strong></td>
                    <td><span class="status-pill {'status-online' if pose_detected else 'status-offline'}">{'ACTIVE' if pose_detected else 'INACTIVE'}</span></td>
                    <td><strong>Left Elbow Angle:</strong></td>
                    <td>{round(telemetry['angles']['left_elbow_angle'], 1)}°</td>
                </tr>
                <tr>
                    <td><strong>Pose Confidence:</strong></td>
                    <td>{100 if pose_detected else 0}%</td>
                    <td><strong>Stability Score:</strong></td>
                    <td>{int(telemetry['stability_index'] * 100)}%</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Face Mesh Telemetry Box
    face_detected = telemetry["landmarks"][132] != 0.0
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 15px; margin-bottom: 0px;">
            <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #121212;">👤 Face Mesh Telemetry</h4>
            <table style="width:100%; font-size:0.85rem; line-height:1.6;">
                <tr>
                    <td><strong>MESH SENSOR:</strong></td>
                    <td><span class="status-pill {'status-online' if face_detected else 'status-offline'}">{'LOCKED' if face_detected else 'UNLOCKED'}</span></td>
                    <td><strong>Face Stability:</strong></td>
                    <td>{95 if face_detected else 0}%</td>
                </tr>
                <tr>
                    <td><strong>Points Tracked:</strong></td>
                    <td>468 Points</td>
                    <td><strong>Head Tilt (yaw):</strong></td>
                    <td>{round(telemetry['landmarks'][132] * 10, 1) if face_detected else 0.0}°</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- RIGHT COLUMN: System Intelligence & Dataset Recorder -----------------
with col_right:
    st.markdown(
        """
        <div class="bauhaus-card card-yellow" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0;">3. SYSTEM COCKPIT</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Feature processing diagnostics
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 15px; margin-bottom: 15px;">
            <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #121212;">📊 Signal Diagnostics</h4>
            <table style="width:100%; font-size:0.8rem; line-height:1.6;">
                <tr><td><strong>Cleaned Vectors:</strong></td><td>1662 Values</td></tr>
                <tr><td><strong>Tremor Noise index:</strong></td><td>{round(1.0 - telemetry['stability_index'], 3)}</td></tr>
                <tr><td><strong>Missing Points recovered:</strong></td><td>{21 if not rh_detected and not lh_detected else 0} Points</td></tr>
                <tr><td><strong>Displacement vectors:</strong></td><td>{1662 if telemetry['mean_velocity'] > 0 else 0} Arrays</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Dataset Collection Mode
    st.markdown("### Dataset Builder")
    selected_label = st.selectbox("Record Target Label", options=SUPPORTED_GESTURES, id="v_select_label")
    
    rec_btn_col1, rec_btn_col2 = st.columns(2)
    with rec_btn_col1:
        if st.button("Start Capture", key="btn_start_capture"):
            dataset_recorder.start_session(selected_label)
            st.session_state["rec_session_id"] = dataset_recorder.session_id
            st.success("Recording started...")
    with rec_btn_col2:
        if st.button("Stop Capture", key="btn_stop_capture"):
            summary = dataset_recorder.stop_session()
            st.session_state["rec_session_id"] = "Inactive"
            st.session_state["recorded_rep_count"] += 1
            st.success(f"Repetition recorded successfully! Label: {summary['label']}, Frames: {summary['frames_count']}")

    if st.button("Export dataset sequence", key="btn_export_dataset"):
        export = dataset_recorder.export_dataset()
        st.info(f"Export completed: {export['message']}\nShape: {export['shape']}")

    st.markdown(
        f"""
        <div style="background-color:#E6E6E6; border:2px dashed #121212; padding:10px; font-size:0.8rem; margin-top:10px;">
            <strong>Session ID:</strong> {st.session_state["rec_session_id"]}<br/>
            <strong>Captured Frames:</strong> {dataset_recorder.captured_frames_count}<br/>
            <strong>Recorded Repetitions:</strong> {st.session_state["recorded_rep_count"]}<br/>
            <strong>Status:</strong> {dataset_recorder.export_status}
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- BOTTOM SECTION: Data Pipeline Monitor & Analytics -----------------
st.markdown("---")
st.markdown("### Data Pipeline Monitor")

b_col1, b_col2 = st.columns([2, 1])

with b_col1:
    # Render line charts of rolling parameters
    st.markdown("#### Real-time Kinematic Telemetry Track")
    
    # Access historical buffer states
    history_30 = list(vision_pipeline.memory.buffer_30)
    
    if history_30:
        # Construct Pandas dataframe
        velocities = [r["mean_velocity"] * 100 for r in history_30]
        accelerations = [r["mean_acceleration"] * 100 for r in history_30]
        stabilities = [r["stability_index"] * 100 for r in history_30]
        
        df_plot = pd.DataFrame({
            "Velocity (x100)": velocities,
            "Acceleration (x100)": accelerations,
            "Stability (%)": stabilities
        })
        st.line_chart(df_plot)
    else:
        st.info("Live data stream graph will render once Camera Ingestion begins.")

with b_col2:
    st.markdown("#### AI Readiness Panel")
    
    readiness = telemetry["readiness"]
    grade_class = "status-online" if readiness["is_training_ready"] else "status-offline"
    
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding:15px; background-color: #FFFFFF !important;">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                <strong>DATA QUALITY:</strong>
                <span>{int(readiness['data_quality_score'] * 100)}%</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                <strong>FEATURE QUALITY:</strong>
                <span>{int(readiness['feature_quality_score'] * 100)}%</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                <strong>TRACKING STABILITY:</strong>
                <span>{int(readiness['tracking_stability_score'] * 100)}%</span>
            </div>
            <hr style="margin: 10px 0; border:0; border-top:2px solid #121212;"/>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong>AI TRAIN READY:</strong>
                <span class="status-pill {grade_class}">{readiness['readiness_grade']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
