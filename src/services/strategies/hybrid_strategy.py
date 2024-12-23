import random


from src.services.strategies.strategy_interface import RecommendationStrategy
from src.services.strategies.content_based_strategy import ContentBasedStrategy
from src.services.strategies.spaced_repetition_strategy import SpacedRepetitionStrategy
from src.utils.logger import LOGGER

class HybridStrategy(RecommendationStrategy):
    def recommend(self, user_id, max_exercises=10):
        user_logs = self.logs.fetch_logs_by_user(user_id)
        user_ratings = self.ratings.fetch_ratings_by_user(user_id)
        if len(user_logs) == 0:
            LOGGER.info(f"User has not done any exercises.")
            recommendations = {
                "exercise_ids": [],
                "knowledge_concepts": [],
                "clusters": [],
                "message": f"{self.users.fetch_user_info(user_id=user_id).get('name')} ơi! Hãy thử làm một số bài tập để mở khóa chức năng gợi ý học tập nhé!"
            }
            return recommendations
        
        if user_ratings is None:
            spaced_repetition_strategy = SpacedRepetitionStrategy()
            return spaced_repetition_strategy.recommend(user_id, max_exercises=max_exercises)

        if random.random() < 0.6:
            spaced_repetition_strategy = SpacedRepetitionStrategy()
            return spaced_repetition_strategy.recommend(user_id, max_exercises=max_exercises)
        else:
            content_based_strategy = ContentBasedStrategy()
            return content_based_strategy.recommend(user_id, max_exercises=max_exercises)