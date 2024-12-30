import pandas as pd
import json
import os

from src.repositories.base_repo import BaseRepo
from src.entities import Ratings
from src.utils.logger import LOGGER

class RatingsRepo(BaseRepo):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection="ratings", notion_database_id=notion_database_id)

    def fetch_by_user(self, user_id):
        try:
            query = {"user_id": user_id}
            data = self.fetch_all(query)
            ratings = [Ratings.from_dict(rating).to_dict() for rating in data]
            return ratings
        except Exception as e:
            LOGGER.error(f"Error fetching rating by user: {e}")
            raise e

    def generate_training_data(self):
        '''
        Generate training data for training the model
        Returns pd.DataFrame with columns:  user_id, cluster, rating
        Note: The key is user_id and cluster (newest rating updated)
        '''
        try:
            ratings = self.fetch_all()
            ratings_df = pd.DataFrame(ratings)
            ratings_df = ratings_df.sort_values(by='updated_at', ascending=False)
            ratings_df = ratings_df.drop_duplicates(subset=['user_id', 'cluster'], keep='first')
            ratings_df = ratings_df[['user_id', 'cluster', 'rating']]
            ratings_df = ratings_df.reset_index(drop=True)

            # Label encode user_id 
            user_ids = ratings_df['user_id'].unique()
            user_map_path = "src/tmp/users/user_map.json"
            if os.path.exists(user_map_path):
                with open(user_map_path, "r") as f:
                    try:
                        user_map = json.load(f)
                        if user_map is None:
                            user_map = {}
                    except json.JSONDecodeError:
                        user_map = {}
            else:
                user_map = {}

            user_map = {user_id: idx + 1 for idx, user_id in enumerate(user_ids)}
            ratings_df['user_id_encoded'] = ratings_df['user_id'].map(user_map)
            ratings_df = ratings_df.drop(columns=['user_id'])
            ratings_df = ratings_df.rename(columns={'user_id_encoded': 'user_id', 'cluster': 'item_id'})
            ratings_df = ratings_df[['user_id', 'item_id', 'rating']]
            LOGGER.info(f"Generated training data with {ratings_df.shape[0]} entries and {ratings_df['user_id'].nunique()} unique users.")

            dir = 'src/tmp/users'
            os.makedirs(dir, exist_ok=True)
            with open("src/tmp/users/user_map.json", "w") as f:
                json.dump(user_map, f)
            
            return ratings_df
        except Exception as e:
            LOGGER.error(f"Error generating training data: {e}")
            raise e