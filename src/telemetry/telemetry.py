from flask import Flask, jsonify, request
import random
from datetime import datetime, timedelta

app = Flask(__name__)


# Function to generate random telemetry data for a database
def generate_database_telemetry_randam_true():
    return {
        "database": [
            {
                "status": random.choice(["healthy", "unhealthy"]),
                "connections": random.randint(0, 100),
                "queries_per_second": random.randint(0, 500),
                "latency_ms": random.randint(10, 1000),
                "timestamp": datetime.now()
            },
            {
                "status": random.choice(["healthy", "unhealthy"]),
                "connections": random.randint(0, 100),
                "queries_per_second": random.randint(0, 500),
                "latency_ms": random.randint(10, 1000),
                "timestamp": datetime.today() - timedelta(hours=1)
            },
            {
                "status": random.choice(["healthy", "unhealthy"]),
                "connections": random.randint(0, 100),
                "queries_per_second": random.randint(0, 500),
                "latency_ms": random.randint(10, 1000),
                "timestamp": datetime.today() - timedelta(hours=2)
            },
            {
                "status": random.choice(["healthy", "unhealthy"]),
                "connections": random.randint(0, 100),
                "queries_per_second": random.randint(0, 500),
                "latency_ms": random.randint(10, 1000),
                "timestamp": datetime.today() - timedelta(hours=3)
            },
            {
                "status": random.choice(["healthy", "unhealthy"]),
                "connections": random.randint(0, 100),
                "queries_per_second": random.randint(0, 500),
                "latency_ms": random.randint(10, 1000),
                "timestamp": datetime.today() - timedelta(hours=4)
            }
        ]
    }


def generate_database_telemetry():
    return {
        "database": [
            {
                "status": "healthy",
                "connections": 90,
                "queries_per_second": 450,
                "latency_ms": 1000,
                "timestamp": datetime.now()
            }
        ]
    }


# Function to generate random telemetry data for apps
def generate_apps_telemetry_randam_true():
    return {
        "appInfo": [
            {
                "status": random.choice(["running", "stopped"]),
                "cpu_usage": random.randint(0, 100),
                "memory_usage": random.randint(0, 100),

                "health_status": random.choice(["healthy", "degraded", "unhealthy"]),
                "response_time_ms": random.randint(50, 2000),
                "error_rate": random.uniform(0, 1),
                "timestamp": datetime.now(),

            },
            {
                "status": random.choice(["running", "stopped"]),
                "cpu_usage": random.randint(0, 100),
                "memory_usage": random.randint(0, 100),
                "health_status": random.choice(["healthy", "degraded", "unhealthy"]),
                "response_time_ms": random.randint(50, 2000),
                "error_rate": random.uniform(0, 1),
                "timestamp": datetime.today() - timedelta(hours=1)
            },
            {
                "status": random.choice(["running", "stopped"]),
                "cpu_usage": random.randint(0, 100),
                "memory_usage": random.randint(0, 100),
                "health_status": random.choice(["healthy", "degraded", "unhealthy"]),
                "response_time_ms": random.randint(50, 2000),
                "error_rate": random.uniform(0, 1),
                "timestamp": datetime.today() - timedelta(hours=2)

            },
            {
                "status": random.choice(["running", "stopped"]),
                "cpu_usage": random.randint(0, 100),
                "memory_usage": random.randint(0, 100),

                "health_status": random.choice(["healthy", "degraded", "unhealthy"]),
                "response_time_ms": random.randint(50, 2000),
                "error_rate": random.uniform(0, 1),
                "timestamp": datetime.today() - timedelta(hours=3)
            },
            {
                "status": random.choice(["running", "stopped"]),
                "cpu_usage": random.randint(0, 100),
                "memory_usage": random.randint(0, 100),

                "health_status": random.choice(["healthy", "degraded", "unhealthy"]),
                "response_time_ms": random.randint(50, 2000),
                "error_rate": random.uniform(0, 1),
                "timestamp": datetime.today() - timedelta(hours=4)  # Error rate between 0 and 1

            }

        ]
    }


def generate_apps_telemetry():
    return {
        "appInfo": [
            {
                "status": "stopped",
                "cpu_usage": 62,
                "memory_usage": 50,

                "health_status": "healthy",
                "response_time_ms": 20,
                "error_rate": 0,
                "timestamp": datetime.now().isoformat(),

            }

        ]
    }


@app.route('/telemetryData', methods=['POST'])
def get_app_health_telemetryData():
    try:
        # Get all parameters from request JSON body
        request_data = request.get_json()

        if not request_data:
            return jsonify({"error": "No request body provided"}), 400

        # Validate request format
        if not isinstance(request_data, list):
            return jsonify({"error": "Request body should be an array of node objects"}), 400

        # Process each node in the request
        responses = []
        for node in request_data:
            node_id = node.get('node_id')
            node_name = node.get('node_name')

            if not node_id:
                responses.append({
                    "error": "Missing node_id in node object",
                    "node": node
                })
                continue

            # Determine which telemetry generator to use based on node_id
            # (Assuming node_id contains type information like "db_" or "app_")
            if "db_" in node_name.lower() or "database" in node_name.lower():
                if node.get("random", False):
                    telemetry = generate_database_telemetry()
                else:
                    telemetry = generate_database_telemetry_randam_true()
            else:
                if node.get("random", False):
                    telemetry = generate_apps_telemetry()
                else:
                    telemetry = generate_apps_telemetry_randam_true()

            # Add node context to the telemetry data
            telemetry_with_context = {
                "node_id": node_id,
                "node_name": node.get('node_name', node.get("node_name")),
                "telemetry": telemetry,
                "metrics": node.get('metrics', [])
            }

            responses.append(telemetry_with_context)

        return jsonify(responses)

    except Exception as e:
        #logging.error(f"Error in telemetryData endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)

