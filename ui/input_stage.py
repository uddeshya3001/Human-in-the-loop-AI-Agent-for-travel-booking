"""
Input stage UI - where users describe their trip.
"""

import streamlit as st
from config.settings import ICONS


def render_input_stage(graph, config):
    """
    Render the input form for trip details.
    
    Args:
        graph: LangGraph compiled graph
        config: Graph configuration with thread_id
    
    Returns:
        None (modifies session state)
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h2>{ICONS['flight']} Plan Your Perfect Trip</h2>
        <p style="font-size: 18px; color: #666;">
            Tell us about your travel plans and we'll create a personalized itinerary
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input form
    with st.form("trip_form"):
        request = st.text_area(
            "Describe your trip",
            placeholder="Example: Plan a 5 day trip from New York to Paris from 2026-06-10 to 2026-06-15 with a budget of 3000 USD. I'm interested in museums, food tours, and local experiences.",
            height=150,
            help="Include: origin, destination, dates, budget, and interests"
        )
        
        # Optional: Add structured inputs
        with st.expander("Or use structured input (optional)"):
            col1, col2 = st.columns(2)
            with col1:
                origin = st.text_input("Origin City")
                destination = st.text_input("Destination City")
            with col2:
                depart_date = st.date_input("Departure Date")
                return_date = st.date_input("Return Date")
            
            budget = st.number_input("Budget (USD)", min_value=500, max_value=50000, value=3000, step=100)
            interests = st.text_input("Interests (comma-separated)", placeholder="museums, food, adventure")
        
        submitted = st.form_submit_button("🚀 Generate Plan", type="primary", use_container_width=True)
    
    if submitted:
        if request.strip():
            # Use natural language request
            final_request = request
        elif origin and destination and depart_date and return_date:
            # Build request from structured input
            final_request = f"Plan a trip from {origin} to {destination} from {depart_date} to {return_date} with a budget of {budget} USD."
            if interests:
                final_request += f" I'm interested in {interests}."
        else:
            st.warning("Please provide trip details either in the text area or using structured inputs.")
            return
        
        # Generate new thread for new request
        import uuid
        st.session_state.thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        
        initial_state = {
            "user_request": final_request,
            "plan": None,
            "approval": None,
            "execution": None
        }
        
        with st.spinner("✨ Creating your personalized travel plan..."):
            try:
                # Stream through the graph until interrupt
                for event in graph.stream(initial_state, config, stream_mode="values"):
                    pass
                
                # Get the current state after interrupt
                current_state = graph.get_state(config)
                
                # Check if we hit an interrupt
                if current_state.next:
                    plan = current_state.values.get("plan")
                    if plan:
                        st.session_state.pending_plan = plan
                        st.session_state.stage = "pending"
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error generating plan: {e}")