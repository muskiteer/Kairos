import argparse
import json
from api.portfolio import get_portfolio

def get_token_balance(token):
    """Return {'symbol': token, 'amount': ...} for the given token symbol."""
    portfolio = get_portfolio()
    token = token.upper()
    result = {"symbol": token, "amount": 0}

    if isinstance(portfolio, dict):
        for key in ["balances", "data", "result"]:
            if key in portfolio and isinstance(portfolio[key], list):
                for entry in portfolio[key]:
                    if isinstance(entry, dict) and entry.get("symbol", "").upper() == token:
                        result["amount"] = entry.get("amount", entry.get("balance", 0))
                        break
            if result["amount"] > 0:
                break

    return result

def main():
    parser = argparse.ArgumentParser(description="Get the balance of a specific token")
    parser.add_argument("--token", required=True, help="Token symbol (e.g., WETH, USDC, etc.)")
    args = parser.parse_args()
    result = get_token_balance(args.token)
    print(json.dumps(result))

if __name__ == "__main__":
    main()