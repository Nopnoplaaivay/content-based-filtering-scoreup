import os
import json
from datetime import datetime

from src.utils.logger import LOGGER
from src.utils.time_utils import TimeUtils

if __name__ == "__main__":

    '''
    Test repositories
    '''
    from src.entities import (
        Users,
        Concepts,
        Ratings,
        Logs,
        Questions,
        ProcessTracking
    )

    from src.repositories import (
        UsersRepo, 
        ConceptsRepo,
        RatingsRepo,
        LogsRepo,
        QuestionsRepo,
        ProcessTrackingRepo
    )
    
    user_id = "6747fa55dc9599b62cbebcdb"
    # print(UsersRepo().fetch_by_id(user_id=user_id))
    # print(ConceptsRepo().fetch_by_id(concept_id="thong-tin-xu-ly-thong-tin"))
    # print(RatingsRepo().fetch_by_user(user_id=user_id))
    # print(RatingsRepo().generate_training_data())
    # # print(LogsRepo().fetch_by_user(user_id=user_id))
    # raw_questions = QuestionsRepo().fetch_all()
    # print(QuestionsRepo().preprocess_questions(raw_questions))

    # process_tracking = {
    #     "created_at": timestamp,
    #     "updated_at": TimeUtils.vn_current_time(),
    #     "collection_name": "ratings",
    #     "notion_database_id": "c3a788eb31f1471f9734157e9516f9b6",
    #     "key_name": "lastUpdatedday",
    #     "key_value":  TimeUtils.vn_current_time()
    # }

    # ProcessTrackingRepo().insert_one(process_tracking)
    updated_timestamp = datetime.fromisoformat("2024-12-30T09:00:00.153+00:00")

    # Update process tracking
    process_tracking_repo = ProcessTrackingRepo()
    process_tracking_repo.update_one(
        query={"collection_name": "ratings"},
        update={"$set": {"key_value": updated_timestamp}}
    )
    

    '''
    Test strategies
    '''
    # from src.services.strategies import ContentBasedStrategy, SpacedRepetitionStrategy, HybridStrategy
    # from src.services.recommendation_service import RecommendationService
    # strategy = HybridStrategy()
    # service = RecommendationService(strategy)
    # recommendations = service.get_recommendations(user_id=user_id, max_exercises=10)
    # print(recommendations)


    '''
    Test services
    '''
    from src.services.ratings_service import RatingService
    rating_service = RatingService()
    rating_service.update_implicits()
    # rating_service.init_implicits
    
    # data = {
    #     "user_id": "67021b10012649250e92b7da",
    #     "data": {
    #         "clusters": [43, 47],
    #         "rating": 1
    #     }
    # }
    # rating_service.upsert_ratings(data)


    '''
    Test models
    '''
    # from src.models.cbf_model import CBFModel
    # LOGGER.info("Training model...")
    # model = CBFModel()
    # model.train()
    # model.load_model()
    # print(model.Yhat)

    '''
    Test feature vectors
    '''
    # from src.utils.feature_vectors import FeatureVectors
    # feature_vectors = FeatureVectors()
    # feature_vectors.gen_feature_vectors_df()
    # print(feature_vectors.features_vectors)

    '''
    API notes
    '''
    # Thay đổi /recommend --> /api/v1/recommend: same body request
    # Thay đổi /upsert --> /api/v1/ratings/upsert

    # API train: api/v1/model/train
    # API khởi tạo implicit rating: /api/v1/ratings/init
    # API khởi tạo features vector: /api/v1/features/init
    # API update độ khó: /api/v1/questions/update