import streamlit as st
from database.mongodb import db_conn
from config.config import PROJECT_NAME

# Welcoming Header
st.markdown('<h1 class="gradient-text" style="font-size: 3.8rem; margin-bottom: 0px; letter-spacing: -2px;">SIGNBRIDGE AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.25rem; font-weight: 700; color: #1040C0; text-transform: uppercase; margin-top: 0px;">Breaking Communication Barriers with AI</p>', unsafe_allow_html=True)
st.markdown("---")

# 1. HERO SECTION
col_hero_text, col_hero_shapes = st.columns([3, 2])

with col_hero_text:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="min-height: 250px;">
            <h2 style="font-size: 2.5rem; line-height: 1.0; margin-bottom: 15px;">COMMUNICATION WITHOUT BARRIERS</h2>
            <p style="font-size: 1.15rem; line-height: 1.6; color: #333333; margin-bottom: 25px;">
                SignBridge AI transforms American Sign Language (ASL) gestures into real-time speech and text 
                using Computer Vision and deep neural network sequence pipelines. Built with accessibility-first 
                principles to ensure natural connection for deaf, mute, and hearing-impaired communities.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # CTA Buttons
    col_cta1, col_cta2 = st.columns(2)
    with col_cta1:
        if st.button("Start Live Translation", key="btn_hero_translate"):
            st.switch_page("pages/live_translation.py") if hasattr(st, "switch_page") else st.info("Select 'Live Translation' in the sidebar.")
    with col_cta2:
        if st.button("Configure Settings", key="btn_hero_settings"):
            st.switch_page("pages/settings.py") if hasattr(st, "switch_page") else st.info("Select 'Settings' in the sidebar.")

with col_hero_shapes:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="height: 330px; overflow: hidden; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #E6E6E6 !important;">
            <div style="width: 150px; height: 150px; background-color: #D02020; border-radius: 50%; border: 4px solid #121212; margin-bottom: 10px;"></div>
            <div style="width: 200px; height: 30px; background-color: #F0C020; border: 4px solid #121212; transform: rotate(5deg);"></div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 900; font-size: 1.5rem; text-transform: uppercase; margin-top: 15px;">DESIGN IN MOTION</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 2. PROBLEM STATEMENT SECTION
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">THE COMMUNICATION GAP</h2>', unsafe_allow_html=True)

