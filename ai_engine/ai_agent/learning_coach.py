import json

from ai_engine.ai_agent.llm_engine import llm_engine
from config.logger import setup_logger
from database.learning_schemas import learning_db

logger = setup_logger("ai_agent.coach")


class LearningCoach:
    def generate_quiz(self, phone: str, lang_name: str = "English", num_questions: int = 3) -> dict:
        """
        Generates a sign language quiz based on the user's weak signs list.
        Uses the LLM engine and falls back to offline templates if necessary.
        """
        # Fetch progress to identify weak signs
        progress = learning_db.get_progress(phone)
        weak_signs = progress.get("weak_signs", [])

        weak_signs_str = ", ".join(weak_signs) if weak_signs else "general sign language concepts"

        system_prompt = (
            "You are a helpful, professional Sign Language Instructor. "
            "Generate multiple-choice quiz questions to test the user's knowledge. "
            "Return ONLY a valid raw JSON array of objects. Do not wrap in markdown code blocks like ```json."
        )

        prompt = (
            f"Generate a quiz in the language '{lang_name}' containing exactly {num_questions} multiple-choice questions. "
            f"Focus on the following signs the user needs practice with: {weak_signs_str}. "
            "Each question object MUST have the following keys:\n"
            "1. 'question_text': A question about how to form the gesture or its meaning.\n"
            "2. 'options': A list of exactly 4 choices.\n"
            "3. 'correct_answer': The exact string from the options that is correct.\n\n"
            "Format the output strictly as a JSON list of objects."
        )

        # Call LLM
        response_text = llm_engine.generate_completion(prompt, system_prompt=system_prompt)

        # Parse JSON
        questions = []
        try:
            # Clean up markdown formatting if the LLM returned it
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            questions = json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse LLM generated quiz: {e}. Falling back to default questions.")
            # Standard fallback questions translated for basic support
            questions = self._get_fallback_questions(lang_name, weak_signs)

        # Save to DB
        quiz_id = learning_db.save_quiz(phone, questions)

        return {"quiz_id": quiz_id, "questions": questions}

    def get_daily_challenge(self, phone: str, lang_name: str = "English") -> dict:
        """
        Returns the active daily practice challenge for the user.
        """
        progress = learning_db.get_progress(phone)
        weak_signs = progress.get("weak_signs", [])

        target_sign = "THANK_YOU"
        if weak_signs:
            target_sign = weak_signs[0]

        # Provide localized descriptions
        challenge_desc = f"Practice the sign '{target_sign}' 3 times with at least 80% tracking accuracy."
        if lang_name.lower() in ["hi", "hindi"]:
            challenge_desc = f"कम से कम 80% सटीकता के साथ '{target_sign}' संकेत का 3 बार अभ्यास करें।"
        elif lang_name.lower() in ["te", "telugu"]:
            challenge_desc = f"కనీసం 80% ఖచ్చితత్వంతో '{target_sign}' గుర్తును 3 సార్లు ప్రాక్టీస్ చేయండి."
        elif lang_name.lower() in ["ta", "tamil"]:
            challenge_desc = f"குறைந்தது 80% துல்லியத்துடன் '{target_sign}' சைகையை 3 முறை பயிற்சி செய்யுங்கள்."
        elif lang_name.lower() in ["kn", "kannada"]:
            challenge_desc = f"ಕನಿಷ್ಠ 80% ನಿಖರತೆಯೊಂದಿಗೆ '{target_sign}' ಸೈನ್ ಅನ್ನು 3 ಬಾರಿ ಅಭ್ಯಾಸ ಮಾಡಿ."
        elif lang_name.lower() in ["ml", "malayalam"]:
            challenge_desc = f"കുറഞ്ഞത് 80% കൃത്യതയോടെ '{target_sign}' അടയാളം 3 തവണ പരിശീലിക്കുക."

        return {
            "challenge_id": f"challenge_{target_sign.lower()}",
            "description": challenge_desc,
            "target_sign": target_sign,
            "target_accuracy": 0.80,
            "required_repetitions": 3,
            "completed": False,
        }

    def _get_fallback_questions(self, lang: str, weak_signs: list) -> list:
        # Simple English default
        q_list = [
            {
                "question_text": "What is the primary visual aspect to watch when signing 'THANK_YOU'?",
                "options": [
                    "Moving the hand flat from the lips forward and down",
                    "Waving the fingers close to the ears",
                    "Pointing to the chest in a circular pattern",
                    "Crossing both arms over the body",
                ],
                "correct_answer": "Moving the hand flat from the lips forward and down",
            },
            {
                "question_text": "How do you improve joint visibility and classification confidence on SignBridge?",
                "options": [
                    "Ensure adequate room lighting and sit straight in front of the lens",
                    "Stand behind a physical obstruction or object",
                    "Perform gestures as rapidly as possible",
                    "Decrease camera frame rate settings",
                ],
                "correct_answer": "Ensure adequate room lighting and sit straight in front of the lens",
            },
        ]

        # Localize question texts slightly for other target languages if set
        if lang.lower() in ["hi", "hindi"]:
            q_list[0]["question_text"] = "'THANK_YOU' संकेत करते समय ध्यान देने योग्य मुख्य दृश्य पहलू क्या है?"
            q_list[0]["options"] = [
                "हाथ को होठों से चपटा करके आगे और नीचे ले जाना",
                "उंगलियों को कानों के पास लहराना",
                "गोलाकार पैटर्न में छाती की ओर इशारा करना",
                "दोनों बाहों को शरीर के ऊपर से पार करना",
            ]
            q_list[0]["correct_answer"] = "हाथ को होठों से चपटा करके आगे और नीचे ले जाना"

            q_list[1]["question_text"] = "साइनब्रिज पर संयुक्त दृश्यता और वर्गीकरण सटीकता में सुधार कैसे करें?"
            q_list[1]["options"] = [
                "कमरे में पर्याप्त प्रकाश व्यवस्था सुनिश्चित करें और लेंस के सामने सीधे बैठें",
                "किसी भौतिक बाधा या वस्तु के पीछे खड़े हों",
                "जितनी जल्दी हो सके संकेत करें",
                "कैमरा फ्रेम दर सेटिंग्स कम करें",
            ]
            q_list[1]["correct_answer"] = "कमरे में पर्याप्त प्रकाश व्यवस्था सुनिश्चित करें और लेंस के सामने सीधे बैठें"

        return q_list


learning_coach = LearningCoach()
