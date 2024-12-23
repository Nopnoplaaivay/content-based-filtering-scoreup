from flask import Blueprint, request, jsonify

from src.db import Ratings
from src.utils.logger import LOGGER

update_ratings_bp = Blueprint('update_ratings', __name__)

ratings = Ratings()

@update_ratings_bp.route('/update_ratings', methods=['POST'])
def update_ratings():
    global ratings
    # Pipeline: Ratings.upsert -> train model
    try:
        ratings.update_implicit_ratings()
        LOGGER.info(f"Updating implicit rating completed")
        return jsonify({"status": "success"})
    except Exception as e:
        LOGGER.error(f"Error in update: {e}")
        return jsonify({"status": "error", "message": str(e)})