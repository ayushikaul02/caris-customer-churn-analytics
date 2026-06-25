from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


class CustomerSegment(enum.Enum):
    PREMIUM = "premium"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    BASIC = "basic"


class CustomerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    SUSPENDED = "suspended"


class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    gender = Column(String(10))
    age = Column(Integer)
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    join_date = Column(Date, nullable=False)
    customer_segment = Column(Enum(CustomerSegment))
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    monthly_charge = Column(Float)
    total_spent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="customer")
    transactions = relationship("Transaction", back_populates="customer")
    support_tickets = relationship("SupportTicket", back_populates="customer")
    predictions = relationship("ChurnPrediction", back_populates="customer")


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    plan_name = Column(String(50), nullable=False)
    monthly_fee = Column(Float, nullable=False)
    status = Column(String(20), default="active")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="subscriptions")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50))
    transaction_type = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="transactions")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    issue_type = Column(String(50), nullable=False)
    priority = Column(String(20))
    status = Column(String(20), default="open")
    created_date = Column(DateTime, nullable=False)
    resolved_date = Column(DateTime)
    satisfaction_score = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="support_tickets")


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    churn_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel))
    recommendation = Column(Text)
    generated_date = Column(DateTime, nullable=False)
    model_version = Column(String(50))
    feature_importance = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="predictions")


class Referral(Base):
    __tablename__ = "referrals"

    referral_id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(Integer, ForeignKey("customers.customer_id"))
    referred_id = Column(Integer, ForeignKey("customers.customer_id"))
    referral_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")
    reward_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    referrer = relationship("Customer", foreign_keys=[referrer_id])
    referred = relationship("Customer", foreign_keys=[referred_id])
