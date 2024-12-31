from abc import ABC, abstractmethod

from src.factories import FactoryRepo


class RecommendationStrategy(ABC):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.factory = FactoryRepo(notion_database_id=notion_database_id)
        self.questions = self.factory.create_questions()
        self.logs = self.factory.create_logs()
        self.ratings = self.factory.create_ratings()
        self.concepts = self.factory.create_concepts()
        self.users = self.factory.create_users()
        self.user_map = self.factory.load_user_map()
        self.model = self.factory.create_model()
        self.feature_vectors = self.factory.load_feature_vectors()

    @abstractmethod
    def recommend(self, user_id, max_exercises):
        pass