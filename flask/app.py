from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

import time
import threading
from collections import deque


app = Flask(__name__)

CORS(app)


# =========================================================
# METRICS
# =========================================================

lock = threading.Lock()

total_requests = 0
successful_requests = 0
failed_requests = 0

active_requests = 0

request_times = deque(maxlen=1000)


# =========================================================
# MIDDLEWARE
# =========================================================

@app.before_request
def before_request():

    global total_requests
    global active_requests

    request.start_time = time.perf_counter()

    with lock:
        total_requests += 1
        active_requests += 1


@app.after_request
def after_request(response):

    global successful_requests
    global failed_requests
    global active_requests

    elapsed = (
        time.perf_counter()
        - request.start_time
    )

    latency_ms = elapsed * 1000

    with lock:

        active_requests -= 1

        request_times.append(
            latency_ms
        )

        if response.status_code < 400:

            successful_requests += 1

        else:

            failed_requests += 1

    return response


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# TEST API
# =========================================================

@app.route("/api/hello")
def hello():

    return jsonify({
        "message": "Hello from Flask",
        "timestamp": time.time()
    })


# =========================================================
# STUDENTS
# =========================================================

@app.route("/api/students")
def students():

    return jsonify([
        {
            "id": 1,
            "name": "John"
        },
        {
            "id": 2,
            "name": "David"
        },
        {
            "id": 3,
            "name": "Sarah"
        }
    ])


# =========================================================
# SLOW API
# =========================================================

@app.route("/api/slow")
def slow_api():

    time.sleep(0.2)

    return jsonify({
        "message":
        "Slow request completed"
    })


# =========================================================
# ERROR TEST
# =========================================================

@app.route("/api/error")
def error_api():

    return jsonify({
        "error": True,
        "message": "Simulated error"
    }), 500


# =========================================================
# NORMAL TEST
# =========================================================

@app.route("/test")
def test():

    return jsonify({
        "status": "ok",
        "message":
        "Test request successful"
    })


# =========================================================
# HEALTH
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


# =========================================================
# METRICS
# =========================================================

@app.route("/metrics")
def metrics():

    with lock:

        total = total_requests

        success = successful_requests

        failed = failed_requests

        active = active_requests

        times = list(
            request_times
        )


    if times:

        average_latency = (
            sum(times) /
            len(times)
        )

        min_latency = min(times)

        max_latency = max(times)

    else:

        average_latency = 0

        min_latency = 0

        max_latency = 0


    return jsonify({

        "total_requests":
            total,

        "successful_requests":
            success,

        "failed_requests":
            failed,

        "active_requests":
            active,

        "average_latency_ms":
            round(
                average_latency,
                2
            ),

        "min_latency_ms":
            round(
                min_latency,
                2
            ),

        "max_latency_ms":
            round(
                max_latency,
                2
            )
    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )