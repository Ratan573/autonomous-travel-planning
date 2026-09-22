import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .config import settings, BASE_DIR
from .database import init_db, save_plan, get_plan, list_plans, delete_plan
from .models.travel_models import (
    TravelPlanRequest,
    TravelPlanResponse,
    ConfigUpdateRequest,
    TravelPlanData
)
from .agents.graph import travel_agent_app, run_travel_agent_stream

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Travel Planning System powered by LangGraph"
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
def on_startup():
    init_db()

# REST Endpoints
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "active_provider": settings.get_active_provider(),
        "langsmith_tracing": settings.LANGCHAIN_TRACING_V2 == "true",
        "database": "connected"
    }

@app.get("/api/config")
def get_config():
    return {
        "active_provider": settings.get_active_provider(),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY),
        "has_openweather_key": bool(settings.OPENWEATHER_API_KEY),
        "langsmith_tracing": settings.LANGCHAIN_TRACING_V2 == "true",
        "langchain_project": settings.LANGCHAIN_PROJECT
    }

@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    if req.openai_api_key is not None:
        settings.OPENAI_API_KEY = req.openai_api_key.strip()
    if req.gemini_api_key is not None:
        settings.GEMINI_API_KEY = req.gemini_api_key.strip()
    if req.groq_api_key is not None:
        settings.GROQ_API_KEY = req.groq_api_key.strip()
    if req.openweather_api_key is not None:
        settings.OPENWEATHER_API_KEY = req.openweather_api_key.strip()
    if req.langchain_tracing_v2 is not None:
        settings.LANGCHAIN_TRACING_V2 = "true" if req.langchain_tracing_v2 else "false"
    if req.langchain_api_key is not None:
        settings.LANGCHAIN_API_KEY = req.langchain_api_key.strip()

    return {"status": "updated", "active_provider": settings.get_active_provider()}

@app.post("/api/plan", response_model=TravelPlanResponse)
def create_travel_plan(request: TravelPlanRequest):
    """
    Synchronous REST endpoint to generate and persist a travel plan.
    """
    session_id = f"plan_{uuid.uuid4().hex[:10]}"
    req_dict = request.dict()

    try:
        # Execute LangGraph Multi-Agent Workflow
        result = travel_agent_app.invoke({
            "session_id": session_id,
            "request": req_dict,
            "agent_logs": [],
            "iteration": 0,
            "status": "starting"
        })

        final_plan = result.get("final_plan")
        if not final_plan:
            raise HTTPException(status_code=500, detail="Failed to synthesize final plan")

        # Save to SQLite persistence
        save_plan(
            plan_id=session_id,
            destination=final_plan.get("destination", request.destination),
            origin=final_plan.get("origin", request.origin),
            title=final_plan.get("title", f"Trip to {request.destination}"),
            duration_days=final_plan.get("duration_days", request.duration_days),
            budget_category=final_plan.get("budget_tier", request.budget),
            travelers=final_plan.get("travelers", request.travelers),
            travel_style=final_plan.get("travel_style", request.travel_style),
            plan_data=final_plan,
            request_data=req_dict
        )

        return TravelPlanResponse(
            success=True,
            plan_id=session_id,
            message="Plan generated successfully",
            data=TravelPlanData(**final_plan)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plans")
def get_saved_plans():
    """Retrieve all previously generated and saved plans."""
    return list_plans()

@app.get("/api/plans/{plan_id}")
def get_plan_by_id(plan_id: str):
    """Retrieve full details of a specific saved plan."""
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    return plan

@app.delete("/api/plans/{plan_id}")
def delete_plan_by_id(plan_id: str):
    """Delete a saved plan."""
    success = delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    return {"status": "deleted", "plan_id": plan_id}

# WebSocket Endpoint for Live Multi-Agent Streaming
@app.websocket("/ws/{session_id}")
async def websocket_agent_stream(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        # Await incoming travel planning parameters
        data_text = await websocket.receive_text()
        req_payload = json.loads(data_text)

        # Stream LangGraph events
        final_plan_data = None
        async for event in run_travel_agent_stream(req_payload, session_id):
            await websocket.send_text(json.dumps(event))
            if event.get("type") == "workflow_complete":
                final_plan_data = event.get("final_plan")

        # Persist final plan to database
        if final_plan_data:
            save_plan(
                plan_id=session_id,
                destination=final_plan_data.get("destination", req_payload.get("destination", "Destination")),
                origin=final_plan_data.get("origin", req_payload.get("origin", "Origin")),
                title=final_plan_data.get("title", f"Trip to {req_payload.get('destination')}"),
                duration_days=final_plan_data.get("duration_days", req_payload.get("duration_days", 5)),
                budget_category=final_plan_data.get("budget_tier", req_payload.get("budget", "Moderate")),
                travelers=final_plan_data.get("travelers", req_payload.get("travelers", 1)),
                travel_style=final_plan_data.get("travel_style", req_payload.get("travel_style", "General")),
                plan_data=final_plan_data,
                request_data=req_payload
            )
            # Confirm saved event
            await websocket.send_text(json.dumps({
                "type": "database_saved",
                "plan_id": session_id,
                "message": "Trip plan safely saved to persistent storage"
            }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    finally:
        try:
            await websocket.close()
        except Exception:
            pass

# Serve Frontend static assets (supports compiled React Vite dist and fallback)
frontend_path = settings.FRONTEND_DIR
dist_path = frontend_path / "dist"

if (dist_path / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="react-assets")

if (frontend_path / "css").exists():
    app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
if (frontend_path / "js").exists():
    app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")

@app.get("/")
def serve_frontend_index():
    if (dist_path / "index.html").exists():
        return FileResponse(str(dist_path / "index.html"))
    return FileResponse(str(frontend_path / "index.html"))

@app.get("/{full_path:path}")
def serve_static_or_index(full_path: str):
    # Check in dist first (for React build)
    target_in_dist = dist_path / full_path
    if dist_path.exists() and target_in_dist.is_file():
        return FileResponse(str(target_in_dist))

    # Check in frontend root
    target_file = frontend_path / full_path
    if target_file.is_file():
        return FileResponse(str(target_file))

    # Fallback to SPA index
    if (dist_path / "index.html").exists():
        return FileResponse(str(dist_path / "index.html"))
    return FileResponse(str(frontend_path / "index.html"))

