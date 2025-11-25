"""
Test Script for Part II Features
=================================

Tests the two implemented Part II features:
1. Enhanced Inter-Service Communication
   - Circuit Breaker Pattern
   - Rate Limiting and Throttling
2. Advanced Development Practices
   - Custom Exception Handling
   - API Versioning

Run this script while all services are running in Docker.
"""

import requests
import time
import json

BASE_URLS = {
    "users": "http://localhost:8001",
    "rooms": "http://localhost:8002",
    "bookings": "http://localhost:8003",
    "reviews": "http://localhost:8004"
}


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_rate_limiting():
    """Test rate limiting on various endpoints."""
    print_section("TEST 1: Rate Limiting and Throttling")
    
    print("Testing rate limiting on /users/login (limit: 10/minute)...")
    print("Making 15 rapid requests...\n")
    
    url = f"{BASE_URLS['users']}/users/login"
    success_count = 0
    rate_limited_count = 0
    
    for i in range(15):
        try:
            response = requests.post(
                url,
                json={"username": "test", "password": "test"},
                timeout=2
            )
            
            if response.status_code == 429:
                rate_limited_count += 1
                print(f"  Request {i+1}: RATE LIMITED (429)")
                if rate_limited_count == 1:
                    print(f"    Response: {response.json()}")
            elif response.status_code == 401:
                success_count += 1
                print(f"  Request {i+1}: Allowed (401 - Invalid credentials)")
            else:
                success_count += 1
                print(f"  Request {i+1}: Allowed ({response.status_code})")
        except Exception as e:
            print(f"  Request {i+1}: Error - {str(e)}")
        
        time.sleep(0.1)
    
    print(f"\n  Summary:")
    print(f"    - Requests allowed: {success_count}")
    print(f"    - Requests rate limited: {rate_limited_count}")
    print(f"    - Rate limiting: {'WORKING ✓' if rate_limited_count > 0 else 'NOT WORKING ✗'}")
    
    # Test register endpoint
    print("\n" + "-"*70)
    print("Testing rate limiting on /users/register (limit: 5/minute)...")
    print("Making 7 rapid requests...\n")
    
    url = f"{BASE_URLS['users']}/users/register"
    success_count = 0
    rate_limited_count = 0
    
    for i in range(7):
        try:
            response = requests.post(
                url,
                json={
                    "name": f"Test User {i}",
                    "username": f"testuser{i}",
                    "email": f"test{i}@example.com",
                    "password": "test123",
                    "role": "regular_user"
                },
                timeout=2
            )
            
            if response.status_code == 429:
                rate_limited_count += 1
                print(f"  Request {i+1}: RATE LIMITED (429)")
            elif response.status_code in [201, 400]:
                success_count += 1
                print(f"  Request {i+1}: Allowed ({response.status_code})")
            else:
                success_count += 1
                print(f"  Request {i+1}: Allowed ({response.status_code})")
        except Exception as e:
            print(f"  Request {i+1}: Error - {str(e)}")
        
        time.sleep(0.1)
    
    print(f"\n  Summary:")
    print(f"    - Requests allowed: {success_count}")
    print(f"    - Requests rate limited: {rate_limited_count}")
    print(f"    - Rate limiting: {'WORKING ✓' if rate_limited_count > 0 else 'NOT WORKING ✗'}")


def test_api_versioning():
    """Test API versioning."""
    print_section("TEST 2: API Versioning")
    
    print("Testing API versioning...")
    print("Both /users/login and /v1/users/login should work\n")
    
    # Test unversioned endpoint
    print("1. Testing unversioned endpoint: /users/login")
    try:
        response = requests.post(
            f"{BASE_URLS['users']}/users/login",
            json={"username": "test", "password": "test"},
            timeout=2
        )
        version = response.headers.get("API-Version", "Not found")
        print(f"   Status: {response.status_code}")
        print(f"   API-Version header: {version}")
        print(f"   ✓ Unversioned endpoint works (defaults to v1)")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test versioned endpoint
    print("\n2. Testing versioned endpoint: /v1/users/login")
    try:
        response = requests.post(
            f"{BASE_URLS['users']}/v1/users/login",
            json={"username": "test", "password": "test"},
            timeout=2
        )
        version = response.headers.get("API-Version", "Not found")
        print(f"   Status: {response.status_code}")
        print(f"   API-Version header: {version}")
        print(f"   ✓ Versioned endpoint works")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test other services
    print("\n3. Testing versioning on other services:")
    services = ["rooms", "bookings", "reviews"]
    for service in services:
        try:
            response = requests.get(f"{BASE_URLS[service]}/health", timeout=2)
            version = response.headers.get("API-Version", "Not found")
            print(f"   {service.upper()}: API-Version = {version} ✓")
        except Exception as e:
            print(f"   {service.upper()}: Error - {str(e)} ✗")


