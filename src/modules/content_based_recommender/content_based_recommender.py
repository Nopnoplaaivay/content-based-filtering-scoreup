import json
import random
import numpy as np

from src.modules.items_map import ItemsMap
from src.models.content_based import ContentBasedModel
from src.utils.logger import LOGGER

class ContentBasedRecommender:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
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
            "clusters": [],
            "message": None,
        }

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
                        recommendations["exercise_ids"].append(exercise)
                    else:
                        break
        messages = [
            "These questions connect to multiple topics you’ve studied before, helping you see the bigger picture and build integrated knowledge."
            , "Based on your learning history and preferences, these questions aligns well with your strengths and areas of improvement, offering a perfect next step."
            , "These questions is a great way to reinforce your understanding of a key concept, helping you retain and apply knowledge more effectively."
            , "This question aligns closely with topics you’ve shown interest in, ensuring the learning experience remains both challenging and motivating."
            , "This question is slightly more advanced and explores related concepts to those you've already mastered. It’s chosen to push your boundaries and keep your learning engaging."
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
            return None
