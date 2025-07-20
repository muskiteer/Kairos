#!/usr/bin/env python3
"""
Kairos Autonomous Trading Agent - Refactored for Robustness
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from agent.gemini_agent import PowerfulGeminiTradingAgent
from api.portfolio import get_portfolio
from api.token_price import get_token_price_json
from api.execute import trade_exec, token_addresses
from agent.coinpanic_api import get_trending_news
from database.supabase_client import supabase_client

class KairosAutonomousAgent:
    """Autonomous Trading Agent with Full AI Decision Making"""

    def __init__(self, user_id: str, session_id: str, duration_minutes: int):
        self.user_id = user_id
        self.session_id = session_id
        self.end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.gemini_agent = PowerfulGeminiTradingAgent(user_id=self.user_id)
        self.is_running = False
        print(f"🤖 Kairos Autonomous Agent initialized for session {self.session_id}")

    async def run_trading_loop(self):
        """Main autonomous trading loop."""
        self.is_running = True
        print(f"✅ Autonomous trading loop started. Will run until {self.end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        while self.is_running and datetime.utcnow() < self.end_time:
            try:
                print("\n" + "="*80)
                print(f"🔄 Starting new autonomous cycle for session {self.session_id[:8]}...")
                await self._autonomous_decision_cycle()
                print("="*80)
                wait_time = 180
                print(f"⏱️ Next cycle in {wait_time // 60} minutes...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                print(f"❌ CRITICAL ERROR in trading loop: {e}")
                await asyncio.sleep(60)

        print(f"🏁 Autonomous trading session {self.session_id} completed.")
        self.is_running = False

    async def _autonomous_decision_cycle(self):
        """Implements the full Perceive -> Reason & Decide -> Act -> Learn workflow."""
        try:
            print("\n🔍 Step 1: Gathering market intelligence and portfolio state...")
            portfolio_state = self._analyze_current_portfolio()
            market_prices = self._get_all_market_prices()
            news_data = get_trending_news(limit=10)
            strategy_performance = supabase_client.get_strategies_for_session(self.session_id)
            print(f"🧠 Loading {len(strategy_performance)} past strategies from memory...")

            print("\n🧠 Step 2: Querying Kairos AI for intelligent decision...")
            ai_decision = self.gemini_agent.get_intelligent_analysis(
                portfolio_state, market_prices, news_data, strategy_performance
            )

            execution_result = {"success": False, "error": "AI decided not to trade."}
            if ai_decision.get("should_trade"):
                print("\n🎯 Step 3: Validating and Executing AI's chosen trade...")
                is_valid, validation_error = self._sanity_check_trade(ai_decision.get('trade_params', {}), portfolio_state)
                if is_valid:
                    execution_result = self._execute_autonomous_trade(ai_decision['trade_params'])
                else:
                    print(f"❌ Trade Aborted by Sanity Check: {validation_error}")
                    ai_decision.setdefault('reasoning', []).append(f"Trade Aborted: {validation_error}")
                    execution_result = {"success": False, "error": validation_error}
            
            print("\n📚 Step 4: Learning from decision and updating knowledge base...")
            self._learn_from_decision(ai_decision, execution_result, {"prices": market_prices, "news": news_data})

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ ERROR in decision cycle: {e}")

    def _execute_autonomous_trade(self, trade_params: Dict) -> Dict:
        """Executes a trade and returns the result."""
        try:
            from_token = trade_params["from_token"]
            to_token = trade_params["to_token"]
            amount = float(trade_params["amount"])
            from_address = token_addresses.get(from_token.upper())
            to_address = token_addresses.get(to_token.upper())

            if not from_address or not to_address:
                raise ValueError(f"Unsupported token(s): {from_token}, {to_token}")
            
            print(f"🔥 Executing trade: {amount:.6f} {from_token} -> {to_token}")
            trade_result = trade_exec(from_address, to_address, amount)

            if trade_result and "transaction" in trade_result and "txHash" in trade_result["transaction"]:
                print("✅ Trade successful.")
                return {"success": True, "result": trade_result}
            else:
                error = trade_result.get("error", "Unknown error") if trade_result else "Execution failed."
                print(f"❌ Trade failed: {error}")
                return {"success": False, "error": error}
        except Exception as e:
            print(f"❌ CRITICAL EXECUTION ERROR: {e}")
            return {"success": False, "error": str(e)}

    def _learn_from_decision(self, decision: Dict, execution: Dict, market_data: Dict):
        """Persists the AI's decision and trade outcome to the database."""
        try:
            print("💾 Persisting decision and outcome to Supabase...")
            strategy_chosen = decision.get("strategy_chosen", {})
            strategy_name = strategy_chosen.get("name", "unknown_ai_strategy")
            strategy_type = strategy_chosen.get("type", "custom")  # Get the type from AI decision
            
            # ** FIX: Pass both name and type to upsert_strategy **
            strategy_id = supabase_client.upsert_strategy(
                session_id=self.session_id, 
                strategy_name=strategy_name,
                strategy_type=strategy_type
            )

            # ** FIX: Only log to the 'trades' table if a trade was actually attempted **
            if decision.get("should_trade") and execution.get("attempted", False):
                trade_params = decision.get("trade_params", {})
                supabase_client.log_trade_with_metrics(
                    session_id=self.session_id,
                    trade_data={
                        "trade_type": trade_params.get("trade_type", "swap"),
                        "from_token": trade_params.get("from_token"),
                        "to_token": trade_params.get("to_token"),
                        "amount": trade_params.get("amount", 0),
                        "success": execution.get("success", False),
                        "confidence": decision.get("confidence_score"),
                        "market_conditions": market_data
                    },
                    reasoning="\n".join(decision.get("reasoning", [])),
                    pre_portfolio_value=0, post_portfolio_value=0
                )
            
            if strategy_id and strategy_id not in ["failed_to_save", "unknown_id"]:
                supabase_client.update_strategy_performance(
                    strategy_id=strategy_id,
                    success=execution.get("success", False),
                    performance_data={"last_execution_result": execution}
                )
                print("✅ Learning cycle complete. Strategy performance updated.")
            else:
                print("✅ Learning cycle complete (strategy logging had issues)")
                
        except Exception as e:
            print(f"❌ DATABASE LOGGING ERROR: {e}")
            print("🔄 Continuing autonomous trading despite logging error...")
            import traceback
            traceback.print_exc()

    def _sanity_check_trade(self, trade_params: Dict, portfolio: Dict) -> tuple[bool, Optional[str]]:
        """Performs critical pre-flight checks on the AI's decided trade."""
        print(f"🔬 Performing sanity check on trade: {trade_params}")
        if not isinstance(trade_params, dict):
            return False, "AI returned invalid trade_params (not a dictionary)."

        from_token = trade_params.get('from_token')
        try:
            amount_to_trade = float(trade_params.get('amount', 0))
        except (ValueError, TypeError):
             return False, f"Invalid trade amount from AI: {trade_params.get('amount')}"

        if not from_token or amount_to_trade <= 0:
            return False, "Invalid trade parameters (missing token or zero/negative amount)."

        # ** FIX: Aggregate balances for the same token across all chains **
        total_available_balance = 0.0
        chain_specific_balances = []
        
        for token_data in portfolio.get('balances', []):
            if isinstance(token_data, dict) and token_data.get('symbol') == from_token:
                balance_amount = float(token_data.get('amount', 0))
                total_available_balance += balance_amount
                chain_specific_balances.append({
                    'chain': token_data.get('chain', 'unknown'),
                    'amount': balance_amount,
                    'usd_value': token_data.get('usd_value', 0)
                })
        
        print(f"💰 Multi-Chain Balance Check for {from_token}:")
        for chain_balance in chain_specific_balances:
            print(f"  - {chain_balance['chain']}: {chain_balance['amount']:,.6f} {from_token}")
        print(f"  - TOTAL AVAILABLE: {total_available_balance:,.6f} {from_token}")
        print(f"  - AI WANTS TO TRADE: {amount_to_trade:,.6f} {from_token}")

        if total_available_balance < amount_to_trade:
            return False, f"Insufficient total balance for {from_token}. Available: {total_available_balance:.6f}, Requested: {amount_to_trade:.6f}"

        # ** ADDITIONAL CHECK: Warn if trade amount is > 50% of total balance **
        if amount_to_trade > (total_available_balance * 0.5):
            print(f"⚠️ WARNING: Trading {amount_to_trade:.6f} is more than 50% of total {from_token} balance ({total_available_balance:.6f})")

        print("✅ Sanity check passed.")
        return True, None

    def _analyze_current_portfolio(self) -> Dict:
        """Analyzes portfolio state and returns a structured dictionary."""
        try:
            portfolio_raw = get_portfolio(user_id=self.user_id)
            
            # ** FIX: Handle multiple possible structures for portfolio data **
            if isinstance(portfolio_raw, dict) and 'error' in portfolio_raw:
                print(f"⚠️ Portfolio API error: {portfolio_raw.get('error')}")
                return {"total_value": 0.0, "balances": [], "error": portfolio_raw.get('error')}
            
            balances = []
            total_value = 0.0
            
            if isinstance(portfolio_raw, dict):
                balances = portfolio_raw.get('balances', [])
                total_value = portfolio_raw.get('total_value', 0.0)
            elif isinstance(portfolio_raw, list):
                balances = portfolio_raw
                
            # Validate and clean balance data
            valid_balances = []
            calculated_total = 0.0
            
            if balances:
                for balance in balances:
                    if isinstance(balance, dict):
                        # Ensure required fields exist
                        symbol = balance.get('symbol', 'UNKNOWN')
                        amount = balance.get('amount', 0)
                        usd_value = balance.get('usd_value', 0)
                        
                        try:
                            amount_float = float(amount)
                            usd_value_float = float(usd_value)
                            
                            if amount_float > 0:  # Only include tokens with positive balance
                                valid_balance = {
                                    'symbol': symbol,
                                    'amount': amount_float,
                                    'usd_value': usd_value_float
                                }
                                valid_balances.append(valid_balance)
                                calculated_total += usd_value_float
                                
                        except (ValueError, TypeError):
                            continue
        
            # Use calculated total if original was 0
            if total_value == 0.0:
                total_value = calculated_total
                
            print(f"💵 Calculated portfolio value: ${total_value:.2f}")
            return {"total_value": total_value, "balances": valid_balances}
            
        except Exception as e:
            print(f"⚠️ Could not analyze portfolio: {e}")
            import traceback
            traceback.print_exc()
            return {"total_value": 0.0, "balances": [], "error": str(e)}

    def _get_all_market_prices(self) -> Dict:
        """Fetches prices for all tradable tokens."""
        prices = {}
        for token in token_addresses.keys():
            try:
                price_data = get_token_price_json(token)
                prices[token] = price_data.get('price', 0) if price_data else 0
            except Exception:
                prices[token] = 0
        return prices