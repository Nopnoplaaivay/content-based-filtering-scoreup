import pandas as pd
from datetime import datetime

from src.db.connection import MongoDBConnection
from src.utils.logger import LOGGER

class LogsCollection:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.connection = MongoDBConnection()
        self.collection_name = "logs-questions"
        self.notion_database_id = notion_database_id

    def fetch_all_logs(self):
        """Fetch logs from the MongoDB collection based on filter criteria."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            logs = list(collection.find({"course_id": self.notion_database_id}))
            LOGGER.info(f"Fetched {len(logs)} logs from the database.")
            return logs
        except Exception as e:
            LOGGER.error(f"Error fetching logs: {e}")
            raise e
        finally:
            self.connection.close()

    def fetch_logs_by_user(self, user_id):
        """Fetch logs from the MongoDB collection based on filter criteria."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            logs = list(collection.find({"course_id": self.notion_database_id, "user_id": user_id}))
            LOGGER.info(f"Fetched {len(logs)} logs from the database.")
            return logs
        except Exception as e:
            LOGGER.error(f"Error fetching logs: {e}")
            raise e
        finally:
            self.connection.close()

    def preprocess_logs(self, raw_logs):
        try:
            data = []
            for log in raw_logs:
                user_id = log['user_id']
                question_id = log['exercise_id']
                chapter = log['chapter']
                concept = log['knowledge_concept']
                difficulty = log['difficulty']
                score = log['score']
                timecost = log['time_cost']
                created_at = log['created_at']
                
                data.append({
                    'user_id': user_id,
                    'question_id': question_id,
                    'chapter': chapter,
                    'concept': concept,
                    'difficulty': difficulty,
                    'score': score,
                    'timecost': timecost,
                    'created_at': created_at
                })

            df = pd.DataFrame(data)
            return df
        except Exception as e:
            LOGGER.error(f"Error preprocessing logs: {e}")
            raise e