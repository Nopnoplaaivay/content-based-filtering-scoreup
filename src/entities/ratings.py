from typing import Dict, Union
from bson import ObjectId
from datetime import datetime


class Ratings:
    def __init__(
        self, 
        _id: Union[str, ObjectId], 
        user_id: str, 
        cluster: Union[int, float], 
        rating: Union[int, float],
        notion_database_id: str,
        created_at: datetime,
        updated_at: datetime,
        implicit: bool 
    ):
        self._id = _id
        self.user_id = user_id
        self.cluster = cluster
        self.rating = rating
        self.notion_database_id = notion_database_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.implicit = implicit

    def to_dict(self) -> Dict:
        return {
            "id": self._id, 
            "user_id": self.user_id, 
            "cluster": self.cluster, 
            "rating": self.rating,
            "notion_database_id": self.notion_database_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "implitcit": self.implicit
        }

    @staticmethod
    def from_dict(data: Dict) -> "Ratings":
        return Ratings(
            _id=data.get("_id"), 
            user_id=data.get("user_id"), 
            cluster=data.get("cluster"),
            rating=data.get("rating"),
            notion_database_id=data.get("notionDatabaseId"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            implicit=data.get("implicit")
        )