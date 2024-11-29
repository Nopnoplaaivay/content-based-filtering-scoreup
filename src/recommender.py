import random

from src.db import Ratings, Logs, Users
from src.modules.content_based_recommender import CBFRecommender
from src.modules.spaced_repetition_recommender import LSRRecommender
from src.modules.learner_level_recommender import LLRRecommender
from src.utils.logger import LOGGER

class Recommender:
    def __init__(self):
        self.cb_recommender = CBFRecommender()
        self.lsr_recommender = LSRRecommender()
        self.llr_recommender = LLRRecommender()

    def recommend(self, user_id, max_exercises=5):
        # Check if user has done any exercises
        logs = Logs()
        users = Users()
        user_logs = logs.fetch_logs_by_user(user_id)
        if len(user_logs) == 0:
            LOGGER.info(f"User has not done any exercises.")
            recommendations = {
                "exercise_ids": [],
                "knowledge_concepts": [],
                "clusters": [],
                "message": f"{users.fetch_user_info(user_id=user_id).get('name')} ơi! Hãy thử làm một số bài tập để mở khóa chức năng gợi ý học tập nhé!"
            }
            return recommendations

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
            if random.random() < 0.9:
                LOGGER.info(f"Recommending based on leitner spaced repetition.")
                return self.lsr_recommend(user_id, max_exercises=max_exercises)
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