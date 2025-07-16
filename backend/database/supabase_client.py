#!/usr/bin/env python3
"""
Supabase client for Kairos Trading Agent
Handles structured data storage and vector embeddings
"""

import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from datetime import datetime
import json
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    """Supabase client for trading data and strategy storage"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.client: Client = create_client(self.url, self.key)
    
    # Trading Sessions
    async def create_trading_session(self, user_id: str = "default") -> str:
        """Create a new trading session"""
        session_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "start_time": datetime.utcnow().isoformat(),
            "status": "active",
            "initial_portfolio": {},
            "final_portfolio": {},
            "total_trades": 0,
            "total_profit_loss": 0.0
        }
        
        result = self.client.table("trading_sessions").insert(session_data).execute()
        return result.data[0]["id"]
    
    async def end_trading_session(self, session_id: str, final_portfolio: dict, total_pnl: float):
        """End a trading session with final results"""
        update_data = {
            "end_time": datetime.utcnow().isoformat(),
            "status": "completed",
            "final_portfolio": final_portfolio,
            "total_profit_loss": total_pnl
        }
        
        self.client.table("trading_sessions").update(update_data).eq("id", session_id).execute()
    
    # Trade Logging
    async def log_trade(self, session_id: str, trade_data: dict, reasoning: str):
        """Log a trade execution with AI reasoning"""
        trade_log = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "trade_type": trade_data.get("trade_type", "unknown"),
            "from_token": trade_data.get("from_token"),
            "to_token": trade_data.get("to_token"),
            "amount": float(trade_data.get("amount", 0)),
            "price": float(trade_data.get("price", 0)),
            "reasoning": reasoning,
            "market_conditions": trade_data.get("market_conditions", {}),
            "success": trade_data.get("success", False),
            "profit_loss": float(trade_data.get("profit_loss", 0))
        }
        
        self.client.table("trade_logs").insert(trade_log).execute()
        return trade_log["id"]
    
    # Strategy Storage (Vector Embeddings)
    async def store_strategy(self, strategy_text: str, embedding: List[float], 
                           performance_score: float, context: dict):
        """Store a trading strategy with its vector embedding"""
        strategy_data = {
            "id": str(uuid.uuid4()),
            "strategy_text": strategy_text,
            "embedding": embedding,
            "performance_score": performance_score,
            "context": context,
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0
        }
        
        self.client.table("strategies").insert(strategy_data).execute()
        return strategy_data["id"]
    
    async def search_similar_strategies(self, query_embedding: List[float], 
                                      limit: int = 5) -> List[dict]:
        """Search for similar strategies using vector similarity"""
        # Use pgvector similarity search
        result = self.client.rpc(
            "match_strategies",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.7,
                "match_count": limit
            }
        ).execute()
        
        return result.data if result.data else []
    
    # Session Analytics
    async def get_session_analytics(self, session_id: str) -> dict:
        """Get comprehensive analytics for a trading session"""
        # Get session data
        session = self.client.table("trading_sessions").select("*").eq("id", session_id).execute()
        
        # Get all trades for this session
        trades = self.client.table("trade_logs").select("*").eq("session_id", session_id).execute()
        
        if not session.data:
            return {"error": "Session not found"}
        
        session_data = session.data[0]
        trade_data = trades.data if trades.data else []
        
        # Calculate analytics
        total_trades = len(trade_data)
        successful_trades = len([t for t in trade_data if t["success"]])
        total_pnl = sum([t["profit_loss"] for t in trade_data])
        
        return {
            "session": session_data,
            "trades": trade_data,
            "analytics": {
                "total_trades": total_trades,
                "successful_trades": successful_trades,
                "success_rate": (successful_trades / total_trades * 100) if total_trades > 0 else 0,
                "total_pnl": total_pnl,
                "avg_trade_pnl": total_pnl / total_trades if total_trades > 0 else 0
            }
        }

# Global instance
supabase_client = SupabaseClient()
