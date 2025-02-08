from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

CHAT_MESSAGES = Counter(
    'chat_messages_total',
    'Total chat messages processed',
    ['instance_id', 'status']
)

LLM_LATENCY = Histogram(
    'llm_request_duration_seconds',
    'LLM request latency'
)

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response 