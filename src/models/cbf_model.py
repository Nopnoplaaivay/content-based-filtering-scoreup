import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge

from src.db import Ratings
from src.modules.feature_vectors import FeatureVectors
from src.utils.logger import LOGGER

class CBFModel:

    def __init__(self):
        self.n_users = None
        self.rating_train = None
        self.rating_test = None

    def save_model(self):
        dir = 'src/tmp/weights'
        os.makedirs(dir, exist_ok=True)
        np.save('src/tmp/weights/content_based_model_weights.npy', self.Yhat)

    def load_model(self):
        try:
            self.Yhat = np.load('src/tmp/weights/content_based_model_weights.npy')
            LOGGER.info("Loaded weights successfully.")
        except Exception as e:
            LOGGER.error(f"Error loading weights: {e}")
            LOGGER.info("Training model...")
            self.train()

    def train_test_split_data(self, ratings_df, test_size=0.2, random_state=42):
        rating_train = pd.DataFrame(columns=ratings_df.columns)
        rating_test = pd.DataFrame(columns=ratings_df.columns)

        for _, group in ratings_df.groupby('user_id'):
            if len(group) >= 2:
                train, test = train_test_split(group, test_size=test_size, random_state=random_state)
                rating_train = pd.concat([rating_train, train])
                rating_test = pd.concat([rating_test, test])

        rating_train_base = rating_train.sort_values(by='user_id').reset_index(drop=True)
        rating_test_base = rating_test.sort_values(by='user_id').reset_index(drop=True)

        rating_train = rating_train_base.values
        rating_test = rating_test_base.values

        return rating_train, rating_test

    def get_items_rated_by_user(self, rate_matrix, user_id):
        """
        in each line of rate_matrix, we have infor: user_id, cluster, rating (scores), time_stamp
        we care about the first three values
        return (item_ids, scores) rated by user user_id
        """
        y = rate_matrix[:,0] # all users
        # item indices rated by user_id
        # we need to +1 to user_id since in the rate_matrix, id starts from 1 
        # while index in python starts from 0
        ids = np.where(y == user_id)[0] 
        item = rate_matrix[ids, 1]
        ratings = rate_matrix[ids, 2]
        return (item, ratings)

    def train(self):
        ratings = Ratings()
        ratings_df = ratings.get_training_data()

        self.n_users = ratings_df['user_id'].nunique()
        self.rating_train, self.rating_test = self.train_test_split_data(ratings_df, test_size=0.2, random_state=42)
        fv = FeatureVectors()
        fv.load_fv()
        feature_vectors = fv.features_vectors

        d = feature_vectors.shape[1]
        W = np.zeros((d, self.n_users))
        b = np.zeros((1, self.n_users))

        for n in range(self.n_users):
            user_id = n + 1
            item, scores = self.get_items_rated_by_user(self.rating_train, user_id)
            item = list(map(int, item))
            if len(item) == 0:
                continue  # The rating train may not have any rating of user n
            clf = Ridge(alpha=1.0, fit_intercept=True)
            Xhat = feature_vectors[item, :]

            clf.fit(Xhat, scores)
            W[:, n] = clf.coef_
            b[0, n] = clf.intercept_

        self.W = W
        self.b = b
        self.Yhat = feature_vectors.dot(W) + b
        self.save_model()
        LOGGER.info("Training completed.")

    def test_pred(self, user_id):
        ids, scores = self.get_items_rated_by_user(self.rating_test, user_id)
        ids = list(map(int, ids))
        predict_ratings = self.Yhat[ids, user_id - 1]

        print("rated cluster: ", ids)
        print("true ratings: ", scores)
        print("predict ratings: ", predict_ratings)

    def evaluate(self, rate_matrix):
        se = 0
        cnt = 0
        for n in range(self.n_users):
            ids, scores_truth = self.get_items_rated_by_user(rate_matrix, n)
            ids = list(map(int, ids))
            scores_pred = self.Yhat[ids, n]
            e = scores_truth - scores_pred
            se += (e*e).sum(axis = 0)
            cnt += e.size
        return np.sqrt(se/cnt)
