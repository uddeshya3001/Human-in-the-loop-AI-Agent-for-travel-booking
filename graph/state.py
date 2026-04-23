"""
State definition for the LangGraph workflow.
"""

from typing import TypedDict, Dict, Any, Optional


class State(TypedDict):
    """Graph state containing user request, plan, approval, and execution results."""
    user_request: str
    plan: Optional[Dict[str, Any]]
    approval: Optional[Dict[str, Any]]
    execution: Optional[Dict[str, Any]]