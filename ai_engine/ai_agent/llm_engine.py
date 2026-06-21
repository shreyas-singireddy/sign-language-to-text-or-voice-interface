import json
import os

import httpx

from config.logger import setup_logger

logger = setup_logger("ai_agent.llm")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


class LLMEngine:
    def __init__(self):
        self.client = httpx.Client(timeout=10.0)

    def is_ollama_available(self) -> bool:
        """Checks if local Ollama service is reachable."""
        try:
            res = self.client.get(f"{OLLAMA_HOST}/api/tags")
            return res.status_code == 200
        except Exception:
            return False

    def generate_completion(self, prompt: str, system_prompt: str = "", model: str = None) -> str:
        """
        Generates completion using local Ollama (first choice) or Gemini (online fallback).
        Falls back to rule-based mock responses if neither is available.
        """
        # 1. Try Ollama (Local/Offline)
        if self.is_ollama_available():
            logger.info("Ollama local service detected. Routing request to Ollama...")
            # Use requested model, default to a general open weights fallback
            ollama_model = model or "qwen2.5"
            try:
                payload = {
                    "model": ollama_model,
                    "prompt": f"System: {system_prompt}\nUser: {prompt}" if system_prompt else prompt,
                    "stream": False,
                    "options": {"temperature": 0.3},
                }
                res = self.client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
            except Exception as e:
                logger.error(f"Failed local Ollama query: {e}. Falling back to Gemini...")

        # 2. Try Gemini API (Online)
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            logger.info("Gemini API key detected. Routing request to Google Gemini API...")
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}

                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                payload = {"contents": [{"parts": [{"text": full_prompt}]}], "generationConfig": {"temperature": 0.3}}

                res = self.client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return text.strip()
            except Exception as e:
                logger.error(f"Failed Gemini API request: {e}. Routing to rule-based fallback...")

        # 3. Rule-based Static Fallback (Ensures no crash)
        logger.warning("No LLM connection available. Triggering rule-based agent mock.")
        return self._generate_rule_based_fallback(prompt)

    def _generate_rule_based_fallback(self, prompt: str) -> str:
        """Provides high-quality template responses when completely offline without Ollama."""
        prompt_lower = prompt.lower()

        # Explain Sign
        if "explain" in prompt_lower or "meaning" in prompt_lower:
            return (
                "### Sign Explanation (Offline Fallback)\n\n"
                "This sign is classified as a standard gesture. In general conversation, it represents a polite "
                "acknowledgment, greetings, or basic assertion. \n\n"
                "**Potential Misclassifications:**\n"
                "- Similar circular arm sweeps or hand extensions.\n\n"
                "**Practice Tip:** Keep your fingers aligned and do not overshoot the coordinate plane to improve accuracy."
            )

        # Error Detection
        elif "error" in prompt_lower or "mistake" in prompt_lower or "deviation" in prompt_lower:
            return (
                "### Postural Alignment Analysis (Offline Fallback)\n\n"
                "The gesture tracking system detected a landmark displacement:\n"
                "- **Angle Variance:** Elbow or shoulder joint is out of range by approximately 15%.\n"
                "- **Fingers:** Posture is too tense. Relax the joints and check the camera alignment.\n\n"
                "**Correction suggestion:** Adjust your posture, center your chest to the camera stream, and extend the sign clearly."
            )

        # Conversation suggest
        elif "conversation" in prompt_lower or "predict" in prompt_lower or "phrase" in prompt_lower:
            return (
                "### Conversation Predictions & Suggestions (Offline Fallback)\n\n"
                "Based on the last detected signs, here are likely conversational continuations:\n"
                "1. *'Hello, how can I help you today?'*\n"
                "2. *'Thank you very much for your support.'*\n"
                "3. *'Can we schedule another discussion session?'*"
            )

        # Quiz
        elif "quiz" in prompt_lower or "question" in prompt_lower:
            # Return a valid JSON structure representing quiz questions
            questions = [
                {
                    "question_text": "Which joint coordinate set is primary for tracking finger gestures in MediaPipe?",
                    "options": [
                        "Pose Landmarker keypoints",
                        "Hand Landmarker 21 3D points",
                        "Facial landmark mesh coordinates",
                        "Object detection bounding boxes",
                    ],
                    "correct_answer": "Hand Landmarker 21 3D points",
                },
                {
                    "question_text": "What is the best way to correct a gesture confidence classification bottleneck?",
                    "options": [
                        "Increase room illumination and maintain uniform distance",
                        "Move completely out of view of the camera",
                        "Accelerate hand signing velocity",
                        "Use different sign configurations",
                    ],
                    "correct_answer": "Increase room illumination and maintain uniform distance",
                },
            ]
            return json.dumps(questions)

        # Default fallback
        return (
            "### SignBridge Assistant (Offline)\n\n"
            "Unable to connect to Ollama model or Google Gemini API. Please make sure Ollama is running "
            "locally (`ollama run qwen2.5`) or a valid `GEMINI_API_KEY` is present in your environment variables."
        )


llm_engine = LLMEngine()
