import pandas as pd
import random

from src.db import Logs, Questions
from src.modules.items_map import ItemsMap
from src.modules.spaced_repetition_recommender.leitner_spaced_repetition import LeitnerSpacedRepetition

class LSRRecommender:

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.logs = Logs(notion_database_id=notion_database_id)
        self.questions = Questions(notion_database_id=notion_database_id)

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
        recommendations = {
            "exercise_ids": [],
            "clusters": [],
            "message": None,
        }

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
                        recommendations["exercise_ids"].append(exercise)
                    else:
                        break

        if recommendations["exercise_ids"]:
            recommendations["message"] = (f"{message}")
        else:
            recommendations["message"] = (
                f"Hi User {user_id}, we currently have no recommendations for you. "
                "Please try answering more questions to generate new suggestions!"
            )

        return recommendations