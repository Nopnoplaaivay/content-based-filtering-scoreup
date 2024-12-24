from flask import Blueprint, request, jsonify

from src.services.update_difficulty_service import UpdateDifficultyService
from src.utils.logger import LOGGER


questions_routes = Blueprint('questions', __name__, url_prefix="/api/v1/questions")
update_difficulty_service = UpdateDifficultyService()

@questions_routes.route("/update", methods=['POST'])
def update_difficulty():
    try:
        update_difficulty_service.update()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        LOGGER.error(f"Error in updating difficulty: {e}")
        return jsonify({"status": "error", "message": str(e)}), 404