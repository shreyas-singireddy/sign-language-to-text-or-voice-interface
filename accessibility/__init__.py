"""
SignBridge AI — Layer 10: Accessibility Engine Package
Provides theme management, keyboard navigation registry,
and screen reader hint injection for universal accessibility.
"""

from accessibility.keyboard_nav import KeyboardNavRegistry, keyboard_nav
from accessibility.theme_manager import ThemeManager, theme_manager

__all__ = ["ThemeManager", "theme_manager", "KeyboardNavRegistry", "keyboard_nav"]
