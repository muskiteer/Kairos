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
    
    # AI Strategies Management
    def get_strategies_for_session(self, session_id: str) -> List[dict]:
        """Get all active strategies for a session"""
        try:
            result = self.client.table("ai_strategies").select("*").eq("session_id", session_id).eq("is_active", True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"⚠️ Error fetching strategies: {e}")
            return []
    
    def insert_strategy(self, strategy_data: dict) -> dict:
        """Insert a new strategy record"""
        try:
            # Ensure all required fields are present
            strategy_record = {
                "id": str(uuid.uuid4()),
                "session_id": strategy_data.get("session_id"),
                "strategy_name": strategy_data.get("strategy_name", "unknown"),
                "strategy_type": strategy_data.get("strategy_type", "custom"),
                "strategy_description": strategy_data.get("strategy_description", ""),
                "strategy_parameters": strategy_data.get("strategy_parameters", {}),
                "performance_metrics": strategy_data.get("performance_metrics", {}),
                "market_conditions": strategy_data.get("market_conditions", {}),
                "risk_assessment": strategy_data.get("risk_assessment", {}),
                "success_rate": strategy_data.get("success_rate", 0.0),
                "is_active": strategy_data.get("is_active", True),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("ai_strategies").insert(strategy_record).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"⚠️ Error inserting strategy: {e}")
            return {}
        

    # Add these methods to the SupabaseClient class (around line 180, before update_strategy_performance):

    # AI Conversations for Decision Persistence
    def insert_ai_conversation(self, data: dict) -> dict:
        """Insert an AI conversation/decision record"""
        try:
            result = self.client.table("ai_conversations").insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"⚠️ Error inserting AI conversation: {e}")
            return {}
    
    def get_ai_conversations(self, session_id: str) -> List[dict]:
        """Get all AI conversations for a session, ordered by message_order"""
        try:
            result = self.client.table("ai_conversations").select("*").eq("session_id", session_id).order("message_order").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"⚠️ Error fetching AI conversations: {e}")
            return []
    
    def get_latest_message_order(self, session_id: str) -> int:
        """Get the latest message_order for a session to avoid conflicts"""
        try:
            result = self.client.table("ai_conversations").select("message_order").eq("session_id", session_id).order("message_order", desc=True).limit(1).execute()
            if result.data:
                return result.data[0]["message_order"] + 1
            return 1
        except Exception as e:
            print(f"⚠️ Error getting latest message order: {e}")
            return 1
    
    def insert_trade_record(self, session_id: str, trade_data: dict) -> dict:
        """Insert a trade record with AI reasoning"""
        try:
            full_trade_data = {
                "session_id": session_id,
                **trade_data,
                "created_at": datetime.utcnow().isoformat()
            }
            result = self.client.table("trades").insert(full_trade_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"⚠️ Error inserting trade record: {e}")
            return {}
    
    def get_session_memory_summary(self, session_id: str) -> dict:
        """Get a summary of session memory for quick loading"""
        try:
            conversations = self.get_ai_conversations(session_id)
            trades_result = self.client.table("trades").select("*").eq("session_id", session_id).order("created_at").execute()
            strategies_result = self.client.table("ai_strategies").select("*").eq("session_id", session_id).execute()
            
            return {
                "conversations": conversations,
                "trades": trades_result.data if trades_result.data else [],
                "strategies": strategies_result.data if strategies_result.data else []
            }
        except Exception as e:
            print(f"⚠️ Error getting session memory: {e}")
            return {"conversations": [], "trades": [], "strategies": []}
    
    def update_strategy_performance(self, strategy_id: str, success: bool, performance_data: dict):
        """Update strategy performance after execution"""
        try:
            # Get current strategy
            current = self.client.table("ai_strategies").select("*").eq("id", strategy_id).execute()
            if not current.data:
                return
            
            strategy = current.data[0]
            current_success_rate = strategy.get("success_rate", 0.0)
            current_metrics = strategy.get("performance_metrics", {})
            
            # Update success rate (simple moving average)
            usage_count = current_metrics.get("usage_count", 0) + 1
            if success:
                new_success_rate = ((current_success_rate * (usage_count - 1)) + 1.0) / usage_count
            else:
                new_success_rate = (current_success_rate * (usage_count - 1)) / usage_count
            
            # Update performance metrics
            updated_metrics = {
                **current_metrics,
                "usage_count": usage_count,
                "last_used": datetime.utcnow().isoformat(),
                **performance_data
            }
            
            # Update the strategy
            self.client.table("ai_strategies").update({
                "success_rate": new_success_rate,
                "performance_metrics": updated_metrics,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", strategy_id).execute()
            
        except Exception as e:
            print(f"⚠️ Error updating strategy performance: {e}")

# Global instance
supabase_client = SupabaseClient()
