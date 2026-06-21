import time

import streamlit as st

from ai_engine.utils.cv_overlay import draw_skeleton_and_telemetry
from ai_engine.utils.dependency_guard import CV2_AVAILABLE, MP_AVAILABLE, cv2, mp, require_torch
from src.services.translation_service import t

# --- Graceful degradation gate ---
if not CV2_AVAILABLE or not MP_AVAILABLE:
    st.warning(
        "⚠️ **Visual Debug Dashboard is unavailable in this deployment.**\n\n"
        "This page requires OpenCV and MediaPipe which could not be loaded. "
        "All other pages remain fully functional.",
        icon="🚫",
    )
    st.stop()

if not require_torch():
    st.stop()

from ai_engine.gesture_recognition.services.gesture_service import gesture_service
from ai_engine.services.perception_service import perception_service
from ai_engine.utils.config import sys_config

# MediaPipe drawing tools
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

# Page Layout Header
st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">{t("debug_title")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>{t('db_subtitle')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if "debug_active" not in st.session_state:
    st.session_state["debug_active"] = False

col_cam, col_telemetry = st.columns([5, 4])

with col_cam:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">{t("db_skeletal_stream")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Toggle controller
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        if st.button(t("db_start_feed"), key="btn_start_debug"):
            st.session_state["debug_active"] = True
    with ctrl_col2:
        if st.button(t("db_stop_feed"), key="btn_stop_debug"):
            st.session_state["debug_active"] = False

    video_placeholder = st.empty()

with col_telemetry:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">{t("db_telemetry_analytics")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Layout slots for continuous telemetry outputs
    slot_prediction = st.empty()
    slot_head_pose = st.empty()
    slot_kinematics = st.empty()
    slot_quality = st.empty()

# Run Real-Time Frame loop if active
if st.session_state["debug_active"]:
    success = perception_service.camera.initialize_camera(sys_config.camera.source_index)
    if success:
        try:
            sequence_buffer = []

            while st.session_state["debug_active"]:
                read_success, frame, latency = perception_service.camera.read_frame()
                if not read_success:
                    st.error(t("db_cam_timeout"))
                    break

                # 1. Pipeline Telemetry response
                telemetry = perception_service.process_perception_frame(frame, latency)
                flat_lms = perception_service._flatten_landmarks(telemetry.landmarks)

                # 2. Run sequential gesture recognition
                sequence_buffer.append(flat_lms)
                if len(sequence_buffer) > 30:
                    sequence_buffer.pop(0)

                pred = gesture_service.predict_sequence(
                    sequence_buffer,
                    telemetry.visibility.overall_visibility,
                    telemetry.readiness.frame_quality_score,
                    telemetry.occlusion.occlusion_percentage,
                    telemetry.stability.tracking_stability,
                )

                # 3. Draw Annotated overlays on mirrored image using our efficient drawer
                display_img = cv2.flip(frame, 1)
                display_img = draw_skeleton_and_telemetry(
                    display_img,
                    telemetry.landmarks,
                    pred,
                    telemetry.camera.fps,
                    telemetry.performance.total_pipeline_ms,
                )

                # Convert to RGB and render
                rgb_display = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_display, use_column_width=True)

                # 4. Render Telemetry widgets
                # Gesture predictions widget
                slot_prediction.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:12px; border-left:12px solid #F0C020;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">{t("db_active_classification")}</h4>
                        <div style="font-size:2rem; font-weight:900; color:#D02020;">{pred["prediction"]}</div>
                        <div style="font-size:0.85rem; font-weight:bold; color:#1040C0;">{t("db_confidence_pct", conf=int(pred["confidence"] * 100))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Head Pose yaw/pitch/roll widget
                pitch = telemetry.landmarks.face.head_rotation_pitch if telemetry.landmarks.face.present else 0.0
                yaw = telemetry.landmarks.face.head_rotation_yaw if telemetry.landmarks.face.present else 0.0
                roll = telemetry.landmarks.face.head_rotation_roll if telemetry.landmarks.face.present else 0.0
                slot_head_pose.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:12px; border-left:12px solid #1040C0;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">{t("db_head_pose")}</h4>
                        <table style="width:100%; font-size:0.85rem; font-weight:bold;">
                            <tr><td><strong>{t("db_pitch")}:</strong></td><td style="color:#D02020;">{pitch}°</td><td><strong>{t("db_yaw")}:</strong></td><td style="color:#1040C0;">{yaw}°</td></tr>
                            <tr><td><strong>{t("db_roll")}:</strong></td><td style="color:#F0C020;">{roll}°</td><td><strong>{t("db_mouth_open")}:</strong></td><td>{telemetry.landmarks.face.mouth_openness if telemetry.landmarks.face.present else 0.0}</td></tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Kinematics velocity & stability widget
                slot_kinematics.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:12px; border-left:12px solid #D02020;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">{t("db_kinematics_vel")}</h4>
                        <table style="width:100%; font-size:0.85rem; font-weight:bold;">
                            <tr><td><strong>{t("db_l_hand_vel")}:</strong></td><td>{round(telemetry.motion.left_hand.average_velocity, 3)}</td><td><strong>{t("db_r_hand_vel")}:</strong></td><td>{round(telemetry.motion.right_hand.average_velocity, 3)}</td></tr>
                            <tr><td><strong>{t("db_stability")}:</strong></td><td style="color:#1040C0;">{telemetry.stability.tracking_stability}%</td><td><strong>{t("db_occlusion")}:</strong></td><td style="color:#D02020;">{telemetry.occlusion.occlusion_percentage}%</td></tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Quality performance index
                slot_quality.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:0px; border-left:12px solid #121212;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">{t("db_ingest_quality")}</h4>
                        <table style="width:100%; font-size:0.85rem; font-weight:bold;">
                            <tr><td><strong>{t("db_fps")}:</strong></td><td style="color:#1040C0;">{telemetry.camera.fps}</td><td><strong>{t("db_latency")}:</strong></td><td style="color:#D02020;">{telemetry.performance.total_pipeline_ms}ms</td></tr>
                            <tr><td><strong>{t("db_quality_score")}:</strong></td><td>{telemetry.readiness.frame_quality_score}%</td><td><strong>{t("db_readiness")}:</strong></td><td>{telemetry.readiness.gesture_readiness}%</td></tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                time.sleep(0.01)
        finally:
            perception_service.camera.release()
            video_placeholder.empty()
    else:
        st.error(t("db_cam_error"))
else:
    video_placeholder.info(t("db_activate_info"))
