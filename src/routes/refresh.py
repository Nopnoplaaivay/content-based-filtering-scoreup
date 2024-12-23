from flask import Blueprint, jsonify

from src.modules.feature_vectors import FeatureVectors
from src.utils.logger import LOGGER

refresh_routes = Blueprint('refresh', __name__)

@refresh_routes.route('/refresh', methods=['GET'])
def refresh_fv():
    try:
        fv = FeatureVectors()
        fv.refresh_fv()
        return jsonify({"status": "success"})
    except Exception as e:
        LOGGER.error(f"Error in refreshing: {e}")
        return jsonify({"status": "error", "message": str(e)})