import pandas as pd

from src.repositories.base_repo import BaseRepo
from src.utils.logger import LOGGER


class LogsRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="logs-questions", notion_database_id=notion_database_id)

    def fetch_logs_by_user(self, user_id):
        try:
            query = {"course_id": self.notion_database_id, "user_id": user_id}
            return self.fetch_all(query)
        except Exception as e:
            LOGGER.error(f"Error fetching logs: {e}")
            raise e
        finally:
            self.close()

    def preprocess_logs(self, raw_logs):
        """Preprocess logs into a pandas DataFrame."""
        try:
            data = []
            for log in raw_logs:
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

    def get_user_level(self, user_id):
        try:
            logs = self.fetch_logs_by_user(user_id)
            df = self.preprocess_logs(logs)
            avg_score = df['score'].mean()
            if avg_score <= 0.33:
                return 'Beginner'
            elif avg_score <= 0.66:
                return 'Intermediate'
            else:
                return 'Advanced'
        except Exception as e:
            LOGGER.error(f"Error fetching user level logs: {e}")
            raise e
        finally:
            self.close()