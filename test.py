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

    data = {
        "user_id": "67021b10012649250e92b7da",
        "data": {
            "clusters": [43, 47],
            "rating": 1
        }
    }
    ratings = Ratings()
    ratings.upsert(data)

    # LOGGER.info("Training model...")
    model = CBFModel()
    ratings_df = Ratings().get_training_data()
    model.train(ratings_df=ratings_df)
    model.load_weights()
    # print(model.Yhat)

    cbf_recommender = CBFRecommender()
    p_list = cbf_recommender.get_priority_list("67021b10012649250e92b7da")
    print(p_list.head(30))
    
    # user_predicted_ratings = p_list["rating"].values
    # current_min, current_max = user_predicted_ratings.min(), user_predicted_ratings.max()
    # desired_min, desired_max = 0, 5
    #
    # user_predicted_ratings = (user_predicted_ratings - current_min) / (current_max - current_min) * (desired_max - desired_min) + desired_min
    # print(user_predicted_ratings)

    # questions = Questions()
    # raw_questions = questions.fetch_all()
    # questions_df = questions.preprocess_questions(raw_questions)
    # import pandas as pd
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(questions_df)
    #     # export to csv
    #     questions_df.to_csv("questions.csv", index=False)

    # from src.db import Difficulty
    # difficulty = Difficulty()
    # difficulty.update()

    # from src.modules.items_map import ItemsMap
    # items_map = ItemsMap()
    # items_map.gen_qcmap()
    # features_vector = items_map.get_features_vector()
    # print(features_vector.shape)

    # cluster_map = items_map.get_cluster_map()
    # print(cluster_map)