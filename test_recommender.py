import numpy as np
import pandas as pd

from src.models.content_based import ContentBasedModel
from src.db import RatingCollection
np.set_printoptions(precision=2)  # 2 digits after .

# ratings = pd.read_csv('user_cluster_ratings.csv')
ratings_df, user_map = RatingCollection().training_data()
user_id = '66f2591ff515ebc548e19223'
user_id_encoded = user_map[user_id]
print(user_map)
print(f"User ID: {user_id} -> Encoded User ID: {user_id_encoded}")
# print(f"Rating data:")
# print(ratings_df) 

cb = ContentBasedModel()
# print(cb.feature_vectors)
# print(cb.n_users)
# print(cb.rating_train)
# print(cb.rating_test)
# print("Training...")
cb.train(ratings_df=ratings_df)
# cb.load_weights()
print(cb.pred(user_id_encoded))
# cb.test_pred(user_id=user_id)
# print(f"Predicted cluster for user {user_id}: {cb.pred(user_id)}")

# print("RSME for training: ", cb.evaluate(cb.rating_train))
# print("RSME for testing: ", cb.evaluate(cb.rating_test))