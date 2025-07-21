#!/usr/bin/env python3
"""
Powerful Gemini AI Trading Agent - Enhanced with Assistant Mode
Supports both autonomous trading decisions and interactive assistant chat
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import colorama
from colorama import Fore
from typing import Optional, Dict, List
from datetime import datetime
import requests

# Import token addresses if available
try:
    from api.execute import token_addresses
except ImportError:
    # Fallback token addresses
    token_addresses = {
        'ETH': '0x0000000000000000000000000000000000000000',
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
        'SOL': 'So11111111111111111111111111111111111111112',
        'MATIC': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0',
        'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
        'USDbC': '0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
        'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7'
    }

colorama.init()

class PowerfulGeminiTradingAgent:
    """Advanced Gemini AI trading agent with autonomous and assistant capabilities"""

    def __init__(self, user_id: str = "default", gemini_api_key: Optional[str] = None):
        load_dotenv()
        self.user_id = user_id
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
                top_k=40,
                response_mime_type="application/json"
            )
        )
        
        # Assistant mode model (for conversational responses)
        self.assistant_model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config=genai.types.GenerationConfig(
                temperature=0.6,
                max_output_tokens=4096,
                top_p=0.9,
                top_k=30
            )
        )
        
        print(f"{Fore.GREEN}✅ Gemini AI Agent initialized with FULL CAPABILITIES{Fore.RESET}")

    def get_assistant_response(self, user_query: str, market_data: Dict, portfolio_data: Dict, news_data: Dict) -> str:
        """
        🤖 ASSISTANT MODE: Interactive chat with market analysis capabilities
        Returns conversational responses for user queries about crypto, markets, portfolio, etc.
        """
        try:
            # Create comprehensive assistant prompt
            assistant_prompt = f"""
            You are Kairos AI Assistant, an expert cryptocurrency trading advisor and market analyst. You have access to real-time market data and can help users with comprehensive crypto-related queries.

            **Your Capabilities:**
            - Real-time price analysis and market insights
            - Portfolio analysis and recommendations
            - Cryptocurrency education and explanations
            - Latest news and market sentiment analysis
            - Trading strategy suggestions
            - Risk assessment and management advice

            **Current Market Data (Live):**
            {json.dumps(market_data, indent=2)}

            **User's Portfolio:**
            {json.dumps(portfolio_data, indent=2)}

            **Latest Crypto News:**
            {json.dumps(news_data, indent=2)}

            **User Query:** "{user_query}"

            **Response Guidelines:**
            1. **Be Conversational**: Write in a friendly, professional tone
            2. **Use Real Data**: Reference the actual market data, prices, and portfolio information provided
            3. **Be Specific**: Give concrete numbers, percentages, and actionable insights
            4. **Format Well**: Use emojis, headers, and bullet points for readability
            5. **Stay Current**: Reference the latest news and market conditions
            6. **Be Educational**: Explain concepts when helpful
            7. **Show Confidence**: When you have data, be definitive in your analysis

            **Response Format:**
            - Start with a relevant emoji and clear header
            - Provide direct answer to the user's question
            - Include relevant data points and analysis
            - Add context from news or market conditions when relevant
            - End with actionable insights or next steps if appropriate

            **Examples of Good Responses:**
            - For price queries: Include current price, recent changes, market context
            - For portfolio questions: Analyze holdings, suggest optimizations, show performance
            - For news questions: Summarize key developments and their potential impact
            - For trading questions: Provide strategy suggestions with risk considerations

            Please provide a comprehensive, helpful response to the user's query using all available data.
            """

            # Get response from Gemini
            response = self.assistant_model.generate_content(assistant_prompt)
            return response.text

        except Exception as e:
            print(f"{Fore.RED}❌ Assistant Mode Error: {e}{Fore.RESET}")
            
            # Provide intelligent fallback based on query type
            return self._generate_fallback_response(user_query, market_data, portfolio_data, news_data)

    def _generate_fallback_response(self, query: str, market_data: Dict, portfolio_data: Dict, news_data: Dict) -> str:
        """Generate intelligent fallback responses when Gemini API fails"""
        
        query_lower = query.lower()
        
        # Price-related queries
        if any(keyword in query_lower for keyword in ['price', 'cost', 'value', 'worth']):
            if 'bitcoin' in query_lower or 'btc' in query_lower:
                btc_price = market_data.get('BTC', 0)
                return f"📈 **Bitcoin Price Update**\n\n**Current BTC Price:** ${btc_price:,.2f}\n\n*Bitcoin remains the leading cryptocurrency by market cap. This price reflects real-time market conditions.*"
            
            elif 'ethereum' in query_lower or 'eth' in query_lower:
                eth_price = market_data.get('ETH', 0)
                return f"📈 **Ethereum Price Update**\n\n**Current ETH Price:** ${eth_price:,.2f}\n\n*Ethereum continues to be the leading smart contract platform with strong ecosystem growth.*"
            
            else:
                price_list = "\n".join([f"• **{symbol}**: ${price:,.2f}" for symbol, price in market_data.items() if price > 0])
                return f"📊 **Current Crypto Prices**\n\n{price_list}\n\n*Prices updated in real-time from CoinGecko*"
        
        # Portfolio-related queries
        elif any(keyword in query_lower for keyword in ['portfolio', 'balance', 'holdings', 'assets']):
            if portfolio_data and portfolio_data.get('balances'):
                portfolio_response = "💼 **Your Portfolio Analysis**\n\n"
                total_value = 0
                
                for balance in portfolio_data['balances'][:5]:  # Top 5 holdings
                    token = balance.get('token', 'Unknown')
                    amount = balance.get('balance', 0)
                    price = balance.get('price', 0)
                    usd_value = balance.get('usd_value', 0)
                    total_value += usd_value
                    
                    percentage = (usd_value / portfolio_data.get('total_value', 1)) * 100
                    portfolio_response += f"• **{token}**: {amount:.6f} (${usd_value:,.2f} • {percentage:.1f}%)\n"
                
                portfolio_response += f"\n💰 **Total Portfolio Value**: ${portfolio_data.get('total_value', 0):,.2f}"
                portfolio_response += f"\n📈 **Diversification**: {len(portfolio_data.get('balances', []))} different assets"
                
                return portfolio_response
            else:
                return "💼 **Portfolio Status**\n\nNo portfolio data available. Please ensure your wallet is properly connected to see your holdings and analysis."
        
        # News-related queries
        elif any(keyword in query_lower for keyword in ['news', 'updates', 'happenings', 'trends']):
            if news_data and news_data.get('results'):
                news_response = "📰 **Latest Crypto News**\n\n"
                for i, article in enumerate(news_data['results'][:3], 1):
                    title = article.get('title', 'No title')
                    news_response += f"{i}. **{title}**\n"
                
                news_response += "\n*Stay informed with the latest developments in the crypto space.*"
                return news_response
            else:
                return "📰 **Crypto News**\n\nNews data is currently unavailable. The crypto market continues to evolve rapidly with new developments in DeFi, NFTs, and blockchain technology."
        
        # Trading-related queries
        elif any(keyword in query_lower for keyword in ['trade', 'buy', 'sell', 'swap', 'exchange']):
            return """🔄 **Trading Assistance**

