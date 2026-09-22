from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TravelPlanRequest(BaseModel):
    destination: str = Field(..., description="Target destination city/country")
    origin: Optional[str] = Field("New York", description="Starting departure city")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    duration_days: int = Field(5, ge=1, le=30, description="Duration of the trip in days")
    budget: str = Field("Moderate", description="Budget tier: Budget, Moderate, Luxury")
    travelers: int = Field(2, ge=1, le=20, description="Number of travelers")
    travel_style: str = Field("Culture & Exploration", description="e.g. Adventure, Relaxing, Culture, Foodie, Romantic, Family")
    interests: List[str] = Field(default_factory=lambda: ["Sightseeing", "Local Cuisine", "Historic Landmarks"], description="Specific interests")
    special_requirements: Optional[str] = Field("", description="Special dietary, accessibility, or schedule requests")

class DayScheduleItem(BaseModel):
    time_slot: str # Morning, Afternoon, Evening, Night
    activity: str
    location: str
    description: str
    estimated_cost: float = 0.0
    lat: Optional[float] = None
    lon: Optional[float] = None

class DayItinerary(BaseModel):
    day: int
    title: str
    summary: str
    items: List[DayScheduleItem]
    lunch_suggestion: str
    dinner_suggestion: str
    daily_cost_estimate: float = 0.0

class AccommodationOption(BaseModel):
    name: str
    type: str # Hotel, Resort, Airbnb, Boutique
    price_per_night: float
    total_price: float
    rating: float
    location: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    amenities: List[str]
    description: str
    badge: Optional[str] = None # Best Value, Top Rated, Luxury Pick

class TransportOption(BaseModel):
    category: str # Flight, Train, Bus, Local Transit, Car Rental
    title: str
    provider: str
    route: str
    duration: str
    estimated_price: float
    frequency_or_schedule: str
    tips: str

class WeatherInfo(BaseModel):
    temperature_range: str
    condition: str
    humidity: Optional[str] = None
    rain_probability: Optional[str] = None
    best_time_to_visit: str
    clothing_advice: str

class DestinationInsights(BaseModel):
    country: str
    currency: str
    language: str
    visa_requirements: str
    safety_rating: str
    cultural_tips: List[str]
    top_attractions: List[str]

class BudgetBreakdown(BaseModel):
    currency: str = "USD"
    transport: float
    accommodation: float
    activities_and_attractions: float
    food_and_dining: float
    miscellaneous_and_buffer: float
    total_estimated: float
    cost_per_person: float

class TravelPlanData(BaseModel):
    id: str
    title: str
    destination: str
    origin: str
    duration_days: int
    budget_tier: str
    travelers: int
    travel_style: str
    executive_summary: str
    weather: WeatherInfo
    destination_insights: DestinationInsights
    itinerary: List[DayItinerary]
    accommodations: List[AccommodationOption]
    transport: List[TransportOption]
    budget_breakdown: BudgetBreakdown
    packing_checklist: List[str]
    agent_reasoning_summary: Optional[str] = None

class TravelPlanResponse(BaseModel):
    success: bool
    plan_id: str
    message: str
    data: Optional[TravelPlanData] = None

class AgentLogEvent(BaseModel):
    session_id: str
    agent_name: str
    status: str # started, working, completed, error
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

class ConfigUpdateRequest(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    langchain_tracing_v2: Optional[bool] = None
    langchain_api_key: Optional[str] = None
