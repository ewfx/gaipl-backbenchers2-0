import os
import logging
from flask import Flask,request
import sys

from traits.trait_types import false

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from src.api.endpoints import api
from flask_cors import CORS

# Ensure src is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

# Define log file path
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/api.log"))

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
CORS(app)

@app.before_request
def log_request():
    """Log incoming requests."""
    logging.info(f"Incoming request: {str(request.url)}")

@app.after_request
def log_response(response):
    """Log outgoing responses."""
    logging.info(f"Response: {response.status_code} {response.get_json()}")
    return response

if __name__ == '__main__':
    logging.info("Starting Flask API...")
    app.run(host='0.0.0.0', port=5001)
