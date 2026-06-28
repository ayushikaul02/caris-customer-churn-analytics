import sys
import os
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import logging
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Import database
from database import get_db, User, Customer, Prediction, ActivityLog, init_db
from database import SessionLocal

# Import services
from customer_ingestion.src.ingestion_service import DataIngestionService
from customer_transformation.src.transformation_service import DataTransformationService
from customer_analytics.src.analytics_service import CustomerAnalyticsService
from retention_engine.src.retention_service import RetentionEngine
from dashboard_service.src.dashboard_service import DashboardService
from reporting_service.src.report_service import ReportService

# ==================== AUTHENTICATION SETUP ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# ==================== MODELS ====================

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"

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

# ==================== SECURITY ====================

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

def get_current_user(username: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(allowed_roles: List[str]):
    def decorator(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
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
    """Initialize database and create admin user"""
    init_db()
    
    # Create admin user if not exists
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@caris.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        logger.info("✅ Admin user created")
    db.close()

# ==================== ROOT - LANDING PAGE ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the professional landing page"""
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
    """Redirect dashboard to React app"""
    return RedirectResponse(url="https://caris-frontend.vercel.app")

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"api": "running"}
    }
    
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        health_status["services"]["database"] = "connected"
        db.close()
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
    
    return health_status

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login to get access token"""
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": db_user.username})
    
    # Log activity
    activity = ActivityLog(
        user_id=db_user.id,
        action="login",
        details=f"User {db_user.username} logged in"
    )
    db.add(activity)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role
    }

@app.post("/api/auth/register", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "username": new_user.username}

@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@app.post("/api/auth/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user"""
    activity = ActivityLog(
        user_id=current_user.id,
        action="logout",
        details=f"User {current_user.username} logged out"
    )
    db.add(activity)
    db.commit()
    return {"message": "Logged out successfully"}

# ==================== CUSTOMER ENDPOINTS ====================

@app.get("/api/customers")
async def get_customers(
    limit: int = Query(100, description="Number of customers to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(require_role(["admin", "analyst", "manager", "viewer"])),
    db: Session = Depends(get_db)
):
    """Get all customers with pagination"""
    try:
        customers = db.query(Customer).offset(offset).limit(limit).all()
        total = db.query(Customer).count()
        return {
            "data": customers,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user: User = Depends(require_role(["admin", "analyst", "manager", "viewer"])),
    db: Session = Depends(get_db)
):
    """Get customer by ID"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers")
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(require_role(["admin", "analyst"])),
    db: Session = Depends(get_db)
):
    """Create a new customer (Admin & Analyst only)"""
    try:
        # Generate new ID
        max_id = db.query(Customer).order_by(desc(Customer.id)).first()
        new_id = max_id.id + 1 if max_id else 1
        
        new_customer = Customer(
            customer_id=new_id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            gender=customer.gender,
            age=customer.age,
            city=customer.city,
            state=customer.state,
            join_date=datetime.fromisoformat(customer.join_date) if customer.join_date else datetime.now(),
            customer_segment=customer.customer_segment,
            monthly_charge=customer.monthly_charge
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        
        # Log activity
        activity = ActivityLog(
            user_id=current_user.id,
            action="create_customer",
            details=f"Created customer {new_customer.name}"
        )
        db.add(activity)
        db.commit()
        
        return {"message": "Customer created successfully", "customer_id": new_customer.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/churn")
async def analyze_churn(
    current_user: User = Depends(require_role(["admin", "analyst", "manager"])),
    db: Session = Depends(get_db)
):
    """Get churn analysis"""
    try:
        customers = db.query(Customer).all()
        # Convert to DataFrame for analysis
        df = pd.DataFrame([{
            'customer_id': c.customer_id,
            'name': c.name,
            'email': c.email,
            'status': c.status,
            'customer_segment': c.customer_segment,
            'total_spent': c.total_spent,
            'monthly_charge': c.monthly_charge,
            'age': c.age,
            'join_date': c.join_date
        } for c in customers])
        
        if df.empty:
            return {"message": "No customer data available"}
        
        return analytics_service.analyze_churn(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue")
async def analyze_revenue(
    current_user: User = Depends(require_role(["admin", "analyst", "manager"])),
    db: Session = Depends(get_db)
):
    """Get revenue analysis"""
    try:
        customers = db.query(Customer).all()
        df = pd.DataFrame([{
            'customer_id': c.customer_id,
            'total_spent': c.total_spent,
            'customer_segment': c.customer_segment,
            'monthly_charge': c.monthly_charge,
            'name': c.name
        } for c in customers])
        
        if df.empty:
            return {"message": "No customer data available"}
        
        return analytics_service.analyze_revenue(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(
    current_user: User = Depends(require_role(["admin", "analyst", "manager", "viewer"])),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics"""
    try:
        customers = db.query(Customer).all()
        df = pd.DataFrame([{
            'customer_id': c.customer_id,
            'status': c.status,
            'customer_segment': c.customer_segment,
            'total_spent': c.total_spent,
            'monthly_charge': c.monthly_charge,
            'age': c.age,
            'join_date': c.join_date,
            'churn_risk_score': c.churn_risk_score,
            'risk_level': c.risk_level,
            'name': c.name
        } for c in customers])
        
        if df.empty:
            # Return empty metrics
            return {
                "customer_kpis": {"total_customers": 0, "active_customers": 0, "churned_customers": 0, "retention_rate": 0},
                "revenue_kpis": {"total_revenue": 0, "avg_revenue_per_customer": 0},
                "churn_kpis": {"churn_rate": 0, "high_risk_customers": 0}
            }
        
        return dashboard_service.get_dashboard_metrics(df)
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RETENTION ENDPOINTS ====================

@app.post("/api/retention/recommendations")
async def get_retention_recommendations(
    limit: int = Query(50, description="Number of recommendations to return"),
    current_user: User = Depends(require_role(["admin", "analyst", "manager"])),
    db: Session = Depends(get_db)
):
    """Get retention recommendations"""
    try:
        customers = db.query(Customer).all()
        df = pd.DataFrame([{
            'customer_id': c.customer_id,
            'name': c.name,
            'email': c.email,
            'status': c.status,
            'customer_segment': c.customer_segment,
            'total_spent': c.total_spent,
            'monthly_charge': c.monthly_charge,
            'age': c.age,
            'join_date': c.join_date,
            'churn_risk_score': c.churn_risk_score,
            'risk_level': c.risk_level
        } for c in customers])
        
        if df.empty:
            return {"message": "No customer data available"}
        
        # Calculate risk scores if not present
        if 'risk_level' not in df.columns or df['risk_level'].isnull().all():
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

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)