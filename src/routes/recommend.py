from flask import Blueprint, request, jsonify

from src.services.strategies import HybridStrategy
from src.services.recommendation_service import RecommendationService
from src.utils.logger import LOGGER

recommend_routes = Blueprint('recommend', __name__, url_prefix="/api/v1/recommend")

@recommend_routes.route('/', methods=['POST'])
def recommend():
    try:
        user_id = request.json['user_id']
        max_exercises = request.json.get('max_exercises', 10)

        strategy = HybridStrategy()
        service = RecommendationService(strategy=strategy)
        recommendations = service.get_recommendations(user_id, max_exercises=max_exercises)

        # recommendations = recommender.recommend(user_id, max_exercises=max_exercises)
        return jsonify({"status": "success", "num_exercises": max_exercises, "recommendations": recommendations})
    except Exception as e:
        LOGGER.error(f"Error in recommend: {e}")
        return jsonify({"status": "error", "message": str(e)})