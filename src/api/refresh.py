from flask import Blueprint, request, jsonify

from src.modules.items_map import ItemsMap
from src.utils.logger import LOGGER

refresh_bp = Blueprint('refresh', __name__)

@refresh_bp.route('/refresh', methods=['GET'])
def recommend():
    try:
        items_map = ItemsMap()
        items_map.refresh_mapping()
        return jsonify({"status": "success"})
    except Exception as e:
        # return 4xx status code
        LOGGER.error(f"Error in refreshing: {e}")
        return jsonify({"status": "error", "message": str(e)})