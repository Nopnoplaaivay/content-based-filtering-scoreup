import pandas as pd
import random
import json
import os
import pymongo

from src.db.connection import MongoDBConnection
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER

class RatingCollection:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.connection = MongoDBConnection()
        self.collection_name = "ratings"
        self.notion_database_id = notion_database_id

    def fetch_ratings_by_user(self, user_id):
        """Fetch all ratings by a specific user from the MongoDB collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]

            ratings = list(collection.find({"user_id": user_id}))
            LOGGER.info(f"Fetched {len(ratings)} ratings for user {user_id}.")
            return ratings
        except Exception as e:
            LOGGER.error(f"Error fetching ratings by user: {e}")
            raise e
        finally:
            self.connection.close()

    def fetch_all_ratings(self):
        """Fetch all ratings from the MongoDB collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            ratings = list(collection.find({"notionDatabaseId": self.notion_database_id}))
            LOGGER.info(f"Fetched {len(ratings)} ratings from the database.")
            return ratings
        except Exception as e:
            LOGGER.error(f"Error fetching ratings: {e}")
            raise e
        finally:
            self.connection.close()

    def training_data(self):
        '''
        Generate training data for training the model
        Returns pd.DataFrame with columns:  user_id, cluster, rating
        Note: The key is user_id and cluster (newest rating updated)
        '''
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            ratings = list(collection.find({"notionDatabaseId": self.notion_database_id}))
            LOGGER.info(f"Fetched {len(ratings)} ratings from the database.")
            ratings_df = pd.DataFrame(ratings)
            ratings_df = ratings_df.sort_values(by='updated_at', ascending=False)
            ratings_df = ratings_df.drop_duplicates(subset=['user_id', 'cluster'], keep='first')
            ratings_df = ratings_df[['user_id', 'cluster', 'rating']]
            ratings_df = ratings_df.reset_index(drop=True)

            # Label encode user_id 
            user_ids = ratings_df['user_id'].unique()
            user_map = {user_id: idx + 1 for idx, user_id in enumerate(user_ids)}
            ratings_df['user_id_encoded'] = ratings_df['user_id'].map(user_map)

            ratings_df = ratings_df.drop(columns=['user_id'])
            ratings_df = ratings_df.rename(columns={'user_id_encoded': 'user_id'})
            ratings_df = ratings_df[['user_id', 'cluster', 'rating']]

            LOGGER.info(f"Generated training data with {ratings_df.shape[0]} entries.")

            # save user_map to a file
            dir = 'src/tmp/users'
            if not os.path.exists(dir):
                os.makedirs(dir)
            with open("src/tmp/users/user_map.json", "w") as f:
                json.dump(user_map, f)
            
            return ratings_df
        except Exception as e:
            LOGGER.error(f"Error generating training data: {e}")
            raise e
        finally:
            self.connection.close()

    def upsert(self, data):
        """Insert a new question into the collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]

            # rating_example = {
            #     "user_id": "669d16e11db84069209550bd",
            #     "data": {
            #           "clusters": [2, 7, 12],
            #           "rating": 4
            #     }
            # }

            # Check if user has rated the cluster before
            user_id = data['user_id']
            clusters = data['data']['clusters']
            rating = data['data']['rating']
            messages = {
                "user_id": user_id,
                "inserted": [],
                "updated": []
            }
            for cluster in clusters:
                existing_rating = collection.find_one({"user_id": user_id, "cluster": cluster})
                if existing_rating:
                    # Update the existing rating
                    try:
                        existing_rating['rating'] = (existing_rating['rating'] + rating) / 2
                        existing_rating['updated_at'] = TimeUtils.vn_current_time()
                        result = collection.update_one({"_id": existing_rating['_id']}, {"$set": existing_rating})
                        message = f"Updated rating with cluster {cluster} - New Rating: {existing_rating['rating']}"
                        LOGGER.info(message)
                        messages['updated'].append(message)
                    except Exception as e:
                        LOGGER.error(f"Error updating rating: {e}")
                        raise e
                else:
                    try:
                        # Insert a new rating
                        new_rating = {
                            "user_id": user_id,
                            "cluster": cluster,
                            "rating": rating,
                            "notionDatabaseId": self.notion_database_id,
                            "created_at": TimeUtils.vn_current_time(),
                            "updated_at": TimeUtils.vn_current_time()
                        }
                        result = collection.insert_one(new_rating)
                        message = f"Inserted rating with cluster: {cluster} - Rating: {new_rating['rating']}"
                        LOGGER.info(message)
                        messages["inserted"].append(message)
                    except Exception as e:
                        LOGGER.error(f"Error inserting rating: {e}")
                        raise e
            return messages

        except Exception as e:
            LOGGER.error(f"Error upserting rating: {e}")
            raise e
        finally:
            self.connection.close()

    def generate_random_ratings(self, num_entries=100):
        """Generate random rating data."""
        user_ids = ["669d16e11db84069209550bd", "66f258f4f515ebc548e191f3", "66f2591ff515ebc548e19223"]
        clusters = list(range(1, 36))
        ratings = [round(random.randint(1, 5)) for _ in range(num_entries)]
        
        data = []
        for _ in range(num_entries):
            entry = {
                "notionDatabaseId": self.notion_database_id,
                "user_id": random.choice(user_ids),
                "cluster": random.choice(clusters),
                "rating": random.choice(ratings),
                "created_at": TimeUtils.vn_current_time(),
                "updated_at": TimeUtils.vn_current_time()
            }
            data.append(entry)
        
        return data

    def insert_random_ratings(self, num_entries=100):
        """Insert random rating data into the collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]
            
            random_ratings = self.generate_random_ratings(num_entries)
            result = collection.insert_many(random_ratings)
            LOGGER.info(f"Inserted {len(result.inserted_ids)} random ratings.")
            return result.inserted_ids
        except Exception as e:
            LOGGER.error(f"Error inserting random ratings: {e}")
            raise e
        finally:
            self.connection.close()

