import json
import random
import numpy as np
import pandas as pd

from src.services.strategies.strategy_interface import RecommendationStrategy
from src.modules.feature_vectors import FeatureVectors

class ContentBasedStrategy(RecommendationStrategy):
    def recommend(self, user_id, max_exercises):
        priority_df = self.feature_vectors.metadata

        user_id_encoded = self.user_map[user_id]
        user_index = user_id_encoded - 1

        self.model.load_model()
        predicted_ratings = self.model.Yhat[:, user_index]

        recommendations = {
            "exercise_ids": [],
            "knowledge_concepts": [],
            "clusters": [],
            "message": None,
        }

        knowledge_concepts = set()
        items = np.argsort(predicted_ratings)[::-1]

        for item in items:
            if len(recommendations["exercise_ids"]) >= max_exercises:
                break
            if item < len(priority_df):
                recommendations["clusters"].append(int(item))
                question_id = priority_df.iloc[item]["question_id"]
                exercise = self.questions.fetch_one(id=question_id)
                concept = exercise["properties"]["tags"]["multi_select"][0]["name"]
                knowledge_concepts.add(concept)
                recommendations["exercise_ids"].append(exercise)

        recommendations["knowledge_concepts"] = [self.concepts.fetch_one(id=concept)["title"] for concept in list(knowledge_concepts)]
        hi_message = f"{self.users.fetch_user_info(user_id=user_id).get('name')} Ơi!"
        concept_message = ", ".join(recommendations["knowledge_concepts"])
        messages = [
            f"{hi_message} Những câu hỏi này sẽ giúp cậu làm quen với đa dạng các chủ đề {concept_message} cậu đã học trước đây. Hãy thử sức nhé!",
            f"{hi_message} Dựa trên lịch sử học tập và sở thích của cậu, những câu hỏi {concept_message} phù hợp với thế mạnh của cậu. Hãy thử sức nhé!",
            f"{hi_message} Những câu hỏi {concept_message} sẽ giúp cậu khám phá các khái niệm liên quan đến những gì cậu đã thành thạo và yêu thích. Hãy thử sức nhé!"
        ]

        if recommendations:
            recommendations["message"] = (f"{random.choice(messages)}")
        else:
            recommendations["message"] = (
                f"{hi_message}, ScoreUp Tips! Hãy luyện tập thêm bài tập để có thể mở khóa chức năng gợi ý nha!"
            )
        return recommendations