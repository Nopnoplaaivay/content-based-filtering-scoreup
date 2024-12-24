import json

from src.repositories import (
    QuestionsRepo,
    ConceptsRepo,
    UsersRepo,
    LogsRepo,
    RatingsRepo,
    RecLogsRepo
)

from src.utils.feature_vectors import FeatureVectors
from src.models.cbf_model import CBFModel
from src.utils.logger import LOGGER

class FactoryRepo:
    def __init__(self, notion_database_id):
        self.notion_database_id = notion_database_id

    def create_questions(self):
        return QuestionsRepo(notion_database_id=self.notion_database_id)

    def create_logs(self):
        return LogsRepo(notion_database_id=self.notion_database_id)
    
    def create_recommendation_logs(self):
        return RecLogsRepo(notion_database_id=self.notion_database_id)
    
    def create_ratings(self):
        return RatingsRepo(notion_database_id=self.notion_database_id)

    def create_concepts(self):
        return ConceptsRepo(notion_database_id=self.notion_database_id)

    def create_users(self):
        return UsersRepo()

    def create_model(self):
        return CBFModel()

    def load_feature_vectors(self):
        fv = FeatureVectors()
        fv.load_fv()
        return fv

    def load_user_map(self):
        try:
            with open('src/tmp/users/user_map.json') as f:
                user_map = json.load(f)
            return user_map
        except Exception as e:
            LOGGER.error(f"Error loading user map: {e}")
            LOGGER.info("Please call train model routes first (POST /train) to generate user map.")
            return None