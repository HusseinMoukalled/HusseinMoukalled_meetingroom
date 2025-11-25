from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from rooms_service.app.routers import rooms
from shared.database import Base, engine
from shared.rate_limiter import rate_limit_middleware
from shared.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    BaseAPIException
)
from shared.api_versioning import version_header_middleware
import rooms_service.app.models

# Create database tables (only if not in test mode)
import os
if os.getenv("TESTING") != "true":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass  # Database might not be available during import

app = FastAPI(
    title="Rooms Service",
    description="Service for managing meeting rooms, availability, and room-related operations",
    version="1.0.0"
)

# Add custom exception handlers
app.add_exception_handler(BaseAPIException, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add middleware (order matters: rate limit -> version header -> CORS)
@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

@app.middleware("http")
async def add_version_header(request: Request, call_next):
    return await version_header_middleware(request, call_next)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with versioning support
app.include_router(rooms.router, prefix="/v1/rooms", tags=["Rooms"])
app.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])  # Default to v1

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
