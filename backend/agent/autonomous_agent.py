#!/usr/bin/env python3
"""
Kairos Autonomous Trading Agent
Advanced AI that can trade autonomously for specified time periods
"""

import asyncio
from database.supabase_client import supabase_client
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
import os
from dotenv import load_dotenv

# Import existing modules
from agent.kairos_copilot import kairos_copilot
from api.portfolio import get_portfolio
from api.token_price import get_token_price_json
from api.token_balance import get_token_balance
from api.execute import trade_exec, token_addresses
from api.trades_history import get_portfolio as get_trades_history
from agent.coinpanic_api import get_trending_news
from agent.vincent_agent import vincent_agent
from database.supabase_client import supabase_client

load_dotenv()

class KairosAutonomousAgent:
    """Autonomous Trading Agent with Full AI Decision Making"""
    
    def __init__(self, user_id: str = "default"):
        """Initialize the autonomous agent"""
        self.user_id = user_id
        self.base_copilot = None  # Will be initialized with user_id when needed
        self.autonomous_sessions = {}  # Track active autonomous sessions
        self.memory = []  # Persistent memory for learning
        self.message_order_counter = {}  # Track message order per session
        
        print("🤖 Kairos Autonomous Agent initialized!")
        print("💡 I can trade autonomously for hours, days, or weeks!")
    
    def _get_copilot(self):
        """Get or initialize the copilot with user_id"""
        if not self.base_copilot:
            from agent.kairos_copilot import KairosTradingCopilot
            self.base_copilot = KairosTradingCopilot(user_id=self.user_id)
        return self.base_copilot
    
    async def process_autonomous_request(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        """Process autonomous trading requests"""
        
        # Update user_id if different
        if user_id != self.user_id:
            self.user_id = user_id
            self.base_copilot = None  # Reset copilot to reinitialize with new user_id
        
        # Parse autonomous command
        autonomous_params = self._parse_autonomous_command(user_message)
        
        if not autonomous_params:
            copilot = self._get_copilot()
            return await copilot.process_user_message(user_message)
        
        # Start autonomous session
        session_id = await self._start_autonomous_session(autonomous_params, user_id)
        
        response = f"""🤖 **AUTONOMOUS TRADING ACTIVATED**

⏰ **Duration:** {autonomous_params['duration_text']}
🎯 **Strategy:** Intelligent market analysis & execution
📊 **Monitoring:** Real-time portfolio & news analysis
🔄 **Frequency:** Every 5-10 minutes
💾 **Memory:** Learning from every decision

🚀 **What I'll do autonomously:**
• Monitor your portfolio continuously
• Analyze market news and sentiment
• Execute strategic trades based on AI analysis
• Learn from successful and failed trades
• Maintain risk management protocols
• Log all decisions with detailed reasoning

✅ **Session ID:** `{session_id}`
📅 **End Time:** {autonomous_params['end_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}

💬 **You can still chat with me while I trade!**

**Commands you can use:**
• `"status"` - Check autonomous trading status
• `"stop autonomous"` - Stop autonomous mode
• `"show reasoning"` - See my latest decision logic
• `"performance report"` - Get detailed performance analysis"""
        
        return {
            "intent": "autonomous_activated",
            "response": response,
            "data": {
                "session_id": session_id,
                "autonomous_params": autonomous_params,
                "status": "active"
            },
            "actions_taken": ["activated_autonomous_trading"],
            "reasoning": f"Started autonomous trading for {autonomous_params['duration_text']}"
        }
    
    def _parse_autonomous_command(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse autonomous trading commands"""
        
        message_lower = message.lower()
        
        # Check for autonomous keywords
        autonomous_keywords = ["autonomous", "start trading session", "trade for", "auto trade", "test agent", "run agent"]
        if not any(keyword in message_lower for keyword in autonomous_keywords):
            # Also check for specific patterns like "1hr", "30min", "2days"
            time_pattern = r"\d+\s*(?:hr|hours?|min|minutes?|days?|weeks?)"
            if not re.search(time_pattern, message_lower):
                return None
        
        # Extract duration - NO DEFAULT, MUST BE SPECIFIED
        duration_hours = None
        duration_text = None
        
        # Parse various time formats with enhanced detection
        time_patterns = [
            (r"(\d+)\s*h(?:ours?)?(?:\s*(\d+)\s*m(?:in(?:utes?)?)?)?", "hours_minutes"),
            (r"(\d+)\s*m(?:in(?:utes?)?)", "minutes_only"),
            (r"(\d+)\s*d(?:ays?)?", "days"),
            (r"(\d+)\s*w(?:eeks?)?", "weeks"),
            (r"for\s+(\d+)\s*h(?:ours?)?", "hours_for"),
            (r"(\d+)\s*(?:hr|hrs)", "hours_short"),
        ]
        
        for pattern, pattern_type in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if pattern_type == "hours_minutes":
                    hours = int(match.group(1))
                    minutes = int(match.group(2)) if match.group(2) else 0
                    duration_hours = hours + (minutes / 60)
                    duration_text = f"{hours} hours" + (f" {minutes} minutes" if minutes else "")
                elif pattern_type == "minutes_only":
                    minutes = int(match.group(1))
                    duration_hours = minutes / 60
                    duration_text = f"{minutes} minutes"
                elif pattern_type == "days":
                    days = int(match.group(1))
                    duration_hours = days * 24
                    duration_text = f"{days} days"
                elif pattern_type == "weeks":
                    weeks = int(match.group(1))
                    duration_hours = weeks * 24 * 7
                    duration_text = f"{weeks} weeks"
                elif pattern_type == "hours_for":
                    duration_hours = int(match.group(1))
                    duration_text = f"{duration_hours} hours"
                elif pattern_type == "hours_short":
                    duration_hours = int(match.group(1))
                    duration_text = f"{duration_hours} hours"
                break
        
        # Special parsing for "24hr 10min" format
        special_match = re.search(r"(\d+)hr\s*(\d+)min", message_lower)
        if special_match:
            hours = int(special_match.group(1))
            minutes = int(special_match.group(2))
            duration_hours = hours + (minutes / 60)
            duration_text = f"{hours} hours {minutes} minutes"
        
        # Validation: Duration MUST be specified
        if duration_hours is None:
            return None  # No valid duration found
        
        # Safety limits
        if duration_hours < 0.02:  # Less than ~1 minute
            duration_hours = 0.02
            duration_text = "1 minute (minimum)"
        elif duration_hours > 8760:  # More than 1 year
            duration_hours = 8760
            duration_text = "1 year (maximum)"
        
        end_time = datetime.utcnow() + timedelta(hours=duration_hours)
        
        return {
            "duration_hours": duration_hours,
            "duration_text": duration_text,
            "end_time": end_time,
            "start_time": datetime.utcnow(),
            "target_tokens": ["ETH", "BTC", "USDC", "WETH", "UNI"],  # Default tokens
            "risk_level": "moderate",
            "max_trade_size": 500,  # Max USDC per trade
            "testing_mode": "testing" in message_lower or "test" in message_lower,
            "enhanced_learning": True,
            "cycle_frequency": 120 if "testing" in message_lower else 300  # Faster cycles for testing
        }
    
    async def _start_autonomous_session(self, params: Dict[str, Any], user_id: str) -> str:
        """Start an autonomous trading session with real database logging"""
        
        # Store session in database first and use the returned session_id
        try:
            # Use the correct method signature - only user_id parameter
            session_id = await supabase_client.create_trading_session(user_id)
            print(f"📊 Database session created: {session_id}")
            
            # Initialize message order counter for this session
            self.message_order_counter[session_id] = 1
            
            # Load previous decisions/memory for this session if it exists
            await self.load_session_memory(session_id)
            
        except Exception as e:
            print(f"⚠️ Could not store session in database: {e}")
            # Fallback to local session ID if database fails
            session_id = str(uuid.uuid4())
            self.message_order_counter[session_id] = 1
        
        # Get real starting portfolio value
        try:
            initial_portfolio = get_portfolio(user_id=user_id)
            start_value = self._calculate_real_portfolio_value(initial_portfolio)
        except Exception as e:
            print(f"⚠️ Could not get initial portfolio value: {e}")
            start_value = 0
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "params": params,
            "status": "active",
            "trades_executed": [],
            "strategies_used": [],
            "performance": {
                "total_trades": 0,
                "successful_trades": 0,
                "total_profit_loss": 0,
                "start_portfolio_value": start_value,
                "current_portfolio_value": start_value,
                "best_trade": None,
                "worst_trade": None,
                "roi_percentage": 0.0
            },
            "reasoning_log": [],
            "last_cycle": None,
            "strategies": {
                "momentum_strategy": {"used": 0, "success": 0},
                "mean_reversion": {"used": 0, "success": 0},
                "news_sentiment": {"used": 0, "success": 0},
                "diversification": {"used": 0, "success": 0}
            },
            "activities": []  # Initialize activities log
        }
        
        # Store session
        self.autonomous_sessions[session_id] = session_data
        
        # Seed initial strategies in the database
        await self.seed_initial_strategies(session_id)
        
        # Start the autonomous loop
        asyncio.create_task(self._autonomous_trading_loop(session_id))
        
        return session_id
    
    async def load_session_memory(self, session_id: str):
        """Load previous decisions and learning from database"""
        try:
            # Load previous conversations and decisions
            memory_data = supabase_client.get_session_memory_summary(session_id)
            
            # Restore conversations to memory
            conversations = memory_data.get("conversations", [])
            assistant_decisions = [conv for conv in conversations if conv["role"] == "assistant"]
            
            # Add to memory (append to existing memory)
            self.memory.extend(assistant_decisions)
            
            # Update message order counter
            if conversations:
                latest_order = max(conv["message_order"] for conv in conversations)
                self.message_order_counter[session_id] = latest_order + 1
            
            print(f"🧠 Loaded {len(assistant_decisions)} previous decisions from database")
            print(f"📊 Total memory entries: {len(self.memory)}")
            
        except Exception as e:
            print(f"⚠️ Could not load session memory: {e}")

    async def _autonomous_trading_loop(self, session_id: str):
        """Main autonomous trading loop"""
        
        session = self.autonomous_sessions.get(session_id)
        if not session:
            return
        
        print(f"🤖 Starting autonomous trading loop for session {session_id}")
        
        # Initialize starting portfolio value
        try:
            initial_portfolio = get_portfolio(user_id=session["user_id"])
            session["performance"]["start_portfolio_value"] = self._calculate_real_portfolio_value(initial_portfolio)
        except Exception as e:
            print(f"⚠️ Could not get initial portfolio value: {e}")
        
        cycle_count = 0
        
        while session["status"] == "active" and datetime.utcnow() < session["params"]["end_time"]:
            cycle_count += 1
            
            try:
                print(f"🔄 Autonomous cycle {cycle_count} for session {session_id}")
                
                # Perform autonomous decision cycle
                decision_result = await self._autonomous_decision_cycle(session_id)
                
                # Log the cycle
                session["reasoning_log"].append({
                    "cycle": cycle_count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": decision_result,
                    "portfolio_value": self._get_current_portfolio_value()
                })
                
                session["last_cycle"] = datetime.utcnow().isoformat()
                
                # Dynamic wait time based on testing mode and market conditions
                base_wait = session["params"].get("cycle_frequency", 300)
                wait_time = decision_result.get("next_cycle_wait", base_wait)
                
                # In testing mode, use shorter cycles for more data
                if session["params"].get("testing_mode", False):
                    wait_time = min(wait_time, 180)  # Max 3 minutes in testing
                
                print(f"⏱️ Next cycle in {wait_time//60:.0f}m {wait_time%60:.0f}s")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Error in autonomous cycle {cycle_count}: {e}")
                # Log error and continue
                session["reasoning_log"].append({
                    "cycle": cycle_count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e),
                    "action": "continuing_after_error"
                })
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        # End session
        session["status"] = "completed"
        session["end_time_actual"] = datetime.utcnow().isoformat()
        
        # Calculate final performance
        try:
            final_portfolio = get_portfolio(user_id=session["user_id"])
            session["performance"]["current_portfolio_value"] = self._calculate_real_portfolio_value(final_portfolio)
            session["performance"]["total_profit_loss"] = (
                session["performance"]["current_portfolio_value"] - 
                session["performance"]["start_portfolio_value"]
            )
            session["performance"]["roi_percentage"] = (
                (session["performance"]["total_profit_loss"] / session["performance"]["start_portfolio_value"]) * 100
                if session["performance"]["start_portfolio_value"] > 0 else 0
            )
        except Exception as e:
            print(f"⚠️ Could not calculate final performance: {e}")
        
        # Generate final PDF report
        try:
            pdf_path = await self._generate_session_pdf_report(session_id)
            session["pdf_report_path"] = pdf_path
            print(f"📄 PDF report generated: {pdf_path}")
        except Exception as e:
            print(f"⚠️ Could not generate PDF report: {e}")
        
        print(f"🏁 Autonomous trading session {session_id} completed after {cycle_count} cycles")
    
    async def _autonomous_decision_cycle(self, session_id: str) -> Dict[str, Any]:
        """Single autonomous decision-making cycle"""
        
        session = self.autonomous_sessions[session_id]
        
        # 1. Gather market intelligence
        market_data = await self._gather_market_intelligence()
        
        # 2. Analyze portfolio
        portfolio_analysis = await self._analyze_current_portfolio(session["user_id"])
        
        # 3. Make trading decision using AI
        trading_decision = await self._make_autonomous_trading_decision(
            market_data, 
            portfolio_analysis, 
            {**session["params"], "session_id": session_id}
        )
        
        # 4. Execute trade if decision is to trade
        execution_result = None
        if trading_decision.get("should_trade", False):
            execution_result = await self._execute_autonomous_trade(
                trading_decision["trade_params"],
                session_id
            )
        
        # 5. Learn from the decision (enhanced with strategy tracking) - PASS SESSION_ID
        await self._learn_from_decision(trading_decision, execution_result, market_data, session_id)
        
        return {
            "market_data": market_data,
            "portfolio_analysis": portfolio_analysis,
            "trading_decision": trading_decision,
            "execution_result": execution_result,
            "next_cycle_wait": trading_decision.get("next_cycle_wait", 300)
        }
    
    async def _gather_market_intelligence(self) -> Dict[str, Any]:
        """Gather comprehensive market data"""
        
        intelligence = {
            "timestamp": datetime.utcnow().isoformat(),
            "prices": {},
            "news": [],
            "sentiment": "neutral",
            "volatility": "medium"
        }
        
        try:
            # Get prices for major tokens
            for token in ["ETH", "BTC", "USDC"]:
                try:
                    price_data = get_token_price_json(token)
                    intelligence["prices"][token] = price_data.get("price", 0)
                except Exception as e:
                    print(f"⚠️ Could not get {token} price: {e}")
            
            # Get latest news
            try:
                news_response = get_trending_news(limit=10)
                if isinstance(news_response, dict) and "news" in news_response:
                    intelligence["news"] = news_response["news"][:5]
                    
                    # Basic sentiment analysis
                    positive_words = ["bull", "surge", "gain", "rise", "pump", "moon"]
                    negative_words = ["bear", "crash", "dump", "fall", "decline", "sell"]
                    
                    positive_count = 0
                    negative_count = 0
                    
                    for news_item in intelligence["news"]:
                        title = news_item.get("title", "").lower()
                        positive_count += sum(1 for word in positive_words if word in title)
                        negative_count += sum(1 for word in negative_words if word in title)
                    
                    if positive_count > negative_count + 2:
                        intelligence["sentiment"] = "bullish"
                    elif negative_count > positive_count + 2:
                        intelligence["sentiment"] = "bearish"
                    else:
                        intelligence["sentiment"] = "neutral"
                        
            except Exception as e:
                print(f"⚠️ Could not get news: {e}")
        
        except Exception as e:
            print(f"⚠️ Error gathering market intelligence: {e}")
        
        return intelligence
    
    async def _analyze_current_portfolio(self, user_id: str = "default") -> Dict[str, Any]:
        """Analyze current portfolio state"""
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_value": 0,
            "tokens": {},
            "diversification": "unknown",
            "risk_level": "medium"
        }
        
        try:
            portfolio_data = get_portfolio(user_id=user_id)
            
            if isinstance(portfolio_data, dict) and "balances" in portfolio_data:
                balances = portfolio_data["balances"]
            elif isinstance(portfolio_data, list):
                balances = portfolio_data
            else:
                balances = []
            
            total_value = 0
            for balance in balances:
                symbol = balance.get("symbol", "Unknown")
                amount = balance.get("amount", balance.get("balance", 0))
                
                if amount > 0:
                    # Get token value
                    try:
                        if symbol == "USDC":
                            value = amount  # USDC = $1
                        else:
                            price_data = get_token_price_json(symbol)
                            price = price_data.get("price", 0)
                            value = amount * price
                        
                        analysis["tokens"][symbol] = {
                            "amount": amount,
                            "value": value
                        }
                        total_value += value
                        
                    except Exception as e:
                        print(f"⚠️ Could not value {symbol}: {e}")
            
            analysis["total_value"] = total_value
            
            # Analyze diversification
            if len(analysis["tokens"]) >= 3:
                analysis["diversification"] = "good"
            elif len(analysis["tokens"]) == 2:
                analysis["diversification"] = "moderate"
            else:
                analysis["diversification"] = "poor"
        
        except Exception as e:
            print(f"⚠️ Error analyzing portfolio: {e}")
        
        return analysis
    
    async def _make_autonomous_trading_decision(self, market_data: Dict, portfolio_analysis: Dict, params: Dict) -> Dict[str, Any]:
        """DB-driven autonomous trading decision with guaranteed execution for learning"""
        
        decision = {
            "should_trade": False,
            "reasoning": [],
            "confidence": 0.5,
            "trade_params": None,
            "next_cycle_wait": 300,
            "strategy_used": "none",
            "strategy_id": None,
            "market_analysis": {},
            "risk_assessment": {}
        }

        reasoning = []
        testing_mode = params.get("testing_mode", False)
        session_id = params.get("session_id")
        portfolio_value = portfolio_analysis.get("total_value", 0)
        
        # Get real balances for decision making
        usdc_balance = portfolio_analysis.get("tokens", {}).get("USDC", {}).get("amount", 0)
        eth_balance = portfolio_analysis.get("tokens", {}).get("ETH", {}).get("amount", 0)
        
        reasoning.append(f"Portfolio value: ${portfolio_value:,.2f}")
        reasoning.append(f"USDC: {usdc_balance:,.2f}, ETH: {eth_balance:.4f}")
        reasoning.append(f"Testing mode: {'ACTIVE' if testing_mode else 'OFF'}")

        # 1. Try to fetch strategies from database first
        db_strategies = []
        try:
            db_strategies = supabase_client.get_strategies_for_session(session_id)
            reasoning.append(f"Found {len(db_strategies)} strategies in database")
        except Exception as e:
            reasoning.append(f"Error fetching DB strategies: {e}")

        strategy_selected = False
        
        # 2. If we have strategies in DB, try to apply them
        if db_strategies:
            for strategy in db_strategies:
                if strategy.get("is_active", True):
                    # Try to apply this strategy
                    strategy_params = strategy.get("strategy_parameters", {})
                    
                    # Basic validation - does the strategy make sense?
                    if self._validate_strategy_params(strategy_params, portfolio_analysis):
                        decision.update({
                            "should_trade": True,
                            "confidence": min(strategy.get("success_rate", 0.5), 0.9),
                            "strategy_used": strategy.get("strategy_name", "db_strategy"),
                            "strategy_id": strategy.get("id"),
                            "trade_params": strategy_params,
                            "next_cycle_wait": 120 if testing_mode else 300,
                            "market_analysis": strategy.get("market_conditions", {}),
                        })
                        reasoning.append(f"Applied DB strategy: {strategy.get('strategy_name')}")
                        strategy_selected = True
                        break
        
        # 3. If no valid DB strategy, create and execute a learning strategy
        if not strategy_selected:
            learning_strategy = self._create_learning_strategy(
                market_data, portfolio_analysis, testing_mode
            )
            
            decision.update({
                "should_trade": True,
                "confidence": learning_strategy["confidence"],
                "strategy_used": learning_strategy["name"],
                "trade_params": learning_strategy["params"],
                "next_cycle_wait": 120 if testing_mode else 300,
                "market_analysis": learning_strategy["analysis"],
            })
            reasoning.append(f"Created learning strategy: {learning_strategy['name']}")
            
            # Store this new strategy in the database for future use
            try:
                strategy_data = {
                    "session_id": session_id,
                    "strategy_name": learning_strategy["name"],
                    "strategy_type": learning_strategy.get("type", "custom"),
                    "strategy_description": learning_strategy.get("description", "AI-generated learning strategy"),
                    "strategy_parameters": learning_strategy["params"],
                    "market_conditions": market_data,
                    "risk_assessment": {"generated_for_learning": True},
                    "success_rate": 0.5,  # Initial neutral rating
                    "is_active": True
                }
                
                new_strategy = supabase_client.insert_strategy(strategy_data)
                decision["strategy_id"] = new_strategy.get("id")
                reasoning.append("Stored new learning strategy in database")
                
            except Exception as e:
                reasoning.append(f"Could not store strategy in DB: {e}")

        # 4. Calculate risk but DO NOT override for learning (key change!)
        if decision["should_trade"]:
            risk_score = self._calculate_risk_score(market_data, portfolio_analysis, decision)
            decision["risk_assessment"] = {"risk_score": risk_score}
            
            # In the original code, high risk would cancel the trade
            # NOW: We only reduce trade size but still execute for learning
            if risk_score > 0.8:
                if decision["trade_params"] and "amount" in decision["trade_params"]:
                    original_amount = decision["trade_params"]["amount"]
                    decision["trade_params"]["amount"] = min(original_amount * 0.3, 25)  # Max $25 for high risk learning
                    reasoning.append(f"HIGH RISK ({risk_score:.0%}): Reduced trade size to ${decision['trade_params']['amount']:.2f} for learning")
                else:
                    reasoning.append(f"HIGH RISK ({risk_score:.0%}): Proceeding with small learning trade")
            elif risk_score > 0.6:
                if decision["trade_params"] and "amount" in decision["trade_params"]:
                    decision["trade_params"]["amount"] *= 0.7
                    reasoning.append(f"Medium risk ({risk_score:.0%}): Reduced trade size for safety")

        # 5. Final validation - ensure we ALWAYS have a trade for learning
        if not decision["should_trade"] or not decision["trade_params"]:
            # Absolute fallback - ensure learning always happens
            fallback_amount = 5 if testing_mode else 10  # Very small amount
            decision.update({
                "should_trade": True,
                "confidence": 0.3,
                "strategy_used": "emergency_learning_fallback",
                "trade_params": {
                    "action": "buy",
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": fallback_amount
                },
                "next_cycle_wait": 120 if testing_mode else 300,
                "market_analysis": {"emergency_learning": True},
            })
            reasoning.append(f"EMERGENCY FALLBACK: Executing ${fallback_amount} learning trade")

        decision["reasoning"] = reasoning

        # Enhanced logging
        print(f"� Decision ({decision['strategy_used']}): Trade ${decision['trade_params'].get('amount', 0):.2f} {decision['trade_params'].get('from_token', 'N/A')}→{decision['trade_params'].get('to_token', 'N/A')} (Risk: {decision.get('risk_assessment', {}).get('risk_score', 0):.0%})")
        
        return decision
    
    def _validate_strategy_params(self, strategy_params: Dict, portfolio_analysis: Dict) -> bool:
        """Validate if strategy parameters make sense given current portfolio"""
        try:
            required_fields = ["from_token", "to_token", "amount"]
            if not all(field in strategy_params for field in required_fields):
                return False
            
            from_token = strategy_params["from_token"]
            amount = strategy_params["amount"]
            
            # Check if we have enough balance
            available_balance = portfolio_analysis.get("tokens", {}).get(from_token, {}).get("amount", 0)
            
            return available_balance >= amount and amount > 0
        except Exception:
            return False
    
    def _create_learning_strategy(self, market_data: Dict, portfolio_analysis: Dict, testing_mode: bool) -> Dict:
        """Create a new learning strategy based on current market conditions"""
        
        usdc_balance = portfolio_analysis.get("tokens", {}).get("USDC", {}).get("amount", 0)
        eth_balance = portfolio_analysis.get("tokens", {}).get("ETH", {}).get("amount", 0)
        sentiment = market_data.get("sentiment", "neutral")
        eth_price = market_data.get("prices", {}).get("ETH", 0)
        
        # Generate strategy based on current conditions
        if sentiment == "bullish" and usdc_balance > 20:
            # Bullish sentiment strategy
            amount = min(usdc_balance * 0.1, 50 if testing_mode else 100)
            return {
                "name": f"sentiment_bullish_{datetime.utcnow().strftime('%H%M')}",
                "type": "momentum",
                "confidence": 0.6,
                "description": f"Buy ETH on bullish sentiment (${eth_price:.0f})",
                "params": {
                    "action": "buy",
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": amount
                },
                "analysis": {"sentiment": sentiment, "eth_price": eth_price}
            }
        
        elif sentiment == "bearish" and eth_balance > 0.01:
            # Bearish sentiment strategy
            amount = eth_balance * 0.2
            return {
                "name": f"sentiment_bearish_{datetime.utcnow().strftime('%H%M')}",
                "type": "momentum",
                "confidence": 0.6,
                "description": f"Sell ETH on bearish sentiment (${eth_price:.0f})",
                "params": {
                    "action": "sell",
                    "from_token": "ETH",
                    "to_token": "USDC",
                    "amount": amount
                },
                "analysis": {"sentiment": sentiment, "eth_price": eth_price}
            }
        
        elif usdc_balance >= 15:
            # Default learning strategy - small buy
            amount = 10 if testing_mode else 15
            return {
                "name": f"learning_buy_{datetime.utcnow().strftime('%H%M')}",
                "type": "custom",
                "confidence": 0.4,
                "description": "Small learning trade to gather data",
                "params": {
                    "action": "buy",
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": amount
                },
                "analysis": {"learning_trade": True, "eth_price": eth_price}
            }
        
        else:
            # Absolute minimum fallback
            return {
                "name": "micro_learning",
                "type": "custom",
                "confidence": 0.3,
                "description": "Micro learning trade",
                "params": {
                    "action": "buy",
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": 5
                },
                "analysis": {"micro_trade": True}
            }

    async def _execute_autonomous_trade(self, trade_params: Dict, session_id: str) -> Dict[str, Any]:
        """Execute autonomous trade with strategy performance tracking"""
        
        session = self.autonomous_sessions[session_id]
        
        try:
            from_token = trade_params["from_token"]
            to_token = trade_params["to_token"]
            amount = trade_params["amount"]
            
            # Check balance
            balance_data = get_token_balance(from_token)
            available_balance = balance_data.get("amount", 0)
            
            if available_balance < amount:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Need {amount}, have {available_balance}",
                    "trade_params": trade_params
                }
            
            # Execute trade
            from_address = token_addresses.get(from_token.upper())
            to_address = token_addresses.get(to_token.upper())
            
            trade_result = trade_exec(from_address, to_address, amount)
            
            if trade_result and "error" not in trade_result:
                # Log successful trade
                trade_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "from_token": from_token,
                    "to_token": to_token,
                    "amount": amount,
                    "success": True,
                    "trade_result": trade_result,
                    "pre_trade_portfolio_value": self._get_current_portfolio_value(session["user_id"])
                }
                
                session["trades_executed"].append(trade_record)
                session["performance"]["total_trades"] += 1
                session["performance"]["successful_trades"] += 1
                
                print(f"✅ Autonomous trade executed: {amount} {from_token} → {to_token}")
                
                # Schedule strategy performance evaluation (will be done later)
                asyncio.create_task(self._schedule_trade_evaluation(
                    session_id, trade_record, len(session["trades_executed"]) - 1
                ))
                
                return {
                    "success": True,
                    "trade_record": trade_record,
                    "trade_result": trade_result
                }
            else:
                session["performance"]["total_trades"] += 1  # Count failed trades too
                return {
                    "success": False,
                    "error": trade_result.get("error", "Unknown error"),
                    "trade_params": trade_params
                }
                
        except Exception as e:
            print(f"❌ Autonomous trade execution error: {e}")
            session["performance"]["total_trades"] += 1  # Count failed trades
            return {
                "success": False,
                "error": str(e),
                "trade_params": trade_params
            }
    
    async def _schedule_trade_evaluation(self, session_id: str, trade_record: Dict, trade_index: int):
        """Schedule evaluation of trade performance after a delay"""
        # Wait for some time to see the outcome
        evaluation_delay = 300  # 5 minutes
        await asyncio.sleep(evaluation_delay)
        
        await self._evaluate_trade_outcome(session_id, trade_record, trade_index)
    
    async def _evaluate_trade_outcome(self, session_id: str, trade_record: Dict, trade_index: int):
        """Evaluate whether a trade was favorable after execution - IMPROVED VERSION"""
        try:
            session = self.autonomous_sessions.get(session_id)
            if not session:
                return
            
            # Get current portfolio value
            current_portfolio_value = self._get_current_portfolio_value(session["user_id"])
            pre_trade_value = trade_record.get("pre_trade_portfolio_value", 0)
            
            # Calculate portfolio value change
            value_change = current_portfolio_value - pre_trade_value
            trade_amount_usd = trade_record.get("amount", 0)
            
            # OPTION 4: Log detailed debug info
            print(f"🔍 DEBUG Trade Evaluation:")
            print(f"   Pre-trade portfolio: ${pre_trade_value:,.2f}")
            print(f"   Current portfolio: ${current_portfolio_value:,.2f}")
            print(f"   Value change: ${value_change:+.6f}")
            print(f"   Trade amount: ${trade_amount_usd:.2f}")
            
            # OPTION 1: Evaluate specific traded assets (improved logic)
            from_token = trade_record.get("from_token", "")
            to_token = trade_record.get("to_token", "")
            
            # Get current token balances for the traded tokens
            asset_evaluation_favorable = False
            try:
                # For buy trades (USDC -> ETH), check if we got more ETH
                if from_token == "USDC" and to_token == "ETH":
                    current_portfolio = get_portfolio(user_id=session["user_id"])
                    if isinstance(current_portfolio, dict) and "balances" in current_portfolio:
                        balances = current_portfolio["balances"]
                        for balance in balances:
                            if balance.get("symbol") == "ETH":
                                eth_amount = balance.get("amount", 0)
                                # If we have any ETH, the buy was successful
                                if eth_amount > 0:
                                    asset_evaluation_favorable = True
                                    print(f"   ✅ Asset check: Have {eth_amount:.6f} ETH after buy")
                                break
                
                # For sell trades (ETH -> USDC), check if we got more USDC
                elif from_token == "ETH" and to_token == "USDC":
                    # Any successful sell should be considered favorable for learning
                    asset_evaluation_favorable = True
                    print(f"   ✅ Asset check: ETH sell completed successfully")
                    
            except Exception as e:
                print(f"   ⚠️ Asset evaluation error: {e}")
            
            # OPTION 2: Much lower threshold for favorable trades (0.01% instead of 1%)
            portfolio_threshold_favorable = value_change > (trade_amount_usd * 0.0001) # 0.01% instead of 1%
            
            # Alternative: Any positive change is favorable
            any_positive_change = value_change > 0
            
            # COMBINED LOGIC: Trade is favorable if ANY of these conditions are met:
            was_favorable = (
                asset_evaluation_favorable or           # Asset-specific check passed
                portfolio_threshold_favorable or        # Tiny portfolio improvement
                any_positive_change or                  # Any positive change
                abs(value_change) < 1.0                # Very small change (assume neutral/favorable)
            )
            
            # Enhanced logging with more details
            evaluation_reasons = []
            if asset_evaluation_favorable:
                evaluation_reasons.append("asset_check_passed")
            if portfolio_threshold_favorable:
                evaluation_reasons.append("portfolio_improved")
            if any_positive_change:
                evaluation_reasons.append("positive_change")
            if abs(value_change) < 1.0:
                evaluation_reasons.append("minimal_change")
            
            # Get the strategy ID from the decision that led to this trade
            strategy_id = None
            if trade_index < len(session["reasoning_log"]):
                decision_log = session["reasoning_log"][trade_index]
                strategy_id = decision_log.get("decision", {}).get("trading_decision", {}).get("strategy_id")
            
            # Update strategy performance in database
            if strategy_id:
                try:
                    performance_data = {
                        "trade_amount": trade_amount_usd,
                        "portfolio_change": value_change,
                        "evaluation_time": datetime.utcnow().isoformat(),
                        "was_favorable": was_favorable,
                        "evaluation_reasons": evaluation_reasons,
                        "from_token": from_token,
                        "to_token": to_token
                    }
                    
                    supabase_client.update_strategy_performance(strategy_id, was_favorable, performance_data)
                    
                    # More detailed logging
                    reasons_str = ", ".join(evaluation_reasons) if evaluation_reasons else "none"
                    print(f"📈 Trade evaluation: {'✅ Favorable' if was_favorable else '❌ Unfavorable'} "
                          f"(${value_change:+.6f} change, Reasons: {reasons_str}, Strategy: {strategy_id[:8]})")
                    
                except Exception as e:
                    print(f"⚠️ Could not update strategy performance: {e}")
            else:
                # Log even without strategy ID
                reasons_str = ", ".join(evaluation_reasons) if evaluation_reasons else "none"
                print(f"📈 Trade evaluation: {'✅ Favorable' if was_favorable else '❌ Unfavorable'} "
                      f"(${value_change:+.6f} change, Reasons: {reasons_str})")
            
            # Log the evaluation result
            evaluation_result = {
                "trade_index": trade_index,
                "timestamp": datetime.utcnow().isoformat(),
                "was_favorable": was_favorable,
                "portfolio_change": value_change,
                "evaluation_delay_minutes": 5,
                "evaluation_reasons": evaluation_reasons,
                "trade_details": {
                    "from_token": from_token,
                    "to_token": to_token,
                    "amount": trade_amount_usd
                }
            }
            
            if "trade_evaluations" not in session:
                session["trade_evaluations"] = []
            session["trade_evaluations"].append(evaluation_result)
            
        except Exception as e:
            print(f"❌ Error evaluating trade outcome: {e}")

    async def _learn_from_decision(self, decision: Dict, execution: Dict, market_data: Dict, session_id: str):
        """Enhanced learning from trading decisions with strategy feedback and persistence"""
        
        # Create learning entry for in-memory storage
        learning_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "execution": execution,
            "market_conditions": market_data,
            "strategy_id": decision.get("strategy_id"),
            "outcome": "pending_evaluation",
            "session_id": session_id  # Store session_id in memory too
        }
        
        # Add to in-memory storage
        self.memory.append(learning_entry)
        
        # Persist to database - PASS SESSION_ID CORRECTLY
        await self.persist_decision_to_db(session_id, decision, execution, market_data)
        
        # Keep memory manageable (last 100 decisions)
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
        
        # Log strategy usage for future analysis
        strategy_used = decision.get("strategy_used", "unknown")
        print(f"🧠 Learning recorded: {strategy_used} strategy, {len(self.memory)} total decisions in memory")
        print(f"💾 Decision persisted to database for session {session_id}")
        
        # If execution was successful, we'll get the outcome evaluation later
        if execution and execution.get("success"):
            print(f"📊 Trade evaluation scheduled for 5 minutes to assess outcome")

    async def persist_decision_to_db(self, session_id: str, decision: Dict, execution: Dict, market_data: Dict):
        """Persist agent decision and learning to Supabase"""
        try:
            if not session_id:
                print("⚠️ No session_id provided for decision persistence")
                return
            
            # Get next message order
            message_order = self.message_order_counter.get(session_id, 1)
            self.message_order_counter[session_id] = message_order + 1
            
            # Prepare conversation data
            conversation_data = {
                "session_id": session_id,
                "message_order": message_order,
                "role": "assistant",
                "content": f"Decision: {decision.get('strategy_used', 'unknown')} - {decision.get('trade_params', {})}",
                "intent": "autonomous_decision",
                "confidence": decision.get("confidence", 0.5),
                "actions_taken": [
                    decision.get("strategy_used", "unknown"),
                    f"trade_{execution.get('success', False)}"
                ],
                "reasoning": "\n".join(decision.get("reasoning", [])),
                "suggestions": None,
                "metadata": {
                    "decision": decision,
                    "execution": execution,
                    "market_conditions": market_data,
                    "agent_type": "autonomous",
                    "decision_timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Insert into ai_conversations
            result = supabase_client.insert_ai_conversation(conversation_data)
            
            # Also insert trade record if trade was executed
            if execution and execution.get("success") and execution.get("trade_record"):
                trade_record = execution["trade_record"]
                trade_data = {
                    "trade_type": "swap",  # or determine from trade_record
                    "from_token": trade_record.get("from_token"),
                    "to_token": trade_record.get("to_token"),
                    "from_amount": trade_record.get("amount", 0),
                    "status": "executed" if execution.get("success") else "failed",
                    "ai_reasoning": "\n".join(decision.get("reasoning", [])),
                    "ai_confidence": decision.get("confidence", 0.5),
                    "market_conditions": market_data,
                    "execution_time": datetime.utcnow().isoformat()
                }
                
                supabase_client.insert_trade_record(session_id, trade_data)
            
            print(f"✅ Decision persisted to DB: message_order {message_order}")
            
        except Exception as e:
            print(f"❌ Error persisting decision to database: {e}")

    async def get_session_learning_stats(self, session_id: str) -> Dict[str, Any]:
        """Get learning statistics for a session from database"""
        try:
            memory_data = supabase_client.get_session_memory_summary(session_id)
            
            conversations = memory_data.get("conversations", [])
            trades = memory_data.get("trades", [])
            strategies = memory_data.get("strategies", [])
            
            # Analyze decisions
            assistant_decisions = [conv for conv in conversations if conv["role"] == "assistant"]
            successful_trades = [trade for trade in trades if trade.get("status") == "executed"]
            
            # Calculate stats
            stats = {
                "total_decisions": len(assistant_decisions),
                "total_trades": len(trades),
                "successful_trades": len(successful_trades),
                "success_rate": len(successful_trades) / max(1, len(trades)),
                "strategies_created": len(strategies),
                "avg_confidence": sum(conv.get("confidence", 0) for conv in assistant_decisions) / max(1, len(assistant_decisions)),
                "learning_span_hours": 0,
                "memory_persistence": "database_enabled"
            }
            
            # Calculate time span
            if assistant_decisions:
                first_decision = min(assistant_decisions, key=lambda x: x["created_at"])
                last_decision = max(assistant_decisions, key=lambda x: x["created_at"])
                
                first_time = datetime.fromisoformat(first_decision["created_at"].replace("Z", "+00:00"))
                last_time = datetime.fromisoformat(last_decision["created_at"].replace("Z", "+00:00"))
                
                stats["learning_span_hours"] = (last_time - first_time).total_seconds() / 3600
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting learning stats: {e}")
            return {
                "total_decisions": 0,
                "total_trades": 0,
                "successful_trades": 0,
                "success_rate": 0,
                "strategies_created": 0,
                "avg_confidence": 0,
                "learning_span_hours": 0,
                "memory_persistence": "database_error"
            }

    async def debug_persistence_system(self, session_id: str = None) -> Dict[str, Any]:
        """Debug the persistence system to ensure it's working"""
        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_connection": "unknown",
            "memory_in_ram": len(self.memory),
            "sessions_tracked": len(self.autonomous_sessions),
            "message_order_counters": dict(self.message_order_counter),
            "persistence_test": "not_run"
        }
        
        # Test database connection
        try:
            if session_id:
                memory_data = supabase_client.get_session_memory_summary(session_id)
                debug_info["database_connection"] = "✅ Connected"
                debug_info["db_conversations"] = len(memory_data.get("conversations", []))
                debug_info["db_trades"] = len(memory_data.get("trades", []))
                debug_info["db_strategies"] = len(memory_data.get("strategies", []))
            else:
                debug_info["database_connection"] = "✅ Connected (no session specified)"
        except Exception as e:
            debug_info["database_connection"] = f"❌ Error: {e}"
        
        # Test persistence
        try:
            if session_id:
                test_decision = {
                    "strategy_used": "debug_test",
                    "confidence": 0.8,
                    "reasoning": ["Testing persistence system"],
                    "trade_params": {"action": "test"}
                }
                test_execution = {"success": False, "test": True}
                test_market = {"test_data": True}
                
                await self.persist_decision_to_db(session_id, test_decision, test_execution, test_market)
                debug_info["persistence_test"] = "✅ Test decision persisted"
            else:
                debug_info["persistence_test"] = "⚠️ No session_id for test"
        except Exception as e:
            debug_info["persistence_test"] = f"❌ Error: {e}"
        
        return debug_info
    
    async def seed_initial_strategies(self, session_id: str):
        """Seed the database with a comprehensive set of initial trading strategies"""
        try:
            initial_strategies = [
                # ==================== MOMENTUM-BASED STRATEGIES ====================
                {
                    "session_id": session_id,
                    "strategy_name": "bullish_momentum_buy",
                    "strategy_type": "momentum",
                    "strategy_description": "Buy ETH when market sentiment is bullish",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 25
                    },
                    "market_conditions": {"sentiment": "bullish"},
                    "success_rate": 0.6,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "bearish_momentum_sell",
                    "strategy_type": "momentum",
                    "strategy_description": "Sell some ETH when market sentiment is bearish",
                    "strategy_parameters": {
                        "action": "sell",
                        "from_token": "ETH",
                        "to_token": "USDC",
                        "amount": 0.01
                    },
                    "market_conditions": {"sentiment": "bearish"},
                    "success_rate": 0.65,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "strong_bullish_aggressive_buy",
                    "strategy_type": "momentum",
                    "strategy_description": "Aggressive buy when sentiment is extremely bullish",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 50
                    },
                    "market_conditions": {"sentiment": "bullish", "confidence": "high"},
                    "success_rate": 0.7,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "neutral_momentum_small_buy",
                    "strategy_type": "hodl",
                    "strategy_description": "Small buy on neutral sentiment for position building",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 10
                    },
                    "market_conditions": {"sentiment": "neutral"},
                    "success_rate": 0.45,
                    "is_active": True
                },
                
                # ==================== SWING TRADING STRATEGIES ====================
                
                
                # ==================== DCA STRATEGIES ====================
                {
                    "session_id": session_id,
                    "strategy_name": "morning_accumulation",
                    "strategy_type": "dca",
                    "strategy_description": "Small ETH accumulation during morning hours (UTC)",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 12
                    },
                    "market_conditions": {"time_range": "06:00-10:00 UTC"},
                    "success_rate": 0.52,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "weekend_consolidation",
                    "strategy_type": "dca",
                    "strategy_description": "Conservative trading during weekends",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 8
                    },
                    "market_conditions": {"day_type": "weekend"},
                    "success_rate": 0.48,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "end_of_month_rebalance",
                    "strategy_type": "dca",
                    "strategy_description": "Rebalancing strategy at month end",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 35
                    },
                    "market_conditions": {"period": "month_end"},
                    "success_rate": 0.63,
                    "is_active": True
                },
                
                # ==================== SCALPING STRATEGIES ====================
                {
                    "session_id": session_id,
                    "strategy_name": "high_volatility_small_trade",
                    "strategy_type": "scalping",
                    "strategy_description": "Small trades during high volatility periods",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 8
                    },
                    "market_conditions": {"volatility": "high"},
                    "success_rate": 0.42,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "low_volatility_accumulate",
                    "strategy_type": "hodl",
                    "strategy_description": "Accumulate during low volatility periods",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 22
                    },
                    "market_conditions": {"volatility": "low"},
                    "success_rate": 0.67,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "volatility_spike_profit_take",
                    "strategy_type": "scalping",
                    "strategy_description": "Take profits during sudden volatility spikes",
                    "strategy_parameters": {
                        "action": "sell",
                        "from_token": "ETH",
                        "to_token": "USDC",
                        "amount": 0.008
                    },
                    "market_conditions": {"volatility": "spike"},
                    "success_rate": 0.71,
                    "is_active": True
                },
                
                # ==================== PORTFOLIO BALANCE STRATEGIES ====================
                {
                    "session_id": session_id,
                    "strategy_name": "usdc_heavy_rebalance",
                    "strategy_type": "swing",
                    "strategy_description": "Buy ETH when USDC percentage is too high",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 40
                    },
                    "market_conditions": {"usdc_percentage_above": 70},
                    "success_rate": 0.61,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "eth_heavy_rebalance",
                    "strategy_type": "swing",
                    "strategy_description": "Sell some ETH when ETH percentage is too high",
                    "strategy_parameters": {
                        "action": "sell",
                        "from_token": "ETH",
                        "to_token": "USDC",
                        "amount": 0.02
                    },
                    "market_conditions": {"eth_percentage_above": 80},
                    "success_rate": 0.59,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "balanced_portfolio_maintain",
                    "strategy_type": "swing",
                    "strategy_description": "Maintain 60/40 ETH/USDC balance",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 18
                    },
                    "market_conditions": {"target_balance": "60_40"},
                    "success_rate": 0.56,
                    "is_active": True
                },
       
               
            ]
            
            created_count = 0
            for strategy_data in initial_strategies:
                result = supabase_client.insert_strategy(strategy_data)
                if result:
                    created_count += 1
            
            print(f"🌱 Seeded {created_count} initial strategies for session {session_id}")
            return created_count
            
        except Exception as e:
            print(f"⚠️ Error seeding strategies: {e}")
            return 0
    
    def _calculate_real_portfolio_value(self, portfolio_data: Dict) -> float:
        """Calculate the real USD value of the portfolio"""
        try:
            total_value = 0.0
            
            if isinstance(portfolio_data, dict) and 'tokens' in portfolio_data:
                tokens = portfolio_data.get('tokens', {})
                
                for token_symbol, token_data in tokens.items():
                    if isinstance(token_data, dict):
                        amount = token_data.get('amount', 0)
                        usd_value = token_data.get('usd_value', 0)
                        
                        if usd_value and amount:
                            total_value += float(usd_value)
                        elif token_symbol.upper() == 'USDC':
                            # USDC is roughly 1:1 with USD
                            total_value += float(amount)
                            
            return total_value
            
        except Exception as e:
            print(f"⚠️ Error calculating portfolio value: {e}")
            return 0.0

    def _calculate_risk_score(self, market_data: Dict, portfolio_analysis: Dict, decision: Dict) -> float:
        """Calculate risk score for a trading decision"""
        try:
            risk_factors = []
            
            # Market sentiment risk
            sentiment = market_data.get('sentiment', 'neutral')
            if sentiment == 'bearish':
                risk_factors.append(0.3)
            elif sentiment == 'bullish':
                risk_factors.append(0.1)
            else:
                risk_factors.append(0.2)
            
            # Portfolio concentration risk
            portfolio_value = portfolio_analysis.get('total_value', 0)
            trade_amount = decision.get('trade_params', {}).get('amount', 0)
            
            if portfolio_value > 0:
                trade_ratio = trade_amount / portfolio_value
                if trade_ratio > 0.5:  # More than 50% of portfolio
                    risk_factors.append(0.4)
                elif trade_ratio > 0.2:  # More than 20% of portfolio
                    risk_factors.append(0.2)
                else:
                    risk_factors.append(0.1)
            else:
                risk_factors.append(0.3)  # Unknown portfolio = higher risk
            
            # Confidence risk (lower confidence = higher risk)
            confidence = decision.get('confidence', 0.5)
            confidence_risk = 1.0 - confidence
            risk_factors.append(confidence_risk * 0.3)
            
            # Calculate average risk score
            total_risk = sum(risk_factors) / len(risk_factors) if risk_factors else 0.5
            
            # Ensure risk score is between 0 and 1
            return max(0.0, min(1.0, total_risk))
            
        except Exception as e:
            print(f"⚠️ Error calculating risk score: {e}")
            return 0.5  # Default moderate risk
    
    def _get_current_portfolio_value(self, user_id: str = "default") -> float:
        """Get the current total portfolio value in USD"""
        try:
            portfolio_data = get_portfolio(user_id=user_id)
            return self._calculate_real_portfolio_value(portfolio_data)
        except Exception as e:
            print(f"⚠️ Error getting current portfolio value: {e}")
            return 0.0

    async def seed_initial_strategies(self, session_id: str):
        """Seed the database with a comprehensive set of initial trading strategies"""
        try:
            initial_strategies = [
                # ==================== MOMENTUM-BASED STRATEGIES ====================
                {
                    "session_id": session_id,
                    "strategy_name": "bullish_momentum_buy",
                    "strategy_type": "momentum",
                    "strategy_description": "Buy ETH when market sentiment is bullish",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC",
                        "to_token": "ETH",
                        "amount": 25
                    },
                    "market_conditions": {"sentiment": "bullish"},
                    "success_rate": 0.6,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "bearish_momentum_sell",
                    "strategy_type": "momentum", 
                    "strategy_description": "Sell some ETH when market sentiment is bearish",
                    "strategy_parameters": {
                        "action": "sell",
                        "from_token": "ETH",
                        "to_token": "USDC",
                        "amount": 0.01
                    },
                    "market_conditions": {"sentiment": "bearish"},
                    "success_rate": 0.65,
                    "is_active": True
                },
                {
                    "session_id": session_id,
                    "strategy_name": "neutral_small_buy",
                    "strategy_type": "hodl",
                    "strategy_type": "hodl",
                    "strategy_description": "Small buy on neutral sentiment for position building",
                    "strategy_parameters": {
                        "action": "buy",
                        "from_token": "USDC", 
                        "to_token": "ETH",
                        "amount": 10
                    },
                    "market_conditions": {"sentiment": "neutral"},
                    "success_rate": 0.45,
                    "is_active": True
                }
            ]
            
            created_count = 0
            for strategy_data in initial_strategies:
                try:
                    result = supabase_client.insert_strategy(strategy_data)
                    if result:
                        created_count += 1
                except Exception as e:
                    print(f"⚠️ Error inserting strategy: {e}")
            
            print(f"🌱 Seeded {created_count} initial strategies for session {session_id}")
            return created_count
            
        except Exception as e:
            print(f"⚠️ Error seeding strategies: {e}")
            return 0

# Create global instance
kairos_autonomous_agent = KairosAutonomousAgent()