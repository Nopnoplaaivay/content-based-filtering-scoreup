from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from src.utils.logger import LOGGER

class QuestionClustering:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.best_n_clusters = None

    def get_optimal_clusters(self, X, max_clusters=200):
        """Find the best number of clusters using the silhouette score."""
        best_score = -1
        for n_clusters in range(2, max_clusters + 1):
            model = KMeans(n_clusters=n_clusters, random_state=42)
            labels = model.fit_predict(X)
            score = silhouette_score(X, labels)
            # LOGGER.info(f"Number of clusters: {n_clusters}, Silhouette Score: {score:.4f}")

            if score > best_score:
                best_score = score
                self.best_n_clusters = n_clusters

        LOGGER.info(f"Best number of clusters: {self.best_n_clusters}, Score: {best_score:.4f}")

    def fit(self, X):
        if self.best_n_clusters is None:
            LOGGER.warning("Best number of clusters not found. Running with default.")
        else:
            self.model = KMeans(n_clusters=self.best_n_clusters, random_state=42)
        
        self.model.fit(X)
        LOGGER.info("Clustering model training completed.")

    def predict(self, X):
        return self.model.predict(X)

    def get_cluster_centers(self):
        return self.model.cluster_centers_
