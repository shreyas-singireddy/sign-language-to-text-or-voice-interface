import base64
import numpy as np
from app.utils.mediapipe_model import SignLanguageModel
from app.utils.image_decoder import image_from_base64

model = SignLanguageModel()

TRANSLATION_MAP = {
    'English': {
        'HELLO': 'Hello',
        'THANKS': 'Thanks',
        'YES': 'Yes',
        'NO': 'No',
        'PLEASE': 'Please',
        'SORRY': 'Sorry',
        'HELP': 'Help',
        'GOOD MORNING': 'Good morning',
        'GOOD NIGHT': 'Good night'
    },
    'Hindi': {
        'HELLO': 'नमस्ते',
        'THANKS': 'धन्यवाद',
        'YES': 'हाँ',
        'NO': 'नहीं',
        'PLEASE': 'कृपया',
        'SORRY': 'मुझे खेद है',
        'HELP': 'मदद',
        'GOOD MORNING': 'सुप्रभात',
        'GOOD NIGHT': 'शुभ रात्रि'
    },
    'Telugu': {
        'HELLO': 'హలో',
        'THANKS': 'ధన్యవాదాలు',
        'YES': 'అవును',
        'NO': 'కాదు',
        'PLEASE': 'దయచేసి',
        'SORRY': 'క్షమించండి',
        'HELP': 'సహాయం',
        'GOOD MORNING': 'శుభోదయం',
        'GOOD NIGHT': 'శుభ రాత్రి'
    },
    'Spanish': {
        'HELLO': 'Hola',
        'THANKS': 'Gracias',
        'YES': 'Sí',
        'NO': 'No',
        'PLEASE': 'Por favor',
        'SORRY': 'Lo siento',
        'HELP': 'Ayuda',
        'GOOD MORNING': 'Buenos días',
        'GOOD NIGHT': 'Buenas noches'
    },
    'French': {
        'HELLO': 'Bonjour',
        'THANKS': 'Merci',
        'YES': 'Oui',
        'NO': 'Non',
        'PLEASE': 'S’il vous plaît',
        'SORRY': 'Désolé',
        'HELP': 'Aidez-moi',
        'GOOD MORNING': 'Bonjour',
        'GOOD NIGHT': 'Bonne nuit'
    },
    'German': {
        'HELLO': 'Hallo',
        'THANKS': 'Danke',
        'YES': 'Ja',
        'NO': 'Nein',
        'PLEASE': 'Bitte',
        'SORRY': 'Entschuldigung',
        'HELP': 'Hilfe',
        'GOOD MORNING': 'Guten Morgen',
        'GOOD NIGHT': 'Gute Nacht'
    },
    'Chinese': {
        'HELLO': '你好',
        'THANKS': '谢谢',
        'YES': '是',
        'NO': '不',
        'PLEASE': '请',
        'SORRY': '对不起',
        'HELP': '帮助',
        'GOOD MORNING': '早上好',
        'GOOD NIGHT': '晚安'
    },
    'Japanese': {
        'HELLO': 'こんにちは',
        'THANKS': 'ありがとう',
        'YES': 'はい',
        'NO': 'いいえ',
        'PLEASE': 'お願いします',
        'SORRY': 'ごめんなさい',
        'HELP': '助けて',
        'GOOD MORNING': 'おはようございます',
        'GOOD NIGHT': 'おやすみなさい'
    },
    'Arabic': {
        'HELLO': 'مرحبا',
        'THANKS': 'شكرا',
        'YES': 'نعم',
        'NO': 'لا',
        'PLEASE': 'من فضلك',
        'SORRY': 'آسف',
        'HELP': 'مساعدة',
        'GOOD MORNING': 'صباح الخير',
        'GOOD NIGHT': 'تصبح على خير'
    }
}

LANGUAGE_CODES = {
    'English': 'en-US',
    'Hindi': 'hi-IN',
    'Telugu': 'te-IN',
    'Spanish': 'es-ES',
    'French': 'fr-FR',
    'German': 'de-DE',
    'Chinese': 'zh-CN',
    'Japanese': 'ja-JP',
    'Arabic': 'ar-SA',
    'Portuguese': 'pt-PT',
    'Russian': 'ru-RU',
    'Italian': 'it-IT',
    'Korean': 'ko-KR',
    'Bengali': 'bn-BD',
    'Tamil': 'ta-IN',
    'Urdu': 'ur-PK'
}

async def translate_image(image_data: str, language: str) -> dict:
    image = image_from_base64(image_data)
    detected = model.predict(image)

    translation_data = TRANSLATION_MAP.get(language, TRANSLATION_MAP['English'])
    translated = translation_data.get(detected, f'{detected} ({language})')
    result_text = f'{detected} — {translated}'

    return {
        'detectedGesture': detected,
        'translatedText': result_text,
        'confidence': float(model.confidence),
        'language': language,
        'speechLang': LANGUAGE_CODES.get(language, 'en-US')
    }
