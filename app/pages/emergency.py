"""
SignBridge AI — Layer 12: Emergency Communication System Page
Life-critical communication interface for deaf and mute users in emergencies.
Features: SOS broadcast, quick-access phrases, emergency contacts,
multilingual emergency alerts, and protocol activation.
"""
import streamlit as st
import streamlit.components.v1 as components
from emergency.sos_detector import sos_detector, LEVEL_CRITICAL, LEVEL_URGENT
from emergency.alert_dispatcher import alert_dispatcher
from emergency.panic_protocol import panic_protocol
from emergency.emergency_phrases import EMERGENCY_CATEGORIES, get_all_phrases_for_language
from speech.tts_engine import tts_engine
from config.config import SUPPORTED_LANGUAGES

# ─── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="font-size: 3rem; margin-bottom: 5px; text-transform: uppercase;
        font-family: 'Space Grotesk', sans-serif; font-weight: 900; color: #D02020 !important;">
        🚨 EMERGENCY SYSTEM
    </h1>
    <p style='font-size: 1.1rem; font-weight: bold; color: #D02020;'>
        Critical communication platform for life-threatening situations.
        Instant SOS broadcast, multilingual emergency phrases, and alert dispatch.
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ─── Session State ──────────────────────────────────────────────────────────────
if "emergency_active" not in st.session_state:
    st.session_state["emergency_active"] = False
if "emergency_language" not in st.session_state:
    st.session_state["emergency_language"] = "English"
if "emergency_log" not in st.session_state:
    st.session_state["emergency_log"] = []
if "sos_history" not in st.session_state:
    st.session_state["sos_history"] = []

