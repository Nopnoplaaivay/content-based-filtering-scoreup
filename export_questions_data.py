import pandas as pd

from src.db.questions import QuestionsCollection

questions = QuestionsCollection().fetch_all_questions()
questions_df = QuestionsCollection().preprocess_questions(questions)

questions_df.to_csv("src/data/questions.csv", index=False)