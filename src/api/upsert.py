from flask import Blueprint, request, jsonify

from src.models.cbf_model import CBFModel
from src.db import Ratings
from src.utils.logger import LOGGER

ratings = Ratings()

upsert_bp = Blueprint('upsert_rating', __name__)

@upsert_bp.route('/upsert', methods=['POST'])
def upsert():
    global ratings
    # Pipeline: Ratings.upsert -> train model
    try:
        data = request.json
        messages = ratings.upsert(data)
        LOGGER.info(f"Upserted rating completed: {data}")

        # Train model
        ratings = Ratings()
        ratings_df = ratings.get_training_data()
        model = CBFModel()
        model.train(ratings_df=ratings_df)
        return jsonify({"status": "success", "messages": messages})
    except Exception as e:
        LOGGER.error(f"Error in upsert: {e}")
        return jsonify({"status": "error", "message": str(e)})