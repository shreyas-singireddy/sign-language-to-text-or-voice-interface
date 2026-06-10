"""
SignBridge AI — Communication Hub (Layer 7: Conversation Platform)
Full conversation platform with dialogue management, emotion detection,
STT input, response suggestions, and session history.
"""
import streamlit as st
import streamlit.components.v1 as components
from app.services.database_service import db_service
from speech.tts_engine import tts_engine
from speech.stt_engine import stt_engine
from conversation.dialogue_manager import dialogue_manager
from conversation.schemas import MessageRole, EmotionTone
from multilingual.language_registry import language_registry
from config.config import SUPPORTED_LANGUAGES
from datetime import datetime

# ─── Page Header ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="font-size: 3rem; margin-bottom: 5px; text-transform: uppercase;
        font-family: 'Space Grotesk', sans-serif; font-weight: 900;">
        CONVERSATION HUB
    </h1>
    <p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>
        Full conversation platform — dialogue management, emotion detection, voice synthesis, and history.
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ─── Session State Init ──────────────────────────────────────────────────────────
if "conv_session_id" not in st.session_state:
    st.session_state["conv_session_id"] = None
if "conv_language" not in st.session_state:
    st.session_state["conv_language"] = "English"

# ─── Layout ──────────────────────────────────────────────────────────────────────
col_chat, col_controls = st.columns([3, 1])

