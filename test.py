import os
import json
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

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
    # logs = Logs()
    # raw_logs = logs.fetch_logs_by_user(user_id="6747fa55dc9599b62cbebcdb")
    # logs_df = logs.preprocess_logs(raw_logs)
    # print(logs_df.head())

    # ratings = Ratings()
    # ratings = ratings.get_training_data()
    # print(ratings)

    # data = {
    #     "user_id": "67021b10012649250e92b7da",
    #     "data": {
    #         "clusters": [43, 47],
    #         "rating": 1
    #     }
    # }
    # ratings = Ratings()
    # ratings.upsert(data)

    # # LOGGER.info("Training model...")
    # model = CBFModel()
    # model.train()
    # model.load_weights()
    # print(model.Yhat)

    cbf_recommender = CBFRecommender()
    p_list = cbf_recommender.recommend("67021b10012649250e92b7da", max_exercises=10)
    print(p_list)
    
    # user_predicted_ratings = p_list["rating"].values
    # current_min, current_max = user_predicted_ratings.min(), user_predicted_ratings.max()
    # desired_min, desired_max = 0, 5
    #
    # user_predicted_ratings = (user_predicted_ratings - current_min) / (current_max - current_min) * (desired_max - desired_min) + desired_min
    # print(user_predicted_ratings)

    # import pandas as pd
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(questions_df)
    #     # export to csv
    #     questions_df.to_csv("questions.csv", index=False)

    # from src.db import Difficulty
    # difficulty = Difficulty()
    # difficulty.update()

    # questions = Questions()
    # raw_questions = questions.fetch_all()
    # questions_df = questions.preprocess_questions(raw_questions)
    # from src.modules.feature_vectors import FeatureVectors

    # feature_vectors = FeatureVectors()
    # feature_vectors.gen_feature_vectors_df()
    # print(feature_vectors.features_vectors)