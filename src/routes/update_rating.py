from flask import Blueprint, jsonify

from src.repositories import Ratings
from src.utils.logger import LOGGER

update_ratings_routes = Blueprint('update_ratings', __name__)

ratings = Ratings()

@update_ratings_routes.route('/update_ratings', methods=['POST'])
def update_ratings():
    global ratings
    # Pipeline: Ratings.upsert -> train model
    try:
        ratings.update_implicit_ratings()
        LOGGER.info(f"DONE updating ratings")
        return jsonify({"status": "success"})
    except Exception as e:
        LOGGER.error(f"Error in update: {e}")
        return jsonify({"status": "error", "message": str(e)})