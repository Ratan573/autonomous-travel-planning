# Travel Planning Multi-Agent System with LangGraph 🌍✈️

An intelligent, autonomous travel planning multi-agent system built using **LangGraph**, **FastAPI**, and a **Modern Web UI**. The system coordinates a hierarchical network of specialized AI agents to generate personalized, day-by-day travel itineraries with real-time streaming, interactive maps, weather forecasts, hotel curation, and budget breakdowns.

---

## 🏗️ Architecture Overview

The multi-agent workflow is orchestrated via **LangGraph StateGraph** following a supervisor-worker pattern:

1. **🧠 Supervisor Agent**:
   - Analyzes user natural language requirements (destination, duration, budget, style, party size).
   - Dynamically sequences and dispatches tasks to worker agents.
   - Evaluates intermediate state and coordinates the multi-agent pipeline.
2. **🔍 Destination Research Agent**:
   - Fetches live weather forecasts via Open-Meteo API / OpenWeatherMap.
   - Evaluates geographic coordinates via OpenStreetMap Nominatim.
   - Researches cultural etiquette, visa requirements, safety ratings, and top landmarks.
3. **🗓️ Itinerary Planning Agent**:
   - Constructs an optimized day-wise schedule (Morning, Afternoon, Evening).
   - Minimizes commute times through geographic clustering.
   - Pairs activities with curated local lunch and dinner spots.
4. **🏨 Accommodation Agent**:
   - Searches and filters stays (Boutique, Hotels, Resorts) matching the budget tier (Budget, Moderate, Luxury).
   - Highlights guest ratings, amenities, and proximity to sights.
5. **✈️ Transport Booking Agent**:
   - Evaluates flight schedules and pricing between origin and destination.
   - Curates airport express transfers and local transit passes.
6. **💬 Response Aggregator Agent**:
   - Consolidates all domain findings into a unified travel master plan.
   - Calculates itemized budget breakdowns (Transit, Stays, Activities, Meals, Buffer).
   - Generates weather-adapted packing checklists and executive summaries.

---

## 🚀 Key Features

- **Real-Time WebSocket Streaming**: Watch agents plan in real-time with an interactive live pipeline and thought log terminal.
- **Interactive Leaflet Maps**: Automatically plots attractions, hotels, and daily route markers on an interactive map.
- **Zero-Key Autonomous Mode**: Works immediately out of the box with built-in simulation domain logic and live free APIs (Open-Meteo, OpenStreetMap).
- **Plug-and-Play LLM Providers**: Enter your OpenAI, Google Gemini, or Groq API key in Settings for full LLM-driven generation.
- **LangSmith Tracing**: Instant observability and tracing support.
- **Persistent SQLite Storage**: Save, browse, export (PDF / Markdown), and delete past itineraries.
- **Glassmorphic Modern Design**: Sleek dark theme, responsive cards, micro-animations, and quick destination presets.

---

## 📂 Project Directory Structure

```
AGENT/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py             # Environment & provider settings
│   │   ├── database.py           # SQLite persistence for travel plans
│   │   ├── main.py               # FastAPI REST + WebSocket application
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── travel_models.py  # Pydantic schemas (Request, Response, State)
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── weather_tool.py   # Live Open-Meteo weather API
│   │   │   ├── places_tool.py    # OpenStreetMap geocoding & attractions
│   │   │   ├── flight_tool.py    # Flight & transit search engine
│   │   │   └── hotel_tool.py     # Hotel & accommodation search engine
│   │   └── agents/
│   │       ├── __init__.py
│   │       ├── state.py          # LangGraph State definition
│   │       ├── supervisor.py     # Supervisor Agent
│   │       ├── destination.py    # Destination Research Agent
│   │       ├── itinerary.py      # Itinerary Planning Agent
│   │       ├── accommodation.py  # Accommodation Agent
│   │       ├── transport.py      # Transport Booking Agent
│   │       ├── aggregator.py     # Response Aggregator Agent
│   │       └── graph.py          # StateGraph assembly & streaming runner
├── frontend/
│   ├── index.html                # Main single-page web UI
│   ├── css/
│   │   └── styles.css            # Glassmorphism styling & animations
│   └── js/
│       ├── app.js                # UI logic, plan rendering & tabs
│       ├── websocket.js          # Real-time WebSocket agent stream
│       └── map.js                # Leaflet interactive map integration
├── .env.example                  # Environment configuration template
├── requirements.txt              # Python dependencies
├── run.bat                       # 1-click Windows launcher
└── README.md                     # Documentation
```

---

## ⚡ Quick Start

### 1. Launch with One Click (Windows)
Double-click `run.bat` in this folder, or execute in terminal:
```bash
.\run.bat
```

### 2. Manual Startup
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Launch FastAPI Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📡 API Endpoints

- `GET /api/health`: Health status, active provider, database connection.
- `POST /api/plan`: Run multi-agent workflow and generate a travel plan.
- `GET /api/plans`: List all saved itineraries.
- `GET /api/plans/{id}`: Fetch complete details of a specific plan.
- `DELETE /api/plans/{id}`: Delete an itinerary.
- `GET /api/config`: View active settings and keys status.
- `POST /api/config`: Update API keys dynamically.
- `WS /ws/{session_id}`: Live WebSocket stream for real-time agent execution events.

---

## 🔑 Optional API Keys & Observability

To use real cloud LLMs or tracing, you can either:
1. Add them to the `.env` file:
   ```env
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=AIza...
   GROQ_API_KEY=gsk_...
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_...
   ```
2. Or click the **Settings** gear icon in the web UI at runtime.
