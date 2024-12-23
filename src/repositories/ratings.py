import pandas as pd
import json
import numpy as np
import os

from src.repositories.base_repo import BaseRepo
from src.repositories.rec_logs import RecLogs
from src.utils.feature_vectors import FeatureVectors
from src.utils.logger import LOGGER
from src.utils.time_utils import TimeUtils

class Ratings(BaseRepo):
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
        finally:
            self.close()

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
        finally:
            self.close()

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
                raw_ratings = self.fetch_all(query)
                existing_rating = raw_ratings[0] if raw_ratings else None

                # Upsert the rating
                if existing_rating:
                    existing_rating['rating'] = (existing_rating['rating'] + rating) / 2
                    existing_rating['updated_at'] = TimeUtils.vn_current_time()
                    message = f"Updated rating with cluster {cluster} - New Rating: {existing_rating['rating']}"  
                    messages["updated"].append(message)             
                    
                    # Update the existing rating
                    self.update_one(query, {"$set": existing_rating})
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
                    self.insert_one(new_rating)

            LOGGER.info(f"Upserted ratings {messages}.")

            return messages
        except Exception as e:
            LOGGER.error(f"Error upserting rating: {e}")
            raise e
        finally:
            self.close()
        
    def update_implicit_ratings(self):
        try:
            fv = FeatureVectors()
            fv.load_fv()

            # Update the implicit rating for all users
            rec_logs = RecLogs(notion_database_id=self.notion_database_id)
            raw_rec_logs = rec_logs.fetch_all()
            rec_logs_df = rec_logs.preprocess_logs(raw_rec_logs)

            # Reduce the dataframe to unique user_id and question_id with the latest created_at
            rec_logs_df = rec_logs_df.sort_values("created_at", ascending=False)
            rec_logs_df = rec_logs_df.drop_duplicates(subset=["user_id", "question_id"], keep="first")

            # Merge the rec_logs_df with the feature vectors' item_id
            rec_logs_df = pd.merge(rec_logs_df, fv.metadata, left_on="question_id", right_on="question_id", how="left")
            rec_logs_df = rec_logs_df.dropna(subset=["item_id"])
            rec_logs_df = rec_logs_df[["user_id", "item_id", "answered", "timecost", "bookmarked"]]

            # Normalize the timecost
            time_cost_min = rec_logs_df["timecost"].min()
            time_cost_max = np.quantile(rec_logs_df["timecost"], 0.95)
            rec_logs_df = rec_logs_df[rec_logs_df["timecost"] <= time_cost_max]
            target_min, target_max = 0, 1
            rec_logs_df["timecost"] = (rec_logs_df["timecost"] - time_cost_min) / (time_cost_max - time_cost_min) * (target_max - target_min) + target_min
            time_threshold = 1000
            time_threshold_norm = (time_threshold - time_cost_min) / (time_cost_max - time_cost_min) * (target_max - target_min) + target_min

            # Calculate the implicit rating
            def calculate_implicit_rating(row):
                answered = row["answered"] # True if answered, False if not
                timecost = row["timecost"] # Time cost to answer the question (ms)
                bookmarked = row["bookmarked"] # 1 if bookmarked, 0 if not
                
                # Calculate the implicit rating (0 -> 5)
                base_rating = 3 if answered else 0
                if timecost < time_threshold_norm:
                    base_rating -= 1
                else:
                    base_rating += timecost
                base_rating += bookmarked
                return min(max(base_rating, 0), 5)

            os.makedirs("src/tmp/csv", exist_ok=True)
            rec_logs_df["implicit_rating"] = rec_logs_df.apply(calculate_implicit_rating, axis=1)
            rec_logs_df.to_csv("src/tmp/csv/implicit_ratings.csv", index=False)

            # Upsert the implicit ratings
            messages = {
                "inserted": [],
                "updated": []
            }

            total_ratings = len(rec_logs_df)
            for idx, row in rec_logs_df.iterrows():
                user_id = row["user_id"]
                item_id = row["item_id"]
                implicit_rating = row["implicit_rating"]
                query = {"user_id": user_id, "cluster": item_id}
                raw_ratings = self.fetch_all(query)
                existing_rating = raw_ratings[0] if raw_ratings else None

                # Upsert the rating
                if existing_rating:
                    existing_rating['rating'] = implicit_rating
                    existing_rating['updated_at'] = TimeUtils.vn_current_time()
                    existing_rating['implicit'] = True
                    message = f"Updated rating with cluster {item_id} - New Rating: {existing_rating['rating']}"  
                    messages["updated"].append(message)             
                    
                    # Update the existing rating with rating and implicit flag
                    self.update_one(query, {"$set": existing_rating})

                else:
                    new_rating = {
                        "user_id": user_id,
                        "cluster": item_id,
                        "rating": implicit_rating,
                        "implicit": True,
                        "notionDatabaseId": self.notion_database_id,
                        "created_at": TimeUtils.vn_current_time(),
                        "updated_at": TimeUtils.vn_current_time()
                    }
                    message = f"Inserted rating with cluster {item_id} - Rating: {implicit_rating}"
                    messages["inserted"].append(message)

                    # Insert a new rating
                    self.insert_one(new_rating)
                LOGGER.info(f"Upserted implicit rating {idx + 1}/{total_ratings}...")

            LOGGER.info("DONE")
        except Exception as e:
            LOGGER.error(f"Error initializing implicit rating: {e}")
            raise e
        finally:
            self.close()
