#!/usr/bin/env python3
"""
Test script for Flask application endpoints.
"""

import sys
import os
import requests
import time
import subprocess
import signal

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def start_test_server():
    """Start Flask server for testing."""
    env = os.environ.copy()
    env['FLASK_PORT'] = '5002'  # Use different port for testing
    
    # Start the server in background
    process = subprocess.Popen(
        ['python', 'app.py'],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start up
    time.sleep(3)
    
    return process


def stop_test_server(process):
    """Stop the test server."""
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def test_flask_endpoints():
    """Test all Flask application endpoints."""
    
    print("Testing Flask application endpoints...")
    
    # Start test server
    print("\n1. Starting test server...")
    server_process = start_test_server()
    
    try:
        base_url = "http://localhost:5002"
        
        # Test 1: Index endpoint
        print("\n2. Testing index endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Endpoints: {data.get('endpoints')}")
        
        # Test 2: Health check endpoint
        print("\n3. Testing health check endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health status: {data.get('status')}")
            print(f"   Database status: {data.get('database', {}).get('status')}")
            print(f"   Users count: {data.get('database', {}).get('users_count')}")
            print(f"   Config errors: {data.get('configuration', {}).get('config_errors')}")
        
        # Test 3: Webhook endpoint with valid user
        print("\n4. Testing webhook endpoint (valid user)...")
        webhook_data = {
            'recipient': 'user1@yourdomain.com',
            'sender': 'recruiter@techcorp.com',
            'subject': 'Software Engineer Position',
            'body-plain': 'Hello, we have an exciting opportunity...',
            'timestamp': '1234567890',
            'Message-Id': 'test@mailgun.com'
        }
        response = requests.post(f"{base_url}/webhook/email", data=webhook_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response status: {data.get('status')}")
            print(f"   User: {data.get('user')}")
            print(f"   Message: {data.get('message')}")
        
        # Test 4: Webhook endpoint with invalid user
        print("\n5. Testing webhook endpoint (invalid user)...")
        webhook_data['recipient'] = 'unknown@example.com'
        response = requests.post(f"{base_url}/webhook/email", data=webhook_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   Response status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
        
        # Test 5: 404 endpoint
        print("\n6. Testing 404 handling...")
        response = requests.get(f"{base_url}/nonexistent")
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            print(f"   Response status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
        
        print("\n✅ All Flask endpoint tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to test server")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up
        print("\n7. Stopping test server...")
        stop_test_server(server_process)


if __name__ == "__main__":
    test_flask_endpoints()