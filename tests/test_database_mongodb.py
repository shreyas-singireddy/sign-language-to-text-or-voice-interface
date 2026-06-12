import pytest
from unittest.mock import MagicMock, patch
from database.mongodb import MongoDBConnection, db_conn
from app.services.database_service import DatabaseService, db_service
from bson import ObjectId
import datetime
from pymongo.errors import ConnectionFailure

def test_mongodb_connection_singleton():
    conn1 = MongoDBConnection()
    conn2 = MongoDBConnection()
    assert conn1 is conn2

@patch("pymongo.MongoClient")
def test_mongodb_connect_success(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    conn = MongoDBConnection()
    # Temporarily set MONGO_URI for testing
    with patch("database.mongodb.MONGO_URI", "mongodb://localhost:27017"):
        # Clear previous client
        conn._client = None
        success = conn.connect()
        assert success is True
        assert conn._client is not None
        mock_client.admin.command.assert_called_with("ping")

@patch("pymongo.MongoClient")
def test_mongodb_connect_failure(mock_client_class):
    mock_client_class.side_effect = ConnectionFailure("Connection error")
    
    conn = MongoDBConnection()
    with patch("database.mongodb.MONGO_URI", "mongodb://localhost:27017"):
        conn._client = None
        success = conn.connect()
        assert success is False
        assert conn._client is None

def test_mongodb_get_db_offline():
    conn = MongoDBConnection()
    with patch("database.mongodb.MONGO_URI", ""):
        conn._client = None
        db = conn.get_db()
        assert db is None

@patch("app.services.database_service.db_conn")
def test_database_service_mongodb_log_success(mock_db_conn):
    mock_col = MagicMock()
    mock_db_conn.get_collection.return_value = mock_col
    
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId()
    mock_col.insert_one.return_value = mock_result
    
    svc = DatabaseService()
    record = svc.log_translation(
        detected_gestures=["HELLO"],
        translated_text="Hello",
        confidence=0.95,
        language="English"
    )
    
    assert record["id"] == str(mock_result.inserted_id)
    assert record["is_offline"] is False
    mock_col.insert_one.assert_called_once()

@patch("app.services.database_service.db_conn")
def test_database_service_mongodb_get_history_success(mock_db_conn):
    mock_col = MagicMock()
    mock_db_conn.get_collection.return_value = mock_col
    
    dummy_id = ObjectId()
    dummy_time = datetime.datetime.now(datetime.UTC)
    mock_cursor = [
        {"_id": dummy_id, "timestamp": dummy_time, "detectedGestures": ["YES"], "translatedText": "Yes", "confidence": 0.9, "language": "English"}
    ]
    mock_col.find.return_value.sort.return_value.limit.return_value = mock_cursor
    
    svc = DatabaseService()
    history = svc.get_history(limit=5)
    
    assert len(history) == 1
    assert history[0]["id"] == str(dummy_id)
    assert history[0]["translatedText"] == "Yes"

@patch("app.services.database_service.db_conn")
def test_database_service_mongodb_delete_success(mock_db_conn):
    mock_col = MagicMock()
    mock_db_conn.get_collection.return_value = mock_col
    
    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_col.delete_one.return_value = mock_result
    
    svc = DatabaseService()
    dummy_id = str(ObjectId())
    success = svc.delete_history_record(dummy_id)
    
    assert success is True
    mock_col.delete_one.assert_called_with({"_id": ObjectId(dummy_id)})
