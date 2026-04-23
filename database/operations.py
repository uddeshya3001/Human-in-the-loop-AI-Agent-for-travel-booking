"""
Database CRUD operations.
"""

from sqlalchemy.orm import Session
from database.models import User, TravelPlanDB, ExecutionResult
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


def get_or_create_user(db: Session, session_id: str) -> User:
    """
    Get existing user or create new one.
    
    Args:
        db: Database session
        session_id: User session ID
    
    Returns:
        User object
    """
    user = db.query(User).filter(User.session_id == session_id).first()
    
    if not user:
        user = User(session_id=session_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update last active
        user.last_active = datetime.utcnow()
        db.commit()
    
    return user


def save_plan(
    db: Session,
    session_id: str,
    thread_id: str,
    plan_data: Dict[str, Any],
    user_request: str,
    status: str = "draft"
) -> TravelPlanDB:
    """
    Save a travel plan to database.
    
    Args:
        db: Database session
        session_id: User session ID
        thread_id: LangGraph thread ID
        plan_data: Plan data dictionary
        user_request: Original user request
        status: Plan status
    
    Returns:
        Saved TravelPlanDB object
    """
    # Get or create user
    user = get_or_create_user(db, session_id)
    
    # Check if plan already exists
    existing_plan = db.query(TravelPlanDB).filter(
        TravelPlanDB.thread_id == thread_id
    ).first()
    
    if existing_plan:
        # Update existing plan
        existing_plan.plan_data = plan_data
        existing_plan.user_request = user_request
        existing_plan.status = status
        existing_plan.trip_title = plan_data.get("trip_title", "Untitled Trip")
        existing_plan.origin = plan_data.get("origin", "Unknown")
        existing_plan.destination = plan_data.get("destination", "Unknown")
        existing_plan.depart_date = plan_data.get("depart_date", "")
        existing_plan.return_date = plan_data.get("return_date", "")
        existing_plan.budget_usd = plan_data.get("budget_usd", 0)
        existing_plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_plan)
        return existing_plan
    
    # Create new plan
    plan = TravelPlanDB(
        user_id=user.id,
        thread_id=thread_id,
        trip_title=plan_data.get("trip_title", "Untitled Trip"),
        origin=plan_data.get("origin", "Unknown"),
        destination=plan_data.get("destination", "Unknown"),
        depart_date=plan_data.get("depart_date", ""),
        return_date=plan_data.get("return_date", ""),
        budget_usd=plan_data.get("budget_usd", 0),
        plan_data=plan_data,
        user_request=user_request,
        status=status
    )
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    return plan


def get_plan_by_id(db: Session, plan_id: int) -> Optional[TravelPlanDB]:
    """
    Get a plan by ID.
    
    Args:
        db: Database session
        plan_id: Plan ID
    
    Returns:
        TravelPlanDB object or None
    """
    return db.query(TravelPlanDB).filter(TravelPlanDB.id == plan_id).first()


def get_plan_by_thread_id(db: Session, thread_id: str) -> Optional[TravelPlanDB]:
    """
    Get a plan by thread ID.
    
    Args:
        db: Database session
        thread_id: Thread ID
    
    Returns:
        TravelPlanDB object or None
    """
    return db.query(TravelPlanDB).filter(TravelPlanDB.thread_id == thread_id).first()


def get_user_plans(
    db: Session,
    session_id: str,
    limit: int = 50,
    status: Optional[str] = None
) -> List[TravelPlanDB]:
    """
    Get all plans for a user.
    
    Args:
        db: Database session
        session_id: User session ID
        limit: Maximum number of plans to return
        status: Filter by status (optional)
    
    Returns:
        List of TravelPlanDB objects
    """
    user = db.query(User).filter(User.session_id == session_id).first()
    
    if not user:
        return []
    
    query = db.query(TravelPlanDB).filter(TravelPlanDB.user_id == user.id)
    
    if status:
        query = query.filter(TravelPlanDB.status == status)
    
    return query.order_by(TravelPlanDB.created_at.desc()).limit(limit).all()


def delete_plan(db: Session, plan_id: int) -> bool:
    """
    Delete a plan.
    
    Args:
        db: Database session
        plan_id: Plan ID
    
    Returns:
        True if deleted, False if not found
    """
    plan = db.query(TravelPlanDB).filter(TravelPlanDB.id == plan_id).first()
    
    if not plan:
        return False
    
    db.delete(plan)
    db.commit()
    return True


def update_plan_status(db: Session, thread_id: str, status: str) -> Optional[TravelPlanDB]:
    """
    Update plan status.
    
    Args:
        db: Database session
        thread_id: Thread ID
        status: New status
    
    Returns:
        Updated TravelPlanDB object or None
    """
    plan = db.query(TravelPlanDB).filter(TravelPlanDB.thread_id == thread_id).first()
    
    if not plan:
        return None
    
    plan.status = status
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    
    return plan


def save_execution_result(
    db: Session,
    thread_id: str,
    status: str,
    results_data: Dict[str, Any],
    selected_options: Optional[Dict[str, Any]] = None,
    total_cost: Optional[float] = None
) -> Optional[ExecutionResult]:
    """
    Save execution results.
    
    Args:
        db: Database session
        thread_id: Thread ID
        status: Execution status
        results_data: Results data
        selected_options: Selected options dictionary
        total_cost: Total cost of selections
    
    Returns:
        ExecutionResult object or None
    """
    # Get plan
    plan = db.query(TravelPlanDB).filter(TravelPlanDB.thread_id == thread_id).first()
    
    if not plan:
        return None
    
    # Check if execution result already exists
    existing_result = db.query(ExecutionResult).filter(
        ExecutionResult.plan_id == plan.id
    ).first()
    
    if existing_result:
        # Update existing result
        existing_result.status = status
        existing_result.results_data = results_data
        if selected_options:
            existing_result.selected_flight = selected_options.get("flight")
            existing_result.selected_hotel = selected_options.get("hotel")
            existing_result.selected_car = selected_options.get("car")
            existing_result.selected_activities = selected_options.get("activities")
        if total_cost is not None:
            existing_result.total_cost = total_cost
        db.commit()
        db.refresh(existing_result)
        return existing_result
    
    # Create new execution result
    execution = ExecutionResult(
        plan_id=plan.id,
        status=status,
        results_data=results_data,
        selected_flight=selected_options.get("flight") if selected_options else None,
        selected_hotel=selected_options.get("hotel") if selected_options else None,
        selected_car=selected_options.get("car") if selected_options else None,
        selected_activities=selected_options.get("activities") if selected_options else None,
        total_cost=total_cost
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    return execution


def get_execution_result(db: Session, plan_id: int) -> Optional[ExecutionResult]:
    """
    Get execution result for a plan.
    
    Args:
        db: Database session
        plan_id: Plan ID
    
    Returns:
        ExecutionResult object or None
    """
    return db.query(ExecutionResult).filter(ExecutionResult.plan_id == plan_id).first()