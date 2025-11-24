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
from typing import List, Dict, Optional
import json
import os
from jose import jwt

SERVICES = {
    "users": "http://localhost:8001",
    "rooms": "http://localhost:8002",
    "bookings": "http://localhost:8003",
    "reviews": "http://localhost:8004"
}

SECRET_KEY = "supersecretkey"

def decode_username_from_token(token: str) -> Optional[str]:
    """Extract username from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except:
        return None

def print_performance_result(result: Dict):
    """Print performance results."""
    if result.get('successful_requests', 0) > 0:
        print(f"   Average: {result.get('avg_response_time_ms', 0):.2f} ms | "
              f"Min: {result.get('min_response_time_ms', 0):.2f} ms | "
              f"Max: {result.get('max_response_time_ms', 0):.2f} ms | "
              f"Success Rate: {result.get('success_rate', 0):.1f}%")
    else:
        print(f"   No successful requests | Errors: {result.get('errors', 0)}/{result.get('iterations', 0)}")

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
        url: Endpoint URL
        headers: Request headers
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
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            if response.status_code < 400:
                response_times.append(response_time)
            else:
                errors += 1
                
        except Exception as e:
            errors += 1
    
    if not response_times:
        return {
            "url": url,
            "method": method,
            "iterations": iterations,
            "successful_requests": 0,
            "errors": errors,
            "success_rate": 0,
            "avg_response_time_ms": 0,
            "min_response_time_ms": 0,
            "max_response_time_ms": 0,
            "median_response_time_ms": 0,
            "std_deviation_ms": 0
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

def setup_test_data(admin_token: str, regular_token: str) -> Dict:
    """Create test data needed for profiling."""
    print("\nSetting up test data...")
    test_data = {
        "room_id": None,
        "booking_id": None,
        "review_id": None,
        "regular_username": None,
        "admin_username": None
    }
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    regular_headers = {"Authorization": f"Bearer {regular_token}"}
    
    timestamp = int(time.time())
    
    try:
        regular_username = decode_username_from_token(regular_token) or f"perfuser{timestamp}"
        admin_username = decode_username_from_token(admin_token) or f"perfadmin{timestamp}"
        test_data["regular_username"] = regular_username
        test_data["admin_username"] = admin_username
        
        room_response = requests.post(
            f"{SERVICES['rooms']}/rooms/add",
            headers=admin_headers,
            json={
                "name": f"Performance Test Room {timestamp}",
                "capacity": 20,
                "equipment": "Projector, Whiteboard, TV",
                "location": "Building A, Floor 2"
            },
            timeout=10
        )
        if room_response.status_code == 201:
            test_data["room_id"] = room_response.json().get("id")
            print(f"   Created room with ID: {test_data['room_id']}")
        
        if test_data["room_id"]:
            booking_response = requests.post(
                f"{SERVICES['bookings']}/bookings/create",
                headers=regular_headers,
                json={
                    "username": regular_username,
                    "room_id": test_data["room_id"],
                    "date": "2025-12-31",
                    "start_time": "14:00:00",
                    "end_time": "15:00:00"
                },
                timeout=10
            )
            if booking_response.status_code == 201:
                test_data["booking_id"] = booking_response.json().get("id")
                print(f"   Created booking with ID: {test_data['booking_id']}")
            
            review_response = requests.post(
                f"{SERVICES['reviews']}/reviews/create",
                headers=regular_headers,
                json={
                    "username": regular_username,
                    "room_id": test_data["room_id"],
                    "rating": 5,
                    "comment": "Excellent room for meetings"
                },
                timeout=10
            )
            if review_response.status_code == 201:
                test_data["review_id"] = review_response.json().get("id")
                print(f"   Created review with ID: {test_data['review_id']}")
        
        print("   Test data setup complete\n")
    except Exception as e:
        print(f"   Warning: Some test data setup failed: {e}\n")
    
    return test_data

def profile_users_service(access_token: str, admin_token: str) -> List[Dict]:
    """Profile all Users Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING USERS SERVICE")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    results = []
    timestamp = int(time.time())
    
    print("\n1. Testing POST /users/register...")
    unique_username = f"perfreg{timestamp}"
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['users']}/users/register",
        headers={},
        data={
            "name": "Performance Test User",
            "username": unique_username,
            "email": f"perf{timestamp}@test.com",
            "password": "test123",
            "role": "regular_user"
        },
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n2. Testing POST /users/login...")
    username = decode_username_from_token(access_token) or "perfuser"
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['users']}/users/login",
        headers={},
        data={"username": username, "password": "test123"},
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n3. Testing GET /users/{username}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['users']}/users/{username}",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n4. Testing GET /users/ (Admin only)...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['users']}/users/",
        headers=admin_headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n5. Testing PUT /users/{username} (Update profile)...")
    result = measure_endpoint_performance(
        "PUT",
        f"{SERVICES['users']}/users/{username}",
        headers=headers,
        data={"name": "Updated Name", "email": f"updated{timestamp}@test.com"},
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n6. Testing PUT /users/{username}/role (Admin only)...")
    result = measure_endpoint_performance(
        "PUT",
        f"{SERVICES['users']}/users/{username}/role",
        headers=admin_headers,
        data={"role": "regular_user"},
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n7. Testing GET /users/{username}/bookings (Booking history)...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['users']}/users/{username}/bookings",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    return results

def profile_rooms_service(access_token: str, admin_token: str, room_id: int) -> List[Dict]:
    """Profile all Rooms Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING ROOMS SERVICE")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    results = []
    timestamp = int(time.time())
    
    print("\n1. Testing POST /rooms/add (Admin only)...")
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['rooms']}/rooms/add",
        headers=admin_headers,
        data={
            "name": f"Perf Room {timestamp}",
            "capacity": 15,
            "equipment": "Projector",
            "location": "Building B"
        },
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n2. Testing GET /rooms/...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n3. Testing GET /rooms/available...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/available",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n4. Testing GET /rooms/available?capacity=10...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/available?capacity=10",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n5. Testing GET /rooms/status/{room_id}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/status/{room_id}",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n6. Testing GET /rooms/{room_id}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['rooms']}/rooms/{room_id}",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n7. Testing PUT /rooms/update/{room_id} (Admin only)...")
    result = measure_endpoint_performance(
        "PUT",
        f"{SERVICES['rooms']}/rooms/update/{room_id}",
        headers=admin_headers,
        data={"capacity": 25, "is_available": True},
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    return results

def profile_bookings_service(access_token: str, admin_token: str, room_id: int, username: str) -> List[Dict]:
    """Profile all Bookings Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING BOOKINGS SERVICE")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    results = []
    timestamp = int(time.time())
    
    print("\n1. Testing GET /bookings/check...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['bookings']}/bookings/check?room_id={room_id}&date=2025-12-31&start_time=16:00:00&end_time=17:00:00",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n2. Testing POST /bookings/create...")
    hour = 18 + (timestamp % 5)
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['bookings']}/bookings/create",
        headers=headers,
        data={
            "username": username,
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": f"{hour}:00:00",
            "end_time": f"{hour+1}:00:00"
        },
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n3. Testing GET /bookings/user/{username}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['bookings']}/bookings/user/{username}",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n4. Testing GET /bookings/ (Admin only)...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['bookings']}/bookings/",
        headers=admin_headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n5. Testing GET /bookings/{booking_id}...")
    try:
        bookings_response = requests.get(
            f"{SERVICES['bookings']}/bookings/user/{username}",
            headers=headers,
            timeout=10
        )
        if bookings_response.status_code == 200 and bookings_response.json():
            booking_id = bookings_response.json()[0].get("id")
            if booking_id:
                result = measure_endpoint_performance(
                    "GET",
                    f"{SERVICES['bookings']}/bookings/{booking_id}",
                    headers=headers,
                    iterations=10
                )
                results.append(result)
                print_performance_result(result)
            else:
                print("   No bookings found to test")
        else:
            print("   No bookings found to test")
    except:
        print("   Could not retrieve booking ID")
    
    print("\n6. Testing PUT /bookings/{booking_id} (Update booking)...")
    try:
        bookings_response = requests.get(
            f"{SERVICES['bookings']}/bookings/user/{username}",
            headers=headers,
            timeout=10
        )
        if bookings_response.status_code == 200 and bookings_response.json():
            booking_id = bookings_response.json()[0].get("id")
            if booking_id:
                result = measure_endpoint_performance(
                    "PUT",
                    f"{SERVICES['bookings']}/bookings/{booking_id}",
                    headers=headers,
                    data={"start_time": "19:00:00", "end_time": "20:00:00"},
                    iterations=5
                )
                results.append(result)
                print_performance_result(result)
            else:
                print("   No bookings found to test")
        else:
            print("   No bookings found to test")
    except:
        print("   Could not retrieve booking ID")
    
    return results

