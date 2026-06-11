"""
SignBridge AI — Layer 10: Keyboard Navigation Registry
Defines keyboard shortcut mappings for accessibility.
Injects JavaScript keyboard listeners into Streamlit via HTML components.
"""
from typing import Dict, List
from config.logger import setup_logger

logger = setup_logger("accessibility.keyboard_nav")


class KeyboardShortcut:
    """Represents a single keyboard shortcut binding."""

    def __init__(self, key: str, modifier: str, action: str, description: str):
        self.key = key
        self.modifier = modifier  # "ctrl", "alt", "shift", or ""
        self.action = action
        self.description = description

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "modifier": self.modifier,
            "action": self.action,
            "description": self.description,
            "label": f"{self.modifier.upper()+'+' if self.modifier else ''}{self.key.upper()}",
        }


# Registry of all keyboard shortcuts
SHORTCUTS: List[KeyboardShortcut] = [
    KeyboardShortcut("s", "alt", "start_camera",     "Start/Stop camera"),
    KeyboardShortcut("r", "alt", "reset_buffer",     "Reset translation buffer"),
    KeyboardShortcut("t", "alt", "play_tts",         "Play voice synthesis"),
    KeyboardShortcut("h", "alt", "go_home",          "Navigate to Home"),
    KeyboardShortcut("v", "alt", "go_vision",        "Navigate to Vision Engine"),
    KeyboardShortcut("g", "alt", "go_gesture",       "Navigate to Gesture Recognition"),
    KeyboardShortcut("l", "alt", "go_translation",   "Navigate to Live Translation"),
    KeyboardShortcut("c", "alt", "go_chat",          "Navigate to Communication Hub"),
    KeyboardShortcut("e", "alt", "go_emergency",     "Navigate to Emergency System"),
    KeyboardShortcut("Escape", "", "close_modal",    "Close modal / cancel action"),
    KeyboardShortcut("+", "ctrl", "increase_font",   "Increase font size"),
    KeyboardShortcut("-", "ctrl", "decrease_font",   "Decrease font size"),
]


class KeyboardNavRegistry:
    """
    Registry and JavaScript generator for keyboard navigation shortcuts.
    Provides accessibility keyboard bindings for all major SignBridge actions.
    """

    def get_all_shortcuts(self) -> List[dict]:
        """Return all shortcuts as serializable dicts."""
        return [s.to_dict() for s in SHORTCUTS]

    def get_shortcuts_by_modifier(self, modifier: str) -> List[dict]:
        """Return shortcuts filtered by modifier key."""
        return [s.to_dict() for s in SHORTCUTS if s.modifier == modifier]

    def generate_keyboard_listener_html(self) -> str:
        """
        Generate JavaScript keyboard listener HTML for injection into Streamlit.
        Displays a floating shortcut guide and intercepts keyboard events.

        Returns:
            HTML string with keyboard listener script
        """
        shortcuts_js = []
        for shortcut in SHORTCUTS:
            key = shortcut.key.lower()
            mod = shortcut.modifier.lower()
            action = shortcut.action

            if mod == "alt":
                condition = f"e.altKey && e.key.toLowerCase() === '{key}'"
            elif mod == "ctrl":
                condition = f"e.ctrlKey && e.key === '{key}'"
            elif mod == "shift":
                condition = f"e.shiftKey && e.key.toLowerCase() === '{key}'"
            else:
                condition = f"!e.altKey && !e.ctrlKey && e.key === '{key}'"

            shortcuts_js.append(
                f"if ({condition}) {{ handleAction('{action}'); e.preventDefault(); }}"
            )

        shortcuts_block = "\n".join(f"            {s}" for s in shortcuts_js)

        return f"""
        <script>
        function handleAction(action) {{
            // Log shortcut to console (Streamlit doesn't support direct Python callbacks from JS)
            console.log('[SignBridge KB] Action:', action);

            // Visual feedback
            var indicator = document.getElementById('kb-action-indicator');
            if (indicator) {{
                indicator.innerText = 'Shortcut: ' + action.replace(/_/g, ' ').toUpperCase();
                indicator.style.opacity = '1';
                setTimeout(function() {{ indicator.style.opacity = '0'; }}, 1500);
            }}
        }}

        document.addEventListener('keydown', function(e) {{
            {shortcuts_block}
        }});
        </script>
        <div id="kb-action-indicator" style="
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: #121212;
            color: #F0C020;
            font-family: 'Space Grotesk', monospace;
            font-weight: 800;
            font-size: 0.85rem;
            padding: 8px 14px;
            border: 2px solid #F0C020;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 9999;
            pointer-events: none;
        ">SHORTCUT</div>
        """

    def generate_shortcut_reference_html(self) -> str:
        """
        Generate HTML table of all keyboard shortcuts for display on Accessibility page.

        Returns:
            HTML table string
        """
        rows = ""
        for shortcut in SHORTCUTS:
            label = f"{shortcut.modifier.upper()+' + ' if shortcut.modifier else ''}{shortcut.key.upper()}"
            rows += f"""
            <tr>
                <td style="padding: 8px 12px; border-bottom: 1px solid #E0E0E0;">
                    <code style="background: #F0F0F0; padding: 3px 8px; border: 1px solid #121212; font-weight: 700;">{label}</code>
                </td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #E0E0E0; font-size: 0.9rem;">{shortcut.description}</td>
            </tr>
            """

        return f"""
        <table style="width: 100%; border-collapse: collapse; font-family: 'Outfit', sans-serif;">
            <thead>
                <tr style="background: #121212; color: #FFFFFF;">
                    <th style="padding: 10px 12px; text-align: left;">Shortcut</th>
                    <th style="padding: 10px 12px; text-align: left;">Action</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """


keyboard_nav = KeyboardNavRegistry()
