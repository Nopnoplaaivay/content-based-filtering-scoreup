import pandas as pd
import random

from src.db import Logs, Questions, Concepts, Users
from src.modules.items_map import ItemsMap
from src.modules.spaced_repetition_recommender.leitner_spaced_repetition import LeitnerSpacedRepetition

class LSRRecommender:

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.logs = Logs(notion_database_id=notion_database_id)
        self.questions = Questions(notion_database_id=notion_database_id)
        self.concepts = Concepts(notion_database_id=notion_database_id)
        self.users = Users()

    def recommend(self, user_id, max_exercises=10):
        # Get items map
        questions_map = ItemsMap().get_question_map()
        cluster_map = ItemsMap().get_cluster_map()

        # Preprocess logs
        self.logs_df = self.logs.preprocess_logs(raw_logs=self.logs.fetch_logs_by_user(user_id))
        self.logs_df['cluster'] = self.logs_df['question_id'].map(questions_map)
        self.logs_df.dropna(subset=['cluster'], inplace=True)
        self.logs_df['cluster'] = self.logs_df['cluster'].astype(int)

        cols = ['user_id', 'cluster', 'rec_score', 'message']
        Y = pd.DataFrame(columns=cols)
        group_user_cluster = self.logs_df.groupby(['cluster'])

        rows = []
        for cluster, group_df in group_user_cluster:
            rec_score, message = LeitnerSpacedRepetition.leitner_score(group_df)
            rows.append([user_id, cluster, rec_score, message])

        Y = pd.concat([Y, pd.DataFrame(rows, columns=cols)], ignore_index=True)
        Y = Y.sort_values(by='rec_score', ascending=False)

        clusters = Y['cluster'].values
        message = Y['message'].iloc[0]
        
        # metadata
        recommendations = {
            "exercise_ids": [],
            "knowledge_concepts": [],
            "clusters": [],
            "message": None,
        }
        knowledge_concepts = set()

        for cluster in clusters:
            cluster_str = str(cluster[0])
            if len(recommendations["exercise_ids"]) >= max_exercises:
                break
            if cluster_str in cluster_map:
                recommendations["clusters"].append(int(cluster_str))
                exercises = cluster_map[cluster_str]["question_id"]
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
        if recommendations["exercise_ids"]:
            hi_message = f"{self.users.fetch_user_info(user_id=user_id).get('name')} Ơi!"
            concepts_message = ", ".join(recommendations["knowledge_concepts"])
            if message == "NEVER_ATTEMPTED_MESSAGE":
                recommendations["message"] = f"{hi_message} Hãy thử sức với những câu hỏi thuộc các chủ đề: {concepts_message} mà cậu chưa từng gặp trên ScoreUp nhé"
            elif message == "FREQUENTLY_WRONG_MESSAGE":
                recommendations["message"] = f"{hi_message} Đây là các chủ đề cậu thường xuyên trả lời sai: {concepts_message}. Hãy luyện tập lại nhé!"
            elif message == "OCCASIONALLY_WRONG_MESSAGE":
                recommendations["message"] = f"{hi_message} Cậu thi thoảng gặp chút khó khăn khi trả lời câu hỏi thuộc chủ đề: {concepts_message}. Cùng ScoreUp ôn tập lại nhé!"
            elif message == "CORRECT_MESSAGE":
                recommendations["message"] = f"{hi_message} Cậu đã thể hiện khá tốt trong chủ đề: {concepts_message}. Tuy nhiên việc ôn luyện lại là cần thiết để củng cố kiến thức"
            else:
                recommendations["message"] = f"{hi_message} Có vẻ cậu đã rất thành thạo trong lĩnh vực: {concepts_message}. Để duy trì kiến thức, cùng ScoreUp ôn lại chút nhé!"
        else:
            recommendations["message"] = (
                f"Hi User {user_id}, we currently have no recommendations for you. "
                "Please try answering more questions to generate new suggestions!"
            )

        return recommendations