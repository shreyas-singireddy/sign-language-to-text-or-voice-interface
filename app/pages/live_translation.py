import streamlit as st
import cv2
import numpy as np
import time
import threading
import queue
import psutil
import mediapipe as mp
from app.services.ai_service import ai_service
from app.services.audio_service import audio_service
from app.services.database_service import db_service
from config.config import SUPPORTED_LANGUAGES

# ──────────────────────────────────────────────────────────────────────────────
# Page Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">LIVE TRANSLATION</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>Real-time Sign Language → Text → Speech pipeline.</p>", unsafe_allow_html=True)
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
        unsafe_allow_html=True
    )

    # Controls
    camera_btn_col1, camera_btn_col2, camera_btn_col3 = st.columns(3)
    with camera_btn_col1:
        start_cam = st.button("🔌 Start Camera", key="btn_start_cam", use_container_width=True)
    with camera_btn_col2:
        stop_cam = st.button("🛑 Stop Camera", key="btn_stop_cam", use_container_width=True)
    with camera_btn_col3:
        reset_seq = st.button("🔄 Reset Buffer", key="btn_reset_seq", use_container_width=True)

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
    status_placeholder = st.empty()

    # ── Debug metrics bar (shown when debug_mode is on) ──
    if st.session_state["debug_mode"] and st.session_state["camera_active"]:
        debug_col1, debug_col2, debug_col3 = st.columns(3)
        with debug_col1:
            fps_metric = st.empty()
        with debug_col2:
            latency_metric = st.empty()
        with debug_col3:
            mem_metric = st.empty()

        debug_col4, debug_col5 = st.columns(2)
        with debug_col4:
            queue_metric = st.empty()
        with debug_col5:
            hands_metric = st.empty()
    else:
        fps_metric = latency_metric = mem_metric = queue_metric = hands_metric = None


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
        unsafe_allow_html=True
    )

    selected_language = st.selectbox(
        "Output Translation Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        key="select_lang_translation"
    )

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
    tts_lang_code = SUPPORTED_LANGUAGES[selected_language]

    if st.button("🔊 Play Voice Translation", key="btn_play_voice",
                 disabled=(not text_output), use_container_width=True):
        with st.spinner("Synthesizing voice..."):
            try:
                audio_bytes = audio_service.generate_speech(text_output, lang_code=tts_lang_code)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.warning("Audio synthesis returned empty result. Check internet connection for gTTS.")
            except Exception as e:
                st.error(f"TTS Error: {e}")

    # Database logging
    if st.button("💾 Log Translation to Database", key="btn_log_db",
                 disabled=(not text_output), use_container_width=True):
        try:
            record = db_service.log_translation(
                detected_gestures=active_seq,
                translated_text=text_output,
                confidence=st.session_state.get("live_confidence", 0.88),
                language=selected_language
            )
            st.success(f"Log saved! ID: {record['id']}")
        except Exception as e:
            st.error(f"Database error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# FRAME CONSUMPTION — pulls from the queue and renders ONE frame per rerun
# Streamlit automatically re-runs this script at ~33ms intervals when active
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state["camera_active"]:
    status_placeholder.markdown('<div class="pulse-badge">● RECORDING ACTIVE</div>', unsafe_allow_html=True)

    q = st.session_state["cam_queue"]
    payload = None

    # Drain queue — use latest available frame
    while True:
        try:
            payload = q.get_nowait()
        except queue.Empty:
            break

    if payload is not None:
        if "error" in payload:
            st.error(payload["error"])
            _stop_camera()
        else:
            # Update session state with latest results
            st.session_state["detected_sequence"] = payload.get("sequence", [])
            st.session_state["translation_buffer"] = payload.get("translation", "")
            st.session_state["live_gesture"] = payload.get("gesture", "IDLE")
            st.session_state["live_confidence"] = payload.get("confidence", 0.0)
            st.session_state["live_hands_detected"] = payload.get("hands_detected", False)
            st.session_state["live_fps"] = payload.get("fps", 0.0)
            st.session_state["live_latency_ms"] = payload.get("latency_ms", 0.0)
            st.session_state["live_queue_depth"] = payload.get("queue_depth", 0)
            st.session_state["live_mem_mb"] = payload.get("mem_mb", 0.0)

            # Render annotated frame
            annotated = payload.get("annotated_frame")
            if annotated is not None:
                display = cv2.flip(annotated, 1)

                # Debug overlay: burn metrics into frame
                if st.session_state["debug_mode"]:
                    fps_val = payload.get("fps", 0.0)
                    lat_val = payload.get("latency_ms", 0.0)
                    gest_val = payload.get("gesture", "IDLE")
                    conf_val = int(payload.get("confidence", 0.0) * 100)
                    hands_val = "HANDS" if payload.get("hands_detected") else "NO HANDS"
                    q_val = payload.get("queue_depth", 0)
                    mem_val = payload.get("mem_mb", 0.0)

                    overlay_lines = [
                        f"FPS: {fps_val:.1f}",
                        f"LATENCY: {lat_val:.1f}ms",
                        f"GESTURE: {gest_val} ({conf_val}%)",
                        f"{hands_val}",
                        f"QUEUE: {q_val}",
                        f"MEM: {mem_val:.0f}MB",
                    ]
                    y = 30
                    for line in overlay_lines:
                        cv2.putText(display, line, (10, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                                    (0, 255, 100), 2, cv2.LINE_AA)
                        y += 28

                    # Hand detection indicator box
                    box_color = (0, 220, 80) if payload.get("hands_detected") else (0, 0, 220)
                    cv2.rectangle(display, (display.shape[1]-160, 10), (display.shape[1]-10, 50), box_color, -1)
                    cv2.putText(display, hands_val[:9], (display.shape[1]-155, 38),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                display_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_rgb, channels="RGB", use_column_width=True)

                # Update debug metric cards
                if st.session_state["debug_mode"] and fps_metric is not None:
                    fps_metric.metric("FPS", f"{payload.get('fps', 0.0):.1f}")
                    latency_metric.metric("Latency", f"{payload.get('latency_ms', 0.0):.1f}ms")
                    mem_metric.metric("RAM", f"{payload.get('mem_mb', 0.0):.0f}MB")
                    queue_metric.metric("Queue Depth", payload.get("queue_depth", 0))
                    hands_metric.metric("Hands", "✅" if payload.get("hands_detected") else "❌")

    else:
        # No frame yet — show spinner
        video_placeholder.info("⏳ Waiting for webcam frames...")

    # Check if thread is still alive
    t = st.session_state.get("cam_thread")
    if t is not None and not t.is_alive():
        st.warning("Camera thread stopped unexpectedly. Click Stop Camera to reset.")
        st.session_state["camera_active"] = False

    # Auto-rerun to pull the next frame (~33ms = ~30 fps display rate)
    time.sleep(0.033)
    st.rerun()

else:
    video_placeholder.info("Click '🔌 Start Camera' to launch webcam translation stream.")
