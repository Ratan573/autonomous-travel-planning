from datetime import datetime
from typing import Dict, Any
from .state import TravelPlanState
from ..tools.places_tool import geocode_city, get_destination_places
from ..tools.weather_tool import get_weather_forecast

def destination_research_agent(state: TravelPlanState) -> Dict[str, Any]:
    """
    Destination Research Agent:
    Finds geographical, cultural, visa, safety, attractions, and real-time weather information.
    """
    request = state.get("request", {})
    destination = request.get("destination", "Tokyo")
    interests = request.get("interests", ["Sightseeing", "Food"])
    logs = list(state.get("agent_logs", []))

    # 1. Geocode location & fetch top attractions
    lat, lon, full_name = geocode_city(destination)
    places = get_destination_places(destination, interests)

    # 2. Query weather
    weather = get_weather_forecast(destination, lat, lon)

    # 3. Country / Cultural Intelligence based on destination
    dest_lower = destination.lower()
    if "japan" in dest_lower or "tokyo" in dest_lower or "kyoto" in dest_lower or "osaka" in dest_lower:
        country = "Japan"
        currency = "Japanese Yen (JPY / ¥)"
        language = "Japanese (English signage widespread in transit)"
        visa = "Visa-free for 90 days for US, EU, UK, Canada, Australia (Visit Japan Web pre-clearance recommended)"
        safety = "Exceptional (Ranked among safest worldwide, 9.8/10)"
        cultural_tips = [
            "No tipping culture; exceptional hospitality (Omotenashi) is standard.",
            "Always carry a small coin pouch and small trash bag, as public bins are rare.",
            "Stand on the left side on escalators in Tokyo (right side in Osaka).",
            "Keep voice volume down on trains and subways."
        ]
    elif "france" in dest_lower or "paris" in dest_lower:
        country = "France"
        currency = "Euro (EUR / €)"
        language = "French (English widely spoken in tourist zones)"
        visa = "Schengen Visa or ETIAS authorization for visa-exempt nationalities"
        safety = "High (9.0/10; practice standard awareness against pickpockets around Eiffel Tower & Metro)"
        cultural_tips = [
            "Always greet shopkeepers with 'Bonjour Madame/Monsieur' upon entering.",
            "Service charge (service compris) is included by law; rounding up 1-2€ is appreciated.",
            "Dinner typically starts around 19:30 or 20:00."
        ]
    elif "italy" in dest_lower or "rome" in dest_lower:
        country = "Italy"
        currency = "Euro (EUR / €)"
        language = "Italian (English spoken in tourism spots)"
        visa = "Schengen Area rules apply"
        safety = "High (8.8/10; maintain vigilance at crowded Termini Station and Colosseum)"
        cultural_tips = [
            "Cappuccino is traditionally consumed in the morning only, not after dinner.",
            "Cover shoulders and knees when visiting basilicas and churches (e.g., St. Peter's).",
            "Validate paper train and bus tickets in machine before boarding."
        ]
    else:
        country = f"{destination.title()} Region"
        currency = "Local Currency / USD / EUR accepted"
        language = "Local Official Language + English"
        visa = "Standard tourist visa or e-visa depending on traveler passport; check embassy portal"
        safety = "Good / High (8.5/10; exercise standard travel caution)"
        cultural_tips = [
            "Respect local religious customs and dress codes at heritage sites.",
            "Download offline maps and translation apps for seamless navigation.",
            "Keep emergency contact numbers and photocopy of passport handy."
        ]

    top_attraction_names = [p["name"] for p in places[:6]]

    destination_data = {
        "destination_name": destination.title(),
        "country": country,
        "coordinates": {"lat": lat, "lon": lon},
        "display_name": full_name,
        "currency": currency,
        "language": language,
        "visa_requirements": visa,
        "safety_rating": safety,
        "cultural_tips": cultural_tips,
        "top_attractions": top_attraction_names,
        "places_catalog": places,
        "weather": weather
    }

    thought = (
        f"Conducted multi-factor destination audit for {destination}. "
        f"Geolocated at ({lat:.4f}, {lon:.4f}). Gathered live weather ({weather['temperature_range']}, {weather['condition']}) "
        f"and indexed {len(places)} premium points of interest matching user interests: {', '.join(interests)}."
    )

    logs.append({
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "agent": "Destination Research Agent",
        "action": "research_completed",
        "thought": thought,
        "next_step": "supervisor"
    })

    return {
        "destination_data": destination_data,
        "current_agent": "Destination Research Agent",
        "agent_logs": logs
    }
