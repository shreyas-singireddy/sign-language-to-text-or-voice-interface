import time

import cv2
import streamlit as st

from app.services.ai_service import ai_service
from app.services.audio_service import audio_service
from app.services.database_service import db_service
from config.config import SUPPORTED_LANGUAGES

# ──────────────────────────────────────────────────────────────────────────────
# Page Header
st.markdown(
    '<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">LIVE TRANSLATION</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>Real-time Sign Language to Text and Speech pipeline.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "camera_active": False,
        "translation_buffer": "",
        "detected_sequence": [],
        "last_processed_time": time.time(),
        "live_frame": None,          # holds latest annotated frame (BGR bytes)
        "live_gesture": "IDLE",
        "live_confidence": 0.0,
        "live_fps": 0.0,
        "live_latency_ms": 0.0,
        "live_queue_depth": 0,
        "live_hands_detected": False,
        "live_mem_mb": 0.0,
        "debug_mode": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ──────────────────────────────────────────────────────────────────────────────
# BACKGROUND WEBCAM THREAD — runs independently of Streamlit's main thread
# Uses a single-slot queue so the UI always gets the freshest frame without
# accumulating a backlog.
# ──────────────────────────────────────────────────────────────────────────────

# Module-level objects so they survive across Streamlit reruns
if "cam_thread" not in st.session_state:
    st.session_state["cam_thread"] = None
if "cam_queue" not in st.session_state:
    st.session_state["cam_queue"] = queue.Queue(maxsize=2)
if "cam_stop_event" not in st.session_state:
    st.session_state["cam_stop_event"] = threading.Event()


def _camera_worker(stop_event: threading.Event, result_queue: queue.Queue):
    """
    Runs in a daemon thread.  Captures frames, runs the full AI pipeline,
    and pushes results into result_queue (dropping stale frames to prevent lag).
    """
    from ai_engine.computer_vision.camera import CameraManager
    cam = CameraManager()
    if not cam.start():
        result_queue.put({"error": "Camera failed to open."})
        return

    frame_times = []
    frame_count = 0
    t_start = time.time()

    try:
        while not stop_event.is_set():
            t0 = time.perf_counter()
            ok, frame = cam.get_frame()
            if not ok or frame is None:
                time.sleep(0.01)
                continue

            # Full AI inference
            results = ai_service.process_frame(frame)

            t1 = time.perf_counter()
            latency_ms = round((t1 - t0) * 1000, 1)

            # FPS calculation
            frame_count += 1
            elapsed = time.time() - t_start
            fps = round(frame_count / elapsed, 1) if elapsed > 0 else 0.0

            # Memory
            try:
                mem_mb = round(psutil.Process().memory_info().rss / 1024 / 1024, 1)
            except Exception:
                mem_mb = 0.0

            payload = {
                "annotated_frame": results.get("annotated_frame"),
                "gesture": results.get("gesture", "IDLE"),
                "confidence": results.get("confidence", 0.0),
                "sequence": results.get("sequence", []),
                "translation": results.get("translation", ""),
                "hands_detected": results.get("hands_detected", False),
                "fps": fps,
                "latency_ms": latency_ms,
                "queue_depth": result_queue.qsize(),
                "mem_mb": mem_mb,
            }

            # Non-blocking put — drop oldest if queue full
            if result_queue.full():
                try:
                    result_queue.get_nowait()
                except queue.Empty:
                    pass
            result_queue.put_nowait(payload)

            # Adaptive FPS cap: target ~25 fps max
            elapsed_frame = time.perf_counter() - t0
            sleep_time = max(0.0, 0.040 - elapsed_frame)
            time.sleep(sleep_time)

    finally:
        cam.stop()


def _start_camera():
    """Starts the background camera thread."""
    stop_event = st.session_state["cam_stop_event"]
    stop_event.clear()

    q = st.session_state["cam_queue"]
    # Drain stale frames
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break

    t = threading.Thread(
        target=_camera_worker,
        args=(stop_event, q),
        daemon=True,
        name="CamWorker"
    )
    t.start()
    st.session_state["cam_thread"] = t
    st.session_state["camera_active"] = True


def _stop_camera():
    """Signals the background thread to stop."""
    st.session_state["cam_stop_event"].set()
    st.session_state["camera_active"] = False
    ai_service.pipeline.reset_sequence()
    st.session_state["detected_sequence"] = []


# ──────────────────────────────────────────────────────────────────────────────
# Layout
# ──────────────────────────────────────────────────────────────────────────────
col_video, col_results = st.columns([3, 2])

with col_video:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">WEBCAM INGESTION STREAM</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Camera Toggle buttons
    camera_btn_col1, camera_btn_col2, camera_btn_col3 = st.columns(3)
    with camera_btn_col1:
        start_cam = st.button(
            "🔌 Start Camera", key="btn_start_cam", use_container_width=True
        )
    with camera_btn_col2:
        stop_cam = st.button(
            "🛑 Stop Camera", key="btn_stop_cam", use_container_width=True
        )
    with camera_btn_col3:
        reset_seq = st.button(
            "🔄 Reset Buffer", key="btn_reset_seq", use_container_width=True
        )

    debug_mode = st.toggle("🔬 Debug Overlay", value=st.session_state["debug_mode"], key="toggle_debug")
    st.session_state["debug_mode"] = debug_mode

    # Handle button actions
    if start_cam and not st.session_state["camera_active"]:
        _start_camera()
        st.rerun()

    if stop_cam and st.session_state["camera_active"]:
        _stop_camera()
        st.session_state["translation_buffer"] = ""
        st.rerun()

    if reset_seq:
        ai_service.pipeline.reset_sequence()
        st.session_state["detected_sequence"] = []
        st.session_state["translation_buffer"] = ""
        st.success("Buffer cleared!")

    # ── Video display placeholder ──
    video_placeholder = st.empty()

    if st.session_state.get("camera_active", False):
        st.markdown(
            '<div class="pulse-badge">● RECORDING ACTIVE</div>', unsafe_allow_html=True
        )

        # Open camera stream using OpenCV
        from ai_engine.computer_vision.camera import CameraManager

        cam = CameraManager()
        if cam.start():
            try:
                # Continuous loop for frame rendering
                while st.session_state.get("camera_active", False):
                    success, frame = cam.get_frame()
                    if not success:
                        st.error(
                            "Failed to read camera frame. Check webcam connection."
                        )
                        break

                    # Process frame
                    results = ai_service.process_frame(frame)

                    # Flip frame for mirror display
                    display_frame = cv2.flip(results["annotated_frame"], 1)
                    # Convert to RGB for Streamlit rendering
                    display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

                    # Render image
                    video_placeholder.image(
                        display_frame_rgb, channels="RGB", use_column_width=True
                    )

                    # Update states
                    st.session_state["detected_sequence"] = results["sequence"]
                    st.session_state["translation_buffer"] = results["translation"]

                    # Small sleep to manage render rates (approx 24 fps)
                    time.sleep(0.04)
            finally:
                cam.stop()
                video_placeholder.empty()
    else:
        video_placeholder.info(
            "Click '🔌 Start Camera' to launch webcam translation stream."
        )


# ──────────────────────────────────────────────────────────────────────────────
# TRANSLATION RESULTS PANEL
# ──────────────────────────────────────────────────────────────────────────────
with col_results:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">TRANSLATION ENGINE PANEL</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Language selection dropdown
    selected_language = st.selectbox(
        "Output Translation Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        key="select_lang_translation",
    )
    
    # Update AI service language so the background thread uses it
    ai_service.set_target_language(selected_language)

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
        unsafe_allow_html=True,
    )

    # Current gesture + confidence live display
    if st.session_state["camera_active"]:
        gesture_conf_col1, gesture_conf_col2 = st.columns(2)
        with gesture_conf_col1:
            conf_pct = int(st.session_state.get("live_confidence", 0.0) * 100)
            gesture_label = st.session_state.get("live_gesture", "IDLE")
            st.markdown(
                f"""
                <div style="padding:12px; background:#121212; border-radius:8px; text-align:center; margin-top:10px;">
                    <div style="font-size:0.75rem; color:#888; font-weight:bold;">CURRENT GESTURE</div>
                    <div style="font-size:1.6rem; font-weight:900; color:#F0C020;">{gesture_label}</div>
                    <div style="font-size:0.75rem; color:#4FC; font-weight:bold;">CONF: {conf_pct}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with gesture_conf_col2:
            hands_icon = "✅" if st.session_state.get("live_hands_detected") else "❌"
            st.markdown(
                f"""
                <div style="padding:12px; background:#121212; border-radius:8px; text-align:center; margin-top:10px;">
                    <div style="font-size:0.75rem; color:#888; font-weight:bold;">HANDS DETECTED</div>
                    <div style="font-size:1.6rem;">{hands_icon}</div>
                    <div style="font-size:0.75rem; color:#4FC; font-weight:bold;">FPS: {st.session_state.get('live_fps', 0.0)}</div>
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

    # Voice synthesis
    st.markdown("---")
    st.markdown("### Voice Synthesis")

    # Generate Voice Button
    tts_lang_code = SUPPORTED_LANGUAGES[selected_language]

    if st.button(
        "🔊 Play Voice Translation",
        key="btn_play_voice",
        disabled=(not text_output),
        use_container_width=True,
    ):
        with st.spinner("Synthesizing voice..."):
            audio_bytes = audio_service.generate_speech(
                text_output, lang_code=tts_lang_code
            )
            st.audio(audio_bytes, format="audio/wav")

    # Database Logging section
    if st.button(
        "💾 Log Translation to Database",
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
        st.success(f"Log saved successfully! ID: {record['id']}")
