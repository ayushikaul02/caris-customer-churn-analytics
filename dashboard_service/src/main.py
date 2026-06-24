import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime

# Import services
from customer_ingestion.src.ingestion_service import DataIngestionService
from customer_transformation.src.transformation_service import DataTransformationService
from customer_analytics.src.analytics_service import CustomerAnalyticsService
from retention_engine.src.retention_service import RetentionEngine
from dashboard_service.src.dashboard_service import DashboardService
from reporting_service.src.report_service import ReportService

# Initialize FastAPI app
app = FastAPI(
    title="CARIS API",
    description="Customer Churn Analytics & Retention Intelligence System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ingestion_service = DataIngestionService()
transformation_service = DataTransformationService()
analytics_service = CustomerAnalyticsService()
retention_engine = RetentionEngine()
dashboard_service = DashboardService()
report_service = ReportService()

# Models
class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    join_date: str
    customer_segment: Optional[str] = "basic"
    monthly_charge: Optional[float] = 0.0

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CARIS API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Customer endpoints
@app.get("/api/customers")
async def get_customers():
    """Get all customers"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: int):
    """Get customer by ID"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        customer = df[df['customer_id'] == customer_id]
        if customer.empty:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/api/analytics/churn")
async def analyze_churn():
    """Get churn analysis"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        churn_analysis = analytics_service.analyze_churn(df)
        return churn_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue")
async def analyze_revenue():
    """Get revenue analysis"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        revenue_analysis = analytics_service.analyze_revenue(df)
        return revenue_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/customer-segments")
async def get_customer_segments():
    """Get customer segmentation"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        segmented_df = analytics_service.segment_customers(df)
        return {
            "segments": segmented_df['segment_label'].value_counts().to_dict(),
            "details": segmented_df[['customer_id', 'customer_segment_cluster', 'segment_label']].to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard endpoints
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        metrics = dashboard_service.get_dashboard_metrics(df)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/revenue")
async def get_revenue_dashboard():
    """Get revenue dashboard data"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        dashboard_data = dashboard_service.create_revenue_dashboard(df)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/customer")
async def get_customer_dashboard():
    """Get customer dashboard data"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        dashboard_data = dashboard_service.create_customer_dashboard(df)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/churn")
async def get_churn_dashboard():
    """Get churn dashboard data"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        dashboard_data = dashboard_service.create_churn_dashboard(df)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retention endpoints
@app.post("/api/retention/recommendations")
async def get_retention_recommendations():
    """Get retention recommendations"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        recommended_df = retention_engine.generate_recommendations(df)
        return recommended_df[['customer_id', 'risk_level', 'recommendations']].to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/retention/campaigns")
async def get_promotional_campaigns():
    """Get promotional campaigns"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        campaigns = retention_engine.create_promotional_campaigns(df)
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Report endpoints
@app.get("/api/reports/monthly")
async def get_monthly_report():
    """Generate monthly report"""
    try:
        df = pd.read_csv('./data/raw/customers.csv')
        report = report_service.generate_monthly_report(df)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)