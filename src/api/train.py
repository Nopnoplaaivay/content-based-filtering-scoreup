import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify

from src.models import ContentBasedModel
from src.db import RatingCollection
from src.utils.logger import LOGGER

training_bp = Blueprint('training', __name__)

@training_bp.route('/train', methods=['POST'])
def train():

    '''Prepare training data'''
    ratings_df = RatingCollection().training_data()

    '''Train model'''
    LOGGER.info("Training model...")
    model = ContentBasedModel()
    model.train(ratings_df=ratings_df)
    return jsonify({"status": "success"})
