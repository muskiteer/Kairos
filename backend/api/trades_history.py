import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Constants
RECALL_SANDBOX_API_BASE = os.getenv("RECALL_SANDBOX_API_BASE", "https://api.sandbox.competitions.recall.network")
API_KEY = os.getenv("RECALL_API_KEY")

def get_portfolio():
    """Get portfolio information from Recall API"""
    url = f"{RECALL_SANDBOX_API_BASE}/api/agent/trades"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.ok:
            return resp.json()
        else:
            return {
                "error": "Failed to get trades",
                "status": resp.status_code,
                "details": resp.text
            }
    except Exception as e:
        return {
            "error": "Exception occurred while fetching portfolio",
            "details": str(e)
        }

if __name__ == "__main__":
    portfolio = get_portfolio()
    print(json.dumps(portfolio))  # ✅ Valid JSON output