# ── CONTROLS PANEL ────────────────────────────────────────────────────────────
with col_controls:
    st.markdown(
        """
        <div class="bauhaus-card card-yellow" style="padding: 20px;">
            <h4 style="margin-top: 0;">SESSION CONTROLS</h4>
        </div>
        """, unsafe_allow_html=True
    )

    conv_lang = st.selectbox(
        "Conversation Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        key="sel_conv_lang",
        id="select_conv_lang"
    )
    st.session_state["conv_language"] = conv_lang

    if st.button("▶ Start New Session", key="btn_new_session", use_container_width=True):
        session_id = dialogue_manager.start_session(language=conv_lang)
        st.session_state["conv_session_id"] = session_id
        st.success(f"Session started")
        st.rerun()

    session_id = st.session_state.get("conv_session_id")
    if session_id:
        summary = dialogue_manager.get_session_summary(session_id)
        st.markdown(
            f"""
            <div class="bauhaus-card" style="padding: 14px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase; margin-bottom: 8px;">Active Session</div>
                <div style="font-size: 0.85rem; margin-bottom: 4px;">Turns: <strong>{summary.total_turns}</strong></div>
                <div style="font-size: 0.85rem; margin-bottom: 4px;">Messages: <strong>{summary.total_messages}</strong></div>
                <div style="font-size: 0.85rem; margin-bottom: 4px;">Signs: <strong>{summary.sign_tokens_processed}</strong></div>
                <div style="font-size: 0.85rem;">Emotion: <strong>{summary.dominant_emotion.value.upper()}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🔄 Reset Session", key="btn_reset_session", use_container_width=True):
            dialogue_manager.reset_session(session_id)
            st.success("Session reset.")
            st.rerun()

    st.markdown("---")

    # STT Section
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 14px;">
            <h4 style="margin-top: 0; font-size: 0.95rem;">VOICE INPUT (STT)</h4>
        </div>
        """, unsafe_allow_html=True
    )
    lang_bcp47 = SUPPORTED_LANGUAGES.get(conv_lang, "en-US")
    components.html(
        stt_engine.get_stt_html(lang_code=lang_bcp47, button_label="🎤 Listen"),
        height=160,
        scrolling=False
    )

    st.markdown("---")

    # TTS Manual Synthesis
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 14px;">
            <h4 style="margin-top: 0; font-size: 0.95rem;">ACCESSIBILITY TTS</h4>
        </div>
        """, unsafe_allow_html=True
    )
    tts_text = st.text_area("Text to speak:", height=80, key="ctrl_tts_text")
    if st.button("🔊 Synthesize Voice", key="btn_ctrl_tts", use_container_width=True, disabled=not tts_text.strip()):
        with st.spinner("Synthesizing..."):
            audio_bytes = tts_engine.speak(tts_text, language_name=conv_lang)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")

# ── MAIN CHAT PANEL ──────────────────────────────────────────────────────────────
with col_chat:
    # Manual signer input (simulates Layer 4 output)
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 16px; margin-bottom: 12px;">
            <h3 style="margin-top: 0;">SIGNER INPUT SIMULATOR</h3>
            <p style="font-size: 0.85rem; color: #555; margin: 0;">
                In production, this receives output automatically from Layer 4. For testing, enter signs manually.
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    input_col1, input_col2 = st.columns([3, 1])
    with input_col1:
        sign_input = st.text_input(
            "Enter sign tokens (comma-separated):",
            placeholder="e.g. WATER, WANT",
            key="input_sign_tokens",
            id="input_conv_signs"
        )
    with input_col2:
        send_confidence = st.slider("Confidence", min_value=0.1, max_value=1.0, value=0.92, step=0.05, key="sl_confidence")

    if st.button("📤 Send Signer Message", key="btn_send_sign", use_container_width=True):
        if sign_input.strip():
            session_id = st.session_state.get("conv_session_id")
            session_id = dialogue_manager.get_or_create_session(session_id, language=conv_lang)
            st.session_state["conv_session_id"] = session_id

            # Quick translate via rule-based
            from translation.engine import translation_engine
            tokens = [t.strip().upper() for t in sign_input.split(",") if t.strip()]
            translated = translation_engine.translate_simple(tokens, target_language=conv_lang, confidence=send_confidence)

            # Process turn
            turn = dialogue_manager.process_turn(
                session_id=session_id,
                signs=tokens,
                translated_text=translated,
                language=conv_lang,
                confidence=send_confidence,
            )

            # Play TTS
            audio_bytes = tts_engine.speak(translated, language_name=conv_lang)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")

            st.rerun()

    st.markdown("---")

    # Listener reply input
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 14px; margin-bottom: 12px;">
            <h4 style="margin-top: 0;">LISTENER REPLY</h4>
        </div>
        """, unsafe_allow_html=True
    )
    listener_reply = st.text_input(
        "Hearing participant reply:",
        placeholder="Type your response here...",
        key="input_listener_reply",
        id="input_listener_msg"
    )
    if st.button("📨 Send Reply", key="btn_send_reply", use_container_width=True):
        if listener_reply.strip():
            session_id = st.session_state.get("conv_session_id")
            session_id = dialogue_manager.get_or_create_session(session_id, language=conv_lang)
            st.session_state["conv_session_id"] = session_id
            dialogue_manager.add_listener_reply(session_id, listener_reply, language=conv_lang)
            st.rerun()

    # ── CONVERSATION THREAD DISPLAY ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💬 Conversation Thread")

    session_id = st.session_state.get("conv_session_id")
    if session_id:
        messages = dialogue_manager.get_messages(session_id)
        if messages:
            for msg in reversed(messages):
                if msg.role == MessageRole.SIGNER:
                    emotion_color = {
                        EmotionTone.URGENT: "card-red",
                        EmotionTone.DISTRESSED: "card-blue",
                        EmotionTone.GRATEFUL: "card-yellow",
                        EmotionTone.FRIENDLY: "card-blue",
                    }.get(msg.emotion, "")
                    signs_display = ", ".join(msg.original_signs) if msg.original_signs else ""
                    st.markdown(
                        f"""
                        <div class="bauhaus-card {emotion_color}" style="padding: 14px; margin-bottom: 8px; border-left: 8px solid #D02020;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #555; margin-bottom: 6px;">
                                <span>🤟 SIGNER [{msg.language}] — {msg.emotion.value.upper()}</span>
                                <span>Conf: {int(msg.confidence*100)}% | {msg.timestamp.strftime('%H:%M:%S')}</span>
                            </div>
                            <p style="font-size: 1.15rem; font-weight: 800; text-transform: uppercase; margin: 0;">{msg.text}</p>
                            {"<div style='font-size: 0.8rem; color: #888; margin-top: 4px;'>Signs: <code>" + signs_display + "</code></div>" if signs_display else ""}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif msg.role == MessageRole.LISTENER:
                    st.markdown(
                        f"""
                        <div class="bauhaus-card" style="padding: 14px; margin-bottom: 8px; border-left: 8px solid #1040C0;">
                            <div style="font-size: 0.75rem; color: #555; margin-bottom: 4px;">
                                👂 LISTENER — {msg.timestamp.strftime('%H:%M:%S')}
                            </div>
                            <p style="font-size: 1rem; font-weight: 600; margin: 0;">{msg.text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("Conversation thread is empty. Send a signer message to begin.")
    else:
        st.info("Start a new session using the controls panel.")

    # ── HISTORY LOG ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Database Log History")
    if st.button("🔄 Refresh Logs", key="btn_refresh_logs", use_container_width=True):
        st.rerun()

    history = db_service.get_history(limit=20)
    if history:
        for idx, record in enumerate(history):
            record_id = record.get("id")
            gestures = ", ".join(record.get("detectedGestures", []))
            text = record.get("translatedText", "")
            lang = record.get("language", "English")
            timestamp = record.get("timestamp", "")[:19].replace("T", " ")

            log_col1, log_col2 = st.columns([5, 1])
            with log_col1:
                st.markdown(
                    f"""
                    <div class="bauhaus-card" style="padding: 12px; margin-bottom: 6px;">
                        <div style="font-size: 0.75rem; color: #555; margin-bottom: 4px;">🕒 {timestamp} ({lang})</div>
                        <p style="font-size: 1rem; font-weight: 700; margin: 0;">{text}</p>
                        <div style="font-size: 0.75rem; color: #888;">Gestures: <code>{gestures}</code></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with log_col2:
                if st.button("🔊", key=f"btn_log_play_{record_id}_{idx}", use_container_width=True):
                    audio_bytes = tts_engine.speak(text, language_name=lang)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.info("No logged translations yet.")
