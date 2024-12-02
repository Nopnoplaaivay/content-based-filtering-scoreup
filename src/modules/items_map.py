import json
import re
import os
import numpy as np
import pandas as pd

from src.db import Questions
from src.models.cluster_questions_model import ClusterModel
from src.modules.feature_vectors import FeatureVectors
from src.utils.encode_utils import EncodeQuestionsUtils
from src.utils.logger import LOGGER

class ItemsMap:
    def __init__(self):
        self.encoder = EncodeQuestionsUtils()
        self.cluster_model = ClusterModel()
        self.feature_vectors = FeatureVectors()

    def refresh_mapping(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        # Delete existing mapping src/tmp
        if os.path.exists(f"src/tmp"):
            os.system(f"rm -rf src/tmp")

        self.gen_qcmap(notion_database_id=notion_database_id)

    def get_feature_vectors_map(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        try:
            if os.path.exists(f"src/tmp/mapping/{notion_database_id}_feature_vectors_map.json"):
                with open(f"src/tmp/mapping/{notion_database_id}_feature_vectors_map.json", "r") as f:
                    feature_vectors_map = json.load(f)
                return feature_vectors_map
            else:
                LOGGER.error(f"Cluster map not found for {notion_database_id}")
                self.gen_qcmap(notion_database_id=notion_database_id)
                with open(f"src/tmp/mapping/{notion_database_id}_feature_vectors_map.json", "r") as f:
                    feature_vectors_map = json.load(f)
                return feature_vectors_map
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
        question_df, feature_vectors_df = self.feature_vectors.gen_feature_vectors_df(raw_questions_df)

        feature_vectors_map = {}
        for cluster in feature_vectors_df['idx'].unique():
            feature_vector_str = str(cluster)
            features_vectors = feature_vectors_df[feature_vectors_df['idx'] == cluster].iloc[:, :-2].values

            # get cluster features_vector
            centroid = features_vectors.mean(axis=0)
            cluster_centroid = centroid.tolist()
            print(f"Cluster {cluster} centroid: {cluster_centroid}")

            question_ids = raw_questions_df[raw_questions_df['idx'] == cluster]['question_id'].tolist()
            feature_vectors_map[feature_vector_str] = {
                "features_vector": cluster_centroid,
                "question_id": question_ids
            }

        # Calculate cluster difficulty = average difficulty of questions in cluster
        question_df['difficulty'] = question_df['difficulty'].astype(float)
        question_difficulty = question_df.groupby('idx')['difficulty'].mean().reset_index()
        question_difficulty.columns = ['idx', 'question_difficulty']

        for cluster in question_difficulty['idx']:
            feature_vector_str = str(cluster)
            if feature_vector_str in feature_vectors_map:
                feature_vectors_map[feature_vector_str]['question_difficulty'] = question_difficulty[question_difficulty['idx'] == cluster]['question_difficulty'].values[0]

        # Generate features vector
        features_vector = {}
        for key, value in feature_vectors_map.items():
            features_vector[key] = value["features_vector"]

        # Save feature_vectors_map, question_map in json format
        os.makedirs('src/tmp/mapping', exist_ok=True)
        with open(f"src/tmp/mapping/{notion_database_id}_feature_vectors_map.json", "w") as f:
            json.dump(feature_vectors_map, f)

        question_map = raw_questions_df.set_index('question_id')['idx'].to_dict()
        with open(f"src/tmp/mapping/{notion_database_id}_question_map.json", "w") as f:
            json.dump(question_map, f)

        # Save features vector
        os.makedirs('src/tmp/features_vector', exist_ok=True)
        with open(f"src/tmp/features_vector/{notion_database_id}_features_vector.json", "w") as f:
            json.dump(features_vector, f)