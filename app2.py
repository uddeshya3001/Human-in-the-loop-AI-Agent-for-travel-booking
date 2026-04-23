import os
import json
import uuid
from typing import TypedDict, Dict, Any, List, Optional

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver


# ================== ENV ==================
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found in .env file")
    st.stop()

client = OpenAI()


# ================== TOOLS ==================
def tool_search_flights(origin, destination, depart_date, return_date, budget_usd):
    options = [
        {"airline": "SkyJet", "route": f"{origin} -> {destination}", "price_usd": int(budget_usd * 0.55)},
        {"airline": "AeroBlue", "route": f"{origin} -> {destination}", "price_usd": int(budget_usd * 0.70)},
        {"airline": "Nimbus Air", "route": f"{origin} -> {destination}", "price_usd": int(budget_usd * 0.62)},
    ]
    return {
        "tool": "search_flights",
        "results": sorted(options, key=lambda x: x["price_usd"])[:2]
    }


def tool_search_hotels(city, nights, budget_usd):
    base = max(60, int(budget_usd / max(nights, 1)))
    picks = [
        {"name": "Central Boutique", "nightly_usd": int(base * 0.9)},
        {"name": "Riverside Stay", "nightly_usd": int(base * 0.8)},
        {"name": "Modern Loft Hotel", "nightly_usd": int(base * 1.1)},
    ]
    return {
        "tool": "search_hotels",
        "results": sorted(picks, key=lambda x: x["nightly_usd"])[:2]
    }


# Tool Registry
TOOLS = {
    "search_flights": tool_search_flights,
    "search_hotels": tool_search_hotels
}


# ================== SCHEMA ==================
class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]


class TravelPlan(BaseModel):
    trip_title: str
    origin: str
    destination: str
    depart_date: str
    return_date: str
    budget_usd: int
    tool_calls: List[ToolCall]


# ================== STATE ==================
class State(TypedDict):
    user_request: str
    plan: Optional[Dict[str, Any]]
    approval: Optional[Dict[str, Any]]
    execution: Optional[Dict[str, Any]]


