import pandas as pd

from src.db.connection import MongoDBConnection
from src.utils.logger import LOGGER

class QuestionsCollection:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.connection = MongoDBConnection()
        self.collection_name = "questions"
        self.notion_database_id = notion_database_id

    def fetch_all_questions(self):
        """Fetch all questions from the MongoDB collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            questions = list(collection.find({"notionDatabaseId": self.notion_database_id}))
            LOGGER.info(f"Fetched {len(questions)} questions from the database.")
            return questions
        except Exception as e:
            LOGGER.error(f"Error fetching questions: {e}")
            raise e
        finally:
            self.connection.close()

    def preprocess_questions(self, raw_questions):
        try:
            data = []
            for question in raw_questions:
                question_id = question['_id']
                chapter = question['chapter']
                difficulty = f"{question['difficulty']:.2f}"
                tag_name = question['properties']['tags']['multi_select'][0]['name']
                content = question['properties']['question']['rich_text'][0]['plain_text']
                data.append({
                    'question_id': question_id,
                    'chapter': chapter,
                    'difficulty': difficulty,
                    'concept': tag_name,
                    'content': content
                })

            df = pd.DataFrame(data)
            return df
        except Exception as e:
            LOGGER.error(f"Error preprocessing questions: {e}")
            raise e


    def insert_question(self, question):
        """Insert a new question into the collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            result = collection.insert_one(question)
            LOGGER.info(f"Inserted question with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            LOGGER.error(f"Error inserting question: {e}")
            raise e
        finally:
            self.connection.close()
