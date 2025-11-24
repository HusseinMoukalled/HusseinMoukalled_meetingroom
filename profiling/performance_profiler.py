"""
Performance Profiling Script
=============================

This script profiles the performance of API endpoints by measuring response times,
throughput, and identifying bottlenecks.

Author: Hussein Moukalled
Date: Fall 2025-2026
"""

import time
import statistics
import requests
from typing import List, Dict
import json

# Base URLs for services
SERVICES = {
    "users": "http://localhost:8001",
    "rooms": "http://localhost:8002",
    "bookings": "http://localhost:8003",
    "reviews": "http://localhost:8004"
}

def measure_endpoint_performance(
    method: str,
    url: str,
    headers: Dict = None,
    data: Dict = None,
    iterations: int = 10
) -> Dict:
    """
    Measure the performance of an API endpoint.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request data (for POST/PUT)
        iterations: Number of times to test
        
    Returns:
        Dictionary with performance metrics
    """
    response_times = []
    errors = 0
    
    for i in range(iterations):
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code < 400:
                response_times.append(response_time)
            else:
                errors += 1
                
        except Exception as e:
            errors += 1
            print(f"Error on iteration {i+1}: {e}")
    
    if not response_times:
        return {
            "url": url,
            "method": method,
            "iterations": iterations,
            "errors": errors,
            "success_rate": 0,
            "avg_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
            "median_response_time": 0
        }
    
    return {
        "url": url,
        "method": method,
        "iterations": iterations,
        "successful_requests": len(response_times),
        "errors": errors,
        "success_rate": (len(response_times) / iterations) * 100,
        "avg_response_time_ms": statistics.mean(response_times),
        "min_response_time_ms": min(response_times),
        "max_response_time_ms": max(response_times),
        "median_response_time_ms": statistics.median(response_times),
        "std_deviation_ms": statistics.stdev(response_times) if len(response_times) > 1 else 0
    }

def profile_users_service(access_token: str = None) -> List[Dict]:
    """Profile all Users Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING USERS SERVICE")
    print("="*60)
    
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    results = []
    
    # Register endpoint
    print("\n1. Testing POST /users/register...")
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['users']}/users/register",
        headers=headers,
        data={
            "name": "Test User",
            "username": f"testuser{int(time.time())}",
            "email": f"test{int(time.time())}@example.com",
            "password": "test123",
            "role": "regular_user"
        },
        iterations=5
    )
    results.append(result)
    print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    # Login endpoint
    print("\n2. Testing POST /users/login...")
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['users']}/users/login",
        headers=headers,
        data={
            "username": "testuser",
            "password": "test123"
        },
        iterations=10
    )
    results.append(result)
    print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    # Get user endpoint
    if access_token:
        print("\n3. Testing GET /users/{{username}}...")
        result = measure_endpoint_performance(
            "GET",
            f"{SERVICES['users']}/users/testuser",
            headers=headers,
            iterations=10
        )
        results.append(result)
        print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    return results

def profile_rooms_service(access_token: str = None) -> List[Dict]:
    """Profile all Rooms Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING ROOMS SERVICE")
    print("="*60)
    
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    results = []
    
    # Get all rooms
    print("\n1. Testing GET /rooms/...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    # Get available rooms
    print("\n2. Testing GET /rooms/available...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/available",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    return results

def profile_bookings_service(access_token: str = None) -> List[Dict]:
    """Profile all Bookings Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING BOOKINGS SERVICE")
    print("="*60)
    
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    results = []
    
    # Check availability
    print("\n1. Testing GET /bookings/check...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['bookings']}/bookings/check?room_id=1&date=2025-12-31&start_time=10:00:00&end_time=11:00:00",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    return results

def profile_reviews_service(access_token: str = None) -> List[Dict]:
    """Profile all Reviews Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING REVIEWS SERVICE")
    print("="*60)
    
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    results = []
    
    # Get reviews for room
    print("\n1. Testing GET /reviews/room/{{room_id}}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['reviews']}/reviews/room/1",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print(f"   Average response time: {result['avg_response_time_ms']:.2f} ms")
    
    return results

def generate_performance_report(results: List[Dict]) -> str:
    """Generate a formatted performance report."""
    report = "\n" + "="*60 + "\n"
    report += "PERFORMANCE PROFILING REPORT\n"
    report += "="*60 + "\n\n"
    
    for result in results:
        report += f"Endpoint: {result['method']} {result['url']}\n"
        report += f"  Iterations: {result['iterations']}\n"
        report += f"  Success Rate: {result['success_rate']:.2f}%\n"
        report += f"  Average Response Time: {result['avg_response_time_ms']:.2f} ms\n"
        report += f"  Min Response Time: {result['min_response_time_ms']:.2f} ms\n"
        report += f"  Max Response Time: {result['max_response_time_ms']:.2f} ms\n"
        report += f"  Median Response Time: {result['median_response_time_ms']:.2f} ms\n"
        if 'std_deviation_ms' in result:
            report += f"  Standard Deviation: {result['std_deviation_ms']:.2f} ms\n"
        report += "\n"
    
    return report

if __name__ == "__main__":
    print("Starting Performance Profiling...")
    print("Make sure all services are running on localhost:8001-8004")
    
    all_results = []
    
    # Profile all services
    all_results.extend(profile_users_service())
    all_results.extend(profile_rooms_service())
    all_results.extend(profile_bookings_service())
    all_results.extend(profile_reviews_service())
    
    # Generate report
    report = generate_performance_report(all_results)
    print(report)
    
    # Save to file
    with open("profiling/performance_report.txt", "w") as f:
        f.write(report)
    
    print("Performance report saved to profiling/performance_report.txt")

