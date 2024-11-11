import json

from src.models.feature_vectors import FeaturesVector

FeaturesVector.generate_features_vector()

# print json pretty
print(json.dumps(FeaturesVector.FEATURES_VECTOR, indent=4))


