#!/usr/bin/env python3
"""
Enhanced Kairos Trading Copilot
Advanced AI agent with conversational interaction, strategy generation, and learning
"""

import os
import json
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
import google.generativeai as genai
from datetime import datetime
import uuid

# Import existing modules
from database.supabase_client import supabase_client
from agent.vincent_agent import vincent_agent
from agent.coinpanic_api import get_crypto_news, get_trending_news
from api.portfolio import get_portfolio
from api.token_balance import get_token_balance
from api.token_price import get_token_price_json
from api.execute import trade_exec, token_addresses

class KairosTradingCopilot:
    """Advanced AI Trading Copilot with conversational interface and learning capabilities"""
    
    def __init__(self, user_id: str = "default", gemini_api_key: Optional[str] = None):
        """Initialize the Kairos Trading Copilot"""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Store user ID for dynamic API key retrieval
        self.user_id = user_id
        
        # Setup Gemini AI
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,
                top_p=0.8,
                top_k=40
            )
        )
        
        # Initialize Gemini Agent for autonomous decision making
        try:
            from agent.gemini_agent import PowerfulGeminiTradingAgent
            self.gemini_agent = PowerfulGeminiTradingAgent(user_id=self.user_id, gemini_api_key=api_key)
            print("✅ POWERFUL Gemini AI Trading Agent initialized with FULL CAPABILITIES")
        except Exception as e:
            print(f"⚠️ Could not initialize Gemini agent: {e}")
            self.gemini_agent = None
        
        # Initialize session
        self.current_session = None
        self.conversation_history = []
        self.trade_context = {}
        
        print("🚀 Kairos Trading Copilot initialized!")
        print("💡 I'm your AI trading assistant. Let's start a conversation about your trading goals.")
    
    async def start_trading_session(self, user_id: str = "default") -> str:
        """Start a new trading session"""
        try:
            self.current_session = await supabase_client.create_trading_session(user_id)
            print(f"📊 Trading session started: {self.current_session}")
            return self.current_session
        except Exception as e:
            print(f"⚠️ Session creation error: {e}")
            # Fallback to local session
            self.current_session = str(uuid.uuid4())
            return self.current_session
    
    async def process_user_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and provide intelligent response"""
        
        # Check for autonomous trading commands first
        try:
            from agent.autonomous_agent import autonomous_agent
            
            # Detect autonomous commands with better pattern matching
            message_lower = user_message.lower()
            autonomous_patterns = [
                "start trading session",
                "start the trading session", 
                "autonomous",
                "auto trade",
                r"\d+hr\s*\d+min",  # "24hr 10min"
                r"trade for \d+",   # "trade for 2 hours"
            ]
            
            is_autonomous = any(
                pattern in message_lower if not pattern.startswith('\\') 
                else re.search(pattern, message_lower) 
                for pattern in autonomous_patterns
            )
            
            if is_autonomous:
                return await autonomous_agent.process_autonomous_request(user_message)
        
        except ImportError:
            print("⚠️ Autonomous agent not available")
        
        # Check for autonomous status commands
        if any(cmd in user_message.lower() for cmd in ["status", "stop autonomous", "show reasoning", "performance report"]):
            return await self._handle_autonomous_status_commands(user_message)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Analyze intent and extract parameters
        intent_analysis = await self._analyze_intent(user_message)
        
        response_data = {
            "intent": intent_analysis["intent"],
            "confidence": intent_analysis["confidence"],
            "extracted_params": intent_analysis["params"],
            "response": "",
            "data": {},
            "actions_taken": [],
            "reasoning": "",
            "suggestions": []
        }
        
        # Handle different intents
        if intent_analysis["intent"] == "trade_request":
            response_data = await self._handle_trade_request(user_message, intent_analysis)
        elif intent_analysis["intent"] == "portfolio_inquiry":
            response_data = await self._handle_portfolio_inquiry(user_message)
        elif intent_analysis["intent"] == "market_analysis":
            response_data = await self._handle_market_analysis(user_message, intent_analysis)
        elif intent_analysis["intent"] == "strategy_discussion":
            response_data = await self._handle_strategy_discussion(user_message)
        else:
            response_data = await self._handle_general_conversation(user_message)
        
        # Ensure response_data has all required keys
        response_data = self._ensure_response_structure(response_data)
        
        # Add assistant response to history with safe access
        self.conversation_history.append({
            "role": "assistant",
            "content": response_data.get("response", "No response generated"),
            "timestamp": datetime.utcnow().isoformat(),
            "intent": response_data.get("intent", "unknown"),
            "data": response_data.get("data", {})
        })
        
        return response_data
    
    async def _handle_autonomous_status_commands(self, message: str) -> Dict[str, Any]:
        """Handle autonomous trading status commands"""
        
        from agent.autonomous_agent import autonomous_agent
        
        message_lower = message.lower()
        
        if "status" in message_lower:
            status = await autonomous_agent.get_autonomous_status()
            
            if status["active_sessions"] > 0:
                sessions_info = ""
                for session_id, session in status["sessions"].items():
                    try:
                        end_time = session["params"]["end_time"]
                        if isinstance(end_time, str):
                            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        
                        time_remaining = end_time - datetime.utcnow().replace(tzinfo=None)
                        time_remaining_str = str(time_remaining).split('.')[0]
                    except Exception as e:
                        time_remaining_str = "Unknown"
                    
                    sessions_info += f"""
