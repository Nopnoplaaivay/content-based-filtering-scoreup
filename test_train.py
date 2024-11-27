from src.models.content_based import ContentBasedModel

from src.db import Logs
from src.db import Questions
from src.db import Ratings
from src.db import Users
from src.db import Concepts

from src.utils.logger import LOGGER

if __name__ == "__main__":
    '''Train model'''
    # ratings_df = Ratings().get_training_data()
    # LOGGER.info("Training model...")
    # model = ContentBasedModel()
    # model.train(ratings_df=ratings_df)

    # user = UsersCollection().fetch_user(user_id="67021b10012649250e92b7da")
    # print(user)

    # logs = LogsCollection()
    # raw_logs = logs.fetch_logs_by_user(user_id="67021b10012649250e92b7da")
    # logs_df = logs.preprocess_logs(raw_logs)
    # print(logs_df.head())
    # print("-" * 100)

    # logs_2 = Logs()
    # raw_logs = logs_2.fetch_logs_by_user(user_id="67021b10012649250e92b7da")
    # logs_df = logs_2.preprocess_logs(raw_logs)
    # print(logs_df.head())

    # questions = QuestionsCollection()
    # question = questions.fetch_question(question_id="fc084299-5fff-4543-b5f6-5a7971b93da6")
    # print(question)
    # questions_2 = Questions()
    # question = questions_2.fetch_one(id="fc084299-5fff-4543-b5f6-5a7971b93da6")
    # print(question)

    # ratings = Ratings()
    # ratings = ratings.get_training_data()
    # print(ratings)

    # ratings_2 = RatingCollection()
    # ratings = ratings_2.get_training_data()
    # print(ratings)

    # data = {
    #     "user_id": "66ed84437f5170a9671f1ba2",
    #     "data": {
    #         "clusters": [            
    #             2
    #         ],
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

    from src.recommender import Recommender
    recommendations = Recommender().recommend("66f22bf5c5434edfec4e3acf", max_exercises=10)
    print(recommendations)
