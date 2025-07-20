#!/usr/bin/env python3
"""
Kairos Trading API Server - Enhanced for True Autonomous Trading
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

# Import the specific, refactored agent and necessary functions
from agent.kairos_autonomous_agent import KairosAutonomousAgent
from database.supabase_client import supabase_client
from api.portfolio import get_portfolio

# Initialize FastAPI app
app = FastAPI(title="Kairos Autonomous Trading API", version="3.0.0")

# This dictionary will store active agent instances by session_id
active_sessions: Dict[str, KairosAutonomousAgent] = {}

# --- Request/Response Models ---
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    duration_minutes: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    timestamp: str

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"status": "🚀 Kairos Autonomous Trading API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint to start an autonomous trading session.
    """
    try:
        user_id = request.user_id or "default"
        duration = request.duration_minutes
        
        if not duration or duration <= 0:
            raise HTTPException(status_code=400, detail="A valid 'duration_minutes' > 0 is required to start an autonomous session.")

        # 1. Create a new session in the database
        session_name = f"Autonomous Session for {duration} mins"
        initial_portfolio = get_portfolio(user_id=user_id)
        start_value = 0.0
        if initial_portfolio and isinstance(initial_portfolio.get('balances'), list):
            start_value = sum(float(b.get('usd_value', 0)) for b in initial_portfolio['balances'] if isinstance(b,dict) and 'usd_value' in b)
        
        session_id = supabase_client.create_trading_session(
            user_id=user_id,
            session_name=session_name,
            initial_portfolio_value=start_value
        )
        print(f"✅ Created new session in DB: {session_id}")

        # 2. Create a new, dedicated agent instance for this session
        agent_instance = KairosAutonomousAgent(
            user_id=user_id,
            session_id=session_id,
            duration_minutes=duration
        )

        # 3. Store the agent instance in our active sessions dictionary
        active_sessions[session_id] = agent_instance

        # 4. Start the agent's trading loop in the background
        background_tasks.add_task(agent_instance.run_trading_loop)
        
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        response_text = f"🤖 **AUTONOMOUS TRADING ACTIVATED**\n\n✅ **Session ID:** `{session_id}`\n⏰ **Duration:** {duration} minutes\n📅 **End Time:** {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"

        return ChatResponse(
            response=response_text,
            intent="autonomous_session_started",
            data={
                "session_id": session_id,
                "user_id": user_id,
                "duration_minutes": duration,
                "end_time": end_time.isoformat(),
                "status": "active"
            },
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@app.get("/api/autonomous/status/{session_id}")
async def get_autonomous_status(session_id: str):
    """Get the real-time status of an active autonomous trading session."""
    agent_instance = active_sessions.get(session_id)

    if not agent_instance or not agent_instance.is_running:
        session_from_db = supabase_client.client.table("trading_sessions").select("*").eq("id", session_id).single().execute()
        if session_from_db.data:
            return {"session_found": True, "status": "completed", "session_data": session_from_db.data}
        raise HTTPException(status_code=404, detail="Autonomous session not found or has completed.")

    latest_portfolio = agent_instance._analyze_current_portfolio()
    
    return {
        "session_found": True,
        "session_id": agent_instance.session_id,
        "user_id": agent_instance.user_id,
        "status": "active" if agent_instance.is_running else "stopping",
        "end_time": agent_instance.end_time.isoformat(),
        "current_portfolio_value": latest_portfolio.get('total_value'),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Kairos Autonomous Trading API Server (v3)...")
    print("🔗 API Documentation: http://localhost:8000/docs")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)