**Session:** `{session_id[:8]}...`
⏰ **Time Remaining:** {time_remaining_str}
📊 **Trades:** {session['performance']['total_trades']}
💰 **Success Rate:** {(session['performance']['successful_trades'] / max(1, session['performance']['total_trades']) * 100):.1f}%
📈 **Last Cycle:** {session.get('last_cycle', 'Not started')}
"""
                
                response = f"""🤖 **AUTONOMOUS TRADING STATUS**

✅ **Active Sessions:** {status['active_sessions']}
{sessions_info}

💡 **Commands:**
• `"stop autonomous"` - Stop all autonomous trading
• `"show reasoning"` - See latest decision logic
• `"performance report"` - Detailed analysis"""
                
            else:
                response = """🤖 **AUTONOMOUS TRADING STATUS**

❌ **No active autonomous sessions**

Start autonomous trading with:
`"Start the trading session for 24hr 10min"`"""
            
            return {
                "intent": "autonomous_status",
                "response": response,
                "data": status,
                "actions_taken": ["checked_autonomous_status"]
            }
        
        elif "stop autonomous" in message_lower:
            # Stop all autonomous sessions
            stopped_count = 0
            for session_id, session in autonomous_agent.autonomous_sessions.items():
                if session["status"] == "active":
                    session["status"] = "stopped_by_user"
                    stopped_count += 1
            
            response = f"""🛑 **AUTONOMOUS TRADING STOPPED**

✅ **Stopped {stopped_count} active session(s)**
📊 **All autonomous trading has been halted**
💬 **You can restart anytime with a new command**"""
            
            return {
                "intent": "autonomous_stopped",
                "response": response,
                "data": {"stopped_sessions": stopped_count},
                "actions_taken": ["stopped_autonomous_trading"]
            }
        
        elif "show reasoning" in message_lower or "reasoning" in message_lower:
            # Show latest reasoning from active sessions
            reasoning_data = []
            
            for session_id, session in autonomous_agent.autonomous_sessions.items():
                if session["status"] == "active" and session["reasoning_log"]:
                    latest_reasoning = session["reasoning_log"][-1]
                    reasoning_data.append({
                        "session_id": session_id[:8],
                        "latest_reasoning": latest_reasoning
                    })
            
            if reasoning_data:
                response = "🧠 **LATEST AUTONOMOUS REASONING**\n\n"
                for data in reasoning_data:
                    response += f"**Session {data['session_id']}:**\n"
                    decision = data['latest_reasoning'].get('decision', {})
                    if 'reasoning' in decision:
                        for reason in decision['reasoning'][-3:]:  # Last 3 reasoning points
                            response += f"• {reason}\n"
                    response += "\n"
            else:
                response = "🧠 **No active reasoning data available**\nStart autonomous trading to see AI decision-making in action!"
            
            return {
                "intent": "autonomous_reasoning",
                "response": response,
                "data": reasoning_data,
                "actions_taken": ["retrieved_autonomous_reasoning"]
            }
        
        else:
            return {
                "intent": "autonomous_help",
                "response": """🤖 **AUTONOMOUS TRADING COMMANDS**