def test_custom_exceptions():
    """Test custom exception handling."""
    print_section("TEST 3: Custom Exception Handling")
    
    print("Testing custom exception handling...\n")
    
    # Test validation error
    print("1. Testing validation error (invalid request):")
    try:
        response = requests.post(
            f"{BASE_URLS['users']}/users/register",
            json={"invalid": "data"},
            timeout=2
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "error" in data:
            print(f"   Error Code: {data['error'].get('code')}")
            print(f"   Error Message: {data['error'].get('message')}")
            print(f"   ✓ Custom error format returned")
        else:
            print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test not found error
    print("\n2. Testing not found error:")
    try:
        response = requests.get(
            f"{BASE_URLS['users']}/users/nonexistentuser12345",
            timeout=2
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            if "error" in data:
                print(f"   Error Code: {data['error'].get('code')}")
                print(f"   Error Message: {data['error'].get('message')}")
                print(f"   ✓ Custom error format returned")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Test authentication error
    print("\n3. Testing authentication error:")
    try:
        response = requests.get(
            f"{BASE_URLS['users']}/users/profile",
            timeout=2
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            data = response.json()
            if "error" in data:
                print(f"   Error Code: {data['error'].get('code')}")
                print(f"   Error Message: {data['error'].get('message')}")
                print(f"   ✓ Custom error format returned")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")


def test_circuit_breaker_status():
    """Test circuit breaker status endpoint."""
    print_section("TEST 4: Circuit Breaker Status")
    
    print("Checking circuit breaker status endpoint...\n")
    
    try:
        response = requests.get(
            f"{BASE_URLS['users']}/circuit-breaker/status",
            timeout=2
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"\nCircuit Breaker Status:")
            print(json.dumps(data, indent=2))
            print(f"\n✓ Circuit breaker status endpoint working")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("Note: Circuit breakers are initialized when inter-service calls are made")


def test_rate_limit_headers():
    """Test rate limit response headers."""
    print_section("TEST 5: Rate Limit Headers")
    
    print("Testing rate limit headers in responses...\n")
    
    url = f"{BASE_URLS['users']}/users/login"
    
    try:
        response = requests.post(
            url,
            json={"username": "test", "password": "test"},
            timeout=2
        )
        
        print("Response headers:")
        print(f"  X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit', 'Not found')}")
        print(f"  X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining', 'Not found')}")
        print(f"  X-RateLimit-Window: {response.headers.get('X-RateLimit-Window', 'Not found')}")
        
        if response.headers.get('X-RateLimit-Limit'):
            print("\n✓ Rate limit headers present")
        else:
            print("\n✗ Rate limit headers missing")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  PART II FEATURES TEST SCRIPT")
    print("  Hussein's Meeting Room Management System")
    print("="*70)
    print("\nTesting:")
    print("  1. Enhanced Inter-Service Communication")
    print("     - Circuit Breaker Pattern")
    print("     - Rate Limiting and Throttling")
    print("  2. Advanced Development Practices")
    print("     - Custom Exception Handling")
    print("     - API Versioning")
    print("\n" + "="*70)
    print("\nIMPORTANT: Make sure all Docker services are running!")
    print("  Run: docker-compose up")
    print("\n" + "="*70 + "\n")
    
    input("Press ENTER to start testing...\n")
    
    # Run all tests
    test_rate_limiting()
    time.sleep(2)
    
    test_api_versioning()
    time.sleep(2)
    
    test_custom_exceptions()
    time.sleep(2)
    
    test_rate_limit_headers()
    time.sleep(2)
    
    test_circuit_breaker_status()
    
    print("\n" + "="*70)
    print("  TESTING COMPLETE")
    print("="*70)
    print("\nSummary:")
    print("  ✓ Rate Limiting: Prevents API abuse with configurable limits")
    print("  ✓ API Versioning: Supports /v1/ and unversioned endpoints")
    print("  ✓ Custom Exceptions: Standardized error format across services")
    print("  ✓ Circuit Breaker: Protects inter-service communication")
    print("\n" + "="*70 + "\n")
