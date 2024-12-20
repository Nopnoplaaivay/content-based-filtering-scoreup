import json
import random
import numpy as np
import pandas as pd

from src.db import Questions, Concepts, Users
from src.modules.feature_vectors import FeatureVectors
from src.models.cbf_model import CBFModel
from src.utils.logger import LOGGER

class CBFRecommender:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = Questions(notion_database_id=notion_database_id)
        self.concepts = Concepts(notion_database_id=notion_database_id)
        self.users = Users()
        self.model = CBFModel()
        self.user_map = self.load_user_map()

    def recommend(self, user_id, max_exercises=5):
        # Get items map
        fv = FeatureVectors()
        fv.load_fv()
        priority_df = fv.metadata

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

    def load_user_map(self):
        try:
            with open('src/tmp/users/user_map.json') as f:
                user_map = json.load(f)
            return user_map
        except Exception as e:
            LOGGER.error(f"Error loading user map: {e}")
            LOGGER.info("Please call train model api first (POST /train) to generate user map.")
            return None

    def priority_list(self, user_id):
        fv = FeatureVectors()
        fv.load_fv()
        priority_df = fv.metadata

        user_id_encoded = self.user_map[user_id]
        user_index = user_id_encoded - 1

        self.model.load_model()
        predicted_ratings = self.model.Yhat[:, user_index]

        # Standardized
        current_min, current_max = predicted_ratings.min(), predicted_ratings.max()
        desired_min, desired_max = 0, 5
        transformed_predicted_ratings = (predicted_ratings - current_min) / (current_max - current_min) * (desired_max - desired_min) + desired_min
        items = np.argsort(transformed_predicted_ratings)[::-1]

        priority_list = []
        for item in items:
            exercise_id = priority_df.iloc[item]["question_id"]
            priority_list.append({"cluster": int(item), "rating": predicted_ratings[item], "exercise_id": exercise_id})

        priority_df = pd.DataFrame(priority_list)
        return priority_df

