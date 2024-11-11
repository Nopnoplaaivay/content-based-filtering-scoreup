import json
import re
import numpy as np
import pandas as pd

from src.db.questions import QuestionsCollection
from src.models.clustering import QuestionClustering   
from src.utils.encode_utils import EncodeQuestionsUtils

def combine_features(row):
    return np.append(row['concept_embedding'], row['difficulty'])

def clean_and_convert_embedding(embedding_str):
    cleaned_str = re.sub(r'[\[\]]', '', embedding_str)
    return np.fromstring(cleaned_str, sep=' ')


class QuestionsMap:
    def __init__(self):
        
        self.encoder = EncodeQuestionsUtils()
        self.clustering_model = QuestionClustering()

    def get_map(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        questions_collection = QuestionsCollection(notion_database_id=notion_database_id)
        raw_questions = questions_collection.fetch_all_questions()
        questions_df = questions_collection.preprocess_questions(raw_questions=raw_questions)
        
        # Prepare X
        X = self.encoder.encode(questions_df)
        self.clustering_model.get_optimal_clusters(X)
        self.clustering_model.fit(X)

        # Predict cluster
        cluster_labels = self.clustering_model.predict(X)
        questions_df['cluster'] = cluster_labels

        questions_df.to_csv(f"src/data/{notion_database_id}_questions_cluster.csv", index=False)

        question_map = questions_df.set_index('question_id')['cluster'].to_dict()

        # Create feature vector for each cluster
        temp_df = questions_df.drop(columns=['question_id', 'concept', 'content'])
        temp_df['concept_embedding'] = temp_df['concept_embedding'].apply(lambda x: np.array(x, dtype=float))
        temp_df['difficulty'] = temp_df['difficulty'].astype(float)

        temp_df['combined_features'] = temp_df.apply(combine_features, axis=1)
        print(type(temp_df['combined_features']))
        print(type(temp_df['combined_features'].iloc[0]))
        print(temp_df['combined_features'].iloc[0])

        cluster_features = temp_df.groupby('cluster')['combined_features'].apply(lambda x: np.mean(np.stack(x), axis=0)).reset_index()
        print(cluster_features.head())

        # Convert the combined features back to separate columns for easier readability
        combined_features_df = pd.DataFrame(cluster_features['combined_features'].tolist(), index=cluster_features['cluster'])
        combined_features_df.columns = [f'feature_{i}' for i in range(combined_features_df.shape[1])]

        # Concatenate the cluster column with the combined features
        cluster_features = pd.concat([cluster_features['cluster'], combined_features_df], axis=1)

        # Create the cluster_map
        cluster_map = {}
        for cluster in cluster_features['cluster']:
            cluster_str = str(cluster)
            features_vector = cluster_features[cluster_features['cluster'] == cluster].iloc[:, 1:].values.flatten().tolist()
            question_ids = questions_df[questions_df['cluster'] == cluster]['question_id'].tolist()
            cluster_map[cluster_str] = {
                "features_vector": features_vector,
                "question_id": question_ids
            }

        with open(f"src/data/{notion_database_id}_cluster_map.json", "w") as f:
            json.dump(cluster_map, f)

        question_map = questions_df.set_index('question_id')['cluster'].to_dict()
        with open(f"src/data/{notion_database_id}_question_map.json", "w") as f:
            json.dump(question_map, f)

        return question_map, cluster_map