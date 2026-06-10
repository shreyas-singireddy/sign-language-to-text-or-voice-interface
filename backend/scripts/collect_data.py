import cv2
import mediapipe as mp
import numpy as np
import os
import csv
import time

# Directory for saving the dataset
DATA_DIR = '../data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATASET_CSV = os.path.join(DATA_DIR, 'landmarks.csv')

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

SUPPORTED_GESTURES = [
    'HELLO', 'THANKS', 'YES', 'NO', 'PLEASE', 'SORRY', 'HELP', 'GOOD MORNING', 'GOOD NIGHT'
]

def create_csv():
    """Create CSV file with headers if it doesn't exist."""
    if not os.path.exists(DATASET_CSV):
        headers = ['label']
        for i in range(21): # 21 landmarks
            headers.extend([f'x_{i}', f'y_{i}', f'z_{i}'])
        with open(DATASET_CSV, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def normalize_landmarks(landmarks):
    """Normalize landmarks to make them translation and scale invariant."""
    # Find bounding box
    x_min = min([lm.x for lm in landmarks])
    y_min = min([lm.y for lm in landmarks])
    x_max = max([lm.x for lm in landmarks])
    y_max = max([lm.y for lm in landmarks])

    width = x_max - x_min
    height = y_max - y_min
    
    # Avoid division by zero
    if width == 0: width = 1e-6
    if height == 0: height = 1e-6
    
    normalized = []
    for lm in landmarks:
        normalized.append((lm.x - x_min) / width)
        normalized.append((lm.y - y_min) / height)
        normalized.append(lm.z) # keep z as is for now
    return normalized

def collect_data():
    create_csv()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    current_class_idx = 0
    recording = False
    samples_collected = 0
    target_samples = 200

    print("--- SignBridge AI Data Collection ---")
    print(f"Current Class: {SUPPORTED_GESTURES[current_class_idx]}")
    print("Press 's' to start/stop recording.")
    print("Press 'n' to go to the next class.")
    print("Press 'p' to go to the previous class.")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                if recording and samples_collected < target_samples:
                    normalized_data = normalize_landmarks(hand_landmarks.landmark)
                    
                    row = [SUPPORTED_GESTURES[current_class_idx]] + normalized_data
                    with open(DATASET_CSV, mode='a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(row)
                    
                    samples_collected += 1
                    time.sleep(0.05) # Add a small delay for variety

        # Display UI
        cv2.putText(frame, f"Class: {SUPPORTED_GESTURES[current_class_idx]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f"Samples: {samples_collected}/{target_samples}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if recording else (0, 0, 255), 2)
        if recording:
            cv2.putText(frame, "RECORDING...", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Data Collection', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            recording = not recording
            if recording:
                print(f"Started recording for {SUPPORTED_GESTURES[current_class_idx]}")
            else:
                print(f"Paused recording.")
        elif key == ord('n'):
            current_class_idx = (current_class_idx + 1) % len(SUPPORTED_GESTURES)
            samples_collected = 0
            recording = False
            print(f"Switched to {SUPPORTED_GESTURES[current_class_idx]}")
        elif key == ord('p'):
            current_class_idx = (current_class_idx - 1) % len(SUPPORTED_GESTURES)
            samples_collected = 0
            recording = False
            print(f"Switched to {SUPPORTED_GESTURES[current_class_idx]}")
            
        if samples_collected >= target_samples and recording:
            recording = False
            print(f"Finished recording {target_samples} samples for {SUPPORTED_GESTURES[current_class_idx]}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    collect_data()
