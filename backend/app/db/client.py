from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None

db: Any = None

def get_db() -> Any:
    return db

class FakeCursor:
    def __init__(self, items):
        self.items = items
        self._sort_keys = []
        self._limit = None

    def sort(self, key, direction):
        self._sort_keys.append((key, direction))
        return self

    def limit(self, length):
        self._limit = length
        return self

    async def to_list(self, length):
        items = list(self.items)
        for key, direction in self._sort_keys:
            reverse = direction == -1
            items.sort(key=lambda x: x.get(key), reverse=reverse)
        if self._limit is not None:
            items = items[: self._limit]
        return items[:length]

class FakeCollection:
    def __init__(self):
        self._items = []
        self._id_counter = 0

    async def find_one(self, query):
        for item in self._items:
            match = True
            for k, v in query.items():
                if k == '_id':
                    if str(item.get(k)) != str(v):
                        match = False
                        break
                elif item.get(k) != v:
                    match = False
                    break
            if match:
                return item
        return None

    async def insert_one(self, doc):
        self._id_counter += 1
        doc['_id'] = str(self._id_counter)
        self._items.append(doc)

        class InsertResult:
            inserted_id = doc['_id']

        return InsertResult()

    def find(self, query=None):
        query = query or {}
        matched = []
        for item in self._items:
            match = True
            for k, v in query.items():
                if k == '_id':
                    if str(item.get(k)) != str(v):
                        match = False
                        break
                elif item.get(k) != v:
                    match = False
                    break
            if match:
                matched.append(item)
        return FakeCursor(matched)

    async def delete_one(self, query):
        for index, item in enumerate(self._items):
            match = True
            for k, v in query.items():
                if k == '_id':
                    if str(item.get(k)) != str(v):
                        match = False
                        break
                elif item.get(k) != v:
                    match = False
                    break
            if match:
                self._items.pop(index)

                class DeleteResult:
                    deleted_count = 1

                return DeleteResult()

        class DeleteResult:
            deleted_count = 0

        return DeleteResult()

    async def count_documents(self, query):
        count = 0
        for item in self._items:
            match = True
            for k, v in query.items():
                if k == '_id':
                    if str(item.get(k)) != str(v):
                        match = False
                        break
                elif item.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count

class FakeDB:
    def __init__(self):
        self.users = FakeCollection()
        self.translations = FakeCollection()

# Ensure the application can still store users and translations without MongoDB.
db = FakeDB()

async def connect_to_mongo() -> None:
    global client, db
    if not settings.mongo_uri:
        db = FakeDB()
        return

    try:
        client = AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
        await client.admin.command('ping')
        db = client.get_default_database()
    except Exception:
        db = FakeDB()

async def close_mongo_connection() -> None:
    if client:
        client.close()
