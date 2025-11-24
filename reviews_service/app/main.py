from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.database import Base, engine
from reviews_service.app.routers.reviews import router

import users_service.app.models
import rooms_service.app.models
import reviews_service.app.models

# Create database tables (only if not in test mode)
import os
if os.getenv("TESTING") != "true":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Database might not be available during import

app = FastAPI(
    title="Reviews Service",
    description="Service for managing room reviews, ratings, and moderation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/reviews", tags=["Reviews"])

@app.get("/")
def root():
    """
    Root endpoint for the Reviews Service.
    
    Returns:
        dict: Service information
    """
    return {
        "service": "Reviews Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy"}
