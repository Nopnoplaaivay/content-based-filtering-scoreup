import pandas as pd
import numpy as np

from flask import Blueprint, request, jsonify
from src.db.ratings import RatingCollection

rating_collection = RatingCollection()

upsert_bp = Blueprint('upsert_rating', __name__)

@upsert_bp.route('/upsert', methods=['POST'])
def upsert():
    global rating_collection

    data = request.json
    user_id = data['user_id']
    cluster = data['cluster']
    rating = data['rating']

    rating_collection.upsert({
        "user_id": user_id,
        "cluster": cluster,
        "rating": rating
    })
    return jsonify({"status": "success"})