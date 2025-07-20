import argparse
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Using CoinGecko API (no API key needed for basic usage)
COINGECKO_ENDPOINT = "https://api.coingecko.com/api/v3/simple/price"

# CoinGecko token ID mapping
token_coingecko_ids = {
    "USDC": "usd-coin",
    "WETH": "weth", 
    "WBTC": "wrapped-bitcoin",
    "DAI": "dai",
    "USDT": "tether",
    "UNI": "uniswap",
    "LINK": "chainlink",
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "SOL": "solana"
}

def get_token_price_json(symbol):
    """Get token price from CoinGecko API"""
    symbol = symbol.upper()
    if symbol not in token_coingecko_ids:
        return {"error": "Unsupported token symbol", "supported": list(token_coingecko_ids.keys())}
    
    coingecko_id = token_coingecko_ids[symbol]
    
    # CoinGecko API parameters
    params = {
        "ids": coingecko_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "precision": "full"
    }
    
    try:
        resp = requests.get(COINGECKO_ENDPOINT, params=params, timeout=10)
        
        # Check if response status is OK
        if resp.status_code != 200:
            return {
                "error": f"CoinGecko API request failed with status {resp.status_code}",
                "status_code": resp.status_code,
                "response_text": resp.text[:500]
            }
        
        # Try to parse JSON response
        try:
            data = resp.json()
            
            if coingecko_id in data:
                price_data = data[coingecko_id]
                return {
                    "symbol": symbol,
                    "price": price_data.get("usd", 0),
                    "change_24h": price_data.get("usd_24h_change", 0),
                    "source": "coingecko",
                    "timestamp": resp.headers.get('Date')
                }
            else:
                return {"error": f"No price data found for {symbol}"}
                
        except json.JSONDecodeError as json_err:
            return {
                "error": f"Invalid JSON response: {str(json_err)}",
                "status_code": resp.status_code,
                "response_text": resp.text[:500]
            }
            
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request failed: {str(req_err)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Get the price of a token using CoinGecko API")
    parser.add_argument("--symbol", required=True, help="Token symbol (e.g., USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH, BTC, SOL)")
    args = parser.parse_args()
    result = get_token_price_json(args.symbol)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()