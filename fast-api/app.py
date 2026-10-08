import time
import asyncio
from collections import deque
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="FastAPI Performance Monitor",
    description="Live FastAPI performance monitoring dashboard",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

metrics_lock = Lock()

total_requests = 0
successful_requests = 0
failed_requests = 0

request_times = deque(maxlen=1000)

request_history = deque(maxlen=60)

active_requests = 0


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

@app.middleware("http")
async def performance_middleware(request: Request, call_next):

    global total_requests
    global successful_requests
    global failed_requests
    global active_requests

    start_time = time.perf_counter()

    with metrics_lock:
        total_requests += 1
        active_requests += 1

    try:

        response = await call_next(request)

        if response.status_code < 400:
            with metrics_lock:
                successful_requests += 1
        else:
            with metrics_lock:
                failed_requests += 1

        return response

    except Exception:

        with metrics_lock:
            failed_requests += 1

        raise

    finally:

        elapsed = time.perf_counter() - start_time

        with metrics_lock:
            active_requests -= 1
            request_times.append(elapsed * 1000)


# ---------------------------------------------------------
# Test API
# ---------------------------------------------------------

@app.get("/")
async def home():

    return FileResponse("static/index.html")


@app.get("/api/hello")
async def hello():

    return {
        "message": "Hello from FastAPI",
        "timestamp": time.time()
    }


@app.get("/api/students")
async def students():

    return [
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
    ]


@app.get("/api/slow")
async def slow_api():

    # Simulate slow API

    await asyncio.sleep(0.2)

    return {
        "message": "Slow request completed"
    }


@app.get("/api/error")
async def error_api():

    return {
        "error": True,
        "message": "Simulated error"
    }


# ---------------------------------------------------------
# Metrics API
# ---------------------------------------------------------

@app.get("/metrics")
async def get_metrics():

    with metrics_lock:

        total = total_requests
        success = successful_requests
        failed = failed_requests
        active = active_requests

        times = list(request_times)

    if times:

        average_latency = sum(times) / len(times)

        min_latency = min(times)

        max_latency = max(times)

    else:

        average_latency = 0
        min_latency = 0
        max_latency = 0

    return {
        "total_requests": total,
        "successful_requests": success,
        "failed_requests": failed,
        "active_requests": active,
        "average_latency_ms": round(average_latency, 2),
        "min_latency_ms": round(min_latency, 2),
        "max_latency_ms": round(max_latency, 2),
    }


# ---------------------------------------------------------
# Generate traffic
# ---------------------------------------------------------

@app.get("/test")

async def test_endpoint():

    return {
        "status": "ok",
        "message": "Test request successful"
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")

async def health():

    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)