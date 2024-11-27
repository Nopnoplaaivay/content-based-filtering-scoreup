import random

from src.db import Logs, Questions
from src.modules.items_map import ItemsMap

class LLRRecommender:

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = Questions()
        self.logs = Logs()

    def recommend(self, user_id, max_exercises=10):
        questions_map = ItemsMap().get_question_map()
        cluster_map = ItemsMap().get_cluster_map()

        self.logs_df = self.logs.preprocess_logs(raw_logs=self.logs.fetch_logs_by_user(user_id))
        self.logs_df['cluster'] = self.logs_df['question_id'].map(questions_map)
        self.logs_df.dropna(subset=['cluster'], inplace=True)
        self.logs_df['cluster'] = self.logs_df['cluster'].astype(int)

        # Xác định cấp độ người học
        user_level = self.logs.get_user_level(user_id)

        messages = {
            "Beginner": "Chúng tôi đã chọn những câu hỏi cấp độ Cơ bản để giúp bạn bắt đầu!",
            "Intermediate": "Chúng tôi đã chọn những câu hỏi cấp độ Trung bình để giúp bạn cải thiện kỹ năng!",
            "Advanced": "Chúng tôi đã chọn những câu hỏi cấp độ Nâng cao để thử thách kiến thức của bạn!"
        }

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
                        exercise = self.questions.fetch_one(id=exercise)
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
        if user_level == 'Beginner' and cluster_difficulty <= 0.33:
            return True
        if user_level == 'Intermediate' and 0.34 <= cluster_difficulty <= 0.66:
            return True
        if user_level == 'Advanced' and cluster_difficulty > 0.66:
            return True
        return False