import pandas as pd
import json
import os

from src.db.base import Base
from src.db.entities.users import Users
from src.utils.logger import LOGGER
from src.utils.time_utils import TimeUtils

class Ratings(Base):
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        super().__init__(collection_name="ratings", notion_database_id=notion_database_id)

    def fetch_ratings_by_user(self, user_id):
        try:
            query = {"user_id": user_id}
            ratings = list(self.fetch_all(query))
            return ratings if len(ratings) > 0 else None
        except Exception as e:
            LOGGER.error(f"Error fetching ratings by user: {e}")
            raise e

    def get_training_data(self):
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

            # users = Users()
            # for user_id in user_ids:
            #     if user_id not in user_map:
            #         # print(user_id, type(user_id))
            #         user_info = users.fetch_user_info(user_id=user_id)
            #         LOGGER.info(f"CBF model available for new user: {user_info}")

            user_map = {user_id: idx + 1 for idx, user_id in enumerate(user_ids)}
            ratings_df['user_id_encoded'] = ratings_df['user_id'].map(user_map)
            ratings_df = ratings_df.drop(columns=['user_id'])
            ratings_df = ratings_df.rename(columns={'user_id_encoded': 'user_id', 'cluster': 'item_id'})
            ratings_df = ratings_df[['user_id', 'item_id', 'rating']]
            LOGGER.info(f"Generated training data with {ratings_df.shape[0]} entries.")

            # save user_map to a file
            dir = 'src/tmp/users'
            os.makedirs(dir, exist_ok=True)
            with open("src/tmp/users/user_map.json", "w") as f:
                json.dump(user_map, f)
            
            return ratings_df
        except Exception as e:
            LOGGER.error(f"Error generating training data: {e}")
            raise e

    def upsert(self, data):
        try:
            user_id = data['user_id']
            clusters = data['data']['clusters']
            rating = data['data']['rating']
            messages = {
                "user_id": user_id,
                "inserted": [],
                "updated": []
            }

            for cluster in clusters:
                query = {"user_id": user_id, "cluster": cluster}
                existing_rating = self.fetch_all(query)[0] if self.fetch_all(query) else None

                # Upsert the rating
                self.connect()
                if existing_rating:
                    existing_rating['rating'] = (existing_rating['rating'] + rating) / 2
                    existing_rating['updated_at'] = TimeUtils.vn_current_time()
                    message = f"Updated rating with cluster {cluster} - New Rating: {existing_rating['rating']}"  
                    messages["updated"].append(message)             
                    
                    # Update the existing rating
                    self.connection.update_one(query, {"$set": existing_rating})
                else:
                    new_rating = {
                        "user_id": user_id,
                        "cluster": cluster,
                        "rating": rating,
                        "notionDatabaseId": self.notion_database_id,
                        "created_at": TimeUtils.vn_current_time(),
                        "updated_at": TimeUtils.vn_current_time()
                    }
                    message = f"Inserted rating with cluster {cluster} - Rating: {rating}"
                    messages["inserted"].append(message)

                    # Insert a new rating
                    self.connection.insert_one(new_rating)
                self.close()
            LOGGER.info(f"Upserted ratings {messages}.")

            return messages
        except Exception as e:
            LOGGER.error(f"Error upserting rating: {e}")
            raise e