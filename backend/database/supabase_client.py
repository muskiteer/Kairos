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
    
    # Trading Sessions with Enhanced Metrics
    def create_trading_session(self, user_id: str = "default", session_name: str = None, initial_portfolio_value: float = 0.0) -> str:
        """Create a new trading session with proper initialization"""
        session_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_name": session_name or f"Auto Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "start_time": datetime.utcnow().isoformat(),
            "status": "active",
            "initial_portfolio_value": initial_portfolio_value,
            "current_portfolio_value": initial_portfolio_value,
            "initial_portfolio": {},
            "final_portfolio": {},
            "total_trades": 0,
            "successful_trades": 0,
            "total_volume": 0.0,
            "total_profit_loss": 0.0,
            "total_pnl": 0.0,
            "ai_confidence_avg": 0.0,
            "risk_score": "medium",
            "session_metadata": {
                "created_by": "autonomous_agent",
                "version": "2.0",
                "initial_tokens": {}
            }
        }
        
        result = self.client.table("trading_sessions").insert(session_data).execute()
        return result.data[0]["id"]

    def update_trading_session_metrics(self, session_id: str, portfolio_value: float, trade_count: int = None, successful_trades: int = None, confidence: float = None, trade_volume: float = None):
        """Update trading session with real-time metrics"""
        try:
            # Get current session data
            current_session = self.client.table("trading_sessions").select("*").eq("id", session_id).execute()
            if not current_session.data:
                print(f"⚠️ Session {session_id} not found")
                return
            
            session = current_session.data[0]
            initial_value = float(session.get("initial_portfolio_value", 0))
            
            # Calculate P&L
            total_pnl = portfolio_value - initial_value if initial_value > 0 else 0.0
            
            # Prepare update data
            update_data = {
                "current_portfolio_value": portfolio_value,
                "total_pnl": total_pnl,
                "total_profit_loss": total_pnl,  # Same value, different field
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Add optional fields if provided
            if trade_count is not None:
                update_data["total_trades"] = trade_count
            if successful_trades is not None:
                update_data["successful_trades"] = successful_trades
            if confidence is not None:
                update_data["ai_confidence_avg"] = confidence
            if trade_volume is not None:
                current_volume = float(session.get("total_volume", 0))
                update_data["total_volume"] = current_volume + trade_volume
            
            # Update session
            self.client.table("trading_sessions").update(update_data).eq("id", session_id).execute()
            print(f"✅ Updated session metrics: Portfolio ${portfolio_value:,.2f}, P&L ${total_pnl:+,.2f}")
            
        except Exception as e:
            print(f"⚠️ Error updating session metrics: {e}")

    def end_trading_session(self, session_id: str, final_portfolio: dict, total_pnl: float):
        """End a trading session with comprehensive final results"""
        try:
            # Calculate final portfolio value
            final_value = sum(token.get("usd_value", 0) for token in final_portfolio.get("balances", []))
            
            update_data = {
                "end_time": datetime.utcnow().isoformat(),
                "status": "completed", 
                "final_portfolio": final_portfolio,
                "current_portfolio_value": final_value,
                "total_profit_loss": total_pnl,
                "total_pnl": total_pnl,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.client.table("trading_sessions").update(update_data).eq("id", session_id).execute()
            print(f"✅ Session {session_id} ended with P&L: ${total_pnl:+,.2f}")
            
        except Exception as e:
            print(f"⚠️ Error ending session: {e}")

    # Enhanced Trade Logging with Performance Tracking
    def log_trade_with_metrics(self, session_id: str, trade_data: dict, reasoning: str, pre_portfolio_value: float, post_portfolio_value: float):
        """Log a trade with comprehensive performance metrics"""
        try:
            trade_pnl = post_portfolio_value - pre_portfolio_value
            trade_volume = float(trade_data.get("amount", 0))
            
            # Enhance market_conditions with portfolio data
            enhanced_market_conditions = trade_data.get("market_conditions", {})
            enhanced_market_conditions.update({
                "pre_trade_portfolio_value": pre_portfolio_value,
                "post_trade_portfolio_value": post_portfolio_value,
                "portfolio_pnl": trade_pnl,
                "trade_volume_usd": trade_volume
            })
            
            trade_log = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "trade_type": trade_data.get("trade_type", "swap"),
                "from_token": trade_data.get("from_token"),
                "to_token": trade_data.get("to_token"),
                "from_amount": float(trade_data.get("amount", 0)),
                "to_amount": float(trade_data.get("to_amount", 0)) if trade_data.get("to_amount", 0) > 0 else None,
                "price": float(trade_data.get("price", 0)) if trade_data.get("price", 0) > 0 else None,
                "ai_reasoning": reasoning,
                "ai_confidence": float(trade_data.get("confidence", 0.5)),
                "market_conditions": enhanced_market_conditions,
                "status": "executed" if trade_data.get("success", False) else "failed",
                "execution_time": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert trade
            result = self.client.table("trades").insert(trade_log).execute()
            
            # Update session metrics
            self.update_trading_session_metrics(
                session_id=session_id,
                portfolio_value=post_portfolio_value,
                trade_volume=trade_volume,
                confidence=float(trade_data.get("confidence", 0.5))
            )
            
            return result.data[0]["id"] if result.data else None
            
        except Exception as e:
            print(f"⚠️ Error logging trade: {e}")
            return None
    
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
    
    def upsert_strategy(self, session_id: str, strategy_name: str, strategy_type: str = "custom"):
        """Upsert a strategy with proper type mapping and correct column names"""
        try:
            # Map strategy names to valid database types
            strategy_type_mapping = {
                'momentum': 'momentum',
                'arbitrage': 'arbitrage', 
                'dca': 'dca',
                'swing': 'swing',
                'scalping': 'scalping',
                'hodl': 'hodl',  # Fixed: use 'hodl' not 'hold'
                'hold': 'hodl',   # Fixed: map 'hold' to 'hodl'
                'custom': 'custom',
                'system_error': 'custom',
                'unknown_ai_strategy': 'custom',
                'hodl_empty_portfolio': 'hodl'
            }
            
            # Get proper strategy type for database
            db_strategy_type = strategy_type_mapping.get(strategy_type.lower(), 'custom')
            
            # Fixed: Use correct column names from schema
            strategy_data = {
                'session_id': session_id,
                'strategy_name': strategy_name,  # Fixed: was 'name'
                'strategy_type': db_strategy_type,
                'strategy_description': f"AI-generated strategy: {strategy_name}",  # Fixed: was 'description'
                'strategy_parameters': {'auto_generated': True},  # Fixed: was 'parameters'
                'performance_metrics': {'usage_count': 0},  # Fixed: was 'metadata'
                'success_rate': 0.0,
                'is_active': True
                # Removed created_at/updated_at - they're auto-generated by DB
            }
            
            result = self.client.table('ai_strategies').upsert(strategy_data).execute()
            
            if result.data:
                strategy_id = result.data[0].get('id')
                print(f"✅ Strategy '{strategy_name}' saved with ID: {strategy_id}")
                return strategy_id
            else:
                print("⚠️ Strategy upserted but no ID returned")
                return None
                
        except Exception as e:
            print(f"⚠️ Error upserting strategy: {e}")
            return None
        

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
