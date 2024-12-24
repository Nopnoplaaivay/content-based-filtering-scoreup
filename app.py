import os
import warnings
from flask import Flask
from flask_cors import CORS

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore")

from src.routes import (
    recommend_routes,
    training_routes,
    feature_routes,
    rating_routes,
    questions_routes
)

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*", }})
CORS(app, resources={r"/*": {"origins": "*", "methods": "*"}})

app.register_blueprint(recommend_routes)
app.register_blueprint(training_routes)
app.register_blueprint(feature_routes)
app.register_blueprint(rating_routes)
app.register_blueprint(questions_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)