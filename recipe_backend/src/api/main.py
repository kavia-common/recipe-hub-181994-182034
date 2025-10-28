from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure DB layer imports fine (Base, SessionLocal)
from src.db.session import SessionLocal  # noqa: F401
from src.db.base import Base  # noqa: F401

app = FastAPI(
    title="Recipe Backend API",
    description="API for managing users, recipes, tags, and favorites.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Simple health check endpoint to verify the service is running."""
    return {"message": "Healthy"}
