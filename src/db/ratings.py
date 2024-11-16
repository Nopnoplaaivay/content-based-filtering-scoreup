import pandas as pd
import random
import json
import os

from src.db.connection import MongoDBConnection
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER

class RatingCollection:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.connection = MongoDBConnection()
        self.collection_name = "ratings"
        self.notion_database_id = notion_database_id

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


    def upsert(self, rating):
        """Insert a new question into the collection."""
        try:
            self.connection.connect()
            db = self.connection.get_database()
            collection = db[self.collection_name]

            # rating_example = {
            #     "user_id": "669d16e11db84069209550bd",
            #     "cluster": 1,
            #     "rating": 5
            # }

            # Check if user has rated the cluster before
            user_id = rating['user_id']
            cluster = rating['cluster']
            existing_rating = collection.find_one({"user_id": user_id, "cluster": cluster})
            if existing_rating:
                # Update the existing rating
                existing_rating['rating'] = rating['rating']
                existing_rating['updated_at'] = TimeUtils.vn_current_time()
                result = collection.update_one({"_id": existing_rating['_id']}, {"$set": existing_rating})
                LOGGER.info(f"Updated rating with ID: {existing_rating['_id']} - New Rating: {rating['rating']}")
            else:
                # Insert a new rating
                rating['notionDatabaseId'] = self.notion_database_id
                rating['created_at'] = TimeUtils.vn_current_time()
                rating['updated_at'] = TimeUtils.vn_current_time()
                result = collection.insert_one(rating)
                LOGGER.info(f"Inserted rating with ID: {result.inserted_id}")

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

