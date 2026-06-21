import datetime
import json

from config.config import DATASETS_DIR
from config.logger import setup_logger
from database.mongodb import db_conn

logger = setup_logger("database.learning")

OFFLINE_LEARNING_FILE = DATASETS_DIR / "offline_learning_progress.json"
OFFLINE_QUIZZES_FILE = DATASETS_DIR / "offline_quizzes.json"


class LearningDatabase:
    def __init__(self):
        # Initialize fallback files if they do not exist
        if not OFFLINE_LEARNING_FILE.exists():
            OFFLINE_LEARNING_FILE.write_text(json.dumps({}))
        if not OFFLINE_QUIZZES_FILE.exists():
            OFFLINE_QUIZZES_FILE.write_text(json.dumps([]))

    def _get_learning_collection(self):
        return db_conn.get_collection("learning_progress")

    def _get_quizzes_collection(self):
        return db_conn.get_collection("quizzes")

    def get_progress(self, phone: str) -> dict:
        """
        Retrieves the learning progress profile for a given phone number.
        Returns a default profile if none exists.
        """
        col = self._get_learning_collection()
        if col is not None:
            try:
                doc = col.find_one({"phone": phone})
                if doc:
                    doc["id"] = str(doc.get("_id"))
                    doc.pop("_id", None)
                    return doc
            except Exception as e:
                logger.error(f"Error fetching progress from MongoDB: {e}. Falling back to offline.")

        # Offline fallback
        try:
            with open(OFFLINE_LEARNING_FILE) as f:
                data = json.load(f)
            if phone in data:
                return data[phone]
        except Exception as e:
            logger.error(f"Failed to read offline progress: {e}")

        # Return default profile
        return {
            "phone": phone,
            "skill_level": "Novice",
            "practice_count": 0,
            "average_accuracy": 0.0,
            "weak_signs": [],
            "streak": 0,
            "last_practice_date": None,
        }

    def save_progress(self, phone: str, progress: dict) -> bool:
        """
        Saves or updates the user's learning progress.
        """
        progress["phone"] = phone
        progress["last_updated"] = datetime.datetime.now(datetime.UTC).isoformat()

        col = self._get_learning_collection()
        if col is not None:
            try:
                col.update_one({"phone": phone}, {"$set": progress}, upsert=True)
                logger.info(f"Saved learning progress for {phone} in MongoDB.")
                return True
            except Exception as e:
                logger.error(f"Error saving progress to MongoDB: {e}. Falling back to offline.")

        # Offline fallback
        try:
            with open(OFFLINE_LEARNING_FILE) as f:
                data = json.load(f)
            data[phone] = progress
            with open(OFFLINE_LEARNING_FILE, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved learning progress for {phone} offline.")
            return True
        except Exception as e:
            logger.error(f"Failed to save progress offline: {e}")
            return False

    def log_practice(self, phone: str, accuracy: float, detected_sign: str) -> dict:
        """
        Logs a single practice attempt, updating streaks, accuracies, and weak signs lists.
        """
        progress = self.get_progress(phone)

        # Calculate new average accuracy
        cnt = progress.get("practice_count", 0)
        old_acc = progress.get("average_accuracy", 0.0)
        new_acc = ((old_acc * cnt) + accuracy) / (cnt + 1)

        progress["practice_count"] = cnt + 1
        progress["average_accuracy"] = round(new_acc, 2)

        # Update weak signs
        weak_signs = progress.get("weak_signs", [])
        if accuracy < 0.75:
            if detected_sign and detected_sign not in weak_signs:
                weak_signs.append(detected_sign)
        elif detected_sign in weak_signs:
            weak_signs.remove(detected_sign)
        progress["weak_signs"] = weak_signs[:10]  # cap at 10 weak signs

        # Update daily streak
        today_str = datetime.date.today().isoformat()
        last_date = progress.get("last_practice_date")

        if last_date == today_str:
            # Already practiced today, keep streak
            pass
        elif last_date == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
            # Practiced yesterday, increment streak
            progress["streak"] = progress.get("streak", 0) + 1
        else:
            # Streak broken
            progress["streak"] = 1

        progress["last_practice_date"] = today_str

        # Update skill level based on practice count and average accuracy
        if progress["practice_count"] > 30 and progress["average_accuracy"] >= 0.85:
            progress["skill_level"] = "Advanced"
        elif progress["practice_count"] > 10 and progress["average_accuracy"] >= 0.70:
            progress["skill_level"] = "Intermediate"
        else:
            progress["skill_level"] = "Novice"

        self.save_progress(phone, progress)
        return progress

    def save_quiz(self, phone: str, questions: list) -> str:
        """
        Creates a new quiz record and returns its ID.
        """
        quiz_id = f"quiz_{int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)}"
        quiz = {
            "quiz_id": quiz_id,
            "phone": phone,
            "questions": questions,
            "score": None,
            "completed": False,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }

        col = self._get_quizzes_collection()
        if col is not None:
            try:
                col.insert_one(quiz.copy())
                logger.info(f"Saved new quiz {quiz_id} for {phone} to MongoDB.")
                return quiz_id
            except Exception as e:
                logger.error(f"Error saving quiz to MongoDB: {e}. Falling back to offline.")

        # Offline fallback
        try:
            with open(OFFLINE_QUIZZES_FILE) as f:
                data = json.load(f)
            data.append(quiz)
            with open(OFFLINE_QUIZZES_FILE, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved new quiz {quiz_id} for {phone} offline.")
            return quiz_id
        except Exception as e:
            logger.error(f"Failed to save quiz offline: {e}")
            return quiz_id

    def submit_quiz(self, quiz_id: str, score: int) -> bool:
        """
        Marks a quiz as completed with the given score.
        """
        col = self._get_quizzes_collection()
        if col is not None:
            try:
                res = col.update_one(
                    {"quiz_id": quiz_id},
                    {
                        "$set": {
                            "score": score,
                            "completed": True,
                            "completed_at": datetime.datetime.now(datetime.UTC).isoformat(),
                        }
                    },
                )
                if res.modified_count > 0:
                    logger.info(f"Updated quiz {quiz_id} in MongoDB with score {score}.")
                    return True
            except Exception as e:
                logger.error(f"Error submitting quiz to MongoDB: {e}. Falling back to offline.")

        # Offline fallback
        try:
            with open(OFFLINE_QUIZZES_FILE) as f:
                data = json.load(f)
            updated = False
            for q in data:
                if q.get("quiz_id") == quiz_id:
                    q["score"] = score
                    q["completed"] = True
                    q["completed_at"] = datetime.datetime.now(datetime.UTC).isoformat()
                    updated = True
                    break
            if updated:
                with open(OFFLINE_QUIZZES_FILE, "w") as f:
                    json.dump(data, f, indent=4)
                logger.info(f"Updated quiz {quiz_id} offline with score {score}.")
                return True
        except Exception as e:
            logger.error(f"Failed to update quiz offline: {e}")
        return False


learning_db = LearningDatabase()
