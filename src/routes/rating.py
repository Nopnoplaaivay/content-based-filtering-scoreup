from flask import Blueprint, request, jsonify

from src.services.ratings_service import RatingService
from src.models.cbf_model import CBFModel
from src.utils.logger import LOGGER


rating_routes = Blueprint('ratings', __name__, url_prefix="/api/v1/ratings")
rating_service = RatingService()

@rating_routes.route("/upsert", methods=['POST'])
def upsert_ratings():
    try:
        data = request.json
        messages = rating_service.upsert_ratings(data)
        LOGGER.info(f"DONE upsert ratings: {data}")

        model = CBFModel()
        model.train()
        return jsonify({"status": "success", "messages": messages}), 200
    
    except Exception as e:
        LOGGER.error(f"Error in upsert: {e}")
        return jsonify({"status": "error", "message": str(e)}), 404
        
@rating_routes.route("/update", methods=['POST'])
def update_implicits():
    try:
        rating_service.update_newest_ratings_daily()
        LOGGER.info(f"DONE update implicit ratings.")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        LOGGER.error(f"Error in update implicit ratings: {e}")
        return jsonify({"status": "error", "message": str(e)}), 404

# @rating_routes.route("/init", methods=['POST'])
# def init_implicits():
#     try:
#         rating_service.init_implicits()
#         LOGGER.info(f"DONE init implicit ratings.")
#         return jsonify({"status": "success"}), 200
#     except Exception as e:
#         LOGGER.error(f"Error in init implicit ratings: {e}")
#         return jsonify({"status": "error", "message": str(e)}), 404