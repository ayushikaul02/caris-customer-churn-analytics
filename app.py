import sys
import os
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import logging
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.orm import Session

# SHAP and ML imports
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load environment variables
load_dotenv()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import services
from customer_ingestion.src.ingestion_service import DataIngestionService
from customer_transformation.src.transformation_service import DataTransformationService
from customer_analytics.src.analytics_service import CustomerAnalyticsService
from retention_engine.src.retention_service import RetentionEngine
from dashboard_service.src.dashboard_service import DashboardService
from reporting_service.src.report_service import ReportService

# Import database
from database import get_db, engine, Base
from sqlalchemy.orm import Session

# Import data structures
from backend.data_structures import PriorityQueue, Queue, Graph, HashMap, Trie

# ==================== DATABASE MODELS ====================

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# ==================== DATA GENERATION ====================

def generate_sample_data():
    """Generate sample data if it doesn't exist"""
    data_path = './data/raw/customers_cleaned.csv'
    
    if os.path.exists(data_path):
        print(f"✅ Data already exists at {data_path}")
        return
    
    print(f"📊 Generating sample data...")
    os.makedirs('./data/raw', exist_ok=True)
    
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

# Mock users database (for CSV mode)
fake_users_db = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "analyst": {"username": "analyst", "password": "analyst123", "role": "analyst"},
    "manager": {"username": "manager", "password": "manager123", "role": "manager"},
    "viewer": {"username": "viewer", "password": "viewer123", "role": "viewer"}
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

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

def require_role(allowed_roles: List[str]):
    def decorator(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return decorator

# ==================== SHAP HELPER ====================

def get_recommendation(churn_prob):
    """Get recommendation based on churn probability"""
    if churn_prob > 0.7:
        return "🚨 Immediate action required: Offer personalized discount and schedule customer success call"
    elif churn_prob > 0.4:
        return "📞 Reach out with engagement email and loyalty offer"
    else:
        return "✅ Customer is likely to stay. Send periodic newsletter."

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

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Create tables and generate sample data"""
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization warning: {e}")
    
    generate_sample_data()

# ==================== ROOT ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a0a1a; color: white;">
                <h1>📊 CARIS</h1>
                <p>Visit <a href="/docs" style="color: #667eea;">/docs</a> for API documentation</p>
                <p>Frontend: <a href="https://caris-frontend.vercel.app" style="color: #667eea;">caris-frontend.vercel.app</a></p>
            </body>
        </html>
        """

# ==================== DASHBOARD REDIRECT ====================

@app.get("/dashboard")
async def dashboard_redirect():
    return RedirectResponse(url="https://caris-frontend.vercel.app")

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"api": "running"}
    }
    
    # Check database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
        db.close()
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
    
    # Check data
    data_path = './data/raw/customers_cleaned.csv'
    if os.path.exists(data_path):
        try:
            df = pd.read_csv(data_path)
            health_status["data_stats"] = {"total_customers": len(df)}
            health_status["services"]["data"] = "loaded"
        except Exception as e:
            health_status["services"]["data"] = f"error: {str(e)}"
    else:
        health_status["services"]["data"] = "missing"
    
    return health_status

# ==================== AUTHENTICATION ====================

@app.post("/api/auth/login")
async def login(user: UserLogin):
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

# ==================== CUSTOMERS ====================

