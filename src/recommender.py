import random

from src.db import Ratings
from src.modules.content_based_recommender import ContentBasedRecommender
from src.modules.spaced_repetition_recommender import LSRRecommender
from src.modules.learner_level_recommender import LLRRecommender
from src.utils.logger import LOGGER

class Recommender:
    def __init__(self):
        self.cb_recommender = ContentBasedRecommender()
        self.lsr_recommender = LSRRecommender()
        self.llr_recommender = LLRRecommender()

    def recommend(self, user_id, max_exercises=5):
        # Check if user has rated any items
        ratings = Ratings()
        user_ratings = ratings.fetch_ratings_by_user(user_id)
        if user_ratings is None:
            if random.random() < 0.99:
                LOGGER.info(f"Recommending based on leitner spaced repetition.")
                return self.lsr_recommend(user_id, max_exercises=max_exercises)
            else:
                LOGGER.info(f"Recommending based on user level.")
                return self.llr_recommend(user_id, max_exercises=max_exercises)
        else:
            LOGGER.info(f"Recommending based on CBF Model.")
            return self.cb_recommend(user_id, max_exercises=max_exercises)

    def cb_recommend(self, user_id, max_exercises: int):
        recommendations = self.cb_recommender.recommend(user_id, max_exercises=max_exercises)
        return recommendations
    
    def lsr_recommend(self, user_id, max_exercises: int):
        recommendations = self.lsr_recommender.recommend(user_id, max_exercises=max_exercises)
        return recommendations
    
    def llr_recommend(self, user_id, max_exercises: int):
        recommendations = self.llr_recommender.recommend(user_id, max_exercises=max_exercises)
        return recommendations