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

    def gen_cluster_df(self, df):
        LOGGER.info('Generating cluster model...')
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        text_features = sentence_model.encode(df['content'].tolist())

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
        clustered_df['question_id'] = df['question_id']

        # Sort by cluster
        clustered_df = clustered_df.sort_values(by='cluster').reset_index(drop=True)

        # df.to_csv("df.csv", index=False)
        # clustered_df.to_csv("clustered_df.csv", index=False)

        return df, clustered_df
