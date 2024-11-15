import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn import linear_model

from src.models.feature_vectors import FeaturesVector

FeaturesVector.generate_features_vector()

class ContentBased:

    def __init__(self, ratings: pd.DataFrame):
        self.ratings = ratings
        self.n_users = ratings['user_id'].nunique()
        self.feature_vectors = np.array(list(FeaturesVector.FEATURES_VECTOR.values()))
        self.split_data()

    def split_data(self):
        rating_train_base = pd.DataFrame(columns=self.ratings.columns)
        rating_test_base = pd.DataFrame(columns=self.ratings.columns)

        # Group the data by user_id and split each group
        for user_id, group in self.ratings.groupby('user_id'):
            train, test = train_test_split(group, test_size=0.2, random_state=42)
            rating_train_base = pd.concat([rating_train_base, train])
            rating_test_base = pd.concat([rating_test_base, test])


        rating_train_base = rating_train_base.sort_values(by='user_id').reset_index(drop=True)
        rating_test_base = rating_test_base.sort_values(by='user_id').reset_index(drop=True)
        rating_train_base.to_csv('user_cluster_ratings_train.csv', index=False)
        rating_test_base.to_csv('user_cluster_ratings_test.csv', index=False)

        # Convert to matrix: np array
        self.rating_train = rating_train_base.values
        self.rating_test = rating_test_base.values

    @staticmethod
    def get_items_rated_by_user(rate_matrix, user_id):
        """
        in each line of rate_matrix, we have infor: user_id, item_id, rating (scores), time_stamp
        we care about the first three values
        return (item_ids, scores) rated by user user_id
        """
        y = rate_matrix[:,0] # all users
        # item indices rated by user_id
        # we need to +1 to user_id since in the rate_matrix, id starts from 1 
        # while index in python starts from 0
        ids = np.where(y == user_id)[0] 
        item_ids = rate_matrix[ids, 1] # index starts from 0 
        scores = rate_matrix[ids, 2]
        return (item_ids, scores)

    def train(self):
        d = self.feature_vectors.shape[1]
        W = np.zeros((d, self.n_users))
        b = np.zeros((1, self.n_users))

        for n in range(self.n_users):
            user_id = n + 1
            ids, scores = self.get_items_rated_by_user(self.rating_train, user_id)
            ids = list(map(int, ids))
            clf = Ridge(alpha=1.0, fit_intercept = True)
            Xhat = self.feature_vectors[ids, :]

            clf.fit(Xhat, scores) 
            W[:, n] = clf.coef_
            b[0, n] = clf.intercept_

        self.W = W
        self.b = b
        self.Yhat = self.feature_vectors.dot(W) + b

    def test_pred(self, user_id):
        ids, scores = self.get_items_rated_by_user(self.rating_test, user_id)
        ids = list(map(int, ids))
        predict_ratings = self.Yhat[ids, user_id - 1]

        print("rated cluster: ", ids)
        print("true ratings: ", scores)
        print("predict ratings: ", predict_ratings)

    def pred(self, user_id):
        user_index = user_id - 1
        predicted_ratings = self.Yhat[:, user_index]
        best_cluster_index = np.argmax(predicted_ratings)
        best_cluster_rating = predicted_ratings[best_cluster_index]
        return best_cluster_index, best_cluster_rating

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
