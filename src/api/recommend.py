import pandas as pd
import numpy as np

from flask import Blueprint, request, jsonify

from src.models import ContentBasedModel
from src.utils.logger import LOGGER

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend():
    user_id = request.json['user_id']
    ratings = pd.read_csv('user_cluster_ratings.csv')
    model = ContentBasedModel(ratings)
    model.train()
    recommended_items = model.pred(user_id)
    LOGGER.info(f"Recommended Exercise: {recommended_items}")
    return jsonify({"recommended_items": "success"})