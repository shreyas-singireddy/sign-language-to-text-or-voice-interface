# DATABASE BLUEPRINT - SignBridge AI Reconstruction Blueprint

This document details the database integration schemas, data structures, and storage behaviors of the SignBridge AI application.

---

## 1. MongoDB Connection Setup

MongoDB connection properties are managed via a singleton connection manager defined in [database/mongodb.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/database/mongodb.py).

*   **Client Driver**: `pymongo`
*   **Default Timeouts**:
    *   `serverSelectionTimeoutMS = 5000` (5-second timeout avoids application hangs if the database is unreachable).
    *   `connectTimeoutMS = 5000`.
*   **Connection Validation**: A ping command checks database connectivity:
    ```python
    self._client.admin.command('ping')
    ```
    If unreachable, the app falls back to offline mode.

---

## 2. Collections & Schema Layouts

The application writes to two collections inside the target database `signbridge_ai`:

### 2.1 Collection: `translation_history`
Used to log translated phrase records.

```json
{
  "_id": {"$oid": "6668021f1e31d45c5ab1e9cb"},
  "timestamp": {"$date": "2026-06-11T12:00:00.000Z"},
  "detectedGestures": ["HELLO", "PLEASE"],
  "translatedText": "Hello, please.",
  "confidence": 0.89,
  "language": "en-US",
  "is_offline": false
}
```

*Key Fields*:
*   `_id`: MongoDB unique identifier.
*   `timestamp`: BSON DateTime object for sorting.
*   `detectedGestures`: Array of strings representing classified gestures.
*   `translatedText`: Formatted translated text string.
*   `confidence`: Float value ($0.0 \dots 1.0$) indicating classification confidence.
*   `language`: Target translation language locale code (e.g. `en-US`).
*   `is_offline`: Boolean value (set to `true` for local fallback records).

### 2.2 Collection: `system_analytics`
Used to log aggregated system telemetry.

```json
{
  "_id": {"$oid": "6668025f1e31d45c5ab1e9cc"},
  "timestamp": {"$date": "2026-06-11T12:00:00.000Z"},
  "total_translations": 1240,
  "average_confidence": 0.84,
  "language_distribution": {
    "en-US": 820,
    "hi-IN": 420
  },
  "gesture_frequency": {
    "HELLO": 500,
    "PLEASE": 320
  }
}
```

---

## 3. Database Indexes

For performance optimization, create the following index on the `translation_history` collection:

*   **Timestamp Index**: Sorted descending (`{"timestamp": -1}`) to speed up sorting in the history view.

---

## 4. Local Offline JSON Fallback Mechanism

If the MongoDB cluster is unreachable or no `MONGO_URI` is provided, database operations automatically fall back to local storage:

*   **Storage Path**: `ai_engine/datasets/data/offline_history.json`.
*   **Format**: JSON array of translation records.
*   **Write Flow**: Prepend new records to the array and cap the list to a maximum of 100 entries to prevent unbounded file growth:
    ```python
    history.insert(0, record)
    history = history[:100]
    ```
*   **Data Merging**: When reading history, the database service attempts to fetch online records and merges them with the local fallback file before displaying them to the user.
