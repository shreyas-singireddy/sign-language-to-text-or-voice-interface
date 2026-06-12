import time

import cv2
import mediapipe as mp
import streamlit as st

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
    '<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">VISUAL DEBUG COCKPIT</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>Advanced real-time human perception debugging, joint skeletal overlays, and telemetry analytics.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if "debug_active" not in st.session_state:
    st.session_state["debug_active"] = False

col_cam, col_telemetry = st.columns([5, 4])

with col_cam:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">🎥 annotated skeletal video stream</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Toggle controller
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        if st.button("Start Debug Feed", key="btn_start_debug"):
            st.session_state["debug_active"] = True
    with ctrl_col2:
        if st.button("Stop Debug Feed", key="btn_stop_debug"):
            st.session_state["debug_active"] = False

    video_placeholder = st.empty()

with col_telemetry:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">📊 real-time telemetry analytics</h3>
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
            # We initialize standard drawing models locally to ensure overlay draws correctly
            mp_hands_model = mp_hands.Hands(
                min_detection_confidence=sys_config.detectors.min_detection_confidence,
                min_tracking_confidence=sys_config.detectors.min_tracking_confidence,
            )
            mp_pose_model = mp_pose.Pose(
                min_detection_confidence=sys_config.detectors.min_detection_confidence,
                min_tracking_confidence=sys_config.detectors.min_tracking_confidence,
            )
            mp_face_mesh_model = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=sys_config.detectors.min_detection_confidence,
                min_tracking_confidence=sys_config.detectors.min_tracking_confidence,
            )

            sequence_buffer = []

            while st.session_state["debug_active"]:
                read_success, frame, latency = perception_service.camera.read_frame()
                if not read_success:
                    st.error("Webcam device read timeout / disconnected.")
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

                # 3. Draw Annotated overlays on mirrored image
                display_img = cv2.flip(frame, 1)
                img_h, img_w, _ = display_img.shape

                # Convert back to RGB for MediaPipe processors
                rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Run local estimators to draw native landmarks
                hands_res = mp_hands_model.process(rgb_img)
                pose_res = mp_pose_model.process(rgb_img)
                face_res = mp_face_mesh_model.process(rgb_img)

                # Draw Face Mesh Outline
                if face_res.multi_face_landmarks:
                    for face_landmarks in face_res.multi_face_landmarks:
                        mp_drawing.draw_landmarks(
                            image=display_img,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style(),
                        )

                # Draw Pose Skeleton
                if pose_res.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        image=display_img,
                        landmark_list=pose_res.pose_landmarks,
                        connections=mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                    )

                # Draw Hand Joints
                if hands_res.multi_hand_landmarks:
                    for hand_landmarks in hands_res.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image=display_img,
                            landmark_list=hand_landmarks,
                            connections=mp_hands.HAND_CONNECTIONS,
                            landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                            connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
                        )

                # Convert to RGB and render
                rgb_display = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_display, use_column_width=True)

                # 4. Render Telemetry widgets
                # Gesture predictions widget
                slot_prediction.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:12px; border-left:12px solid #F0C020;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">ACTIVE CLASSIFICATION</h4>
                        <div style="font-size:2rem; font-weight:900; color:#D02020;">{pred["prediction"]}</div>
                        <div style="font-size:0.85rem; font-weight:bold; color:#1040C0;">CONFIDENCE: {int(pred["confidence"] * 100)}%</div>
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
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">PnP HEAD POE ESTIMATION</h4>
                        <table style="width:100%; font-size:0.85rem; font-weight:bold;">
                            <tr><td><strong>PITCH:</strong></td><td style="color:#D02020;">{pitch}°</td><td><strong>YAW:</strong></td><td style="color:#1040C0;">{yaw}°</td></tr>
                            <tr><td><strong>ROLL:</strong></td><td style="color:#F0C020;">{roll}°</td><td><strong>MOUTH OPEN:</strong></td><td>{telemetry.landmarks.face.mouth_openness if telemetry.landmarks.face.present else 0.0}</td></tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Kinematics velocity & stability widget
                slot_kinematics.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:12px; border-left:12px solid #D02020;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">KINEMATICS VELOCITY</h4>
                        <table style="width:100%; font-size:0.85rem; font-weight:bold;">
                            <tr><td><strong>L HAND VEL:</strong></td><td>{round(telemetry.motion.left_hand.average_velocity, 3)}</td><td><strong>R HAND VEL:</strong></td><td>{round(telemetry.motion.right_hand.average_velocity, 3)}</td></tr>
                            <tr><td><strong>STABILITY:</strong></td><td style="color:#1040C0;">{telemetry.stability.tracking_stability}%</td><td><strong>OCCLUSION:</strong></td><td style="color:#D02020;">{telemetry.occlusion.occlusion_percentage}%</td></tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Quality performance index
                slot_quality.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding:15px; margin-bottom:0px; border-left:12px solid #121212;">
                        <h4 style="margin:0 0 5px 0; font-size:0.9rem; color:#121212;">INGEST QUALITY INDEX</h4>
                        <table style="width:100%; font-size:0.85rem; font-weight:bold;">
                            <tr><td><strong>FPS:</strong></td><td style="color:#1040C0;">{telemetry.camera.fps}</td><td><strong>LATENCY:</strong></td><td style="color:#D02020;">{telemetry.performance.total_pipeline_ms}ms</td></tr>
                            <tr><td><strong>QUALITY SCORE:</strong></td><td>{telemetry.readiness.frame_quality_score}%</td><td><strong>READINESS:</strong></td><td>{telemetry.readiness.gesture_readiness}%</td></tr>
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
        st.error("Capture device initialization failed. Confirm webcam index is correct in settings.")
else:
    video_placeholder.info("Activate the visual debug loop to view live joint tracking overlays.")
