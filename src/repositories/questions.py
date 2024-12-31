import pandas as pd

from src.entities import Questions
from src.repositories.base_repo import BaseRepo
from src.utils.logger import LOGGER

class QuestionsRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="questions", notion_database_id=notion_database_id)

    def preprocess_questions(self, raw_questions):
        """Preprocess questions into a pandas DataFrame."""
        try:
            data = []
            for question in raw_questions:
                question_dict = Questions.from_dict(question).to_dict()
                if question_dict['concept'] == 'post_test':
                    continue
                data.append({
                    'question_id': question.get('_id'),
                    'chapter': question.get('chapter'),
                    'difficulty': question.get('difficulty'),
                    'concept': question.get('properties').get('tags').get('multi_select')[0].get('name'),
                    'content': question.get('properties').get('question').get('rich_text')[0].get('plain_text')
                })
                # data.append(question_dict)

            return pd.DataFrame(data)
        except Exception as e:
            LOGGER.error(f"Error preprocessing questions: {e}")
            raise e