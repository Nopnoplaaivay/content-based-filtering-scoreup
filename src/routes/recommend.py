from flask import Blueprint, request, jsonify
from src.recommender import Recommender
from src.utils.logger import LOGGER

recommend_routes = Blueprint('recommend', __name__)

@recommend_routes.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_id = request.json['user_id']
        max_exercises = request.json.get('max_exercises', 5)
        recommender = Recommender()
        recommendations = recommender.recommend(user_id, max_exercises=max_exercises)
        return jsonify({"status": "success", "num_exercises": max_exercises, "recommendations": recommendations})
    except Exception as e:
        LOGGER.error(f"Error in recommend: {e}")
        return jsonify({"status": "error", "message": str(e)})