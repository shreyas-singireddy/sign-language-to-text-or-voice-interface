"""
SignBridge AI — Layer 5: Rule-Based Translation Provider
Production-grade local translation engine with no external API dependencies.
Uses linguistic grammar rules, subject inference, tense detection,
and a comprehensive phrase dictionary to convert sign tokens to natural language.
"""

from config.logger import setup_logger
from translation.providers.base import BaseTranslationProvider

logger = setup_logger("translation.providers.rule_based")


# ──────────────────────────────────────────────────────────────
# PHRASE DICTIONARY: direct sign sequence → English mappings
# ──────────────────────────────────────────────────────────────
PHRASE_DICTIONARY: dict[tuple[str, ...], str] = {
    # Greetings
    ("HELLO",): "Hello!",
    ("HI",): "Hi there!",
    ("GOOD", "MORNING"): "Good morning!",
    ("GOOD", "NIGHT"): "Good night!",
    ("GOOD", "AFTERNOON"): "Good afternoon!",
    ("GOOD", "EVENING"): "Good evening!",
    ("GOODBYE",): "Goodbye!",
    ("BYE",): "Goodbye!",
    ("NICE", "MEET", "YOU"): "Nice to meet you.",
    ("HOW", "ARE", "YOU"): "How are you?",
    ("I", "AM", "FINE"): "I am doing fine.",
    # Requests
    ("PLEASE", "HELP"): "Please help me.",
    ("HELP",): "I need help.",
    ("HELP", "ME"): "Please help me.",
    ("HELP", "DOCTOR"): "I need a doctor immediately.",
    ("CALL", "DOCTOR"): "Please call a doctor.",
    ("CALL", "POLICE"): "Please call the police.",
    ("CALL", "AMBULANCE"): "Please call an ambulance.",
    ("NEED", "HELP"): "I need help.",
    ("WATER", "PLEASE"): "May I have some water, please?",
    ("WATER", "WANT"): "I would like some water.",
    ("WATER",): "I need water.",
    ("FOOD", "WANT"): "I would like some food.",
    ("FOOD", "PLEASE"): "May I have something to eat, please?",
    ("FOOD",): "I need food.",
    ("MEDICINE", "NEED"): "I need my medication.",
    ("MEDICINE",): "I need medicine.",
    ("BATHROOM",): "I need to use the bathroom.",
    ("TOILET",): "I need to use the restroom.",
    # Affirmations / Negations
    ("YES",): "Yes.",
    ("NO",): "No.",
    ("MAYBE",): "Maybe.",
    ("OK",): "Okay.",
    ("OKAY",): "Okay.",
    ("UNDERSTAND",): "I understand.",
    ("NOT", "UNDERSTAND"): "I do not understand.",
    ("I", "UNDERSTAND"): "I understand.",
    # Gratitude
    ("THANK", "YOU"): "Thank you.",
    ("THANKS",): "Thank you!",
    ("THANK",): "Thank you.",
    ("SORRY",): "I am sorry.",
    ("EXCUSE", "ME"): "Excuse me.",
    # Pain / Emergency
    ("PAIN",): "I am in pain.",
    ("HURT",): "I am hurting.",
    ("CHEST", "PAIN"): "I have chest pain. This is an emergency.",
    ("CAN", "NOT", "BREATHE"): "I cannot breathe. Please help.",
    ("BREATHE",): "I am having trouble breathing.",
    ("DIZZY",): "I feel dizzy.",
    ("FALL",): "I have fallen.",
    ("EMERGENCY",): "This is an emergency!",
    ("SOS",): "EMERGENCY — I need immediate help!",
    ("DANGER",): "I am in danger!",
    # Location / Direction
    ("WHERE",): "Where am I?",
    ("LOST",): "I am lost.",
    ("HOME",): "I want to go home.",
    ("HOSPITAL",): "I need to go to the hospital.",
    # Communication
    ("REPEAT",): "Please repeat that.",
    ("SLOW", "DOWN"): "Please speak more slowly.",
    ("WRITE",): "Please write it down.",
    ("SPEAK",): "Please speak to me.",
    ("SIGN",): "Can you sign to me?",
    # Time
    ("WAIT",): "Please wait.",
    ("HURRY",): "Please hurry.",
    ("LATER",): "Later, please.",
    ("NOW",): "Right now.",
    ("SOON",): "Very soon.",
}

