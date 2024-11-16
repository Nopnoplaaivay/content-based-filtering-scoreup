import numpy as np
import json

from src.db import RatingCollection
from src.modules.content_based_recommender import ContentBasedRecommender
from src.modules.spaced_repetition_recommender import LSRRecommender
from src.utils.logger import LOGGER

class Recommender:
    def __init__(self):
        self.cb_reommender = ContentBasedRecommender()
        self.lsr_recommender = LSRRecommender()

    def recommend(self, user_id):
        # Check if user has rated any items
        rating_collection = RatingCollection()
        user_ratings = rating_collection.fetch_ratings_by_user(user_id)
        if user_ratings is None:
            LOGGER.info(f"User {user_id} has not rated any items. Recommending cold start items.")
            return self.cold_start_recommend(user_id)
        else:
            LOGGER.info(f"User {user_id} has rated items. Recommending based on content.")
            return self.cb_recommend(user_id)
        
    def cb_recommend(self, user_id, max_exercises=5):
        recommendation_items = self.cb_reommender.recommend(user_id, max_exercises=max_exercises)
        return recommendation_items
    
    def cold_start_recommend(self, user_id, max_exercises=5):
        recommendation_items = self.lsr_recommender.recommend(user_id, max_exercises=max_exercises)
        return recommendation_items

    # def load_user_map(self):
    #     try:
    #         with open('src/tmp/users/user_map.json') as f:
    #             user_map = json.load(f)
    #         return user_map
    #     except Exception as e:
    #         LOGGER.error(f"Error loading user map: {e}")
    #         return None



