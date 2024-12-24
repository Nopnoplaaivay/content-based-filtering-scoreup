import os
import json
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# from src.models.cbf_model import CBFModel
# from src.modules.content_based_recommender import CBFRecommender
# from src.modules.spaced_repetition_recommender import LSRRecommender
# from src.modules.hybrid_recommender import HybridRecommender
# from src.recommender import Recommender

from src.repositories import (Logs, Ratings, Questions, ConceptsRepo, Users)

from src.utils.logger import LOGGER

if __name__ == "__main__":
    user_id = "67021b10012649250e92b7da"

    from src.services.strategies import ContentBasedStrategy, SpacedRepetitionStrategy, HybridStrategy
    from src.services.recommendation_service import RecommendationService
    strategy = HybridStrategy()
    service = RecommendationService(strategy)

    recommendations = service.get_recommendations(user_id, max_exercises=10)
    print(recommendations)

    # hybrid_recommender = HybridRecommender()
    # recommendations = hybrid_recommender.recommendation_list(user_id, max_exercises=10)

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
    # questions_df = questions.preprocess_questions(raw_questions)
    # from src.modules.feature_vectors import FeatureVectors

    # feature_vectors = FeatureVectors()
    # feature_vectors.gen_feature_vectors_df()
    # print(feature_vectors.features_vectors)