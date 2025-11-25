"""
Rate Limiting and Throttling
============================

Implements rate limiting to prevent API abuse and ensure fair resource usage.
"""

from collections import defaultdict
from time import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Tuple


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    
    Tracks requests per client (IP address) and endpoint.
    """
    
    def __init__(self):
        """Initialize rate limiter with empty request tracking."""
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int]:
        """
        Check if request is allowed within rate limit.
        
        Args:
            key: Unique identifier (e.g., "IP:endpoint")
            limit: Maximum number of requests
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time()
        request_times = self.requests[key]
        
        # Remove old requests outside the window
        request_times[:] = [t for t in request_times if now - t < window]
        
        # Check if limit exceeded
        if len(request_times) >= limit:
            return False, 0
        
        # Add current request
        request_times.append(now)
        remaining = limit - len(request_times)
        return True, remaining
    
    def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests for a key."""
        now = time()
        request_times = self.requests[key]
        request_times[:] = [t for t in request_times if now - t < window]
        return max(0, limit - len(request_times))


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    if request.client:
        return request.client.host
    return "unknown"


# Rate limit configurations per endpoint
RATE_LIMITS: Dict[str, Dict[str, int]] = {
    "/users/login": {"limit": 10, "window": 60},
    "/users/register": {"limit": 5, "window": 60},
    "/bookings/create": {"limit": 20, "window": 60},
    "/reviews/create": {"limit": 15, "window": 60},
}


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for FastAPI.
    
    Applies rate limits based on endpoint configuration.
    Returns 429 (Too Many Requests) when limit is exceeded.
    """
    path = str(request.url.path)
    
    # Check if endpoint has rate limiting configured
    if path in RATE_LIMITS:
        limit_config = RATE_LIMITS[path]
        client_ip = get_client_ip(request)
        key = f"{client_ip}:{path}"
        
        is_allowed, remaining = rate_limiter.is_allowed(
            key=key,
            limit=limit_config["limit"],
            window=limit_config["window"]
        )
        
        if not is_allowed:
            # Add API version header even for rate limited responses
            from shared.api_versioning import get_api_version
            version = get_api_version(request)
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": (
                        f"Rate limit exceeded. Maximum {limit_config['limit']} "
                        f"requests per {limit_config['window']} seconds. "
                        f"Please try again later."
                    ),
                    "retry_after": limit_config["window"]
                },
                headers={
                    "X-RateLimit-Limit": str(limit_config["limit"]),
                    "X-RateLimit-Window": str(limit_config["window"]),
                    "Retry-After": str(limit_config["window"]),
                    "API-Version": version
                }
            )
            return response
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit_config["limit"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(limit_config["window"])
        return response
    
    return await call_next(request)