col_prob1, col_prob2 = st.columns(2)
with col_prob1:
    st.markdown(
        """
        <div class="bauhaus-card card-yellow" style="min-height: 200px;">
            <h3 style="color: #D02020 !important;">THE CHALLENGE</h3>
            <p style="font-size: 1rem; line-height: 1.6;">
                Over 70 million deaf individuals globally rely on sign language as their primary mode of communication. 
                However, less than 1% of the hearing population understands sign language, creating absolute barriers in 
                daily routines, workplaces, medical facilities, and emergency scenarios.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_prob2:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="min-height: 200px;">
            <h3 style="color: #1040C0 !important;">THE SOLUTION</h3>
            <p style="font-size: 1rem; line-height: 1.6;">
                SignBridge AI bypasses traditional translators. By processing video feeds and predicting sign features 
                in real time, it reconstructs conversational dialogue, offering instantaneous translation to hearing 
                non-signers via text outputs and voice synthesis.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 3. SOLUTION PIPELINE FLOW CHART
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">THE TRANSLATION WORKFLOW</h2>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px;">
        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #D02020;">
            <h4 style="margin: 0 0 5px 0;">1. CAMERA</h4>
            <span style="font-size: 0.85rem; color: #555555;">Webcam Stream Ingests Frames</span>
        </div>
        <div style="flex: 0.2; min-width: 30px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold;">➔</div>
        
        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #1040C0;">
            <h4 style="margin: 0 0 5px 0;">2. VISION</h4>
            <span style="font-size: 0.85rem; color: #555555;">MediaPipe Extracts Skeletons</span>
        </div>
        <div style="flex: 0.2; min-width: 30px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold;">➔</div>
        
        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #F0C020;">
            <h4 style="margin: 0 0 5px 0;">3. DETECTION</h4>
            <span style="font-size: 0.85rem; color: #555555;">Gesture Engine Maps Shapes</span>
        </div>
        <div style="flex: 0.2; min-width: 30px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold;">➔</div>
        
        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #121212;">
            <h4 style="margin: 0 0 5px 0;">4. TRANSLATION</h4>
            <span style="font-size: 0.85rem; color: #555555;">Text & Synthetic Speech Output</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 4. HOW IT WORKS 4-STEP CONSTRUCTIVIST BLOCKS
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">CORE PIPELINE STAGES</h2>', unsafe_allow_html=True)

hiw1, hiw2 = st.columns(2)
with hiw1:
    st.markdown(
        """
        <div class="bauhaus-card">
            <div class="geo-number num-red">01</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px;">CAPTURE</h3>
                <p style="font-size: 0.95rem; line-height: 1.5;">
                    The system reads frames from any camera (webcam, external source) using OpenCV, extracting raw 
                    visual information at 24+ frames per second.
                </p>
            </div>
        </div>
        
        <div class="bauhaus-card">
            <div class="geo-number num-blue">02</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px;">ANALYZE</h3>
                <p style="font-size: 0.95rem; line-height: 1.5;">
                    Features are processed using MediaPipe to generate x, y, and z skeletal coordinates for 
                    pose, fingers, hands, and facial indicators.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with hiw2:
    st.markdown(
        """
        <div class="bauhaus-card">
            <div class="geo-number num-yellow">03</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px;">TRANSLATE</h3>
                <p style="font-size: 0.95rem; line-height: 1.5;">
                    Sequence models monitor joint coordinates over temporal sliding windows to identify gestures 
                    and decode them into coherent sentences.
                </p>
            </div>
        </div>
        
        <div class="bauhaus-card">
            <div class="geo-number">04</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px;">COMMUNICATE</h3>
                <p style="font-size: 0.95rem; line-height: 1.5;">
                    Decoded sentences are displayed visually and synthesized into synthetic audio formats, 
                    facilitating seamless accessibility.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 5. CORE FEATURES
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">CORE PLATFORM FEATURES</h2>', unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="min-height: 200px;">
            <h4>🎥 Real-time Capture</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">Webcam pipeline running MediaPipe tracking points with minimal lag.</p>
        </div>
        <div class="bauhaus-card card-blue" style="min-height: 200px;">
            <h4>🏋️ custom Training</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">Training console to record and export coordinate dataset collections.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with f_col2:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="min-height: 200px;">
            <h4>🧠 Sequence Translation</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">LSTM and Transformer architectures decoding sequences into fluent sentences.</p>
        </div>
        <div class="bauhaus-card card-yellow" style="min-height: 200px;">
            <h4>💬 Message Hub</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">Chat transcripts database and accessibility text-to-speech tools.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with f_col3:
    st.markdown(
        """
        <div class="bauhaus-card card-yellow" style="min-height: 200px;">
            <h4>🔊 TTS Synthesis</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">Coqui TTS engine generating natural voices across multiple languages.</p>
        </div>
        <div class="bauhaus-card card-red" style="min-height: 200px;">
            <h4>🛡️ System Analytics</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">Usage charts, daily timelines, and classification confidence indicators.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 6. ACCESSIBILITY COMMITMENT & FUTURE ROADMAP
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">OUR MANIFESTO</h2>', unsafe_allow_html=True)

col_man1, col_man2 = st.columns(2)
with col_man1:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="min-height: 250px;">
            <h3 style="color:#D02020 !important;">ACCESSIBILITY MANIFESTO</h3>
            <p style="font-size: 0.95rem; line-height: 1.6;">
                Communication is a fundamental human right. Our platform is designed around strict WCAG guidelines. 
                With high-contrast geometric themes, large and clear sans-serif typography, and keyboard navigation 
                mechanisms, we guarantee accessibility for all users regardless of visual or motor capabilities.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_man2:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="min-height: 250px;">
            <h3 style="color:#1040C0 !important;">FUTURE ROADMAP</h3>
            <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 18px; margin: 0;">
                <li><strong>Sign ➔ Voice</strong>: Seamless multi-accent speech outputs.</li>
                <li><strong>Voice ➔ Text</strong>: Integrated transcription engines (Whisper STT).</li>
                <li><strong>Text ➔ Sign</strong>: Synthetic 3D avators demonstrating signs in real-time.</li>
                <li><strong>AI Companion</strong>: Contextual translation suggestions and auto-complete filters.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# 7. CALL TO ACTION & FOOTER
st.markdown(
    """
    <div style="background-color: #121212; border: 3.5px solid #121212; padding: 40px; text-align: center; color: #FFFFFF !important;">
        <h2 style="color: #FFFFFF !important; font-size: 2.2rem; margin-top: 0px;">JOIN THE ACCESSIBILITY REVOLUTION</h2>
        <p style="color: #E6E6E6 !important; max-width: 600px; margin: 10px auto 25px auto;">
            Expand translation maps, record signs, or run live translation sessions to break down language barriers.
        </p>
    </div>
    <div style="text-align: center; font-size: 0.8rem; color: #555555; padding: 20px 0;">
        SignBridge AI © 2026. Designed under the Bauhaus Aesthetic. Accessibility First.
    </div>
    """,
    unsafe_allow_html=True
)
