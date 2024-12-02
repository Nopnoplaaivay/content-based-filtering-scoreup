import json
import re
import os
import numpy as np
import pandas as pd

from src.db import Questions
from src.models.cluster_questions_model import ClusterModel
from src.utils.encode_utils import EncodeQuestionsUtils
from src.utils.logger import LOGGER

class ItemsMap:
    def __init__(self):
        self.encoder = EncodeQuestionsUtils()
        self.cluster_model = ClusterModel()

    def refresh_mapping(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.gen_qcmap(notion_database_id=notion_database_id)

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
                transformed_features_vector = np.array(list(features_vector.values()))
                return transformed_features_vector
            else:
                LOGGER.error(f"Features vector not found for {notion_database_id}")
                self.gen_qcmap(notion_database_id=notion_database_id)
                with open(f"src/tmp/features_vector/{notion_database_id}_features_vector.json", "r") as f:
                    features_vector = json.load(f)
                transformed_features_vector = np.array(list(features_vector.values()))  
                return transformed_features_vector
        except Exception as e:
            LOGGER.error(f"Error fetching features vector: {e}")
            return None

    def gen_qcmap(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        # Prepare data
        questions = Questions(notion_database_id=notion_database_id)
        raw_questions = questions.fetch_all()
        raw_questions_df = questions.preprocess_questions(raw_questions=raw_questions)
        
        # Prepare df
        question_df, cluster_df = self.cluster_model.gen_cluster_df(raw_questions_df)

        cluster_map = {}
        for cluster in cluster_df['cluster'].unique():
            cluster_str = str(cluster)
            features_vectors = cluster_df[cluster_df['cluster'] == cluster].iloc[:, :-2].values

            # get cluster features_vector
            centroid = features_vectors.mean(axis=0)
            cluster_centroid = centroid.tolist()
            print(f"Cluster {cluster} centroid: {cluster_centroid}")

            question_ids = raw_questions_df[raw_questions_df['cluster'] == cluster]['question_id'].tolist()
            cluster_map[cluster_str] = {
                "features_vector": cluster_centroid,
                "question_id": question_ids
            }

        # Calculate cluster difficulty = average difficulty of questions in cluster
        question_df['difficulty'] = question_df['difficulty'].astype(float)
        cluster_difficulty = question_df.groupby('cluster')['difficulty'].mean().reset_index()
        cluster_difficulty.columns = ['cluster', 'cluster_difficulty']

        for cluster in cluster_difficulty['cluster']:
            cluster_str = str(cluster)
            if cluster_str in cluster_map:
                cluster_map[cluster_str]['cluster_difficulty'] = cluster_difficulty[cluster_difficulty['cluster'] == cluster]['cluster_difficulty'].values[0]

        # Generate features vector
        features_vector = {}
        for key, value in cluster_map.items():
            features_vector[key] = value["features_vector"]

        # Save cluster_map, question_map in json format
        os.makedirs('src/tmp/mapping', exist_ok=True)
        with open(f"src/tmp/mapping/{notion_database_id}_cluster_map.json", "w") as f:
            json.dump(cluster_map, f)

        question_map = raw_questions_df.set_index('question_id')['cluster'].to_dict()
        with open(f"src/tmp/mapping/{notion_database_id}_question_map.json", "w") as f:
            json.dump(question_map, f)

        # Save features vector
        os.makedirs('src/tmp/features_vector', exist_ok=True)
        with open(f"src/tmp/features_vector/{notion_database_id}_features_vector.json", "w") as f:
            json.dump(features_vector, f)