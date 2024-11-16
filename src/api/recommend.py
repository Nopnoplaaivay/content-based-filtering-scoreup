from flask import Blueprint, request, jsonify

from src.recommender import Recommender
from src.utils.logger import LOGGER

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend():
    user_id = request.json['user_id']
    recommender = Recommender()
    # best_cluster_index, best_cluster_rating = recommender.recommend(user_id, max_items=5)
    recommendations = recommender.recommend(user_id)
    LOGGER.info(f"Recommendations for user {user_id}: {recommendations}")

    return jsonify({"status": "success", "recommendations": recommendations})