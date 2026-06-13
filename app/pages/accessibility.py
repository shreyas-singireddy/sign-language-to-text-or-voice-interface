"""
SignBridge AI — Layer 10: Accessibility Settings Page
Full accessibility control center: themes, font scaling, keyboard shortcuts,
screen reader settings, and motion preferences.
"""

import streamlit as st
import streamlit.components.v1 as components

from accessibility.keyboard_nav import keyboard_nav
from accessibility.screen_reader_hints import screen_reader_hints
from accessibility.theme_manager import (
    THEME_DESCRIPTIONS,
    THEME_LABELS,
    AccessibilityTheme,
    theme_manager,
)
from src.services.translation_service import t

# ─── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <h1 style="font-size: 3rem; margin-bottom: 5px; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif; font-weight: 900;">
        {t("acc_title")}
    </h1>
    <p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>
        {t("acc_subtitle")}
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ─── Session State Init ─────────────────────────────────────────────────────────
if "active_themes" not in st.session_state:
    st.session_state["active_themes"] = [AccessibilityTheme.BAUHAUS_DEFAULT.value]
if "font_scale" not in st.session_state:
    st.session_state["font_scale"] = 100
if "screen_reader_mode" not in st.session_state:
    st.session_state["screen_reader_mode"] = False

# ─── Apply Active Themes ────────────────────────────────────────────────────────
combined_css = theme_manager.get_combined_css(st.session_state["active_themes"])
if combined_css.strip():
    st.markdown(theme_manager.inject_css(combined_css), unsafe_allow_html=True)

# ─── Layout ─────────────────────────────────────────────────────────────────────
col_themes, col_controls = st.columns([2, 1])

with col_themes:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("acc_visual_presets")}</h3>
            <p style="font-size: 0.9rem; color: #555; margin-bottom: 0;">
                {t("acc_visual_desc")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    theme_options = {v: k for k, v in THEME_LABELS.items()}
    theme_values = list(THEME_LABELS.values())
    theme_keys = list(THEME_LABELS.keys())

    selected_themes = []
    for theme_enum, label in THEME_LABELS.items():
        is_active = theme_enum.value in st.session_state["active_themes"]
        description = THEME_DESCRIPTIONS.get(theme_enum, "")
        col_check, col_desc = st.columns([1, 4])
        with col_check:
            checked = st.checkbox(label, value=is_active, key=f"theme_cb_{theme_enum.value}")
        with col_desc:
            st.markdown(
                f"<span style='font-size: 0.85rem; color: #555; font-style: italic;'>{description}</span>",
                unsafe_allow_html=True,
            )
        if checked:
            selected_themes.append(theme_enum.value)

    if not selected_themes:
        selected_themes = [AccessibilityTheme.BAUHAUS_DEFAULT.value]

    if st.button(f"✅ {t('acc_apply_themes')}", key="btn_apply_themes", use_container_width=True):
        st.session_state["active_themes"] = selected_themes
        st.success(t("acc_themes_applied", themes=", ".join(selected_themes)))
        st.rerun()

    # Live preview badge
    st.markdown("---")
    st.markdown(f"### {t('acc_theme_preview')}")
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h4 style="margin-top: 0;">{t("acc_sample_card")}</h4>
            <p style="margin: 0;">{t("acc_sample_card_desc")}</p>
        </div>
        <div class="bauhaus-card card-red" style="padding: 15px; text-align: center; margin-top: 10px;">
            <strong>{t("acc_bauhaus_headline")}</strong>
        </div>
        <div class="bauhaus-card card-yellow" style="padding: 15px; text-align: center; margin-top: 10px;">
            <strong>{t("acc_metric")}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_controls:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("acc_controls")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Font size control
    font_scale = st.slider(
        t("acc_font_scale"),
        min_value=80,
        max_value=150,
        value=st.session_state["font_scale"],
        step=10,
        key="slider_font_scale",
    )
    if font_scale != st.session_state["font_scale"]:
        st.session_state["font_scale"] = font_scale
        font_css = f"html, body, .stApp {{ font-size: {font_scale}% !important; }}"
        st.markdown(f"<style>{font_css}</style>", unsafe_allow_html=True)

    st.markdown(f"**{t('acc_active_scale', scale=font_scale)}**")

    st.markdown("---")

    # Screen reader mode toggle
    sr_mode = st.toggle(
        t("acc_screen_reader_mode"),
        value=st.session_state["screen_reader_mode"],
        key="toggle_sr_mode",
        help=t("acc_screen_reader_help"),
    )
    st.session_state["screen_reader_mode"] = sr_mode
    if sr_mode:
        st.markdown(
            screen_reader_hints.live_region(
                content=f"<span>{t('acc_screen_reader_active')}</span>",
                aria_label="Screen reader status",
            ),
            unsafe_allow_html=True,
        )
        st.success(t("acc_screen_reader_success"))

    st.markdown("---")

    # WCAG compliance status
    active_count = len(st.session_state["active_themes"])
    has_high_contrast = AccessibilityTheme.HIGH_CONTRAST.value in st.session_state["active_themes"]
    has_reduced_motion = AccessibilityTheme.REDUCED_MOTION.value in st.session_state["active_themes"]
    wcag_level = "AA"
    if has_high_contrast and has_reduced_motion and sr_mode:
        wcag_level = "AAA"
    elif has_high_contrast or has_reduced_motion:
        wcag_level = "AA+"

    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="padding: 16px; text-align: center;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase;">{t("acc_wcag_compliance")}</div>
            <div style="font-size: 2.5rem; font-weight: 900; color: #121212;">{wcag_level}</div>
            <div style="font-size: 0.75rem; color: #555;">{t("acc_themes_active_count", count=active_count)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Keyboard Shortcuts Reference ───────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""
    <div class="bauhaus-card card-yellow" style="padding: 20px;">
        <h3 style="margin-top: 0;">{t("acc_keyboard_shortcuts")}</h3>
        <p style="font-size: 0.9rem; color: #555;">
            {t("acc_keyboard_desc")}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(keyboard_nav.generate_shortcut_reference_html(), unsafe_allow_html=True)

# Inject keyboard listener
components.html(keyboard_nav.generate_keyboard_listener_html(), height=0)

# ─── Screen Reader Test ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"### {t('acc_sr_test_title')}")
test_col1, test_col2 = st.columns(2)
with test_col1:
    test_message = st.text_input(
        t("acc_sr_test_label"),
        value="",
        key="sr_test_input",
    )
with test_col2:
    if st.button(f"📢 {t('acc_announce_btn')}", key="btn_announce_sr", use_container_width=True):
        if test_message.strip():
            st.markdown(
                screen_reader_hints.alert_region(
                    content=f"<strong>{test_message}</strong>",
                    label="User announcement",
                ),
                unsafe_allow_html=True,
            )
            st.success(t("acc_announced_msg", msg=test_message))

# ─── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""
    <div class="bauhaus-card" style="padding: 14px; text-align: center;">
        <p style="font-size: 0.8rem; color: #555; margin: 0;">
            {t("acc_footer_desc")}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
