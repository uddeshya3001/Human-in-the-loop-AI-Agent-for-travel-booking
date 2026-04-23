"""
Reusable UI components for displaying travel plan elements.
"""

import streamlit as st
from config.settings import ICONS
from utils.helpers import format_currency, format_date


def render_flight_card(flight_data, index=0, selected=False, key_prefix=""):
    """Render a single flight option as a selectable card."""
    card_style = """
        border: 3px solid #4CAF50;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
    """ if selected else """
        border: 2px solid #e0e0e0;
    """
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style="{card_style} border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; transition: all 0.3s;">
                <h4 style="margin: 0;">{ICONS['flight']} {flight_data.get('airline', 'Unknown')}</h4>
                <p style="margin: 5px 0;"><strong>Route:</strong> {flight_data.get('route', 'N/A')}</p>
                <p style="margin: 5px 0; color: #4CAF50; font-size: 20px; font-weight: bold;">
                    {format_currency(flight_data.get('price_usd', 0))}
                </p>
                <p style="margin: 5px 0;"><strong>Duration:</strong> {flight_data.get('duration', 'N/A')} • {flight_data.get('stops', 'N/A')}</p>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    {flight_data.get('departure', 'N/A')} → {flight_data.get('return', 'N/A')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            is_selected = st.checkbox(
                "Select",
                value=selected,
                key=f"{key_prefix}_flight_{index}",
                label_visibility="visible"
            )
    
    return is_selected, flight_data.get('price_usd', 0)


def render_hotel_card(hotel_data, index=0, selected=False, key_prefix=""):
    """Render a single hotel option as a selectable card."""
    card_style = """
        border: 3px solid #2196F3;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
    """ if selected else """
        border: 2px solid #e0e0e0;
    """
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            rating_stars = '⭐' * int(hotel_data.get('rating', 0))
            amenities = ', '.join(hotel_data.get('amenities', []))
            
            st.markdown(f"""
            <div style="{card_style} border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; transition: all 0.3s;">
                <h4 style="margin: 0;">{ICONS['hotel']} {hotel_data.get('name', 'Unknown')}</h4>
                <p style="margin: 5px 0;">{rating_stars} • {hotel_data.get('location', 'N/A')}</p>
                <p style="margin: 5px 0; color: #2196F3; font-size: 20px; font-weight: bold;">
                    {format_currency(hotel_data.get('nightly_usd', 0))}/night
                </p>
                <p style="margin: 5px 0;"><strong>Total:</strong> {format_currency(hotel_data.get('total_usd', 0))}</p>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    <strong>Amenities:</strong> {amenities}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            is_selected = st.checkbox(
                "Select",
                value=selected,
                key=f"{key_prefix}_hotel_{index}",
                label_visibility="visible"
            )
    
    return is_selected, hotel_data.get('total_usd', 0)


def render_car_card(car_data, index=0, selected=False, key_prefix=""):
    """Render a single car rental option as a selectable card."""
    card_style = """
        border: 3px solid #FF9800;
        box-shadow: 0 4px 8px rgba(255, 152, 0, 0.3);
    """ if selected else """
        border: 2px solid #e0e0e0;
    """
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            features = ', '.join(car_data.get('features', []))
            
            st.markdown(f"""
            <div style="{card_style} border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; transition: all 0.3s;">
                <h4 style="margin: 0;">{ICONS['car']} {car_data.get('company', 'Unknown')}</h4>
                <p style="margin: 5px 0;"><strong>Type:</strong> {car_data.get('car_type', 'N/A')} - {car_data.get('model', 'N/A')}</p>
                <p style="margin: 5px 0; color: #FF9800; font-size: 20px; font-weight: bold;">
                    {format_currency(car_data.get('daily_usd', 0))}/day
                </p>
                <p style="margin: 5px 0;"><strong>Total:</strong> {format_currency(car_data.get('total_usd', 0))}</p>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    <strong>Pickup:</strong> {car_data.get('pickup_location', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    <strong>Features:</strong> {features}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            is_selected = st.checkbox(
                "Select",
                value=selected,
                key=f"{key_prefix}_car_{index}",
                label_visibility="visible"
            )
    
    return is_selected, car_data.get('total_usd', 0)


def render_activity_card(activity_data, index=0, selected=False, key_prefix=""):
    """Render a single activity option as a selectable card."""
    card_style = """
        border: 3px solid #9C27B0;
        box-shadow: 0 4px 8px rgba(156, 39, 176, 0.3);
    """ if selected else """
        border: 2px solid #e0e0e0;
    """
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            rating_stars = '⭐' * int(activity_data.get('rating', 0))
            
            st.markdown(f"""
            <div style="{card_style} border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9; transition: all 0.3s;">
                <h4 style="margin: 0;">{ICONS['activity']} {activity_data.get('name', 'Unknown')}</h4>
                <p style="margin: 5px 0;"><strong>Category:</strong> {activity_data.get('category', 'N/A')} • {rating_stars}</p>
                <p style="margin: 5px 0; color: #9C27B0; font-size: 20px; font-weight: bold;">
                    {format_currency(activity_data.get('price_usd', 0))}
                </p>
                <p style="margin: 5px 0;"><strong>Duration:</strong> {activity_data.get('duration_hours', 0)} hours</p>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    {activity_data.get('description', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            is_selected = st.checkbox(
                "Select",
                value=selected,
                key=f"{key_prefix}_activity_{index}",
                label_visibility="visible"
            )
    
    return is_selected, activity_data.get('price_usd', 0)


def render_budget_summary(plan, execution_results=None, selected_costs=None):
    """
    Render real-time budget breakdown and summary.
    
    Args:
        plan: The travel plan
        execution_results: Execution results (if available)
        selected_costs: Dictionary with selected costs by category
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; color: white; margin: 20px 0;">
        <h2 style="margin: 0; color: white;">{ICONS['budget']} Budget Tracker</h2>
    </div>
    """, unsafe_allow_html=True)
    
    total_budget = plan.get('budget_usd', 0)
    
    # If we have selected costs, use those
    if selected_costs:
        total_spent = sum(selected_costs.values())
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Budget",
                format_currency(total_budget),
                help="Your total trip budget"
            )
        
        with col2:
            st.metric(
                "Selected Items",
                format_currency(total_spent),
                delta=f"{(total_spent/total_budget*100):.1f}%" if total_budget > 0 else "0%",
                help="Total cost of selected options"
            )
        
        with col3:
            remaining = total_budget - total_spent
            st.metric(
                "Remaining",
                format_currency(remaining),
                delta=f"{(remaining/total_budget*100):.1f}%" if total_budget > 0 else "0%",
                delta_color="normal" if remaining >= 0 else "inverse",
                help="Budget remaining after selections"
            )
        
        # Progress bar
        progress = min(total_spent / total_budget, 1.0) if total_budget > 0 else 0
        
        if progress > 1.0:
            st.error(f"⚠️ Over budget by {format_currency(total_spent - total_budget)}!")
        elif progress > 0.9:
            st.warning(f"⚠️ Using {progress*100:.1f}% of budget")
        else:
            st.success(f"✅ Using {progress*100:.1f}% of budget")
        
        st.progress(progress)
        
        # Category breakdown
        st.markdown("### 📊 Cost Breakdown by Category")
        
        for category, cost in selected_costs.items():
            if cost > 0:
                percentage = (cost / total_budget * 100) if total_budget > 0 else 0
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{category}**")
                with col2:
                    st.markdown(f"{format_currency(cost)}")
                with col3:
                    st.markdown(f"{percentage:.1f}%")
        
        # Budget suggestions
        if remaining > 0:
            st.info(f"💡 **Suggestion:** You have {format_currency(remaining)} remaining. Consider upgrading your selections or adding more activities!")
        elif remaining < 0:
            st.error(f"💡 **Suggestion:** You're over budget. Consider selecting less expensive options to stay within your {format_currency(total_budget)} budget.")
    
    # If we have execution results (old behavior for results page)
    elif execution_results:
        total_spent = 0
        breakdown = {}
        
        for result in execution_results.get('results', []):
            tool_name = result.get('tool', '')
            tool_results = result.get('results', [])
            
            if tool_results and len(tool_results) > 0:
                if 'price_usd' in tool_results[0]:
                    cost = tool_results[0]['price_usd']
                elif 'total_usd' in tool_results[0]:
                    cost = tool_results[0]['total_usd']
                else:
                    cost = 0
                
                category = tool_name.replace('search_', '').title()
                breakdown[category] = cost
                total_spent += cost
        
        # Display breakdown
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Budget", format_currency(total_budget))
        with col2:
            st.metric("Estimated Total", format_currency(total_spent))
        
        # Progress bar
        progress = min(total_spent / total_budget, 1.0) if total_budget > 0 else 0
        st.progress(progress)
        
        remaining = total_budget - total_spent
        if remaining >= 0:
            st.success(f"Remaining: {format_currency(remaining)}")
        else:
            st.error(f"Over budget by: {format_currency(abs(remaining))}")
        
        # Breakdown by category
        st.markdown("### Cost Breakdown")
        for tool, cost in breakdown.items():
            percentage = (cost / total_budget * 100) if total_budget > 0 else 0
            st.markdown(f"**{tool}:** {format_currency(cost)} ({percentage:.1f}%)")
    
    else:
        # Just show total budget
        st.info(f"**Total Budget:** {format_currency(total_budget)}")
        st.markdown("*Select options below to see real-time budget tracking*")


def render_plan_header(plan):
    """Render plan header with trip details."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0; color: white;">{plan.get('trip_title', 'Travel Plan')}</h1>
        <h3 style="margin: 10px 0; color: white;">
            {ICONS['location']} {plan.get('origin', 'Unknown')} → {plan.get('destination', 'Unknown')}
        </h3>
        <p style="margin: 5px 0; font-size: 18px; color: white;">
            {ICONS['calendar']} {format_date(plan.get('depart_date', ''))} - {format_date(plan.get('return_date', ''))}
        </p>
        <p style="margin: 5px 0; font-size: 18px; color: white;">
            {ICONS['budget']} Budget: {format_currency(plan.get('budget_usd', 0))}
        </p>
    </div>
    """, unsafe_allow_html=True)