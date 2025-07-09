import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Constants
RECALL_SANDBOX_API_BASE = os.getenv("RECALL_SANDBOX_API_BASE", "https://api.sandbox.competitions.recall.network")
API_KEY = os.getenv("RECALL_API_KEY")

def get_portfolio():
    """Get portfolio information from Recall API"""
    url = f"{RECALL_SANDBOX_API_BASE}/api/agent/portfolio"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"🔍 Portfolio API Request:")
    print(f"   URL: {url}")
    print(f"   Headers: {headers}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f"🔍 Response Status: {resp.status_code}")
        
        if resp.ok:
            portfolio_data = resp.json()
            print(f"🔍 Portfolio Response: {portfolio_data}")
            return portfolio_data
        else:
            print(f"❌ Failed to get portfolio: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Error fetching portfolio: {e}")
        return None

# 👇 Run when the script is executed directly
if __name__ == "__main__":
    get_portfolio()
