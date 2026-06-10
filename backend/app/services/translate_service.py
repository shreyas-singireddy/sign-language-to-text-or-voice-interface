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

import collections

prediction_history = collections.deque(maxlen=5)
last_stable_prediction = "UNKNOWN"

async def translate_image(image_data: str, language: str) -> dict:
    global last_stable_prediction
    
    image = image_from_base64(image_data)
    detected = model.predict(image)

    # Smoothing logic
    if detected != "UNKNOWN" and detected != "NO_HANDS" and detected != "ERROR":
        prediction_history.append(detected)
    else:
        # If no hands, clear history or keep last stable
        prediction_history.clear()
        
    if len(prediction_history) == prediction_history.maxlen:
        # Check if all recent predictions are the same
        if len(set(prediction_history)) == 1:
            last_stable_prediction = prediction_history[0]
            
    # Use stable prediction if available, else fallback to current if it's high confidence, 
    # but for simplicity we'll just use the detected one if stable isn't ready.
    final_prediction = last_stable_prediction if last_stable_prediction != "UNKNOWN" else detected
    if final_prediction in ["UNKNOWN", "NO_HANDS", "ERROR"]:
        final_prediction = detected # Just show what's happening

    translation_data = TRANSLATION_MAP.get(language, TRANSLATION_MAP['English'])
    translated = translation_data.get(final_prediction, f'{final_prediction} ({language})')
    
    # Don't translate system messages
    if final_prediction in ["UNKNOWN", "NO_HANDS", "ERROR"]:
        result_text = final_prediction
    else:
        result_text = f'{final_prediction} — {translated}'

    return {
        'detectedGesture': final_prediction,
        'translatedText': result_text,
        'confidence': float(model.confidence),
        'language': language,
        'speechLang': LANGUAGE_CODES.get(language, 'en-US')
    }
