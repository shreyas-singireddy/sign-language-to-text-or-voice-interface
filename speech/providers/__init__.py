"""
SignBridge AI — Layer 6: Speech Providers Package
"""
from speech.providers.gtts_provider import GTTSProvider
from speech.providers.browser_provider import BrowserTTSProvider

__all__ = ["GTTSProvider", "BrowserTTSProvider"]
