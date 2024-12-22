import os
import json
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# from src.modules.feature_vectors import FeatureVectors
# from src.models.cbf_model import CBFModel
# from src.modules.content_based_recommender import CBFRecommender
# from src.modules.spaced_repetition_recommender import LSRRecommender
# from src.modules.hybrid_recommender import HybridRecommender
# from src.recommender import Recommender


from src.db import Logs
from src.db import Questions
from src.db import Ratings
from src.db import Users
from src.db import Concepts
from src.db import RecLogs

from src.utils.logger import LOGGER

if __name__ == "__main__":
    user_id = "67021b10012649250e92b7da"

    rec_logs = RecLogs()
    raw_data = rec_logs.fetch_all()
    prepared_data = rec_logs.preprocess_logs(raw_data)

    # Reduce the dataframe to unique user_id and question_id with the latest created_at
    prepared_data = prepared_data.sort_values("created_at", ascending=False)
    prepared_data = prepared_data.drop_duplicates(subset=["user_id", "question_id"], keep="first")
    print(prepared_data[prepared_data["answered"] == False])



    # hybrid_recommender = HybridRecommender()
    # recommendations = hybrid_recommender.recommendation_list(user_id, max_exercises=10)

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

    # LOGGER.info("Training model...")
    # model = CBFModel()
    # model.train()
    # model.load_model()
    # print(model.Yhat)
    # user_id = "67021b10012649250e92b7da"
    # max_exercises = 10
    # recommender = Recommender()
    # recommendations = recommender.recommend(user_id, max_exercises=max_exercises)
    # print(recommendations)
    # cbf_recommender = CBFRecommender()
    # lsr_recommender = LSRRecommender()
    # p_list = cbf_recommender.recommend("67021b10012649250e92b7da", max_exercises=10)
    # print(p_list)

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