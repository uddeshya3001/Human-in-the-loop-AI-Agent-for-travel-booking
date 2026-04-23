"""
Main Streamlit application for Human-in-the-Loop Travel Agent.
"""

import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from graph.builder import build_graph
from ui import render_input_stage, render_approval_stage, render_results_stage, render_saved_plans_stage
from database.db import init_db


# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ OPENAI_API_KEY not found in .env file")
    st.stop()

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="AI Travel Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("🧭 Navigation")
    
    page = st.radio(
        "Go to:",
        ["🆕 New Plan", "📚 My Plans"],
        key="navigation"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Session Info")
    
    # Show session ID
    if "user_session_id" in st.session_state:
        st.caption(f"Session: {st.session_state.user_session_id[:8]}...")
    else:
        st.caption("No active session")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption("AI-powered travel planning with human-in-the-loop approval")

# Main content area
if page == "📚 My Plans":
    render_saved_plans_stage()
else:
    # App title
    st.title("✈️ AI Travel Agent")
    st.markdown("*Plan your perfect trip with AI-powered recommendations*")
    st.markdown("---")

    # Initialize graph (cached)
    @st.cache_resource
    def get_graph():
        """Get or create the compiled graph."""
        return build_graph()

    graph = get_graph()

    # Initialize session state
    if "user_session_id" not in st.session_state:
        st.session_state.user_session_id = str(uuid.uuid4())

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "stage" not in st.session_state:
        st.session_state.stage = "input"

    # Get config
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # Render appropriate stage
    if st.session_state.stage == "input":
        render_input_stage(graph, config)

    elif st.session_state.stage == "pending":
        render_approval_stage(graph, config)

    elif st.session_state.stage == "completed":
        render_results_stage()

    else:
        st.error("Unknown stage")
        st.session_state.stage = "input"
        st.rerun()