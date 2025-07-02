from pymongo import IndexModel, ASCENDING
from datetime import datetime
from typing import Optional

class User:
    def __init__(self, db):
        self.collection = db["users"]
        self.setup_indexes()
    
    def setup_indexes(self):
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("verification_token", ASCENDING)]),
        ]
        self.collection.create_indexes(indexes)
    
    async def create_user(self, user_data: dict):
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        user_data["is_verified"] = False
        user_data["is_ops_user"] = False
        result = await self.collection.insert_one(user_data)
        return await self.get_user_by_id(result.inserted_id)
    
    async def get_user_by_email(self, email: str):
        return await self.collection.find_one({"email": email})
    
    async def get_user_by_id(self, user_id: str):
        return await self.collection.find_one({"_id": user_id})
    
    async def verify_user(self, verification_token: str):
        user = await self.collection.find_one({"verification_token": verification_token})
        if user:
            await self.collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "is_verified": True,
                        "verification_token": None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return True
        return False
    
    async def update_user(self, user_id: str, update_data: dict):
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        return await self.get_user_by_id(user_id)
    
    async def make_ops_user(self, email: str):
        await self.collection.update_one(
            {"email": email},
            {"$set": {"is_ops_user": True, "updated_at": datetime.utcnow()}}
        )
        return await self.get_user_by_email(email)