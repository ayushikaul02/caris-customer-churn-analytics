import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/caris")

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer")  # admin, analyst, manager, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user")
    activities = relationship("ActivityLog", back_populates="user")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    gender = Column(String(10))
    age = Column(Integer)
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    join_date = Column(DateTime)
    customer_segment = Column(String(20))
    status = Column(String(20), default="active")
    monthly_charge = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    churn_risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="Low")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="customer")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    churn_probability = Column(Float, nullable=False)
    risk_level = Column(String(20))
    model_version = Column(String(50))
    feature_importance = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="predictions")
    user = relationship("User", back_populates="predictions")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("customers.id"))
    referred_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String(20), default="pending")
    reward_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== CREATE TABLES ====================

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()