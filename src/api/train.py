import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify

from src.models.content_based import ContentBasedModel
from src.db import RatingCollection
from src.utils.logger import LOGGER

training_bp = Blueprint('training', __name__)

@training_bp.route('/train', methods=['POST'])
def train():
    try:
        '''Prepare training data'''
        ratings_df = RatingCollection().get_training_data()

        '''Train model'''
        LOGGER.info("Training model...")
        model = ContentBasedModel()
        model.train(ratings_df=ratings_df)
        return jsonify({"status": "success"})
    except Exception as e:
        LOGGER.error(f"Error in train: {e}")
        return jsonify({"status": "error", "message": str(e)})
