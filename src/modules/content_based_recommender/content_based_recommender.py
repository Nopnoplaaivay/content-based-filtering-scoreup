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
        recommendations = []
        best_clusters_index = np.argsort(predicted_ratings)[::-1]
        for cluster in best_clusters_index:
            cluster_str = str(cluster)
            for cluster_str in cluster_map:
                exercises = cluster_map[cluster_str]["question_id"]
                random.shuffle(exercises)
                for exercise in exercises:
                    if len(recommendations) < max_exercises:
                        recommendations.append(exercise)
                    else:
                        break

        # Get exercise ids of the best cluster until max_exercises
        # recommendations = [cluster_map[str(cluster_id)]["question_id"] for cluster_id in best_cluster_index[:max_exercises]]
        return recommendations

        # best_cluster_index = np.argmax(predicted_ratings)
        # best_cluster_rating = predicted_ratings[best_cluster_index]
        # return best_cluster_index, best_cluster_rating

    def load_user_map(self):
        try:
            with open('src/tmp/users/user_map.json') as f:
                user_map = json.load(f)
            return user_map
        except Exception as e:
            LOGGER.error(f"Error loading user map: {e}")
            return None
