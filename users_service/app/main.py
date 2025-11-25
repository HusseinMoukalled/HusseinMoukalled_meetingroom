from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from users_service.app.routers import users
from shared.database import Base, engine
from shared.rate_limiter import rate_limit_middleware
from shared.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    BaseAPIException
)
from shared.api_versioning import version_header_middleware
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

# Add custom exception handlers
app.add_exception_handler(BaseAPIException, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Add middleware (order matters: rate limit -> version header -> CORS)
# Rate limit needs to run first to add version header to 429 responses
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
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(users.router, prefix="/users", tags=["Users"])  # Default to v1

# Add circuit breaker status endpoint
from shared.circuit_breaker_status import router as cb_router
app.include_router(cb_router, prefix="/circuit-breaker", tags=["Circuit Breaker"])

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