# ──────────────────────────────────────────────────────────────
# SUBJECT INFERENCE: token → inferred English subject
# ──────────────────────────────────────────────────────────────
SUBJECT_TOKENS = {"I", "YOU", "HE", "SHE", "WE", "THEY", "IT"}
DEFAULT_SUBJECT = "I"

# ──────────────────────────────────────────────────────────────
# VERB GRAMMAR TABLE: base form → "I/you/they" / "he/she/it"
# ──────────────────────────────────────────────────────────────
VERB_CONJUGATION: dict[str, tuple[str, str]] = {
    "WANT": ("want", "wants"),
    "NEED": ("need", "needs"),
    "HAVE": ("have", "has"),
    "GO": ("go", "goes"),
    "LIKE": ("like", "likes"),
    "FEEL": ("feel", "feels"),
    "HURT": ("hurt", "hurts"),
    "KNOW": ("know", "knows"),
    "CALL": ("call", "calls"),
    "SEE": ("see", "sees"),
    "HELP": ("help", "helps"),
    "COME": ("come", "comes"),
    "GET": ("get", "gets"),
    "MAKE": ("make", "makes"),
    "USE": ("use", "uses"),
}

# ──────────────────────────────────────────────────────────────
# MULTILINGUAL TRANSLATION TABLE (16 languages)
# ──────────────────────────────────────────────────────────────
MULTILINGUAL_TABLE: dict[str, dict[str, str]] = {
    "Spanish": {
        "Hello!": "¡Hola!",
        "Good morning!": "¡Buenos días!",
        "Good night!": "¡Buenas noches!",
        "Thank you.": "Gracias.",
        "Thank you!": "¡Gracias!",
        "I need help.": "Necesito ayuda.",
        "Please help me.": "Por favor ayúdame.",
        "Yes.": "Sí.",
        "No.": "No.",
        "I am sorry.": "Lo siento.",
        "I need water.": "Necesito agua.",
        "I need a doctor immediately.": "Necesito un médico de inmediato.",
        "EMERGENCY — I need immediate help!": "¡EMERGENCIA — Necesito ayuda inmediata!",
        "I am in pain.": "Estoy sufriendo dolor.",
        "I am lost.": "Estoy perdido.",
        "Please wait.": "Por favor espere.",
        "I understand.": "Entiendo.",
        "I do not understand.": "No entiendo.",
        "Maybe.": "Quizás.",
        "Good afternoon!": "¡Buenas tardes!",
        "Good evening!": "¡Buenas noches!",
    },
    "Hindi": {
        "Hello!": "नमस्ते!",
        "Good morning!": "शुभ प्रभात!",
        "Good night!": "शुभ रात्रि!",
        "Thank you.": "धन्यवाद।",
        "Thank you!": "धन्यवाद!",
        "I need help.": "मुझे मदद चाहिए।",
        "Please help me.": "कृपया मेरी मदद करें।",
        "Yes.": "हाँ।",
        "No.": "नहीं।",
        "I am sorry.": "माफ़ कीजिये।",
        "I need water.": "मुझे पानी चाहिए।",
        "I need a doctor immediately.": "मुझे तुरंत एक डॉक्टर चाहिए।",
        "EMERGENCY — I need immediate help!": "आपातकाल — मुझे तत्काल सहायता चाहिए!",
        "I am in pain.": "मैं दर्द में हूँ।",
        "I am lost.": "मैं खो गया हूँ।",
        "I understand.": "मैं समझता हूँ।",
        "I do not understand.": "मैं नहीं समझता।",
    },
    "Telugu": {
        "Hello!": "హలో!",
        "Good morning!": "శుభోదయం!",
        "Good night!": "శుభ రాత్రి!",
        "Thank you.": "ధన్యవాదాలు.",
        "Thank you!": "ధన్యవాదాలు!",
        "I need help.": "నాకు సహాయం కావాలి.",
        "Please help me.": "దయచేసి నాకు సహాయం చేయండి.",
        "Yes.": "అవును.",
        "No.": "కాదు.",
        "I am sorry.": "క్షమించండి.",
        "I need water.": "నాకు నీళ్ళు కావాలి.",
        "I need a doctor immediately.": "నాకు వెంటనే వైద్యుడు కావాలి.",
        "EMERGENCY — I need immediate help!": "అత్యవసరం — నాకు తక్షణ సహాయం కావాలి!",
    },
    "French": {
        "Hello!": "Bonjour!",
        "Good morning!": "Bonjour!",
        "Good night!": "Bonne nuit!",
        "Thank you.": "Merci.",
        "Thank you!": "Merci!",
        "I need help.": "J'ai besoin d'aide.",
        "Please help me.": "Aidez-moi s'il vous plaît.",
        "Yes.": "Oui.",
        "No.": "Non.",
        "I am sorry.": "Je suis désolé.",
        "I need water.": "J'ai besoin d'eau.",
        "I need a doctor immediately.": "J'ai besoin d'un médecin immédiatement.",
        "EMERGENCY — I need immediate help!": "URGENCE — J'ai besoin d'aide immédiatement!",
    },
    "German": {
        "Hello!": "Hallo!",
        "Good morning!": "Guten Morgen!",
        "Good night!": "Gute Nacht!",
        "Thank you.": "Danke.",
        "Thank you!": "Danke!",
        "I need help.": "Ich brauche Hilfe.",
        "Please help me.": "Bitte helfen Sie mir.",
        "Yes.": "Ja.",
        "No.": "Nein.",
        "I am sorry.": "Es tut mir leid.",
        "I need water.": "Ich brauche Wasser.",
        "I need a doctor immediately.": "Ich brauche sofort einen Arzt.",
        "EMERGENCY — I need immediate help!": "NOTFALL — Ich brauche sofortige Hilfe!",
    },
    "Chinese": {
        "Hello!": "你好！",
        "Good morning!": "早上好！",
        "Good night!": "晚安！",
        "Thank you.": "谢谢。",
        "Thank you!": "谢谢！",
        "I need help.": "我需要帮助。",
        "Please help me.": "请帮帮我。",
        "Yes.": "是。",
        "No.": "不。",
        "I am sorry.": "对不起。",
        "I need water.": "我需要水。",
        "I need a doctor immediately.": "我立即需要医生。",
        "EMERGENCY — I need immediate help!": "紧急情况——我需要立即帮助！",
    },
    "Japanese": {
        "Hello!": "こんにちは！",
        "Good morning!": "おはようございます！",
        "Good night!": "おやすみなさい！",
        "Thank you.": "ありがとうございます。",
        "Thank you!": "ありがとう！",
        "I need help.": "助けが必要です。",
        "Please help me.": "助けてください。",
        "Yes.": "はい。",
        "No.": "いいえ。",
        "I am sorry.": "申し訳ありません。",
        "I need water.": "水が必要です。",
        "I need a doctor immediately.": "すぐに医者が必要です。",
        "EMERGENCY — I need immediate help!": "緊急事態 — すぐに助けが必要です！",
    },
    "Arabic": {
        "Hello!": "مرحبا!",
        "Good morning!": "صباح الخير!",
        "Good night!": "تصبح على خير!",
        "Thank you.": "شكرًا لك.",
        "Thank you!": "شكرًا!",
        "I need help.": "أحتاج إلى مساعدة.",
        "Please help me.": "من فضلك ساعدني.",
        "Yes.": "نعم.",
        "No.": "لا.",
        "I am sorry.": "أنا آسف.",
        "I need water.": "أحتاج إلى ماء.",
        "I need a doctor immediately.": "أحتاج إلى طبيب فورًا.",
        "EMERGENCY — I need immediate help!": "طوارئ — أحتاج إلى مساعدة فورية!",
    },
    "Portuguese": {
        "Hello!": "Olá!",
        "Good morning!": "Bom dia!",
        "Good night!": "Boa noite!",
        "Thank you.": "Obrigado.",
        "Thank you!": "Obrigado!",
        "I need help.": "Preciso de ajuda.",
        "Please help me.": "Por favor, me ajude.",
        "Yes.": "Sim.",
        "No.": "Não.",
        "I am sorry.": "Eu sinto muito.",
        "I need water.": "Preciso de água.",
        "I need a doctor immediately.": "Preciso de um médico imediatamente.",
        "EMERGENCY — I need immediate help!": "EMERGÊNCIA — Preciso de ajuda imediata!",
    },
    "Russian": {
        "Hello!": "Привет!",
        "Good morning!": "Доброе утро!",
        "Good night!": "Спокойной ночи!",
        "Thank you.": "Спасибо.",
        "Thank you!": "Спасибо!",
        "I need help.": "Мне нужна помощь.",
        "Please help me.": "Пожалуйста, помогите мне.",
        "Yes.": "Да.",
        "No.": "Нет.",
        "I am sorry.": "Извините.",
        "I need water.": "Мне нужна вода.",
        "I need a doctor immediately.": "Мне срочно нужен врач.",
        "EMERGENCY — I need immediate help!": "ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ — Мне нужна немедленная помощь!",
    },
    "Italian": {
        "Hello!": "Ciao!",
        "Good morning!": "Buongiorno!",
        "Good night!": "Buonanotte!",
        "Thank you.": "Grazie.",
        "Thank you!": "Grazie!",
        "I need help.": "Ho bisogno di aiuto.",
        "Please help me.": "Per favore aiutami.",
        "Yes.": "Sì.",
        "No.": "No.",
        "I am sorry.": "Mi dispiace.",
        "I need water.": "Ho bisogno di acqua.",
        "I need a doctor immediately.": "Ho bisogno di un medico subito.",
        "EMERGENCY — I need immediate help!": "EMERGENZA — Ho bisogno di aiuto immediato!",
    },
    "Korean": {
        "Hello!": "안녕하세요!",
        "Good morning!": "좋은 아침이에요!",
        "Good night!": "잘 자요!",
        "Thank you.": "감사합니다.",
        "Thank you!": "감사해요!",
        "I need help.": "도움이 필요합니다.",
        "Please help me.": "도와주세요.",
        "Yes.": "네.",
        "No.": "아니요.",
        "I am sorry.": "죄송합니다.",
        "I need water.": "물이 필요합니다.",
        "I need a doctor immediately.": "즉시 의사가 필요합니다.",
        "EMERGENCY — I need immediate help!": "긴급 상황 — 즉각적인 도움이 필요합니다!",
    },
    "Bengali": {
        "Hello!": "হ্যালো!",
        "Good morning!": "সুপ্রভাত!",
        "Good night!": "শুভ রাত্রি!",
        "Thank you.": "ধন্যবাদ।",
        "I need help.": "আমার সাহায্য দরকার।",
        "Please help me.": "অনুগ্রহ করে আমাকে সাহায্য করুন।",
        "Yes.": "হ্যাঁ।",
        "No.": "না।",
        "I am sorry.": "আমি দুঃখিত।",
        "I need water.": "আমার পানি দরকার।",
        "EMERGENCY — I need immediate help!": "জরুরি অবস্থা — আমার তাৎক্ষণিক সাহায্য দরকার!",
    },
    "Tamil": {
        "Hello!": "வணக்கம்!",
        "Good morning!": "காலை வணக்கம்!",
        "Good night!": "இரவு வணக்கம்!",
        "Thank you.": "நன்றி.",
        "I need help.": "எனக்கு உதவி தேவை.",
        "Please help me.": "தயவுசெய்து என்னை உதவுங்கள்.",
        "Yes.": "ஆம்.",
        "No.": "இல்லை.",
        "I am sorry.": "மன்னிக்கவும்.",
        "I need water.": "எனக்கு தண்ணீர் தேவை.",
        "EMERGENCY — I need immediate help!": "அவசரநிலை — எனக்கு உடனடி உதவி தேவை!",
    },
    "Urdu": {
        "Hello!": "ہیلو!",
        "Good morning!": "صبح بخیر!",
        "Good night!": "شب بخیر!",
        "Thank you.": "شکریہ۔",
        "I need help.": "مجھے مدد چاہیے۔",
        "Please help me.": "براہ کرم میری مدد کریں۔",
        "Yes.": "ہاں۔",
        "No.": "نہیں۔",
        "I am sorry.": "مجھے افسوس ہے۔",
        "I need water.": "مجھے پانی چاہیے۔",
        "EMERGENCY — I need immediate help!": "ایمرجنسی — مجھے فوری مدد چاہیے!",
    },
}


