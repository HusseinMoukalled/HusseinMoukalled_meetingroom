from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users_service.app.routers import users
from shared.database import Base, engine
import users_service.app.models

# Create database tables (only if not in test mode)
import os
if os.getenv("TESTING") != "true":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Database might not be available during import

app = FastAPI(
    title="Users Service",
    description="Service for managing user accounts, authentication, and user-related operations",
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

app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    """
    Root endpoint for the Users Service.
    
    Returns:
        dict: Service information
    """
    return {
        "service": "Users Service",
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
