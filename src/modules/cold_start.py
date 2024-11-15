import pandas as pd
import json
import random

from src.modules.rec_score import RecScore
from src.db import LogsDB


with open("src/data/question_map.json", "r") as f:
    questions_map = json.load(f)

with open("src/data/cluster_map.json", "r") as f:
    cluster_map = json.load(f)

class ColdStart:
    global questions_map
    global cluster_map

    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.logs_collection = LogsDB(notion_database_id=notion_database_id)

    def recommend(self, user_id, max_exercises=10):
        self.logs_df = self.logs_collection.preprocess_logs(raw_logs=self.logs_collection.fetch_logs_by_user(user_id))

        self.logs_df['cluster'] = self.logs_df['question_id'].map(questions_map)
        self.logs_df.dropna(subset=['cluster'], inplace=True)
        self.logs_df['cluster'] = self.logs_df['cluster'].astype(int)

        cols = ['user_id', 'cluster', 'rec_score']
        Y = pd.DataFrame(columns=cols)
        group_user_cluster = self.logs_df.groupby(['cluster'])

        rows = []
        for cluster, group_df in group_user_cluster:
            rec_score = RecScore(group_df).leitner_score
            rows.append([user_id, cluster, rec_score])

        Y = pd.concat([Y, pd.DataFrame(rows, columns=cols)], ignore_index=True)
        Y = Y.sort_values(by='rec_score', ascending=False)

        clusters = Y['cluster'].values
        recommendations = []

        for cluster in clusters:

            cluster_str = str(cluster[0]) 
            if cluster_str in cluster_map:
                exercises = cluster_map[cluster_str]
                random.shuffle(exercises)
                for exercise in exercises:
                    if len(recommendations) < max_exercises:
                        recommendations.append(exercise)
                    else:
                        break

        print(f"Recommendations for user {user_id}:")
        print(recommendations)
