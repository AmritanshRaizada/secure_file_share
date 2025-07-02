from pymongo import IndexModel, ASCENDING, DESCENDING
from datetime import datetime
import os
from typing import Optional

class File:
    def __init__(self, db):
        self.collection = db["files"]
        self.setup_indexes()
    
    def setup_indexes(self):
        indexes = [
            IndexModel([("uploaded_by", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("access_token", ASCENDING)], unique=True, sparse=True),
        ]
        self.collection.create_indexes(indexes)
    
    async def create_file(self, file_data: dict):
        file_data["created_at"] = datetime.utcnow()
        file_data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(file_data)
        return await self.get_file_by_id(result.inserted_id)
    
    async def get_file_by_id(self, file_id: str):
        return await self.collection.find_one({"_id": file_id})
    
    async def get_file_by_access_token(self, access_token: str):
        return await self.collection.find_one({"access_token": access_token})
    
    async def get_files_by_uploader(self, user_id: str):
        return await self.collection.find({"uploaded_by": user_id}).sort("created_at", -1).to_list(None)
    
    async def update_file(self, file_id: str, update_data: dict):
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": file_id},
            {"$set": update_data}
        )
        return await self.get_file_by_id(file_id)
    
    async def delete_file(self, file_id: str):
        file = await self.get_file_by_id(file_id)
        if file:
            if os.path.exists(file["file_path"]):
                os.remove(file["file_path"])
            await self.collection.delete_one({"_id": file_id})
        return file