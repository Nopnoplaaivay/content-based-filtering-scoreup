import random

from src.db import Logs, Questions, Concepts, Users
from src.modules.items_map import ItemsMap

class LLRRecommender:

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = Questions(notion_database_id=notion_database_id)
        self.logs = Logs(notion_database_id=notion_database_id)
        self.concepts = Concepts(notion_database_id=notion_database_id)
        self.users = Users()

    def recommend(self, user_id, max_exercises=10):
        questions_map = ItemsMap().get_question_map()
        cluster_map = ItemsMap().get_cluster_map()

        self.logs_df = self.logs.preprocess_logs(raw_logs=self.logs.fetch_logs_by_user(user_id))
        self.logs_df['cluster'] = self.logs_df['question_id'].map(questions_map)
        self.logs_df.dropna(subset=['cluster'], inplace=True)
        self.logs_df['cluster'] = self.logs_df['cluster'].astype(int)

        # Xác định cấp độ người học
        user_level = self.logs.get_user_level(user_id)

        recommendations = {
            "exercise_ids": [],
            "knowledge_concepts": [],
            "clusters": [],
            "message": None,
        }

        knowledge_concepts = set()
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
                        concept = exercise["properties"]["tags"]["multi_select"][0]["name"]
                        knowledge_concepts.add(concept)
                        recommendations["exercise_ids"].append(exercise)
                    else:
                        break


        recommendations["knowledge_concepts"] = [self.concepts.fetch_one(id=concept)["title"] for concept in list(knowledge_concepts)]
        hi_message = f"{self.users.fetch_user_info(user_id=user_id).get('name')} Ơi!"
        concepts_message = ", ".join(recommendations["knowledge_concepts"])
        
        messages = {
            "Beginner": f"{hi_message} ScoreUp đã chọn những câu hỏi cấp độ Cơ bản thuộc chủ để {concepts_message} để giúp cậu làm quen với kiến thức mới nhé!",
            "Intermediate": f"{hi_message} ScoreUp đã chọn những câu hỏi cấp độ Khá thuộc chủ để {concepts_message} để giúp cậu cải thiện kỹ năng nhé!",
            "Advanced": f"{hi_message} ScoreUp đã chọn những câu hỏi cấp độ Nâng cao thuộc chủ để {concepts_message} để thử thách kiến thức của cậu! Hãy thử sức nhé!"
        }

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