@app.get("/api/customers")
async def get_customers(
    limit: int = Query(100),
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return df.head(limit).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        customer = df[df['customer_id'] == customer_id]
        if customer.empty:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ====================

@app.get("/api/analytics/churn")
async def analyze_churn(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return analytics_service.analyze_churn(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue")
async def analyze_revenue(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return analytics_service.analyze_revenue(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/customer-segments")
async def get_customer_segments(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        segmented_df = analytics_service.segment_customers(df)
        return {
            "status": "success",
            "segments": segmented_df['segment_label'].value_counts().to_dict(),
            "details": segmented_df[['customer_id', 'customer_segment_cluster', 'segment_label']].head(100).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CLV ENDPOINT ====================

@app.get("/api/analytics/clv")
async def calculate_clv(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        clv_df = analytics_service.calculate_clv(df)
        return clv_df[['customer_id', 'clv', 'clv_category']].head(100).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REVENUE IMPACT ENDPOINT ====================

@app.get("/api/analytics/revenue-impact")
async def get_revenue_impact(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        impact = analytics_service.calculate_revenue_impact(df)
        return impact
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WHAT-IF ANALYSIS ENDPOINT ====================

@app.post("/api/analytics/what-if")
async def what_if_analysis(
    discount_percent: float = Query(..., description="Discount percentage (0-50)", ge=0, le=50),
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    """
    What-if analysis: Simulate churn reduction based on discount offer
    """
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        
        # Calculate current churn rate
        total = len(df)
        churned = len(df[df['status'] == 'churned'])
        current_churn_rate = churned / total if total > 0 else 0
        
        # Simulate discount impact (simplified model)
        discount_effect = min(discount_percent / 100, 0.5)  # Max 50% reduction
        new_churn_rate = current_churn_rate * (1 - discount_effect * 0.5)
        
        # Calculate impact
        customers_saved = int((current_churn_rate - new_churn_rate) * total)
        avg_revenue = df['total_spent'].mean()
        revenue_saved = customers_saved * avg_revenue
        
        return {
            "discount_percent": discount_percent,
            "current_churn_rate": round(current_churn_rate * 100, 2),
            "predicted_churn_rate": round(new_churn_rate * 100, 2),
            "churn_reduction": round((current_churn_rate - new_churn_rate) * 100, 2),
            "customers_saved": customers_saved,
            "revenue_saved": round(revenue_saved, 2),
            "recommendation": "Highly effective" if discount_percent >= 20 else "Moderately effective" if discount_percent >= 10 else "Low impact",
            "roi": round((revenue_saved / (customers_saved * 50)) if customers_saved > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SHAP EXPLANATION ENDPOINT ====================

@app.post("/api/explain/churn")
async def explain_churn(
    customer_id: int = Query(..., description="Customer ID to explain"),
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    """
    Get SHAP explanation for a specific customer
    Returns: Why this customer may churn
    """
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        
        # Get customer
        customer = df[df['customer_id'] == customer_id]
        if customer.empty:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Prepare features
        features = ['total_spent', 'monthly_charge', 'age', 'tenure_days']
        available_features = [f for f in features if f in df.columns]
        
        if not available_features:
            return {
                "customer_id": customer_id,
                "churn_probability": 0.5,
                "risk_level": "Unknown",
                "top_factors": [],
                "explanation": "Not enough data to explain"
            }
        
        # Prepare data
        df['churned'] = (df['status'] == 'churned').astype(int)
        X = df[available_features].fillna(0)
        y = df['churned']
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        # SHAP Explanation
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        
        # Get customer's features
        customer_features = customer[available_features].iloc[0].values
        
        # Get SHAP values for this customer
        shap_values_customer = explainer.shap_values(customer_features.reshape(1, -1))
        
        if isinstance(shap_values_customer, list):
            shap_values_customer = shap_values_customer[1]
        
        # Create explanation
        top_indices = np.argsort(np.abs(shap_values_customer[0]))[-3:][::-1]
        top_features = []
        
        for idx in top_indices:
            feature_name = available_features[idx]
            value = customer_features[idx]
            shap_value = shap_values_customer[0][idx]
            
            if shap_value > 0:
                impact = f"{feature_name} is {value:.2f} (increases churn risk)"
            else:
                impact = f"{feature_name} is {value:.2f} (decreases churn risk)"
            
            top_features.append({
                "feature": feature_name,
                "value": round(float(value), 2),
                "shap_value": round(float(shap_value), 4),
                "impact": impact
            })
        
        # Calculate churn probability
        churn_prob = model.predict_proba(customer_features.reshape(1, -1))[0][1]
        
        # Generate business-friendly explanation
        if churn_prob > 0.7:
            risk_level = "HIGH"
            explanation = "This customer has a high risk of churning. "
            if top_features:
                explanation += f"Top factors: {top_features[0]['feature']} and {top_features[1]['feature'] if len(top_features) > 1 else 'others'}."
        elif churn_prob > 0.4:
            risk_level = "MEDIUM"
            explanation = "This customer has a moderate risk of churning."
        else:
            risk_level = "LOW"
            explanation = "This customer has a low risk of churning."
        
        return {
            "customer_id": customer_id,
            "customer_name": customer.iloc[0]['name'],
            "churn_probability": round(float(churn_prob), 4),
            "risk_level": risk_level,
            "top_factors": top_features,
            "explanation": explanation,
            "recommendation": get_recommendation(churn_prob)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DASHBOARD ====================

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.get_dashboard_metrics(df)
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/revenue")
async def get_revenue_dashboard(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.create_revenue_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/customer")
async def get_customer_dashboard(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.create_customer_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/churn")
async def get_churn_dashboard(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager", "viewer"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return dashboard_service.create_churn_dashboard(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RETENTION ====================

@app.post("/api/retention/recommendations")
async def get_retention_recommendations(
    limit: int = Query(50),
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
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

# ==================== REPORTS ====================

@app.get("/api/reports/monthly")
async def get_monthly_report(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
    try:
        df = pd.read_csv('./data/raw/customers_cleaned.csv')
        return report_service.generate_monthly_report(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/excel")
async def generate_excel_report(
    current_user: dict = Depends(require_role(["admin", "analyst", "manager"]))
):
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