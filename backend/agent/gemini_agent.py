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
    """Powerful Gemini AI trading agent with full Recall API integration"""
    
    def __init__(self):
        """Initialize the agent"""
        # Load environment variables
        load_dotenv()
        
        # Setup Gemini AI
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print(f"{Fore.GREEN}✅ Powerful Gemini AI Trading Agent initialized{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Full Recall API integration enabled{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚡ Ready to execute real trades!{Style.RESET_ALL}")
    
    def get_portfolio_data(self):
        """Get portfolio information"""
        try:
            return get_portfolio()
        except Exception as e:
            return {"error": f"Failed to get portfolio: {str(e)}"}
    
    def get_token_balance_data(self, token):
        """Get token balance"""
        try:
            return get_token_balance(token)
        except Exception as e:
            return {"error": f"Failed to get {token} balance: {str(e)}"}
    
    def get_token_price_data(self, symbol):
        """Get token price"""
        try:
            return get_token_price_json(symbol)
        except Exception as e:
            return {"error": f"Failed to get {symbol} price: {str(e)}"}
    
    def get_trades_history_data(self):
        """Get trading history"""
        try:
            return get_trades_history()
        except Exception as e:
            return {"error": f"Failed to get trades history: {str(e)}"}
    
    def get_crypto_news_data(self, currencies=None, limit=5, news_type="trending"):
        """Get cryptocurrency news (optimized for speed)"""
        try:
            if news_type == "trending":
                return get_trending_news(limit=limit)
            elif news_type == "bullish":
                return get_bullish_news(limit=limit)
            elif news_type == "bearish":
                return get_bearish_news(limit=limit)
            elif news_type == "currency" and currencies:
                return get_currency_news(currencies[0], limit=limit)
            else:
                return get_crypto_news(currencies=currencies, limit=limit)
        except Exception as e:
            return {"error": f"Failed to get crypto news: {str(e)}"}
    
    def execute_trade_now(self, from_token, to_token, amount):
        """Execute a trade immediately - REAL TRADING"""
        try:
            from_token = from_token.upper()
            to_token = to_token.upper()
            
            print(f"{Fore.YELLOW}🔥 EXECUTING REAL TRADE: {amount} {from_token} → {to_token}{Style.RESET_ALL}")
            
            # Check if tokens are supported
            if from_token not in token_addresses or to_token not in token_addresses:
                return {
                    "error": f"Unsupported token(s): {from_token}, {to_token}",
                    "supported_tokens": list(token_addresses.keys())
                }
            
            # Check balance first
            balance_data = self.get_token_balance_data(from_token)
            if 'error' in balance_data:
                return balance_data
            
            current_balance = balance_data.get('amount', 0)
            if current_balance < amount:
                return {
                    "error": f"Insufficient balance. You have {current_balance} {from_token}, need {amount}",
                    "current_balance": current_balance,
                    "required": amount
                }
            
            # Get token addresses
            from_address = token_addresses[from_token]
            to_address = token_addresses[to_token]
            
            # Execute trade via Recall API
            print(f"{Fore.RED}⚡ EXECUTING TRADE VIA RECALL API...{Style.RESET_ALL}")
            result = trade_exec(from_address, to_address, amount)
            
            if result:
                print(f"{Fore.GREEN}🎉 TRADE EXECUTED SUCCESSFULLY!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📊 Trade Details:{Style.RESET_ALL}")
                print(f"   From: {amount} {from_token}")
                print(f"   To: {to_token}")
                print(f"   Result: {json.dumps(result, indent=2)}")
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to execute trade: {str(e)}"}
    
    def parse_trade_request(self, message):
        """Parse trade requests from natural language"""
        message_lower = message.lower()
        
        # Pattern 1: "buy X USDC worth of WETH" or "trade 500 USDC to WETH"
        pattern1 = r'(?:buy|trade|swap|exchange).*?(\d+\.?\d*)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth).*?(?:to|for|of|worth of)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth)'
        match1 = re.search(pattern1, message_lower)
        
        # Pattern 2: "500 USDC to WETH" or "convert 100 USDC to WETH"
        pattern2 = r'(?:convert\s+)?(\d+\.?\d*)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth)\s+(?:to|for|into)\s+(usdc|weth|wbtc|dai|usdt|uni|link|eth)'
        match2 = re.search(pattern2, message_lower)
        
        # Pattern 3: "buy WETH with 500 USDC"
        pattern3 = r'(?:buy|get)\s+(usdc|weth|wbtc|dai|usdt|uni|link|eth)\s+(?:with|using)\s+(\d+\.?\d*)\s*(usdc|weth|wbtc|dai|usdt|uni|link|eth)'
        match3 = re.search(pattern3, message_lower)
        
        if match1:
            amount = float(match1.group(1))
            from_token = match1.group(2).upper()
            to_token = match1.group(3).upper()
            return 'trade', from_token, to_token, amount
        elif match2:
            amount = float(match2.group(1))
            from_token = match2.group(2).upper()
            to_token = match2.group(3).upper()
            return 'trade', from_token, to_token, amount
        elif match3:
            to_token = match3.group(1).upper()
            amount = float(match3.group(2))
            from_token = match3.group(3).upper()
            return 'trade', from_token, to_token, amount
        
        return None, None, None, None
    
    def analyze_user_intent(self, message):
        """Analyze what the user wants to do"""
        message_lower = message.lower()
        
        # Check for trade requests first
        action, from_token, to_token, amount = self.parse_trade_request(message)
        if action == 'trade':
            return 'execute_trade', {'from_token': from_token, 'to_token': to_token, 'amount': amount}
        
        # News requests
        if any(word in message_lower for word in ['news', 'latest', 'updates', 'trending', 'bullish', 'bearish']):
            # Check for specific sentiment
            if 'bullish' in message_lower or 'bull' in message_lower or 'positive' in message_lower:
                return 'news', {'type': 'bullish', 'limit': 5}
            elif 'bearish' in message_lower or 'bear' in message_lower or 'negative' in message_lower:
                return 'news', {'type': 'bearish', 'limit': 5}
            elif 'trending' in message_lower or 'hot' in message_lower:
                return 'news', {'type': 'trending', 'limit': 3}
            else:
                # Check for specific currency news
                for token in token_addresses.keys():
                    if token.lower() in message_lower:
                        return 'news', {'type': 'currency', 'currencies': [token], 'limit': 5}
                return 'news', {'type': 'trending', 'limit': 3}
        
        # Portfolio requests
        elif any(word in message_lower for word in ['portfolio', 'holdings', 'balance', 'wallet']):
            # Check for specific token
            for token in token_addresses.keys():
                if token.lower() in message_lower:
                    return 'token_balance', {'token': token}
            return 'portfolio', {}
        
        # Price requests
        elif any(word in message_lower for word in ['price', 'cost', 'value', 'worth']):
            for token in token_addresses.keys():
                if token.lower() in message_lower:
                    return 'price', {'token': token}
            return 'price_help', {}
        
        # History requests
        elif any(word in message_lower for word in ['history', 'trades', 'transactions']):
            return 'history', {}
        
        # Help requests
        elif any(word in message_lower for word in ['help', 'what can you do', 'tokens', 'supported']):
            return 'help', {}
        
        # General conversation
        return 'chat', {}
    
    def format_portfolio_display(self, portfolio_data):
        """Format portfolio data for display"""
        if 'error' in portfolio_data:
            return f"❌ Error: {portfolio_data['error']}"
        
        display = "\n📊 Your Portfolio:\n"
        
        # Handle different portfolio data structures
        balances = []
        if 'balances' in portfolio_data:
            balances = portfolio_data['balances']
        elif isinstance(portfolio_data, list):
            balances = portfolio_data
        
        if balances:
            total_value = 0
            for balance in balances:
                if isinstance(balance, dict):
                    symbol = balance.get('symbol', 'Unknown')
                    amount = balance.get('amount', balance.get('balance', 0))
                    value = balance.get('value', 0)
                    
                    display += f"   {symbol}: {amount:,.6f}"
                    if value > 0:
                        display += f" (${value:,.2f})"
                        total_value += value
                    display += "\n"
            
            if total_value > 0:
                display += f"\n💰 Total Value: ${total_value:,.2f}"
        else:
            display += "   No balances found or portfolio is empty"
        
        return display
    
    def format_trade_result(self, result, from_token, to_token, amount):
        """Format trade execution result"""
        if 'error' in result:
            return f"❌ Trade Failed: {result['error']}"
        
        display = f"\n🎉 TRADE EXECUTED SUCCESSFULLY!\n"
        display += f"   📊 Trade Details:\n"
        display += f"   • From: {amount} {from_token}\n"
        display += f"   • To: {to_token}\n"
        
        if 'txHash' in result:
            display += f"   • Transaction Hash: {result['txHash']}\n"
        
        if 'toTokenAmount' in result:
            display += f"   • Received: {result['toTokenAmount']} {to_token}\n"
        
        if 'gasUsed' in result:
            display += f"   • Gas Used: {result['gasUsed']}\n"
        
        display += f"\n✅ Trade completed via Recall API!"
        
        return display
    
    def send_message(self, message):
        """Process user message and generate response"""
        try:
            # Analyze user intent
            intent, params = self.analyze_user_intent(message)
            
            # Prepare context data
            context_data = ""
            function_result = None
            
            # Execute relevant functions based on intent
            if intent == 'execute_trade':
                from_token = params['from_token']
                to_token = params['to_token']
                amount = params['amount']
                
                print(f"{Fore.RED}🔥 TRADE REQUEST DETECTED:{Style.RESET_ALL}")
                print(f"   Amount: {amount} {from_token}")
                print(f"   Target: {to_token}")
                print(f"   Action: EXECUTING REAL TRADE...")
                
                # Execute the trade
                trade_result = self.execute_trade_now(from_token, to_token, amount)
                function_result = trade_result
                context_data = self.format_trade_result(trade_result, from_token, to_token, amount)
                print(context_data)
                
            elif intent == 'portfolio':
                print(f"{Fore.YELLOW}🔍 Getting your portfolio...{Style.RESET_ALL}")
                portfolio_data = self.get_portfolio_data()
                function_result = portfolio_data
                context_data = self.format_portfolio_display(portfolio_data)
                print(context_data)
            
            elif intent == 'token_balance':
                token = params['token']
                print(f"{Fore.YELLOW}🔍 Getting {token} balance...{Style.RESET_ALL}")
                balance_data = self.get_token_balance_data(token)
                function_result = balance_data
                context_data = f"\n💳 {token} Balance: {balance_data.get('amount', 0):,.6f}"
                print(context_data)
            
            elif intent == 'price':
                token = params['token']
                print(f"{Fore.YELLOW}🔍 Getting {token} price...{Style.RESET_ALL}")
                price_data = self.get_token_price_data(token)
                function_result = price_data
                price = price_data.get('price', 0)
                context_data = f"\n💰 {token} Current Price: ${price:,.2f}"
                print(context_data)
            
            elif intent == 'history':
                print(f"{Fore.YELLOW}🔍 Getting your trading history...{Style.RESET_ALL}")
                history_data = self.get_trades_history_data()
                function_result = history_data
                context_data = f"\n📜 Trading History:\n{json.dumps(history_data, indent=2)}"
                print(context_data)
            
            elif intent == 'news':
                news_type = params.get('type', 'trending')
                currencies = params.get('currencies', None)
                limit = params.get('limit', 10)
                
                print(f"{Fore.YELLOW}🔍 Getting {news_type} crypto news...{Style.RESET_ALL}")
                news_data = self.get_crypto_news_data(currencies=currencies, limit=limit, news_type=news_type)
                function_result = news_data
                context_data = self.format_news_display(news_data)
                print(context_data)
            
            elif intent == 'help':
                context_data = f"""
🎯 I can help you with:
• Portfolio management: "Show my portfolio"
• Token balances: "How much USDC do I have?"
• Price checking: "What's the price of WETH?"
• Trading history: "Show my trades"
• Crypto news: "Show me trending news", "Get bullish news", "Show ETH news"
• REAL TRADING: "Buy 500 USDC worth of WETH" or "Trade 100 USDC to WETH"

💰 Supported tokens: {', '.join(token_addresses.keys())}
📰 News types: trending, bullish, bearish, currency-specific
🔥 REAL TRADING ENABLED - I can execute actual trades via Recall API!
"""
                print(context_data)
            
            # Generate AI response with full context
            ai_prompt = f"""
You are a POWERFUL cryptocurrency trading assistant with FULL ACCESS to the Recall API and CoinPanic News API. You can:

1. View portfolios and balances
2. Get real-time prices  
3. View trading history
4. Get cryptocurrency news (trending, bullish, bearish, currency-specific)
5. EXECUTE REAL TRADES via Recall API

User message: {message}

Context data from API: {context_data}

Function execution result: {json.dumps(function_result, indent=2) if function_result else 'None'}

Guidelines:
- You have FULL POWER to execute trades via Recall API
- You can provide latest cryptocurrency news and market sentiment
- Be confident and professional
- Explain what you did and the results
- Provide market insights and trading advice based on news
- If a trade was executed, confirm the details
- If news was fetched, analyze the sentiment and provide insights
- Be encouraging but mention risks appropriately
- You are a REAL trading assistant with access to live market data and news

Respond as a powerful crypto trading expert who just executed actions via APIs.
"""
            
            response = self.model.generate_content(ai_prompt)
            
            if response and response.text:
                print(f"{Fore.CYAN}🤖 AI Trading Agent: {response.text}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}🤖 AI Trading Agent: Ready to execute your next trade!{Style.RESET_ALL}")
            
            print()
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
            print()
    
    def run(self):
        """Start the interactive chat"""
        print(f"{Fore.CYAN}🚀 Welcome to POWERFUL Gemini Trading Agent!{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Your AI-powered cryptocurrency trading assistant with FULL RECALL API ACCESS{Style.RESET_ALL}")
        print()
        print(f"{Fore.GREEN}⚡ FULL POWER FEATURES:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • Real-time portfolio and balance checking{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • Live cryptocurrency price feeds{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • Complete trading history access{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • Cryptocurrency news and market sentiment{Style.RESET_ALL}")
        print(f"{Fore.RED}  • REAL TRADE EXECUTION via Recall API{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • Advanced market analysis and insights{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}💰 Supported tokens: {', '.join(token_addresses.keys())}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📰 NEWS EXAMPLES:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • \"Show me trending crypto news\"{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • \"Get bullish news\"{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • \"Show me Bitcoin news\"{Style.RESET_ALL}")
        print(f"{Fore.RED}🔥 REAL TRADING EXAMPLES:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • \"Buy 500 USDC worth of WETH\"{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • \"Trade 100 USDC to WETH\"{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  • \"Convert 50 USDC to WBTC\"{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Type 'quit' or 'exit' to stop{Style.RESET_ALL}")
        print("=" * 80)
        
        while True:
            try:
                user_input = input(f"{Fore.BLUE}You: {Style.RESET_ALL}")
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print(f"{Fore.CYAN}👋 Thank you for using Powerful Gemini Trading Agent!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Happy trading and stay profitable! 🚀{Style.RESET_ALL}")
                    break
                
                if user_input.strip() == "":
                    continue
                
                self.send_message(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}👋 Goodbye! Happy trading!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

# Keep the old class name for compatibility
GeminiTradingAgent = PowerfulGeminiTradingAgent

def main():
    """Main function"""
    try:
        agent = PowerfulGeminiTradingAgent()
        agent.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Setup Error: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please check your .env file and API keys{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
