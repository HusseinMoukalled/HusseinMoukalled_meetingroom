"""
Memory Profiling Script
=======================

This script profiles memory usage of the application using memory-profiler.

Author: Hussein Moukalled
Date: Fall 2025-2026

Usage:
    python -m memory_profiler profiling/memory_profiler.py
"""

import psutil
import os
import time
import requests
from typing import Dict

def get_memory_usage() -> Dict:
    """
    Get current memory usage statistics.
    
    Returns:
        Dictionary with memory statistics
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
        "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
        "percent": process.memory_percent()
    }

def test_users_endpoints():
    """Test users service endpoints and profile memory."""
    base_url = "http://localhost:8001"
    
    # Register user
    response = requests.post(
        f"{base_url}/users/register",
        json={
            "name": "Memory Test User",
            "username": f"memtest{int(time.time())}",
            "email": f"memtest{int(time.time())}@example.com",
            "password": "test123",
            "role": "regular_user"
        }
    )
    
    # Login
    if response.status_code == 201:
        username = response.json()["username"]
        login_response = requests.post(
            f"{base_url}/users/login",
            json={
                "username": username,
                "password": "test123"
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get user
            requests.get(f"{base_url}/users/{username}", headers=headers)
            
            # Get all users (if admin)
            requests.get(f"{base_url}/users/", headers=headers)

def test_rooms_endpoints():
    """Test rooms service endpoints and profile memory."""
    base_url = "http://localhost:8002"
    
    # Get all rooms
    requests.get(f"{base_url}/rooms/")
    
    # Get available rooms
    requests.get(f"{base_url}/rooms/available")
    
    # Get room status
    requests.get(f"{base_url}/rooms/status/1")

def test_bookings_endpoints():
    """Test bookings service endpoints and profile memory."""
    base_url = "http://localhost:8003"
    
    # Check availability
    requests.get(
        f"{base_url}/bookings/check",
        params={
            "room_id": 1,
            "date": "2025-12-31",
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    )

def test_reviews_endpoints():
    """Test reviews service endpoints and profile memory."""
    base_url = "http://localhost:8004"
    
    # Get reviews for room
    requests.get(f"{base_url}/reviews/room/1")

def generate_memory_report():
    """Generate a memory profiling report."""
    print("\n" + "="*60)
    print("MEMORY PROFILING REPORT")
    print("="*60 + "\n")
    
    print("Initial Memory Usage:")
    initial = get_memory_usage()
    print(f"  RSS: {initial['rss_mb']:.2f} MB")
    print(f"  VMS: {initial['vms_mb']:.2f} MB")
    print(f"  Percent: {initial['percent']:.2f}%\n")
    
    print("Testing Users Service...")
    test_users_endpoints()
    
    print("\nTesting Rooms Service...")
    test_rooms_endpoints()
    
    print("\nTesting Bookings Service...")
    test_bookings_endpoints()
    
    print("\nTesting Reviews Service...")
    test_reviews_endpoints()
    
    print("\nFinal Memory Usage:")
    final = get_memory_usage()
    print(f"  RSS: {final['rss_mb']:.2f} MB")
    print(f"  VMS: {final['vms_mb']:.2f} MB")
    print(f"  Percent: {final['percent']:.2f}%")
    print(f"  Memory Increase: {final['rss_mb'] - initial['rss_mb']:.2f} MB")

if __name__ == "__main__":
    print("Starting Memory Profiling...")
    print("Make sure all services are running on localhost:8001-8004")
    print("\nNote: Run this script with: python -m memory_profiler profiling/memory_profiler.py")
    
    generate_memory_report()

