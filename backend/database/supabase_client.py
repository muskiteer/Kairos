#!/usr/bin/env python3
"""
Supabase Client for Kairos Trading Agent - FIXED VERSION (No Hanging!)
"""

import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import uuid
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
    print("✅ Supabase client loaded successfully")
except ImportError as e:
    print(f"⚠️ Supabase not available: {e}")
    SUPABASE_AVAILABLE = False

class EnhancedSupabaseClient:
    """🚀 FAST & RELIABLE Supabase client (No hanging!)"""
    
    def __init__(self):
        """Initialize Supabase client WITHOUT connection testing (fast startup)"""
        if not SUPABASE_AVAILABLE:
            print("❌ Supabase not available - running in mock mode")
            self.client = None
            self.mock_mode = True
            return
            
        try:
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_ANON_KEY")
            
            if not self.url or not self.key:
                print("⚠️ Missing Supabase credentials - running in mock mode")
                self.client = None
                self.mock_mode = True
                return
                
            # Create client WITHOUT testing connection (this was causing the hang!)
            self.client: Client = create_client(self.url, self.key)
            self.mock_mode = False
            
            print("✅ Supabase client initialized successfully (fast mode)")
            
        except Exception as e:
            print(f"❌ Supabase initialization failed: {e}")
            print("🔄 Falling back to mock mode")
            self.client = None
            self.mock_mode = True
    
    def _test_connection(self):
        """Test database connection ONLY when needed (lazy testing)"""
        try:
            if self.mock_mode or not self.client:
                return True
                
            # Simple test query with timeout
            result = self.client.table("trading_sessions").select("id").limit(1).execute()
            print("✅ Database connection verified")
            return True
        except Exception as e:
            print(f"⚠️ Database connection test failed: {e}")
            print("🔄 Switching to mock mode")
            self.mock_mode = True
            return False

    # 🏆 TRADING SESSIONS
    def create_trading_session(self, user_id: str = "default", session_name: str = None, 
                             initial_portfolio_value: float = 0.0, duration_minutes: int = 60) -> str:
        """Create a new trading session"""
        
        session_id = str(uuid.uuid4())
        
        if self.mock_mode:
            print(f"🔄 MOCK: Creating session {session_id[:8]}... for {duration_minutes} minutes")
            return session_id
            
        try:
            # Test connection on first use
            if not hasattr(self, '_connection_tested'):
                self._test_connection()
                self._connection_tested = True
            
            if self.mock_mode:  # Might have switched during test
                return session_id
                
            current_time = datetime.utcnow().isoformat()
            end_time = (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat()
            
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "session_name": session_name or f"Autonomous Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                "start_time": current_time,
                "end_time": end_time,
                "status": "active",
                "initial_portfolio_value": float(initial_portfolio_value),
                "current_portfolio_value": float(initial_portfolio_value),
                "total_trades": 0,
                "successful_trades": 0,
                "total_volume": 0.0,
                "total_profit_loss": 0.0,
                "total_pnl": 0.0,
                "session_metadata": {
                    "created_by": "kairos_ai_agent",
                    "version": "3.0",
                    "duration_minutes": duration_minutes
                }
            }
            
            print(f"💾 Creating session in database: {session_id[:8]}...")
            result = self.client.table("trading_sessions").insert(session_data).execute()
            
            if result.data:
                print(f"✅ Session created successfully: {session_id[:8]}...")
                return result.data[0]["id"]
            else:
                print("⚠️ No data returned, using generated ID")
                return session_id
                
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            print("🔄 Continuing with mock ID")
            return session_id

    def update_trading_session_metrics(self, session_id: str, portfolio_value: float, 
                                     trade_count: int = None, successful_trades: int = None, 
                                     confidence: float = None, trade_volume: float = None):
        """Update trading session metrics"""
        
        if self.mock_mode:
            print(f"🔄 MOCK: Updating session {session_id[:8]}... metrics")
            return
            
        try:
            print(f"📊 Updating session metrics for {session_id[:8]}...")
            
            update_data = {
                "current_portfolio_value": float(portfolio_value),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if trade_count is not None:
                update_data["total_trades"] = int(trade_count)
                
            if successful_trades is not None:
                update_data["successful_trades"] = int(successful_trades)
                
            if confidence is not None:
                update_data["ai_confidence_avg"] = float(confidence)
                
            if trade_volume is not None:
                # Get current volume first (simplified)
                update_data["total_volume"] = float(trade_volume)
            
            result = self.client.table("trading_sessions").update(update_data).eq("id", session_id).execute()
            print(f"✅ Session metrics updated successfully")
            
        except Exception as e:
            print(f"❌ Error updating session metrics: {e}")

    def end_trading_session(self, session_id: str, final_portfolio: dict, total_pnl: float):
        """End a trading session"""
        
        if self.mock_mode:
            print(f"🔄 MOCK: Ending session {session_id[:8]}... with P&L ${total_pnl:+.4f}")
            return
            
        try:
            print(f"🏁 Ending trading session {session_id[:8]}...")
            
            final_value = final_portfolio.get("total_value", 0) if isinstance(final_portfolio, dict) else 0
            
            update_data = {
                "end_time": datetime.utcnow().isoformat(),
                "status": "completed",
                "final_portfolio": final_portfolio,
                "current_portfolio_value": float(final_value),
                "total_profit_loss": float(total_pnl),
                "total_pnl": float(total_pnl),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("trading_sessions").update(update_data).eq("id", session_id).execute()
            print(f"✅ Session {session_id[:8]}... completed successfully")
            
        except Exception as e:
            print(f"❌ Error ending session: {e}")

    # 💱 TRADE LOGGING
    def log_trade_with_metrics(self, session_id: str, trade_data: dict, reasoning: str, 
                             pre_portfolio_value: float, post_portfolio_value: float):
        """Log a trade with metrics"""
        
        if self.mock_mode:
            print(f"🔄 MOCK: Logging trade for session {session_id[:8]}...")
            return f"mock_trade_{uuid.uuid4()}"
            
        try:
            trade_pnl = post_portfolio_value - pre_portfolio_value
            
            trade_log = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "trade_type": trade_data.get("trade_type", "swap"),
                "from_token": trade_data.get("from_token"),
                "to_token": trade_data.get("to_token"),
                "from_amount": float(trade_data.get("amount", 0)),
                "ai_reasoning": reasoning,
                "ai_confidence": float(trade_data.get("confidence", 0.5)),
                "status": "executed" if trade_data.get("success", False) else "failed",
                "execution_time": datetime.utcnow().isoformat(),
                "profit_loss": float(trade_pnl),
                "success": bool(trade_data.get("success", False)),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("trades").insert(trade_log).execute()
            
            if result.data:
                trade_id = result.data[0]["id"]
                print(f"✅ Trade logged successfully: {trade_id[:8]}...")
                return trade_id
            else:
                return str(uuid.uuid4())
                
        except Exception as e:
            print(f"❌ Error logging trade: {e}")
            return None

    # 🧠 AI STRATEGIES
    def get_strategies_for_session(self, session_id: str) -> List[dict]:
        """Get AI strategies for session"""
        
        if self.mock_mode:
            print(f"🔄 MOCK: Getting strategies for session {session_id[:8]}...")
            return [
                {
                    "id": "mock_strategy_1",
                    "strategy_name": "momentum_trading",
                    "strategy_type": "momentum",
                    "success_rate": 0.75,
                    "performance_metrics": {"usage_count": 5}
                }
            ]
            
        try:
            result = self.client.table("ai_strategies").select("*").eq("session_id", session_id).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error fetching strategies: {e}")
            return []

    def upsert_strategy(self, session_id: str, strategy_name: str, strategy_type: str = "custom") -> Optional[str]:
        """Upsert AI strategy with proper schema compliance"""
        
        if self.mock_mode:
            mock_id = f"mock_strategy_{uuid.uuid4()}"
            print(f"🔄 MOCK: Upserting strategy {strategy_name} -> {mock_id[:8]}...")
            return mock_id
            
        try:
            strategy_type_mapping = {
                'momentum': 'momentum', 'arbitrage': 'arbitrage', 'dca': 'dca',
                'swing': 'swing', 'scalping': 'scalping', 'hodl': 'hodl',
                'hold': 'hodl', 'custom': 'custom', 'system_error': 'custom',
                'unknown_ai_strategy': 'custom', 'hodl_empty_portfolio': 'hodl',
                'momentum_trading': 'momentum', 'arbitrage_opportunity': 'arbitrage',
                'system_error_recovery': 'hodl'
            }
            
            db_strategy_type = strategy_type_mapping.get(strategy_type.lower(), 'custom')
            
            # Create comprehensive strategy data matching database schema
            strategy_data = {
                'session_id': session_id,
                'strategy_name': strategy_name,
                'strategy_type': db_strategy_type,
                'strategy_description': f"AI-generated {db_strategy_type} strategy: {strategy_name}",
                'strategy_parameters': {  # Required field - must not be NULL
                    'auto_generated': True,
                    'ai_engine': 'gemini-1.5-pro',
                    'strategy_type': db_strategy_type,
                    'creation_timestamp': datetime.utcnow().isoformat(),
                    'risk_tolerance': 'moderate',
                    'position_sizing': 'conservative'
                },
                'performance_metrics': {
                    'usage_count': 0,
                    'total_executions': 0,
                    'successful_executions': 0,
                    'creation_time': datetime.utcnow().isoformat()
                },
                'success_rate': 0.0,
                'total_return': 0.0,
                'max_drawdown': None,
                'sharpe_ratio': None,
                'win_rate': None,
                'avg_trade_duration': None,
                'strategy_embedding': None,  # Will be populated later if needed
                'market_conditions': {},
                'risk_assessment': {
                    'risk_level': 'medium',
                    'position_sizing': 'conservative',
                    'max_position_size': 0.5
                },
                'is_active': True
            }
            
            result = self.client.table('ai_strategies').upsert(strategy_data).execute()
            
            if result.data:
                strategy_id = result.data[0].get('id')
                print(f"✅ Strategy '{strategy_name}' upserted successfully: {strategy_id[:8]}...")
                return strategy_id
            else:
                print("⚠️ Strategy upserted but no ID returned")
                return str(uuid.uuid4())
                
        except Exception as e:
            print(f"❌ Error upserting strategy: {e}")
            # Log detailed error for debugging
            import traceback
            traceback.print_exc()
            return None
        
        
    def update_strategy_performance(self, strategy_id: str, success: bool, performance_data: dict):
        """Update strategy performance"""
        
        if self.mock_mode:
            print(f"🔄 MOCK: Updating strategy {strategy_id[:8]}... performance")
            return
            
        try:
            # Simplified update without complex calculations
            update_data = {
                "updated_at": datetime.utcnow().isoformat(),
                "performance_metrics": performance_data
            }
            
            result = self.client.table("ai_strategies").update(update_data).eq("id", strategy_id).execute()
            print(f"✅ Strategy performance updated")
            
        except Exception as e:
            print(f"❌ Error updating strategy performance: {e}")

    # 📊 ANALYTICS (Simplified)
    def get_session_analytics(self, session_id: str) -> dict:
        """Get session analytics"""
        
        if self.mock_mode:
            return {
                "session_data": {"id": session_id, "status": "completed"},
                "performance": {"total_trades": 5, "successful_trades": 4},
                "trades_executed": []
            }
            
        try:
            # Get session data
            session_result = self.client.table("trading_sessions").select("*").eq("id", session_id).execute()
            
            # Get trades
            trades_result = self.client.table("trades").select("*").eq("session_id", session_id).execute()
            
            if not session_result.data:
                return {"error": "Session not found"}
            
            session_data = session_result.data[0]
            trades = trades_result.data if trades_result.data else []
            
            return {
                "session_data": {
                    **session_data,
                    "trades_executed": trades
                },
                "performance": {
                    "total_trades": len(trades),
                    "successful_trades": sum(1 for t in trades if t.get("success", False)),
                    "current_portfolio_value": session_data.get("current_portfolio_value", 0),
                    "total_profit_loss": session_data.get("total_profit_loss", 0),
                    "ai_engine": "Kairos Gemini v3.0"
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating analytics: {e}")
            return {"error": str(e)}

# 🌟 GLOBAL INSTANCE - FAST STARTUP!
try:
    supabase_client = EnhancedSupabaseClient()
    print("🚀 Supabase client ready! (No hanging)")
except Exception as e:
    print(f"⚠️ Failed to initialize Supabase client: {e}")
    
    # Ultra-simple mock fallback
    class MockSupabaseClient:
        def __init__(self):
            self.mock_mode = True
            print("🔄 Mock Supabase client active")
        
        def create_trading_session(self, *args, **kwargs):
            return str(uuid.uuid4())
        
        def update_trading_session_metrics(self, *args, **kwargs):
            print("🔄 MOCK: Session metrics updated")
        
        def end_trading_session(self, *args, **kwargs):
            print("🔄 MOCK: Session ended")
        
        def log_trade_with_metrics(self, *args, **kwargs):
            return str(uuid.uuid4())
        
        def get_strategies_for_session(self, *args, **kwargs):
            return []
        
        def upsert_strategy(self, *args, **kwargs):
            return str(uuid.uuid4())
        
        def update_strategy_performance(self, *args, **kwargs):
            print("🔄 MOCK: Strategy performance updated")
        
        def get_session_analytics(self, session_id, *args, **kwargs):
            return {
                "session_data": {"id": session_id, "status": "mock"},
                "performance": {"total_trades": 0}
            }
    
    supabase_client = MockSupabaseClient()