# ─── EMERGENCY ACTIVE BANNER ────────────────────────────────────────────────────
if st.session_state.get("emergency_active", False):
    st.markdown(
        """
        <div style="
            background: #D02020;
            border: 5px solid #FFFFFF;
            color: #FFFFFF;
            font-family: 'Space Grotesk', monospace;
            font-weight: 900;
            font-size: 1.6rem;
            text-transform: uppercase;
            text-align: center;
            padding: 24px;
            margin-bottom: 20px;
            animation: pulse-alert 1s infinite;
            box-shadow: 0 0 40px rgba(208, 32, 32, 0.8);
        ">
            🚨 EMERGENCY PROTOCOL ACTIVE 🚨
            <br/>
            <span style="font-size: 0.9rem;">All channels alerted. Stay calm. Help is coming.</span>
        </div>
        <style>
        @keyframes pulse-alert { 0%,100%{opacity:1} 50%{opacity:0.75} }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("✅ Emergency Resolved — Deactivate Protocol", key="btn_deactivate_emergency", use_container_width=True):
        st.session_state["emergency_active"] = False
        panic_protocol.deactivate()
        sos_detector.reset_session()
        st.success("Emergency protocol deactivated. Stay safe.")
        st.rerun()

    st.markdown("---")

# ─── MAIN LAYOUT ────────────────────────────────────────────────────────────────
col_sos, col_phrases = st.columns([1, 2])

# ── LEFT: SOS BROADCAST PANEL ──────────────────────────────────────────────────
with col_sos:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 20px; text-align: center;">
            <h3 style="margin-top: 0; color: #D02020 !important;">SOS BROADCAST</h3>
            <p style="font-size: 0.85rem; color: #555;">
                Activate to send emergency signals across all channels.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Primary SOS Button
    st.markdown(
        """
        <div style="text-align: center; margin: 10px 0;">
            <div style="
                width: 160px;
                height: 160px;
                background: #D02020;
                border-radius: 50%;
                border: 8px solid #121212;
                box-shadow: 10px 10px 0px #121212;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.8rem;
                font-weight: 900;
                color: #FFFFFF;
                margin: 0 auto;
                letter-spacing: 0.1em;
            ">SOS</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    user_name = st.session_state.get("user_name", "SignBridge User")

    if st.button("🚨 ACTIVATE FULL SOS PROTOCOL", key="btn_sos_activate", use_container_width=True):
        from emergency.sos_detector import SOSEvent, LEVEL_CRITICAL
        from datetime import datetime, timezone
        critical_event = SOSEvent(
            severity=LEVEL_CRITICAL,
            triggered_tokens=["SOS"],
            matching_pattern=["SOS"],
            confidence=1.0,
            timestamp=datetime.now(timezone.utc),
            message="Manual SOS activated by user.",
        )
        result = panic_protocol.activate(critical_event, user_name=user_name)
        st.session_state["emergency_active"] = True
        st.session_state["sos_history"].append(result["alert_record"].to_dict())

        # Play emergency TTS
        audio_bytes = tts_engine.speak_emergency(result["tts_text"])
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

        st.markdown(result["ui_html"], unsafe_allow_html=True)
        st.rerun()

    st.markdown("---")

    # Quick SOS test from sign tokens
    st.markdown("### Test SOS from Signs")
    test_tokens = st.text_input(
        "Enter sign tokens (comma-separated):",
        value="CHEST, PAIN",
        key="input_sos_test_tokens",
        id="input_emergency_tokens"
    )
    if st.button("🔍 Check SOS Pattern", key="btn_check_sos", use_container_width=True):
        token_list = [t.strip().upper() for t in test_tokens.split(",") if t.strip()]
        event = sos_detector.check_tokens(token_list)
        if event:
            st.markdown(
                f"""
                <div class="bauhaus-card card-red" style="padding: 14px;">
                    <strong>SOS DETECTED</strong><br/>
                    Severity: <code>{event.severity}</code><br/>
                    Pattern: <code>{event.matching_pattern}</code><br/>
                    Confidence: <code>{event.confidence:.0%}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.success("✅ No emergency patterns detected in this sequence.")

    # Alert statistics
    st.markdown("---")
    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="padding: 14px; text-align: center;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #555;">Total Alerts</div>
            <div style="font-size: 2.5rem; font-weight: 900;">{alert_dispatcher.get_alert_count()}</div>
            <div style="font-size: 0.75rem; color: #555;">Dispatched This Session</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ── RIGHT: EMERGENCY PHRASE BANK ──────────────────────────────────────────────
with col_phrases:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0;">EMERGENCY PHRASE BANK</h3>
            <p style="font-size: 0.85rem; color: #555; margin-bottom: 0;">
                Tap any phrase to hear it synthesized in the selected language.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Language selector
    em_lang = st.selectbox(
        "Emergency Language:",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        key="sel_emergency_lang",
        id="select_emergency_lang"
    )
    st.session_state["emergency_language"] = em_lang

    # Category tabs
    category_tabs = st.tabs(list(EMERGENCY_CATEGORIES.keys()))
    for tab, (category, phrases) in zip(category_tabs, EMERGENCY_CATEGORIES.items()):
        with tab:
            for idx, phrase in enumerate(phrases):
                ph_col1, ph_col2 = st.columns([4, 1])
                with ph_col1:
                    st.markdown(
                        f"""
                        <div class="bauhaus-card" style="padding: 10px 14px; margin-bottom: 6px;">
                            <span style="font-size: 0.95rem; font-weight: 700;">{phrase}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with ph_col2:
                    if st.button("🔊", key=f"btn_em_phrase_{category}_{idx}", use_container_width=True, help="Play this phrase"):
                        lang_code = SUPPORTED_LANGUAGES.get(em_lang, "en-US")
                        audio_bytes = tts_engine.speak(phrase, language_name=em_lang)
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                            st.session_state["emergency_log"].append({
                                "phrase": phrase, "language": em_lang
                            })

# ─── EMERGENCY CONTACT MANAGER ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div class="bauhaus-card card-yellow" style="padding: 20px;">
        <h3 style="margin-top: 0;">EMERGENCY CONTACTS</h3>
    </div>
    """,
    unsafe_allow_html=True
)

contact_col1, contact_col2, contact_col3 = st.columns(3)
with contact_col1:
    ec1_name = st.text_input("Contact 1 Name", value="", key="ec1_name", id="input_ec1_name")
    ec1_phone = st.text_input("Contact 1 Phone", value="", key="ec1_phone", id="input_ec1_phone")
with contact_col2:
    ec2_name = st.text_input("Contact 2 Name", value="", key="ec2_name", id="input_ec2_name")
    ec2_phone = st.text_input("Contact 2 Phone", value="", key="ec2_phone", id="input_ec2_phone")
with contact_col3:
    medical_info = st.text_area("Medical Information", value="", height=100, key="medical_info")

if st.button("💾 Save Emergency Profile", key="btn_save_emergency", use_container_width=True):
    st.session_state["emergency_profile"] = {
        "contact1": {"name": ec1_name, "phone": ec1_phone},
        "contact2": {"name": ec2_name, "phone": ec2_phone},
        "medical": medical_info,
    }
    st.success("Emergency profile saved to session. In production this would persist to encrypted storage.")

# ─── ALERT HISTORY ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Alert History This Session")
history = alert_dispatcher.get_recent_alerts(10)
if history:
    for alert in reversed(history):
        severity_color = "#D02020" if alert["severity"] == LEVEL_CRITICAL else "#E06010"
        st.markdown(
            f"""
            <div class="bauhaus-card" style="padding: 12px; margin-bottom: 8px; border-left: 8px solid {severity_color};">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #555; margin-bottom: 4px;">
                    <span><strong>{alert['severity']}</strong> — {alert['dispatched_at'][:19]}</span>
                    <span>Conf: {int(alert['confidence']*100)}%</span>
                </div>
                <p style="margin: 0; font-weight: 700; font-size: 0.95rem;">{alert['message']}</p>
                <div style="font-size: 0.8rem; color: #555;">Channels: {', '.join(alert['channels'])}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No emergency alerts dispatched in this session.")
