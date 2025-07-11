#!/usr/bin/env python3
"""
Powerful Gemini AI Trading Agent
A robust cryptocurrency trading assistant with complete Recall API integration
"""

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style
from datetime import datetime

# Import your existing API functions
from api.portfolio import get_portfolio
from api.token_balance import get_token_balance
from api.token_price import get_token_price_json
from api.trades_history import get_portfolio as get_trades_history
from api.execute import trade_exec, token_addresses
from agent.coinpanic_api import coinpanic_api, get_crypto_news, get_trending_news, get_currency_news, get_bullish_news, get_bearish_news

# Initialize colorama for colored output
colorama.init()

class PowerfulGeminiTradingAgent:
    """Advanced Gemini AI trading agent with full API access and intelligent analysis"""
    
    def __init__(self):
        """Initialize the powerful agent with full capabilities"""
        # Load environment variables
        load_dotenv()
        
        # Setup Gemini AI with maximum capabilities
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        # Use the most powerful model available
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',  # Using the most powerful model
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,  # Balanced creativity and accuracy
                max_output_tokens=8192,  # Maximum response length
                top_p=0.8,
                top_k=40
            )
        )
        
        # Store available tools and APIs
        self.available_apis = {
            'portfolio': self.get_portfolio_data,
            'token_balance': self.get_token_balance_data,
            'token_price': self.get_token_price_data,
            'trades_history': self.get_trades_history_data,
            'crypto_news': self.get_crypto_news_data,
            'execute_trade': self.execute_trade_now
        }
        
        print(f"{Fore.GREEN}✅ POWERFUL Gemini AI Trading Agent initialized with FULL CAPABILITIES{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Complete Recall API & CoinPanic News integration enabled{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚡ Ready to analyze, trade, and provide expert insights!{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🧠 Using Gemini-1.5-Pro with maximum intelligence settings{Style.RESET_ALL}")
    
    def get_portfolio_data(self):
        """Get comprehensive portfolio information with enhanced error handling"""
        try:
            print(f"{Fore.YELLOW}📊 Fetching portfolio data...{Style.RESET_ALL}")
            portfolio = get_portfolio()
            
            if isinstance(portfolio, dict) and 'error' not in portfolio:
                print(f"{Fore.GREEN}✅ Portfolio data retrieved successfully{Style.RESET_ALL}")
            
            return portfolio
        except Exception as e:
            error_msg = f"Failed to get portfolio: {str(e)}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            return {"error": error_msg}
    
    def get_token_balance_data(self, token):
        """Get token balance with comprehensive validation"""
        try:
            print(f"{Fore.YELLOW}💰 Fetching {token} balance...{Style.RESET_ALL}")
            balance = get_token_balance(token)
            
            if isinstance(balance, dict) and 'amount' in balance:
                print(f"{Fore.GREEN}✅ {token} balance retrieved: {balance['amount']}{Style.RESET_ALL}")
            
            return balance
        except Exception as e:
            error_msg = f"Failed to get {token} balance: {str(e)}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            return {"error": error_msg}
    
    def get_token_price_data(self, symbol):
        """Get real-time token price with market data"""
        try:
            print(f"{Fore.YELLOW}💹 Fetching {symbol} price data...{Style.RESET_ALL}")
            price_data = get_token_price_json(symbol)
            
            if isinstance(price_data, dict) and 'price' in price_data:
                print(f"{Fore.GREEN}✅ {symbol} price retrieved: ${price_data['price']}{Style.RESET_ALL}")
            
            return price_data
        except Exception as e:
            error_msg = f"Failed to get {symbol} price: {str(e)}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            return {"error": error_msg}
    
    def get_trades_history_data(self):
        """Get comprehensive trading history"""
        try:
            print(f"{Fore.YELLOW}📜 Fetching trading history...{Style.RESET_ALL}")
            history = get_trades_history()
            
            if isinstance(history, dict) and 'error' not in history:
                print(f"{Fore.GREEN}✅ Trading history retrieved successfully{Style.RESET_ALL}")
            
            return history
        except Exception as e:
            error_msg = f"Failed to get trades history: {str(e)}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            return {"error": error_msg}
    
    def get_crypto_news_data(self, currencies=None, limit=10, news_type="trending"):
        """Get comprehensive cryptocurrency news with sentiment analysis"""
        try:
            print(f"{Fore.YELLOW}📰 Fetching {news_type} crypto news...{Style.RESET_ALL}")
            
            if news_type == "trending":
                news_data = get_trending_news(limit=limit)
            elif news_type == "bullish":
                news_data = get_bullish_news(limit=limit)
            elif news_type == "bearish":
                news_data = get_bearish_news(limit=limit)
            elif news_type == "currency" and currencies:
                news_data = get_currency_news(currencies[0], limit=limit)
            else:
                news_data = get_crypto_news(currencies=currencies, limit=limit)
            
            if isinstance(news_data, dict) and 'news' in news_data:
                print(f"{Fore.GREEN}✅ Retrieved {len(news_data['news'])} news items{Style.RESET_ALL}")
            
            return news_data
        except Exception as e:
            error_msg = f"Failed to get crypto news: {str(e)}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            return {"error": error_msg}
    
    def execute_trade_now(self, from_token, to_token, amount):
        """Execute a trade immediately with comprehensive validation and reporting"""
        try:
            from_token = from_token.upper()
            to_token = to_token.upper()
            
            print(f"{Fore.YELLOW}🔥 INITIATING REAL TRADE EXECUTION{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Trade Request: {amount} {from_token} → {to_token}{Style.RESET_ALL}")
            
            # Comprehensive validation
            if from_token not in token_addresses or to_token not in token_addresses:
                error_msg = f"Unsupported token(s): {from_token}, {to_token}"
                print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
                return {
                    "error": error_msg,
                    "supported_tokens": list(token_addresses.keys())
                }
            
            # Check balance with detailed feedback
            print(f"{Fore.YELLOW}💰 Checking {from_token} balance...{Style.RESET_ALL}")
            balance_data = self.get_token_balance_data(from_token)
            
            if 'error' in balance_data:
                print(f"{Fore.RED}❌ Balance check failed: {balance_data['error']}{Style.RESET_ALL}")
                return balance_data
            
            current_balance = balance_data.get('amount', 0)
            print(f"{Fore.GREEN}✅ Current {from_token} balance: {current_balance}{Style.RESET_ALL}")
            
            if current_balance < amount:
                error_msg = f"Insufficient balance. Available: {current_balance} {from_token}, Required: {amount}"
                print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
                return {
                    "error": error_msg,
                    "current_balance": current_balance,
                    "required": amount
                }
            
            # Get token addresses and execute trade
            from_address = token_addresses[from_token]
            to_address = token_addresses[to_token]
            
            print(f"{Fore.RED}⚡ EXECUTING TRADE VIA RECALL API...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📡 From Address: {from_address}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📡 To Address: {to_address}{Style.RESET_ALL}")
            
            # Execute the actual trade
            result = trade_exec(from_address, to_address, amount)
            
            if result and 'error' not in result:
                print(f"{Fore.GREEN}🎉 TRADE EXECUTED SUCCESSFULLY!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}✅ Transaction completed via Recall API{Style.RESET_ALL}")
                
                # Add timestamp and trade details
                result['executed_at'] = datetime.now().isoformat()
                result['trade_details'] = {
                    'from_token': from_token,
                    'to_token': to_token,
                    'amount': amount,
                    'from_address': from_address,
                    'to_address': to_address
                }
            else:
                print(f"{Fore.RED}❌ Trade execution failed{Style.RESET_ALL}")
                if result:
                    print(f"{Fore.RED}Error: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
            
            return result
            
        except Exception as e:
            error_msg = f"Critical error during trade execution: {str(e)}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            return {"error": error_msg}
    
    def analyze_user_intent_with_ai(self, message):
        """Use Gemini AI to analyze user intent and extract parameters"""
        try:
            analysis_prompt = f"""
Analyze this user message for cryptocurrency trading intent:

Message: "{message}"

Available actions:
1. execute_trade - for trading requests
2. portfolio - for portfolio/balance info
3. token_balance - for specific token balance
4. token_price - for price information
5. trades_history - for trading history
6. crypto_news - for cryptocurrency news
7. help - for help requests
8. general_chat - for general conversation

Available tokens: {', '.join(token_addresses.keys())}

If it's a trading request, extract:
- from_token (token to sell)
- to_token (token to buy)
- amount (quantity)

If it's a news request, extract:
- news_type (trending, bullish, bearish, currency)
- currencies (if specific)
- limit (default 5)

If it's a price or balance request, extract:
- token (symbol)

Return JSON format:
{{
    "intent": "action_name",
    "confidence": 0.95,
    "parameters": {{
        "key": "value"
    }}
}}
"""
            
            response = self.model.generate_content(analysis_prompt)
            
            if response and response.text:
                try:
                    # Extract JSON from response
                    json_str = response.text
                    if '```json' in json_str:
                        json_str = json_str.split('```json')[1].split('```')[0]
                    elif '```' in json_str:
                        json_str = json_str.split('```')[1].split('```')[0]
                    
                    analysis = json.loads(json_str.strip())
                    return analysis
                except:
                    # Fallback to simple analysis
                    return self.simple_intent_analysis(message)
            
            return self.simple_intent_analysis(message)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ AI analysis failed, using fallback: {str(e)}{Style.RESET_ALL}")
            return self.simple_intent_analysis(message)
    
    def simple_intent_analysis(self, message):
        """Fallback simple intent analysis"""
        message_lower = message.lower()
        
        # Trade patterns
        trade_patterns = [
            r'(?:buy|trade|swap|exchange|convert).*?(\d+\.?\d*)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth).*?(?:to|for|of|worth of|into)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth)',
            r'(\d+\.?\d*)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth)\s+(?:to|for|into)\s+(usdc|weth|wbtc|dai|usdt|uni|link|eth)',
            r'(?:buy|get)\s+(usdc|weth|wbtc|dai|usdt|uni|link|eth)\s+(?:with|using)\s+(\d+\.?\d*)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth)'
        ]
        
        for pattern in trade_patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    amount = float(groups[0])
                    from_token = groups[1].upper()
                    to_token = groups[2].upper()
                    return {
                        "intent": "execute_trade",
                        "confidence": 0.9,
                        "parameters": {
                            "from_token": from_token,
                            "to_token": to_token,
                            "amount": amount
                        }
                    }
        
        # Other intents
        if any(word in message_lower for word in ['news', 'latest', 'updates', 'trending', 'bullish', 'bearish']):
            news_type = "trending"
            if 'bullish' in message_lower:
                news_type = "bullish"
            elif 'bearish' in message_lower:
                news_type = "bearish"
            
            return {
                "intent": "crypto_news",
                "confidence": 0.8,
                "parameters": {"news_type": news_type, "limit": 5}
            }
        
        elif any(word in message_lower for word in ['portfolio', 'holdings', 'balance', 'wallet']):
            return {
                "intent": "portfolio",
                "confidence": 0.8,
                "parameters": {}
            }
        
        elif any(word in message_lower for word in ['price', 'cost', 'value', 'worth']):
            for token in token_addresses.keys():
                if token.lower() in message_lower:
                    return {
                        "intent": "token_price",
                        "confidence": 0.8,
                        "parameters": {"token": token}
                    }
        
        elif any(word in message_lower for word in ['history', 'trades', 'transactions']):
            return {
                "intent": "trades_history",
                "confidence": 0.8,
                "parameters": {}
            }
        
        elif any(word in message_lower for word in ['help', 'what can you do', 'commands']):
            return {
                "intent": "help",
                "confidence": 0.9,
                "parameters": {}
            }
        
        return {
            "intent": "general_chat",
            "confidence": 0.5,
            "parameters": {}
        }
    
    def format_data_for_display(self, data_type, data, additional_context=None):
        """Format API data for beautiful presentation"""
        if isinstance(data, dict) and 'error' in data:
            return f"❌ {data_type.title()} Error: {data['error']}"
        
        if data_type == "portfolio":
            return self._format_portfolio(data)
        elif data_type == "token_balance":
            return self._format_token_balance(data, additional_context)
        elif data_type == "token_price":
            return self._format_token_price(data, additional_context)
        elif data_type == "trades_history":
            return self._format_trades_history(data)
        elif data_type == "crypto_news":
            return self._format_crypto_news(data)
        elif data_type == "trade_result":
            return self._format_trade_result(data, additional_context)
        else:
            return json.dumps(data, indent=2)
    
    def _format_portfolio(self, portfolio_data):
        """Format portfolio data beautifully"""
        display = "\n📊 YOUR PORTFOLIO OVERVIEW\n" + "="*50 + "\n"
        
        balances = []
        if isinstance(portfolio_data, dict):
            if 'balances' in portfolio_data:
                balances = portfolio_data['balances']
            elif 'data' in portfolio_data:
                balances = portfolio_data['data']
        elif isinstance(portfolio_data, list):
            balances = portfolio_data
        
        if balances:
            total_value = 0
            for balance in balances:
                if isinstance(balance, dict):
                    symbol = balance.get('symbol', 'Unknown')
                    amount = balance.get('amount', balance.get('balance', 0))
                    value = balance.get('value', 0)
                    
                    display += f"💰 {symbol:<8} | Balance: {amount:>15,.6f}"
                    if value > 0:
                        display += f" | Value: ${value:>10,.2f}"
                        total_value += value
                    display += "\n"
            
            display += "-" * 50 + "\n"
            if total_value > 0:
                display += f"� TOTAL PORTFOLIO VALUE: ${total_value:,.2f}\n"
        else:
            display += "📭 No balances found or portfolio is empty\n"
        
        display += "="*50
        return display
    
    def _format_token_balance(self, balance_data, token=None):
        """Format token balance beautifully"""
        if not token:
            token = balance_data.get('symbol', 'Unknown')
        
        amount = balance_data.get('amount', 0)
        display = f"\n💳 {token} BALANCE\n"
        display += "="*30 + "\n"
        display += f"🪙 Amount: {amount:,.6f} {token}\n"
        display += "="*30
        return display
    
    def _format_token_price(self, price_data, token=None):
        """Format token price beautifully"""
        if 'price' not in price_data:
            return f"❌ Price data not available for {token}"
        
        price = price_data['price']
        display = f"\n💹 {token} PRICE DATA\n"
        display += "="*35 + "\n"
        display += f"💵 Current Price: ${price:,.4f}\n"
        
        if 'change24h' in price_data:
            change = price_data['change24h']
            emoji = "📈" if change > 0 else "📉"
            display += f"{emoji} 24h Change: {change:+.2f}%\n"
        
        display += f"🕐 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        display += "="*35
        return display
    
    def _format_trades_history(self, history_data):
        """Format trading history beautifully"""
        display = "\n📜 TRADING HISTORY\n"
        display += "="*60 + "\n"
        
        trades = []
        if isinstance(history_data, dict):
            if 'trades' in history_data:
                trades = history_data['trades']
            elif 'data' in history_data:
                trades = history_data['data']
        elif isinstance(history_data, list):
            trades = history_data
        
        if trades:
            for i, trade in enumerate(trades[:10], 1):  # Show last 10 trades
                if isinstance(trade, dict):
                    display += f"🔄 Trade #{i}\n"
                    display += f"   📅 Date: {trade.get('date', 'Unknown')}\n"
                    display += f"   💱 Pair: {trade.get('from_token', 'Unknown')} → {trade.get('to_token', 'Unknown')}\n"
                    display += f"   � Amount: {trade.get('amount', 0)}\n"
                    display += f"   📊 Status: {trade.get('status', 'Unknown')}\n"
                    display += "-" * 40 + "\n"
        else:
            display += "📭 No trading history found\n"
        
        display += "="*60
        return display
    
    def _format_crypto_news(self, news_data):
        """Format cryptocurrency news beautifully"""
        if 'news' not in news_data:
            return "❌ No news data available"
        
        news_items = news_data['news']
        display = f"\n📰 CRYPTOCURRENCY NEWS ({len(news_items)} items)\n"
        display += "="*70 + "\n"
        
        for i, item in enumerate(news_items, 1):
            display += f"📍 {i}. {item.get('title', 'No title')}\n"
            
            # Add source and time
            source = item.get('source', 'Unknown')
            published = item.get('published_at', '')
            if published:
                try:
                    # Simple time formatting
                    display += f"   📡 {source} | {published[:10]}\n"
                except:
                    display += f"   📡 {source}\n"
            
            # Add currencies if available
            currencies = item.get('currencies', [])
            if currencies:
                currency_str = ', '.join(currencies)
                display += f"   🪙 Related: {currency_str}\n"
            
            # Add sentiment
            votes = item.get('votes', {})
            positive = votes.get('positive', 0)
            negative = votes.get('negative', 0)
            if positive > 0 or negative > 0:
                display += f"   📊 Sentiment: +{positive}/-{negative}\n"
            
            display += "-" * 50 + "\n"
        
        display += "="*70
        return display
    
    def _format_trade_result(self, result, context):
        """Format trade execution result beautifully"""
        if 'error' in result:
            return f"❌ TRADE FAILED: {result['error']}"
        
        from_token = context.get('from_token', 'Unknown')
        to_token = context.get('to_token', 'Unknown')
        amount = context.get('amount', 0)
        
        display = "\n🎉 TRADE EXECUTED SUCCESSFULLY!\n"
        display += "="*50 + "\n"
        display += f"📊 TRADE DETAILS:\n"
        display += f"   💸 Sold: {amount} {from_token}\n"
        display += f"   💰 Bought: {to_token}\n"
        
        if 'toTokenAmount' in result:
            display += f"   📈 Received: {result['toTokenAmount']} {to_token}\n"
        
        if 'txHash' in result:
            display += f"   🔗 Transaction: {result['txHash'][:20]}...\n"
        
        if 'gasUsed' in result:
            display += f"   ⛽ Gas Used: {result['gasUsed']}\n"
        
        if 'executed_at' in result:
            display += f"   🕐 Executed: {result['executed_at'][:19]}\n"
        
        display += "\n✅ Trade completed via Recall API!"
        display += "\n" + "="*50
        return display
    
    def send_message(self, message):
        """Process user message with full AI analysis and API integration"""
        try:
            print(f"\n{Fore.BLUE}🧠 Processing your request...{Style.RESET_ALL}")
            
            # Step 1: Analyze user intent with AI
            intent_analysis = self.analyze_user_intent_with_ai(message)
            intent = intent_analysis.get('intent', 'general_chat')
            params = intent_analysis.get('parameters', {})
            confidence = intent_analysis.get('confidence', 0.5)
            
            print(f"{Fore.CYAN}📋 Intent: {intent} (Confidence: {confidence:.0%}){Style.RESET_ALL}")
            
            # Step 2: Execute appropriate API calls
            api_data = None
            formatted_display = ""
            
            if intent == 'execute_trade':
                from_token = params.get('from_token')
                to_token = params.get('to_token')
                amount = params.get('amount')
                
                if from_token and to_token and amount:
                    print(f"{Fore.RED}🔥 EXECUTING TRADE: {amount} {from_token} → {to_token}{Style.RESET_ALL}")
                    api_data = self.execute_trade_now(from_token, to_token, amount)
                    formatted_display = self.format_data_for_display('trade_result', api_data, params)
                else:
                    api_data = {"error": "Invalid trade parameters"}
                    formatted_display = "❌ Could not parse trade request"
            
            elif intent == 'portfolio':
                api_data = self.get_portfolio_data()
                formatted_display = self.format_data_for_display('portfolio', api_data)
            
            elif intent == 'token_balance':
                token = params.get('token')
                if token:
                    api_data = self.get_token_balance_data(token)
                    formatted_display = self.format_data_for_display('token_balance', api_data, token)
                else:
                    api_data = {"error": "Token not specified"}
                    formatted_display = "❌ Please specify a token"
            
            elif intent == 'token_price':
                token = params.get('token')
                if token:
                    api_data = self.get_token_price_data(token)
                    formatted_display = self.format_data_for_display('token_price', api_data, token)
                else:
                    api_data = {"error": "Token not specified"}
                    formatted_display = "❌ Please specify a token"
            
            elif intent == 'trades_history':
                api_data = self.get_trades_history_data()
                formatted_display = self.format_data_for_display('trades_history', api_data)
            
            elif intent == 'crypto_news':
                news_type = params.get('news_type', 'trending')
                currencies = params.get('currencies', None)
                limit = params.get('limit', 5)
                
                api_data = self.get_crypto_news_data(currencies=currencies, limit=limit, news_type=news_type)
                formatted_display = self.format_data_for_display('crypto_news', api_data)
            
            elif intent == 'help':
                formatted_display = self._get_help_text()
            
            # Step 3: Display formatted data
            if formatted_display:
                print(formatted_display)
            
            # Step 4: Generate intelligent AI response
            print(f"\n{Fore.MAGENTA}🤖 Generating AI response...{Style.RESET_ALL}")
            ai_response = self.generate_ai_response(message, intent, api_data, formatted_display)
            
            print(f"\n{Fore.GREEN}🎯 AI TRADING AGENT:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{ai_response}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error processing message: {str(e)}{Style.RESET_ALL}")
            
            # Generate fallback response
            fallback_response = self.generate_fallback_response(message, str(e))
            print(f"\n{Fore.YELLOW}🤖 AI TRADING AGENT:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{fallback_response}{Style.RESET_ALL}")
    
    def generate_pre_trade_response(self, user_message, from_token, to_token, amount):
        """Generate AI response BEFORE executing trade - analysis and reasoning"""
        try:
            # Get current market data for better analysis
            from_balance = self.get_token_balance_data(from_token)
            to_price = self.get_token_price_data(to_token)
            from_price = self.get_token_price_data(from_token)
            recent_news = self.get_crypto_news_data(currencies=[to_token], limit=3, news_type="trending")
            
            pre_trade_prompt = f"""You are an EXPERT cryptocurrency trading advisor. A user wants to execute this trade:

USER REQUEST: "{user_message}"

TRADE DETAILS:
- Selling: {amount} {from_token}
- Buying: {to_token}

CURRENT MARKET DATA:
- {from_token} Balance: {from_balance.get('amount', 0)} {from_token}
- {from_token} Price: ${from_price.get('price', 0):.4f}
- {to_token} Price: ${to_price.get('price', 0):.4f}

RECENT {to_token} NEWS:
{json.dumps(recent_news, indent=2) if recent_news and 'error' not in recent_news else 'No recent news available'}

TASK: Provide a pre-trade analysis response that includes:
1. 🎯 Trade Assessment - Is this a good trade right now?
2. 📊 Market Analysis - Current market conditions for both tokens
3. 💡 Key Insights - What the user should know before executing
4. ⚠️ Risk Factors - Any risks or considerations
5. 🚀 Expected Outcome - What to expect from this trade

Be professional, insightful, and educational. This response comes BEFORE the trade execution.
Use proper formatting with emojis and clear sections.
Be confident but mention appropriate risks.
"""
            
            response = self.model.generate_content(pre_trade_prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return f"🎯 **Trade Analysis:** Converting {amount} {from_token} to {to_token}\n\n📊 **Assessment:** Analyzing market conditions and preparing to execute your trade. This trade will convert your {from_token} holdings to {to_token} at current market rates.\n\n⚡ **Status:** Ready to proceed with execution!"
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Pre-trade analysis failed: {str(e)}{Style.RESET_ALL}")
            return f"🎯 **Trade Request Confirmed:** I'll execute your trade to convert {amount} {from_token} to {to_token}.\n\n⚡ **Status:** Proceeding with trade execution..."

    def generate_post_trade_response(self, user_message, trade_result, from_token, to_token, amount):
        """Generate AI response AFTER executing trade - based on actual JSON result"""
        try:
            # Get updated portfolio and market data after trade
            updated_portfolio = self.get_portfolio_data()
            current_prices = {
                from_token: self.get_token_price_data(from_token),
                to_token: self.get_token_price_data(to_token)
            }
            
            post_trade_prompt = f"""You are an EXPERT cryptocurrency trading advisor. A trade has just been executed and you have the REAL RESULTS.

ORIGINAL USER REQUEST: "{user_message}"

EXECUTED TRADE:
- Sold: {amount} {from_token}
- Bought: {to_token}

ACTUAL TRADE RESULT JSON:
{json.dumps(trade_result, indent=2)}

UPDATED PORTFOLIO:
{json.dumps(updated_portfolio, indent=2) if updated_portfolio else 'Portfolio data unavailable'}

CURRENT MARKET PRICES:
- {from_token}: ${current_prices[from_token].get('price', 0):.4f}
- {to_token}: ${current_prices[to_token].get('price', 0):.4f}

TASK: Provide a comprehensive post-trade analysis response that includes:

IF TRADE WAS SUCCESSFUL:
1. 🎉 Trade Confirmation - Celebrate the successful execution
2. 📊 Trade Details - Exactly what was executed (use real JSON data)
3. 💰 Financial Impact - How much was received, rates, etc.
4. 🔍 Performance Analysis - How well did the trade execute?
5. 📈 Next Steps - Recommendations for portfolio management
6. 🎯 Market Outlook - What to watch for going forward

IF TRADE FAILED:
1. ❌ Issue Explanation - What went wrong (use real error data)
2. 🔍 Problem Analysis - Why it failed
3. 💡 Solutions - How to fix the issue
4. ✅ Next Steps - What to do next

Be professional, detailed, and educational. Use the REAL trade result data.
Reference specific numbers, transaction hashes, gas costs, etc. from the JSON.
Use proper formatting with emojis and clear sections.
Provide actionable insights based on the actual execution.
"""
            
            response = self.model.generate_content(post_trade_prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                # Fallback response based on trade result
                if trade_result and 'error' not in trade_result:
                    return f"🎉 **Trade Executed Successfully!**\n\n📊 **Result:** Your trade of {amount} {from_token} to {to_token} has been completed successfully!\n\n✅ **Status:** Transaction processed and your portfolio has been updated."
                else:
                    error_msg = trade_result.get('error', 'Unknown error') if trade_result else 'Trade execution failed'
                    return f"❌ **Trade Failed:** {error_msg}\n\n💡 **Next Steps:** Please check your balance and try again, or contact support if the issue persists."
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Post-trade analysis failed: {str(e)}{Style.RESET_ALL}")
            if trade_result and 'error' not in trade_result:
                return f"🎉 **Trade Completed!** Your {amount} {from_token} to {to_token} trade has been executed successfully!"
            else:
                return f"❌ **Trade Issue:** There was a problem executing your trade. Please check the details and try again."

    def generate_ai_response(self, user_message, intent, api_data, formatted_display):
        """Generate intelligent AI response based on context"""
        try:
            # Create comprehensive prompt for Gemini
            ai_prompt = f"""You are an EXPERT cryptocurrency trading assistant with FULL ACCESS to live market data and trading capabilities. You just processed a user request and have real data from APIs.

USER REQUEST: "{user_message}"

ANALYSIS RESULTS:
- Intent: {intent}
- API Data Available: {api_data is not None}
- Successful API Call: {'Yes' if api_data and 'error' not in api_data else 'No'}

LIVE API DATA:
{json.dumps(api_data, indent=2) if api_data else 'No data retrieved'}

FORMATTED DISPLAY:
{formatted_display}

CONTEXT:
- You have FULL ACCESS to Recall API for real trading
- You have FULL ACCESS to CoinPanic API for latest crypto news
- You can execute real trades, check portfolios, get prices, and provide news
- You just executed actions and have real results
- Available tokens: {', '.join(token_addresses.keys())}

RESPONSE GUIDELINES:
1. Be professional but approachable
2. Reference the specific data you just retrieved
3. Provide actionable insights based on the data
4. If trade was executed, confirm details and next steps
5. If getting prices/news, analyze and provide market perspective
6. Be confident - you have real access to trading systems
7. Mention relevant market trends if news data is available
8. Always be helpful and educational
9. Use proper formatting and emojis appropriately
10. Keep responses focused and valuable

Generate a response that shows you understand the data and can provide expert analysis and guidance."""

            response = self.model.generate_content(ai_prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._generate_basic_response(intent, api_data)
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ AI generation failed: {str(e)}{Style.RESET_ALL}")
            return self._generate_basic_response(intent, api_data)
    
    def _generate_basic_response(self, intent, api_data):
        """Generate basic response when AI fails"""
        if intent == 'execute_trade':
            if api_data and 'error' not in api_data:
                return "✅ Trade executed successfully! The transaction has been processed via Recall API."
            else:
                return "❌ Trade execution failed. Please check the details and try again."
        
        elif intent == 'portfolio':
            if api_data and 'error' not in api_data:
                return "📊 Your portfolio data has been retrieved successfully. Review your holdings above."
            else:
                return "❌ Unable to retrieve portfolio data at this time."
        
        elif intent == 'crypto_news':
            if api_data and 'error' not in api_data:
                return "📰 Latest cryptocurrency news retrieved! Stay informed about market trends."
            else:
                return "❌ Unable to fetch news at this time."
        
        else:
            return "I've processed your request. Let me know if you need anything else!"
    
    def generate_fallback_response(self, message, error):
        """Generate fallback response when everything fails"""
        try:
            fallback_prompt = f"""You are a cryptocurrency trading assistant. A user sent this message: "{message}"

There was an error: {error}

Provide a helpful response that:
1. Acknowledges the request
2. Explains there was a technical issue
3. Suggests alternative actions
4. Remains professional and helpful
5. Mentions your capabilities (trading, portfolio, news, prices)

Keep it concise and supportive."""

            response = self.model.generate_content(fallback_prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I apologize, but I'm experiencing technical difficulties. Please try again or ask for help with specific commands."
                
        except:
            return "I apologize for the technical issues. I can help you with trading, portfolio management, price checks, and crypto news. Please try your request again."
    
    def _get_help_text(self):
        """Generate comprehensive help text"""
        return f"""
🎯 GEMINI AI TRADING AGENT - FULL CAPABILITIES

🔥 REAL TRADING COMMANDS:
• "Trade 500 USDC to WETH" - Execute real trades
• "Buy 100 USDC worth of WBTC" - Purchase tokens
• "Convert 50 USDC to DAI" - Convert between tokens

📊 PORTFOLIO MANAGEMENT:
• "Show my portfolio" - View all holdings
• "Check my USDC balance" - Get specific token balance
• "What's my portfolio worth?" - Get total value

💹 PRICE & MARKET DATA:
• "What's the price of WETH?" - Get current prices
• "Show me Bitcoin price" - Check token values

📰 CRYPTOCURRENCY NEWS:
• "Show me trending crypto news" - Latest market updates
• "Get bullish news" - Positive market sentiment
• "Show me bearish news" - Negative market sentiment
• "Get Bitcoin news" - Token-specific updates

📜 TRADING HISTORY:
• "Show my trading history" - View past trades
• "What trades have I made?" - Transaction history

💰 SUPPORTED TOKENS:
{', '.join(token_addresses.keys())}

🚀 POWERED BY:
• Recall API - Real trading execution
• CoinPanic API - Live cryptocurrency news
• Gemini AI - Intelligent analysis and responses

⚡ I have FULL ACCESS to execute real trades and provide live market data!
"""
    
    def run(self):
        """Start the interactive chat with enhanced interface"""
        print(f"\n{Fore.CYAN}🚀 WELCOME TO GEMINI AI TRADING AGENT{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🎯 Your Advanced Cryptocurrency Trading Assistant{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   Powered by Gemini AI + Recall API + CoinPanic News API{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'='*80}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}⚡ FULL CAPABILITIES:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  🔥 REAL TRADING EXECUTION via Recall API{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  📊 Live Portfolio & Balance Management{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  💹 Real-time Price Monitoring{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  📰 Latest Cryptocurrency News & Sentiment{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  📜 Complete Trading History Access{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  🧠 Advanced AI Analysis & Insights{Style.RESET_ALL}")
        
        print(f"\n{Fore.MAGENTA}💰 SUPPORTED TOKENS:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {', '.join(token_addresses.keys())}{Style.RESET_ALL}")
        
        print(f"\n{Fore.BLUE}🎯 EXAMPLE COMMANDS:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  🔥 \"Trade 500 USDC to WETH\" - Execute real trades{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  📊 \"Show my portfolio\" - View all holdings{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  💹 \"What's the price of Bitcoin?\" - Get current prices{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  � \"Show me trending crypto news\" - Latest updates{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  📜 \"Show my trading history\" - Past transactions{Style.RESET_ALL}")
        
        print(f"\n{Fore.RED}⚠️  IMPORTANT: THIS AGENT EXECUTES REAL TRADES!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Always verify trade details before confirming.{Style.RESET_ALL}")
        
        print(f"\n{Fore.MAGENTA}Type 'quit', 'exit', or 'bye' to stop{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'='*80}{Style.RESET_ALL}")
        
        while True:
            try:
                print(f"\n{Fore.CYAN}💬 Ready for your command...{Style.RESET_ALL}")
                user_input = input(f"{Fore.BLUE}You: {Style.RESET_ALL}")
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye', 'stop']:
                    print(f"\n{Fore.GREEN}👋 Thank you for using Gemini AI Trading Agent!{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}🚀 Happy trading and stay profitable!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}� Remember: Always do your own research (DYOR)!{Style.RESET_ALL}")
                    break
                
                if user_input.strip() == "":
                    print(f"{Fore.YELLOW}💭 Please enter a command or question.{Style.RESET_ALL}")
                    continue
                
                # Process the message
                print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
                self.send_message(user_input)
                print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Goodbye! Happy trading!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Please try again or type 'help' for assistance.{Style.RESET_ALL}")


# Keep the old class name for compatibility
GeminiTradingAgent = PowerfulGeminiTradingAgent

def main():
    """Main function with enhanced startup"""
    try:
        print(f"{Fore.CYAN}🚀 Initializing Gemini AI Trading Agent...{Style.RESET_ALL}")
        agent = PowerfulGeminiTradingAgent()
        agent.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Startup interrupted. Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Startup Error: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Please check your .env file and API keys:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   - GEMINI_API_KEY{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   - RECALL_API_KEY{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   - COINPANIC_API_KEY{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
