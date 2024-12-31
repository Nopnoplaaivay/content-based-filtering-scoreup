from typing import Dict, Union
from bson import ObjectId
from datetime import datetime


class Logs:
    def __init__(
        self, 
        _id: Union[str, ObjectId], 
        user_id: str, 
        course_id: str,
        exercise_id: str,
        difficulty: Union[int, float],
        knowledge_concept: str,
        answered: Union[int, bool, None],
        score: Union[int, float],
        time_cost: Union[int, float],
        chapter: str,
        bookmarked: Union[int, bool, None],
        mastered: Union[int, bool, None],
        created_at: datetime,
        updated_at: datetime
    ):
        self._id = _id
        self.user_id = user_id
        self.exercise_id = exercise_id
        self.course_id = course_id
        self.difficulty = difficulty
        self.knowledge_concept = knowledge_concept
        self.score = score
        self.answered = answered
        self.time_cost = time_cost
        self.chapter = chapter
        self.bookmarked = bookmarked
        self.mastered = mastered
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict:
        return {
            "id": self._id, 
            "user_id": self.user_id, 
            "exercise_id": self.exercise_id,
            "course_id": self.course_id,
            "difficulty": self.difficulty,
            "knowledge_concept": self.knowledge_concept,
            "score": self.score,
            "answered": self.answered,
            "time_cost": self.time_cost,
            "chapter": self.chapter,
            "bookmarked": self.bookmarked,
            "mastered": self.mastered,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict) -> "Logs":
        return Logs(
            _id=data.get("_id"), 
            user_id=data.get("user_id"),
            exercise_id=data.get("exercise_id"),
            course_id=data.get("course_id"),
            difficulty=data.get("difficulty"),
            knowledge_concept=data.get("knowledge_concept"),
            score=data.get("score"),
            answered=data.get("answered") ,
            time_cost=data.get("time_cost"),
            chapter=data.get("chapter"),
            bookmarked=data.get("bookmarked"),
            mastered=data.get("mastered"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )