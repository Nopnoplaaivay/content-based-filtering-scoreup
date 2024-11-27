import json
import random
import numpy as np

from src.db import Questions, Concepts, Users
from src.modules.items_map import ItemsMap
from src.models.content_based import ContentBasedModel
from src.utils.logger import LOGGER

class ContentBasedRecommender:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = Questions(notion_database_id=notion_database_id)
        self.concepts = Concepts(notion_database_id=notion_database_id)
        self.users = Users()
        self.model = ContentBasedModel()
        self.model.load_weights()
        self.user_map = self.load_user_map()

    def recommend(self, user_id, max_exercises=5):
        # Get items map
        cluster_map = ItemsMap().get_cluster_map()

        user_id_encoded = self.user_map[user_id]
        user_index = user_id_encoded - 1
        predicted_ratings = self.model.Yhat[:, user_index]

        # Get descending order of predicted ratings index
        recommendations = {
            "exercise_ids": [],
            "knowledge_concepts": [],
            "clusters": [],
            "message": None,
        }

        knowledge_concepts = set()
        clusters = np.argsort(predicted_ratings)[::-1]
        for cluster in clusters:
            cluster_str = str(cluster)
            if len(recommendations["exercise_ids"]) >= max_exercises:
                break
            if cluster_str in cluster_map:
                recommendations["clusters"].append(int(cluster_str))
                exercises = cluster_map[cluster_str]["question_id"]
                random.shuffle(exercises)
                for exercise in exercises:
                    if len(recommendations["exercise_ids"]) < max_exercises:
                        exercise = self.questions.fetch_one(id=exercise)
                        concept = exercise["properties"]["tags"]["multi_select"][0]["name"]
                        knowledge_concepts.add(concept)
                        recommendations["exercise_ids"].append(exercise)
                    else:
                        break

        recommendations["knowledge_concepts"] = [self.concepts.fetch_one(id=concept)["title"] for concept in list(knowledge_concepts)]
        hi_message = f"{self.users.fetch_user_info(user_id=user_id).get('name')} Ơi!"
        concept_message = ", ".join(recommendations["knowledge_concepts"])
        messages = [
            f"{hi_message} Những câu hỏi này sẽ giúp cậu làm quen với đa dạng các chủ đề {concept_message} cậu đã học trước đây. Hãy thử sức nhé!",
            f"{hi_message} Dựa trên lịch sử học tập và sở thích của cậu, những câu hỏi {concept_message} phù hợp với thế mạnh của cậu. Hãy thử sức nhé!",
            f"{hi_message} Những câu hỏi {concept_message} sẽ giúp cậu khám phá các khái niệm liên quan đến những gì bạn đã thành thạo và yêu thích. Hãy thử sức nhé!"
        ]

        if recommendations:
            recommendations["message"] = (f"{random.choice(messages)}")
        else:
            recommendations["message"] = (
                f"Hi User {user_id}, we currently have no recommendations for you. "
                "Please try answering more questions to generate new suggestions!"
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
