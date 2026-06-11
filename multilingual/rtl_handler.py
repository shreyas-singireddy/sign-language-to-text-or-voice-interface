"""
SignBridge AI — Layer 11: RTL Handler
Manages Right-to-Left text rendering for Arabic and Urdu.
Injects CSS and HTML attributes to correctly display RTL content
within Streamlit's LTR-default layout.
"""

from config.logger import setup_logger

logger = setup_logger("multilingual.rtl_handler")

RTL_LANGUAGES = {"Arabic", "Urdu"}

RTL_CSS = """
    .rtl-text {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: embed;
        font-size: 1.2rem;
        line-height: 1.8;
    }
    .rtl-container {
        direction: rtl !important;
        text-align: right !important;
    }
    .rtl-container * {
        text-align: right !important;
    }
"""


class RTLHandler:
    """
    Handles RTL layout for Arabic and Urdu text in Streamlit.
    Wraps translated text in appropriate HTML for correct rendering.
    """

    def is_rtl_language(self, language_name: str) -> bool:
        """Check if a language requires RTL layout."""
        return language_name in RTL_LANGUAGES

    def wrap_rtl_text(self, text: str, language_name: str) -> str:
        """
        Wrap text in RTL HTML div if the language is RTL.
        Returns plain text unchanged for LTR languages.

        Args:
            text: Text to potentially wrap
            language_name: Language of the text

        Returns:
            HTML string with RTL attributes if needed, or plain text
        """
        if not self.is_rtl_language(language_name):
            return text

        return f'<div class="rtl-text" lang="{language_name.lower()}">{text}</div>'

    def get_rtl_css(self) -> str:
        """Return CSS needed for RTL text rendering."""
        return RTL_CSS

    def get_html_dir_attribute(self, language_name: str) -> str:
        """
        Get the HTML dir attribute value for a language.

        Args:
            language_name: Language name

        Returns:
            'rtl' or 'ltr'
        """
        return "rtl" if self.is_rtl_language(language_name) else "ltr"

    def apply_to_bauhaus_card(self, content: str, language_name: str) -> str:
        """
        Wrap content in a Bauhaus card with correct text direction.

        Args:
            content: HTML content (translated text)
            language_name: Language for direction detection

        Returns:
            Complete Bauhaus card HTML with direction set
        """
        direction = self.get_html_dir_attribute(language_name)
        text_align = "right" if self.is_rtl_language(language_name) else "left"

        return f"""
        <div class="bauhaus-card card-yellow" style="
            direction: {direction};
            text-align: {text_align};
            min-height: 80px;
            padding: 20px;
        ">
            <p style="font-size: 1.35rem; font-weight: 800; margin: 0;">
                {content}
            </p>
        </div>
        """


rtl_handler = RTLHandler()