**Status & Control:**
• `"status"` - Check active sessions
• `"stop autonomous"` - Stop all trading
• `"show reasoning"` - See AI decision logic

**Start Trading:**
• `"Start trading session for 24hr 10min"`
• `"Trade autonomously for 2 hours"`
• `"Auto trade for 30 minutes"`""",
                "actions_taken": ["provided_autonomous_help"]
            }
    
    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message intent with fast keyword matching"""
        
        message_lower = message.lower()
        
        # Price inquiry - EXACT MATCH
        if any(word in message_lower for word in ["price", "cost", "worth", "value"]):
            token = "ETH"  # Default
            for token_name in token_addresses.keys():
                if token_name.lower() in message_lower:
                    token = token_name
                    break
            return {
                "intent": "portfolio_inquiry",  # Changed to portfolio_inquiry for price checks
                "confidence": 0.9,
                "params": {"token": token}
            }
        
        # News inquiry - EXACT MATCH  
        if any(word in message_lower for word in ["news", "latest", "trending", "market"]):
            return {
                "intent": "market_analysis",  # Changed to market_analysis for news
                "confidence": 0.9,
                "params": {}
            }
        
        # Trade execution
        if any(word in message_lower for word in ["trade", "swap", "buy", "sell", "convert"]):
            return {
                "intent": "trade_request",
                "confidence": 0.9,
                "params": self._extract_trade_params_simple(message)
            }
        
        # Portfolio
        if any(word in message_lower for word in ["portfolio", "balance", "holdings"]):
            return {
                "intent": "portfolio_inquiry",
                "confidence": 0.9,
                "params": {}
            }
        
        # History
        if any(word in message_lower for word in ["history", "trades", "transactions"]):
            return {
                "intent": "portfolio_inquiry",  # Use portfolio for history too
                "confidence": 0.8,
                "params": {}
            }
        
        # Strategy
        if any(word in message_lower for word in ["strategy", "analysis", "recommend"]):
            return {
                "intent": "strategy_discussion",
                "confidence": 0.8,
                "params": {}
            }
        
        # Autonomous mode
        if any(phrase in message_lower for phrase in ["autonomous", "start trading session", "trade for"]):
            return {
                "intent": "general_conversation",  # Handle as conversation for now
                "confidence": 0.9,
                "params": {"autonomous": True}
            }
        
        # Default
        return {
            "intent": "general_conversation",
            "confidence": 0.7,
            "params": {}
        }
    
    def _extract_trade_params_simple(self, message: str) -> Dict[str, Any]:
        """Extract trade parameters simply"""
        import re
        
        # Look for pattern like "100 USDC to ETH"
        pattern = r"(\d+(?:\.\d+)?)\s+(\w+)\s+(?:to|for|→)\s+(\w+)"
        match = re.search(pattern, message, re.IGNORECASE)
        
        if match:
            amount, from_token, to_token = match.groups()
            return {
                "amount": amount,
                "token_from": from_token.upper(),
                "token_to": to_token.upper()
            }
        
        return {}
    
    async def _handle_trade_request(self, message: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trade execution requests with conversational parameter gathering"""
        
        params = intent_data.get("params", {})
        missing_params = []
        
        # Check required parameters
        if not params.get("token_from"):
            missing_params.append("source token")
        if not params.get("token_to"):
            missing_params.append("destination token")
        if not params.get("amount"):
            missing_params.append("trade amount")
        
        # If parameters are missing, ask for them conversationally
        if missing_params:
            questions = {
                "source token": "Which token would you like to trade from? (e.g., USDC, ETH, WBTC)",
                "destination token": "Which token would you like to buy? (e.g., ETH, WBTC, UNI)",
                "trade amount": "How much would you like to trade? (e.g., 100 USDC, 0.5 ETH)"
            }
            
            next_question = questions[missing_params[0]]
            
            return {
                "intent": "trade_request_incomplete",
                "response": f"I'd be happy to help you with that trade! {next_question}",
                "missing_params": missing_params,
                "data": {"partial_params": params},
                "reasoning": f"Need to gather {len(missing_params)} more parameters for trade execution",
                "suggestions": ["Provide all trade details at once for faster execution"]
            }
        
        # Execute trade with all parameters available
        return await self._execute_trade_with_reasoning(params)
    
    async def _execute_trade_with_reasoning(self, trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade with comprehensive analysis and reasoning"""
        
        # Step 1: Get current market data
        try:
            portfolio_data = get_portfolio(user_id=self.user_id)
            token_price = get_token_price_json(trade_params["token_to"])
            market_news_response = get_trending_news()
            market_news = market_news_response.get("news", []) if isinstance(market_news_response, dict) else []
        except Exception as e:
            return {
                "response": f"❌ Error gathering market data: {str(e)}",
                "success": False
            }
        
        # Step 2: Basic risk check (using Vincent stub)
        risk_check = await vincent_agent.check_trade_policy({
            "trade_type": "swap",
            "from_token": trade_params["token_from"],
            "to_token": trade_params["token_to"],
            "amount": trade_params["amount"],
            "market_conditions": {"news": market_news[:3] if market_news else []}  # Recent news
        })
        
        # Step 3: Generate AI reasoning
        reasoning_prompt = f"""
        As Kairos, an expert trading AI, analyze this trade request:
        
        Trade Details:
        - From: {trade_params['token_from']}
        - To: {trade_params['token_to']}
        - Amount: {trade_params['amount']}
        
        Market Context:
        - Current price: {token_price}
        - Portfolio: {json.dumps(portfolio_data, indent=2)}
        - Recent news: {market_news[:3]}
        - Risk assessment: {risk_check}
        
        Provide detailed reasoning for this trade including:
        1. Market analysis
        2. Risk assessment
        3. Strategic rationale
        4. Expected outcome
        5. Recommendation (execute/modify/wait)
        """
        
        try:
            reasoning_response = await self.model.generate_content_async(reasoning_prompt)
            ai_reasoning = reasoning_response.text
        except Exception as e:
            ai_reasoning = f"Reasoning analysis unavailable: {str(e)}"
        
        # Step 4: Execute trade if approved
        if risk_check.get("approved", False):
            try:
                # Convert token symbols to addresses
                from_address = token_addresses.get(trade_params["token_from"].upper())
                to_address = token_addresses.get(trade_params["token_to"].upper())
                
                if not from_address or not to_address:
                    return {
                        "response": f"❌ Unsupported token. Available tokens: {list(token_addresses.keys())}",
                        "success": False,
                        "reasoning": ai_reasoning
                    }
                
                # Execute the trade
                trade_result = trade_exec(from_address, to_address, float(trade_params["amount"]))
                
                # Log trade to database
                if self.current_session:
                    try:
                        await supabase_client.log_trade(
                            self.current_session,
                            {
                                "trade_type": "swap",
                                "from_token": trade_params["token_from"],
                                "to_token": trade_params["token_to"],
                                "amount": trade_params["amount"],
                                "success": trade_result.get("success", False),
                                "market_conditions": {"news": market_news[:3] if market_news else []}
                            },
                            ai_reasoning
                        )
                    except Exception as e:
                        print(f"Trade logging error: {e}")
                
                return {
                    "intent": "trade_executed",
                    "response": f"✅ Trade executed successfully!\n\n📊 **Trade Details:**\n- Swapped {trade_params['amount']} {trade_params['token_from']} → {trade_params['token_to']}\n- Status: {trade_result.get('status', 'Completed')}\n\n🧠 **AI Reasoning:**\n{ai_reasoning}",
                    "data": trade_result,
                    "reasoning": ai_reasoning,
                    "success": True,
                    "actions_taken": ["trade_execution", "policy_check", "market_analysis"]
                }
                
            except Exception as e:
                return {
                    "intent": "trade_error",
                    "response": f"❌ Trade execution failed: {str(e)}",
                    "data": {"error": str(e)},
                    "reasoning": ai_reasoning,
                    "success": False,
                    "actions_taken": ["error_handling"]
                }
        else:
            return {
                "intent": "trade_blocked",
                "response": f"⚠️ Trade not approved by risk assessment.\n\n**Reason:** {risk_check.get('reason', 'Policy violation')}\n**Risk Score:** {risk_check.get('risk_score', 'Unknown')}\n\n🧠 **AI Analysis:**\n{ai_reasoning}",
                "data": risk_check,
                "reasoning": ai_reasoning,
                "success": False,
                "suggestions": risk_check.get("recommendations", [])
            }
    
    async def _handle_portfolio_inquiry(self, message: str) -> Dict[str, Any]:
        """Handle portfolio and price queries"""
        
        try:
            # Check if this is a price inquiry
            message_lower = message.lower()
            if any(word in message_lower for word in ["price", "cost", "worth", "value"]):
                # Extract token from message
                token = "ETH"  # Default
                for token_name in token_addresses.keys():
                    if token_name.lower() in message_lower:
                        token = token_name
                        break
                
                # Get price data
                try:
                    price_data = get_token_price_json(token)
                    if isinstance(price_data, dict) and "price" in price_data:
                        price = price_data["price"]
                        response = f"💰 **{token} Price**\n\n🔸 **Current Price:** ${price:,.4f}\n🔸 **Source:** Real-time API\n🔸 **Updated:** {datetime.now().strftime('%H:%M:%S UTC')}"
                        
                        return {
                            "intent": "price_inquiry",
                            "response": response,
                            "data": price_data,
                            "actions_taken": ["fetched_price"],
                            "reasoning": f"Retrieved current {token} price"
                        }
                    else:
                        return {
                            "intent": "price_error",
                            "response": f"❌ Unable to fetch {token} price. The API returned: {price_data}",
                            "data": {"error": str(price_data)},
                            "actions_taken": ["price_fetch_failed"]
                        }
                except Exception as price_error:
                    return {
                        "intent": "price_error", 
                        "response": f"❌ Error fetching {token} price: {str(price_error)}",
                        "data": {"error": str(price_error)},
                        "actions_taken": ["price_fetch_error"]
                    }
            
            # Regular portfolio inquiry
            portfolio_data = get_portfolio(user_id=self.user_id)
            
            # Format response based on data structure
            if isinstance(portfolio_data, dict) and "error" not in portfolio_data:
                response = "📊 **Your Portfolio**\n\n"
                
                # Handle different portfolio data formats
                if "balances" in portfolio_data:
                    balances = portfolio_data["balances"]
                elif isinstance(portfolio_data, list):
                    balances = portfolio_data
                else:
                    balances = []
                
                if balances:
                    for balance in balances[:10]:  # Show top 10
                        symbol = balance.get("symbol", "Unknown")
                        amount = balance.get("amount", balance.get("balance", 0))
                        if amount > 0:
                            response += f"• {symbol}: {amount:,.4f}\n"
                else:
                    response += "📭 No tokens found in portfolio"
                
                response += "\n🤖 **Status:** Portfolio data retrieved successfully"
                
            else:
                response = f"❌ Unable to fetch portfolio: {portfolio_data.get('error', 'Unknown error')}"
            
            return {
                "intent": "portfolio_analysis",
                "response": response,
                "data": portfolio_data,
                "actions_taken": ["portfolio_fetch"],
                "reasoning": "Retrieved portfolio holdings"
            }
            
        except Exception as e:
            return {
                "intent": "portfolio_error",
                "response": f"❌ Unable to fetch portfolio data: {str(e)}",
                "data": {"error": str(e)},
                "success": False,
                "actions_taken": ["error_handling"],
                "reasoning": f"Portfolio fetch failed: {str(e)}"
            }
    
    async def _handle_market_analysis(self, message: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market analysis and trade history requests"""
        
        try:
            message_lower = message.lower()
            
            # Check if this is a trade history request
            if any(word in message_lower for word in ["history", "trades", "transactions", "trading history"]):
                try:
                    from api.trades_history import get_portfolio as get_trades_history
                    history_data = get_trades_history(user_id=self.user_id)
                    
                    if isinstance(history_data, dict) and "error" not in history_data:
                        # Format trade history display
                        response = "📜 **Your Trading History**\n\n"
                        
                        if isinstance(history_data, list):
                            trades = history_data
                        elif "trades" in history_data:
                            trades = history_data["trades"]
                        else:
                            trades = []
                        
                        if trades:
                            for i, trade in enumerate(trades[-10:], 1):  # Last 10 trades
                                timestamp = trade.get("timestamp", "Unknown")
                                from_token = trade.get("from_token", trade.get("tokenSold", "Unknown"))
                                to_token = trade.get("to_token", trade.get("tokenBought", "Unknown"))
                                amount = trade.get("amount", trade.get("amountSold", 0))
                                
                                response += f"{i}. {from_token} → {to_token}\n"
                                response += f"   Amount: {amount}\n"
                                response += f"   Time: {timestamp}\n\n"
                        else:
                            response += "📭 No trading history found\n"
                        
                        response += "💡 **Tip:** Start autonomous trading to build your history!"
                        
                        return {
                            "intent": "trade_history",
                            "response": response,
                            "data": {"trades": trades, "total_trades": len(trades)},
                            "actions_taken": ["fetched_trade_history"],
                            "reasoning": "Retrieved real trading history from Recall API"
                        }
                    else:
                        return {
                            "intent": "trade_history_error",
                            "response": f"❌ Unable to fetch trade history: {history_data.get('error', 'Unknown error')}",
                            "data": history_data,
                            "actions_taken": ["trade_history_fetch_failed"]
                        }
                        
                except Exception as history_error:
                    return {
                        "intent": "trade_history_error",
                        "response": f"❌ Error fetching trade history: {str(history_error)}",
                        "data": {"error": str(history_error)},
                        "actions_taken": ["trade_history_fetch_error"]
                    }
            
            # Check if this is specifically a news request
            elif any(word in message_lower for word in ["news", "latest", "trending"]):
                try:
                    news_data = get_trending_news(limit=5)
                    
                    if isinstance(news_data, dict) and "news" in news_data:
                        news_items = news_data["news"]
                        response = "📰 **Latest Crypto News**\n\n"
                        
                        for i, item in enumerate(news_items[:5], 1):
                            title = item.get("title", "No title")[:80] + "..." if len(item.get("title", "")) > 80 else item.get("title", "No title")
                            currencies = item.get("currencies", [])
                            
                            response += f"{i}. {title}"
                            if currencies:
                                response += f" ({', '.join(currencies[:2])})"
                            response += "\n"
                        
                        response += "\n🤖 **Market Sentiment:** News data retrieved successfully"
                        
                        return {
                            "intent": "news_inquiry",
                            "response": response,
                            "data": news_data,
                            "actions_taken": ["fetched_news"],
                            "reasoning": "Retrieved latest cryptocurrency news"
                        }
                    else:
                        return {
                            "intent": "news_error",
                            "response": f"❌ Unable to fetch news. API returned: {news_data}",
                            "data": {"error": str(news_data)},
                            "actions_taken": ["news_fetch_failed"]
                        }
                        
                except Exception as news_error:
                    return {
                        "intent": "news_error",
                        "response": f"❌ Error fetching crypto news: {str(news_error)}",
                        "data": {"error": str(news_error)},
                        "actions_taken": ["news_fetch_error"]
                    }
            
            # General market analysis
            response = """📈 **Market Analysis**

🔸 **Current Status:** Market data analysis available
🔸 **Sentiment:** Analyzing current conditions
🔸 **Recommendation:** Consider checking specific token prices or recent news

💡 **Available Commands:**
• "What's the price of ETH?" - Get current prices
• "Get me the latest crypto news" - View trending news
• "Show my portfolio" - View your holdings
• "Show my trading history" - View past trades"""

            return {
                "intent": "market_analysis",
                "response": response,
                "data": {"analysis_type": "general"},
                "actions_taken": ["general_market_analysis"],
                "reasoning": "Provided general market analysis and guidance"
            }
            
        except Exception as e:
            return {
                "intent": "market_error",
                "response": f"❌ Market analysis error: {str(e)}",
                "data": {"error": str(e)},
                "actions_taken": ["error_handling"]
            }
    
    async def _handle_strategy_discussion(self, message: str) -> Dict[str, Any]:
        """Handle strategy-related conversations"""
        
        # Search for similar strategies in vector DB
        try:
            # Generate embedding for current message (simplified)
            # In production, use proper embedding model
            query_embedding = [0.1] * 1536  # Placeholder
            
            similar_strategies = await supabase_client.search_similar_strategies(query_embedding)
            
            strategy_prompt = f"""
            As Kairos, discuss trading strategy for: "{message}"
            
            Historical Strategies: {json.dumps(similar_strategies, indent=2)}
            
            Provide:
            1. Strategy recommendations
            2. Risk considerations
            3. Implementation steps
            4. Expected outcomes
            """
            
            ai_response = await self.model.generate_content_async(strategy_prompt)
            
            return {
                "intent": "strategy_discussion",
                "response": ai_response.text,
                "data": {"similar_strategies": similar_strategies},
                "actions_taken": ["strategy_search", "ai_analysis"]
            }
            
        except Exception as e:
            # Fallback to general strategy discussion
            fallback_prompt = f"""
            As Kairos, provide trading strategy advice for: "{message}"
            
            Focus on:
            1. Risk management
            2. Diversification
            3. Market timing
            4. Practical implementation
            """
            
            try:
                ai_response = await self.model.generate_content_async(fallback_prompt)
                return {
                    "intent": "strategy_discussion",
                    "response": ai_response.text,
                    "actions_taken": ["ai_strategy_analysis"]
                }
            except Exception as e2:
                return {
                    "response": f"💭 Strategy discussion temporarily unavailable: {str(e2)}",
                    "success": False
                }
    
    async def _handle_general_conversation(self, message: str) -> Dict[str, Any]:
        """Handle general conversation and questions"""
        
        conversation_prompt = f"""
        As Kairos, a friendly and knowledgeable AI trading assistant, respond to: "{message}"
        
        Context from recent conversation:
        {json.dumps(self.conversation_history[-3:], indent=2)}
        
        Maintain conversational tone while being helpful about trading and crypto topics.
        If the user needs trading help, guide them toward specific actions.
        """
        
        try:
            ai_response = await self.model.generate_content_async(conversation_prompt)
            
            return {
                "intent": "general_conversation",
                "response": ai_response.text,
                "actions_taken": ["conversation"],
                "suggestions": [
                    "Ask about your portfolio: 'How is my portfolio doing?'",
                    "Request market analysis: 'What's happening in the crypto market?'",
                    "Start a trade: 'I want to buy some ETH'"
                ]
            }
            
        except Exception as e:
            return {
                "response": "I'm here to help with your trading needs! How can I assist you today?",
                "success": False
            }
    
    async def generate_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        
        try:
            analytics = await supabase_client.get_session_analytics(session_id)
            
            summary_prompt = f"""
            Generate a comprehensive trading session summary:
            
            Session Data: {json.dumps(analytics, indent=2)}
            Conversation History: {json.dumps(self.conversation_history, indent=2)}
            
            Include:
            1. Session overview
            2. Trades executed
            3. Performance analysis
            4. Key insights
            5. Recommendations for future sessions
            
            Format as a professional report.
            """
            
            summary_response = await self.model.generate_content_async(summary_prompt)
            
            return {
                "summary": summary_response.text,
                "analytics": analytics,
                "conversation_count": len(self.conversation_history),
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "summary": f"Session summary generation failed: {str(e)}",
                "session_id": session_id
            }
    
    def _ensure_response_structure(self, response_data: Dict) -> Dict[str, Any]:
        """Ensure response has all required fields"""
        defaults = {
            "intent": "general_conversation",
            "confidence": 0.5,
            "response": "I'm processing your request...",
            "data": {},
            "actions_taken": [],
            "reasoning": "",
            "suggestions": []
        }
        
        # If response_data is None or not a dict, create a new one
        if not isinstance(response_data, dict):
            response_data = {}
        
        # Add missing keys with default values
        for key, default_value in defaults.items():
            if key not in response_data:
                response_data[key] = default_value
        
        return response_data

# Global instancez
kairos_copilot = KairosTradingCopilot()
