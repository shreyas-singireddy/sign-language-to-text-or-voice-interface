import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseHelper:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    async def connect(self) -> None:
        if not settings.MONGO_URI:
            logger.warning("MONGO_URI is not set. MongoDB client is not connected.")
            return
        
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Ping database to verify connection
            await self.client.admin.command('ping')
            self.db = self.client[settings.DB_NAME]
            logger.info("Connected successfully to MongoDB Atlas.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise e

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection.")

db_manager = DatabaseHelper()

def get_db():
    return db_manager.db
