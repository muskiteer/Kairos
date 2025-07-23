# Corrected and simplified api/portfolio.py

import os
import requests
import json
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Constants
RECALL_SANDBOX_API_BASE = os.getenv("RECALL_SANDBOX_API_BASE", "https://api.competitions.recall.network")
DEFAULT_API_KEY = os.getenv("RECALL_API_KEY")

async def get_user_api_keys(user_id: str = "default") -> dict:
    """Get user API keys from profile or fallback to defaults."""
    try:
        from api.profile import get_user_api_keys as profile_get_keys
        return await profile_get_keys(user_id)
    except Exception as e:
        # Fallback for simplicity if profile module is complex/unavailable
        return {"recall_api_key": DEFAULT_API_KEY}

def get_portfolio(user_id: str = "default"):
    """
    Fetches the raw portfolio data from the Recall API.
    It no longer calculates USD values; that is the agent's responsibility.
    """
    api_key = DEFAULT_API_KEY  # Simplified API key handling for clarity
    
    if not api_key:
        return {"error": "API key not available"}
    
    url = f"{RECALL_SANDBOX_API_BASE}/api/agent/balances"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print(f"📡 Fetching raw portfolio for user '{user_id}'...")
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()  # Raise an exception for bad status codes
        
        portfolio_data = resp.json()
        print(f"✅ Successfully fetched raw data for {len(portfolio_data.get('balances', []))} assets.")
        return portfolio_data

    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error fetching portfolio: {e.response.status_code} - {e.response.text}")
        return {"error": "Failed to get portfolio", "details": e.response.text}
    except Exception as e:
        print(f"❌ Exception occurred while fetching portfolio: {e}")
        return {"error": "Exception occurred", "details": str(e)}

if __name__ == "__main__":
    portfolio_data = get_portfolio()
    print(json.dumps(portfolio_data, indent=2))