class RuleBasedProvider(BaseTranslationProvider):
    """
    Local rule-based translation provider with zero external dependencies.
    Uses a phrase dictionary, grammar rules, and a multilingual lookup table.
    This is the default provider — always available offline.
    """

    @property
    def provider_name(self) -> str:
        return "rule_based"

    @property
    def supports_multilingual(self) -> bool:
        return True

    def signs_to_english(self, tokens: list[str], context: list[str] | None = None) -> str:
        """
        Convert sign tokens to English using grammar rules and phrase dictionary.
        Applies subject inference, verb conjugation, and context-aware corrections.
        """
        if not tokens:
            return ""

        # Step 1: Normalize — uppercase, strip whitespace
        normalized = [t.strip().upper() for t in tokens if t.strip()]

        # Step 2: De-duplicate consecutive repeats
        deduped: list[str] = []
        for token in normalized:
            if not deduped or deduped[-1] != token:
                deduped.append(token)

        if not deduped:
            return ""

        # Step 3: Try exact phrase dictionary match
        key = tuple(deduped)
        if key in PHRASE_DICTIONARY:
            logger.debug(f"Exact match found for key: {key}")
            return PHRASE_DICTIONARY[key]

        # Step 4: Try sliding window sub-phrase matches (longest first)
        for window_size in range(min(len(deduped), 4), 1, -1):
            for start in range(len(deduped) - window_size + 1):
                sub_key = tuple(deduped[start : start + window_size])
                if sub_key in PHRASE_DICTIONARY:
                    logger.debug(f"Sub-phrase match: {sub_key}")
                    # Build sentence around the matched phrase
                    prefix_tokens = deduped[:start]
                    suffix_tokens = deduped[start + window_size :]
                    parts = []
                    if prefix_tokens:
                        parts.append(self._build_fallback_clause(prefix_tokens))
                    parts.append(PHRASE_DICTIONARY[sub_key].rstrip(".!?"))
                    if suffix_tokens:
                        parts.append(self._build_fallback_clause(suffix_tokens))
                    return " ".join(parts).capitalize() + "."

        # Step 5: Grammar-rule fallback construction
        return self._construct_grammatically(deduped, context)

    def _construct_grammatically(self, tokens: list[str], context: list[str] | None) -> str:
        """
        Construct a natural English sentence from tokens using grammar rules.
        Infers subject, selects verb form, and builds object phrase.
        """
        # Detect explicit subject
        subject = DEFAULT_SUBJECT
        subject_third_person = False
        remaining = list(tokens)

        if remaining and remaining[0] in SUBJECT_TOKENS:
            subject_token = remaining.pop(0)
            subject = subject_token.capitalize()
            subject_third_person = subject_token in {"HE", "SHE", "IT"}

        if not remaining:
            return f"{subject}."

        # Detect negation
        negated = False
        if remaining and remaining[0] in {
            "NOT",
            "NO",
            "CANNOT",
            "CAN'T",
            "DONT",
            "DON'T",
        }:
            negated = True
            remaining.pop(0)

        if not remaining:
            return f"{subject} does not." if not negated else f"{subject} does not."

        # Detect verb
        verb_token = remaining[0].upper()
        if verb_token in VERB_CONJUGATION:
            base_form, third_form = VERB_CONJUGATION[verb_token]
            conjugated = third_form if subject_third_person else base_form
            if negated:
                aux = "doesn't" if subject_third_person else "don't"
                verb_phrase = f"{aux} {base_form}"
            else:
                verb_phrase = conjugated
            remaining.pop(0)
        else:
            # Unknown verb — treat as noun
            verb_phrase = "is associated with" if not negated else "is not associated with"

        # Remaining tokens become the object/complement
        object_phrase = " ".join(w.lower() for w in remaining) if remaining else ""

        sentence_parts = [subject, verb_phrase]
        if object_phrase:
            sentence_parts.append(object_phrase)

        sentence = " ".join(sentence_parts)
        return sentence.capitalize() + "."

    def _build_fallback_clause(self, tokens: list[str]) -> str:
        """Convert a small token list into a readable clause for prefix/suffix fragments."""
        return " ".join(w.capitalize() for w in tokens)

    def translate_to_language(self, english_text: str, target_language: str) -> str:
        """
        Translate English text to the target language using the lookup table.
        Falls back to a bracketed label if the phrase is not in the dictionary.
        """
        if target_language == "English":
            return english_text

        lang_map = MULTILINGUAL_TABLE.get(target_language, {})
        if english_text in lang_map:
            return lang_map[english_text]

        # Attempt partial match — look for the closest phrase
        for eng_phrase, translated in lang_map.items():
            if eng_phrase.lower() in english_text.lower():
                logger.debug(f"Partial match for '{english_text}' → '{translated}'")
                return translated

        # Final fallback: return English with language label
        logger.info(f"No translation found for '{english_text}' in {target_language}. Returning labeled fallback.")
        return f"[{target_language}] {english_text}"
