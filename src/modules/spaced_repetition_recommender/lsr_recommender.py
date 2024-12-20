import pandas as pd
import random
import numpy as np

from src.db import Logs, Questions, Concepts, Users
from src.modules.feature_vectors import FeatureVectors
from src.modules.spaced_repetition_recommender.leitner_spaced_repetition import LeitnerSpacedRepetition

class LSRRecommender:

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.questions = Questions(notion_database_id=notion_database_id)
        self.concepts = Concepts(notion_database_id=notion_database_id)
        self.logs = Logs(notion_database_id=notion_database_id)
        self.users = Users()

    def recommend(self, user_id, max_exercises=10):
        fv = FeatureVectors()
        fv.load_fv()
        priority_df = fv.metadata
        priority_df['f_missed'] = -1

        # Preprocess logs
        raw_logs = self.logs.fetch_logs_by_user(user_id)
        self.logs_df = self.logs.preprocess_logs(raw_logs=raw_logs)
        
        # mapping to item_id in fv.metadata through question_id
        self.logs_df = self.logs_df.merge(fv.metadata[['question_id', 'item_id']], left_on='question_id', right_on='question_id', how='left')
        self.logs_df.dropna(subset=['item_id'], inplace=True)
        self.logs_df['item_id'] = self.logs_df['item_id'].astype(int)

        # self.logs_df.to_csv('logs.csv')
        # Calculate Fmiss = 4*M_n + 2*M_n-1 + M_n-2 + M_before
        # where:

        # M_i = 1 if the user has a "missed" at the i-th position, otherwise M_i = 0.
        # M_before (Missed before) = 1 if there is at least a "missed" in [M_n-3 ... M_0], otherwise M_before = 0 (and if n < 3, then M_before = M_0).

        # The value of F(missed) is ranged from -1 to 8 (-1 is the default value when n = 0).
        for item, group_df in self.logs_df.groupby('item_id'):
            group_df.sort_values(by='created_at', ascending=True, inplace=True)
            m_values = [1 if log['score'] == 0 else 0 for _, log in group_df.iterrows()]
            
            if len(m_values) == 0:
                F_missed = -1
            else:
                m_before = 1 if any(m_values[:-3]) else (m_values[0] if len(m_values) < 3 else 0)
                F_missed = sum([4 * m_values[-1], 2 * m_values[-2] if len(m_values) > 1 else 0, m_values[-3] if len(m_values) > 2 else 0, m_before])
            
            priority_df.loc[priority_df['item_id'] == item, 'f_missed'] = F_missed
            priority_list = priority_df['f_missed'].values

        recommendations = {
            "exercise_ids": [],
            "knowledge_concepts": [],
            "clusters": [],
            "message": None,
        }
        
        knowledge_concepts = set()
        max_f_missed = max(priority_list)
        items = np.argsort(priority_list)[::-1]
        for item in items:
            if len(recommendations["exercise_ids"]) >= max_exercises:
                break
            if item < len(priority_df):
                recommendations["clusters"].append(int(item))
                question_id = priority_df.iloc[item]["question_id"]
                exercise = self.questions.fetch_one(id=question_id)
                concept = exercise["properties"]["tags"]["multi_select"][0]["name"]
                knowledge_concepts.add(concept)
                recommendations["exercise_ids"].append(exercise)

        recommendations["knowledge_concepts"] = [self.concepts.fetch_one(id=concept)["title"] for concept in list(knowledge_concepts)]
        hi_message = f"{self.users.fetch_user_info(user_id=user_id).get('name')} Ơi!"

        if recommendations["exercise_ids"]:
            concepts_message = ", ".join(recommendations["knowledge_concepts"])
            if max_f_missed == -1:
                recommendations["message"] = f"{hi_message} Hãy thử sức với những câu hỏi thuộc các chủ đề: {concepts_message} mà cậu chưa từng gặp trên ScoreUp nhé"
            elif max_f_missed < 4:
                recommendations["message"] = f"{hi_message} Đây là các chủ đề cậu thường xuyên trả lời sai: {concepts_message}. Hãy luyện tập lại nhé!"
            elif max_f_missed < 8:
                recommendations["message"] = f"{hi_message} Cậu đôi lúc gặp chút khó khăn khi trả lời câu hỏi thuộc chủ đề: {concepts_message}. Cùng ScoreUp ôn tập lại nhé!"
            elif max_f_missed == 8:
                recommendations["message"] = f"{hi_message} Đây là chủ đề cậu gặp nhiều khó khăn và trả lời sai nhiều nhất: {concepts_message}. Hãy cố gắng hơn nữa nhé!"
        else:
            recommendations["message"] = (
                f"{hi_message}, ScoreUp Tips! Hãy luyện tập thêm bài tập để có thể mở khóa chức năng gợi ý nha!"
            )

        return recommendations