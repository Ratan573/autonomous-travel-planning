from typing import List, Dict, Any

def search_flights(origin: str, destination: str, budget_tier: str = "Moderate", travelers: int = 1) -> List[Dict[str, Any]]:
    """
    Finds flight and primary transit options based on route and budget preferences.
    """
    origin = origin.strip() if origin else "Major International Hub"
    dest = destination.strip()
    tier = budget_tier.lower()

    if "budget" in tier:
        economy_price = 420.0
        return [
            {
                "category": "Flight",
                "title": f"Value Economy ({origin} ➔ {dest})",
                "provider": "TransGlobal Budget Air / SkyWings",
                "route": f"{origin} (Main) ➔ 1 Stop (2h layover) ➔ {dest} International",
                "duration": "14h 25m",
                "estimated_price": round(economy_price * travelers, 2),
                "frequency_or_schedule": "Daily departures at 08:30 & 21:15",
                "tips": "Carry-on included (10kg). Checked bag $45 extra. Book 4-6 weeks ahead for lowest fares."
            },
            {
                "category": "Airport Express Transit",
                "title": f"Express Rail / Metro Shuttle ({dest})",
                "provider": "City Rapid Airport Express",
                "route": f"{dest} International Airport ➔ City Center Terminal",
                "duration": "35m",
                "estimated_price": round(15.0 * travelers, 2),
                "frequency_or_schedule": "Departs every 10 minutes",
                "tips": "Convenient tap-to-pay via contactless card. Direct transfer with zero traffic delays."
            }
        ]
    elif "luxury" in tier:
        lux_price = 2450.0
        return [
            {
                "category": "Flight",
                "title": f"Flagship Business / First Class ({origin} ➔ {dest})",
                "provider": "Emirates / Singapore Airlines / ANA Premium",
                "route": f"{origin} ➔ Non-stop Direct ➔ {dest} International",
                "duration": "11h 10m",
                "estimated_price": round(lux_price * travelers, 2),
                "frequency_or_schedule": "Direct daily flight departing 18:40",
                "tips": "Lie-flat suite, lounge access, gourmet multi-course dining, 64kg luggage allowance & fast-track customs."
            },
            {
                "category": "Private Transfer",
                "title": "Chauffeured Executive Airport Transfer",
                "provider": "Blacklane / Elite Chauffeur Services",
                "route": f"{dest} Arrivals Gate ➔ Hotel Lobby",
                "duration": "40m",
                "estimated_price": round(110.0, 2),
                "frequency_or_schedule": "On-demand meet & greet with luggage assistance",
                "tips": "Includes Mercedes-Benz S-Class or E-Class, complimentary bottled water, Wi-Fi, and 60m flight delay grace period."
            }
        ]
    else: # Moderate / Standard
        mod_price = 780.0
        return [
            {
                "category": "Flight",
                "title": f"Standard Non-stop or 1-Stop Economy ({origin} ➔ {dest})",
                "provider": "Delta / United / Lufthansa / Japan Airlines",
                "route": f"{origin} International ➔ Direct or 1-Short Layover ➔ {dest}",
                "duration": "12h 45m",
                "estimated_price": round(mod_price * travelers, 2),
                "frequency_or_schedule": "Multiple daily departures (Morning & Evening)",
                "tips": "1 free checked bag included per passenger, seat selection, in-flight entertainment and hot meal included."
            },
            {
                "category": "Airport Transfer & Local Pass",
                "title": "Airport Express Train + Unlimited Multi-Day Transit Pass",
                "provider": "Regional Transport Authority",
                "route": f"Airport Terminal ➔ Central Station & all city subway lines",
                "duration": "30m to center",
                "estimated_price": round(42.0 * travelers, 2),
                "frequency_or_schedule": "Valid for entire trip duration",
                "tips": "Unlocks unlimited rides on subways, trams, and city buses throughout your stay."
            }
        ]
