import uuid
from datetime import datetime
from typing import Dict, Any, List
from .state import TravelPlanState

def response_aggregator_agent(state: TravelPlanState) -> Dict[str, Any]:
    """
    Response Aggregator Agent:
    Combines all agent results into a cohesive master travel plan,
    computes itemized budget breakdown, and finalizes packing and logistical advice.
    """
    request = state.get("request", {})
    destination = request.get("destination", "Tokyo").title()
    origin = request.get("origin", "New York").title()
    duration = request.get("duration_days", 5)
    travelers = request.get("travelers", 2)
    budget_tier = request.get("budget", "Moderate")
    travel_style = request.get("travel_style", "Cultural Exploration")

    dest_data = state.get("destination_data", {})
    itinerary_data = state.get("itinerary_data", [])
    accommodations = state.get("accommodation_data", [])
    transports = state.get("transport_data", [])
    logs = list(state.get("agent_logs", []))

    # Calculate Budget Totals
    # 1. Transport cost
    flight_cost = sum(t.get("estimated_price", 0.0) for t in transports if t.get("category") == "Flight")
    if flight_cost == 0:
        flight_cost = 750.0 * travelers

    local_transit_cost = sum(t.get("estimated_price", 0.0) for t in transports if t.get("category") != "Flight")
    if local_transit_cost == 0:
        local_transit_cost = 40.0 * travelers

    transport_total = round(flight_cost + local_transit_cost, 2)

    # 2. Accommodation cost
    primary_hotel = accommodations[0] if accommodations else {}
    hotel_total = primary_hotel.get("total_price", 140.0 * duration)

    # 3. Activities & Attractions
    activities_total = round(sum(d.get("daily_cost_estimate", 60.0) * 0.45 for d in itinerary_data) * travelers, 2)
    if activities_total == 0:
        activities_total = round(35.0 * duration * travelers, 2)

    # 4. Dining & Food
    dining_total = round(sum(d.get("daily_cost_estimate", 60.0) * 0.55 for d in itinerary_data) * travelers, 2)
    if dining_total == 0:
        dining_total = round(50.0 * duration * travelers, 2)

    # 5. Buffer / Miscellaneous
    misc_buffer = round((transport_total + hotel_total + activities_total + dining_total) * 0.08, 2)

    total_cost = round(transport_total + hotel_total + activities_total + dining_total + misc_buffer, 2)
    cost_per_person = round(total_cost / max(travelers, 1), 2)

    budget_breakdown = {
        "currency": "USD",
        "transport": transport_total,
        "accommodation": round(hotel_total, 2),
        "activities_and_attractions": activities_total,
        "food_and_dining": dining_total,
        "miscellaneous_and_buffer": misc_buffer,
        "total_estimated": total_cost,
        "cost_per_person": cost_per_person
    }

    # Packing checklist tailored to weather and destination
    weather = dest_data.get("weather", {})
    weather_cond = weather.get("condition", "").lower()
    
    packing_checklist = [
        "Passport valid for at least 6 months + printed/digital visas & flight tickets",
        "Multi-country universal power plug adapter and portable high-capacity power bank",
        "Comfortable broken-in walking shoes / sneakers (10,000+ daily steps expected)",
        "Weather-appropriate clothing layers: breathable t-shirts, light sweater, and evening outerwear",
        "Credit cards with zero foreign transaction fees + small reserve of local currency cash",
        "Personal medications, compact first-aid kit, and electrolyte packs",
        "Offline maps downloaded on smartphone (e.g., Google Maps / Maps.me)"
    ]
    if "rain" in weather_cond or "shower" in weather_cond:
        packing_checklist.append("Compact travel umbrella and waterproof jacket or shoes")
    if "sunny" in weather_cond or "warm" in weather_cond:
        packing_checklist.append("High SPF sunscreen, polarized sunglasses, and UV protection sun hat")

    plan_id = state.get("session_id") or f"plan_{uuid.uuid4().hex[:8]}"

    executive_summary = (
        f"Welcome to your custom-crafted {duration}-day journey to {destination}! "
        f"Designed for {travelers} traveler(s) embracing a '{travel_style}' style with a {budget_tier.lower()} budget. "
        f"This itinerary pairs iconic highlights such as {', '.join(dest_data.get('top_attractions', [])[:3])} "
        f"with hand-picked local culinary moments, premium lodging at {primary_hotel.get('name', 'selected hotel')}, "
        f"and smooth transit connections from {origin}."
    )

    final_plan_data = {
        "id": plan_id,
        "title": f"{duration}-Day {destination} {travel_style} Expedition",
        "destination": destination,
        "origin": origin,
        "duration_days": duration,
        "budget_tier": budget_tier,
        "travelers": travelers,
        "travel_style": travel_style,
        "executive_summary": executive_summary,
        "weather": weather,
        "destination_insights": {
            "country": dest_data.get("country", "Global"),
            "currency": dest_data.get("currency", "USD"),
            "language": dest_data.get("language", "English"),
            "visa_requirements": dest_data.get("visa_requirements", "Standard"),
            "safety_rating": dest_data.get("safety_rating", "9.0/10"),
            "cultural_tips": dest_data.get("cultural_tips", []),
            "top_attractions": dest_data.get("top_attractions", [])
        },
        "itinerary": itinerary_data,
        "accommodations": accommodations,
        "transport": transports,
        "budget_breakdown": budget_breakdown,
        "packing_checklist": packing_checklist,
        "agent_reasoning_summary": (
            f"Orchestrated across 5 domain-specific agents under Supervisor supervision: "
            f"Destination Research, Itinerary Planning, Accommodation Curation, Transport Routing, and Synthesis."
        )
    }

    thought = (
        f"Successfully consolidated findings from all worker agents into unified dossier '{final_plan_data['title']}'. "
        f"Calculated complete trip budget breakdown (${total_cost:,.2f} total, ${cost_per_person:,.2f} / person). "
        f"Generated customized packing checklist and finalized executive master plan."
    )

    logs.append({
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "agent": "Response Aggregator Agent",
        "action": "plan_finalized",
        "thought": thought,
        "next_step": "completed"
    })

    return {
        "final_plan": final_plan_data,
        "current_agent": "Response Aggregator Agent",
        "agent_logs": logs,
        "status": "completed"
    }
