from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bookings_service.app.routers import bookings
from shared.database import Base, engine
import bookings_service.app.models
import users_service.app.models
import rooms_service.app.models

# Create database tables (only if not in test mode)
import os
if os.getenv("TESTING") != "true":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Database might not be available during import

app = FastAPI(
    title="Bookings Service",
    description="Service for managing meeting room bookings, availability checks, and booking history",
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

app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

@app.get("/")
def root():
    """
    Root endpoint for the Bookings Service.
    
    Returns:
        dict: Service information
    """
    return {
        "service": "Bookings Service",
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
