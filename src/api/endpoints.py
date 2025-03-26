import os
import logging
from flask import Blueprint, request, jsonify, Response

from src.chatbot.chatbot import HybridSearchRetriever
from src.classifier.microservice.classifier import predict_microservice
from src.classifier.issuetype.kbClassifier import predict_knowledgeBaseArticle
from src.comments.CommentsDAO import getComments, saveComments
from src.incident.IncidentDAO import getIncidenceDate, updateIncident
from src.resolver.resolver import execute_crew
from pymongo import MongoClient
from src.summarizer.summarizer import summarize_text, summarize_incident
from flask_cors import CORS
import atexit
from bson import ObjectId
from json import dumps
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import time
import json

from src.telemetry.telemetry import generate_database_telemetry_randam_true, generate_database_telemetry, \
    generate_apps_telemetry_randam_true, generate_apps_telemetry

# Define log file path
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs/app.log"))

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

api = Blueprint('api', __name__)
CORS(api)  # Enable CORS for all routes in this blueprint

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "IncidenceDB"
COLLECTION_NAME = "Incidents"
KB_COLLECTION_NAME = "ResolutionKnowledgeBase"


# MongoDB Connection Management
class MongoDBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(MONGO_URI)
            atexit.register(cls._instance.close_connections)
        return cls._instance

    def get_db(self):
        return self.client[DATABASE_NAME]

    def get_collection(self, collection_name):
        return self.get_db()[collection_name]

    def close_connections(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()
            logging.info("MongoDB connections closed via atexit")


# Initialize MongoDB connection manager
mongo_manager = MongoDBManager()


@api.teardown_request
def teardown_mongo(exception=None):
    """Flask teardown handler for request cleanup"""
    pass  # Connection is managed by MongoDBManager


# Helper function to serialize MongoDB documents
def serialize_mongo_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


@api.route('/microservice/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data or 'title' not in data or 'description' not in data:
        logging.warning("Missing title or description in request")
        return jsonify({'error': 'Missing title or description'}), 400

    title = data['title']
    description = data['description']

    predicted_microservice = predict_microservice(title, description)
    logging.info(f"Prediction Response: {predicted_microservice}")

    return jsonify({'predicted_microservice': predicted_microservice})


@api.route('/kb/predict', methods=['POST'])
def predictKB():
    data = request.get_json()

    if not data or 'title' not in data or 'description' not in data:
        logging.warning("Missing title or description in request")
        return jsonify({'error': 'Missing title or description'}), 400

    title = data['title']
    description = data['description']

    predicted_kb = predict_knowledgeBaseArticle(title, description)
    logging.info(f"Prediction Response: {predicted_kb}")

    return jsonify({'predicted_kb': predicted_kb})


@api.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json()
        input_text = data.get("text", "")

        if not input_text:
            return jsonify({"error": "No text provided"}), 400

        summary_result = summarize_text(input_text)
        return jsonify(summary_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/health", methods=['GET'])
def test_endpoint():
    return "API Blueprint is working!"


@api.route("/summarize_incident", methods=["GET"])
def summarize_incident_details():
    try:
        incident_id = request.args.get("incident_id")

        if not incident_id:
            return jsonify({"error": "Incident ID is required"}), 400

        summary_result = summarize_incident(incident_id)
        return jsonify(summary_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/stream", methods=['POST', 'OPTIONS'])
def stream():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    try:
        incident_data = request.get_json()
        if not incident_data:
            return jsonify({"error": "Invalid request. No JSON payload received."}), 400

        required_keys = {"incident_id", "description", "severity"}
        if not required_keys.issubset(incident_data.keys()):
            return jsonify({"error": f"Missing required keys. Expected: {list(required_keys)}"}), 400

    except Exception as e:
        return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400

    def generate():
        for message in execute_crew(incident_data):
            yield f"data: {message}\n\n"

    response = Response(generate(), mimetype="text/event-stream")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@api.route('/update-incident/<incidentId>', methods=['POST'])
def update_incident(incidentId):
    try:
        update_data = request.json
        if not update_data:
            return jsonify({"error": "No update data provided"}), 400

        # Remove _id field if present in the update data
        if '_id' in update_data:
            del update_data['_id']
        logging.info(f"Updating incident {incidentId} with data: {update_data}")
        collection = mongo_manager.get_collection(COLLECTION_NAME)
        logging.info(collection)
        query = {'incident_id': incidentId}
        updated_document = collection.replace_one(query, update_data)
        '''updated_document = collection.find_one_and_update(
            {"article_id": incidentId},
            {"$set": update_data},
            return_document=True
        )

        if not updated_document:
            return jsonify({"error": "Incident not found"}), 404

        return jsonify(serialize_mongo_doc(updated_document)), 200
'''
        return jsonify({"status": "Update completed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@api.route('/incidents/<incidentId>', methods=['GET'])
def get_incident(incidentId):
    try:
        collection = mongo_manager.get_collection(COLLECTION_NAME)
        incident = collection.find_one({"incident_id": incidentId})
        logging.info("IncidentID: " + incidentId+" Title "+incident['title']+ " Description "+incident['description']+ " kb_article_id "+incident['kb_article_id'])
        if not incident:
            return jsonify({"error": "Incident not found"}), 404

        return jsonify(serialize_mongo_doc(incident)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/incident-post', methods=['POST'])
def post_incidents():
    data = request.json
    pageSize=data.get('pageSize');
    pageNo=data.get('page');
    return getIncidenceDate(data,pageSize,pageNo)

@api.route('/save-comment', methods=['POST'])
def save_commentc():
    data = request.json
    return saveComments(data)

@api.route('/get-comments', methods=['POST'])
def get_comments():
    data = request.json
    return getComments(data)


@api.route('/knowledgeArticle/<kbId>', methods=['POST'])
def get_knowledgeArticle(kbId):
    try:
        kb_collection = mongo_manager.get_collection(KB_COLLECTION_NAME)
        kb_article = kb_collection.find_one({"article_id": kbId})

        if not kb_article:
            return jsonify({"error": "KB Article not found"}), 404

        response = serialize_mongo_doc(kb_article);
        print(json.dumps(response))
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/telemetryData', methods=['GET'])
def get_app_health_telemetryData():
    category_type = request.args.get('category', None)
    random_type = request.args.get('randomType', None)

    if category_type == "database":
        if random_type == "true":
            return jsonify(generate_database_telemetry_randam_true())
        return jsonify(generate_database_telemetry())
    else:
        if random_type == "true":
            return jsonify(generate_apps_telemetry_randam_true())
        return jsonify(generate_apps_telemetry())



# Session management
sessions = defaultdict(dict)
session_lock = threading.Lock()

def cleanup_expired_sessions():
    """Clean up sessions older than 60 seconds"""
    while True:
        time.sleep(30)  # Run every 30 seconds
        now = datetime.now()
        with session_lock:
            expired = [sid for sid, session in sessions.items()
                      if now - session['last_activity'] > timedelta(seconds=60)]
            for sid in expired:
                del sessions[sid]
                logging.info(f"Cleaned up expired session: {sid}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_expired_sessions, daemon=True)
cleanup_thread.start()

# Initialize the retriever
retriever = HybridSearchRetriever()


@api.route('/search', methods=['POST'])
def search():
    """Endpoint for hybrid search with session context and summarization"""
    data = request.json
    query = data.get('query')
    session_id = data.get('session_id', 'default')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        with session_lock:
            # Initialize or update session
            if session_id not in sessions:
                sessions[session_id] = {
                    'context': [],
                    'last_activity': datetime.now()
                }
            else:
                sessions[session_id]['last_activity'] = datetime.now()

            # Perform search with context
            context = sessions[session_id]['context']
            enhanced_query = f"{query} {' '.join(context)}" if context else query
            results = retriever.search(enhanced_query)

            # Find and process the highest scoring result
            processed_result = None
            if results:
                # Sort results by score and get the top one
                results_sorted = sorted(
                    results,
                    key=lambda x: x.get('metadata', {}).get('score', 0),
                    reverse=True
                )
                top_result = results_sorted[0] if results_sorted else None

                if top_result:
                    # Summarize the content
                    summarized_content = summarize_text(top_result['content'])

                    # Create processed result with original and summarized content
                    processed_result = {
                        "original_content": top_result['content'],
                        "summary": summarized_content['summary'],
                        "metadata": top_result['metadata']
                    }

            # Update context with current query
            sessions[session_id]['context'].append(query)
            if len(sessions[session_id]['context']) > 5:
                sessions[session_id]['context'].pop(0)

            return jsonify({
                "result": processed_result,
                "session_id": session_id,
                "context": sessions[session_id]['context'],
                "metadata": {
                    "total_results": len(results),
                    "top_score": processed_result['metadata']['score'] if processed_result else 0
                }
            })

    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api.route('/sessions', methods=['GET'])
def list_sessions():
    """Endpoint to list active sessions (for debugging)"""
    with session_lock:
        return jsonify({
            "active_sessions": len(sessions),
            "sessions": list(sessions.keys())
        })
