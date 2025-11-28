#!/usr/bin/env python3
"""
Development test script for the quiz solver
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

STUDENT_EMAIL = os.getenv("STUDENT_EMAIL")
STUDENT_SECRET = os.getenv("STUDENT_SECRET")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_invalid_json():
    """Test with invalid JSON"""
    print("Testing with invalid JSON...")
    response = requests.post(f"{BASE_URL}/quiz", data="invalid")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")

def test_missing_fields():
    """Test with missing fields"""
    print("Testing with missing fields...")
    response = requests.post(f"{BASE_URL}/quiz", json={"email": STUDENT_EMAIL})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_invalid_credentials():
    """Test with invalid credentials"""
    print("Testing with invalid credentials...")
    payload = {
        "email": "wrong@email.com",
        "secret": "wrong-secret",
        "url": DEMO_URL
    }
    response = requests.post(f"{BASE_URL}/quiz", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_valid_quiz():
    """Test with valid credentials"""
    print(f"Testing with valid credentials...")
    payload = {
        "email": STUDENT_EMAIL,
        "secret": STUDENT_SECRET,
        "url": DEMO_URL
    }
    response = requests.post(f"{BASE_URL}/quiz", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    if not STUDENT_EMAIL or not STUDENT_SECRET:
        print("ERROR: STUDENT_EMAIL and STUDENT_SECRET must be set in .env file")
        exit(1)
    
    print(f"Testing against {BASE_URL}\n")
    print(f"Email: {STUDENT_EMAIL}\n")
    
    test_health()
    test_invalid_json()
    test_missing_fields()
    test_invalid_credentials()
    test_valid_quiz()
    
    print("All tests completed!")
