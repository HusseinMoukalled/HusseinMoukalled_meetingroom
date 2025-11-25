"""
Inter-Service Communication Client
===================================

Client for making HTTP requests to other services with circuit breaker protection.
"""

import requests
from typing import Optional, Dict, Any
from shared.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenError
from shared.exceptions import ServiceUnavailableException
import logging

logger = logging.getLogger(__name__)


class InterServiceClient:
    """
    HTTP client for inter-service communication with circuit breaker.
    
    Automatically applies circuit breaker pattern to prevent cascading failures.
    """
    
    def __init__(self, service_name: str, base_url: str, timeout: int = 5):
        """
        Initialize inter-service client.
        
        Args:
            service_name: Name of the target service
            base_url: Base URL of the target service
            timeout: Request timeout in seconds
        """
        self.service_name = service_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.circuit_breaker = get_circuit_breaker(service_name)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with circuit breaker protection.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request arguments
            
        Returns:
            Response object
            
        Raises:
            ServiceUnavailableException: If circuit breaker is open
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        def request_func():
            return requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
        
        try:
            response = self.circuit_breaker.call(request_func)
            return response
        except CircuitBreakerOpenError:
            logger.warning(
                f"Circuit breaker open for {self.service_name}. "
                f"Request to {url} blocked."
            )
            raise ServiceUnavailableException(
                service=self.service_name,
                message=f"Service {self.service_name} is currently unavailable"
            )
        except requests.RequestException as e:
            logger.error(f"Request to {self.service_name} failed: {str(e)}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self._make_request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make POST request."""
        if json:
            kwargs['json'] = json
        return self._make_request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PUT request."""
        if json:
            kwargs['json'] = json
        return self._make_request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def get_circuit_breaker_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return self.circuit_breaker.get_state()


# Pre-configured clients for each service
def get_users_service_client() -> InterServiceClient:
    """Get client for Users Service."""
    return InterServiceClient(
        service_name="users_service",
        base_url="http://users_service:8001"
    )


def get_rooms_service_client() -> InterServiceClient:
    """Get client for Rooms Service."""
    return InterServiceClient(
        service_name="rooms_service",
        base_url="http://rooms_service:8002"
    )


def get_bookings_service_client() -> InterServiceClient:
    """Get client for Bookings Service."""
    return InterServiceClient(
        service_name="bookings_service",
        base_url="http://bookings_service:8003"
    )


def get_reviews_service_client() -> InterServiceClient:
    """Get client for Reviews Service."""
    return InterServiceClient(
        service_name="reviews_service",
        base_url="http://reviews_service:8004"
    )

