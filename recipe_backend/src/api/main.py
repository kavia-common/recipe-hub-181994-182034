from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure DB layer imports fine (Base, SessionLocal)
from src.db.session import SessionLocal  # noqa: F401
from src.db.base import Base  # noqa: F401

from src.core.config import get_settings
from src.api.routers.auth import router as auth_router
from src.api.routers.recipes import router as recipes_router
from src.api.routers.favorites import router as favorites_router

app = FastAPI(
    title="Recipe Backend API",
    description="API for managing users, recipes, tags, and favorites.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "recipes", "description": "Recipe CRUD and search"},
        {"name": "favorites", "description": "Favorite management"},
    ],
)

# CORS configuration: allow common frontend default; can be extended via env later
settings = get_settings()
default_origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Simple health check endpoint to verify the service is running."""
    return {"message": "Healthy"}


# Mount routers
app.include_router(auth_router)
app.include_router(recipes_router)
app.include_router(favorites_router)
