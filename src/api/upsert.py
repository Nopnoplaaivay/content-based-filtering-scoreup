from flask import Blueprint, request, jsonify

from src.db.ratings import RatingCollection
from src.utils.logger import LOGGER
rating_collection = RatingCollection()

upsert_bp = Blueprint('upsert_rating', __name__)

@upsert_bp.route('/upsert', methods=['POST'])
def upsert():
    global rating_collection

    data = request.json
    LOGGER.info(f"Upserting rating: {data}")

    messages = rating_collection.upsert(data)
    return jsonify({"status": "success", "messages": messages})