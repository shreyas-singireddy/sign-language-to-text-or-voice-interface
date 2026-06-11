"""
SignBridge AI — Layer 10: Theme Manager
Manages UI accessibility themes including high-contrast mode,
large-text mode, colorblind-friendly mode, and dark mode.
Injects CSS overrides into Streamlit via st.markdown.
"""
from typing import Dict
from enum import Enum
from config.logger import setup_logger

logger = setup_logger("accessibility.theme_manager")


class AccessibilityTheme(str, Enum):
    """Available accessibility theme presets."""
    BAUHAUS_DEFAULT = "bauhaus_default"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    COLORBLIND_SAFE = "colorblind_safe"
    DARK_MODE = "dark_mode"
    REDUCED_MOTION = "reduced_motion"


# CSS overrides for each theme
THEME_CSS: Dict[AccessibilityTheme, str] = {
    AccessibilityTheme.BAUHAUS_DEFAULT: "",  # Default — no override needed

    AccessibilityTheme.HIGH_CONTRAST: """
        html, body, .stApp {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }
        .bauhaus-card {
            background-color: #000000 !important;
            border: 4px solid #FFFFFF !important;
            box-shadow: 8px 8px 0px #FFFFFF !important;
            color: #FFFFFF !important;
        }
        .bauhaus-card * { color: #FFFFFF !important; }
        .stButton > button {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 3px solid #FFFFFF !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 4px solid #FFFFFF !important;
        }
        .card-red { border-top: 15px solid #FF6060 !important; }
        .card-blue { border-top: 15px solid #6699FF !important; }
        .card-yellow { border-top: 15px solid #FFFF00 !important; }
    """,

    AccessibilityTheme.LARGE_TEXT: """
        html, body, .stApp { font-size: 120% !important; }
        h1 { font-size: 3rem !important; }
        h2 { font-size: 2.5rem !important; }
        h3 { font-size: 2rem !important; }
        p, div, span, label { font-size: 1.15rem !important; line-height: 1.8 !important; }
        .stButton > button { font-size: 1.3rem !important; padding: 16px 28px !important; }
        .stSelectbox, .stTextInput { font-size: 1.15rem !important; }
    """,

    AccessibilityTheme.COLORBLIND_SAFE: """
        .card-red { border-top: 15px solid #0072B2 !important; }
        .card-blue { border-top: 15px solid #E69F00 !important; }
        .card-yellow { border-top: 15px solid #009E73 !important; }
        .stButton > button { background-color: #0072B2 !important; color: #FFFFFF !important; }
        .stButton > button:hover { background-color: #E69F00 !important; color: #000000 !important; }
        .num-red { background-color: #0072B2 !important; }
        .num-blue { background-color: #E69F00 !important; }
        .num-yellow { background-color: #009E73 !important; }
    """,

    AccessibilityTheme.DARK_MODE: """
        html, body, .stApp {
            background-color: #0D0D0D !important;
            color: #E8E8E8 !important;
        }
        .bauhaus-card {
            background-color: #1A1A1A !important;
            border-color: #444444 !important;
            box-shadow: 8px 8px 0px #333333 !important;
        }
        .bauhaus-card * { color: #E8E8E8 !important; }
        .stButton > button {
            background-color: #2A2A2A !important;
            color: #E8E8E8 !important;
            border-color: #555555 !important;
        }
        .stButton > button:hover { background-color: #D02020 !important; color: #FFFFFF !important; }
        section[data-testid="stSidebar"] { background-color: #050505 !important; }
        input, select, textarea { background-color: #1A1A1A !important; color: #E8E8E8 !important; }
    """,

    AccessibilityTheme.REDUCED_MOTION: """
        *, *::before, *::after {
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
        }
        .circle-shape, .square-shape, .line-shape { animation: none !important; }
        .bauhaus-card:hover { transform: none !important; box-shadow: 8px 8px 0px #121212 !important; }
    """,
}

THEME_LABELS: Dict[AccessibilityTheme, str] = {
    AccessibilityTheme.BAUHAUS_DEFAULT: "Default (Bauhaus)",
    AccessibilityTheme.HIGH_CONTRAST: "High Contrast (WCAG AAA)",
    AccessibilityTheme.LARGE_TEXT: "Large Text (120% Scale)",
    AccessibilityTheme.COLORBLIND_SAFE: "Colorblind Safe (Deuteranopia)",
    AccessibilityTheme.DARK_MODE: "Dark Mode",
    AccessibilityTheme.REDUCED_MOTION: "Reduced Motion",
}

THEME_DESCRIPTIONS: Dict[AccessibilityTheme, str] = {
    AccessibilityTheme.BAUHAUS_DEFAULT: "Standard Bauhaus design system with primary color palette.",
    AccessibilityTheme.HIGH_CONTRAST: "Maximum contrast black/white theme for low vision users.",
    AccessibilityTheme.LARGE_TEXT: "120% larger text for improved readability.",
    AccessibilityTheme.COLORBLIND_SAFE: "Deuteranopia-safe palette using blue/orange/green instead of red/green.",
    AccessibilityTheme.DARK_MODE: "Dark background theme to reduce eye strain in low light.",
    AccessibilityTheme.REDUCED_MOTION: "Disables all animations for users with vestibular disorders.",
}


class ThemeManager:
    """
    Manages accessibility theme selection and CSS injection for Streamlit.
    """

    def __init__(self):
        self._active_theme = AccessibilityTheme.BAUHAUS_DEFAULT
        self._active_themes: set = {AccessibilityTheme.BAUHAUS_DEFAULT}
        logger.info("ThemeManager initialized.")

    def get_all_themes(self) -> Dict[str, str]:
        """Return all available themes as {value: label} dict for selectbox."""
        return {theme.value: label for theme, label in THEME_LABELS.items()}

    def get_theme_description(self, theme_value: str) -> str:
        """Get the description of a theme by its value string."""
        try:
            theme = AccessibilityTheme(theme_value)
            return THEME_DESCRIPTIONS.get(theme, "")
        except ValueError:
            return ""

    def apply_theme(self, theme_value: str) -> str:
        """
        Get the CSS for a given theme value.

        Args:
            theme_value: Theme enum value string

        Returns:
            CSS string to inject via st.markdown()
        """
        try:
            theme = AccessibilityTheme(theme_value)
        except ValueError:
            theme = AccessibilityTheme.BAUHAUS_DEFAULT

        css = THEME_CSS.get(theme, "")
        self._active_theme = theme
        logger.info(f"Theme applied: {theme.value}")
        return css

    def get_combined_css(self, active_themes: list) -> str:
        """
        Combine CSS from multiple active themes.
        Useful when Reduced Motion + Large Text are both enabled.

        Args:
            active_themes: List of theme value strings

        Returns:
            Combined CSS string
        """
        combined = ""
        for theme_value in active_themes:
            combined += self.apply_theme(theme_value)
        return combined

    def inject_css(self, css: str) -> str:
        """
        Wrap CSS in a Streamlit-injectable style tag.

        Args:
            css: Raw CSS string

        Returns:
            HTML string with <style> tag for st.markdown(unsafe_allow_html=True)
        """
        if not css.strip():
            return ""
        return f"<style>{css}</style>"


theme_manager = ThemeManager()
