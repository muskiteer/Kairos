import os
import requests
import json
from dotenv import load_dotenv
from typing import Optional
import asyncio

load_dotenv()  # Load environment variables from .env file

# Constants
RECALL_SANDBOX_API_BASE = os.getenv("RECALL_SANDBOX_API_BASE", "https://api.sandbox.competitions.recall.network")
DEFAULT_API_KEY = os.getenv("RECALL_API_KEY")

async def get_user_api_keys(user_id: str = "default") -> dict:
    """Get user API keys from profile or fallback to defaults"""
    try:
        # Try to import profile module
        from api.profile import get_user_api_keys as profile_get_keys
        return await profile_get_keys(user_id)
    except Exception as e:
        print(f"⚠️ Could not get user API keys: {e}")
        # Fallback to environment variables
        return {
            "recall_api_key": DEFAULT_API_KEY or "",
            "coinpanic_api_key": os.getenv("COINPANIC_API_KEY", "")
        }

def calculate_token_usd_value(symbol: str, amount: float) -> float:
    """Calculate USD value for a token amount"""
    try:
        # Import token price function
        from api.token_price import get_token_price_json
        
        # Get current price
        price_data = get_token_price_json(symbol)
        if price_data and 'price' in price_data:
            price_usd = float(price_data['price'])
            usd_value = amount * price_usd
            return usd_value
        else:
            print(f"⚠️ Could not get price for {symbol}")
            return 0.0
            
    except Exception as e:
        print(f"⚠️ Error calculating USD value for {symbol}: {e}")
        return 0.0

def get_portfolio(user_id: str = "default"):
    """Get portfolio information from Recall API using user-specific API key"""
    
    # Get user API key (synchronous wrapper with proper async handling)
    try:
        # Check if we're already in an async context
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            # We're in an async context, use create_task
            task = loop.create_task(get_user_api_keys(user_id))
            # Since we can't await in a sync function, use fallback
            api_key = DEFAULT_API_KEY
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            try:
                api_keys = asyncio.run(get_user_api_keys(user_id))
                api_key = api_keys.get("recall_api_key") or DEFAULT_API_KEY
            except Exception as e:
                print(f"⚠️ Error getting API keys: {e}")
                api_key = DEFAULT_API_KEY
    except Exception as e:
        print(f"⚠️ Using default API key: {e}")
        api_key = DEFAULT_API_KEY
    
    if not api_key:
        return {
            "error": "No API key available",
            "message": "Please configure your Recall API key in your profile",
            "balances": [],
            "total_value": 0.0
        }
    
    url = f"{RECALL_SANDBOX_API_BASE}/api/agent/balances"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print(f"📡 Fetching portfolio for user '{user_id}' using default API key...")
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.ok:
            portfolio_data = resp.json()
            
            # ** FIX: Handle Recall API response structure properly **
            if isinstance(portfolio_data, dict):
                balances = portfolio_data.get('balances', [])
                
                # ** NEW: Calculate USD values using token prices **
                enriched_balances = []
                total_value = 0.0
                
                for balance in balances:
                    if isinstance(balance, dict):
                        symbol = balance.get('symbol', 'UNKNOWN')
                        amount = float(balance.get('amount', 0))
                        
                        if amount > 0:
                            # Get current USD price for this token
                            usd_value = calculate_token_usd_value(symbol, amount)
                            
                            enriched_balance = {
                                'symbol': symbol,
                                'amount': amount,
                                'usd_value': usd_value,
                                'chain': balance.get('specificChain', 'unknown'),
                                'tokenAddress': balance.get('tokenAddress', '')
                            }
                            enriched_balances.append(enriched_balance)
                            total_value += usd_value
                            
                            print(f"  💰 {symbol}: {amount:,.6f} (${usd_value:,.2f}) on {balance.get('specificChain', 'unknown')}")
                
                # Update the portfolio data with enriched balances and calculated total
                portfolio_data['balances'] = enriched_balances
                portfolio_data['total_value'] = total_value
                
                print(f"✅ Successfully enriched portfolio with {len(enriched_balances)} assets. Total: ${total_value:,.2f}")
                return portfolio_data
            else:
                return {
                    "error": "Invalid portfolio data structure",
                    "balances": [],
                    "total_value": 0.0
                }
        else:
            return {
                "error": "Failed to get portfolio",
                "status": resp.status_code,
                "details": resp.text,
                "balances": [],
                "total_value": 0.0
            }
    except Exception as e:
        return {
            "error": "Exception occurred while fetching portfolio",
            "details": str(e),
            "balances": [],
            "total_value": 0.0
        }

if __name__ == "__main__":
    portfolio = get_portfolio()
    print(json.dumps(portfolio))  # ✅ Valid JSON output
