from src.factories import FactoryRepo

class BaseService:
    def __init__(self, repository):
        self.repo = repository
        self.factory = FactoryRepo(notion_database_id=self.repo.notion_database_id)
