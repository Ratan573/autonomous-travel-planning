from typing import List, Dict, Any, Optional
from .places_tool import geocode_city

def search_accommodations(destination: str, duration_days: int = 5, budget_tier: str = "Moderate", travelers: int = 2) -> List[Dict[str, Any]]:
    """
    Finds hotel and lodging options matching budget tier and duration.
    """
    lat, lon, _ = geocode_city(destination)
    base_lat = lat if lat else 48.8566
    base_lon = lon if lon else 2.3522

    tier = budget_tier.lower()
    dest_title = destination.title()

    if "budget" in tier:
        return [
            {
                "name": f"Urban Pod & Boutique Hostel {dest_title}",
                "type": "Boutique Hostel / Smart Hotel",
                "price_per_night": 55.0,
                "total_price": round(55.0 * duration_days, 2),
                "rating": 4.6,
                "location": f"Central District, 5 min walk to Metro, {dest_title}",
                "lat": base_lat + 0.003,
                "lon": base_lon - 0.002,
                "amenities": ["High-speed Wi-Fi", "Free Breakfast", "Lockers", "Rooftop Terrace", "Luggage Storage"],
                "description": "Ultra-clean modern minimalist pods and private ensuite rooms with vibrant communal coworking and social lounge.",
                "badge": "Best Value Pick"
            },
            {
                "name": f"{dest_title} Central Metro Inn",
                "type": "Budget 3-Star Hotel",
                "price_per_night": 79.0,
                "total_price": round(79.0 * duration_days, 2),
                "rating": 4.3,
                "location": f"Historic Old Town Edge, {dest_title}",
                "lat": base_lat - 0.004,
                "lon": base_lon + 0.005,
                "amenities": ["Ensuite Bathroom", "Air Conditioning", "24/7 Front Desk", "Coffee Station"],
                "description": "Solid comfortable private rooms with crisp linens, quiet soundproofing, and quick subway access.",
                "badge": "Convenient & Affordable"
            }
        ]
    elif "luxury" in tier:
        return [
            {
                "name": f"The Grand Palace & Spa {dest_title}",
                "type": "5-Star Luxury Resort",
                "price_per_night": 460.0,
                "total_price": round(460.0 * duration_days, 2),
                "rating": 4.9,
                "location": f"Exclusive Golden Mile / Waterfront Promenade, {dest_title}",
                "lat": base_lat + 0.002,
                "lon": base_lon + 0.003,
                "amenities": ["Infinity Pool", "Michelin-starred Dining", "Full-service Spa", "Private Balcony", "Butler Service"],
                "description": "Palatial luxury featuring marble suites, panoramic skyline vistas, world-class wellness spa, and bespoke concierge.",
                "badge": "Top Luxury Pick"
            },
            {
                "name": f"Royal Heritage Suites {dest_title}",
                "type": "Historic 5-Star Hotel",
                "price_per_night": 380.0,
                "total_price": round(380.0 * duration_days, 2),
                "rating": 4.8,
                "location": f"Heart of Old Cultural Quarter, {dest_title}",
                "lat": base_lat - 0.002,
                "lon": base_lon - 0.004,
                "amenities": ["Fine Dining Salon", "Champagne Bar", "Valet Parking", "Luxury Linens", "Garden Courtyard"],
                "description": "Timeless architectural elegance paired with discreet luxury, antique appointments, and garden tranquility.",
                "badge": "Heritage & Prestige"
            }
        ]
    else: # Moderate
        return [
            {
                "name": f"Grand Plaza Boutique Hotel {dest_title}",
                "type": "4-Star Boutique Hotel",
                "price_per_night": 145.0,
                "total_price": round(145.0 * duration_days, 2),
                "rating": 4.7,
                "location": f"Historic Center, walking distance to main attractions, {dest_title}",
                "lat": base_lat + 0.002,
                "lon": base_lon - 0.001,
                "amenities": ["Complimentary Artisan Breakfast", "High-speed Wi-Fi", "Fitness Center", "Cocktail Bar", "Soundproof Rooms"],
                "description": "Stylish contemporary design hotel in an unbeatable walkable location, praised for hospitable staff and comfortable king beds.",
                "badge": "Top Recommended"
            },
            {
                "name": f"{dest_title} Garden Residence & Suites",
                "type": "Premium Aparthotel",
                "price_per_night": 165.0,
                "total_price": round(165.0 * duration_days, 2),
                "rating": 4.8,
                "location": f"Cultural District near Parks and Cafes, {dest_title}",
                "lat": base_lat - 0.005,
                "lon": base_lon + 0.003,
                "amenities": ["Full Kitchenette", "Washer/Dryer", "Coffee Machine", "Balcony", "Bicycle Rental"],
                "description": "Spacious apartment-style suite offering the privacy of a home with the convenience of full hotel service and daily housekeeping.",
                "badge": "Most Comfortable"
            }
        ]
