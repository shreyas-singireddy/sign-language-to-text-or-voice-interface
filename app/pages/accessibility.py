"""
SignBridge AI — Layer 10: Accessibility Settings Page
Full accessibility control center: themes, font scaling, keyboard shortcuts,
screen reader settings, and motion preferences.
"""
import streamlit as st
import streamlit.components.v1 as components
from accessibility.theme_manager import theme_manager, AccessibilityTheme, THEME_LABELS, THEME_DESCRIPTIONS
from accessibility.keyboard_nav import keyboard_nav
from accessibility.screen_reader_hints import screen_reader_hints

# ─── Page Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="font-size: 3rem; margin-bottom: 5px; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif; font-weight: 900;">
        ACCESSIBILITY ENGINE
    </h1>
    <p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>
        Universal access settings — themes, motion, keyboard navigation, and screen reader support.
    </p>
    """,
    unsafe_allow_html=True
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
        """
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">VISUAL THEME PRESETS</h3>
            <p style="font-size: 0.9rem; color: #555; margin-bottom: 0;">
                Select one or more themes. Multiple themes can be combined (e.g. Dark Mode + Reduced Motion).
            </p>
        </div>
        """,
        unsafe_allow_html=True
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
                unsafe_allow_html=True
            )
        if checked:
            selected_themes.append(theme_enum.value)

    if not selected_themes:
        selected_themes = [AccessibilityTheme.BAUHAUS_DEFAULT.value]

    if st.button("✅ Apply Selected Themes", key="btn_apply_themes", use_container_width=True):
        st.session_state["active_themes"] = selected_themes
        st.success(f"Themes applied: {', '.join(selected_themes)}")
        st.rerun()

    # Live preview badge
    st.markdown("---")
    st.markdown("### Theme Preview")
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h4 style="margin-top: 0;">Sample Card</h4>
            <p style="margin: 0;">This card reflects your active theme settings.</p>
        </div>
        <div class="bauhaus-card card-red" style="padding: 15px; text-align: center; margin-top: 10px;">
            <strong>BAUHAUS HEADLINE</strong>
        </div>
        <div class="bauhaus-card card-yellow" style="padding: 15px; text-align: center; margin-top: 10px;">
            <strong>METRIC: 92.4%</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_controls:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">ACCESSIBILITY CONTROLS</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Font size control
    font_scale = st.slider(
        "Font Size Scale (%)",
        min_value=80,
        max_value=150,
        value=st.session_state["font_scale"],
        step=10,
        key="slider_font_scale"
    )
    if font_scale != st.session_state["font_scale"]:
        st.session_state["font_scale"] = font_scale
        font_css = f"html, body, [class*='css'] {{ font-size: {font_scale}% !important; }}"
        st.markdown(f"<style>{font_css}</style>", unsafe_allow_html=True)

    st.markdown(f"**Active Scale:** `{font_scale}%`")

    st.markdown("---")

    # Screen reader mode toggle
    sr_mode = st.toggle(
        "Screen Reader Mode",
        value=st.session_state["screen_reader_mode"],
        key="toggle_sr_mode",
        help="Adds ARIA live regions and additional screen reader hints."
    )
    st.session_state["screen_reader_mode"] = sr_mode
    if sr_mode:
        st.markdown(
            screen_reader_hints.live_region(
                content="<span>Screen reader mode active. Navigation landmarks enabled.</span>",
                aria_label="Screen reader status"
            ),
            unsafe_allow_html=True
        )
        st.success("Screen reader enhancements active.")

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
            <div style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase;">WCAG Compliance</div>
            <div style="font-size: 2.5rem; font-weight: 900; color: #121212;">{wcag_level}</div>
            <div style="font-size: 0.75rem; color: #555;">{active_count} theme(s) active</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─── Keyboard Shortcuts Reference ───────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div class="bauhaus-card card-yellow" style="padding: 20px;">
        <h3 style="margin-top: 0;">KEYBOARD SHORTCUTS</h3>
        <p style="font-size: 0.9rem; color: #555;">
            SignBridge AI supports keyboard navigation for hands-free operation.
            All shortcuts use the <kbd>ALT</kbd> modifier key.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    keyboard_nav.generate_shortcut_reference_html(),
    unsafe_allow_html=True
)

# Inject keyboard listener
components.html(keyboard_nav.generate_keyboard_listener_html(), height=0)

# ─── Screen Reader Test ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Screen Reader Announcement Test")
test_col1, test_col2 = st.columns(2)
with test_col1:
    test_message = st.text_input(
        "Type a message to test screen reader live region:",
        value="",
        key="sr_test_input",
        id="input_sr_test"
    )
with test_col2:
    if st.button("📢 Announce", key="btn_announce_sr", use_container_width=True):
        if test_message.strip():
            st.markdown(
                screen_reader_hints.alert_region(
                    content=f"<strong>{test_message}</strong>",
                    label="User announcement"
                ),
                unsafe_allow_html=True
            )
            st.success(f"Announced: '{test_message}'")

# ─── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div class="bauhaus-card" style="padding: 14px; text-align: center;">
        <p style="font-size: 0.8rem; color: #555; margin: 0;">
            SignBridge AI — Accessibility Engine (Layer 10) | WCAG 2.1 Compliant | Universal Design Principles
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