def profile_reviews_service(access_token: str, moderator_token: str, room_id: int, username: str) -> List[Dict]:
    """Profile all Reviews Service endpoints."""
    print("\n" + "="*60)
    print("PROFILING REVIEWS SERVICE")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    moderator_headers = {"Authorization": f"Bearer {moderator_token}"}
    results = []
    timestamp = int(time.time())
    
    print("\n1. Testing GET /reviews/room/{room_id}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['reviews']}/reviews/room/{room_id}",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n2. Testing POST /reviews/create...")
    result = measure_endpoint_performance(
        "POST",
        f"{SERVICES['reviews']}/reviews/create",
        headers=headers,
        data={
            "username": username,
            "room_id": room_id,
            "rating": 4,
            "comment": f"Performance test review {timestamp}"
        },
        iterations=5
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n3. Testing GET /reviews/all...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['reviews']}/reviews/all",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n4. Testing GET /reviews/user/{username}...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['reviews']}/reviews/user/{username}",
        headers=headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n5. Testing GET /reviews/{review_id}...")
    try:
        reviews_response = requests.get(
            f"{SERVICES['reviews']}/reviews/room/{room_id}",
            headers=headers,
            timeout=10
        )
        if reviews_response.status_code == 200 and reviews_response.json():
            review_id = reviews_response.json()[0].get("id")
            if review_id:
                result = measure_endpoint_performance(
                    "GET",
                    f"{SERVICES['reviews']}/reviews/{review_id}",
                    headers=headers,
                    iterations=10
                )
                results.append(result)
                print_performance_result(result)
            else:
                print("   No reviews found to test")
        else:
            print("   No reviews found to test")
    except:
        print("   Could not retrieve review ID")
    
    print("\n6. Testing PUT /reviews/{review_id} (Update review)...")
    try:
        reviews_response = requests.get(
            f"{SERVICES['reviews']}/reviews/room/{room_id}",
            headers=headers,
            timeout=10
        )
        if reviews_response.status_code == 200 and reviews_response.json():
            review_id = reviews_response.json()[0].get("id")
            if review_id:
                result = measure_endpoint_performance(
                    "PUT",
                    f"{SERVICES['reviews']}/reviews/{review_id}",
                    headers=headers,
                    data={"rating": 5, "comment": "Updated review comment"},
                    iterations=5
                )
                results.append(result)
                print_performance_result(result)
            else:
                print("   No reviews found to test")
        else:
            print("   No reviews found to test")
    except:
        print("   Could not retrieve review ID")
    
    print("\n7. Testing POST /reviews/{review_id}/flag...")
    try:
        reviews_response = requests.get(
            f"{SERVICES['reviews']}/reviews/room/{room_id}",
            headers=headers,
            timeout=10
        )
        if reviews_response.status_code == 200 and reviews_response.json():
            review_id = reviews_response.json()[0].get("id")
            if review_id:
                result = measure_endpoint_performance(
                    "POST",
                    f"{SERVICES['reviews']}/reviews/{review_id}/flag",
                    headers=headers,
                    data={"reason": "Test flagging"},
                    iterations=5
                )
                results.append(result)
                print_performance_result(result)
            else:
                print("   No reviews found to test")
        else:
            print("   No reviews found to test")
    except:
        print("   Could not retrieve review ID")
    
    print("\n8. Testing GET /reviews/flagged/all (Moderator only)...")
    result = measure_endpoint_performance(
        "GET",
        f"{SERVICES['reviews']}/reviews/flagged/all",
        headers=moderator_headers,
        iterations=10
    )
    results.append(result)
    print_performance_result(result)
    
    print("\n9. Testing POST /reviews/{review_id}/unflag (Moderator only)...")
    try:
        flagged_response = requests.get(
            f"{SERVICES['reviews']}/reviews/flagged/all",
            headers=moderator_headers,
            timeout=10
        )
        if flagged_response.status_code == 200 and flagged_response.json():
            review_id = flagged_response.json()[0].get("id")
            if review_id:
                result = measure_endpoint_performance(
                    "POST",
                    f"{SERVICES['reviews']}/reviews/{review_id}/unflag",
                    headers=moderator_headers,
                    iterations=5
                )
                results.append(result)
                print_performance_result(result)
            else:
                print("   No flagged reviews found to test")
        else:
            print("   No flagged reviews found to test")
    except:
        print("   Could not retrieve flagged review ID")
    
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

def get_auth_tokens():
    """Get authentication tokens for testing."""
    tokens = {}
    timestamp = int(time.time())
    
    try:
        register_response = requests.post(
            f"{SERVICES['users']}/users/register",
            json={
                "name": "Performance Test User",
                "username": f"perfuser{timestamp}",
                "email": f"perf{timestamp}@test.com",
                "password": "test123",
                "role": "regular_user"
            },
            timeout=10
        )
        if register_response.status_code == 201:
            username = register_response.json()["username"]
            login_response = requests.post(
                f"{SERVICES['users']}/users/login",
                json={"username": username, "password": "test123"},
                timeout=10
            )
            if login_response.status_code == 200:
                tokens["regular"] = login_response.json()["access_token"]
                tokens["regular_username"] = username
        
        admin_register = requests.post(
            f"{SERVICES['users']}/users/register",
            json={
                "name": "Performance Test Admin",
                "username": f"perfadmin{timestamp}",
                "email": f"perfadmin{timestamp}@test.com",
                "password": "test123",
                "role": "admin"
            },
            timeout=10
        )
        if admin_register.status_code == 201:
            admin_username = admin_register.json()["username"]
            admin_login = requests.post(
                f"{SERVICES['users']}/users/login",
                json={"username": admin_username, "password": "test123"},
                timeout=10
            )
            if admin_login.status_code == 200:
                tokens["admin"] = admin_login.json()["access_token"]
                tokens["admin_username"] = admin_username
        
        mod_register = requests.post(
            f"{SERVICES['users']}/users/register",
            json={
                "name": "Performance Test Moderator",
                "username": f"perfmod{timestamp}",
                "email": f"perfmod{timestamp}@test.com",
                "password": "test123",
                "role": "moderator"
            },
            timeout=10
        )
        if mod_register.status_code == 201:
            mod_username = mod_register.json()["username"]
            mod_login = requests.post(
                f"{SERVICES['users']}/users/login",
                json={"username": mod_username, "password": "test123"},
                timeout=10
            )
            if mod_login.status_code == 200:
                tokens["moderator"] = mod_login.json()["access_token"]
                tokens["moderator_username"] = mod_username
    except Exception as e:
        print(f"Warning: Could not get auth tokens: {e}")
    
    return tokens

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 15 + "PERFORMANCE PROFILING TOOL")
    print(" " * 10 + "Hussein's Meeting Room Management System")
    print("="*70)
    print("\nIMPORTANT: Make sure all services are running!")
    print("Services should be available at:")
    print("  - Users Service:    http://localhost:8001")
    print("  - Rooms Service:     http://localhost:8002")
    print("  - Bookings Service:  http://localhost:8003")
    print("  - Reviews Service:   http://localhost:8004")
    print("\n" + "="*70 + "\n")
    
    print("Obtaining authentication tokens...")
    tokens = get_auth_tokens()
    if tokens:
        print(f"  Regular user token: {'Obtained' if 'regular' in tokens else 'Failed'}")
        print(f"  Admin token: {'Obtained' if 'admin' in tokens else 'Failed'}")
        print(f"  Moderator token: {'Obtained' if 'moderator' in tokens else 'Failed'}")
    print()
    
    if not tokens.get("regular") or not tokens.get("admin"):
        print("ERROR: Could not obtain required authentication tokens.")
        print("Please ensure services are running and accessible.")
        exit(1)
    
    test_data = setup_test_data(tokens.get("admin"), tokens.get("regular"))
    room_id = test_data.get("room_id") or 1
    username = tokens.get("regular_username") or decode_username_from_token(tokens.get("regular")) or "perfuser"
    
    all_results = []
    
    all_results.extend(profile_users_service(
        tokens.get("regular"),
        tokens.get("admin")
    ))
    all_results.extend(profile_rooms_service(
        tokens.get("regular"),
        tokens.get("admin"),
        room_id
    ))
    all_results.extend(profile_bookings_service(
        tokens.get("regular"),
        tokens.get("admin"),
        room_id,
        username
    ))
    all_results.extend(profile_reviews_service(
        tokens.get("regular"),
        tokens.get("moderator"),
        room_id,
        username
    ))
    
    report = generate_performance_report(all_results)
    print(report)
    
    os.makedirs("profiling", exist_ok=True)
    with open("profiling/performance_report.txt", "w") as f:
        f.write(report)
    
    print("\n" + "="*70)
    print("Performance profiling completed!")
    print("Report saved to: profiling/performance_report.txt")
    print("="*70 + "\n")
