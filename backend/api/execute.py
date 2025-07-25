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
RECALL_SANDBOX_API_BASE = "https://api.competitions.recall.network"

# Supported tokens and their addresses - EXPANDED LIST
token_addresses = {
    "USDbC": "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    # Ethereum Mainnet tokens
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "ETH":  "0x0000000000000000000000000000000000000000",
    "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "UNI":  "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
    
    # Solana tokens (SVM chain)
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC_SOL": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    
    # Additional popular tokens that may be supported
    "PEPE": "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
}

CHAIN_MAP = {
    "ethereum": "eth", "eth": "eth", "solana": "sol", "sol": "sol",
    "polygon": "matic", "base": "base", "arbitrum": "arbitrum", "optimism": "optimism"
}

def trade_exec(from_token_address: str, to_token_address: str, amount: float, chain: str):
    """Executes a token trade via Recall API with chain awareness."""
    url = f"{RECALL_SANDBOX_API_BASE}/api/trade/execute"
    
    chain_lower = chain.lower()
    if chain_lower not in CHAIN_MAP:
        print(f"❌ Trade failed: Unsupported chain '{chain}'")
        return {"error": f"Unsupported chain: {chain}"}

    api_chain_name = CHAIN_MAP[chain_lower]
    # The main chain type is 'solana' for SOL, and 'evm' for all others
    chain_type = "solana" if api_chain_name == "sol" else "evm"

    payload = {
        "fromToken": from_token_address,
        "toToken": to_token_address,
        "amount": str(amount),
        "reason": "Kairos AI autonomous trade",
        "slippageTolerance": "0.5",
        "fromChain": chain_type,
        "fromSpecificChain": api_chain_name,
        "toChain": chain_type,
        "toSpecificChain": api_chain_name
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=45)
        resp.raise_for_status() # Will raise an exception for 4xx/5xx errors
        return resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Trade failed: {e.response.status_code} - {e.response.text}")
        return e.response.json() # Return the actual error from the API
    except Exception as e:
        print(f"⚠️  Trade execution error: {e}")
        return {"error": str(e)}