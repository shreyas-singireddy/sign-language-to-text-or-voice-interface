"""
SignBridge AI — Layer 6: Voice Profiles
Pre-defined voice profiles for accessibility scenarios.
Each profile specifies the language, speech rate, and TTS provider.
"""
from typing import Dict
from speech.schemas import VoiceProfile


# All built-in voice profiles accessible by name
VOICE_PROFILES: Dict[str, VoiceProfile] = {
    "standard_english": VoiceProfile(
        name="Standard English",
        lang_code="en-US",
        slow=False,
        tld="com",
    ),
    "slow_english": VoiceProfile(
        name="Slow English (Accessibility)",
        lang_code="en-US",
        slow=True,
        tld="com",
    ),
    "british_english": VoiceProfile(
        name="British English",
        lang_code="en-GB",
        slow=False,
        tld="co.uk",
    ),
    "hindi": VoiceProfile(
        name="Hindi",
        lang_code="hi-IN",
        slow=False,
        tld="co.in",
    ),
    "telugu": VoiceProfile(
        name="Telugu",
        lang_code="te-IN",
        slow=False,
        tld="co.in",
    ),
    "spanish": VoiceProfile(
        name="Spanish",
        lang_code="es-ES",
        slow=False,
        tld="es",
    ),
    "french": VoiceProfile(
        name="French",
        lang_code="fr-FR",
        slow=False,
        tld="fr",
    ),
    "german": VoiceProfile(
        name="German",
        lang_code="de-DE",
        slow=False,
        tld="de",
    ),
    "chinese": VoiceProfile(
        name="Chinese Mandarin",
        lang_code="zh-CN",
        slow=False,
        tld="com",
    ),
    "japanese": VoiceProfile(
        name="Japanese",
        lang_code="ja-JP",
        slow=False,
        tld="com",
    ),
    "arabic": VoiceProfile(
        name="Arabic",
        lang_code="ar-SA",
        slow=False,
        tld="com",
    ),
    "portuguese": VoiceProfile(
        name="Portuguese (Brazil)",
        lang_code="pt-PT",
        slow=False,
        tld="com.br",
    ),
    "russian": VoiceProfile(
        name="Russian",
        lang_code="ru-RU",
        slow=False,
        tld="com",
    ),
    "italian": VoiceProfile(
        name="Italian",
        lang_code="it-IT",
        slow=False,
        tld="it",
    ),
    "korean": VoiceProfile(
        name="Korean",
        lang_code="ko-KR",
        slow=False,
        tld="com",
    ),
    "bengali": VoiceProfile(
        name="Bengali",
        lang_code="bn-IN",
        slow=False,
        tld="com",
    ),
    "tamil": VoiceProfile(
        name="Tamil",
        lang_code="ta-IN",
        slow=False,
        tld="co.in",
    ),
    "urdu": VoiceProfile(
        name="Urdu",
        lang_code="ur-PK",
        slow=False,
        tld="com",
    ),
    "emergency": VoiceProfile(
        name="Emergency (Loud & Clear)",
        lang_code="en-US",
        slow=False,
        tld="com",
    ),
}

# Map from Streamlit language name → voice profile key
LANGUAGE_TO_PROFILE: Dict[str, str] = {
    "English":    "standard_english",
    "Hindi":      "hindi",
    "Telugu":     "telugu",
    "Spanish":    "spanish",
    "French":     "french",
    "German":     "german",
    "Chinese":    "chinese",
    "Japanese":   "japanese",
    "Arabic":     "arabic",
    "Portuguese": "portuguese",
    "Russian":    "russian",
    "Italian":    "italian",
    "Korean":     "korean",
    "Bengali":    "bengali",
    "Tamil":      "tamil",
    "Urdu":       "urdu",
}


def get_profile_for_language(language_name: str, slow: bool = False) -> VoiceProfile:
    """
    Retrieve the appropriate voice profile for a given language name.

    Args:
        language_name: Display language name (e.g. 'Hindi')
        slow: Whether to override with slow speech rate

    Returns:
        VoiceProfile for TTS synthesis
    """
    profile_key = LANGUAGE_TO_PROFILE.get(language_name, "standard_english")
    profile = VOICE_PROFILES[profile_key]
    if slow:
        profile = VoiceProfile(
            name=f"{profile.name} (Slow)",
            lang_code=profile.lang_code,
            slow=True,
            tld=profile.tld,
        )
    return profile
