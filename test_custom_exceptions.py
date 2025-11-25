"""
Test Custom Exception Handling
==============================

Tests custom exception handling without rate limiting interference.
Wait for rate limits to reset before running this.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_custom_exceptions():
    """Test custom exception handling."""
    print_section("Custom Exception Handling Tests")
    
    print("Waiting 10 seconds for rate limits to reset...")
    time.sleep(10)
    print("Starting tests...\n")
    
    # Test validation error
    print("1. Testing validation error (missing required fields):")
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            json={"name": "Test"},  # Missing required fields
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response:")
        print(json.dumps(data, indent=4))
        
        if "error" in data:
            print(f"\n   ✓ Custom error format:")
            print(f"     - Code: {data['error'].get('code')}")
            print(f"     - Message: {data['error'].get('message')}")
            print(f"     - Path: {data['error'].get('path')}")
        else:
            print(f"   ⚠ Standard FastAPI validation format")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    print("\n" + "-"*70)
    
    # Test not found with valid auth
    print("2. Testing not found error (authenticated request):")
    try:
        # First, create a user and get token
        register_response = requests.post(
            f"{BASE_URL}/users/register",
            json={
                "name": "Test User",
                "username": "testuser123",
                "email": "testuser123@example.com",
                "password": "test123",
                "role": "regular_user"
            },
            timeout=5
        )
        
        if register_response.status_code == 201:
            # Login to get token
            login_response = requests.post(
                f"{BASE_URL}/users/login",
                json={"username": "testuser123", "password": "test123"},
                timeout=5
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                
                # Try to get non-existent user
                response = requests.get(
                    f"{BASE_URL}/users/nonexistentuser99999",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                print(f"   Status: {response.status_code}")
                data = response.json()
                print(f"   Response:")
                print(json.dumps(data, indent=4))
                
                if "error" in data:
                    print(f"\n   ✓ Custom error format:")
                    print(f"     - Code: {data['error'].get('code')}")
                    print(f"     - Message: {data['error'].get('message')}")
                else:
                    print(f"   ⚠ Standard HTTPException format")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    print("\n" + "-"*70)
    
    # Test authentication error
    print("3. Testing authentication error (no token):")
    try:
        response = requests.get(
            f"{BASE_URL}/users/profile",
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response:")
        print(json.dumps(data, indent=4))
        
        if "error" in data:
            print(f"\n   ✓ Custom error format:")
            print(f"     - Code: {data['error'].get('code')}")
            print(f"     - Message: {data['error'].get('message')}")
        else:
            print(f"   ⚠ Standard FastAPI error format")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  CUSTOM EXCEPTION HANDLING TEST")
    print("="*70)
    print("\nThis test waits for rate limits to reset and then tests")
    print("custom exception handling with proper requests.")
    print("\n" + "="*70 + "\n")
    
    input("Press ENTER to start...\n")
    
    test_custom_exceptions()
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70 + "\n")

