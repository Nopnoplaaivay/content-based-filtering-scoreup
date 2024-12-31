

from src.repositories.base_repo import BaseRepo
from src.entities import ProcessTracking
from src.utils.logger import LOGGER

class ProcessTrackingRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="process_tracking", notion_database_id=notion_database_id)

    def fetch_by_collection(self, collection):
        try:
            query = {"collection_name": collection}
            data = self.fetch_all(query)
            process_trackings = [ProcessTracking.from_dict(process_tracking).to_dict() for process_tracking in data]
            return process_trackings
        except Exception as e:
            LOGGER.error(f"Error fetching process tracking by collection: {e}")
            raise e