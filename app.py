import sys
import os
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import logging
import jwt

# Import services
from customer_ingestion.src.ingestion_service import DataIngestionService
from customer_transformation.src.transformation_service import DataTransformationService
from customer_analytics.src.analytics_service import CustomerAnalyticsService
from retention_engine.src.retention_service import RetentionEngine
from dashboard_service.src.dashboard_service import DashboardService
from reporting_service.src.report_service import ReportService

# ==================== DATA GENERATION ====================

def generate_sample_data():
    """Generate sample data if it doesn't exist"""
    import os
    import pandas as pd
    from faker import Faker
    import random
    
    # Use absolute path based on current file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    
    if os.path.exists(data_path):
        print(f"✅ Data already exists at {data_path}")
        return
    
    print(f"📊 Generating sample data at {data_path}...")
    
    fake = Faker()
    data = []
    segments = ['basic', 'bronze', 'silver', 'gold', 'premium']
    
    for i in range(1000):
        join_date = fake.date_between(start_date='-3y', end_date='today')
        status = random.choices(['active', 'active', 'active', 'churned', 'inactive'], weights=[0.5, 0.2, 0.1, 0.1, 0.1])[0]
        
        data.append({
            'customer_id': i + 1,
            'name': fake.name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'gender': random.choice(['M', 'F']),
            'age': random.randint(18, 75),
            'city': fake.city(),
            'state': fake.state(),
            'country': 'USA',
            'join_date': join_date.isoformat(),
            'customer_segment': random.choice(segments),
            'status': status,
            'monthly_charge': round(random.uniform(20, 200), 2),
            'total_spent': round(random.uniform(100, 5000), 2)
        })
    
    df = pd.DataFrame(data)
    df.to_csv(data_path, index=False)
    print(f"✅ Generated {len(df)} customers at {data_path}")

# ==================== AUTHENTICATION ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "analyst": {"username": "analyst", "password": "analyst123", "role": "analyst"},
    "manager": {"username": "manager", "password": "manager123", "role": "manager"},
    "viewer": {"username": "viewer", "password": "viewer123", "role": "viewer"}
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

# ==================== RBAC ====================

def require_role(allowed_roles: list):
    def decorator(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Access denied. Required roles: {allowed_roles}")
        return current_user
    return decorator

# ==================== FASTAPI APP ====================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CARIS API",
    description="Customer Churn Analytics & Retention Intelligence System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://caris-frontend.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INITIALIZE SERVICES ====================

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

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Generate sample data on startup"""
    generate_sample_data()

# ==================== ROOT - REDIRECT TO REACT APP ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to React frontend"""
    return """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=https://caris-frontend.vercel.app" />
            <title>CARIS - Redirecting...</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 100px;
                    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
                    color: white;
                }
                .loader {
                    display: inline-block;
                    width: 50px;
                    height: 50px;
                    border: 5px solid rgba(255,255,255,0.1);
                    border-top: 5px solid #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                a {
                    color: #667eea;
                }
            </style>
        </head>
        <body>
            <div class="loader"></div>
            <h1>📊 CARIS</h1>
            <p>Redirecting to <a href="https://caris-frontend.vercel.app">CARIS Dashboard</a>...</p>
            <p style="font-size: 0.8rem; opacity: 0.6; margin-top: 20px;">
                API available at <a href="/docs">/docs</a> | 
                <a href="/health">/health</a>
            </p>
        </body>
    </html>
    """

# ==================== DASHBOARD REDIRECT ====================

@app.get("/dashboard")
async def dashboard_redirect():
    """Redirect dashboard to React app"""
    return RedirectResponse(url="https://caris-frontend.vercel.app")

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Detailed health check"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"api": "running"}
    }
    
    # If data doesn't exist, generate it
    if not os.path.exists(data_path):
        generate_sample_data()
    
    if os.path.exists(data_path):
        try:
            df = pd.read_csv(data_path)
            health_status["data_stats"] = {
                "total_customers": len(df),
                "path": data_path
            }
            health_status["services"]["data"] = "loaded"
        except Exception as e:
            health_status["services"]["data"] = f"error: {str(e)}"
    else:
        health_status["services"]["data"] = "missing"
        health_status["data_stats"] = {"path": data_path}
    
    return health_status

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/login")
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

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

# ==================== CUSTOMER ENDPOINTS ====================

@app.get("/api/customers")
async def get_customers(
    limit: int = Query(100),
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return df.head(limit).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        customer = df[df['customer_id'] == customer_id]
        if customer.empty:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers")
async def create_customer(
    customer: CustomerCreate,
    current_user: dict = Depends(require_role(["admin", "analyst"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        new_id = df['customer_id'].max() + 1
        customer_dict = customer.dict()
        customer_dict['customer_id'] = new_id
        df = df.append(customer_dict, ignore_index=True)
        df.to_csv(data_path, index=False)
        return {"message": "Customer created successfully", "customer_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/churn")
async def analyze_churn(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return analytics_service.analyze_churn(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue")
async def analyze_revenue(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return analytics_service.analyze_revenue(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/customer-segments")
async def get_customer_segments(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        
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

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return dashboard_service.get_dashboard_metrics(df)
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/revenue")
async def get_revenue_dashboard(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return dashboard_service.create_revenue_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/customer")
async def get_customer_dashboard(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return dashboard_service.create_customer_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/churn")
async def get_churn_dashboard(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return dashboard_service.create_churn_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RETENTION ENDPOINTS ====================

@app.post("/api/retention/recommendations")
async def get_retention_recommendations(
    limit: int = Query(50),
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        
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

@app.get("/api/retention/campaigns")
async def get_promotional_campaigns(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return retention_engine.create_promotional_campaigns(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REPORT ENDPOINTS ====================

@app.get("/api/reports/monthly")
async def get_monthly_report(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        return report_service.generate_monthly_report(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/excel")
async def generate_excel_report(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', 'raw', 'customers_cleaned.csv')
        
        if not os.path.exists(data_path):
            generate_sample_data()
        
        df = pd.read_csv(data_path)
        filepath = report_service.generate_excel_report(df)
        return {
            "message": "Excel report generated successfully",
            "filepath": filepath,
            "download_url": f"/api/reports/download/{os.path.basename(filepath)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/available")
async def get_available_reports(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        return {"reports": report_service.get_available_reports()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)