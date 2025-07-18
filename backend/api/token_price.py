# this ois coin gecko api

# import argparse
# import json
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()
# # Using CoinGecko API (no API key needed for basic usage)

# COINGECKO_ENDPOINT = "https://api.coingecko.com/api/v3/simple/price"

# # CoinGecko token ID mapping
# token_coingecko_ids = {
#     "USDC": "usd-coin",
#     "WETH": "weth", 
#     "WBTC": "wrapped-bitcoin",
#     "DAI": "dai",
#     "USDT": "tether",
#     "UNI": "uniswap",
#     "LINK": "chainlink",
#     "ETH": "ethereum",
#     "BTC": "bitcoin",
#     "SOL": "solana"
# }

# def get_token_price_json(symbol):
#     """Get token price from CoinGecko API"""
#     symbol = symbol.upper()
#     if symbol not in token_coingecko_ids:
#         return {"error": "Unsupported token symbol", "supported": list(token_coingecko_ids.keys())}
    
#     coingecko_id = token_coingecko_ids[symbol]
    
#     # CoinGecko API parameters
#     params = {
#         "ids": coingecko_id,
#         "vs_currencies": "usd",
#         "include_24hr_change": "true",
#         "precision": "full"
#     }
    
#     try:
#         resp = requests.get(COINGECKO_ENDPOINT, params=params, timeout=10)
        
#         # Check if response status is OK
#         if resp.status_code != 200:
#             return {
#                 "error": f"CoinGecko API request failed with status {resp.status_code}",
#                 "status_code": resp.status_code,
#                 "response_text": resp.text[:500]
#             }
        
#         # Try to parse JSON response
#         try:
#             data = resp.json()
            
#             if coingecko_id in data:
#                 price_data = data[coingecko_id]
#                 return {
#                     "symbol": symbol,
#                     "price": price_data.get("usd", 0),
#                     "change_24h": price_data.get("usd_24h_change", 0),
#                     "source": "coingecko",
#                     "timestamp": resp.headers.get('Date')
#                 }
#             else:
#                 return {"error": f"No price data found for {symbol}"}
                
#         except json.JSONDecodeError as json_err:
#             return {
#                 "error": f"Invalid JSON response: {str(json_err)}",
#                 "status_code": resp.status_code,
#                 "response_text": resp.text[:500]
#             }
            
#     except requests.exceptions.RequestException as req_err:
#         return {"error": f"Request failed: {str(req_err)}"}
#     except Exception as e:
#         return {"error": f"Unexpected error: {str(e)}"}

# def main():
#     parser = argparse.ArgumentParser(description="Get the price of a token using CoinGecko API")
#     parser.add_argument("--symbol", required=True, help="Token symbol (e.g., USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH, BTC, SOL)")
#     args = parser.parse_args()
#     result = get_token_price_json(args.symbol)
#     print(json.dumps(result, indent=2))

# if __name__ == "__main__":
#     main()



# below is with recall 




import argparse
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RECALL_API_KEY")
PRICE_ENDPOINT = "https://api.sandbox.competitions.recall.network/api/price"

token_addresses = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "UNI":  "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "ETH":  "0x0000000000000000000000000000000000000000",
    "SOL":  "So11111111111111111111111111111111111111112",
}

def get_token_price_json(symbol):
    symbol = symbol.upper()
    if symbol not in token_addresses:
        return {"error": "Unsupported token symbol", "supported": list(token_addresses.keys())}
    address = token_addresses[symbol]
    # Use Solana-specific params for SOL, EVM for others
    if symbol == "SOL":
        params = {
            "token": address,
            "chain": "solana",
            "specificChain": "sol"
        }
    else:
        params = {
            "token": address,
            "chain": "evm",
            "specificChain": "eth"
        }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        resp = requests.get(PRICE_ENDPOINT, params=params, headers=headers, timeout=30)
        
        # Check if response status is OK
        if resp.status_code != 200:
            return {
                "error": f"API request failed with status {resp.status_code}",
                "status_code": resp.status_code,
                "response_text": resp.text[:500]  # First 500 chars for debugging
            }
        
        # Try to parse JSON response
        try:
            return resp.json()
        except json.JSONDecodeError as json_err:
            return {
                "error": f"Invalid JSON response: {str(json_err)}",
                "status_code": resp.status_code,
                "response_text": resp.text[:500],  # First 500 chars for debugging
                "content_type": resp.headers.get('Content-Type', 'unknown')
            }
            
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request failed: {str(req_err)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Get the price of a token using Recall API")
    parser.add_argument("--symbol", required=True, help="Token symbol (e.g., USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH)")
    args = parser.parse_args()
    result = get_token_price_json(args.symbol)
    print(json.dumps(result))

if __name__ == "__main__":
    main()