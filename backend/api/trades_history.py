import os
import requests
import json
from dotenv import load_dotenv
from typing import Optional

load_dotenv()  # Load environment variables from .env file

# Constants
RECALL_SANDBOX_API_BASE = os.getenv("RECALL_SANDBOX_API_BASE", "https://api.competitions.recall.network")
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

def get_portfolio(user_id: str = "default"):
    """Get portfolio information from Recall API using user-specific API key"""
    
    # Get user API key (synchronous wrapper with proper async handling)
    try:
        # Check if we're already in an async context
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            # We're in an async context, use fallback for now
            api_key = DEFAULT_API_KEY
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            api_keys = asyncio.run(get_user_api_keys(user_id))
            api_key = api_keys.get("recall_api_key") or DEFAULT_API_KEY
    except Exception as e:
        print(f"⚠️ Using default API key: {e}")
        api_key = DEFAULT_API_KEY
    
    if not api_key:
        return {
            "error": "No API key available",
            "message": "Please configure your Recall API key in your profile",
            "trades": []
        }
    
    url = f"{RECALL_SANDBOX_API_BASE}/api/agent/trades"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print(f"📊 Fetching trades for user {user_id} with API key: {api_key[:10]}...")
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.ok:
            data = resp.json()
            print(f"✅ Successfully fetched {len(data.get('trades', []))} trades")
            return data
        else:
            print(f"❌ API Error: {resp.status_code} - {resp.text}")
            return {
                "error": "Failed to get trades",
                "status": resp.status_code,
                "details": resp.text,
                "trades": []
            }
    except Exception as e:
        return {
            "error": "Exception occurred while fetching portfolio",
            "details": str(e)
        }

if __name__ == "__main__":
    portfolio = get_portfolio()
    print(json.dumps(portfolio))  # ✅ Valid JSON output
