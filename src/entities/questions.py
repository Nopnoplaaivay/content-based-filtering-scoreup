from typing import Dict, Union
from bson import ObjectId
from datetime import datetime


class Questions:
    def __init__(
        self, 
        _id: Union[str, ObjectId], 
        difficulty: Union[int, float],
        concept: str,
        content: str,
        chapter: str,
        notion_database_id: str,
        created_at: datetime,
        updated_at: datetime,

    ):
        self._id = _id
        self.difficulty = difficulty
        self.concept = concept
        self.content = content
        self.chapter = chapter
        self.notion_database_id = notion_database_id
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict:
        return {
            "id": self._id, 
            "difficulty": self.difficulty,
            "concept": self.concept,
            "content": self.content,
            "chapter": self.chapter,
            "notion_database_id": self.notion_database_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict) -> "Questions":
        return Questions(
            _id=data.get("_id"), 
            difficulty=data.get("difficulty"),
            concept=data.get('properties').get('tags').get('multi_select')[0].get('name'),
            content=data.get('properties').get('question').get('rich_text')[0].get('plain_text'),
            chapter=data.get('chapter'),
            notion_database_id=data.get("notion_database_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )