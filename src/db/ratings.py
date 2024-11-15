import pandas as pd
import random

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

    # def preprocess_ratings(self, raw_ratings):
    #     try:
    #         data = []
    #         for question in raw_ratings:
    #             question_id = question['_id']
    #             chapter = question['chapter']
    #             difficulty = f"{question['difficulty']:.2f}"
    #             tag_name = question['properties']['tags']['multi_select'][0]['name']
    #             content = question['properties']['question']['rich_text'][0]['plain_text']
    #             data.append({
    #                 'question_id': question_id,
    #                 'chapter': chapter,
    #                 'difficulty': difficulty,
    #                 'concept': tag_name,
    #                 'content': content
    #             })

    #         df = pd.DataFrame(data)
    #         return df
    #     except Exception as e:
    #         LOGGER.error(f"Error preprocessing ratings: {e}")
    #         raise e


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

            # result = collection.insert_one(rating)
            # LOGGER.info(f"Inserted question with ID: {result.inserted_id}")
            # return result.inserted_id
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

