from src.factories.factory_repository import FactoryRepo

class BaseService:
    def __init__(self, repository):
        self.repo = repository
        self.factory = FactoryRepo(notion_database_id=self.repo.notion_database_id)
