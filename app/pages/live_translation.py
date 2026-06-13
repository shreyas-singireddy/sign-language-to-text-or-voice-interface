import time

import streamlit as st

from ai_engine.utils.dependency_guard import CV2_AVAILABLE, cv2
from src.services.translation_service import t

# --- Graceful degradation gate ---
if not CV2_AVAILABLE:
    st.warning(
        "⚠️ **Live Translation is unavailable in this deployment.**\n\n"
        "This page requires OpenCV which could not be loaded. "
        "All other pages remain fully functional.",
        icon="🚫",
    )
    st.stop()

from app.services.ai_service import ai_service
from app.services.audio_service import audio_service
from app.services.database_service import db_service
from config.config import SUPPORTED_LANGUAGES

# Page Header
st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">{t("sidebar_live_translation")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>{t('lt_subtitle')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Layout columns
col_video, col_results = st.columns([3, 2])

# Initialize session state variables
if "translation_buffer" not in st.session_state:
    st.session_state["translation_buffer"] = ""
if "detected_sequence" not in st.session_state:
    st.session_state["detected_sequence"] = []
if "last_processed_time" not in st.session_state:
    st.session_state["last_processed_time"] = time.time()

with col_video:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("lt_webcam_title")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Camera Toggle buttons
    camera_btn_col1, camera_btn_col2, camera_btn_col3 = st.columns(3)
    with camera_btn_col1:
        start_cam = st.button(f"🔌 {t('lt_start_cam')}", key="btn_start_cam", use_container_width=True)
    with camera_btn_col2:
        stop_cam = st.button(f"🛑 {t('lt_stop_cam')}", key="btn_stop_cam", use_container_width=True)
    with camera_btn_col3:
        reset_seq = st.button(f"🔄 {t('lt_reset_buffer')}", key="btn_reset_seq", use_container_width=True)

    if start_cam:
        st.session_state["camera_active"] = True
    if stop_cam:
        st.session_state["camera_active"] = False
        ai_service.pipeline.reset_sequence()
        st.session_state["detected_sequence"] = []
    if reset_seq:
        ai_service.pipeline.reset_sequence()
        st.session_state["detected_sequence"] = []
        st.session_state["translation_buffer"] = ""
        st.success(t("lt_buffer_cleared"))

    # Video display frame
    video_placeholder = st.empty()

    if st.session_state.get("camera_active", False):
        st.markdown(f'<div class="pulse-badge">● {t("lt_recording_active")}</div>', unsafe_allow_html=True)

        # Open camera stream using OpenCV
        from ai_engine.computer_vision.camera import CameraManager

        cam = CameraManager()
        if cam.start():
            try:
                # Continuous loop for frame rendering
                while st.session_state.get("camera_active", False):
                    success, frame = cam.get_frame()
                    if not success:
                        st.error(t("lt_camera_error"))
                        break

                    # Process frame
                    results = ai_service.process_frame(frame)

                    # Flip frame for mirror display
                    display_frame = cv2.flip(results["annotated_frame"], 1)
                    # Convert to RGB for Streamlit rendering
                    display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

                    # Render image
                    video_placeholder.image(display_frame_rgb, channels="RGB", use_column_width=True)

                    # Update states
                    st.session_state["detected_sequence"] = results["sequence"]
                    st.session_state["translation_buffer"] = results["translation"]

                    # Small sleep to manage render rates (approx 24 fps)
                    time.sleep(0.04)
            finally:
                cam.stop()
                video_placeholder.empty()
    else:
        video_placeholder.info(t("lt_camera_info"))

with col_results:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("lt_panel_title")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Language selection dropdown
    lang_list = list(SUPPORTED_LANGUAGES.keys())
    current_lang = st.session_state.get("language", "English")
    if current_lang not in lang_list:
        current_lang = "English"
    lang_idx = lang_list.index(current_lang)

    selected_language = st.selectbox(
        t("lt_output_lang"),
        options=lang_list,
        index=lang_idx,
        key="select_lang_translation",
    )
    if selected_language != current_lang:
        st.session_state["language"] = selected_language
        st.rerun()

    # Translation Display Box
    st.markdown(f"### {t('lt_text_output')}")
    text_output = st.session_state.get("translation_buffer", "")

    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="min-height: 120px; background-color: #FFFFFF !important;">
            <p style="font-size: 1.35rem; font-weight: 800; text-transform: uppercase; margin: 0; color: #121212;">
                {text_output if text_output else t("lt_waiting")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sequence visualization
    active_seq = st.session_state.get("detected_sequence", [])
    st.markdown(f"**{t('lt_detected_chain')}:**")
    if active_seq:
        st.write(" ➔ ".join([f"`{item}`" for item in active_seq]))
    else:
        st.write(f"*{t('lt_no_tokens')}*")

    # Speech Synthesis section
    st.markdown("---")
    st.markdown(f"### {t('lt_voice_synthesis')}")

    # Generate Voice Button
    tts_lang_code = SUPPORTED_LANGUAGES[selected_language]

    if st.button(
        f"🔊 {t('lt_play_voice')}",
        key="btn_play_voice",
        disabled=(not text_output),
        use_container_width=True,
    ):
        with st.spinner(t("lt_synthesizing")):
            audio_bytes = audio_service.generate_speech(text_output, lang_code=tts_lang_code)
            st.audio(audio_bytes, format="audio/wav")

    # Database Logging section
    if st.button(
        f"💾 {t('lt_log_db')}",
        key="btn_log_db",
        disabled=(not text_output),
        use_container_width=True,
    ):
        # Save record
        record = db_service.log_translation(
            detected_gestures=active_seq,
            translated_text=text_output,
            confidence=0.88,  # Mock pipeline average confidence
            language=selected_language,
        )
        st.success(t("lt_log_success", id=record['id']))
