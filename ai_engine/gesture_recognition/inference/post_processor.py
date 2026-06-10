from collections import Counter
from typing import List, Dict, Any

class PostProcessor:
    def __init__(self, window_size: int = 5, min_noise_duration: int = 3):
        self.window_size = window_size
        self.min_noise_duration = min_noise_duration
        self.label_window: List[str] = []

    def smooth_predictions(self, predicted_label: str) -> str:
        """
        Applies a rolling window voting filter to smooth high-frequency label changes.
        """
        self.label_window.append(predicted_label)
        if len(self.label_window) > self.window_size:
            self.label_window.pop(0)

        # Return the most common label in the window (majority vote)
        count = Counter(self.label_window)
        most_common, frequency = count.most_common(1)[0]
        
        # Require a minimum consensus to switch labels
        if frequency >= (self.window_size // 2 + 1):
            return most_common
            
        return self.label_window[0]

    def suppress_false_positives(self, label_history: List[str]) -> List[str]:
        """
        Suppresses short-lived predictions (transient noise) that persist for fewer than
        `min_noise_duration` consecutive frames.
        """
        if len(label_history) < self.min_noise_duration:
            return []

        cleaned = []
        consecutive_count = 1
        current_label = label_history[0]

        for i in range(1, len(label_history)):
            label = label_history[i]
            if label == current_label:
                consecutive_count += 1
            else:
                if consecutive_count >= self.min_noise_duration:
                    cleaned.append(current_label)
                current_label = label
                consecutive_count = 1
                
        # Catch tail
        if consecutive_count >= self.min_noise_duration:
            cleaned.append(current_label)

        return cleaned

    def deduplicate_sequence(self, sequence: List[str]) -> List[str]:
        """
        Removes consecutive duplicate words (e.g. ['HELLO', 'HELLO', 'YES'] -> ['HELLO', 'YES']).
        Also removes blank tokens like 'IDLE'.
        """
        deduplicated = []
        for word in sequence:
            if word in ["IDLE", "WAITING_FOR_CLEAR_GESTURE", ""]:
                continue
            if not deduplicated or deduplicated[-1] != word:
                deduplicated.append(word)
        return deduplicated

    def clear(self):
        self.label_window.clear()

post_processor = PostProcessor()
