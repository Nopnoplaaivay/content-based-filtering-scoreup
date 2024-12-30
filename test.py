import os
import json


if __name__ == "__main__":

    from src.repositories import (
        UsersRepo, 
        ConceptsRepo,
        RatingsRepo
    )

    user_id = "6747fa55dc9599b62cbebcdb"
    # print(UsersRepo().fetch_by_id(user_id=user_id))
    # print(ConceptsRepo().fetch_by_id(concept_id="thong-tin-xu-ly-thong-tin"))
    print(RatingsRepo().fetch_by_user(user_id=user_id))
    
    # from src.services.strategies import ContentBasedStrategy, SpacedRepetitionStrategy, HybridStrategy
    # from src.services.recommendation_service import RecommendationService
    # strategy = HybridStrategy()
    # service = RecommendationService(strategy)
    #
    # recommendations = service.get_recommendations(user_id, max_exercises=10)
    # print(recommendations)

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