from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import chat_routes, instance_routes
from app.core.exceptions import setup_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Setup exception handlers
setup_exception_handlers(app)

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 