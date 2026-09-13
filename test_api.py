"""
Test script for the Flask API with YOLO model
Run this after starting the Flask API locally
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_predict():
    """Test the predict endpoint with a sample image"""
    print("Testing predict endpoint with YOLO model...")
    
    # Using a sample plant image from Unsplash
    test_data = {
        "image_url": "https://images.unsplash.com/photo-1598512752271-33f913a5af13?w=500"
    }
    
    response = requests.post(
        f"{API_URL}/predict",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_batch():
    """Test the batch predict endpoint"""
    print("Testing batch predict endpoint with YOLO model...")
    
    test_data = {
        "image_urls": [
            "https://images.unsplash.com/photo-1598512752271-33f913a5af13?w=500",
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=500"
        ]
    }
    
    response = requests.post(
        f"{API_URL}/predict/batch",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("Flask API Test Suite - YOLO Model")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_predict()
        test_batch()
        print("All tests completed!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask API. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}")