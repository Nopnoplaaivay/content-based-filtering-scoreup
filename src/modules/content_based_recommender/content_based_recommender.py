import json
import random
import numpy as np

from src.db import QuestionsCollection
from src.modules.items_map import ItemsMap
from src.models.content_based import ContentBasedModel
from src.utils.logger import LOGGER

class ContentBasedRecommender:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.model = ContentBasedModel()
        self.model.load_weights()
        self.user_map = self.load_user_map()

    def recommend(self, user_id, max_exercises=5):
        # Get items map
        cluster_map = ItemsMap().get_cluster_map()

        user_id_encoded = self.user_map[user_id]
        user_index = user_id_encoded - 1
        predicted_ratings = self.model.Yhat[:, user_index]

        # Get descending order of predicted ratings index
        recommendations = {
            "exercise_ids": [],
            "clusters": [],
            "message": None,
        }

        clusters = np.argsort(predicted_ratings)[::-1]
        for cluster in clusters:
            cluster_str = str(cluster)
            if len(recommendations["exercise_ids"]) >= max_exercises:
                break
            if cluster_str in cluster_map:
                recommendations["clusters"].append(int(cluster_str))
                exercises = cluster_map[cluster_str]["question_id"]
                random.shuffle(exercises)
                for exercise in exercises:
                    if len(recommendations["exercise_ids"]) < max_exercises:
                        # Fetch exercise from database
                        exercise = QuestionsCollection().fetch_question(exercise)
                        recommendations["exercise_ids"].append(exercise)
                    else:
                        break

        # messages = [
        #     "These questions connect to multiple topics you’ve studied before, helping you see the bigger picture and build integrated knowledge."
        #     , "Based on your learning history and preferences, these questions aligns well with your strengths and areas of improvement, offering a perfect next step."
        #     , "These questions is a great way to reinforce your understanding of a key concept, helping you retain and apply knowledge more effectively."
        #     , "This question aligns closely with topics you’ve shown interest in, ensuring the learning experience remains both challenging and motivating."
        #     , "This question is slightly more advanced and explores related concepts to those you've already mastered. It’s chosen to push your boundaries and keep your learning engaging."
        # ]

        messages = [
            "Những câu hỏi này kết nối với nhiều chủ đề bạn đã học trước đây, giúp bạn nhìn thấy bức tranh toàn diện và xây dựng kiến thức tích hợp.",
            "Dựa trên lịch sử học tập và sở thích của bạn, những câu hỏi này phù hợp với thế mạnh và những lĩnh vực cần cải thiện của bạn, mang đến bước tiếp theo hoàn hảo.",
            "Những câu hỏi này là cách tuyệt vời để củng cố hiểu biết về một khái niệm chính, giúp bạn ghi nhớ và áp dụng kiến thức hiệu quả hơn.",
            "Câu hỏi này phù hợp chặt chẽ với các chủ đề bạn đã thể hiện sự quan tâm, đảm bảo trải nghiệm học tập vừa mang tính thách thức vừa đầy động lực.",
            "Câu hỏi này hơi nâng cao và khám phá các khái niệm liên quan đến những gì bạn đã thành thạo. Nó được chọn để thúc đẩy giới hạn của bạn và giữ cho việc học luôn hấp dẫn."
        ]

        if recommendations:
            recommendations["message"] = (f"{random.choice(messages)}")
        else:
            recommendations["message"] = (
                f"Hi User {user_id}, we currently have no recommendations for you. "
                "Please try answering more questions to generate new suggestions!"
            )

        return recommendations

    def load_user_map(self):
        try:
            with open('src/tmp/users/user_map.json') as f:
                user_map = json.load(f)
            return user_map
        except Exception as e:
            LOGGER.error(f"Error loading user map: {e}")
            LOGGER.info("Please call train model api first (POST /train) to generate user map.")
            return None
