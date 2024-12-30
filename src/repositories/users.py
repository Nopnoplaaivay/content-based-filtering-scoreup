from typing import Optional
from bson import ObjectId

from src.entities import Users
from src.repositories.base_repo import BaseRepo
from src.utils.logger import LOGGER

class UsersRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="users", notion_database_id=notion_database_id)

    def fetch_by_id(self, user_id: str) -> Optional[Users]:
        try:
            data = self.fetch_one({"_id": ObjectId(user_id)})
            user = Users.from_dict(data) if data else None
            return user.to_dict()
        except Exception as e:
            LOGGER.error(f"Error fetching user by id: {e}")
            raise e