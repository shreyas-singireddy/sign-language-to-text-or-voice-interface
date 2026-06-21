import datetime
import json

from bson import ObjectId

from config.config import DATASETS_DIR
from config.logger import setup_logger
from database.mongodb import db_conn

logger = setup_logger("services.database")

# Local fallback storage path
OFFLINE_HISTORY_FILE = DATASETS_DIR / "offline_history.json"


class DatabaseService:
    def __init__(self):
        # Ensure fallback file exists
        if not OFFLINE_HISTORY_FILE.exists():
            OFFLINE_HISTORY_FILE.write_text(json.dumps([]))

        # Ensure offline preferences file exists
        self.OFFLINE_PREFS_FILE = DATASETS_DIR / "offline_user_preferences.json"
        if not self.OFFLINE_PREFS_FILE.exists():
            self.OFFLINE_PREFS_FILE.write_text(json.dumps({}))

    def _get_history_collection(self):
        return db_conn.get_collection("translation_history")

    def _get_analytics_collection(self):
        return db_conn.get_collection("system_analytics")

    def log_translation(
        self,
        detected_gestures: list,
        translated_text: str,
        confidence: float,
        language: str,
    ) -> dict:
        """
        Saves a translation record. Works online (MongoDB Atlas) or offline (local JSON).
        """
        record = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "detectedGestures": detected_gestures,
            "translatedText": translated_text,
            "confidence": confidence,
            "language": language,
            "is_offline": False,
        }

        col = self._get_history_collection()
        if col is not None:
            try:
                # Add BSON DateTime for MongoDB
                mongo_record = record.copy()
                mongo_record["timestamp"] = datetime.datetime.now(datetime.UTC)
                result = col.insert_one(mongo_record)
                record["id"] = str(result.inserted_id)
                logger.info(f"Logged translation to MongoDB: {translated_text}")
                return record
            except Exception as e:
                logger.error(f"Error logging to MongoDB: {e}. Falling back to local storage.")

        # Local Fallback
        record["is_offline"] = True
        record["id"] = f"offline_{int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)}"
        self._log_offline(record)
        return record

    def _log_offline(self, record: dict):
        try:
            with open(OFFLINE_HISTORY_FILE) as f:
                history = json.load(f)
            history.insert(0, record)  # Prepend new record
            # Keep history capped at 100 entries locally
            history = history[:100]
            with open(OFFLINE_HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=4)
            logger.info(f"Logged translation offline: {record['translatedText']}")
        except Exception as e:
            logger.error(f"Failed to write to local offline storage: {e}")

    def get_history(self, limit: int = 50) -> list:
        """
        Retrieves translation history. Merges online data and offline local records.
        """
        records = []
        col = self._get_history_collection()
        if col is not None:
            try:
                cursor = col.find().sort("timestamp", -1).limit(limit)
                for doc in cursor:
                    doc["id"] = str(doc.get("_id"))
                    doc["timestamp"] = (
                        doc["timestamp"].isoformat()
                        if isinstance(doc["timestamp"], datetime.datetime)
                        else doc["timestamp"]
                    )
                    doc.pop("_id", None)
                    records.append(doc)
                return records
            except Exception as e:
                logger.error(f"Failed to fetch history from MongoDB: {e}. Reading local files.")

        # Fallback to local files
        try:
            with open(OFFLINE_HISTORY_FILE) as f:
                records = json.load(f)
            return records[:limit]
        except Exception as e:
            logger.error(f"Failed to read local offline history: {e}")
            return []

    def delete_history_record(self, record_id: str) -> bool:
        """
        Deletes a specific history record by ID.
        """
        if record_id.startswith("offline_"):
            try:
                with open(OFFLINE_HISTORY_FILE) as f:
                    history = json.load(f)
                updated_history = [r for r in history if r.get("id") != record_id]
                with open(OFFLINE_HISTORY_FILE, "w") as f:
                    json.dump(updated_history, f, indent=4)
                logger.info(f"Deleted offline record: {record_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete offline record: {e}")
                return False

        col = self._get_history_collection()
        if col is not None:
            try:
                result = col.delete_one({"_id": ObjectId(record_id)})
                logger.info(f"Deleted MongoDB record: {record_id}")
                return result.deleted_count > 0
            except Exception as e:
                logger.error(f"Failed to delete MongoDB record {record_id}: {e}")
                return False
        return False

    def get_analytics(self) -> dict:
        """
        Computes aggregates for the analytics charts.
        """
        history = self.get_history(limit=500)
        total_translations = len(history)

        # Calculate stats
        avg_confidence = 0.0
        lang_counts = {}
        gesture_counts = {}
        daily_counts = {}

        if total_translations > 0:
            conf_sum = 0.0
            for r in history:
                conf_sum += r.get("confidence", 0.0)
                lang = r.get("language", "Unknown")
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

                for gesture in r.get("detectedGestures", []):
                    gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

                # Parse simple date yyyy-mm-dd
                dt = r.get("timestamp", "")[:10]
                if dt:
                    daily_counts[dt] = daily_counts.get(dt, 0) + 1

            avg_confidence = conf_sum / total_translations

        return {
            "total_translations": total_translations,
            "average_confidence": round(avg_confidence, 2),
            "language_distribution": lang_counts,
            "gesture_frequency": gesture_counts,
            "daily_activity": daily_counts,
            "db_status": "Online" if db_conn.is_connected() else "Offline",
        }

    def _get_preferences_collection(self):
        return db_conn.get_collection("user_preferences")

    def save_user_language(self, phone: str, language: str) -> bool:
        """
        Saves or updates the user's preferred language.
        Works online (MongoDB) or offline (local JSON).
        """
        col = self._get_preferences_collection()
        if col is not None:
            try:
                col.update_one({"phone": phone}, {"$set": {"phone": phone, "language": language}}, upsert=True)
                logger.info(f"Saved language preference '{language}' for phone {phone} in MongoDB.")
                return True
            except Exception as e:
                logger.error(f"Error saving language preference to MongoDB: {e}. Falling back to offline.")

        # Offline fallback
        try:
            with open(self.OFFLINE_PREFS_FILE) as f:
                prefs = json.load(f)
            prefs[phone] = language
            with open(self.OFFLINE_PREFS_FILE, "w") as f:
                json.dump(prefs, f, indent=4)
            logger.info(f"Saved language preference '{language}' for phone {phone} offline.")
            return True
        except Exception as e:
            logger.error(f"Failed to save offline preference: {e}")
            return False

    def get_user_language(self, phone: str) -> str | None:
        """
        Retrieves the user's preferred language.
        Works online (MongoDB) or offline (local JSON).
        """
        col = self._get_preferences_collection()
        if col is not None:
            try:
                doc = col.find_one({"phone": phone})
                if doc:
                    logger.info(f"Loaded language preference '{doc.get('language')}' for phone {phone} from MongoDB.")
                    return doc.get("language")
            except Exception as e:
                logger.error(f"Error reading language preference from MongoDB: {e}. Falling back to offline.")

        # Offline fallback
        try:
            with open(self.OFFLINE_PREFS_FILE) as f:
                prefs = json.load(f)
            return prefs.get(phone)
        except Exception as e:
            logger.error(f"Failed to read offline preference: {e}")
            return None


db_service = DatabaseService()
