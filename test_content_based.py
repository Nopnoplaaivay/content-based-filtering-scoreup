import numpy as np
import pandas as pd

from src.models import ContentBased

np.set_printoptions(precision=2)  # 2 digits after .

ratings = pd.read_csv('user_cluster_ratings.csv')

user_id = 299
cb = ContentBased(ratings)
cb.train()
cb.test_pred(user_id=user_id)
print(f"Predicted cluster for user {user_id}: {cb.pred(user_id)}")

print("RSME for training: ", cb.evaluate(cb.rating_train))
print("RSME for testing: ", cb.evaluate(cb.rating_test))