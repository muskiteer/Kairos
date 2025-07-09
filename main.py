import os
import sqlite3
import requests
from dotenv import load_dotenv
import argparse

# Load API Key from .env
load_dotenv()

API_KEY = os.getenv("RECALL_API_KEY")

RECALL_MAIN_API_BASE = "https://api.recall.network"
RECALL_SANDBOX_API_BASE = "https://api.sandbox.competitions.recall.network"

TRADE_ENDPOINT = f"{RECALL_SANDBOX_API_BASE}/trade/execute"
PRICE_ENDPOINT = f"{RECALL_SANDBOX_API_BASE}/api/price"



# DB file
DB_FILE = "trading_simulator.db"

def get_balance(asset):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM wallet_balances WHERE asset = ?", (asset,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_balances(from_token, to_token, amount_spent, amount_received):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Deduct from_token
    cursor.execute("UPDATE wallet_balances SET balance = balance - ? WHERE asset = ?", (amount_spent, from_token))

    # Add to_token
    cursor.execute("INSERT OR IGNORE INTO wallet_balances (asset, balance) VALUES (?, ?)", (to_token, 0.0))
    cursor.execute("UPDATE wallet_balances SET balance = balance + ? WHERE asset = ?", (amount_received, to_token))

    conn.commit()
    conn.close()

def log_trade(trade_type, asset, quantity, price_per_unit, total_value, profit_loss=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trade_log (trade_type, asset, quantity, price_per_unit, total_value, profit_loss)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (trade_type, asset, quantity, price_per_unit, total_value, profit_loss))
    conn.commit()
    conn.close()

def get_token_price(token_address, chain="evm", specific_chain="eth"):
    """Get price from Recall's price endpoint using correct format"""
    params = {
        "token": token_address,
        "chain": chain,
        "specificChain": specific_chain
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"🔍 Price API Request:")
    print(f"   URL: {PRICE_ENDPOINT}")
    print(f"   Params: {params}")
    
    try:
        resp = requests.get(PRICE_ENDPOINT, params=params, headers=headers, timeout=30)
        print(f"🔍 Response Status: {resp.status_code}")
        
        if resp.ok:
            price_data = resp.json()
            print(f"🔍 Price Response: {price_data}")
            
            if "price" in price_data:
                return float(price_data["price"])
            else:
                print(f"⚠️  No 'price' field in response: {price_data}")
                return None
        else:
            print(f"❌ Failed to get price: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return None

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
    parser = argparse.ArgumentParser(description="Execute a Recall trade")
    parser.add_argument("--from", dest="from_token", required=True, help="Token to trade from (e.g., USDC, WETH)")
    parser.add_argument("--to", dest="to_token", required=True, help="Token to trade to (e.g., WETH, USDC)")
    parser.add_argument("--amount", required=True, type=float, help="Amount of from_token to trade")
    args = parser.parse_args()

    from_token = args.from_token.upper()
    to_token = args.to_token.upper()
    token_amount = args.amount

    print(f"🔄 Processing trade request:")
    print(f"   From: {from_token}")
    print(f"   To: {to_token}")
    print(f"   Amount: {token_amount}")

    # Token addresses for Ethereum mainnet
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

    # Check supported tokens
    if from_token not in token_addresses or to_token not in token_addresses:
        print("❌ Unsupported token(s). Supported tokens:")
        for k in token_addresses.keys():
            print(f"  - {k}")
        return

    from_address = token_addresses[from_token]
    to_address = token_addresses[to_token]

    print(f"🏷️  Token addresses:")
    print(f"   {from_token}: {from_address}")
    print(f"   {to_token}: {to_address}")

    # Get prices
    print(f"⏳ Getting prices for {from_token} and {to_token}...")
    from_price = get_token_price(from_address)
    to_price = get_token_price(to_address)

    if from_price is None or to_price is None:
        print("❌ Could not fetch prices. Trying swap quote...")
        trade_response = trade_exec(from_address, to_address, token_amount)
        if not trade_response:
            print("❌ Could not get pricing information. Aborting trade.")
            return
        expected_output = float(trade_response.get("amountOut", 0))
        from_price = None
    else:
        usd_value = token_amount * from_price
        expected_output = usd_value / to_price if to_price > 0 else 0
        print(f"📊 Prices:")
        print(f"   {from_token}: ${from_price:.2f}")
        print(f"   {to_token}: ${to_price:.2f}")
        print(f"💰 Estimated Output:")
        print(f"   {token_amount} {from_token} ≈ {expected_output:.6f} {to_token}")

        # Also try to execute actual trade
        trade_response = trade_exec(from_address, to_address, token_amount)
        if not trade_response:
            print("❌ Trade failed during execution.")
            return

    # Check wallet balance
    balance = get_balance(from_token)
    if balance is None:
        print(f"❌ No balance found for {from_token}.")
        print("💡 Run: python initialise.py to set up your wallet.")
        return
    if balance < token_amount:
        print(f"❌ Insufficient balance: You have {balance} {from_token}, need {token_amount:.6f}")
        return

    print(f"✅ Trade Response: {trade_response}")

    # Determine received quantity
    received_qty = 0
    for field in ["amountReceived", "toTokenAmount", "amountOut", "outputAmount"]:
        if field in trade_response:
            received_qty = float(trade_response[field])
            break
    if received_qty == 0:
        print("⚠️  Could not determine received amount, using estimate.")
        received_qty = expected_output

    # Calculate effective price
    actual_price = received_qty / token_amount if token_amount > 0 else 0
    usd_value = token_amount * from_price if from_price else token_amount

    # Update wallet and log
    update_balances(from_token, to_token, token_amount, received_qty)
    log_trade("buy", to_token, received_qty, actual_price, usd_value)

    print(f"✅ Trade successful!")
    print(f"   Spent: {token_amount:.6f} {from_token}")
    print(f"   Received: {received_qty:.6f} {to_token}")
    print(f"   Effective rate: {actual_price:.6f} {to_token} per {from_token}")

   

if __name__ == "__main__":
    main()