import pymongo
from pymongo.errors import ConnectionFailure, ConfigurationError
from config.config import MONGO_URI, DB_NAME
from config.logger import setup_logger

logger = setup_logger("database.mongodb")

class MongoDBConnection:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def connect(self) -> bool:
        """
        Connects to the MongoDB Atlas cluster.
        Returns True if connection succeeded, False otherwise.
        """
        if self._client is not None:
            return True

        if not MONGO_URI:
            logger.warning("MONGO_URI not configured in env variables. Database operations will run in offline mode.")
            return False

        try:
            logger.info("Initializing MongoDB Client connection pool...")
            # Set a low timeout so Streamlit app does not hang indefinitely on startup
            self._client = pymongo.MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Trigger a ping command to verify connection
            self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas!")
            return True
        except (ConnectionFailure, ConfigurationError) as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}. Operating in offline/mock mode.")
            self._client = None
            return False

    def get_db(self):
        """
        Returns the database instance.
        """
        if self._client is None:
            success = self.connect()
            if not success or self._client is None:
                return None
        return self._client[DB_NAME]

    def get_collection(self, collection_name: str):
        """
        Helper to fetch a specific database collection.
        """
        db = self.get_db()
        if db is None:
            return None
        return db[collection_name]

    def is_connected(self) -> bool:
        """
        Performs a fast connection check (ping).
        """
        if self._client is None:
            return False
        try:
            self._client.admin.command('ping')
            return True
        except ConnectionFailure:
            logger.warning("MongoDB ping failed. Database link is down.")
            return False

    def close(self):
        """Closes the client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("MongoDB client connection closed.")

# Singleton instance accessor
db_conn = MongoDBConnection()
