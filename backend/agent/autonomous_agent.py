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
            
        except Exception as e:
            print(f"⚠️ Could not store session in database: {e}")
            # Fallback to local session ID if database fails
            session_id = str(uuid.uuid4())
        
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
        
        # 5. Learn from the decision (enhanced with strategy tracking)
        await self._learn_from_decision(trading_decision, execution_result, market_data)
        
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
        """Evaluate whether a trade was favorable after execution"""
        try:
            session = self.autonomous_sessions.get(session_id)
            if not session:
                return
            
            # Get current portfolio value
            current_portfolio_value = self._get_current_portfolio_value(session["user_id"])
            pre_trade_value = trade_record.get("pre_trade_portfolio_value", 0)
            
            # Calculate if the trade was beneficial
            value_change = current_portfolio_value - pre_trade_value
            trade_amount_usd = trade_record.get("amount", 0)
            
            # Determine if the trade was favorable
            # Positive change greater than trade amount suggests success
            was_favorable = value_change > (trade_amount_usd * 0.01)  # Must gain more than 1% to be considered favorable
            
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
                        "was_favorable": was_favorable
                    }
                    
                    supabase_client.update_strategy_performance(strategy_id, was_favorable, performance_data)
                    
                    print(f"📈 Trade evaluation: {'✅ Favorable' if was_favorable else '❌ Unfavorable'} "
                          f"(${value_change:+.2f} change, Strategy: {strategy_id[:8]})")
                    
                except Exception as e:
                    print(f"⚠️ Could not update strategy performance: {e}")
            
            # Log the evaluation result
            evaluation_result = {
                "trade_index": trade_index,
                "timestamp": datetime.utcnow().isoformat(),
                "was_favorable": was_favorable,
                "portfolio_change": value_change,
                "evaluation_delay_minutes": 5
            }
            
            if "trade_evaluations" not in session:
                session["trade_evaluations"] = []
            session["trade_evaluations"].append(evaluation_result)
            
        except Exception as e:
            print(f"❌ Error evaluating trade outcome: {e}")

    async def _learn_from_decision(self, decision: Dict, execution: Dict, market_data: Dict):
        """Enhanced learning from trading decisions with strategy feedback"""
        
        learning_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "execution": execution,
            "market_conditions": market_data,
            "strategy_id": decision.get("strategy_id"),
            "outcome": "pending_evaluation"  # Will be updated by trade evaluation
        }
        
        self.memory.append(learning_entry)
        
        # Keep memory manageable (last 100 decisions)
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
        
        # Log strategy usage for future analysis
        strategy_used = decision.get("strategy_used", "unknown")
        print(f"🧠 Learning recorded: {strategy_used} strategy, {len(self.memory)} total decisions in memory")
        
        # If execution was successful, we'll get the outcome evaluation later
        if execution and execution.get("success"):
            print(f"📊 Trade evaluation scheduled for 5 minutes to assess outcome")

    async def _generate_session_pdf_report(self, session_id: str) -> str:
        """Generate comprehensive PDF report of autonomous trading session"""
        
        session = self.autonomous_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Create filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"kairos_autonomous_report_{session_id[:8]}_{timestamp}.pdf"
            filepath = f"/tmp/{filename}"
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("🤖 Kairos Autonomous Trading Report", title_style))
            story.append(Spacer(1, 20))
            
            # Session Overview
            story.append(Paragraph("📊 Session Overview", styles['Heading2']))
            
            session_data = [
                ["Session ID:", session_id],
                ["Duration:", f"{session['params']['duration_text']}"],
                ["Status:", session['status'].title()],
                ["Start Time:", session['params']['start_time']],
                ["End Time:", session.get('end_time_actual', 'N/A')],
                ["User ID:", session['user_id']],
            ]
            
            session_table = Table(session_data, colWidths=[2*inch, 4*inch])
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ]))
            
            story.append(session_table)
            story.append(Spacer(1, 20))
            
            # Performance Summary
            story.append(Paragraph("💰 Performance Summary", styles['Heading2']))
            
            perf = session['performance']
            performance_data = [
                ["Starting Portfolio Value:", f"${perf['start_portfolio_value']:,.2f}"],
                ["Final Portfolio Value:", f"${perf['current_portfolio_value']:,.2f}"],
                ["Total P&L:", f"${perf['total_profit_loss']:,.2f}"],
                ["ROI:", f"{perf.get('roi_percentage', 0):.2f}%"],
                ["Total Trades:", str(perf['total_trades'])],
                ["Successful Trades:", str(perf['successful_trades'])],
                ["Success Rate:", f"{(perf['successful_trades']/max(1,perf['total_trades'])*100):.1f}%"],
            ]
            
            perf_table = Table(performance_data, colWidths=[2.5*inch, 2*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.lightcyan),
            ]))
            
            story.append(perf_table)
            story.append(Spacer(1, 20))
            
            # Strategy Usage
            story.append(Paragraph("🎯 Strategy Analysis", styles['Heading2']))
            
            strategies = session.get('strategies', {})
            strategy_data = [["Strategy", "Times Used", "Success Rate"]]
            
            for strategy_name, stats in strategies.items():
                used = stats.get('used', 0)
                success = stats.get('success', 0)
                success_rate = f"{(success/max(1,used)*100):.1f}%" if used > 0 else "N/A"
                strategy_data.append([
                    strategy_name.replace('_', ' ').title(),
                    str(used),
                    success_rate
                ])
            
            strategy_table = Table(strategy_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            strategy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(strategy_table)
            story.append(Spacer(1, 20))
            
            # Trade History
            story.append(Paragraph("📈 Trade History", styles['Heading2']))
            
            trades = session.get('trades_executed', [])
            if trades:
                trade_data = [["Time", "Action", "From", "To", "Amount", "Status"]]
                
                for trade in trades[-10:]:  # Last 10 trades
                    timestamp = trade.get('timestamp', 'N/A')[:16]  # Format: YYYY-MM-DD HH:MM
                    action = trade.get('from_token', 'N/A') + " → " + trade.get('to_token', 'N/A')
                    amount = f"{trade.get('amount', 0):.4f}"
                    status = "✅" if trade.get('success', False) else "❌"
                    
                    trade_data.append([
                        timestamp,
                        action,
                        trade.get('from_token', 'N/A'),
                        trade.get('to_token', 'N/A'), 
                        amount,
                        status
                    ])
                
                trade_table = Table(trade_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 0.5*inch])
                trade_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(trade_table)
            else:
                story.append(Paragraph("No trades executed during this session.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Key Insights
            story.append(Paragraph("🧠 AI Insights", styles['Heading2']))
            
            insights = []
            roi = perf.get('roi_percentage', 0)
            
            if roi > 0:
                insights.append(f"• Profitable session with {roi:.2f}% return")
            elif roi < 0:
                insights.append(f"• Session resulted in {abs(roi):.2f}% loss")
            else:
                insights.append("• Break-even session")
            
            if perf['total_trades'] > 0:
                insights.append(f"• Executed {perf['total_trades']} trades with {(perf['successful_trades']/perf['total_trades']*100):.1f}% success rate")
            
            insights.append(f"• Session duration: {session['params']['duration_text']}")
            insights.append("• All trades executed with real market data and prices")
            
            for insight in insights:
                story.append(Paragraph(insight, styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph("Generated by Kairos Autonomous Trading Agent", styles['Normal']))
            story.append(Paragraph(f"Report created: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            print(f"📄 PDF report generated: {filepath}")
            return filepath
            
        except ImportError:
            # Fallback to text report if reportlab not available
            print("⚠️ ReportLab not available, generating text report")
            return await self._generate_text_report(session_id)
        
        except Exception as e:
            print(f"❌ Error generating PDF report: {e}")
            return await self._generate_text_report(session_id)
    
    async def _generate_text_report(self, session_id: str) -> str:
        """Generate text-based report as fallback"""
        
        session = self.autonomous_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"kairos_autonomous_report_{session_id[:8]}_{timestamp}.txt"
        filepath = f"/tmp/{filename}"
        
        with open(filepath, 'w') as f:
            f.write("🤖 KAIROS AUTONOMOUS TRADING REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("📊 SESSION OVERVIEW\n")
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Duration: {session['params']['duration_text']}\n")
            f.write(f"Status: {session['status'].title()}\n")
            f.write(f"Start Time: {session['params']['start_time']}\n")
            f.write(f"End Time: {session.get('end_time_actual', 'N/A')}\n\n")
            
            perf = session['performance']
            f.write("💰 PERFORMANCE SUMMARY\n")
            f.write(f"Starting Portfolio Value: ${perf['start_portfolio_value']:,.2f}\n")
            f.write(f"Final Portfolio Value: ${perf['current_portfolio_value']:,.2f}\n")
            f.write(f"Total P&L: ${perf['total_profit_loss']:,.2f}\n")
            f.write(f"ROI: {perf.get('roi_percentage', 0):.2f}%\n")
            f.write(f"Total Trades: {perf['total_trades']}\n")
            f.write(f"Successful Trades: {perf['successful_trades']}\n\n")
            
            f.write("📈 TRADE HISTORY\n")
            trades = session.get('trades_executed', [])
            if trades:
                for i, trade in enumerate(trades, 1):
                    f.write(f"{i}. {trade.get('timestamp', 'N/A')[:16]} - ")
                    f.write(f"{trade.get('from_token', 'N/A')} → {trade.get('to_token', 'N/A')} ")
                    f.write(f"({trade.get('amount', 0):.4f}) - ")
                    f.write(f"{'✅' if trade.get('success', False) else '❌'}\n")
            else:
                f.write("No trades executed.\n")
            
            f.write(f"\nReport generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
        return filepath
    
    async def get_autonomous_status(self, session_id: str = None) -> Dict[str, Any]:
        """Get status of autonomous trading sessions"""
        
        if session_id:
            session = self.autonomous_sessions.get(session_id)
            if session:
                return {
                    "session_found": True,
                    "session_data": session,
                    "status": session["status"],
                    "performance": session["performance"]
                }
            else:
                return {"session_found": False, "error": "Session not found"}
        else:
            # Return all active sessions
            active_sessions = {
                sid: session for sid, session in self.autonomous_sessions.items() 
                if session["status"] == "active"
            }
            return {
                "active_sessions": len(active_sessions),
                "sessions": active_sessions
            }
    
    def _add_activity(self, session_id: str, activity_type: str, reasoning: str, strategy: str = "", result: str = ""):
        """Add activity with unique ID to prevent React key conflicts"""
        import time
        import random
        
        if session_id in self.autonomous_sessions:
            unique_id = f"{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
            
            activity = {
                "id": unique_id,  # Add unique ID
                "timestamp": datetime.utcnow().isoformat(),
                "type": activity_type,
                "reasoning": reasoning,
                "strategy": strategy,
                "result": result
            }
            
            self.autonomous_sessions[session_id]["activities"].append(activity)
            
            # Keep only last 50 activities to prevent memory issues
            if len(self.autonomous_sessions[session_id]["activities"]) > 50:
                self.autonomous_sessions[session_id]["activities"] = \
                    self.autonomous_sessions[session_id]["activities"][-50:]
    
    async def debug_trading_system(self, session_id: str = None) -> Dict[str, Any]:
        """Debug autonomous trading system to identify issues"""
        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_connection": "unknown",
            "strategies_available": 0,
            "portfolio_access": "unknown",
            "trade_execution": "unknown",
            "current_balances": {},
            "active_sessions": len(self.autonomous_sessions)
        }
        
        # Test database connection
        try:
            if session_id:
                strategies = supabase_client.get_strategies_for_session(session_id)
                debug_info["database_connection"] = "✅ Connected"
                debug_info["strategies_available"] = len(strategies)
                debug_info["strategies_sample"] = strategies[:2] if strategies else []
            else:
                debug_info["database_connection"] = "⚠️ No session ID provided"
        except Exception as e:
            debug_info["database_connection"] = f"❌ Error: {e}"
        
        # Test portfolio access
        try:
            portfolio = get_portfolio(user_id="default")
            debug_info["portfolio_access"] = "✅ Working"
            
            if isinstance(portfolio, dict) and "balances" in portfolio:
                balances = portfolio["balances"]
            elif isinstance(portfolio, list):
                balances = portfolio
            else:
                balances = []
            
            for balance in balances[:5]:  # Show first 5 tokens
                symbol = balance.get("symbol", "Unknown")
                amount = balance.get("amount", balance.get("balance", 0))
                debug_info["current_balances"][symbol] = amount
                
        except Exception as e:
            debug_info["portfolio_access"] = f"❌ Error: {e}"
        
        # Test market data
        try:
            eth_price = get_token_price_json("ETH")
            debug_info["market_data"] = f"✅ ETH Price: ${eth_price.get('price', 'N/A')}"
        except Exception as e:
            debug_info["market_data"] = f"❌ Error: {e}"
        
        # Test trade execution (dry run)
        try:
            usdc_balance = debug_info["current_balances"].get("USDC", 0)
            if usdc_balance >= 10:
                debug_info["trade_execution"] = "✅ Ready (sufficient USDC balance)"
            else:
                debug_info["trade_execution"] = f"⚠️ Low USDC balance: {usdc_balance}"
        except Exception as e:
            debug_info["trade_execution"] = f"❌ Error: {e}"
        
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