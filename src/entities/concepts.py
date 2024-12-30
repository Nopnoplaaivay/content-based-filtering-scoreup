from typing import Dict, Union
from bson import ObjectId


class Concepts:
    def __init__(
        self, 
        _id: Union[str, ObjectId], 
        title: str, 
        parent: str, 
        course_id: str
    ):
        self._id = _id
        self.title = title
        self.parent = parent
        self.course_id = course_id

    def to_dict(self) -> Dict:
        return {
            "id": self._id, 
            "title": self.title, 
            "parent": self.parent, 
            "course_id": self.course_id
        }

    @staticmethod
    def from_dict(data: Dict) -> "Concepts":
        return Concepts(
            _id=data.get("_id"), 
            title=data.get("title"), 
            parent=data.get("parent"),
            course_id=data.get("course_id")
        )
