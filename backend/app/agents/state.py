from typing import TypedDict, List, Dict, Any, Optional

class TravelPlanState(TypedDict, total=False):
    session_id: str
    request: Dict[str, Any] # user inputs: destination, origin, dates, budget, etc.
    supervisor_plan: Dict[str, Any]
    destination_data: Dict[str, Any]
    itinerary_data: List[Dict[str, Any]]
    accommodation_data: List[Dict[str, Any]]
    transport_data: List[Dict[str, Any]]
    final_plan: Dict[str, Any]
    agent_logs: List[Dict[str, Any]]
    current_agent: str
    next_agent: str
    iteration: int
    status: str
    error: Optional[str]
