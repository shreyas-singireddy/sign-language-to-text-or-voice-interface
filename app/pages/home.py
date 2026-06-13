import streamlit as st

from src.services.translation_service import t

# Welcoming Header
st.html(
    f'<h1 class="gradient-text" style="font-size: 3.8rem; margin-bottom: 0px; letter-spacing: -2px; color: #121212 !important;">{t("home_title")}</h1>'
)
st.html(
    f'<p style="font-size: 1.25rem; font-weight: 700; color: #1040C0; text-transform: uppercase; margin-top: 0px;">{t("home_subtitle")}</p>'
)
st.markdown("---")

# 1. HERO SECTION
col_hero_text, col_hero_shapes = st.columns([3, 2])

with col_hero_text:
    st.html(f"""
        <div class="bauhaus-card card-red" style="min-height: 250px;">
            <h2 style="font-size: 2.5rem; line-height: 1.0; margin-bottom: 15px; color: #121212 !important;">{t("hero_title")}</h2>
            <p style="font-size: 1.15rem; line-height: 1.6; color: #333333; margin-bottom: 25px;">
                {t("hero_desc")}
            </p>
        </div>
        """)

    # CTA Buttons
    col_cta1, col_cta2 = st.columns(2)
    with col_cta1:
        if st.button(t("btn_start_translation"), key="btn_hero_translate"):
            (
                st.switch_page("pages/live_translation.py")
                if hasattr(st, "switch_page")
                else st.info("Select 'Live Translation' in the sidebar.")
            )
    with col_cta2:
        if st.button(t("btn_configure_settings"), key="btn_hero_settings"):
            (
                st.switch_page("pages/settings.py")
                if hasattr(st, "switch_page")
                else st.info("Select 'Settings' in the sidebar.")
            )

with col_hero_shapes:
    st.html(f"""
        <div class="bauhaus-card card-blue" style="height: 330px; overflow: hidden; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #E6E6E6 !important;">
            <div style="width: 150px; height: 150px; background-color: #D02020; border-radius: 50%; border: 4px solid #121212; margin-bottom: 10px;"></div>
            <div style="width: 200px; height: 30px; background-color: #F0C020; border: 4px solid #121212; transform: rotate(5deg);"></div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 900; font-size: 1.5rem; text-transform: uppercase; margin-top: 15px; color: #121212 !important;">{t("design_in_motion")}</div>
        </div>
        """)

# 2. PROBLEM STATEMENT SECTION
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(
    f'<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">{t("gap_title")}</h2>',
    unsafe_allow_html=True,
)

col_prob1, col_prob2 = st.columns(2)
with col_prob1:
    st.html(f"""
        <div class="bauhaus-card card-yellow" style="min-height: 200px;">
            <h3 style="color: #D02020 !important; margin-top: 0px;">{t("challenge_title")}</h3>
            <p style="font-size: 1rem; line-height: 1.6; color: #121212 !important;">
                {t("challenge_desc")}
            </p>
        </div>
        """)
with col_prob2:
    st.html(f"""
        <div class="bauhaus-card card-blue" style="min-height: 200px;">
            <h3 style="color: #1040C0 !important; margin-top: 0px;">{t("solution_title")}</h3>
            <p style="font-size: 1rem; line-height: 1.6; color: #121212 !important;">
                {t("solution_desc")}
            </p>
        </div>
        """)

# 3. SOLUTION PIPELINE FLOW CHART
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(
    f'<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">{t("workflow_title")}</h2>',
    unsafe_allow_html=True,
)

st.html(f"""
    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px;">
        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #D02020; color: #121212 !important;">
            <h4 style="margin: 0 0 5px 0; color: #121212 !important;">{t("workflow_step1_title")}</h4>
            <span style="font-size: 0.85rem; color: #555555;">{t("workflow_step1_desc")}</span>
        </div>
        <div style="flex: 0.2; min-width: 30px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; color: #121212 !important;">➔</div>

        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #1040C0; color: #121212 !important;">
            <h4 style="margin: 0 0 5px 0; color: #121212 !important;">{t("workflow_step2_title")}</h4>
            <span style="font-size: 0.85rem; color: #555555;">{t("workflow_step2_desc")}</span>
        </div>
        <div style="flex: 0.2; min-width: 30px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; color: #121212 !important;">➔</div>

        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #F0C020; color: #121212 !important;">
            <h4 style="margin: 0 0 5px 0; color: #121212 !important;">{t("workflow_step3_title")}</h4>
            <span style="font-size: 0.85rem; color: #555555;">{t("workflow_step3_desc")}</span>
        </div>
        <div style="flex: 0.2; min-width: 30px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; color: #121212 !important;">➔</div>

        <div style="flex: 1; min-width: 150px; background-color: #FFFFFF; border: 3px solid #121212; padding: 15px; text-align: center; border-top: 8px solid #121212; color: #121212 !important;">
            <h4 style="margin: 0 0 5px 0; color: #121212 !important;">{t("workflow_step4_title")}</h4>
            <span style="font-size: 0.85rem; color: #555555;">{t("workflow_step4_desc")}</span>
        </div>
    </div>
    """)

