import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from .config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_plans (
            id TEXT PRIMARY KEY,
            destination TEXT NOT NULL,
            origin TEXT,
            title TEXT NOT NULL,
            duration_days INTEGER DEFAULT 1,
            budget_category TEXT,
            travelers INTEGER DEFAULT 1,
            travel_style TEXT,
            created_at TEXT NOT NULL,
            plan_data TEXT NOT NULL,
            request_data TEXT NOT NULL,
            status TEXT DEFAULT 'completed'
        )
    """)
    conn.commit()
    conn.close()

def save_plan(plan_id: str, destination: str, origin: str, title: str,
              duration_days: int, budget_category: str, travelers: int,
              travel_style: str, plan_data: Dict[str, Any], request_data: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO travel_plans 
        (id, destination, origin, title, duration_days, budget_category, travelers, travel_style, created_at, plan_data, request_data, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plan_id,
        destination,
        origin or "",
        title,
        duration_days,
        budget_category or "Moderate",
        travelers,
        travel_style or "General",
        now_iso,
        json.dumps(plan_data),
        json.dumps(request_data),
        "completed"
    ))
    conn.commit()
    conn.close()
    return plan_id

def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM travel_plans WHERE id = ?", (plan_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "destination": row["destination"],
        "origin": row["origin"],
        "title": row["title"],
        "duration_days": row["duration_days"],
        "budget_category": row["budget_category"],
        "travelers": row["travelers"],
        "travel_style": row["travel_style"],
        "created_at": row["created_at"],
        "plan_data": json.loads(row["plan_data"]),
        "request_data": json.loads(row["request_data"]),
        "status": row["status"]
    }

def list_plans() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, destination, origin, title, duration_days, budget_category, travelers, travel_style, created_at, status 
        FROM travel_plans 
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "destination": row["destination"],
            "origin": row["origin"],
            "title": row["title"],
            "duration_days": row["duration_days"],
            "budget_category": row["budget_category"],
            "travelers": row["travelers"],
            "travel_style": row["travel_style"],
            "created_at": row["created_at"],
            "status": row["status"]
        }
        for row in rows
    ]

def delete_plan(plan_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM travel_plans WHERE id = ?", (plan_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
