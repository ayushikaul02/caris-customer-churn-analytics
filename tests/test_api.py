import pytest
import requests
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    # Skip if server not running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    except requests.exceptions.ConnectionError:
        pytest.skip("Server not running")

def test_root():
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("Server not running")

def test_get_customers():
    try:
        response = requests.get(f"{BASE_URL}/api/customers", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    except requests.exceptions.ConnectionError:
        pytest.skip("Server not running")