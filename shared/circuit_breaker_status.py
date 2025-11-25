"""
Circuit Breaker Status Endpoint
================================

Provides endpoint to check circuit breaker status for all services.
"""

from fastapi import APIRouter
from shared.circuit_breaker import circuit_breakers
from typing import Dict, Any

router = APIRouter()


@router.get("/status")
def get_circuit_breaker_status() -> Dict[str, Any]:
    """
    Get status of all circuit breakers.
    
    Returns:
        Dictionary with circuit breaker states for all services
    """
    status = {}
    for service_name, circuit_breaker in circuit_breakers.items():
        status[service_name] = circuit_breaker.get_state()
    return {
        "circuit_breakers": status,
        "total_services": len(circuit_breakers)
    }

