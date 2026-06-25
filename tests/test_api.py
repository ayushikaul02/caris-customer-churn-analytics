import pytest
import requests

BASE_URL = "http://localhost:8000"


def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"


def test_get_customers():
    response = requests.get(f"{BASE_URL}/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_dashboard_metrics():
    response = requests.get(f"{BASE_URL}/api/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "customer_kpis" in data


def test_churn_analysis():
    response = requests.get(f"{BASE_URL}/api/analytics/churn")
    assert response.status_code == 200
    data = response.json()
    assert "overall_churn_rate" in data


def test_revenue_analysis():
    response = requests.get(f"{BASE_URL}/api/analytics/revenue")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data


def test_recommendations():
    response = requests.post(f"{BASE_URL}/api/retention/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_customer_segments():
    response = requests.post(f"{BASE_URL}/api/analytics/customer-segments")
    assert response.status_code == 200
    data = response.json()
    assert "segments" in data


def test_monthly_report():
    response = requests.get(f"{BASE_URL}/api/reports/monthly")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data


def test_excel_report():
    response = requests.get(f"{BASE_URL}/api/reports/excel")
    assert response.status_code == 200
    data = response.json()
    assert "filepath" in data
