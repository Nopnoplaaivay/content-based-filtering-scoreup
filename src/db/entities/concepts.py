from src.db.base import Base
from src.utils.logger import LOGGER

class Concepts(Base):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection_name="knowledge_concepts", notion_database_id=notion_database_id)