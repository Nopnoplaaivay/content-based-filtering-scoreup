import pandas as pd
import numpy as np
from flask import Blueprint, jsonify

from src.models.cbf_model import CBFModel
from src.utils.logger import LOGGER

training_bp = Blueprint('training', __name__)

@training_bp.route('/train', methods=['POST'])
def train():
    try:
        '''Train model'''
        LOGGER.info("Training model...")
        model = CBFModel()
        model.train()
        return jsonify({"status": "success"})
    except Exception as e:
        LOGGER.error(f"Error in train: {e}")
        return jsonify({"status": "error", "message": str(e)})
