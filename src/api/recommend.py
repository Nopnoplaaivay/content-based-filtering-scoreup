from flask import Blueprint, request, jsonify

from src.recommender import Recommender
from src.utils.logger import LOGGER

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_id = request.json['user_id']
        recommender = Recommender()
        recommendations = recommender.recommend(user_id)
        return jsonify({"status": "success", "recommendations": recommendations})
    except Exception as e:
        LOGGER.error(f"Error in recommend: {e}")
        return jsonify({"status": "error", "message": str(e)})