#!/usr/bin/env python3
"""
Kairos Autonomous Trading Agent - Enhanced for Real Trading with Better Error Handling
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json
import traceback

# Import dependencies with error handling
try:
    from agent.gemini_agent import PowerfulGeminiTradingAgent
    from api.portfolio import get_portfolio
    from api.execute import trade_exec, token_addresses
    from database.supabase_client import supabase_client
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

try:
    from agent.coinpanic_api import get_trending_news
except ImportError:
    print("⚠️ CoinPanic API not available, using fallback news")
    def get_trending_news(limit=10):
        return {
            "results": [
                {"title": "Crypto market shows positive momentum", "kind": "news"},
                {"title": "DeFi protocols report increased activity", "kind": "news"}
            ]
        }

try:
    from api.token_price import get_token_price_json
except ImportError:
    print("⚠️ Token price API not available, using fallback")
    def get_token_price_json(symbol, chain):
        import requests
        try:
            coingecko_ids = {
                'USDC': 'usd-coin', 'WETH': 'weth', 'WBTC': 'wrapped-bitcoin',
                'ETH': 'ethereum', 'UNI': 'uniswap', 'LINK': 'chainlink',
                'AAVE': 'aave', 'MATIC': 'matic-network', 'SOL': 'solana'
            }
            coin_id = coingecko_ids.get(symbol, symbol.lower())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = data.get(coin_id, {}).get('usd', 0)
                return {'price': price, 'error': None}
            return {'price': 0, 'error': 'API failed'}
        except Exception as e:
            return {'price': 0, 'error': str(e)}

class KairosAutonomousAgent:
    """Enhanced Autonomous Trading Agent with Real-time Decision Making"""

    def __init__(self, user_id: str, session_id: str, duration_minutes: int):
        self.user_id = user_id
        self.session_id = session_id
        self.duration_minutes = duration_minutes
        self.end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.start_time = datetime.utcnow()
        self.is_running = False
        self.trade_count = 0
        self.successful_trades = 0
        self.total_pnl = 0.0
        self.last_portfolio_value = 0.0
        
        # Initialize Gemini AI agent
        try:
            self.gemini_agent = PowerfulGeminiTradingAgent(user_id=self.user_id)
            print(f"🤖 Gemini AI agent initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini agent: {e}")
            self.gemini_agent = None
        
        print(f"🤖 Kairos Autonomous Agent initialized for session {self.session_id[:8]}...")
        print(f"⏰ Will run for {duration_minutes} minutes until {self.end_time.strftime('%H:%M:%S UTC')}")

    async def run_trading_loop(self):
        """Main autonomous trading loop with enhanced error handling and logging."""
        self.is_running = True
        cycle_count = 0
        
        print(f"✅ 🚀 Autonomous trading loop STARTED for session {self.session_id[:8]}...")
        print(f"⏰ Duration: {self.duration_minutes} minutes")
        print(f"🎯 End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        # Log session start
        try:
            supabase_client.update_trading_session_metrics(
                session_id=self.session_id,
                portfolio_value=self.last_portfolio_value,
                trade_count=0,
                successful_trades=0
            )
        except Exception as db_error:
            print(f"⚠️ Database logging error (continuing): {db_error}")

        while self.is_running and datetime.utcnow() < self.end_time:
            try:
                cycle_count += 1
                remaining_time = self.end_time - datetime.utcnow()
                remaining_minutes = remaining_time.total_seconds() / 60
                
                print(f"\n{'='*80}")
                print(f"🔄 AUTONOMOUS CYCLE #{cycle_count} - Session {self.session_id[:8]}...")
                print(f"⏰ Time remaining: {remaining_minutes:.1f} minutes")
                print(f"📊 Trades so far: {self.trade_count} (Success: {self.successful_trades})")
                print(f"💰 Total P&L: ${self.total_pnl:+.4f}")
                print(f"{'='*80}")
                
                # Execute one complete decision cycle
                await self._autonomous_decision_cycle()
                
                # Dynamic wait time based on remaining duration
                if remaining_minutes > 30:
                    wait_time = 300  # 5 minutes for long sessions
                elif remaining_minutes > 10:
                    wait_time = 180  # 3 minutes for medium sessions
                else:
                    wait_time = 60   # 1 minute for final phase
                
                if remaining_minutes > (wait_time / 60):
                    print(f"⏱️ Waiting {wait_time//60} minutes before next cycle...")
                    await asyncio.sleep(wait_time)
                else:
                    # Final cycle - wait until end
                    final_wait = remaining_time.total_seconds()
                    if final_wait > 0:
                        print(f"⏱️ Final wait: {final_wait:.0f} seconds until session end...")
                        await asyncio.sleep(final_wait)
                    break

            except Exception as e:
                print(f"❌ CRITICAL ERROR in trading cycle #{cycle_count}: {e}")
                traceback.print_exc()
                print("🔄 Continuing to next cycle after 60-second recovery pause...")
                await asyncio.sleep(60)

        # Session completion
        print(f"\n🏁 AUTONOMOUS TRADING SESSION COMPLETED!")
        print(f"📊 Final Stats:")
        print(f"   • Total Cycles: {cycle_count}")
        print(f"   • Total Trades: {self.trade_count}")
        print(f"   • Successful Trades: {self.successful_trades}")
        print(f"   • Success Rate: {(self.successful_trades/max(self.trade_count,1)*100):.1f}%")
        print(f"   • Total P&L: ${self.total_pnl:+.4f}")
        print(f"   • Session Duration: {self.duration_minutes} minutes")
        
        self.is_running = False
        await self._finalize_session()

    async def _autonomous_decision_cycle(self):
        """Complete decision cycle: Analyze → Decide → Execute → Learn"""
        try:
            print("\n🔍 STEP 1: Gathering market intelligence...")
            
            # Get current portfolio state with enhanced error handling
            portfolio_state = self._analyze_current_portfolio()
            if not portfolio_state or portfolio_state.get('error'):
                print(f"⚠️ Portfolio analysis failed: {portfolio_state.get('error', 'Unknown error')}")
                return
            
            current_value = portfolio_state.get('total_value', 0)
            self.last_portfolio_value = current_value
            
            print(f"💼 Current portfolio value: ${current_value:,.2f}")
            print(f"🏦 Active assets: {len(portfolio_state.get('balances', []))}")
            
            # Get market data
            market_prices = self._get_market_prices_from_portfolio(portfolio_state)
            news_data = get_trending_news(limit=5)
            strategy_performance = self._get_strategy_performance()
            
            print(f"📊 Market prices loaded: {len(market_prices)} tokens")
            print(f"📰 News items loaded: {len(news_data.get('results', []))}")
            print(f"🧠 Strategy memory: {len(strategy_performance)} past strategies")

            # AI Decision Making
            print("\n🧠 STEP 2: AI Analysis & Decision Making...")
            
            if not self.gemini_agent:
                print("❌ Gemini agent not available, skipping this cycle")
                return
                
            ai_decision = self.gemini_agent.get_intelligent_analysis(
                portfolio_state, market_prices, news_data, strategy_performance
            )
            
            if not ai_decision:
                print("❌ AI decision failed, skipping this cycle")
                return
            
            should_trade = ai_decision.get("should_trade", False)
            confidence = ai_decision.get("confidence_score", 0) * 100
            strategy = ai_decision.get("strategy_chosen", {}).get("name", "unknown")
            
            print(f"🎯 AI Decision: {strategy}")
            print(f"📈 Should trade: {should_trade}")
            print(f"🎪 Confidence: {confidence:.1f}%")
            
            # Trade Execution
            execution_result = {"success": False, "attempted": False}
            
            if should_trade:
                print("\n💱 STEP 3: Trade Execution...")
                trade_params = ai_decision.get('trade_params', {})
                
                # Validate trade before execution
                is_valid, validation_error = self._sanity_check_trade(trade_params, portfolio_state)
                
                if is_valid:
                    execution_result = self._execute_autonomous_trade(trade_params)
                    execution_result["attempted"] = True
                    
                    if execution_result.get("success"):
                        self.successful_trades += 1
                        trade_pnl = execution_result.get("pnl", 0)
                        self.total_pnl += trade_pnl
                        print(f"✅ Trade successful! P&L: ${trade_pnl:+.4f}")
                    else:
                        print(f"❌ Trade failed: {execution_result.get('error', 'Unknown error')}")
                    
                    self.trade_count += 1
                else:
                    print(f"🚫 Trade blocked by validation: {validation_error}")
                    execution_result = {"success": False, "error": validation_error, "attempted": False}
            else:
                print("💤 AI decided to HODL this cycle")
            
            # Learning & Database Updates
            print("\n📚 STEP 4: Learning & Data Persistence...")
            self._learn_from_decision(ai_decision, execution_result, {
                "prices": market_prices, 
                "news": news_data,
                "portfolio_value": current_value
            })
            
            # Update session metrics
            try:
                supabase_client.update_trading_session_metrics(
                    session_id=self.session_id,
                    portfolio_value=current_value,
                    trade_count=self.trade_count,
                    successful_trades=self.successful_trades,
                    confidence=confidence/100,
                    trade_volume=trade_params.get("amount", 0) if should_trade else 0
                )
            except Exception as db_error:
                print(f"⚠️ Database update error: {db_error}")
            
            print("✅ Decision cycle completed successfully!")

        except Exception as e:
            print(f"❌ ERROR in decision cycle: {e}")
            traceback.print_exc()

    def _execute_autonomous_trade(self, trade_params: Dict) -> Dict:
        """Execute a trade with comprehensive error handling and logging."""
        try:
            from_token = trade_params.get("from_token", "").upper()
            to_token = trade_params.get("to_token", "").upper()
            amount = float(trade_params.get("amount", 0))
            chain = trade_params.get("chain", "ethereum")
            
            print(f"🔥 Executing: {amount:.6f} {from_token} → {to_token} on {chain}")
            
            # Get token addresses
            from_address = token_addresses.get(from_token)
            to_address = token_addresses.get(to_token)

            if not from_address or not to_address:
                error_msg = f"Unsupported tokens: {from_token} or {to_token}"
                print(f"❌ {error_msg}")
                return {"success": False, "error": error_msg, "attempted": True}
            
            print(f"🔗 From address: {from_address[:10]}...")
            print(f"🔗 To address: {to_address[:10]}...")
            
            # Record pre-trade portfolio value
            pre_trade_portfolio = self._analyze_current_portfolio()
            pre_trade_value = pre_trade_portfolio.get('total_value', 0)
            
            # Execute the trade
            print("📡 Sending trade to execution engine...")
            trade_result = trade_exec(from_address, to_address, amount, chain)
            
            if not trade_result:
                return {"success": False, "error": "No response from trade execution", "attempted": True}
            
            # Check for errors in result
            if "error" in trade_result:
                error_msg = trade_result.get("error", "Unknown trade error")
                print(f"❌ Trade execution error: {error_msg}")
                return {"success": False, "error": error_msg, "attempted": True}
            
            # Check for success indicators
            success_indicators = [
                "txHash" in trade_result,
                "transactionHash" in trade_result,
                "transaction" in trade_result,
                trade_result.get("success") == True
            ]
            
            if any(success_indicators):
                # Calculate P&L
                time.sleep(2)  # Brief wait for portfolio to update
                post_trade_portfolio = self._analyze_current_portfolio()
                post_trade_value = post_trade_portfolio.get('total_value', 0)
                trade_pnl = post_trade_value - pre_trade_value
                
                tx_hash = (trade_result.get("txHash") or 
                          trade_result.get("transactionHash") or 
                          trade_result.get("transaction", {}).get("txHash", "unknown"))
                
                print(f"✅ Trade successful!")
                print(f"🧾 TxHash: {tx_hash}")
                print(f"💰 P&L: ${trade_pnl:+.4f}")
                
                return {
                    "success": True,
                    "result": trade_result,
                    "tx_hash": tx_hash,
                    "pnl": trade_pnl,
                    "pre_value": pre_trade_value,
                    "post_value": post_trade_value,
                    "attempted": True
                }
            else:
                error_msg = f"Trade result unclear: {trade_result}"
                print(f"⚠️ {error_msg}")
                return {"success": False, "error": error_msg, "attempted": True}

        except Exception as e:
            error_msg = f"Trade execution exception: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return {"success": False, "error": error_msg, "attempted": True}

    def _sanity_check_trade(self, trade_params: Dict, portfolio: Dict) -> tuple[bool, Optional[str]]:
        """Enhanced trade validation with detailed logging."""
        print(f"🔬 Validating trade parameters...")
        
        if not isinstance(trade_params, dict):
            return False, "Trade parameters must be a dictionary"

        from_token = trade_params.get('from_token', '').upper()
        to_token = trade_params.get('to_token', '').upper()
        chain = trade_params.get('chain', '')
        
        try:
            amount_to_trade = float(trade_params.get('amount', 0))
        except (ValueError, TypeError):
            return False, f"Invalid amount: {trade_params.get('amount')}"

        # Basic parameter validation
        if not from_token or not to_token or not chain or amount_to_trade <= 0:
            return False, f"Missing required parameters: from_token={from_token}, to_token={to_token}, chain={chain}, amount={amount_to_trade}"

        # Check if tokens exist in our supported list
        if from_token not in token_addresses or to_token not in token_addresses:
            return False, f"Unsupported tokens. Supported: {list(token_addresses.keys())}"

        # Balance verification with chain specificity
        available_balance = 0.0
        balances_found = []

        for token_data in portfolio.get('balances', []):
            if (isinstance(token_data, dict) and 
                token_data.get('symbol', '').upper() == from_token):
                
                token_chain = token_data.get('chain', '').lower()
                token_amount = float(token_data.get('amount', 0))
                
                balances_found.append({
                    'chain': token_chain,
                    'amount': token_amount
                })
                
                # Chain matching (flexible)
                chain_match = (
                    chain.lower() == token_chain or
                    (chain.lower() == 'ethereum' and token_chain in ['ethereum', 'eth', 'evm']) or
                    (chain.lower() == 'polygon' and token_chain in ['polygon', 'matic']) or
                    (chain.lower() == 'base' and token_chain in ['base']) or
                    (chain.lower() == 'solana' and token_chain in ['solana', 'sol'])
                )
                
                if chain_match:
                    available_balance += token_amount

        print(f"💰 Balance check for {from_token}:")
        for balance in balances_found:
            print(f"   • {balance['chain']}: {balance['amount']:.6f}")
        print(f"   • Available on {chain}: {available_balance:.6f}")
        print(f"   • Requested amount: {amount_to_trade:.6f}")

        if available_balance < amount_to_trade:
            return False, f"Insufficient {from_token} balance on {chain}. Available: {available_balance:.6f}, Requested: {amount_to_trade:.6f}"

        # Risk management - don't trade more than 50% of any token
        if amount_to_trade > (available_balance * 0.5):
            print(f"⚠️ WARNING: Trading {amount_to_trade:.6f} is >50% of {from_token} balance ({available_balance:.6f})")

        print("✅ Trade validation passed")
        return True, None

    def _analyze_current_portfolio(self) -> Dict:
        """Get current portfolio with enhanced error handling and price enrichment."""
        print("📊 Analyzing current portfolio...")
        
        try:
            # Get raw portfolio data
            portfolio_raw = get_portfolio(user_id=self.user_id)
            
            if isinstance(portfolio_raw, dict) and 'error' in portfolio_raw:
                print(f"⚠️ Portfolio API error: {portfolio_raw.get('error')}")
                return {"total_value": 0.0, "balances": [], "error": portfolio_raw.get('error')}
            
            balances = portfolio_raw.get('balances', []) if isinstance(portfolio_raw, dict) else []
            
            if not balances:
                print("⚠️ No balances found in portfolio")
                return {"total_value": 0.0, "balances": []}
                
            valid_balances = []
            calculated_total = 0.0
            
            print(f"🔍 Processing {len(balances)} balance entries...")
            
            for balance in balances:
                if not isinstance(balance, dict):
                    continue
                    
                symbol = balance.get('symbol', '').upper()
                chain = balance.get('specificChain', balance.get('chain', 'unknown'))
                
                try:
                    amount = float(balance.get('amount', 0))
                    if amount <= 0:
                        continue
                    
                    # Get fresh price
                    price_data = get_token_price_json(symbol, chain)
                    price = float(price_data.get('price', 0)) if price_data and not price_data.get('error') else 0
                    usd_value = amount * price
                    
                    valid_balances.append({
                        'symbol': symbol,
                        'amount': amount,
                        'usd_value': usd_value,
                        'chain': chain,
                        'price': price
                    })
                    
                    calculated_total += usd_value
                    print(f"   💰 {symbol}: {amount:.6f} @ ${price:.4f} = ${usd_value:.2f} ({chain})")
                    
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Error processing {symbol}: {e}")
                    continue
            
            print(f"✅ Portfolio analyzed: {len(valid_balances)} assets, ${calculated_total:.2f} total value")
            
            return {
                "total_value": calculated_total,
                "balances": valid_balances,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Portfolio analysis error: {e}")
            traceback.print_exc()
            return {"total_value": 0.0, "balances": [], "error": str(e)}

    def _get_market_prices_from_portfolio(self, portfolio: Dict) -> Dict:
        """Extract market prices from portfolio data for AI analysis."""
        prices = {}
        
        for asset in portfolio.get('balances', []):
            symbol = asset.get('symbol')
            price = asset.get('price', 0)
            if symbol and price > 0:
                prices[symbol] = price
        
        print(f"📊 Market prices extracted: {len(prices)} tokens")
        return prices

    def _get_strategy_performance(self) -> List[Dict]:
        """Get historical strategy performance for AI learning."""
        try:
            strategies = supabase_client.get_strategies_for_session(self.session_id)
            print(f"🧠 Retrieved {len(strategies)} historical strategies")
            return strategies
        except Exception as e:
            print(f"⚠️ Error getting strategy performance: {e}")
            return []

    def _learn_from_decision(self, decision: Dict, execution: Dict, market_data: Dict):
        """Enhanced learning with comprehensive data persistence."""
        try:
            print("📚 Persisting AI decision and learning data...")
            
            strategy_chosen = decision.get("strategy_chosen", {})
            strategy_name = strategy_chosen.get("name", "unknown_strategy")
            strategy_type = strategy_chosen.get("type", "custom")
            
            # Store strategy in database
            try:
                strategy_id = supabase_client.upsert_strategy(
                    session_id=self.session_id,
                    strategy_name=strategy_name,
                    strategy_type=strategy_type
                )
                print(f"💾 Strategy saved: {strategy_name} (ID: {strategy_id})")
            except Exception as db_error:
                print(f"⚠️ Strategy storage error: {db_error}")
                strategy_id = None

            # Log trade if attempted
            if execution.get("attempted", False):
                try:
                    trade_params = decision.get("trade_params", {})
                    trade_data = {
                        "trade_type": trade_params.get("trade_type", "swap"),
                        "from_token": trade_params.get("from_token"),
                        "to_token": trade_params.get("to_token"),
                        "amount": trade_params.get("amount", 0),
                        "success": execution.get("success", False),
                        "confidence": decision.get("confidence_score", 0),
                        "market_conditions": market_data,
                        "tx_hash": execution.get("tx_hash"),
                        "pnl": execution.get("pnl", 0)
                    }
                    
                    reasoning = "\n".join(decision.get("reasoning", []))
                    pre_value = execution.get("pre_value", 0)
                    post_value = execution.get("post_value", 0)
                    
                    trade_id = supabase_client.log_trade_with_metrics(
                        session_id=self.session_id,
                        trade_data=trade_data,
                        reasoning=reasoning,
                        pre_portfolio_value=pre_value,
                        post_portfolio_value=post_value
                    )
                    
                    print(f"📊 Trade logged: {trade_id}")
                    
                except Exception as trade_log_error:
                    print(f"⚠️ Trade logging error: {trade_log_error}")

            # Update strategy performance
            if strategy_id:
                try:
                    supabase_client.update_strategy_performance(
                        strategy_id=strategy_id,
                        success=execution.get("success", False),
                        performance_data={
                            "last_execution": execution,
                            "market_conditions": market_data,
                            "session_timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    print("📈 Strategy performance updated")
                except Exception as perf_error:
                    print(f"⚠️ Performance update error: {perf_error}")

            print("✅ Learning cycle completed")

        except Exception as e:
            print(f"❌ Learning error: {e}")
            traceback.print_exc()

    async def _finalize_session(self):
        """Finalize the trading session and generate reports."""
        try:
            print("\n🏁 Finalizing trading session...")
            
            # Get final portfolio state
            final_portfolio = self._analyze_current_portfolio()
            final_value = final_portfolio.get('total_value', 0)
            
            # Calculate final P&L
            session_duration = datetime.utcnow() - self.start_time
            duration_hours = session_duration.total_seconds() / 3600
            
            print(f"📊 SESSION SUMMARY:")
            print(f"   • Duration: {duration_hours:.1f} hours")
            print(f"   • Total trades: {self.trade_count}")
            print(f"   • Successful trades: {self.successful_trades}")
            print(f"   • Success rate: {(self.successful_trades/max(self.trade_count,1)*100):.1f}%")
            print(f"   • Final portfolio value: ${final_value:,.2f}")
            print(f"   • Total P&L: ${self.total_pnl:+.4f}")
            
            # Update database with final results
            try:
                supabase_client.end_trading_session(
                    session_id=self.session_id,
                    final_portfolio=final_portfolio,
                    total_pnl=self.total_pnl
                )
                print("✅ Session finalized in database")
            except Exception as db_error:
                print(f"⚠️ Database finalization error: {db_error}")
            
            print("🎉 Autonomous trading session completed successfully!")
            
        except Exception as e:
            print(f"❌ Session finalization error: {e}")
            traceback.print_exc()