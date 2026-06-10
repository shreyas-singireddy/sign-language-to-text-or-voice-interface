import streamlit as st
from app.services.database_service import db_service
from app.services.audio_service import audio_service
from config.config import SUPPORTED_LANGUAGES

# Page Header
st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">COMMUNICATION HUB</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>Accessible messaging workspace and historic translation log.</p>", unsafe_allow_html=True)
st.markdown("---")

col_chat, col_tts = st.columns([2, 1])

with col_tts:
    st.markdown(
        """
        <div class="bauhaus-card card-yellow" style="padding: 20px;">
            <h3 style="margin-top: 0px;">ACCESSIBILITY TTS</h3>
            <p style="font-size: 0.85rem; color: #555555; margin-bottom: 0px;">
                Type a message below to synthesize high-fidelity voice speech.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    tts_text = st.text_area("Write message here:", height=100, key="hub_tts_text")
    hub_lang = st.selectbox("Speech Accent / Language", options=list(SUPPORTED_LANGUAGES.keys()), index=0, key="hub_tts_lang")
    
    if st.button("🔊 Synthesize Message", key="btn_hub_tts_play", use_container_width=True, disabled=not tts_text.strip()):
        with st.spinner("Synthesizing voice..."):
            lang_code = SUPPORTED_LANGUAGES[hub_lang]
            audio_bytes = audio_service.generate_speech(tts_text, lang_code=lang_code)
            st.audio(audio_bytes, format="audio/wav")

with col_chat:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">TRANSLATION LOG HISTORY</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Refresh button
    if st.button("🔄 Refresh Logs", key="btn_refresh_history", use_container_width=True):
        st.rerun()

    history = db_service.get_history(limit=50)

    if history:
        for idx, record in enumerate(history):
            record_id = record.get("id")
            gestures = ", ".join(record.get("detectedGestures", []))
            text = record.get("translatedText", "")
            lang = record.get("language", "English")
            timestamp = record.get("timestamp", "")[:19].replace("T", " ")
            is_offline = record.get("is_offline", False)
            
            # Badge styles
            badge_text = "OFFLINE LOG" if is_offline else "CLOUD DB"
            badge_class = "status-offline" if is_offline else "status-online"
            
            # Draw standard glass container
            st.markdown(
                f"""
                <div class="bauhaus-card" style="margin-bottom: 12px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #555555; margin-bottom: 6px;">
                        <span>🕒 {timestamp} ({lang})</span>
                        <span class="status-pill {badge_class}" style="font-size: 9px; padding: 2px 6px;">{badge_text}</span>
                    </div>
                    <p style="font-size: 1.2rem; font-weight: 800; text-transform: uppercase; margin: 4px 0; color: #121212;">{text}</p>
                    <div style="font-size: 0.8rem; color: #555555;">Detected Gestures: <code style="color: #D02020;">{gestures}</code></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Action buttons
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                if st.button(f"🔊 Play Audio", key=f"btn_play_{record_id}_{idx}", use_container_width=True):
                    with st.spinner("Preparing playback..."):
                        lang_code = SUPPORTED_LANGUAGES.get(lang, "en-US")
                        audio_bytes = audio_service.generate_speech(text, lang_code=lang_code)
                        st.audio(audio_bytes, format="audio/wav")
            with act_col2:
                if st.button(f"🗑️ Delete Record", key=f"btn_del_{record_id}_{idx}", use_container_width=True):
                    if db_service.delete_history_record(record_id):
                        st.success("Record deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete record.")
    else:
        st.info("No logs present. Start translating on the 'Live Translation' page to generate records.")
