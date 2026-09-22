import asyncio
from typing import Dict, Any, AsyncGenerator
from langgraph.graph import StateGraph, END
from .state import TravelPlanState
from .supervisor import supervisor_agent
from .destination import destination_research_agent
from .itinerary import itinerary_planning_agent
from .accommodation import accommodation_agent
from .transport import transport_agent
from .aggregator import response_aggregator_agent

def supervisor_router(state: TravelPlanState) -> str:
    """Routes the workflow based on the Supervisor's decision."""
    next_agent = state.get("next_agent", "destination_researcher")
    if next_agent == "destination_researcher":
        return "destination_researcher"
    elif next_agent == "itinerary_planner":
        return "itinerary_planner"
    elif next_agent == "accommodation_specialist":
        return "accommodation_specialist"
    elif next_agent == "transport_specialist":
        return "transport_specialist"
    elif next_agent == "response_aggregator":
        return "response_aggregator"
    return "response_aggregator"

def build_travel_graph():
    """
    Constructs and compiles the LangGraph Multi-Agent Workflow:
    Supervisor <---> [Destination, Itinerary, Accommodation, Transport] ---> Aggregator -> END
    """
    workflow = StateGraph(TravelPlanState)

    # Register agent nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("destination_researcher", destination_research_agent)
    workflow.add_node("itinerary_planner", itinerary_planning_agent)
    workflow.add_node("accommodation_specialist", accommodation_agent)
    workflow.add_node("transport_specialist", transport_agent)
    workflow.add_node("response_aggregator", response_aggregator_agent)

    # Entry point
    workflow.set_entry_point("supervisor")

    # Conditional branching from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "destination_researcher": "destination_researcher",
            "itinerary_planner": "itinerary_planner",
            "accommodation_specialist": "accommodation_specialist",
            "transport_specialist": "transport_specialist",
            "response_aggregator": "response_aggregator"
        }
    )

    # Worker agents return results back to Supervisor to assess state & decide next task
    workflow.add_edge("destination_researcher", "supervisor")
    workflow.add_edge("itinerary_planner", "supervisor")
    workflow.add_edge("accommodation_specialist", "supervisor")
    workflow.add_edge("transport_specialist", "supervisor")

    # Final aggregator finishes workflow
    workflow.add_edge("response_aggregator", END)

    return workflow.compile()

# Pre-compiled graph instance
travel_agent_app = build_travel_graph()

async def run_travel_agent_stream(request_dict: Dict[str, Any], session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes the multi-agent graph step by step and yields state transitions and agent logs
    for real-time WebSocket streaming to the frontend.
    """
    initial_state: TravelPlanState = {
        "session_id": session_id,
        "request": request_dict,
        "agent_logs": [],
        "iteration": 0,
        "status": "starting"
    }

    current_state = initial_state
    sent_logs_count = 0

    # Emit initial start event
    yield {
        "type": "agent_start",
        "agent": "System",
        "message": "Initializing Travel Planning Multi-Agent Graph...",
        "timestamp": ""
    }

    # Execute graph nodes
    for event in travel_agent_app.stream(initial_state, stream_mode="updates"):
        for node_name, node_output in event.items():
            # Update working state
            current_state.update(node_output)

            # Check for new logs
            logs = current_state.get("agent_logs", [])
            while sent_logs_count < len(logs):
                log_entry = logs[sent_logs_count]
                sent_logs_count += 1
                yield {
                    "type": "agent_log",
                    "agent": log_entry.get("agent", node_name),
                    "action": log_entry.get("action", "step"),
                    "thought": log_entry.get("thought", ""),
                    "timestamp": log_entry.get("timestamp", ""),
                    "next_step": log_entry.get("next_step", "")
                }
                # Brief aesthetic breathing interval for realistic live multi-agent streaming
                await asyncio.sleep(0.4)

    # Emit completion event with full final plan
    final_plan = current_state.get("final_plan")
    yield {
        "type": "workflow_complete",
        "agent": "Response Aggregator Agent",
        "message": "Master Travel Plan generated successfully!",
        "final_plan": final_plan
    }
