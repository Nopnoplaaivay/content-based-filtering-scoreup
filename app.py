import os
import warnings
from flask import Flask
from flask_cors import CORS

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

warnings.filterwarnings("ignore")
from src.routes import (
    recommend_routes,
    upsert_routes,
    training_routes,
    refresh_routes,
    update_ratings_routes
)

app = Flask(__name__)
CORS(app)

app.register_blueprint(recommend_routes)
app.register_blueprint(upsert_routes)
app.register_blueprint(training_routes)
app.register_blueprint(refresh_routes)
app.register_blueprint(update_ratings_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)