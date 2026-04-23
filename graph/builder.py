"""
Graph construction and compilation.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import State
from graph.nodes import make_plan, approval_node, execute_node


def build_graph():
    """
    Build and compile the LangGraph workflow.
    
    Returns:
        Compiled graph with memory checkpointing
    """
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("plan", make_plan)
    builder.add_node("approve", approval_node)
    builder.add_node("execute", execute_node)

    # Add edges
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "approve")
    builder.add_edge("approve", "execute")
    builder.add_edge("execute", END)

    # Compile with memory
    return builder.compile(checkpointer=MemorySaver())