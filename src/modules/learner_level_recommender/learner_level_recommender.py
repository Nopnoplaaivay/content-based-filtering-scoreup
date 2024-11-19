import pandas as pd
import random
import json

from src.db import LogsCollection, QuestionsCollection
from src.modules.items_map import ItemsMap

class LLRRecommender:

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.logs_collection = LogsCollection(notion_database_id=notion_database_id)
        self.questions_collection = QuestionsCollection()

    def recommend(self, user_id, max_exercises=10):
        # Get items map
        questions_map = ItemsMap().get_question_map()
        cluster_map = ItemsMap().get_cluster_map()

        # Preprocess logs
        self.logs_df = self.logs_collection.preprocess_logs(raw_logs=self.logs_collection.fetch_logs_by_user(user_id))
        self.logs_df['cluster'] = self.logs_df['question_id'].map(questions_map)
        self.logs_df.dropna(subset=['cluster'], inplace=True)
        self.logs_df['cluster'] = self.logs_df['cluster'].astype(int)

        # Xác định cấp độ người học
        user_level = self.logs_collection.cal_user_level(user_id)

        messages = {
            "Beginner": "We picked these Beginner level questions for you to help you get started!",
            "Intermediate": "We picked these Intermediate level questions for you to help you improve your skills!",
            "Advanced": "We picked these Advanced level questions for you to challenge your knowledge!"
        }

        # Gợi ý câu hỏi phù hợp
        recommendations = {
            "exercise_ids": [],
            "clusters": [],
            "message": None,
        }

        clusters = cluster_map.keys()
        for cluster in clusters:
            cluster_str = str(cluster)
            if len(recommendations["exercise_ids"]) >= max_exercises:
                break
            if cluster_str in cluster_map:
                exercises = cluster_map[cluster_str]["question_id"]
                filtered_exercises = self.is_suitable(user_level, cluster_map[cluster_str]["cluster_difficulty"])
                if not filtered_exercises:
                    continue

                recommendations["clusters"].append(int(cluster_str))
                random.shuffle(exercises)
                for exercise in exercises:
                    if len(recommendations["exercise_ids"]) < max_exercises:
                        exercise = self.questions_collection.fetch_question(exercise)
                        recommendations["exercise_ids"].append(exercise)
                    else:
                        break


        if recommendations["exercise_ids"]:
            recommendations["message"] = (f"{messages[user_level]}")
        else:
            recommendations["message"] = (
                f"Hi User {user_id}, we currently have no recommendations for you. "
                "Please try answering more questions to generate new suggestions!"
            )
        
        return recommendations

    @staticmethod
    def is_suitable(user_level, cluster_difficulty):
        """
        Kiểm tra xem câu hỏi có phù hợp với cấp độ người học hay không.

        Args:
            question_id (int): ID câu hỏi.
            user_level (str): Cấp độ của người học ('Beginner', 'Intermediate', 'Advanced').
            cluster_difficulty (dict): Map độ khó của các câu hỏi.

        Returns:
            bool: True nếu câu hỏi phù hợp, False nếu không.
        """
        if user_level == 'Beginner' and cluster_difficulty <= 0.33:
            return True
        if user_level == 'Intermediate' and 0.34 <= cluster_difficulty <= 0.66:
            return True
        if user_level == 'Advanced' and cluster_difficulty > 0.66:
            return True
        return False