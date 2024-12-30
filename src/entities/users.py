from typing import Dict, Union
from bson import ObjectId


class Users:
    def __init__(self, _id: Union[str, ObjectId], email: str, full_name: str):
        self._id = _id
        self.email = email
        self.full_name = full_name

    def to_dict(self) -> Dict:
        return {"id": self._id, "email": self.email, "full_name": self.full_name}

    @staticmethod
    def from_dict(data: Dict) -> "Users":
        return Users(
            _id=data.get("_id"),
            email=data.get("email"),
            full_name=data.get("fullName")
        )
