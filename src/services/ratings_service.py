import numpy as np
import pandas as pd
import os
import time
from typing import Dict, List, Optional
import datetime

from src.entities import ProcessTracking
from src.repositories import RatingsRepo, ProcessTrackingRepo
from src.services.base_service import BaseService
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER


class RatingService(BaseService):
    RATING_BOUNDS = (0, 5)
    TIMECOST_NORM_BOUNDS = (0, 1)
    TIME_THRESHOLD_MS = 1000
    BATCH_SIZE = 100
    CSV_OUTPUT_DIR = "src/tmp/csv"
    
    def __init__(self):
        super().__init__(RatingsRepo())
        self.process_tracking_repo = self.factory.create_process_tracking()
        self.recommendation_logs_repo = self.factory.create_recommendation_logs()
        self.feature_vectors = self.factory.load_feature_vectors()


    def update_newest_ratings_daily(self) -> bool:
        try:
            condition = {"collection_name": "ratings"}
            tracking_records = self.process_tracking_repo.fetch_all(condition)
            if len(tracking_records) == 0:
                self.process_tracking_repo.insert_one({
                    "created_at": TimeUtils.vn_current_time(),
                    "updated_at": TimeUtils.vn_current_time(),
                    "collection_name": "ratings",
                    "notion_database_id": self.repo.notion_database_id,
                    "key_name": "lastUpdatedday",
                    "key_value": None
                })
                tracking_records = self.process_tracking_repo.fetch_all(condition)
            if len(tracking_records) > 1:
                LOGGER.error("More than one tracking record found.")
                raise Exception("More than one tracking record found.")
            tracking_record = tracking_records[0]
            key_value = tracking_record.get("key_value")
            if key_value is not None:
                last_updated_day = key_value
                if  TimeUtils.vn_current_time() - last_updated_day < datetime.timedelta(days=1):
                    LOGGER.info("No Ratings were updated less than a day ago.")
                    return False
                continue_updated_day = last_updated_day - datetime.timedelta(days=1)
                LOGGER.info(f"Continue Updated Day: {continue_updated_day}")
            else:
                continue_updated_day = datetime.datetime(2024, 11, 1)
                LOGGER.info(f"Start Updated Day: {continue_updated_day}")
            
            self.update_newest_ratings_from_date(from_date=continue_updated_day, tracking_record=tracking_record)
            LOGGER.info("DONE")
            return True
        except Exception as e:
            LOGGER.error(f"Error updating newest rating daily: {e}")
            raise e

    def update_newest_ratings_from_date(self, from_date: datetime.datetime, tracking_record: Dict) -> None:
        last_day = TimeUtils.vn_current_time()
        last_day = last_day - datetime.timedelta(days=1)
        while from_date < last_day:
            # Get rating logs on from_date only
            end_from_date = from_date + datetime.timedelta(days=1)
            rec_logs_df = self._get_processed_logs({"created_at": {"$gt": from_date, "$lt": end_from_date}})
            if len(rec_logs_df) == 0:
                from_date += datetime.timedelta(days=1)
                continue
            LOGGER.info(f"Processing ratings from {from_date} to {end_from_date}...")
            # Update from date
            from_date = rec_logs_df["created_at"].max()
            # Upsert ratings
            self._process_and_upsert_ratings(rec_logs_df)
            self.process_tracking_repo.update_one(
                query={"collection_name": "ratings"},
                update={"$set": {"key_value": from_date}}
            )


    '''
    Lấy và xử lý recommendation logs
    '''
    def _get_processed_logs(self, query: Dict = None) -> pd.DataFrame:
        """Retrieves and processes recommendation logs."""
        raw_rec_logs = self.recommendation_logs_repo.fetch_all(query or {})
        rec_logs_df = self.recommendation_logs_repo.preprocess_logs(raw_rec_logs)
        if len(rec_logs_df) == 0:
            return pd.DataFrame()
        
        # Get latest entries for each user-question pair
        rec_logs_df = rec_logs_df.sort_values("created_at", ascending=False)
        rec_logs_df = rec_logs_df.drop_duplicates(subset=["user_id", "question_id"], keep="first")
        
        # Merge with feature vectors and clean data
        rec_logs_df = pd.merge(
            rec_logs_df, 
            self.feature_vectors.metadata,
            left_on="question_id",
            right_on="question_id",
            how="left"
        )
        rec_logs_df = rec_logs_df.dropna(subset=["item_id"])
        return rec_logs_df[["user_id", "item_id", "answered", "timecost", "bookmarked", "created_at"]]

    '''
    Chuẩn hóa và tính toán implicit ratings
    '''
    def _normalize_timecost(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizes timecost values in the dataframe."""
        df = df.copy()
        time_cost_min = df["timecost"].min()
        time_cost_max = np.quantile(df["timecost"], 0.95)
        
        # Filter những timecost lớn hơn 95th percentile
        df = df[df["timecost"] <= time_cost_max]
        
        # Normalize timecost
        df["timecost"] = (df["timecost"] - time_cost_min) / (time_cost_max - time_cost_min) * \
                        (self.TIMECOST_NORM_BOUNDS[1] - self.TIMECOST_NORM_BOUNDS[0]) + \
                        self.TIMECOST_NORM_BOUNDS[0]
                        
        return df, self._normalize_threshold(time_cost_min, time_cost_max)

    def _normalize_threshold(self, min_val: float, max_val: float) -> float:
        """Normalizes the time threshold using the same scale as timecost."""
        return (self.TIME_THRESHOLD_MS - min_val) / (max_val - min_val) * \
               (self.TIMECOST_NORM_BOUNDS[1] - self.TIMECOST_NORM_BOUNDS[0]) + \
               self.TIMECOST_NORM_BOUNDS[0]

    def _calculate_implicit_rating(self, row: pd.Series, time_threshold_norm: float) -> float:
        """Calculates implicit rating based on user interactions."""
        base_rating = 3 if row["answered"] else 0
        
        if row["timecost"] < time_threshold_norm:
            base_rating -= 1
        else:
            base_rating += row["timecost"]
            
        base_rating += row["bookmarked"]
        return min(max(base_rating, *self.RATING_BOUNDS), self.RATING_BOUNDS[1])

    '''
    Tính toán và lưu implicit ratings
    '''
    def _process_and_upsert_ratings(self, df: pd.DataFrame) -> None:
        """Processes ratings and saves them to database and CSV."""
        # Normalize timecost và tính ratings
        df, time_threshold_norm = self._normalize_timecost(df)
        df["implicit_rating"] = df.apply(
            lambda row: self._calculate_implicit_rating(row, time_threshold_norm),
            axis=1
        )

        total_ratings = len(df)
        
        for idx, row in df.iterrows():
            if idx % self.BATCH_SIZE == 0:
                LOGGER.info(f"WAITING FOR 10 SECONDS...")
                time.sleep(10)
                
            self._upsert_single_rating(row, idx, total_ratings)
            
        LOGGER.info("DONE")

    '''
    Update từng rating một
    '''
    def _upsert_single_rating(self, row: pd.Series, idx: int, total: int) -> None:
        """Upserts a single rating to the database."""
        query = {"user_id": row["user_id"], "cluster": row["item_id"]}
        raw_ratings = self.repo.fetch_all(query)
        existing_rating = raw_ratings[0] if raw_ratings else None
        current_time = TimeUtils.vn_current_time()

        if existing_rating:
            existing_rating.update({
                'rating': row["implicit_rating"],
                'updated_at': current_time,
                'implicit': True
            })
            self.repo.update_one(query, {"$set": existing_rating})
        else:
            new_rating = {
                "user_id": row["user_id"],
                "cluster": row["item_id"],
                "rating": row["implicit_rating"],
                "implicit": True,
                "notionDatabaseId": self.repo.notion_database_id,
                "created_at": current_time,
                "updated_at": current_time
            }
            self.repo.insert_one(new_rating)
            
        LOGGER.info(f"Upserted implicit rating {idx + 1}/{total}...")



    '''
    Upsert rating for API
    '''
    def upsert_ratings(self, data):
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
                raw_ratings = self.repo.fetch_all(query)
                existing_rating = raw_ratings[0] if raw_ratings else None

                # Upsert the rating
                if existing_rating:
                    existing_rating['rating'] = (existing_rating['rating'] + rating) / 2
                    existing_rating['updated_at'] = TimeUtils.vn_current_time()
                    message = f"Updated rating with cluster {cluster} - New Rating: {existing_rating['rating']}"
                    messages["updated"].append(message)

                    # Update the existing rating
                    self.repo.update_one(query, {"$set": existing_rating})
                else:
                    new_rating = {
                        "user_id": user_id,
                        "cluster": cluster,
                        "rating": rating,
                        "notionDatabaseId": self.repo.notion_database_id,
                        "created_at": TimeUtils.vn_current_time(),
                        "updated_at": TimeUtils.vn_current_time()
                    }
                    message = f"Inserted rating with cluster {cluster} - Rating: {rating}"
                    messages["inserted"].append(message)

                    # Insert a new rating
                    self.repo.insert_one(new_rating)

            LOGGER.info(f"Upserted ratings {messages}.")

            return messages
        except Exception as e:
            LOGGER.error(f"Error upserting rating: {e}")


# class RatingService(BaseService):
#     def __init__(self):
#         super().__init__(RatingsRepo())
#         self.process_tracking_repo = self.factory.create_process_tracking()
#         self.reccomendation_logs_repo = self.factory.create_recommendation_logs()
#         self.feature_vectors = self.factory.load_feature_vectors()

#     def update_implicits(self):
#         condition = {"collection_name": "ratings"}
#         process_tracking_repo = ProcessTrackingRepo()
#         tracking_record = process_tracking_repo.fetch_one(condition)
#         if len(tracking_record) == 0:
#             condition.update({"key_value": TimeUtils.vn_current_time()})
#             process_tracking_repo.insert_one(condition)
#             self.init_implicits()
#         else:
#             # self.process_tracking_repo.update_one(
#             #     query=condition,
#             #     update={"$set": {"key_value": TimeUtils.vn_current_time()}}
#             # )
#             last_updated = tracking_record["key_value"]
#             # Update the implicit rating for all users from the last updated time
#             # Get rec_logs from the last updated time
#             raw_rec_logs = self.reccomendation_logs_repo.fetch_all({"created_at": {"$gt": last_updated}})
#             rec_logs_df = self.reccomendation_logs_repo.preprocess_logs(raw_rec_logs)

#             rec_logs_df = rec_logs_df.sort_values("created_at", ascending=False)
#             rec_logs_df = rec_logs_df.drop_duplicates(subset=["user_id", "question_id"], keep="first")
            
#             # Merge the rec_logs_df with the feature vectors' item_id
#             rec_logs_df = pd.merge(rec_logs_df, self.feature_vectors.metadata, left_on="question_id", right_on="question_id",
#                                     how="left")
#             rec_logs_df = rec_logs_df.dropna(subset=["item_id"])
#             rec_logs_df = rec_logs_df[["user_id", "item_id", "answered", "timecost", "bookmarked"]]

#             # Normalize the timecost
#             time_cost_min = rec_logs_df["timecost"].min()
#             time_cost_max = np.quantile(rec_logs_df["timecost"], 0.95)
#             rec_logs_df = rec_logs_df[rec_logs_df["timecost"] <= time_cost_max]
#             target_min, target_max = 0, 1
#             rec_logs_df["timecost"] = (rec_logs_df["timecost"] - time_cost_min) / (
#                         time_cost_max - time_cost_min) * (target_max - target_min) + target_min
#             time_threshold = 1000
#             time_threshold_norm = (time_threshold - time_cost_min) / (time_cost_max - time_cost_min) * (
#                         target_max - target_min) + target_min

#             # Calculate the implicit rating
#             def calculate_implicit_rating(row):
#                 answered = row["answered"]  # True if answered, False if not
#                 timecost = row["timecost"]  # Time cost to answer the question (ms)
#                 bookmarked = row["bookmarked"]  # 1 if bookmarked, 0 if not

#                 base_rating = 3 if answered else 0
#                 if timecost < time_threshold_norm:
#                     base_rating -= 1
#                 else:
#                     base_rating += timecost
#                 base_rating += bookmarked
#                 return min(max(base_rating, 0), 5)
            
#             rec_logs_df["implicit_rating"] = rec_logs_df.apply(calculate_implicit_rating, axis=1)
#             rec_logs_df.to_csv("src/tmp/csv/implicit_ratings_last_updated.csv", index=False)
#             # Upsert the implicit ratings
#             messages = {
#                 "inserted": [],
#                 "updated": []
#             }

#             rec_logs_df_copy = rec_logs_df.copy()
#             total_ratings = len(rec_logs_df_copy)
#             for idx, row in rec_logs_df_copy.iterrows():
#                 if idx % 100 == 0:
#                     LOGGER.info(f"WAITING FOR 10 SECONDS...")
#                     time.sleep(10)

#                 user_id = row["user_id"]
#                 item_id = row["item_id"]
#                 implicit_rating = row["implicit_rating"]
#                 query = {"user_id": user_id, "cluster": item_id}
#                 raw_ratings = self.repo.fetch_all(query)
#                 existing_rating = raw_ratings[0] if raw_ratings else None

#                 # Upsert the rating
#                 if existing_rating:
#                     existing_rating['rating'] = implicit_rating
#                     existing_rating['updated_at'] = TimeUtils.vn_current_time()
#                     existing_rating['implicit'] = True
#                     message = f"Updated rating with cluster {item_id} - New Rating: {existing_rating['rating']}"
#                     messages["updated"].append(message)

#                     # Update the existing rating with rating and implicit flag
#                     self.repo.update_one(query, {"$set": existing_rating})

#                 else:
#                     new_rating = {
#                         "user_id": user_id,
#                         "cluster": item_id,
#                         "rating": implicit_rating,
#                         "implicit": True,
#                         "notionDatabaseId": self.repo.notion_database_id,
#                         "created_at": TimeUtils.vn_current_time(),
#                         "updated_at": TimeUtils.vn_current_time()
#                     }
#                     message = f"Inserted rating with cluster {item_id} - Rating: {implicit_rating}"
#                     messages["inserted"].append(message)

#                     # Insert a new rating
#                     self.repo.insert_one(new_rating)
#                 LOGGER.info(f"Upserted implicit rating {idx + 1}/{total_ratings}...")

#             LOGGER.info("DONE")

#     def init_implicits(self):
#         try:
#             # Update the implicit rating for all users
#             raw_rec_logs = self.reccomendation_logs_repo.fetch_all()
#             rec_logs_df = self.reccomendation_logs_repo.preprocess_logs(raw_rec_logs)

#             # Reduce the dataframe to unique user_id and question_id with the latest created_at
#             rec_logs_df = rec_logs_df.sort_values("created_at", ascending=False)
#             rec_logs_df = rec_logs_df.drop_duplicates(subset=["user_id", "question_id"], keep="first")


#             print(rec_logs_df)
#             print(self.feature_vectors.metadata)

#             # Merge the rec_logs_df with the feature vectors' item_id
#             rec_logs_df = pd.merge(rec_logs_df, self.feature_vectors.metadata, left_on="question_id", right_on="question_id",
#                                     how="left")
#             rec_logs_df = rec_logs_df.dropna(subset=["item_id"])
#             rec_logs_df = rec_logs_df[["user_id", "item_id", "answered", "timecost", "bookmarked"]]

#             # Normalize the timecost
#             time_cost_min = rec_logs_df["timecost"].min()
#             time_cost_max = np.quantile(rec_logs_df["timecost"], 0.95)
#             rec_logs_df = rec_logs_df[rec_logs_df["timecost"] <= time_cost_max]
#             target_min, target_max = 0, 1
#             rec_logs_df["timecost"] = (rec_logs_df["timecost"] - time_cost_min) / (
#                         time_cost_max - time_cost_min) * (target_max - target_min) + target_min
#             time_threshold = 1000
#             time_threshold_norm = (time_threshold - time_cost_min) / (time_cost_max - time_cost_min) * (
#                         target_max - target_min) + target_min

#             # Calculate the implicit rating
#             def calculate_implicit_rating(row):
#                 answered = row["answered"]  # True if answered, False if not
#                 timecost = row["timecost"]  # Time cost to answer the question (ms)
#                 bookmarked = row["bookmarked"]  # 1 if bookmarked, 0 if not

#                 base_rating = 3 if answered else 0
#                 if timecost < time_threshold_norm:
#                     base_rating -= 1
#                 else:
#                     base_rating += timecost
#                 base_rating += bookmarked
#                 return min(max(base_rating, 0), 5)

#             os.makedirs("src/tmp/csv", exist_ok=True)
#             rec_logs_df["implicit_rating"] = rec_logs_df.apply(calculate_implicit_rating, axis=1)
#             rec_logs_df.to_csv("src/tmp/csv/implicit_ratings.csv", index=False)

#             # Upsert the implicit ratings
#             messages = {
#                 "inserted": [],
#                 "updated": []
#             }

#             rec_logs_df_copy = rec_logs_df.copy()
#             total_ratings = len(rec_logs_df_copy)
#             for idx, row in rec_logs_df_copy.iterrows():
#                 if idx % 100 == 0:
#                     LOGGER.info(f"WAITING FOR 10 SECONDS...")
#                     time.sleep(10)

#                 user_id = row["user_id"]
#                 item_id = row["item_id"]
#                 implicit_rating = row["implicit_rating"]
#                 query = {"user_id": user_id, "cluster": item_id}
#                 raw_ratings = self.repo.fetch_all(query)
#                 existing_rating = raw_ratings[0] if raw_ratings else None

#                 # Upsert the rating
#                 if existing_rating:
#                     existing_rating['rating'] = implicit_rating
#                     existing_rating['updated_at'] = TimeUtils.vn_current_time()
#                     existing_rating['implicit'] = True
#                     message = f"Updated rating with cluster {item_id} - New Rating: {existing_rating['rating']}"
#                     messages["updated"].append(message)

#                     # Update the existing rating with rating and implicit flag
#                     self.repo.update_one(query, {"$set": existing_rating})

#                 else:
#                     new_rating = {
#                         "user_id": user_id,
#                         "cluster": item_id,
#                         "rating": implicit_rating,
#                         "implicit": True,
#                         "notionDatabaseId": self.repo.notion_database_id,
#                         "created_at": TimeUtils.vn_current_time(),
#                         "updated_at": TimeUtils.vn_current_time()
#                     }
#                     message = f"Inserted rating with cluster {item_id} - Rating: {implicit_rating}"
#                     messages["inserted"].append(message)

#                     # Insert a new rating
#                     self.repo.insert_one(new_rating)
#                 LOGGER.info(f"Upserted implicit rating {idx + 1}/{total_ratings}...")

#             LOGGER.info("DONE")

#         except Exception as e:
#             LOGGER.error(f"Error initializing implicit rating: {e}")
#             raise e

            raise e