# 4. CORE PIPELINE STAGES
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(
    f'<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">{t("stages_title")}</h2>',
    unsafe_allow_html=True,
)

hiw1, hiw2 = st.columns(2)
with hiw1:
    st.html(f"""
        <div class="bauhaus-card">
            <div class="geo-number num-red">01</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px; color: #121212 !important;">{t("stage1_title")}</h3>
                <p style="font-size: 0.95rem; line-height: 1.5; color: #121212 !important;">
                    {t("stage1_desc")}
                </p>
            </div>
        </div>

        <div class="bauhaus-card">
            <div class="geo-number num-blue">02</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px; color: #121212 !important;">{t("stage2_title")}</h3>
                <p style="font-size: 0.95rem; line-height: 1.5; color: #121212 !important;">
                    {t("stage2_desc")}
                </p>
            </div>
        </div>
        """)
with hiw2:
    st.html(f"""
        <div class="bauhaus-card">
            <div class="geo-number num-yellow">03</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px; color: #121212 !important;">{t("stage3_title")}</h3>
                <p style="font-size: 0.95rem; line-height: 1.5; color: #121212 !important;">
                    {t("stage3_desc")}
                </p>
            </div>
        </div>

        <div class="bauhaus-card">
            <div class="geo-number" style="color: #FFFFFF !important;">04</div>
            <div style="margin-left: 85px;">
                <h3 style="margin-top: 0px; color: #121212 !important;">{t("stage4_title")}</h3>
                <p style="font-size: 0.95rem; line-height: 1.5; color: #121212 !important;">
                    {t("stage4_desc")}
                </p>
            </div>
        </div>
        """)

# 5. CORE FEATURES
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(
    f'<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">{t("features_title")}</h2>',
    unsafe_allow_html=True,
)

f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="min-height: 200px;">
            <h4>🎥 {t("feature_capture_title")}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">{t("feature_capture_desc")}</p>
        </div>
        <div class="bauhaus-card card-blue" style="min-height: 200px;">
            <h4>🏋️ {t("feature_training_title")}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">{t("feature_training_desc")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with f_col2:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="min-height: 200px;">
            <h4>🧠 {t("feature_seq_title")}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">{t("feature_seq_desc")}</p>
        </div>
        <div class="bauhaus-card card-yellow" style="min-height: 200px;">
            <h4>💬 {t("feature_hub_title")}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">{t("feature_hub_desc")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with f_col3:
    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="min-height: 200px;">
            <h4>🔊 {t("feature_tts_title")}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">{t("feature_tts_desc")}</p>
        </div>
        <div class="bauhaus-card card-red" style="min-height: 200px;">
            <h4>🛡️ {t("feature_analytics_title")}</h4>
            <p style="font-size: 0.9rem; line-height: 1.5;">{t("feature_analytics_desc")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 6. ACCESSIBILITY COMMITMENT & FUTURE ROADMAP
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(
    f'<h2 style="font-size: 2.2rem; border-bottom: 4px solid #121212; padding-bottom: 10px;">{t("manifesto_title")}</h2>',
    unsafe_allow_html=True,
)

col_man1, col_man2 = st.columns(2)
with col_man1:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="min-height: 250px;">
            <h3 style="color:#D02020 !important;">{t("manifesto_title")}</h3>
            <p style="font-size: 0.95rem; line-height: 1.6;">
                {t("manifesto_desc")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_man2:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="min-height: 250px;">
            <h3 style="color:#1040C0 !important;">{t("roadmap_title")}</h3>
            <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 18px; margin: 0;">
                <li>{t("roadmap_item1")}</li>
                <li>{t("roadmap_item2")}</li>
                <li>{t("roadmap_item3")}</li>
                <li>{t("roadmap_item4")}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 7. CALL TO ACTION & FOOTER
st.html(f"""
    <div style="background-color: #121212; border: 3.5px solid #121212; padding: 40px; text-align: center; color: #FFFFFF !important;">
        <h2 style="color: #FFFFFF !important; font-size: 2.2rem; margin-top: 0px;">{t("cta_title")}</h2>
        <p style="color: #E6E6E6 !important; max-width: 600px; margin: 10px auto 25px auto;">
            {t("cta_desc")}
        </p>
    </div>
    <div style="text-align: center; font-size: 0.8rem; color: #555555; padding: 20px 0;">
        {t("footer_copyright")}
    </div>
    """)
