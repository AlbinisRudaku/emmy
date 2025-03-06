from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.docs import setup_docs
from app.core.logging import RequestLoggingMiddleware, logger
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import RateLimitMiddleware
from app.api.routes import chat_routes, instance_routes, api_key_routes, auth_routes, profile_routes
from app.core.config import get_settings
from app.core.tasks import setup_periodic_tasks

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/api/v1/docs")

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

# Setup documentation
setup_docs(app)

# Setup middleware
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(
    chat_routes.router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["chat"]
)

app.include_router(
    instance_routes.router,
    prefix=f"{settings.API_V1_STR}/instances",
    tags=["instances"]
)

app.include_router(
    api_key_routes.router,
    prefix=f"{settings.API_V1_STR}/api-keys",
    tags=["api-keys"]
)

app.include_router(
    auth_routes.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)

app.include_router(
    profile_routes.router,
    prefix=f"{settings.API_V1_STR}/profiles",
    tags=["profiles"]
)

# Setup periodic tasks
setup_periodic_tasks(app)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down") 