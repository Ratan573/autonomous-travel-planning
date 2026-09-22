from datetime import datetime
from typing import Dict, Any
from .state import TravelPlanState
from ..config import settings

def supervisor_agent(state: TravelPlanState) -> Dict[str, Any]:
    """
    Supervisor Agent: Analyzes user travel request, determines necessary tasks,
    coordinates workflow and routes tasks to specialized worker agents.
    """
    request = state.get("request", {})
    destination = request.get("destination", "Paris")
    origin = request.get("origin", "New York")
    duration = request.get("duration_days", 5)
    budget = request.get("budget", "Moderate")
    travelers = request.get("travelers", 2)
    style = request.get("travel_style", "Culture & Sightseeing")

    current_agent = "Supervisor Agent"
    logs = list(state.get("agent_logs", []))

    # Check which phases are already completed
    has_dest = bool(state.get("destination_data"))
    has_itin = bool(state.get("itinerary_data"))
    has_acc = bool(state.get("accommodation_data"))
    has_trans = bool(state.get("transport_data"))

    if not has_dest:
        next_agent = "destination_researcher"
        thought = (
            f"Parsed travel intent: {duration} days in {destination} departing from {origin} "
            f"for {travelers} traveler(s) with '{budget}' budget and '{style}' style. "
            f"Phase 1: Dispatching Destination Research Agent to investigate geography, weather, "
            f"cultural etiquette, and key landmarks."
        )
    elif not has_itin:
        next_agent = "itinerary_planner"
        thought = (
            f"Destination research received. Phase 2: Dispatching Itinerary Planning Agent "
            f"to construct an optimized {duration}-day schedule with balanced morning, afternoon, "
            f"and evening activities plus dining recommendations."
        )
    elif not has_acc:
        next_agent = "accommodation_specialist"
        thought = (
            f"Itinerary structured. Phase 3: Dispatching Accommodation Agent to find prime hotels "
            f"and suites matching {budget} tier near key attraction clusters."
        )
    elif not has_trans:
        next_agent = "transport_specialist"
        thought = (
            f"Accommodations selected. Phase 4: Dispatching Transport Booking Agent to evaluate "
            f"flights/trains between {origin} and {destination}, along with airport transit and local passes."
        )
    else:
        next_agent = "response_aggregator"
        thought = (
            f"All specialized domain research complete! Phase 5: Routing to Response Aggregator Agent "
            f"to compile the unified master travel dossier, calculate full budget breakdown, and finalize packing checklist."
        )

    log_entry = {
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "agent": current_agent,
        "action": "orchestrate",
        "thought": thought,
        "next_step": next_agent
    }
    logs.append(log_entry)

    supervisor_plan = {
        "target_destination": destination,
        "origin": origin,
        "duration_days": duration,
        "budget_tier": budget,
        "travelers": travelers,
        "travel_style": style,
        "current_dispatch": next_agent,
        "status": "in_progress"
    }

    return {
        "supervisor_plan": supervisor_plan,
        "current_agent": current_agent,
        "next_agent": next_agent,
        "agent_logs": logs,
        "iteration": state.get("iteration", 0) + 1
    }
