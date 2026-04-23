"""
Approval stage UI - visual card-based plan review and editing.
"""

import streamlit as st
import json
from langgraph.types import Command
from pydantic import ValidationError

from models.schemas import TravelPlan
from ui.components import (
    render_plan_header,
    render_flight_card,
    render_hotel_card,
    render_car_card,
    render_activity_card,
    render_budget_summary
)
from config.settings import ICONS
from utils.helpers import calculate_nights


def render_approval_stage(graph, config):
    """
    Render visual approval interface with cards.
    
    Args:
        graph: LangGraph compiled graph
        config: Graph configuration with thread_id
    """
    plan = st.session_state.pending_plan
    
    # Render header
    render_plan_header(plan)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"{ICONS['flight']} Flights",
        f"{ICONS['hotel']} Hotels",
        f"{ICONS['car']} Car Rentals",
        f"{ICONS['activity']} Activities",
        "📋 Full Plan (JSON)"
    ])
    
    # Flights Tab
    with tab1:
        st.subheader("Select Your Flight")
        flight_call = next((tc for tc in plan['tool_calls'] if tc['name'] == 'search_flights'), None)
        if flight_call:
            st.info(f"**Route:** {flight_call['args']['origin']} → {flight_call['args']['destination']}")
            st.info(f"**Budget:** ${flight_call['args']['budget_usd']:,}")
            st.info("*Preview only - actual options will appear after approval*")
        else:
            st.warning("No flight search configured")
    
    # Hotels Tab
    with tab2:
        st.subheader("Select Your Hotel")
        hotel_call = next((tc for tc in plan['tool_calls'] if tc['name'] == 'search_hotels'), None)
        if hotel_call:
            nights = calculate_nights(plan['depart_date'], plan['return_date'])
            st.info(f"**City:** {hotel_call['args']['city']}")
            st.info(f"**Nights:** {nights}")
            st.info(f"**Budget:** ${hotel_call['args']['budget_usd']:,}")
            st.info("*Preview only - actual options will appear after approval*")
        else:
            st.warning("No hotel search configured")
    
    # Cars Tab
    with tab3:
        st.subheader("Select Your Car Rental")
        car_call = next((tc for tc in plan['tool_calls'] if tc['name'] == 'search_cars'), None)
        if car_call:
            st.info(f"**City:** {car_call['args']['city']}")
            st.info(f"**Days:** {car_call['args']['days']}")
            st.info(f"**Budget:** ${car_call['args']['budget_usd']:,}")
            st.info("*Preview only - actual options will appear after approval*")
        else:
            st.warning("No car rental search configured")
    
    # Activities Tab
    with tab4:
        st.subheader("Select Your Activities")
        activity_call = next((tc for tc in plan['tool_calls'] if tc['name'] == 'search_activities'), None)
        if activity_call:
            st.info(f"**City:** {activity_call['args']['city']}")
            st.info(f"**Days:** {activity_call['args']['days']}")
            st.info(f"**Interests:** {activity_call['args']['interests']}")
            st.info(f"**Budget:** ${activity_call['args']['budget_usd']:,}")
            st.info("*Preview only - actual options will appear after approval*")
        else:
            st.warning("No activities search configured")
    
    # JSON Tab (for advanced users)
    with tab5:
        st.subheader("Advanced: Edit Plan JSON")
        edited_json = st.text_area(
            "Edit the plan structure (advanced users only)",
            value=json.dumps(plan, indent=2),
            height=400,
            key="edited_plan_json"
        )
    
    # Budget summary
    st.markdown("---")
    render_budget_summary(plan)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        approve_btn = st.button(
            f"{ICONS['success']} Approve & Search",
            type="primary",
            use_container_width=True,
            help="Execute searches with this plan"
        )
    
    with col2:
        reject_btn = st.button(
            f"{ICONS['error']} Reject",
            use_container_width=True,
            help="Reject this plan"
        )
    
    with col3:
        reset_btn = st.button(
            "🔄 Start Over",
            use_container_width=True
        )
    
    # Handle button clicks
    if approve_btn:
        handle_approval(graph, config, plan, edited_json)
    
    if reject_btn:
        handle_rejection(graph, config)
    
    if reset_btn:
        handle_reset()


def handle_approval(graph, config, plan, edited_json):
    """Handle plan approval and execution."""
    edited_plan = plan
    
    # Validate edited JSON if modified
    try:
        edited_plan = json.loads(edited_json)
        TravelPlan.model_validate(edited_plan)
    except (json.JSONDecodeError, ValidationError) as exc:
        st.error(f"❌ Invalid plan structure: {exc}")
        st.stop()
    
    resume_data = {
        "approved": True,
        "edited_plan": edited_plan
    }
    
    with st.spinner("🔍 Searching for flights, hotels, cars, and activities..."):
        try:
            # Resume the graph with approval
            for event in graph.stream(Command(resume=resume_data), config, stream_mode="values"):
                pass
            
            # Get final state
            final_state = graph.get_state(config)
            st.session_state.execution_result = final_state.values.get("execution")
            st.session_state.stage = "completed"
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error during execution: {e}")


def handle_rejection(graph, config):
    """Handle plan rejection."""
    resume_data = {
        "approved": False,
        "edited_plan": None
    }
    
    with st.spinner("Processing rejection..."):
        try:
            # Resume the graph with rejection
            for event in graph.stream(Command(resume=resume_data), config, stream_mode="values"):
                pass
            
            # Get final state
            final_state = graph.get_state(config)
            st.session_state.execution_result = final_state.values.get("execution")
            st.session_state.stage = "completed"
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error during rejection: {e}")


def handle_reset():
    """Reset to input stage."""
    import uuid
    for key in ["pending_plan", "execution_result"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.stage = "input"
    st.session_state.thread_id = str(uuid.uuid4())
    st.rerun()