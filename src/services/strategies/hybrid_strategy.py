import json
import random
import numpy as np
import pandas as pd

from src.services.strategies.strategy_interface import RecommendationStrategy
from src.modules.feature_vectors import FeatureVectors

class HybridStrategy(RecommendationStrategy):
    def recommend(self, user_id, max_exercises=10):
        # Logic
        a = 1