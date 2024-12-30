import pandas as pd

from src.entities import Logs
from src.repositories.base_repo import BaseRepo
from src.utils.logger import LOGGER


class LogsRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="logs-questions", notion_database_id=notion_database_id)

    def fetch_by_user(self, user_id):
        try:
            query = {"course_id": self.notion_database_id, "user_id": user_id}
            data = self.fetch_all(query)
            logs = [Logs.from_dict(log).to_dict() for log in data]
            return logs
        except Exception as e:
            LOGGER.error(f"Error fetching logs by user: {e}")
            raise e

    def preprocess_logs(self, raw_logs):
        """Preprocess logs into a pandas DataFrame."""
        try:
            data = []
            for log in raw_logs:
                concept = log.get('knowledge_concept')
                if concept == 'post_test':
                    continue
                data.append({
                    'user_id': log.get('user_id'),
                    'question_id': log.get('exercise_id'),
                    'chapter': log.get('chapter'),
                    'concept': log.get('knowledge_concept'),
                    'difficulty': log.get('difficulty'),
                    'score': log.get('score'),
                    'timecost': log.get('time_cost'),
                    'created_at': log.get('created_at'),
                })
            return pd.DataFrame(data)
        except Exception as e:
            LOGGER.error(f"Error preprocessing logs: {e}")
            raise e