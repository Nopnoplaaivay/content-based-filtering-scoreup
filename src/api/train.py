import pandas as pd
import numpy as np

from flask import Blueprint, request, jsonify

training_bp = Blueprint('training', __name__)
