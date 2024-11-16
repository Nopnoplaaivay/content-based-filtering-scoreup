import numpy as np
import json

from src.models import ContentBasedModel
from src.utils.logger import LOGGER

class Recommender:
    def __init__(self):
        self.model = ContentBasedModel()
        self.model.load_weights()
        self.user_map = self.load_user_map()

    def recommend(self, user_id, max_items=5):
        user_id_encoded = self.user_map[user_id]
        user_index = user_id_encoded - 1
        predicted_ratings = self.model.Yhat[:, user_index]
        best_cluster_index = np.argmax(predicted_ratings)
        best_cluster_rating = predicted_ratings[best_cluster_index]
        return best_cluster_index, best_cluster_rating
    
    def load_user_map(self):
        try:
            with open('src/tmp/users/user_map.json') as f:
                user_map = json.load(f)
            return user_map
        except Exception as e:
            LOGGER.error(f"Error loading user map: {e}")
            return None



