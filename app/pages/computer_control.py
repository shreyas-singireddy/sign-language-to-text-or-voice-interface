import time

import streamlit as st

from ai_engine.utils.dependency_guard import CV2_AVAILABLE, MP_AVAILABLE, cv2, require_torch

# --- Graceful degradation gate ---
if not CV2_AVAILABLE or not MP_AVAILABLE:
    st.warning(
        "⚠️ **Computer Control Agent is unavailable in this deployment.**\n\n"
        "This page requires OpenCV and MediaPipe which could not be loaded. "
        "All other pages remain fully functional.",
        icon="🚫",
    )
    st.stop()

if not require_torch():
    st.stop()

from ai_engine.ai_agent.computer_control_service import computer_control_service
from ai_engine.services.perception_service import perception_service
from ai_engine.utils.config import sys_config
from ai_engine.utils.cv_overlay import draw_skeleton_and_telemetry
from app.services.ai_service import ai_service
from app.services.audio_service import audio_service

# Page Layout Header
st.markdown(
    '<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">🖥️ COMPUTER CONTROL AGENT</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.15rem; font-weight: bold; color: #1040C0;'>Control your operating system using Sign Language commands and Multi-Agent planning.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Session state initialization
if "cc_camera_active" not in st.session_state:
    st.session_state["cc_camera_active"] = False
if "cc_latest_command" not in st.session_state:
    st.session_state["cc_latest_command"] = ""
if "cc_intent_data" not in st.session_state:
    st.session_state["cc_intent_data"] = {}
if "cc_execution_plan" not in st.session_state:
    st.session_state["cc_execution_plan"] = []
if "cc_execution_status" not in st.session_state:
    st.session_state["cc_execution_status"] = ""
if "cc_execution_success" not in st.session_state:
    st.session_state["cc_execution_success"] = None
if "cc_audio_bytes" not in st.session_state:
    st.session_state["cc_audio_bytes"] = None

col_controls, col_timeline = st.columns([5, 4])

with col_controls:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">AGENT CONSOLE & VIDEO FEED</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Control buttons
    cam_btn_col1, cam_btn_col2, cam_btn_col3 = st.columns(3)
    with cam_btn_col1:
        if st.button("🔌 Start Agent Camera", key="btn_cc_start"):
            st.session_state["cc_camera_active"] = True
    with cam_btn_col2:
        if st.button("🛑 Stop Agent Camera", key="btn_cc_stop"):
            st.session_state["cc_camera_active"] = False
            perception_service.camera.release()
    with cam_btn_col3:
        if st.button("🔄 Reset Agent States", key="btn_cc_reset"):
            st.session_state["cc_latest_command"] = ""
            st.session_state["cc_intent_data"] = {}
            st.session_state["cc_execution_plan"] = []
            st.session_state["cc_execution_status"] = ""
            st.session_state["cc_execution_success"] = None
            st.session_state["cc_audio_bytes"] = None
            ai_service.pipeline.reset_sequence()

    # Audio & Execution Configuration
    opt_col1, opt_col2 = st.columns(2)
    with opt_col1:
        cc_mode = st.radio(
            "Agent Mode",
            options=["Safe Simulation (Mock Mode)", "Live System Execution"],
            index=0,
            key="cc_execution_mode",
        )
    with opt_col2:
        cc_voice_feedback = st.checkbox("Speak Confirmation Feedback", value=True, key="cc_voice_feedback")

    # Manual Command entry for testing
    manual_input = st.text_input(
        "Simulate Command Input", placeholder="e.g. Open Notepad, Open Downloads, Open Chrome", key="cc_manual_input"
    )
    if st.button("🚀 Execute Simulated Command", key="btn_cc_exec_manual"):
        if manual_input.strip():
            st.session_state["cc_latest_command"] = manual_input.strip()
            # Process through Agent Service
            intent_data = computer_control_service.parse_intent(manual_input.strip())
            st.session_state["cc_intent_data"] = intent_data

            plan = computer_control_service.create_execution_plan(intent_data["intent"], intent_data["target"])
            st.session_state["cc_execution_plan"] = plan

            # Run action
            is_mock = "Mock" in cc_mode
            success, msg = computer_control_service.execute_action(
                intent_data["intent"], intent_data["target"], mock=is_mock
            )
            st.session_state["cc_execution_success"] = success
            st.session_state["cc_execution_status"] = msg

            # Voice synthesis
            if cc_voice_feedback:
                with st.spinner("Generating speech feedback..."):
                    audio_bytes = audio_service.generate_speech(msg, lang_code="en-US")
                    st.session_state["cc_audio_bytes"] = audio_bytes
            else:
                st.session_state["cc_audio_bytes"] = None

    # Video feed element
    video_placeholder = st.empty()

with col_timeline:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">MULTI-AGENT REASONING TIMELINE</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Vision & Gesture State
    st.markdown("#### 1. Ingestion & Vision Agent")
    st.write(f"- Camera status: `{'Active' if st.session_state['cc_camera_active'] else 'Inactive'}`")
    st.write("- Telemetry: `MediaPipe holistic active`")

    # 2. Sign-to-Text State
    st.markdown("#### 2. Sign-to-Text / Natural Language Agent")
    cmd_text = st.session_state.get("cc_latest_command", "")
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border-left: 6px solid #D02020; padding: 8px 12px; font-weight: bold;">
            Command: {cmd_text if cmd_text else 'Waiting for command...'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Intent Understanding State
    st.markdown("#### 3. Intent Understanding Agent")
    intent_data = st.session_state.get("cc_intent_data", {})
    if intent_data:
        st.json(intent_data)
    else:
        st.write("- Intent: `None`")

    # 4. Action Planning Timeline
    st.markdown("#### 4. Action Planning Agent")
    plan = st.session_state.get("cc_execution_plan", [])
    if plan:
        for idx, step in enumerate(plan):
            st.markdown(f"- `[x]` Step {idx+1}: {step}")
    else:
        st.write("- Plan: `No active plan`")

    # 5. OS Control & Confirmation Feedback
    st.markdown("#### 5. Computer Control & Feedback Agent")
    success_status = st.session_state.get("cc_execution_success")
    exec_msg = st.session_state.get("cc_execution_status", "")

    if success_status is not None:
        if success_status:
            st.success(exec_msg)
        else:
            st.error(exec_msg)
    else:
        st.write("- Status: `Pending execution`")

    # Audio playback slot
    audio_bytes = st.session_state.get("cc_audio_bytes")
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

# Live camera loop
if st.session_state["cc_camera_active"]:
    success = perception_service.camera.initialize_camera(sys_config.camera.source_index)
    if success:
        try:
            sequence_buffer = []
            last_action_time = time.time()

            while st.session_state["cc_camera_active"]:
                read_success, frame, latency = perception_service.camera.read_frame()
                if not read_success:
                    st.error("Camera connection lost or timed out.")
                    break

                # Process perception frame
                telemetry = perception_service.process_perception_frame(frame, latency)
                flat_lms = perception_service._flatten_landmarks(telemetry.landmarks)

                # Feed temporal sequence
                sequence_buffer.append(flat_lms)
                if len(sequence_buffer) > 30:
                    sequence_buffer.pop(0)

                # Fetch overall prediction details
                results = ai_service.process_frame(frame)
                gesture = results["gesture"]
                translation = results["translation"]

                # Mirror frame for standard rendering overlays
                display_img = cv2.flip(frame, 1)
                display_img = draw_skeleton_and_telemetry(
                    display_img,
                    telemetry.landmarks,
                    {"prediction": gesture, "confidence": results["confidence"]},
                    telemetry.camera.fps,
                    telemetry.performance.total_pipeline_ms,
                )

                # Render camera feed
                rgb_display = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_display, use_column_width=True)

                # If a valid action phrase is translated and some time has elapsed, trigger the control execution
                # Example gesture command logic: if translation is not empty and has changed
                if translation and translation != st.session_state["cc_latest_command"]:
                    # Rate limit action triggers to avoid double execution (e.g. 5 seconds gap)
                    if time.time() - last_action_time > 5.0:
                        st.session_state["cc_latest_command"] = translation

                        # Process control agent pipeline
                        intent_data = computer_control_service.parse_intent(translation)
                        st.session_state["cc_intent_data"] = intent_data

                        plan = computer_control_service.create_execution_plan(
                            intent_data["intent"], intent_data["target"]
                        )
                        st.session_state["cc_execution_plan"] = plan

                        is_mock = "Mock" in cc_mode
                        success_res, status_msg = computer_control_service.execute_action(
                            intent_data["intent"], intent_data["target"], mock=is_mock
                        )
                        st.session_state["cc_execution_success"] = success_res
                        st.session_state["cc_execution_status"] = status_msg

                        if cc_voice_feedback:
                            audio_bytes = audio_service.generate_speech(status_msg, lang_code="en-US")
                            st.session_state["cc_audio_bytes"] = audio_bytes

                        last_action_time = time.time()
                        # Force streamlit to refresh values
                        st.rerun()

                time.sleep(0.01)
        finally:
            perception_service.camera.release()
            video_placeholder.empty()
    else:
        st.error("Failed to initialize webcam device index.")
