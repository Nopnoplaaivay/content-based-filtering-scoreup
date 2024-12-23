import pandas as pd

from src.repositories.base_repo import BaseRepo
from src.utils.logger import LOGGER

class Questions(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection_name="questions", notion_database_id=notion_database_id)

    def preprocess_questions(self, raw_questions):
        """Preprocess questions into a pandas DataFrame."""
        try:
            data = []
            for question in raw_questions:
                data.append({
                    'question_id': question.get('_id'),
                    'chapter': question.get('chapter'),
                    'difficulty': f"{question.get('difficulty'):.2f}",
                    'concept': question.get('properties').get('tags').get('multi_select')[0].get('name'),
                    'content': question.get('properties').get('question').get('rich_text')[0].get('plain_text')
                })
            return pd.DataFrame(data)
        except Exception as e:
            LOGGER.error(f"Error preprocessing questions: {e}")
            raise e