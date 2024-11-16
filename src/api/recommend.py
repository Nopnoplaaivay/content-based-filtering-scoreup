import pandas as pd
import numpy as np

from flask import Blueprint, request, jsonify

from src.recommender import Recommender
from src.utils.logger import LOGGER

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend():
    user_id = request.json['user_id']
    recommender = Recommender()
    best_cluster_index, best_cluster_rating = recommender.recommend(user_id, max_items=5)

    LOGGER.info(f"BEST CLUSTER INDEX: {best_cluster_index}")
    LOGGER.info(f"BEST CLUSTER RATING: {best_cluster_rating}")
    return jsonify({"cluster": int(best_cluster_index), "predicted_rating": float(best_cluster_rating)})