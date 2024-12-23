from abc import ABC, abstractmethod

from src.services.strategies.factory_strategy import FactoryStrategy


factory = FactoryStrategy(notion_database_id="c3a788eb31f1471f9734157e9516f9b6")


class RecommendationStrategy(ABC):

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = factory.create_questions()
        self.concepts = factory.create_concepts()
        self.users = factory.create_users()
        self.model = factory.create_model()
        self.user_map = factory.load_user_map()
        self.logs = factory.create_logs()
        self.feature_vectors = factory.load_feature_vectors()

    @abstractmethod
    def recommend(self, user_id, max_exercises):
        pass

