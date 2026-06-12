# Database Service Specification

## Overview
A service to handle MongoDB Atlas connection with offline fallback using local JSON files.

## Requirements
- **Must Have**: Connect to MongoDB via `pymongo`. Read `MONGO_URI` from `.env`. Fallback to local `offline_history.json` if MongoDB is down or `MONGO_URI` is not provided.
- **Nice to Have**: Re-sync offline records when MongoDB comes back online.
- **Non-goals**: Local SQLite database.

## User Experience
- Target User: End-users.
- Expected workflow: Users will see translation history without interruptions, even without an internet connection.

## Architecture
- Components affected: `app/services/database_service.py`, `database/mongodb.py`
- Data models updated: Translation history dictionary.
- Third-party APIs/Dependencies: MongoDB Atlas.

## Security & Privacy
- Are there any privacy concerns? Translation history is stored. Offline history is stored on the user's disk.
- How is data stored? MongoDB Atlas (Cloud) and Local JSON (Disk).

## Testing Strategy
- Unit test targets: `MongoDBConnection` singleton logic. Mocked DB collections for online logging and history fetching.
- Integration test targets: Test actual MongoDB connection if `MONGO_URI` provided.
- Manual verification steps: Disconnect Wi-Fi, perform a translation, and check if it logs to `offline_history.json`.
