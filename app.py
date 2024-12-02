import os
from flask import Flask
from flask_cors import CORS

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from src.api import recommend_bp, upsert_bp, training_bp, refresh_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(recommend_bp)
app.register_blueprint(upsert_bp)
app.register_blueprint(training_bp)
app.register_blueprint(refresh_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)