# ================== LLM NODE ==================
def make_plan(state: State):

    if state.get("plan"):
        return state

    user_request = state.get("user_request")
    if not user_request:
        return state

    prompt = f"""
    You are a travel planner.

    Return ONLY valid JSON.
    Do not include explanations.
    Do not include markdown.
    Do not include backticks.

    Required JSON structure:
    {{
        "trip_title": "string",
        "origin": "string",
        "destination": "string",
        "depart_date": "YYYY-MM-DD",
        "return_date": "YYYY-MM-DD",
        "budget_usd": integer,
        "tool_calls": [
            {{
                "name": "search_flights",
                "args": {{
                    "origin": "string",
                    "destination": "string",
                    "depart_date": "YYYY-MM-DD",
                    "return_date": "YYYY-MM-DD",
                    "budget_usd": integer
                }}
            }},
            {{
                "name": "search_hotels",
                "args": {{
                    "city": "string",
                    "nights": integer,
                    "budget_usd": integer
                }}
            }}
        ]
    }}

    User request:
    {user_request}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        st.error(f"LLM API Error: {e}")
        return state

    text = response.choices[0].message.content.strip()

    try:
        # Remove markdown if present
        if text.startswith("```"):
            lines = text.split("```")
            if len(lines) >= 2:
                text = lines[1].replace("json", "").strip()

        plan_json = json.loads(text)

        validated = TravelPlan.model_validate(plan_json)
        return {"plan": validated.model_dump()}

    except (json.JSONDecodeError, ValidationError) as e:
        st.error(f"Plan validation failed: {e}")
        st.error(f"Raw response: {text}")
        return state


# ================== APPROVAL NODE ==================
def approval_node(state: State):
    plan = state.get("plan")
    if not plan:
        return state
    
    decision = interrupt({"plan": plan})
    return {"approval": decision}


# ================== EXECUTION NODE ==================
def execute_node(state: State):

    approval = state.get("approval")
    plan = state.get("plan")

    if not approval:
        return state

    if not approval.get("approved"):
        return {"execution": {"status": "rejected"}}

    plan = approval.get("edited_plan") or plan

    if not plan:
        return {"execution": {"status": "error", "reason": "No plan available"}}

    if not plan.get("tool_calls"):
        return {
            "execution": {
                "status": "error",
                "reason": "No tool calls in approved plan"
            }
        }

    results = []

    for call in plan["tool_calls"]:
        name = call.get("name")
        args = call.get("args", {})

        tool_fn = TOOLS.get(name)

        if not tool_fn:
            results.append({
                "tool": name,
                "error": "Unknown tool"
            })
            continue

        try:
            result = tool_fn(**args)
            results.append(result)
        except TypeError as e:
            results.append({
                "tool": name,
                "error": f"Invalid arguments: {str(e)}"
            })
        except Exception as e:
            results.append({
                "tool": name,
                "error": f"Execution failed: {str(e)}"
            })

    return {"execution": {"status": "executed", "results": results}}


# ================== BUILD GRAPH ==================
def build_graph():
    builder = StateGraph(State)

    builder.add_node("plan", make_plan)
    builder.add_node("approve", approval_node)
    builder.add_node("execute", execute_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "approve")
    builder.add_edge("approve", "execute")
    builder.add_edge("execute", END)

    return builder.compile(checkpointer=MemorySaver())


# ================== STREAMLIT ==================
st.set_page_config(layout="wide")
st.title("Human-in-the-Loop Travel Agent")

# Initialize graph once
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

graph = st.session_state.graph

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "stage" not in st.session_state:
    st.session_state.stage = "input"  # input, pending, completed

config = {"configurable": {"thread_id": st.session_state.thread_id}}


# ================== INPUT STAGE ==================
if st.session_state.stage == "input":
    request = st.text_area("Describe your trip", key="trip_request")

    if st.button("Generate Plan"):
        if request.strip():
            # Generate new thread for new request
            st.session_state.thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            initial_state = {
                "user_request": request,
                "plan": None,
                "approval": None,
                "execution": None
            }

            with st.spinner("Generating plan..."):
                try:
                    # Stream through the graph until interrupt
                    for event in graph.stream(initial_state, config, stream_mode="values"):
                        pass
                    
                    # Get the current state after interrupt
                    current_state = graph.get_state(config)
                    
                    # Check if we hit an interrupt
                    if current_state.next:  # Graph is not finished
                        # Extract the plan from state
                        plan = current_state.values.get("plan")
                        if plan:
                            st.session_state.pending_plan = plan
                            st.session_state.stage = "pending"
                            st.rerun()
                except Exception as e:
                    st.error(f"Error generating plan: {e}")
        else:
            st.warning("Please enter a trip description")


# ================== PENDING APPROVAL STAGE ==================
elif st.session_state.stage == "pending":
    st.subheader("✅ Plan Generated - Approve or Edit")

    edited = st.text_area(
        "Edit JSON (optional)",
        value=json.dumps(st.session_state.pending_plan, indent=2),
        height=400,
        key="edited_plan"
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Approve", type="primary", use_container_width=True):
            edited_plan = st.session_state.pending_plan
            
            try:
                edited_plan = json.loads(edited)
                TravelPlan.model_validate(edited_plan)
            except (json.JSONDecodeError, ValidationError) as exc:
                st.error(f"Invalid JSON: {exc}")
                st.stop()

            resume_data = {
                "approved": True,
                "edited_plan": edited_plan
            }

            with st.spinner("Executing plan..."):
                try:
                    # Resume the graph with the decision
                    for event in graph.stream(Command(resume=resume_data), config, stream_mode="values"):
                        pass
                    
                    # Get final state
                    final_state = graph.get_state(config)
                    st.session_state.execution_result = final_state.values.get("execution")
                    st.session_state.stage = "completed"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error during execution: {e}")
    
    with col2:
        if st.button("❌ Reject", use_container_width=True):
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
                    st.error(f"Error during rejection: {e}")
    
    with col3:
        if st.button("🔄 Start Over", use_container_width=True):
            # Clear all session state
            for key in ["pending_plan", "execution_result"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.stage = "input"
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()


# ================== COMPLETED STAGE ==================
elif st.session_state.stage == "completed":
    execution = st.session_state.get("execution_result")
    
    if execution:
        if execution["status"] == "rejected":
            st.warning("❌ Plan was rejected.")
        elif execution["status"] == "executed":
            st.success("✅ Plan executed successfully!")
            st.subheader("📋 Results")
            
            for result in execution.get("results", []):
                if "error" in result:
                    st.error(f"Tool '{result.get('tool')}' error: {result['error']}")
                else:
                    with st.expander(f"🔍 {result.get('tool', 'Unknown').replace('_', ' ').title()}", expanded=True):
                        st.json(result.get("results", []))
        else:
            st.error(f"Execution status: {execution['status']}")
            if "reason" in execution:
                st.error(f"Reason: {execution['reason']}")
    else:
        st.warning("No execution result found")
    
    # Option to start new request
    if st.button("🔄 Plan Another Trip", type="primary"):
        # Clear all session state
        for key in ["pending_plan", "execution_result"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.stage = "input"
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()