I can help you with trading decisions! Here's what I can analyze:

• **Market Conditions**: Current price trends and volatility
• **Portfolio Optimization**: Rebalancing suggestions
• **Risk Assessment**: Position sizing and risk management
• **Entry/Exit Points**: Technical analysis insights

💡 **Pro Tip**: Always consider your risk tolerance and never invest more than you can afford to lose.

Would you like me to analyze any specific trading pair or strategy?"""
        
        # General crypto queries
        else:
            return f"""🤖 **Kairos AI Assistant**

I'm here to help with all your crypto needs! I can assist with:

📈 **Market Analysis**: Real-time prices and trends
💼 **Portfolio Review**: Holdings analysis and optimization  
📰 **News Updates**: Latest crypto developments
🔄 **Trading Insights**: Strategy suggestions and risk management
📚 **Education**: Explaining crypto concepts and technologies

💡 **Try asking me:**
• "What's the current Bitcoin price?"
• "Analyze my portfolio"
• "Show me the latest crypto news"
• "Should I buy Ethereum now?"

*How can I help you today?*"""

    def get_intelligent_analysis(self, portfolio_json: dict, market_prices_json: dict, news_json: dict, strategy_performance_json: list) -> dict:
        """
        🧠 AUTONOMOUS MODE: Core decision engine for autonomous trading
        Analyzes all data and returns structured trading decisions
        """
        total_value = portfolio_json.get('total_value', 0)
        balances = portfolio_json.get('balances', [])
        
        if total_value == 0 or not balances:
            print(f"{Fore.YELLOW}⚠️ Portfolio is empty or has zero value. Returning HODL decision.{Fore.RESET}")
            return {
                "should_trade": False,
                "confidence_score": 0.0,
                "strategy_chosen": {"name": "hodl_empty_portfolio", "type": "hodl"},
                "trade_params": {
                    "trade_type": "swap", 
                    "from_token": "USDC", 
                    "to_token": "ETH", 
                    "amount": 0.0, 
                    "chain": "ethereum"
                },
                "reasoning": [
                    "Portfolio is empty or has no available balance for trading.",
                    "HODL strategy selected until funds become available.",
                    "Waiting for market opportunity to enter positions."
                ]
            }
        
        available_tokens = list(token_addresses.keys())
        allowed_strategy_types = ['momentum', 'arbitrage', 'dca', 'swing', 'scalping', 'hodl', 'custom']
        allowed_trade_types = ['buy', 'sell', 'swap']

        # Enhanced decision prompt with better chain handling
        master_prompt = f"""
        You are Kairos AI, an expert quantitative cryptocurrency trading analyst with years of experience. Your decisions directly impact real trading outcomes, so precision is critical.

        **REAL-TIME DATA ANALYSIS REQUIRED:**

        **1. Current Portfolio State:**
        ```json
        {json.dumps(portfolio_json, indent=2)}
        ```

        **2. Live Market Prices:**
        ```json
        {json.dumps(market_prices_json, indent=2)}
        ```

        **3. Latest Market News & Sentiment:**
        ```json
        {json.dumps(news_json, indent=2)}
        ```

        **4. Historical Strategy Performance (Your Memory):**
        ```json
        {json.dumps(strategy_performance_json, indent=2)}
        ```

        **🎯 TRADING DECISION FRAMEWORK:**

        **CRITICAL CONSTRAINTS (MUST FOLLOW):**
        1. **Available Tokens**: {available_tokens}
        2. **Strategy Types**: {allowed_strategy_types}
        3. **Trade Types**: {allowed_trade_types}
        4. **Chain Mapping**: 
           - Ethereum tokens: ETH, WETH, USDC, WBTC, UNI, LINK, AAVE, DAI, USDT
           - Polygon tokens: MATIC, USDC (Polygon)
           - Base tokens: USDbC
           - Solana tokens: SOL

        **MULTI-CHAIN PORTFOLIO RULES:**
        - Each token exists on a specific blockchain
        - Trades can only occur within the same chain ecosystem
        - You MUST specify the correct `chain` for the `from_token`
        - Check portfolio balances per chain before trading

        **DECISION LOGIC:**
        1. **Risk Assessment**: Never trade more than 25% of any token balance
        2. **Chain Validation**: Ensure from_token and to_token are on compatible chains
        3. **Balance Verification**: Confirm sufficient balance exists on specified chain
        4. **Market Timing**: Use news sentiment and price trends for timing
        5. **Strategy Selection**: Prioritize high-performing strategies from memory

        **REQUIRED JSON OUTPUT:**
        {{
          "should_trade": boolean,
          "confidence_score": float (0.0-1.0),
          "strategy_chosen": {{
            "name": "descriptive_strategy_name",
            "type": "one_of_{allowed_strategy_types}"
          }},
          "trade_params": {{
            "trade_type": "one_of_{allowed_trade_types}",
            "from_token": "token_from_portfolio",
            "to_token": "target_token",
            "amount": float_amount,
            "chain": "blockchain_network"
          }},
          "reasoning": [
            "Step 1: Market analysis based on current data",
            "Step 2: Portfolio assessment and risk evaluation", 
            "Step 3: Chain and balance verification",
            "Step 4: Strategy selection rationale",
            "Step 5: Final trade decision explanation"
          ]
        }}

        **Special Cases:**
        - If portfolio value is 0: Return should_trade=false with HODL strategy
        - If insufficient balance: Return should_trade=false with explanation
        - If market conditions are unfavorable: Consider HODL with reasoning

        Analyze all data comprehensively and make your best trading decision.
        """

        try:
            print(f"{Fore.MAGENTA}🧠 Kairos AI: Analyzing comprehensive market data...{Fore.RESET}")
            response = self.model.generate_content(master_prompt)
            decision = json.loads(response.text)
            
            # Validate and enhance the decision
            decision = self._validate_trading_decision(decision, portfolio_json)
            
            strategy_name = decision.get('strategy_chosen', {}).get('name', 'Unknown')
            confidence = decision.get('confidence_score', 0) * 100
            should_trade = decision.get('should_trade', False)

            print(f"{Fore.GREEN}✅ Kairos AI Decision: {strategy_name} (Confidence: {confidence:.1f}%){Fore.RESET}")
            print(f"{Fore.CYAN}🤔 Should Trade: {should_trade}{Fore.RESET}")
            
            if should_trade:
                trade_params = decision.get('trade_params', {})
                print(f"{Fore.YELLOW}💱 Trade: {trade_params.get('amount', 0)} {trade_params.get('from_token', 'N/A')} → {trade_params.get('to_token', 'N/A')} on {trade_params.get('chain', 'N/A')}{Fore.RESET}")
            
            return decision

        except Exception as e:
            print(f"{Fore.RED}❌ Kairos AI Analysis Error: {e}{Fore.RESET}")
            if 'response' in locals():
                print(f"Raw response: {getattr(response, 'text', 'No response text')}")
            
            return {
                "should_trade": False,
                "confidence_score": 0.0,
                "strategy_chosen": {"name": "system_error_recovery", "type": "hodl"},
                "trade_params": {
                    "trade_type": "swap",
                    "from_token": "USDC", 
                    "to_token": "ETH", 
                    "amount": 0.0, 
                    "chain": "ethereum"
                },
                "reasoning": [
                    f"System error occurred during analysis: {str(e)}",
                    "Defaulting to HODL strategy for safety",
                    "Will retry analysis in next cycle"
                ]
            }

    def _validate_trading_decision(self, decision: dict, portfolio_data: dict) -> dict:
        """Validate and fix trading decisions from AI"""
        try:
            # Ensure all required fields exist
            if not decision.get('trade_params'):
                decision['trade_params'] = {
                    "trade_type": "swap",
                    "from_token": "USDC",
                    "to_token": "ETH", 
                    "amount": 0.0,
                    "chain": "ethereum"
                }
            
            trade_params = decision['trade_params']
            
            # Validate chain assignment
            chain_mapping = {
                'ETH': 'ethereum', 'WETH': 'ethereum', 'USDC': 'ethereum', 
                'WBTC': 'ethereum', 'UNI': 'ethereum', 'LINK': 'ethereum',
                'AAVE': 'ethereum', 'DAI': 'ethereum', 'USDT': 'ethereum',
                'MATIC': 'polygon', 'SOL': 'solana', 'USDbC': 'base'
            }
            
            from_token = trade_params.get('from_token', 'USDC')
            if from_token in chain_mapping:
                trade_params['chain'] = chain_mapping[from_token]
            
            # Validate token availability in portfolio
            portfolio_balances = portfolio_data.get('balances', [])
            available_tokens = [b.get('symbol') for b in portfolio_balances if b.get('amount', 0) > 0]
            
            if from_token not in available_tokens and decision.get('should_trade', False):
                print(f"{Fore.YELLOW}⚠️ Token {from_token} not available in portfolio, switching to HODL{Fore.RESET}")
                decision['should_trade'] = False
                decision['strategy_chosen'] = {"name": "insufficient_balance_hodl", "type": "hodl"}
                decision['reasoning'].append(f"Token {from_token} not available in portfolio")
            
            # Ensure confidence score is within bounds
            confidence = decision.get('confidence_score', 0.5)
            decision['confidence_score'] = max(0.0, min(1.0, float(confidence)))
            
            return decision
            
        except Exception as e:
            print(f"{Fore.RED}❌ Decision validation error: {e}{Fore.RESET}")
            return decision

    def get_market_analysis(self, symbol: str) -> str:
        """Get detailed market analysis for a specific cryptocurrency"""
        try:
            # Get current price data
            price_data = self._get_live_price_data(symbol)
            
            analysis_prompt = f"""
            Provide a comprehensive market analysis for {symbol} based on current data:
            
            Price Data: {json.dumps(price_data, indent=2)}
            
            Include:
            1. Current price and recent performance
            2. Technical analysis insights
            3. Market sentiment
            4. Key support and resistance levels
            5. Short-term outlook (1-7 days)
            6. Risk factors to consider
            
            Format the response in a clear, professional manner with specific insights.
            """
            
            response = self.assistant_model.generate_content(analysis_prompt)
            return response.text
            
        except Exception as e:
            return f"Unable to generate market analysis for {symbol}: {str(e)}"

    def _get_live_price_data(self, symbol: str) -> dict:
        """Get live price data for a cryptocurrency"""
        try:
            # Map common symbols to CoinGecko IDs
            coingecko_ids = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'USDC': 'usd-coin',
                'WETH': 'weth', 'WBTC': 'wrapped-bitcoin', 'UNI': 'uniswap',
                'LINK': 'chainlink', 'AAVE': 'aave', 'MATIC': 'matic-network',
                'SOL': 'solana', 'DAI': 'dai', 'USDT': 'tether'
            }
            
            coin_id = coingecko_ids.get(symbol.upper(), symbol.lower())
            
            # Get basic price data
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Failed to fetch price data"}
                
        except Exception as e:
            return {"error": str(e)}

# Keep backward compatibility
GeminiTradingAgent = PowerfulGeminiTradingAgent