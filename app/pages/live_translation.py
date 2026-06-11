import streamlit as st
import cv2
import numpy as np
import time
from app.services.ai_service import ai_service
from app.services.audio_service import audio_service
from app.services.database_service import db_service
from config.config import SUPPORTED_LANGUAGES

# Page Header
st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">LIVE TRANSLATION</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>Real-time Sign Language to Text and Speech pipeline.</p>", unsafe_allow_html=True)
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
        """
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">WEBCAM INGESTION STREAM</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Camera Toggle buttons
    camera_btn_col1, camera_btn_col2, camera_btn_col3 = st.columns(3)
    with camera_btn_col1:
        start_cam = st.button("🔌 Start Camera", key="btn_start_cam", use_container_width=True)
    with camera_btn_col2:
        stop_cam = st.button("🛑 Stop Camera", key="btn_stop_cam", use_container_width=True)
    with camera_btn_col3:
        reset_seq = st.button("🔄 Reset Buffer", key="btn_reset_seq", use_container_width=True)

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
        st.success("Buffer cleared!")

    # Video display frame
    video_placeholder = st.empty()
    
    if st.session_state.get("camera_active", False):
        st.markdown('<div class="pulse-badge">● RECORDING ACTIVE</div>', unsafe_allow_html=True)
        
        # Open camera stream using OpenCV
        from ai_engine.computer_vision.camera import CameraManager
        cam = CameraManager()
        if cam.start():
            try:
                # Continuous loop for frame rendering
                while st.session_state.get("camera_active", False):
                    success, frame = cam.get_frame()
                    if not success:
                        st.error("Failed to read camera frame. Check webcam connection.")
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
        video_placeholder.info("Click '🔌 Start Camera' to launch webcam translation stream.")

with col_results:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">TRANSLATION ENGINE PANEL</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Language selection dropdown
    selected_language = st.selectbox(
        "Output Translation Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        key="select_lang_translation"
    )

    # Translation Display Box
    st.markdown("### Text Output")
    text_output = st.session_state.get("translation_buffer", "")
    
    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="min-height: 120px; background-color: #FFFFFF !important;">
            <p style="font-size: 1.35rem; font-weight: 800; text-transform: uppercase; margin: 0; color: #121212;">
                {text_output if text_output else "Waiting for gestures..."}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sequence visualization
    active_seq = st.session_state.get("detected_sequence", [])
    st.markdown("**Detected Token Chain:**")
    if active_seq:
        st.write(" ➔ ".join([f"`{item}`" for item in active_seq]))
    else:
        st.write("*No tokens processed in window*")

    # Speech Synthesis section
    st.markdown("---")
    st.markdown("### Voice Synthesis")
    
    # Generate Voice Button
    tts_lang_code = SUPPORTED_LANGUAGES[selected_language]
    
    if st.button("🔊 Play Voice Translation", key="btn_play_voice", disabled=(not text_output), use_container_width=True):
        with st.spinner("Synthesizing voice..."):
            audio_bytes = audio_service.generate_speech(text_output, lang_code=tts_lang_code)
            st.audio(audio_bytes, format="audio/wav")

    # Database Logging section
    if st.button("💾 Log Translation to Database", key="btn_log_db", disabled=(not text_output), use_container_width=True):
        # Save record
        record = db_service.log_translation(
            detected_gestures=active_seq,
            translated_text=text_output,
            confidence=0.88,  # Mock pipeline average confidence
            language=selected_language
        )
        st.success(f"Log saved successfully! ID: {record['id']}")
