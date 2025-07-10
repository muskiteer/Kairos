import argparse
import json

from api.token_balance import get_token_balance
from api.token_price import get_token_price_json as get_token_price
import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("RECALL_API_KEY")
RECALL_SANDBOX_API_BASE = "https://api.sandbox.competitions.recall.network"

# Supported tokens and their addresses
token_addresses = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "UNI":  "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "ETH":  "0x0000000000000000000000000000000000000000",
}

def trade_exec(from_token_address, to_token_address, amount):
    url = f"{RECALL_SANDBOX_API_BASE}/api/trade/execute"

    payload = {
        "fromToken": from_token_address,
        "toToken": to_token_address,
        "amount": str(amount),
        "reason": "CLI trade for analysis/testing",
        "slippageTolerance": "0.5",
        "fromChain": "evm",
        "fromSpecificChain": "eth",
        "toChain": "evm",
        "toSpecificChain": "eth"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.ok:
            return resp.json()
        else:
            print(f"❌ Trade failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"⚠️  Trade execution error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Execute a token trade via Recall API")
    parser.add_argument("--from", dest="from_token", required=True, help="Token to trade from (e.g., USDC)")
    parser.add_argument("--to", dest="to_token", required=True, help="Token to trade to (e.g., WETH)")
    parser.add_argument("--amount", required=True, type=float, help="Amount of from_token to trade")
    args = parser.parse_args()

    from_token = args.from_token.upper()
    to_token = args.to_token.upper()
    amount = args.amount

    # Check for supported tokens
    if from_token not in token_addresses or to_token not in token_addresses:
        print(json.dumps({
            "error": "Unsupported token(s)",
            "supported_tokens": list(token_addresses.keys())
        }))
        return

    # Get balance
    balance_info = get_token_balance(from_token)
    balance = balance_info.get("amount", 0)

    if balance < amount:
        print(json.dumps({
            "error": "Insufficient balance",
            "balance": balance,
            "required": amount
        }))
        return

    # Get token addresses
    from_address = token_addresses[from_token]
    to_address = token_addresses[to_token]

    # Execute trade
    result = trade_exec(from_address, to_address, amount)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()