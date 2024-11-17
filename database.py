from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME
import datetime
from typing import Dict, Any

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = AsyncIOMotorClient(MONGODB_URI)
            cls._instance.db = cls._instance.client[DATABASE_NAME]
            cls._instance.collection = cls._instance.db[COLLECTION_NAME]
        return cls._instance

    async def save_file_info(self, file_id: str, file_name: str, file_size: int, 
                           mime_type: str, user_id: int, username: str, file_unique_id: str):
        document = {
            "file_id": file_id,
            "file_unique_id": file_unique_id,
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "user_id": user_id,
            "username": username,
            "created_at": datetime.datetime.utcnow(),
            "download_count": 0,
            "last_accessed": datetime.datetime.utcnow(),
            "status": "pending"
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_file_by_id(self, file_id: str):
        return await self.collection.find_one({"file_id": file_id})

    async def update_file_status(self, file_id: str, status: str):
        await self.collection.update_one(
            {"file_id": file_id},
            {"$set": {"status": status}}
        )

    async def increment_download_count(self, file_id: str):
        await self.collection.update_one(
            {"file_id": file_id},
            {
                "$inc": {"download_count": 1},
                "$set": {"last_accessed": datetime.datetime.utcnow()}
            }
        )

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_files": {"$sum": 1},
                "total_size": {"$sum": "$file_size"},
                "total_downloads": {"$sum": "$download_count"}
            }}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0] if result else {"total_files": 0, "total_size": 0, "total_downloads": 0}
