import json

with open('src/data/c3a788eb31f1471f9734157e9516f9b6_cluster_map.json') as file:
    cluster_map = json.load(file)

class FeaturesVector:

    FEATURES_VECTOR = {}

    @classmethod
    def generate_features_vector(cls):
        for key, value in cluster_map.items():
            cls.FEATURES_VECTOR[key] = value["features_vector"]


