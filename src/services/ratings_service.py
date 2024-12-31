import numpy as np
import pandas as pd
import os
import time

from src.repositories import RatingsRepo, ProcessTrackingRepo
from src.services.base_service import BaseService
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER


class RatingService(BaseService):
    def __init__(self):
        super().__init__(RatingsRepo())

    def update_implicits(self):
        condition = {"collection_name": "ratings"}
        process_tracking_repo = ProcessTrackingRepo()
        tracking_record = process_tracking_repo.fetch_one(condition)
        if len(tracking_record) == 0:
            condition.update({"key_value": TimeUtils.vn_current_time()})
            process_tracking_repo.insert_one(condition)
            self.init_implicits()
        else:
            last_updated = tracking_record["key_value"]
            # if TimeUtils.vn_current_time() - last_updated > 86400:
            process_tracking_repo.update_one(
                query=condition,
                update={"$set": {"key_value": TimeUtils.vn_current_time()}}
            )


    def init_implicits(self):
        try:
            # Update the implicit rating for all users
            fv = self.factory.load_feature_vectors()
            rec_logs = self.factory.create_recommendation_logs()
            raw_rec_logs = rec_logs.fetch_all()
            rec_logs_df = rec_logs.preprocess_logs(raw_rec_logs)

            # Reduce the dataframe to unique user_id and question_id with the latest created_at
            rec_logs_df = rec_logs_df.sort_values("created_at", ascending=False)
            rec_logs_df = rec_logs_df.drop_duplicates(subset=["user_id", "question_id"], keep="first")

            # Merge the rec_logs_df with the feature vectors' item_id
            rec_logs_df = pd.merge(rec_logs_df, fv.metadata, left_on="question_id", right_on="question_id",
                                    how="left")
            rec_logs_df = rec_logs_df.dropna(subset=["item_id"])
            rec_logs_df = rec_logs_df[["user_id", "item_id", "answered", "timecost", "bookmarked"]]

            # Normalize the timecost
            time_cost_min = rec_logs_df["timecost"].min()
            time_cost_max = np.quantile(rec_logs_df["timecost"], 0.95)
            rec_logs_df = rec_logs_df[rec_logs_df["timecost"] <= time_cost_max]
            target_min, target_max = 0, 1
            rec_logs_df["timecost"] = (rec_logs_df["timecost"] - time_cost_min) / (
                        time_cost_max - time_cost_min) * (target_max - target_min) + target_min
            time_threshold = 1000
            time_threshold_norm = (time_threshold - time_cost_min) / (time_cost_max - time_cost_min) * (
                        target_max - target_min) + target_min

            # Calculate the implicit rating
            def calculate_implicit_rating(row):
                answered = row["answered"]  # True if answered, False if not
                timecost = row["timecost"]  # Time cost to answer the question (ms)
                bookmarked = row["bookmarked"]  # 1 if bookmarked, 0 if not

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

            rec_logs_df_copy = rec_logs_df.copy()
            total_ratings = len(rec_logs_df_copy)
            for idx, row in rec_logs_df_copy.iterrows():
                if idx % 100 == 0:
                    LOGGER.info(f"WAITING FOR 10 SECONDS...")
                    time.sleep(10)

                user_id = row["user_id"]
                item_id = row["item_id"]
                implicit_rating = row["implicit_rating"]
                query = {"user_id": user_id, "cluster": item_id}
                raw_ratings = self.repo.fetch_all(query)
                existing_rating = raw_ratings[0] if raw_ratings else None

                # Upsert the rating
                if existing_rating:
                    existing_rating['rating'] = implicit_rating
                    existing_rating['updated_at'] = TimeUtils.vn_current_time()
                    existing_rating['implicit'] = True
                    message = f"Updated rating with cluster {item_id} - New Rating: {existing_rating['rating']}"
                    messages["updated"].append(message)

                    # Update the existing rating with rating and implicit flag
                    self.repo.update_one(query, {"$set": existing_rating})

                else:
                    new_rating = {
                        "user_id": user_id,
                        "cluster": item_id,
                        "rating": implicit_rating,
                        "implicit": True,
                        "notionDatabaseId": self.repo.notion_database_id,
                        "created_at": TimeUtils.vn_current_time(),
                        "updated_at": TimeUtils.vn_current_time()
                    }
                    message = f"Inserted rating with cluster {item_id} - Rating: {implicit_rating}"
                    messages["inserted"].append(message)

                    # Insert a new rating
                    self.repo.insert_one(new_rating)
                LOGGER.info(f"Upserted implicit rating {idx + 1}/{total_ratings}...")

            LOGGER.info("DONE")

        except Exception as e:
            LOGGER.error(f"Error initializing implicit rating: {e}")
            raise e

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
            raise e