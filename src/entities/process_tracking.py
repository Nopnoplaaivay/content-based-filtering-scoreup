from typing import Dict, Union
from bson import ObjectId
from datetime import datetime


class ProcessTracking:
    def __init__(
        self,
        created_at: datetime,
        updated_at: datetime,
        collection_name: str,
        notion_database_id: str,
        key_name: str,
        key_value: datetime 
    ):
        
        self.created_at = created_at
        self.updated_at = updated_at
        self.collection_name = collection_name
        self.notion_database_id = notion_database_id
        self.key_name = key_name
        self.key_value = key_value

    def to_dict(self) -> Dict:
        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "collection_name": self.collection_name,
            "notion_database_id": self.notion_database_id,
            "key_name": self.key_name,
            "key_value": self.key_value
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "ProcessTracking":
        return ProcessTracking(
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            collection_name=data.get("collection_name"),
            notion_database_id=data.get("notion_database_id"),
            key_name=data.get("key_name"),
            key_value=data.get("key_value")
        )
        