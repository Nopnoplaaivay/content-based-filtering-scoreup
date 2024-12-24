from flask import Blueprint, jsonify

from src.utils.feature_vectors import FeatureVectors
from src.utils.logger import LOGGER

feature_routes = Blueprint('features', __name__, url_prefix="/api/v1/features")

@feature_routes.route('/init', methods=['POST'])
def init_feature_vector():
    try:
        fv = FeatureVectors()
        fv.refresh_fv()
        return jsonify({"status": "success"})
    except Exception as e:
        LOGGER.error(f"Error in refreshing: {e}")
        return jsonify({"status": "error", "message": str(e)})