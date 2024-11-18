from src.db import RatingCollection
from src.modules.content_based_recommender import ContentBasedRecommender
from src.modules.spaced_repetition_recommender import LSRRecommender
from src.utils.logger import LOGGER

class Recommender:
    def __init__(self):
        self.cb_recommender = ContentBasedRecommender()
        self.lsr_recommender = LSRRecommender()

    def recommend(self, user_id):
        # Check if user has rated any items
        rating_collection = RatingCollection()
        user_ratings = rating_collection.fetch_ratings_by_user(user_id)
        if user_ratings is None:
            LOGGER.info(f"User {user_id} has not rated any items. Recommending cold start items.")
            return self.cs_recommend(user_id)
        else:
            LOGGER.info(f"User {user_id} has rated items. Recommending based on content.")
            return self.cb_recommend(user_id)
        
    def cb_recommend(self, user_id, max_exercises=5):
        recommendations = self.cb_recommender.recommend(user_id, max_exercises=max_exercises)
        return recommendations
    
    def cs_recommend(self, user_id, max_exercises=5):
        recommendations = self.lsr_recommender.recommend(user_id, max_exercises=max_exercises)
        return recommendations