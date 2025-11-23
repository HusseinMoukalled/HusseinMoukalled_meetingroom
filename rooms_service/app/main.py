from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rooms_service.app.routers import rooms
from shared.database import Base, engine
import rooms_service.app.models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rooms Service",
    description="Service for managing meeting rooms, availability, and room-related operations",
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

app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])

@app.get("/")
def root():
    """
    Root endpoint for the Rooms Service.
    
    Returns:
        dict: Service information
    """
    return {
        "service": "Rooms Service",
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
