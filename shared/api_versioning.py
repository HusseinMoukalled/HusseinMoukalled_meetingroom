"""
API Versioning
==============

Implements API versioning to ensure backward compatibility.
Supports URL-based versioning (e.g., /v1/users, /v2/users).
"""

from fastapi import APIRouter, Request
from fastapi.routing import APIRoute
from typing import Callable
import re


class VersionedAPIRouter(APIRouter):
    """
    Extended APIRouter that supports API versioning.
    
    Routes can be versioned by prefixing with version number.
    """
    
    def __init__(self, *args, default_version: str = "v1", **kwargs):
        """
        Initialize versioned router.
        
        Args:
            default_version: Default API version if not specified
            *args: Arguments passed to APIRouter
            **kwargs: Keyword arguments passed to APIRouter
        """
        self.default_version = default_version
        super().__init__(*args, **kwargs)
    
    def versioned_route(
        self,
        path: str,
        version: str = None,
        **kwargs
    ) -> Callable:
        """
        Create a versioned route.
        
        Args:
            path: Route path (without version prefix)
            version: API version (e.g., "v1", "v2")
            **kwargs: Additional route arguments
            
        Returns:
            Route decorator
        """
        version = version or self.default_version
        
        # Add version prefix to path
        versioned_path = f"/{version}{path}"
        
        # Also add route without version (defaults to default_version)
        if version == self.default_version:
            # Register both versioned and unversioned paths
            def decorator(func: Callable) -> Callable:
                # Add versioned route
                self.add_api_route(versioned_path, func, **kwargs)
                # Add unversioned route (defaults to default version)
                self.add_api_route(path, func, **kwargs)
                return func
            return decorator
        else:
            # Only add versioned route for non-default versions
            def decorator(func: Callable) -> Callable:
                self.add_api_route(versioned_path, func, **kwargs)
                return func
            return decorator


def get_api_version(request: Request) -> str:
    """
    Extract API version from request path.
    
    Args:
        request: FastAPI request object
        
    Returns:
        API version string (e.g., "v1", "v2") or default version
    """
    path = str(request.url.path)
    
    # Match version pattern: /v1/, /v2/, etc.
    match = re.match(r'^/(v\d+)/', path)
    if match:
        return match.group(1)
    
    return "v1"  # Default version


async def version_header_middleware(request: Request, call_next):
    """
    Middleware to add API version to response headers.
    """
    version = get_api_version(request)
    response = await call_next(request)
    response.headers["API-Version"] = version
    return response

