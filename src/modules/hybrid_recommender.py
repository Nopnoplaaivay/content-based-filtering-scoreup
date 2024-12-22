import random

from src.db import Ratings, Logs, Users
from src.modules.content_based_recommender import CBFRecommender
from src.modules.spaced_repetition_recommender import LSRRecommender
from src.utils.logger import LOGGER


class HybridRecommender:

    def __init__(self):
        self.cb_recommender = CBFRecommender()
        self.lsr_recommender = LSRRecommender()

    def recommendation_list(self, user_id, max_exercises=5):
        cbf_list = self.cb_recommender.priority_list(user_id)
        print(cbf_list)