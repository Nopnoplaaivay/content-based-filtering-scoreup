from src.models.cbf_model import CBFModel
from src.modules.content_based_recommender import CBFRecommender

from src.db import Logs
from src.db import Questions
from src.db import Ratings
from src.db import Users
from src.db import Concepts

from src.utils.logger import LOGGER

if __name__ == "__main__":
    '''Train model'''
    # user = UsersCollection().fetch_user(user_id="67021b10012649250e92b7da")
    # print(user)

    # logs = LogsCollection()
    # raw_logs = logs.fetch_logs_by_user(user_id="67021b10012649250e92b7da")
    # logs_df = logs.preprocess_logs(raw_logs)
    # print(logs_df.head())
    # print("-" * 100)

    # logs_2 = Logs()
    # raw_logs = logs_2.fetch_logs_by_user(user_id="6747fa55dc9599b62cbebcdb")
    # logs_df = logs_2.preprocess_logs(raw_logs)
    # print(logs_df.head())

    # ratings = Ratings()
    # ratings = ratings.get_training_data()
    # print(ratings)

    # ratings_2 = RatingCollection()
    # ratings = ratings_2.get_training_data()
    # print(ratings)

    # data = {
    #     "user_id": "6747fa55dc9599b62cbebcdb",
    #     "data": {
    #         "clusters": [5, 9, 2, 3, 4],
    #         "rating": 5
    #     }
    # }
    # ratings = Ratings()
    # ratings.upsert(data)

    # users = Users()
    # user = users.fetch_user_info(user_id="67021b10012649250e92b7da")
    # print(user)

    # concepts = Concepts()
    # concept = concepts.fetch_one(id="may-tinh-dien-tu")
    # print(concept["title"])

    # from src.recommender import Recommender
    # recommendations = Recommender().recommend("67021b10012649250e92b7da", max_exercises=10)
    # print(recommendations)

    # ratings_df = Ratings().get_training_data()
    # LOGGER.info("Training model...")
    # model = CBFModel()
    # model.train(ratings_df=ratings_df)

    # cbf_recommender = CBFRecommender()
    # print(cbf_recommender.get_priority_list("6747fa55dc9599b62cbebcdb").head(30))

    # questions = Questions()
    # raw_questions = questions.fetch_all()
    # questions_df = questions.preprocess_questions(raw_questions)
    # Print full df, not truncated
    # import pandas as pd
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(questions_df)
    #     # export to csv
    #     questions_df.to_csv("questions.csv", index=False)

    from src.db import Difficulty
    difficulty = Difficulty()
    difficulty.update()