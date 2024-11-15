import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from src.api.recommend import recommend_bp
from src.api.upsert import upsert_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(recommend_bp)
app.register_blueprint(upsert_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)