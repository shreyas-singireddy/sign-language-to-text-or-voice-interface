import random
import numpy as np
import os
import pickle
import json

try:
    import cv2
    import mediapipe as mp
    MEDIA_AVAILABLE = True
except ImportError:
    cv2 = None
    mp = None
    MEDIA_AVAILABLE = False

SUPPORTED_GESTURES = [
    'HELLO', 'THANKS', 'YES', 'NO', 'PLEASE', 'SORRY', 'HELP', 'GOOD MORNING', 'GOOD NIGHT'
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
LABELS_PATH = os.path.join(os.path.dirname(__file__), 'labels.json')

class SignLanguageModel:
    def __init__(self) -> None:
        self.confidence = 0.0
        self.hands = None
        self.model = None
        self.id_to_label = None

        if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            with open(LABELS_PATH, 'r') as f:
                self.id_to_label = json.load(f)
        
        if MEDIA_AVAILABLE:
            hands_module = getattr(mp, 'solutions', None)
            if hands_module is not None and hasattr(hands_module, 'hands'):
                try:
                    self.hands = hands_module.hands.Hands(
                        static_image_mode=True,
                        max_num_hands=1,
                        min_detection_confidence=0.5,
                    )
                except Exception:
                    self.hands = None

    def normalize_landmarks(self, landmarks):
        x_min = min([lm.x for lm in landmarks])
        y_min = min([lm.y for lm in landmarks])
        x_max = max([lm.x for lm in landmarks])
        y_max = max([lm.y for lm in landmarks])

        width = x_max - x_min
        height = y_max - y_min
        if width == 0: width = 1e-6
        if height == 0: height = 1e-6
        
        normalized = []
        for lm in landmarks:
            normalized.append((lm.x - x_min) / width)
            normalized.append((lm.y - y_min) / height)
            normalized.append(lm.z)
        return normalized

    def predict(self, image: np.ndarray) -> str:
        if image is None or self.hands is None:
            self.confidence = 0.0
            return "NO_HANDS"

        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image_rgb)
            if not results or not results.multi_hand_landmarks:
                self.confidence = 0.0
                return "NO_HANDS"
            
            if self.model is None or self.id_to_label is None:
                # Fallback if model not trained yet
                self.confidence = 50.0
                return random.choice(SUPPORTED_GESTURES)

            # Extract and normalize landmarks for the first hand detected
            landmarks = results.multi_hand_landmarks[0].landmark
            normalized = self.normalize_landmarks(landmarks)
            
            # Predict
            features = np.array([normalized])
            probabilities = self.model.predict_proba(features)[0]
            max_prob_idx = np.argmax(probabilities)
            max_prob = probabilities[max_prob_idx]
            
            self.confidence = max_prob * 100

            # Confidence threshold
            if max_prob > 0.75:
                return self.id_to_label[str(max_prob_idx)]
            else:
                return "UNKNOWN"
            
        except Exception as e:
            print(f"Prediction error: {e}")
            self.confidence = 0.0
            return "ERROR"
