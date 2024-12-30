from src.repositories.base_repo import BaseRepo


from src.entities import Concepts
from src.utils.logger import LOGGER

class ConceptsRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="knowledge_concepts", notion_database_id=notion_database_id)

    def fetch_by_id(self, concept_id: str):
        try:
            data = self.fetch_one({"_id": concept_id})
            concept = Concepts.from_dict(data) if data else None
            return concept.to_dict()
        except Exception as e:
            LOGGER.error(f"Error fetching concept by id: {e}")
            raise e