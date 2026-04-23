"""
SQLAlchemy database models.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class User(Base):
    """User model - simple session-based users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plans = relationship("TravelPlanDB", back_populates="user", cascade="all, delete-orphan")


class TravelPlanDB(Base):
    """Travel plan model."""
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Plan details
    trip_title = Column(String(200), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    depart_date = Column(String(20), nullable=False)
    return_date = Column(String(20), nullable=False)
    budget_usd = Column(Integer, nullable=False)
    
    # Status
    status = Column(String(50), default="draft")  # draft, approved, rejected, executed
    
    # JSON data
    plan_data = Column(JSON, nullable=True)  # Full plan as JSON
    user_request = Column(Text, nullable=True)  # Original user request
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="plans")
    execution = relationship("ExecutionResult", back_populates="plan", uselist=False, cascade="all, delete-orphan")


class ExecutionResult(Base):
    """Execution results for a travel plan."""
    __tablename__ = "execution_results"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False, unique=True)
    
    # Results
    status = Column(String(50), nullable=False)  # executed, rejected, error
    results_data = Column(JSON, nullable=True)  # Full results as JSON
    
    # Selected options (for budget tracking)
    selected_flight = Column(Integer, nullable=True)
    selected_hotel = Column(Integer, nullable=True)
    selected_car = Column(Integer, nullable=True)
    selected_activities = Column(JSON, nullable=True)  # List of indices
    
    total_cost = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plan = relationship("TravelPlanDB", back_populates="execution")