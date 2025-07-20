#!/usr/bin/env python3
"""
Powerful Gemini AI Trading Agent - Refactored for Autonomous Decision Making
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import colorama
from colorama import Fore
from typing import Optional, Dict, List

from api.execute import token_addresses

colorama.init()

#!/usr/bin/env python3
"""
Powerful Gemini AI Trading Agent - Refactored for Autonomous Decision Making
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import colorama
from colorama import Fore
from typing import Optional, Dict, List

# Assuming these are defined elsewhere and imported
# from api.execute import token_addresses

# Mocking for standalone execution
token_addresses = {
    'ETH': '0x...', 'USDC': '0x...', 'WETH': '0x...', 'WBTC': '0x...',
    'SOL': '0x...', 'MATIC': '0x...', 'ARB': '0x...', 'OP': '0x...', 'USDbC': '0x...'
}


colorama.init()

class PowerfulGeminiTradingAgent:
    """Advanced Gemini AI trading agent with full API access and intelligent analysis"""

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
        print(f"{Fore.GREEN}✅ POWERFUL Gemini AI Trading Agent initialized with FULL CAPABILITIES{Fore.RESET}")

    def get_intelligent_analysis(self, portfolio_json: dict, market_prices_json: dict, news_json: dict, strategy_performance_json: list) -> dict:
        """
        🧠 CORE KAIROS AI DECISION ENGINE 🧠
        Analyzes all available data and returns a structured trading decision.
        """
        total_value = portfolio_json.get('total_value', 0)
        balances = portfolio_json.get('balances', [])
        
        if total_value == 0 or not balances:
            print(f"{Fore.YELLOW}⚠️ Portfolio is empty or has zero value. Returning HODL decision.{Fore.RESET}")
            return {
                "should_trade": False,
                "confidence_score": 0.0,
                "strategy_chosen": {"name": "hodl_empty_portfolio", "type": "hodl"},
                # ## CHANGE 1: Add default 'chain' to HODL case for schema consistency
                "trade_params": {"trade_type": "swap", "from_token": "USDC", "to_token": "ETH", "amount": 0.0, "chain": "ETH"},
                "reasoning": ["The current portfolio value is 0 and there are no balances available for trading.", "Therefore, the optimal decision is to HODL and wait for an opportunity to enter the market when funds become available."]
            }
        
        available_tokens = list(token_addresses.keys())
        allowed_strategy_types = ['momentum', 'arbitrage', 'dca', 'swing', 'scalping', 'hodl', 'custom']
        allowed_trade_types = ['buy', 'sell', 'swap']

        master_prompt = f"""
        You are Kairos AI, an expert quantitative cryptocurrency trading analyst. Your primary directive is to maximize portfolio value through intelligent, risk-managed trades. Your decisions are final and will be executed directly.

        Analyze the following real-time data packet to formulate a single, optimal trading decision.

        **1. Current Portfolio State:**
        ```json
        {json.dumps(portfolio_json, indent=2)}
        ```

        **2. Real-Time Market Prices:**
        ```json
        {json.dumps(market_prices_json, indent=2)}
        ```

        **3. Latest Crypto News & Sentiment:**
        ```json
        {json.dumps(news_json, indent=2)}
        ```

        **4. Historical Strategy Performance (Your Memory from the Database):**
        - `success_rate > 0.6` is a good strategy.
        - `success_rate < 0.4` is a bad strategy. Avoid it.
        ```json
        {json.dumps(strategy_performance_json, indent=2)}
        ```

        **🎯 YOUR TASK: FORMULATE THE NEXT TRADE**

        **IMPORTANT MULTI-CHAIN PORTFOLIO RULES:**
        - The portfolio contains tokens on multiple chains (e.g., 'ETH', 'Polygon', 'Solana').
        - When deciding a trade, you MUST specify the `chain` for the `from_token`.
        - Do NOT aggregate balances across different chains. A trade can only happen on one chain.

        **Constraint Checklist (MUST FOLLOW):**
        1.  `trade_type`: MUST be one of {allowed_trade_types}.
        2.  `strategy_type`: MUST be one of {allowed_strategy_types}.
        3.  `from_token` & `to_token`: MUST be chosen from this list: {available_tokens}.
        4.  `amount`: MUST be a positive float number > 0 for a trade, or 0.0 for a HODL.
        5.  `amount`: MUST be ≤ the available balance for the `from_token` on its specific `chain`.
        6.  `chain`: MUST be the specific blockchain network for the `from_token` (e.g., 'ETH', 'Solana', 'Polygon'). This is MANDATORY.

        **Decision Guidelines:**
        - **Critical Rule**: If portfolio `total_value` is 0 or the balance of a potential `from_token` is 0, you MUST decide to HODL. Set `should_trade` to false.
        - **Risk Management**: Never trade more than 25% of any single token's balance (on a specific chain) in one transaction.
        - **Chain Awareness**: Only trade tokens that exist on the same blockchain. Your `trade_params` must reflect this.
        - **Dynamic Sizing**: Calculate the trade `amount` based on confidence and risk. A confident trade might use 5-25% of the available `from_token` balance.
        - **Learning from Memory**: Prioritize strategies with a high `success_rate` from your historical performance.

        **REQUIRED OUTPUT FORMAT (Strict JSON):**
        {{
          "should_trade": "boolean",
          "confidence_score": "float",
          "strategy_chosen": {{
            "name": "strategy_name_from_your_analysis",
            "type": "one_of_{allowed_strategy_types}"
          }},
          "trade_params": {{
            "trade_type": "one_of_{allowed_trade_types}",
            "from_token": "token_from_available_list",
            "to_token": "token_from_available_list",
            "amount": "float_amount",
            "chain": "the_blockchain_network_for_the_trade"
          }},
          "reasoning": [
            "A step-by-step explanation of your thought process, referencing specific data points and the chosen chain."
          ]
        }}

        If you decide to HODL, set "should_trade" to false, "trade_type" to "swap", "from_token" to "USDC", "to_token" to "ETH", "amount" to 0.0, "chain" to "ETH", and explain why in "reasoning".
        """

        try:
            # I removed the print() statements from the f-string for cleaner execution
            print(f"{Fore.MAGENTA}🧠 Kairos AI: Analyzing market data and portfolio state...{Fore.RESET}")
            response = self.model.generate_content(master_prompt)
            decision = json.loads(response.text)
            strategy_name = decision.get('strategy_chosen', {}).get('name', 'Unknown')
            confidence = decision.get('confidence_score', 0) * 100

            print(f"{Fore.GREEN}✅ Kairos AI Decision: {strategy_name} (Confidence: {confidence:.1f}%){Fore.RESET}")
            print(f"{Fore.CYAN}🤔 AI Reasoning: {' '.join(decision.get('reasoning', []))}{Fore.RESET}")
            return decision

        except Exception as e:
            print(f"{Fore.RED}❌ Kairos AI Analysis Error: {e}{Fore.RESET}")
            if 'response' in locals():
                print(f"Raw response was: {getattr(response, 'text', 'No response text available')}")
            return {
                "should_trade": False,
                "confidence_score": 0.0,
                "strategy_chosen": {"name": "system_error", "type": "custom"},
                "reasoning": [f"An error occurred during AI analysis: {str(e)}", "Defaulting to HODL for safety."],
                # ## CHANGE 3: Add default 'chain' to error case for schema consistency
                "trade_params": {"trade_type": "swap", "from_token": "USDC", "to_token": "ETH", "amount": 0.0, "chain": "ETH"}
            }

# Keep old name for compatibility
GeminiTradingAgent = PowerfulGeminiTradingAgent