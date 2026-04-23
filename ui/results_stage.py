"""
Results stage UI - display execution results with visual cards and budget tracking.
"""

import streamlit as st
from ui.components import (
    render_plan_header,
    render_flight_card,
    render_hotel_card,
    render_car_card,
    render_activity_card,
    render_budget_summary
)
from config.settings import ICONS


def render_results_stage():
    """
    Render execution results with visual cards and real-time budget tracking.
    """
    execution = st.session_state.get("execution_result")
    plan = st.session_state.get("pending_plan")
    
    if not execution:
        st.warning("No execution result found")
        if st.button("🔄 Start Over", type="primary"):
            reset_app()
        return
    
    # Handle rejection
    if execution["status"] == "rejected":
        st.warning(f"{ICONS['warning']} Plan was rejected.")
        if st.button("🔄 Plan Another Trip", type="primary"):
            reset_app()
        return
    
    # Handle errors
    if execution["status"] == "error":
        st.error(f"{ICONS['error']} Execution Error")
        st.error(f"Reason: {execution.get('reason', 'Unknown error')}")
        if st.button("🔄 Try Again", type="primary"):
            reset_app()
        return
    
    # Success - render results
    if execution["status"] == "executed":
        # Header
        if plan:
            render_plan_header(plan)
        
        st.success(f"{ICONS['success']} Your personalized travel options are ready!")
        st.markdown("**Select your preferred options to see your final budget:**")
        
        results = execution.get("results", [])
        
        if not results:
            st.warning("No results found")
            if st.button("🔄 Try Again", type="primary"):
                reset_app()
            return
        
        # Organize results by tool
        flights = []
        hotels = []
        cars = []
        activities = []
        
        for result in results:
            tool = result.get("tool", "")
            if "error" in result:
                st.error(f"{ICONS['error']} {tool}: {result['error']}")
                continue
            
            tool_results = result.get("results", [])
            
            if "flight" in tool:
                flights = tool_results
            elif "hotel" in tool:
                hotels = tool_results
            elif "car" in tool:
                cars = tool_results
            elif "activit" in tool:
                activities = tool_results
        
        # Initialize selection state
        if "selected_options" not in st.session_state:
            st.session_state.selected_options = {
                "flight": None,
                "hotel": None,
                "car": None,
                "activities": []
            }
        
        # Budget Summary at the top
        st.markdown("---")
        
        # Calculate selected costs
        selected_costs = {
            "Flights": 0,
            "Hotels": 0,
            "Car Rentals": 0,
            "Activities": 0
        }
        
        # Track selections and costs
        selected_flight_cost = 0
        selected_hotel_cost = 0
        selected_car_cost = 0
        selected_activities_cost = 0
        
        # Render results in tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            f"{ICONS['flight']} Flights ({len(flights)})",
            f"{ICONS['hotel']} Hotels ({len(hotels)})",
            f"{ICONS['car']} Cars ({len(cars)})",
            f"{ICONS['activity']} Activities ({len(activities)})"
        ])
        
        with tab1:
            if flights:
                st.subheader("✈️ Select Your Flight")
                for i, flight in enumerate(flights):
                    is_selected, cost = render_flight_card(
                        flight, 
                        i, 
                        selected=st.session_state.selected_options["flight"] == i,
                        key_prefix="results"
                    )
                    if is_selected:
                        st.session_state.selected_options["flight"] = i
                        selected_flight_cost = cost
                    elif st.session_state.selected_options["flight"] == i and not is_selected:
                        st.session_state.selected_options["flight"] = None
            else:
                st.info("No flight options available")
        
        with tab2:
            if hotels:
                st.subheader("🏨 Select Your Hotel")
                for i, hotel in enumerate(hotels):
                    is_selected, cost = render_hotel_card(
                        hotel, 
                        i, 
                        selected=st.session_state.selected_options["hotel"] == i,
                        key_prefix="results"
                    )
                    if is_selected:
                        st.session_state.selected_options["hotel"] = i
                        selected_hotel_cost = cost
                    elif st.session_state.selected_options["hotel"] == i and not is_selected:
                        st.session_state.selected_options["hotel"] = None
            else:
                st.info("No hotel options available")
        
        with tab3:
            if cars:
                st.subheader("🚗 Select Your Car Rental")
                for i, car in enumerate(cars):
                    is_selected, cost = render_car_card(
                        car, 
                        i, 
                        selected=st.session_state.selected_options["car"] == i,
                        key_prefix="results"
                    )
                    if is_selected:
                        st.session_state.selected_options["car"] = i
                        selected_car_cost = cost
                    elif st.session_state.selected_options["car"] == i and not is_selected:
                        st.session_state.selected_options["car"] = None
            else:
                st.info("No car rental options available")
        
        with tab4:
            if activities:
                st.subheader("🎭 Select Your Activities")
                st.info("💡 You can select multiple activities")
                
                for i, activity in enumerate(activities):
                    is_selected, cost = render_activity_card(
                        activity, 
                        i, 
                        selected=i in st.session_state.selected_options["activities"],
                        key_prefix="results"
                    )
                    if is_selected and i not in st.session_state.selected_options["activities"]:
                        st.session_state.selected_options["activities"].append(i)
                        selected_activities_cost += cost
                    elif not is_selected and i in st.session_state.selected_options["activities"]:
                        st.session_state.selected_options["activities"].remove(i)
                
                # Calculate total activities cost
                for i in st.session_state.selected_options["activities"]:
                    if i < len(activities):
                        selected_activities_cost += activities[i].get('price_usd', 0)
            else:
                st.info("No activity options available")
        
        # Update selected costs
        selected_costs["Flights"] = selected_flight_cost
        selected_costs["Hotels"] = selected_hotel_cost
        selected_costs["Car Rentals"] = selected_car_cost
        selected_costs["Activities"] = selected_activities_cost
        
        # Budget summary with real-time tracking
        st.markdown("---")
        if plan:
            render_budget_summary(plan, selected_costs=selected_costs)
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Plan Another Trip", type="primary", use_container_width=True):
                reset_app()
        
        with col2:
            if st.button("📥 Export Results (Coming Soon)", use_container_width=True, disabled=True):
                st.info("Export feature coming soon!")


def reset_app():
    """Reset the application to initial state."""
    import uuid
    for key in ["pending_plan", "execution_result", "selected_options"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.stage = "input"
    st.session_state.thread_id = str(uuid.uuid4())
    st.rerun()