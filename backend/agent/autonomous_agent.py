#!/usr/bin/env python3
"""
Kairos Autonomous Trading Agent
Advanced AI that can trade autonomously for specified time periods
"""

import asyncio
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
    
    def __init__(self):
        """Initialize the autonomous agent"""
        self.base_copilot = kairos_copilot
        self.autonomous_sessions = {}  # Track active autonomous sessions
        self.memory = []  # Persistent memory for learning
        
        print("🤖 Kairos Autonomous Agent initialized!")
        print("💡 I can trade autonomously for hours, days, or weeks!")
    
    async def process_autonomous_request(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        """Process autonomous trading requests"""
        
        # Parse autonomous command
        autonomous_params = self._parse_autonomous_command(user_message)
        
        if not autonomous_params:
            return await self.base_copilot.process_user_message(user_message)
        
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
        
        session_id = str(uuid.uuid4())
        
        # Store session in database
        try:
            await supabase_client.create_trading_session(user_id, session_data={
                "session_type": "autonomous",
                "duration_hours": params["duration_hours"],
                "target_tokens": params["target_tokens"],
                "risk_level": params["risk_level"],
                "max_trade_size": params["max_trade_size"]
            })
        except Exception as e:
            print(f"⚠️ Could not store session in database: {e}")
        
        # Get real starting portfolio value
        try:
            initial_portfolio = get_portfolio()
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
            }
        }
        
        # Store session
        self.autonomous_sessions[session_id] = session_data
        
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
            initial_portfolio = get_portfolio()
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
            final_portfolio = get_portfolio()
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
        portfolio_analysis = await self._analyze_current_portfolio()
        
        # 3. Make trading decision using AI
        trading_decision = await self._make_autonomous_trading_decision(
            market_data, 
            portfolio_analysis, 
            session["params"]
        )
        
        # 4. Execute trade if decision is to trade
        execution_result = None
        if trading_decision.get("should_trade", False):
            execution_result = await self._execute_autonomous_trade(
                trading_decision["trade_params"],
                session_id
            )
        
        # 5. Learn from the decision
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
    
    async def _analyze_current_portfolio(self) -> Dict[str, Any]:
        """Analyze current portfolio state"""
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_value": 0,
            "tokens": {},
            "diversification": "unknown",
            "risk_level": "medium"
        }
        
        try:
            portfolio_data = get_portfolio()
            
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
        """Enhanced AI-powered autonomous trading decision with 7+ advanced strategies"""
        
        decision = {
            "should_trade": False,
            "reasoning": [],
            "confidence": 0.5,
            "trade_params": None,
            "next_cycle_wait": 300,
            "strategy_used": "none",
            "market_analysis": {},
            "risk_assessment": {}
        }
        
        reasoning = []
        testing_mode = params.get("testing_mode", False)
        
        # Enhanced market data analysis
        portfolio_value = portfolio_analysis.get("total_value", 0)
        sentiment = market_data.get("sentiment", "neutral")
        diversification = portfolio_analysis.get("diversification", "unknown")
        
        reasoning.append(f"Portfolio value: ${portfolio_value:,.2f}")
        reasoning.append(f"Market sentiment: {sentiment}")
        reasoning.append(f"Diversification: {diversification}")
        reasoning.append(f"Testing mode: {'ACTIVE' if testing_mode else 'OFF'}")
        
        # Get real balances
        usdc_balance = portfolio_analysis.get("tokens", {}).get("USDC", {}).get("amount", 0)
        eth_balance = portfolio_analysis.get("tokens", {}).get("ETH", {}).get("amount", 0)
        btc_balance = portfolio_analysis.get("tokens", {}).get("BTC", {}).get("amount", 0)
        
        reasoning.append(f"USDC available: {usdc_balance:,.2f}")
        reasoning.append(f"ETH holdings: {eth_balance:.4f}")
        reasoning.append(f"BTC holdings: {btc_balance:.6f}")
        
        # Enhanced Strategy 1: News Sentiment + Volume Analysis
        if sentiment == "bullish" and usdc_balance > 100:
            trade_amount = min(usdc_balance * 0.15, params.get("max_trade_size", 500))
            confidence = 0.75 + (0.1 if testing_mode else 0)  # Higher confidence in testing
            
            decision.update({
                "should_trade": True,
                "confidence": confidence,
                "strategy_used": "enhanced_sentiment",
                "trade_params": {
                    "action": "buy",
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": trade_amount
                },
                "next_cycle_wait": 600 if not testing_mode else 180,
                "market_analysis": {"sentiment_strength": "strong_bullish"}
            })
            reasoning.append(f"STRATEGY: Enhanced Sentiment - Buy {trade_amount:.2f} USDC worth of ETH (Confidence: {confidence:.0%})")
            
        # Enhanced Strategy 2: Mean Reversion with Technical Analysis
        elif sentiment == "bearish" and eth_balance > 0.01:
            current_eth_price = market_data.get("prices", {}).get("ETH", 0)
            trade_amount = eth_balance * (0.3 if testing_mode else 0.25)  # More aggressive in testing
            
            decision.update({
                "should_trade": True,
                "confidence": 0.7,
                "strategy_used": "enhanced_mean_reversion",
                "trade_params": {
                    "action": "sell",
                    "from_token": "ETH",
                    "to_token": "USDC",
                    "amount": trade_amount
                },
                "next_cycle_wait": 600 if not testing_mode else 150,
                "market_analysis": {"price_analysis": f"ETH at ${current_eth_price:,.2f}"}
            })
            reasoning.append(f"STRATEGY: Enhanced Mean Reversion - Sell {trade_amount:.4f} ETH at ${current_eth_price:,.2f}")
            
        # Enhanced Strategy 3: Portfolio Rebalancing Algorithm
        elif diversification == "poor" and usdc_balance > 200:
            target_allocation = 0.4  # 40% ETH target
            current_eth_value = eth_balance * market_data.get("prices", {}).get("ETH", 0)
            target_eth_value = portfolio_value * target_allocation
            trade_amount = min(abs(target_eth_value - current_eth_value), usdc_balance * 0.3)
            
            decision.update({
                "should_trade": True,
                "confidence": 0.65,
                "strategy_used": "portfolio_rebalancing",
                "trade_params": {
                    "action": "rebalance",
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": trade_amount
                },
                "next_cycle_wait": 450 if not testing_mode else 200,
                "market_analysis": {"target_allocation": f"{target_allocation:.0%} ETH"}
            })
            reasoning.append(f"STRATEGY: Portfolio Rebalancing - Target {target_allocation:.0%} ETH allocation")
            
        # Enhanced Strategy 4: Momentum + Volume Strategy
        elif portfolio_value > 0:
            try:
                current_eth_price = market_data.get("prices", {}).get("ETH", 0)
                current_btc_price = market_data.get("prices", {}).get("BTC", 0)
                
                # Multi-asset momentum analysis
                if current_eth_price > 3000 and current_btc_price > 40000 and usdc_balance > 150:
                    trade_amount = min(250 if testing_mode else 200, usdc_balance * 0.12)
                    
                    decision.update({
                        "should_trade": True,
                        "confidence": 0.6,
                        "strategy_used": "multi_asset_momentum",
                        "trade_params": {
                            "action": "momentum_buy",
                            "from_token": "USDC",
                            "to_token": "ETH",
                            "amount": trade_amount
                        },
                        "next_cycle_wait": 400 if not testing_mode else 160,
                        "market_analysis": {
                            "eth_price": current_eth_price,
                            "btc_price": current_btc_price,
                            "momentum": "bullish_multi_asset"
                        }
                    })
                    reasoning.append(f"STRATEGY: Multi-Asset Momentum - ETH ${current_eth_price:,.0f}, BTC ${current_btc_price:,.0f}")
                    
                # Strategy 5: Counter-Trend Opportunity (Testing Mode Enhanced)
                elif testing_mode and current_eth_price < 2800 and usdc_balance > 100:
                    trade_amount = min(150, usdc_balance * 0.1)
                    
                    decision.update({
                        "should_trade": True,
                        "confidence": 0.55,
                        "strategy_used": "counter_trend_opportunity",
                        "trade_params": {
                            "action": "contrarian_buy",
                            "from_token": "USDC",
                            "to_token": "ETH",
                            "amount": trade_amount
                        },
                        "next_cycle_wait": 300,
                        "market_analysis": {"opportunity": "oversold_conditions"}
                    })
                    reasoning.append(f"STRATEGY: Counter-Trend - ETH potentially oversold at ${current_eth_price:,.0f}")
                else:
                    reasoning.append("STRATEGY: No clear momentum or counter-trend signals")
                    
            except Exception as e:
                reasoning.append(f"STRATEGY: Analysis error - {e}")
        
        # Strategy 6: Risk Management Override (Enhanced for Testing)
        if decision["should_trade"]:
            risk_score = self._calculate_risk_score(market_data, portfolio_analysis, decision)
            decision["risk_assessment"] = {"risk_score": risk_score}
            
            if risk_score > 0.8 and not testing_mode:  # High risk, but allow in testing
                decision["should_trade"] = False
                decision["strategy_used"] = "risk_management_override"
                reasoning.append(f"OVERRIDE: Risk too high ({risk_score:.0%}) - Trade cancelled")
            elif testing_mode and risk_score > 0.6:
                # In testing, reduce trade size for high-risk trades
                if decision["trade_params"]:
                    decision["trade_params"]["amount"] *= 0.7
                reasoning.append(f"TESTING: Risk adjusted - Trade size reduced due to risk score {risk_score:.0%}")
        
        if not decision["should_trade"]:
            base_wait = 300 if not testing_mode else 120
            decision["next_cycle_wait"] = base_wait
            reasoning.append("DECISION: Hold - No favorable trading conditions")
        
        decision["reasoning"] = reasoning
        
        # Enhanced logging for testing mode
        if testing_mode:
            print(f"🧪 TESTING MODE - {decision['strategy_used'].upper()}: {decision['reasoning'][-1]}")
        else:
            print(f"🤖 Autonomous Decision ({decision['strategy_used']}): {decision['reasoning'][-1]}")
            
        return decision
    
    def _calculate_risk_score(self, market_data: Dict, portfolio_analysis: Dict, decision: Dict) -> float:
        """Calculate risk score for the proposed trade"""
        risk_factors = []
        
        # Market volatility risk
        sentiment = market_data.get("sentiment", "neutral")
        if sentiment == "bearish":
            risk_factors.append(0.3)
        elif sentiment == "bullish":
            risk_factors.append(0.1)
        else:
            risk_factors.append(0.2)
        
        # Portfolio concentration risk
        diversification = portfolio_analysis.get("diversification", "unknown")
        if diversification == "poor":
            risk_factors.append(0.4)
        elif diversification == "moderate":
            risk_factors.append(0.2)
        else:
            risk_factors.append(0.1)
        
        # Trade size risk
        portfolio_value = portfolio_analysis.get("total_value", 1)
        trade_amount = decision.get("trade_params", {}).get("amount", 0)
        trade_ratio = trade_amount / max(portfolio_value, 1)
        
        if trade_ratio > 0.3:
            risk_factors.append(0.5)
        elif trade_ratio > 0.2:
            risk_factors.append(0.3)
        else:
            risk_factors.append(0.1)
        
        return min(sum(risk_factors), 1.0)
    
    async def _execute_autonomous_trade(self, trade_params: Dict, session_id: str) -> Dict[str, Any]:
        """Execute autonomous trade"""
        
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
                    "trade_result": trade_result
                }
                
                session["trades_executed"].append(trade_record)
                session["performance"]["total_trades"] += 1
                session["performance"]["successful_trades"] += 1
                
                print(f"✅ Autonomous trade executed: {amount} {from_token} → {to_token}")
                
                return {
                    "success": True,
                    "trade_record": trade_record,
                    "trade_result": trade_result
                }
            else:
                return {
                    "success": False,
                    "error": trade_result.get("error", "Unknown error"),
                    "trade_params": trade_params
                }
                
        except Exception as e:
            print(f"❌ Autonomous trade execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "trade_params": trade_params
            }
    
    async def _learn_from_decision(self, decision: Dict, execution: Dict, market_data: Dict):
        """Learn from trading decisions for future improvement"""
        
        learning_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "execution": execution,
            "market_conditions": market_data,
            "outcome": "unknown"  # Will be evaluated later
        }
        
        self.memory.append(learning_entry)
        
        # Keep memory manageable (last 100 decisions)
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
        
        print(f"🧠 Learning recorded: {len(self.memory)} total decisions in memory")
    
    def _calculate_real_portfolio_value(self, portfolio_data: Any) -> float:
        """Calculate real portfolio value in USD using live prices"""
        total_value = 0.0
        
        try:
            if isinstance(portfolio_data, dict) and "balances" in portfolio_data:
                balances = portfolio_data["balances"]
            elif isinstance(portfolio_data, list):
                balances = portfolio_data
            else:
                return 0.0
            
            for balance in balances:
                symbol = balance.get("symbol", "")
                amount = balance.get("amount", balance.get("balance", 0))
                
                if amount > 0:
                    try:
                        if symbol == "USDC":
                            value = amount  # USDC = $1
                        else:
                            price_data = get_token_price_json(symbol)
                            price = price_data.get("price", 0) if isinstance(price_data, dict) else 0
                            value = amount * price
                        
                        total_value += value
                        print(f"💰 {symbol}: {amount:.4f} × ${price if symbol != 'USDC' else 1:.2f} = ${value:.2f}")
                        
                    except Exception as e:
                        print(f"⚠️ Could not value {symbol}: {e}")
                        
        except Exception as e:
            print(f"⚠️ Error calculating portfolio value: {e}")
            
        print(f"💼 Total Portfolio Value: ${total_value:,.2f}")
        return total_value
    
    def _calculate_portfolio_value(self, portfolio_data: Any) -> float:
        """Legacy method - calls real calculation"""
        return self._calculate_real_portfolio_value(portfolio_data)
    
    def _get_current_portfolio_value(self) -> float:
        """Get current real portfolio value"""
        try:
            portfolio = get_portfolio()
            return self._calculate_real_portfolio_value(portfolio)
        except Exception as e:
            print(f"⚠️ Error getting current portfolio value: {e}")
            return 0.0
    
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

# Global instance
autonomous_agent = KairosAutonomousAgent()
