import json
import re
import os
import numpy as np
import pandas as pd

from src.db.questions import QuestionsCollection
from src.models.questions_cluster import QuestionClustering   
from src.utils.encode_utils import EncodeQuestionsUtils
from src.utils.logger import LOGGER

def combine_features(row):
    return np.append(row['concept_embedding'], row['difficulty'])

def clean_and_convert_embedding(embedding_str):
    cleaned_str = re.sub(r'[\[\]]', '', embedding_str)
    return np.fromstring(cleaned_str, sep=' ')

class ItemsMap:
    def __init__(self):
        
        self.encoder = EncodeQuestionsUtils()
        self.clustering_model = QuestionClustering()

    def get_cluster_map(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        try:
            if os.path.exists(f"src/tmp/mapping/{notion_database_id}_cluster_map.json"):
                with open(f"src/tmp/mapping/{notion_database_id}_cluster_map.json", "r") as f:
                    cluster_map = json.load(f)
                return cluster_map
            else:
                LOGGER.error(f"Cluster map not found for {notion_database_id}")
                self.gen_qcmap(notion_database_id=notion_database_id)
                with open(f"src/tmp/mapping/{notion_database_id}_cluster_map.json", "r") as f:
                    cluster_map = json.load(f)
                return cluster_map
        except Exception as e:
            LOGGER.error(f"Error fetching cluster map: {e}")
            return None

    def get_question_map(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        try:
            if os.path.exists(f"src/tmp/mapping/{notion_database_id}_question_map.json"):
                with open(f"src/tmp/mapping/{notion_database_id}_question_map.json", "r") as f:
                    question_map = json.load(f)
                return question_map
            else:
                LOGGER.error(f"Question map not found for {notion_database_id}")
                self.gen_qcmap(notion_database_id=notion_database_id)
                with open(f"src/tmp/mapping/{notion_database_id}_question_map.json", "r") as f:
                    question_map = json.load(f)
                return question_map
        except Exception as e:
            LOGGER.error(f"Error fetching question map: {e}")
            return None

    def get_features_vector(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        try:
            if os.path.exists(f"src/tmp/features_vector/{notion_database_id}_features_vector.json"):
                with open(f"src/tmp/features_vector/{notion_database_id}_features_vector.json", "r") as f:
                    features_vector = json.load(f)
                # Transform features vector to numpy array
                features_vector = np.array(list(features_vector.values()))
                return features_vector
            else:
                LOGGER.error(f"Features vector not found for {notion_database_id}")
                self.gen_qcmap(notion_database_id=notion_database_id)
                with open(f"src/tmp/features_vector/{notion_database_id}_features_vector.json", "r") as f:
                    features_vector = json.load(f)
                features_vector = np.array(list(features_vector.values()))
                return features_vector
        except Exception as e:
            LOGGER.error(f"Error fetching features vector: {e}")
            return None

    def gen_qcmap(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
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

        # question_map = questions_df.set_index('question_id')['cluster'].to_dict()

        # Create feature vector for each cluster
        temp_df = questions_df.drop(columns=['question_id', 'concept', 'content'])
        temp_df['concept_embedding'] = temp_df['concept_embedding'].apply(lambda x: np.array(x, dtype=float))
        temp_df['difficulty'] = temp_df['difficulty'].astype(float)

        temp_df['combined_features'] = temp_df.apply(combine_features, axis=1)

        cluster_features = temp_df.groupby('cluster')['combined_features'].apply(lambda x: np.mean(np.stack(x), axis=0)).reset_index()

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

        # Generate features vector
        features_vector = {}
        for key, value in cluster_map.items():
            features_vector[key] = value["features_vector"]

        # Save cluster_map, question_map in json format
        os.makedirs('src/tmp/mapping', exist_ok=True)
        with open(f"src/tmp/mapping/{notion_database_id}_cluster_map.json", "w") as f:
            json.dump(cluster_map, f)

        question_map = questions_df.set_index('question_id')['cluster'].to_dict()
        with open(f"src/tmp/mapping/{notion_database_id}_question_map.json", "w") as f:
            json.dump(question_map, f)

        # Save features vector
        os.makedirs('src/tmp/features_vector', exist_ok=True)
        with open(f"src/tmp/features_vector/{notion_database_id}_features_vector.json", "w") as f:
            json.dump(features_vector, f)
