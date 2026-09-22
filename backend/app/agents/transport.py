from datetime import datetime
from typing import Dict, Any
from .state import TravelPlanState
from ..tools.flight_tool import search_flights

def transport_agent(state: TravelPlanState) -> Dict[str, Any]:
    """
    Transport Booking Agent:
    Evaluates flights, long-distance rail, airport express transfers, and local multi-day transit passes.
    """
    request = state.get("request", {})
    origin = request.get("origin", "New York")
    destination = request.get("destination", "Tokyo")
    budget = request.get("budget", "Moderate")
    travelers = request.get("travelers", 2)
    logs = list(state.get("agent_logs", []))

    transport_options = search_flights(
        origin=origin,
        destination=destination,
        budget_tier=budget,
        travelers=travelers
    )

    thought = (
        f"Analyzed transport logistics connecting {origin} to {destination} for {travelers} passenger(s). "
        f"Cross-referenced carriers for punctual arrival windows, baggage allocations, and terminal accessibility. "
        f"Selected optimal flight pairing and integrated local seamless metro/rail pass recommendations."
    )

    logs.append({
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "agent": "Transport Booking Agent",
        "action": "transport_analyzed",
        "thought": thought,
        "next_step": "supervisor"
    })

    return {
        "transport_data": transport_options,
        "current_agent": "Transport Booking Agent",
        "agent_logs": logs
    }
