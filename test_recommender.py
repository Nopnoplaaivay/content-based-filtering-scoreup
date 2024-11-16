import numpy as np
import pandas as pd

from src.recommender import Recommender
np.set_printoptions(precision=2)  # 2 digits after .

# ratings = pd.read_csv('user_cluster_ratings.csv')
user_id = '66f2591ff515ebc548e19223'

# from src.modules.content_based_recommender import ContentBasedRecommender

recommender = Recommender()
print(recommender.recommend(user_id=user_id))


# recommender = Recommender()
# best_cluster_index, best_cluster_rating = recommender.recommend(user_id)
# # cb.load_weights()
# print(best_cluster_index, best_cluster_rating)
# cb.test_pred(user_id=user_id)
# print(f"Predicted cluster for user {user_id}: {cb.pred(user_id)}")

# print("RSME for training: ", cb.evaluate(cb.rating_train))
# print("RSME for testing: ", cb.evaluate(cb.rating_test))