from datetime import datetime
from typing import Dict, Any
from .state import TravelPlanState
from ..tools.hotel_tool import search_accommodations

def accommodation_agent(state: TravelPlanState) -> Dict[str, Any]:
    """
    Accommodation Agent:
    Finds hotel, resort, and lodging options matching the traveler's budget, party size,
    and proximity to planned itinerary sights.
    """
    request = state.get("request", {})
    destination = request.get("destination", "Tokyo")
    duration = request.get("duration_days", 5)
    budget = request.get("budget", "Moderate")
    travelers = request.get("travelers", 2)
    logs = list(state.get("agent_logs", []))

    accommodations = search_accommodations(
        destination=destination,
        duration_days=duration,
        budget_tier=budget,
        travelers=travelers
    )

    thought = (
        f"Surveyed lodging availability in {destination} for {duration} nights ({travelers} travelers, {budget} tier). "
        f"Filtered top contenders based on guest rating (>4.3/5), walkable transit links, and soundproofing. "
        f"Selected {len(accommodations)} prime properties including '{accommodations[0]['name']}' ({accommodations[0]['badge']})."
    )

    logs.append({
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "agent": "Accommodation Agent",
        "action": "hotels_curated",
        "thought": thought,
        "next_step": "supervisor"
    })

    return {
        "accommodation_data": accommodations,
        "current_agent": "Accommodation Agent",
        "agent_logs": logs
    }
