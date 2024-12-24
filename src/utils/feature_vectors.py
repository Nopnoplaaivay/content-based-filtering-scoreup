import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer

from src.repositories import QuestionsRepo
from src.utils.logger import LOGGER

class FeatureVectors:
    def __init__(self, notion_database_id="c3a788eb31f1471f9734157e9516f9b6"):
        self.notion_database_id = notion_database_id
        self.features_vectors = None
        self.metadata = None

    def refresh_fv(self):
        LOGGER.info('Refreshing features vector...')
        self.gen_feature_vectors_df()


    def save_fv(self):
        try:
            os.makedirs("src/tmp/features_vectors", exist_ok=True)
            np.save(f"src/tmp/features_vectors/{self.notion_database_id}_feature_vectors.npy", self.features_vectors)
            self.metadata.to_csv(f"src/tmp/mapping/{self.notion_database_id}_metadata.csv", index=False)
            LOGGER.info("Saved features vector successfully.")
        except Exception as e:
            LOGGER.error(f"Error saving features vector: {e}")

    def load_fv(self):
        try:
            self.features_vectors = np.load(f"src/tmp/features_vectors/{self.notion_database_id}_feature_vectors.npy")
            self.metadata = pd.read_csv(f"src/tmp/mapping/{self.notion_database_id}_metadata.csv")
            LOGGER.info("Loaded features vector successfully.")
        except Exception as e:
            LOGGER.error(f"Error loading features vector: {e}")
            self.gen_feature_vectors_df()

    def gen_feature_vectors_df(self):
        try:
            LOGGER.info('Fetching questions...')
            questions = QuestionsRepo()
            raw_questions = questions.fetch_all()
            df = questions.preprocess_questions(raw_questions)
            df['item_id'] = df.index

            LOGGER.info('Feature vectorizing questions...')
            sentence_tranformer = SentenceTransformer('all-MiniLM-L6-v2')
            encoder = OneHotEncoder()
            scaler = StandardScaler()

            text_features = sentence_tranformer.encode(df['content'].tolist())
            encoded_categorical = encoder.fit_transform(df[['chapter', 'concept']]).toarray()
            scaled_difficulty = scaler.fit_transform(df[['difficulty']])
            features = np.hstack([text_features, encoded_categorical, scaled_difficulty])
            pca = PCA(n_components=9)
            reduced_fv = pca.fit_transform(features)

            self.metadata = df
            self.features_vectors = reduced_fv
            self.save_fv()
        except Exception as e:
            LOGGER.error(f"Error generating feature vectors: {e}")
            raise e
        finally:
            return questions.close()