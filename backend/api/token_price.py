# Place this in your `api/token_price.py` file, replacing the old version.

import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RECALL_API_KEY")
PRICE_ENDPOINT = "https://api.sandbox.competitions.recall.network/api/price"

# Your token_addresses and CHAIN_MAP dictionaries remain the same and are correct.
token_addresses = {
    "eth": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "ETH":  "0x0000000000000000000000000000000000000000",
        "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "UNI":  "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    },
    "sol": {
        "SOL": "So11111111111111111111111111111111111111112",
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    },
    "polygon": {
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0C4c6a9Ac2BB0",
    },
    "base": {
        "USDBC": "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    },
    "arbitrum": {
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
    },
    "optimism": {
        "USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        "OP": "0x4200000000000000000000000000000000000042",
    }
}

CHAIN_MAP = {
    "ethereum": "eth", "eth": "eth",
    "solana": "sol", "sol": "sol", "svm": "sol",
    "polygon": "matic", "matic": "matic",
    "base": "base",
    "arbitrum": "arbitrum",
    "optimism": "optimism"
}

def get_token_price_json(symbol: str, chain: str):
    """
    Get token price from Recall API, with workarounds for specific assets.
    """
    symbol_upper = symbol.upper()
    chain_lower = chain.lower()

    # Your existing workarounds for USDC
    if chain_lower == "polygon" and symbol_upper == "USDC":
        # print("ℹ️  Using Base USDbC as a proxy for Polygon USDC price.")
        return get_token_price_json("USDbC", "base")
    
    if chain_lower == "svm" and symbol_upper == "USDC":
        # print("ℹ️  Using Base USDbC as a proxy for Solana USDC price.")
        return get_token_price_json("USDbC", "base")

    if chain_lower not in CHAIN_MAP:
        return {"error": f"Unsupported chain provided: {chain}"}

    api_chain_name = CHAIN_MAP[chain_lower]

    # --- NEW WORKAROUND FOR NATIVE ETH ---
    # If the token is native ETH, use the WETH address for the price lookup,
    # as they have the same value and WETH is a standard ERC-20 token.
    if symbol_upper == 'ETH' and api_chain_name == 'eth':
        print(f"ℹ️  Using WETH to fetch price for native ETH...")
        symbol_upper = 'WETH'
    # --- END WORKAROUND ---
    
    address = token_addresses.get(api_chain_name, {}).get(symbol_upper)

    if not address:
        return {"error": f"Unsupported token '{symbol}' on chain '{chain}'"}

    params = {
        "token": address,
        "chain": "solana" if api_chain_name == "sol" else "evm",
        "specificChain": api_chain_name
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        resp = requests.get(PRICE_ENDPOINT, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as http_err:
        return {
            "error": f"API request failed with status {http_err.response.status_code}",
            "response_text": http_err.response.text[:500]
        }
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request failed: {str(req_err)}"}
    except json.JSONDecodeError:
         return {"error": "Invalid JSON response from API"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}