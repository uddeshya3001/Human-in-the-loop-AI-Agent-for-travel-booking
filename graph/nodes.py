"""
Node functions for the LangGraph workflow.
"""

import streamlit as st
from langgraph.types import interrupt
from pydantic import ValidationError

from graph.state import State
from models.schemas import TravelPlan
from tools import TOOLS
from utils.llm import call_llm, parse_json_response

from database.db import get_db
from database.operations import save_plan, update_plan_status, save_execution_result

def make_plan(state: State) -> dict:
    """
    Generate a travel plan using LLM and save to database.
    """
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
            }},
            {{
                "name": "search_cars",
                "args": {{
                    "city": "string",
                    "pickup_date": "YYYY-MM-DD",
                    "return_date": "YYYY-MM-DD",
                    "budget_usd": integer,
                    "days": integer
                }}
            }},
            {{
                "name": "search_activities",
                "args": {{
                    "city": "string",
                    "days": integer,
                    "interests": "string or list",
                    "budget_usd": integer
                }}
            }}
        ]
    }}

    User request:
    {user_request}
    
    Important: Distribute the budget reasonably across flights (40-50%), hotels (25-30%), cars (10-15%), and activities (10-20%).
    """

    try:
        text = call_llm(prompt)
        plan_json = parse_json_response(text)
        validated = TravelPlan.model_validate(plan_json)
        plan_dict = validated.model_dump()
        
        # Save to database
        try:
            import streamlit as st
            db = get_db()
            session_id = st.session_state.get("user_session_id")
            thread_id = st.session_state.get("thread_id")
            
            if session_id and thread_id:
                save_plan(
                    db=db,
                    session_id=session_id,
                    thread_id=thread_id,
                    plan_data=plan_dict,
                    user_request=user_request,
                    status="draft"
                )
            db.close()
        except Exception as e:
            st.warning(f"Could not save to database: {e}")
        
        return {"plan": plan_dict}
    except (ValidationError, Exception) as e:
        st.error(f"Plan generation failed: {e}")
        return state

def approval_node(state: State) -> dict:
    """
    Interrupt for human approval of the plan.
    
    Args:
        state: Current graph state
    
    Returns:
        Updated state with approval decision
    """
    plan = state.get("plan")
    if not plan:
        return state
    
    decision = interrupt({"plan": plan})
    return {"approval": decision}

def execute_node(state: State) -> dict:
    """
    Execute approved tool calls and save results to database.
    """
    approval = state.get("approval")
    plan = state.get("plan")

    if not approval:
        return state

    if not approval.get("approved"):
        # Save rejection status
        try:
            import streamlit as st
            db = get_db()
            thread_id = st.session_state.get("thread_id")
            if thread_id:
                update_plan_status(db, thread_id, "rejected")
            db.close()
        except:
            pass
        
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

    execution_data = {"status": "executed", "results": results}
    
    # Save to database
    try:
        import streamlit as st
        db = get_db()
        thread_id = st.session_state.get("thread_id")
        if thread_id:
            update_plan_status(db, thread_id, "executed")
            save_execution_result(
                db=db,
                thread_id=thread_id,
                status="executed",
                results_data=execution_data
            )
        db.close()
    except Exception as e:
        st.warning(f"Could not save execution results: {e}")

    return {"execution": execution_data}