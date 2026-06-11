"""
SignBridge AI — Layer 10: Screen Reader Hints
Generates ARIA-compliant HTML hints for screen reader accessibility.
Provides helper functions for wrapping UI elements with appropriate
ARIA attributes, live regions, and role descriptors.
"""

from config.logger import setup_logger

logger = setup_logger("accessibility.screen_reader_hints")


class ScreenReaderHints:
    """
    Generates ARIA-enhanced HTML for screen reader compatibility.
    All major SignBridge UI regions should use these helpers to ensure
    WCAG 2.1 AA compliance.
    """

    def live_region(
        self,
        content: str,
        aria_label: str = "Live translation output",
        politeness: str = "polite",
    ) -> str:
        """
        Wrap content in an ARIA live region for dynamic content announcements.

        Args:
            content: HTML content to wrap
            aria_label: Accessible label for the region
            politeness: 'polite' (default) or 'assertive' for urgency

        Returns:
            HTML with aria-live attribute
        """
        return f"""
        <div
            aria-live="{politeness}"
            aria-atomic="true"
            aria-label="{aria_label}"
            role="status"
        >
            {content}
        </div>
        """

    def alert_region(self, content: str, label: str = "Alert") -> str:
        """
        Wrap content in an ARIA alert region (immediately announced).

        Args:
            content: Alert content
            label: Accessible label

        Returns:
            HTML with role="alert"
        """
        return (
            f'<div role="alert" aria-label="{label}" aria-atomic="true">{content}</div>'
        )

    def status_badge(self, status_text: str, status_type: str = "info") -> str:
        """
        Generate an accessible status badge with ARIA role.

        Args:
            status_text: Status text to display
            status_type: 'info', 'success', 'warning', 'error'

        Returns:
            Accessible status badge HTML
        """
        colors = {
            "info": "#1040C0",
            "success": "#208040",
            "warning": "#F0C020",
            "error": "#D02020",
        }
        color = colors.get(status_type, "#121212")
        return f"""
        <span
            role="status"
            aria-label="{status_text}"
            style="
                display: inline-block;
                background: {color};
                color: #FFFFFF;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                padding: 3px 10px;
                border: 2px solid #121212;
                letter-spacing: 0.08em;
            "
        >{status_text}</span>
        """

    def skip_to_content_link(self) -> str:
        """
        Generate a skip-to-main-content link for keyboard users.
        Must be the first element in the page.

        Returns:
            Skip link HTML (visible on focus)
        """
        return """
        <a
            href="#main-content"
            style="
                position: absolute;
                left: -9999px;
                top: 0;
                background: #F0C020;
                color: #121212;
                font-weight: 800;
                padding: 12px 20px;
                border: 3px solid #121212;
                z-index: 99999;
            "
            onfocus="this.style.left='10px';"
            onblur="this.style.left='-9999px';"
        >
            Skip to Main Content
        </a>
        """

    def landmark_region(self, content: str, role: str, label: str) -> str:
        """
        Wrap content in an ARIA landmark region.

        Args:
            content: HTML content
            role: ARIA landmark role (main, navigation, complementary, etc.)
            label: Accessible label for the region

        Returns:
            HTML with ARIA landmark
        """
        return (
            f'<div role="{role}" aria-label="{label}" id="main-content">{content}</div>'
        )

    def image_description(self, alt_text: str, role: str = "img") -> str:
        """
        Generate an accessible image description placeholder for webcam feed.

        Args:
            alt_text: Description of the image content
            role: ARIA role

        Returns:
            HTML span with screen-reader-only description
        """
        return f"""
        <span
            role="{role}"
            aria-label="{alt_text}"
            style="position: absolute; left: -9999px; top: auto; width: 1px; height: 1px; overflow: hidden;"
        >{alt_text}</span>
        """


screen_reader_hints = ScreenReaderHints()
