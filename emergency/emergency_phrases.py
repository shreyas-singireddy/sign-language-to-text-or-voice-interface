"""
SignBridge AI — Layer 12: Emergency Phrase Bank
Comprehensive bank of emergency and medical phrases for all 16 languages.
Organized by category: Medical, Safety, Navigation, and Communication.
"""

# Emergency phrase categories
EMERGENCY_CATEGORIES = {
    "Medical": [
        "I need a doctor.",
        "Call an ambulance.",
        "I am having a heart attack.",
        "I cannot breathe.",
        "I am bleeding.",
        "I am having a seizure.",
        "I am allergic to penicillin.",
        "I am diabetic.",
        "I need insulin.",
        "I am in severe pain.",
        "I have chest pain.",
        "I feel dizzy.",
        "I have fallen and cannot get up.",
        "I need my medication.",
        "I am unconscious — please help.",
    ],
    "Safety": [
        "EMERGENCY — I need immediate help!",
        "Call the police.",
        "Call 911.",
        "There is a fire.",
        "I am in danger.",
        "Someone is following me.",
        "I am lost.",
        "I am trapped.",
        "Please do not leave me alone.",
        "I need security.",
    ],
    "Navigation": [
        "Where is the hospital?",
        "Where is the nearest pharmacy?",
        "Where is the nearest exit?",
        "I need to go home.",
        "Can you call me a taxi?",
        "I need directions to safety.",
    ],
    "Communication": [
        "I am deaf and use sign language.",
        "Please write it down.",
        "Please speak slowly.",
        "I do not understand.",
        "Please call my family.",
        "My emergency contact is:",
        "I need an interpreter.",
    ],
}

# ASL sign tokens that trigger emergency detection
SOS_TRIGGER_TOKENS = {
    "SOS",
    "EMERGENCY",
    "DANGER",
    "FIRE",
    "HELP",
    "CALL",
    "POLICE",
    "AMBULANCE",
    "DOCTOR",
    "HEART",
    "ATTACK",
    "BREATHE",
    "BLEEDING",
    "SEIZURE",
    "CHEST",
    "PAIN",
    "TRAPPED",
    "LOST",
    "UNCONSCIOUS",
    "CRITICAL",
    "DYING",
    "HURT",
    "FALLING",
    "ALARM",
}

# Translated emergency phrases for 16 languages
# Key: phrase → Dict[language → translation]
EMERGENCY_TRANSLATIONS: dict[str, dict[str, str]] = {
    "EMERGENCY — I need immediate help!": {
        "English": "EMERGENCY — I need immediate help!",
        "Hindi": "आपातकाल — मुझे तत्काल सहायता चाहिए!",
        "Telugu": "అత్యవసరం — నాకు తక్షణ సహాయం కావాలి!",
        "Spanish": "¡EMERGENCIA — Necesito ayuda inmediata!",
        "French": "URGENCE — J'ai besoin d'aide immédiatement!",
        "German": "NOTFALL — Ich brauche sofortige Hilfe!",
        "Chinese": "紧急情况——我需要立即帮助！",
        "Japanese": "緊急事態 — すぐに助けが必要です！",
        "Arabic": "طوارئ — أحتاج إلى مساعدة فورية!",
        "Portuguese": "EMERGÊNCIA — Preciso de ajuda imediata!",
        "Russian": "ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ — Мне нужна немедленная помощь!",
        "Italian": "EMERGENZA — Ho bisogno di aiuto immediato!",
        "Korean": "긴급 상황 — 즉각적인 도움이 필요합니다!",
        "Bengali": "জরুরি অবস্থা — আমার তাৎক্ষণিক সাহায্য দরকার!",
        "Tamil": "அவசரநிலை — எனக்கு உடனடி உதவி தேவை!",
        "Urdu": "ایمرجنسی — مجھے فوری مدد چاہیے!",
    },
    "Call an ambulance.": {
        "English": "Call an ambulance.",
        "Hindi": "एम्बुलेंस को बुलाओ।",
        "Telugu": "అంబులెన్స్ పిలవండి.",
        "Spanish": "Llame a una ambulancia.",
        "French": "Appelez une ambulance.",
        "German": "Rufen Sie einen Krankenwagen.",
        "Chinese": "请叫救护车。",
        "Japanese": "救急車を呼んでください。",
        "Arabic": "اتصل بسيارة الإسعاف.",
        "Portuguese": "Chame uma ambulância.",
        "Russian": "Вызовите скорую помощь.",
        "Italian": "Chiami un'ambulanza.",
        "Korean": "구급차를 불러주세요.",
        "Bengali": "অ্যাম্বুলেন্স ডাকুন।",
        "Tamil": "அம்புலன்ஸ் அழையுங்கள்.",
        "Urdu": "ایمبولینس کو بلائیں۔",
    },
    "I am in severe pain.": {
        "English": "I am in severe pain.",
        "Hindi": "मुझे बहुत तेज दर्द है।",
        "Telugu": "నాకు తీవ్రమైన నొప్పిగా ఉంది.",
        "Spanish": "Tengo un dolor severo.",
        "French": "J'ai une douleur intense.",
        "German": "Ich habe starke Schmerzen.",
        "Chinese": "我疼痛难忍。",
        "Japanese": "激しい痛みがあります。",
        "Arabic": "أشعر بألم شديد.",
        "Portuguese": "Estou com dor intensa.",
        "Russian": "У меня сильная боль.",
        "Italian": "Ho un dolore intenso.",
        "Korean": "극심한 통증이 있습니다.",
        "Bengali": "আমার প্রচণ্ড ব্যথা হচ্ছে।",
        "Tamil": "எனக்கு கடுமையான வலி உள்ளது.",
        "Urdu": "مجھے شدید درد ہے۔",
    },
    "I cannot breathe.": {
        "English": "I cannot breathe.",
        "Hindi": "मुझे सांस नहीं आ रही।",
        "Telugu": "నాకు శ్వాస తీసుకోలేకపోతున్నాను.",
        "Spanish": "No puedo respirar.",
        "French": "Je ne peux pas respirer.",
        "German": "Ich kann nicht atmen.",
        "Chinese": "我不能呼吸。",
        "Japanese": "呼吸ができません。",
        "Arabic": "لا أستطيع التنفس.",
        "Portuguese": "Não consigo respirar.",
        "Russian": "Я не могу дышать.",
        "Italian": "Non riesco a respirare.",
        "Korean": "숨을 쉴 수 없어요.",
        "Bengali": "আমি শ্বাস নিতে পারছি না।",
        "Tamil": "என்னால் மூச்சு விட முடியவில்லை.",
        "Urdu": "مجھے سانس نہیں آ رہی۔",
    },
}


def get_emergency_phrase(phrase: str, language: str) -> str:
    """
    Get a translated emergency phrase for the given language.

    Args:
        phrase: English emergency phrase
        language: Target language name

    Returns:
        Translated phrase or original English if translation not found
    """
    translations = EMERGENCY_TRANSLATIONS.get(phrase, {})
    return translations.get(language, phrase)


def get_all_phrases_for_language(language: str) -> list[str]:
    """
    Get all translated emergency phrases for a given language.

    Args:
        language: Target language name

    Returns:
        List of translated emergency phrases
    """
    return [
        translations.get(language, english_phrase)
        for english_phrase, translations in EMERGENCY_TRANSLATIONS.items()
    ]
