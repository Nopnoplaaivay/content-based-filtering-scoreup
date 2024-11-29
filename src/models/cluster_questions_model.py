import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer

from src.utils.logger import LOGGER

class ClusterModel:
    def __init__(self, n_clusters=66):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def gen_cluster_df(self, df):
        text_features = self.sentence_model.encode(df['content'].tolist())

        # One-hot encode 'chapter' and 'concept'
        encoder = OneHotEncoder()
        encoded_categorical = encoder.fit_transform(df[['chapter', 'concept']]).toarray()

        # Scale numeric features
        scaler = StandardScaler()
        scaled_difficulty = scaler.fit_transform(df[['difficulty']])

        # Combine all features
        features = np.hstack([text_features, encoded_categorical, scaled_difficulty])

        pca = PCA(n_components=9)
        reduced_features = pca.fit_transform(features)
        df['cluster'] = self.kmeans.fit_predict(reduced_features)

        # Create df with clusters only with reduced features
        clustered_df = pd.DataFrame(reduced_features, columns=[f'feature_{i}' for i in range(reduced_features.shape[1])])
        clustered_df['cluster'] = df['cluster']

        return df, clustered_df
