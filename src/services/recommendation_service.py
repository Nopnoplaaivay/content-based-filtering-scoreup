class RecommendationService:
    def __init__(self, strategy):
        self._strategy = strategy

    def set_strategy(self, strategy):
        self._strategy = strategy

    def get_recommendations(self, user_id, max_exercises=10):
        return self._strategy.recommend(user_id, max_exercises=max_exercises)
