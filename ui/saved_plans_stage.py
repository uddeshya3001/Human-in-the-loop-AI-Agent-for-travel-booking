"""
Saved plans stage - view and manage saved travel plans.
"""

import streamlit as st
from database.db import get_db
from database.operations import get_user_plans, delete_plan, get_plan_by_id, get_execution_result
from ui.components import render_plan_header
from utils.helpers import format_currency, format_date
from config.settings import ICONS


def render_saved_plans_stage():
    """
    Render saved plans view.
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h2>📚 My Saved Plans</h2>
        <p style="font-size: 18px; color: #666;">
            View and manage your travel plans
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get session ID
    session_id = st.session_state.get("user_session_id")
    
    if not session_id:
        st.warning("No session found. Please create a new plan first.")
        if st.button("🆕 Create New Plan", type="primary"):
            st.session_state.stage = "input"
            st.rerun()
        return
    
    # Get database session
    db = get_db()
    
    try:
        # Get user plans
        plans = get_user_plans(db, session_id)
        
        if not plans:
            st.info("📭 No saved plans yet. Create your first travel plan!")
            if st.button("🆕 Create New Plan", type="primary"):
                st.session_state.stage = "input"
                st.rerun()
            return
        
        # Filter options
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "Draft", "Approved", "Executed", "Rejected"],
                key="status_filter"
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest First", "Oldest First", "Budget (High to Low)", "Budget (Low to High)"],
                key="sort_by"
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🆕 New Plan", type="primary", use_container_width=True):
                st.session_state.stage = "input"
                st.rerun()
        
        # Apply filters
        filtered_plans = plans
        
        if status_filter != "All":
            filtered_plans = [p for p in plans if p.status.lower() == status_filter.lower()]
        
        # Apply sorting
        if sort_by == "Oldest First":
            filtered_plans = sorted(filtered_plans, key=lambda x: x.created_at)
        elif sort_by == "Budget (High to Low)":
            filtered_plans = sorted(filtered_plans, key=lambda x: x.budget_usd, reverse=True)
        elif sort_by == "Budget (Low to High)":
            filtered_plans = sorted(filtered_plans, key=lambda x: x.budget_usd)
        # "Newest First" is default (already sorted in query)
        
        st.markdown("---")
        st.markdown(f"**Found {len(filtered_plans)} plan(s)**")
        
        # Display plans
        for plan in filtered_plans:
            render_plan_card(plan, db)
    
    finally:
        db.close()


def render_plan_card(plan, db):
    """Render a single saved plan card."""
    
    # Status badge
    status_colors = {
        "draft": "gray",
        "approved": "blue",
        "executed": "green",
        "rejected": "red"
    }
    
    status_color = status_colors.get(plan.status.lower(), "gray")
    
    with st.container():
        st.markdown(f"""
        <div style="border: 2px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 15px 0; background-color: #ffffff;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">{plan.trip_title}</h3>
                <span style="background-color: {status_color}; color: white; padding: 5px 15px; border-radius: 15px; font-size: 12px; font-weight: bold;">
                    {plan.status.upper()}
                </span>
            </div>
            <p style="margin: 10px 0; color: #666;">
                {ICONS['location']} {plan.origin} → {plan.destination}
            </p>
            <p style="margin: 5px 0; color: #666;">
                {ICONS['calendar']} {format_date(plan.depart_date)} - {format_date(plan.return_date)}
            </p>
            <p style="margin: 5px 0; color: #666;">
                {ICONS['budget']} Budget: {format_currency(plan.budget_usd)}
            </p>
            <p style="margin: 5px 0; color: #999; font-size: 12px;">
                Created: {plan.created_at.strftime("%B %d, %Y at %I:%M %p")}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👁️ View", key=f"view_{plan.id}", use_container_width=True):
                view_plan_details(plan, db)
        
        with col2:
            if plan.status.lower() in ["draft", "approved"]:
                if st.button("▶️ Resume", key=f"resume_{plan.id}", use_container_width=True):
                    resume_plan(plan)
        
        with col3:
            if plan.status.lower() == "executed":
                if st.button("📊 Results", key=f"results_{plan.id}", use_container_width=True):
                    view_results(plan, db)
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{plan.id}", use_container_width=True, type="secondary"):
                delete_plan_confirm(plan.id, db)


def view_plan_details(plan, db):
    """View plan details in a modal."""
    with st.expander(f"📋 Plan Details: {plan.trip_title}", expanded=True):
        st.json(plan.plan_data)
        
        if plan.user_request:
            st.markdown("### Original Request")
            st.info(plan.user_request)
        
        # Check for execution results
        execution = get_execution_result(db, plan.id)
        if execution:
            st.markdown("### Execution Results")
            st.json(execution.results_data)
            
            if execution.total_cost:
                st.success(f"Total Cost: {format_currency(execution.total_cost)}")


def resume_plan(plan):
    """Resume a saved plan."""
    # Load plan data into session state
    st.session_state.pending_plan = plan.plan_data
    st.session_state.thread_id = plan.thread_id
    
    if plan.status.lower() == "draft":
        st.session_state.stage = "pending"
    elif plan.status.lower() == "approved":
        st.session_state.stage = "pending"  # Can re-approve or modify
    
    st.success(f"✅ Resumed plan: {plan.trip_title}")
    st.rerun()


def view_results(plan, db):
    """View execution results for a plan."""
    execution = get_execution_result(db, plan.id)
    
    if not execution:
        st.warning("No execution results found for this plan.")
        return
    
    # Load into results stage
    st.session_state.pending_plan = plan.plan_data
    st.session_state.execution_result = execution.results_data
    st.session_state.stage = "completed"
    
    st.success(f"✅ Loading results for: {plan.trip_title}")
    st.rerun()


def delete_plan_confirm(plan_id, db):
    """Delete a plan with confirmation."""
    if delete_plan(db, plan_id):
        st.success("✅ Plan deleted successfully!")
        st.rerun()
    else:
        st.error("❌ Failed to delete plan.")