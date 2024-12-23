from src.repositories.base_repo import BaseRepo
from src.utils.logger import LOGGER

class Users(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection_name="users", notion_database_id=notion_database_id)

    def fetch_user_info(self, user_id):
        try:
            user =  self.fetch_one(id=user_id, object_id=True)
            user_info = {
                "id": user.get("_id"),
                "name": user.get("fullName"),
            }
            return user_info
        except Exception as e:
            LOGGER.error(f"Error fetching user info: {e}")
            raise e