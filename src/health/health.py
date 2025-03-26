import os
import requests
import psutil
import sqlite3  # Change this for PostgreSQL/MySQL
from flask import Flask, jsonify

# Flask App for Health Check API
app = Flask(__name__)

# Configuration
API_URL = "http://127.0.0.1:5000/predict"  # Change this to your API endpoint
DB_PATH = "/ipe/data/database.db"  # Change this for PostgreSQL/MySQL

def check_api():
    """Check if the API is up and running"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            return {"status": "UP", "response_time": response.elapsed.total_seconds()}
        return {"status": "DOWN", "error": f"Status Code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "DOWN", "error": str(e)}

def check_database():
    """Check if database connection is working"""
    try:
        conn = sqlite3.connect(DB_PATH)  # For PostgreSQL/MySQL, use psycopg2 / MySQLdb
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"status": "UP"}
    except Exception as e:
        return {"status": "DOWN", "error": str(e)}

def check_system_resources():
    """Check system CPU, memory, and disk usage"""
    return {
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "disk_usage": f"{psutil.disk_usage('/').percent}%",
    }

@app.route("/health", methods=["GET"])
def health_check():
    """API Endpoint for health check"""
    health_status = {
        "api": check_api(),
        "database": check_database(),
        "system_resources": check_system_resources(),
    }
    return jsonify(health_status)
