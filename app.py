import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta
import logging
import jwt
import os

# Import services
from customer_ingestion.src.ingestion_service import DataIngestionService
from customer_transformation.src.transformation_service import DataTransformationService
from customer_analytics.src.analytics_service import CustomerAnalyticsService
from retention_engine.src.retention_service import RetentionEngine
from dashboard_service.src.dashboard_service import DashboardService
from reporting_service.src.report_service import ReportService

# ==================== AUTHENTICATION ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "user": {"username": "user", "password": "user123", "role": "user"}
}

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(username: str = Depends(verify_token)):
    if username not in fake_users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return fake_users_db[username]

# ==================== FASTAPI APP ====================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CARIS API",
    description="Customer Churn Analytics & Retention Intelligence System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

# ==================== MODELS ====================

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

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    customer_segment: Optional[str] = None
    status: Optional[str] = None
    monthly_charge: Optional[float] = None

# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "path": request.url.path
        }
    )

# ==================== ROOT - LANDING PAGE ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the landing page"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>📊 CARIS API</h1>
                <p>Visit <a href="/docs">/docs</a> for API documentation</p>
                <p>Or <a href="/dashboard">/dashboard</a> for the dashboard</p>
            </body>
        </html>
        """

# ==================== DASHBOARD ====================

@app.get("/dashboard")
async def dashboard():
    """Redirect to Streamlit dashboard"""
    return FileResponse("dashboard.py")

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/login", tags=["Authentication"])
async def login(user: User):
    if user.username not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if fake_users_db[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": fake_users_db[user.username]["role"]
    }

@app.get("/api/auth/me", tags=["Authentication"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

# ==================== HEALTH ====================

@app.get("/health", tags=["Root"])
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"api": "running", "data": "loaded" if os.path.exists('./data/raw/customers_cleaned.csv') else "missing"}
    }
    
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        health_status["data_stats"] = {
            "total_customers": len(df),
            "columns": list(df.columns)[:10]
        }
    except:
        health_status["data_stats"] = {"error": "Data not available"}
    
    return health_status

# ==================== CUSTOMER ENDPOINTS ====================

@app.get("/api/customers", tags=["Customers"])
async def get_customers(
    limit: int = Query(100, description="Number of customers to return"),
    current_user: dict = Depends(get_current_user)
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return df.head(limit).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}", tags=["Customers"])
async def get_customer(customer_id: int, current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        customer = df[df['customer_id'] == customer_id]
        if customer.empty:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/churn", tags=["Analytics"])
async def analyze_churn(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return analytics_service.analyze_churn(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue", tags=["Analytics"])
async def analyze_revenue(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return analytics_service.analyze_revenue(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/customer-segments", tags=["Analytics"])
async def get_customer_segments(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        if 'tenure_days' not in df.columns:
            if 'join_date' in df.columns:
                df['join_date'] = pd.to_datetime(df['join_date'])
                df['tenure_days'] = (datetime.now() - df['join_date']).dt.days
            else:
                df['tenure_days'] = 365
        
        segmented_df = analytics_service.segment_customers(df)
        return {
            "status": "success",
            "segments": segmented_df['segment_label'].value_counts().to_dict(),
            "details": segmented_df[['customer_id', 'customer_segment_cluster', 'segment_label']].head(100).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/api/dashboard/metrics", tags=["Dashboard"])
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.get_dashboard_metrics(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/revenue", tags=["Dashboard"])
async def get_revenue_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.create_revenue_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/customer", tags=["Dashboard"])
async def get_customer_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.create_customer_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/churn", tags=["Dashboard"])
async def get_churn_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.create_churn_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RETENTION ENDPOINTS ====================

@app.post("/api/retention/recommendations", tags=["Retention"])
async def get_retention_recommendations(
    limit: int = Query(50, description="Number of recommendations to return"),
    current_user: dict = Depends(get_current_user)
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        if 'risk_level' not in df.columns:
            df = analytics_service.calculate_risk_score(df)
        
        recommended_df = retention_engine.generate_recommendations(df)
        
        result = []
        for _, row in recommended_df.iterrows():
            rec_data = row['recommendations']
            if isinstance(rec_data, dict):
                result.append({
                    'customer_id': int(row['customer_id']),
                    'customer_name': rec_data.get('customer_name', row.get('name', 'Unknown')),
                    'risk_level': row.get('risk_level', 'Unknown'),
                    'priority': rec_data.get('priority', 'low'),
                    'recommendations': rec_data.get('recommendations', []),
                    'urgency': rec_data.get('urgency', 'soon')
                })
        return result[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/retention/campaigns", tags=["Retention"])
async def get_promotional_campaigns(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return retention_engine.create_promotional_campaigns(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REPORT ENDPOINTS ====================

@app.get("/api/reports/monthly", tags=["Reports"])
async def get_monthly_report(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return report_service.generate_monthly_report(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/excel", tags=["Reports"])
async def generate_excel_report(current_user: dict = Depends(get_current_user)):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        filepath = report_service.generate_excel_report(df)
        return {
            "message": "Excel report generated successfully",
            "filepath": filepath,
            "download_url": f"/api/reports/download/{os.path.basename(filepath)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/available", tags=["Reports"])
async def get_available_reports(current_user: dict = Depends(get_current_user)):
    try:
        return {"reports": report_service.get_available_reports()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)