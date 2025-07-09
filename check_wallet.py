#!/usr/bin/env python3
import sqlite3
import sys

def check_wallet(db_file='trading_simulator.db'):
    """Display current wallet balances and recent trades"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print("💰 Current Wallet Balances:")
        print("=" * 50)
        
        # Get all balances
        cursor.execute("SELECT asset, balance FROM wallet_balances ORDER BY asset")
        balances = cursor.fetchall()
        
        if not balances:
            print("   No assets found in wallet")
        else:
            total_usd_estimate = 0
            for asset, balance in balances:
                print(f"   {asset:<12}: {balance:>12.6f}")
                # Simple USD estimation (just for display, not accurate)
                if asset in ['USDC', 'USDT', 'DAI', 'USDC-SOL']:
                    total_usd_estimate += balance
                elif asset == 'WETH':
                    total_usd_estimate += balance * 2000  # Rough estimate
                elif asset == 'SOL':
                    total_usd_estimate += balance * 20    # Rough estimate
                elif asset == 'WBTC':
                    total_usd_estimate += balance * 30000 # Rough estimate
                elif asset == 'ETH':
                    total_usd_estimate += balance * 2000  # Rough estimate
            
            print("-" * 50)
            print(f"   Estimated Total: ~${total_usd_estimate:,.2f} USD")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        print("💡 Try running: python initialise.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_specific_asset(asset, db_file='trading_simulator.db'):
    """Check balance for a specific asset"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT balance FROM wallet_balances WHERE asset = ?", (asset.upper(),))
        result = cursor.fetchone()
        
        if result:
            print(f"💰 {asset.upper()} Balance: {result[0]:.6f}")
            
            # Get trade history for this asset
            cursor.execute("""
                SELECT timestamp, trade_type, quantity, price_per_unit, total_value 
                FROM trade_log 
                WHERE asset = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (asset.upper(),))
            trades = cursor.fetchall()
            
            if trades:
                print(f"\n📊 Recent {asset.upper()} Trades:")
                print(f"{'Time':<20} {'Type':<5} {'Quantity':<15} {'Price':<15} {'Value':<10}")
                print("-" * 70)
                for timestamp, trade_type, quantity, price, value in trades:
                    print(f"{timestamp:<20} {trade_type:<5} {quantity:<15.6f} {price:<15.6f} ${value:<10.2f}")
        else:
            print(f"❌ Asset {asset.upper()} not found in wallet")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_help():
    """Show usage help"""
    print("💡 Wallet Checker Usage:")
    print("  python check_wallet.py              # Show full wallet")
    print("  python check_wallet.py USDC         # Show specific asset")
    print("  python check_wallet.py --help       # Show this help")
    print("\n📋 Available assets:")
    print("  Ethereum: USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH")
    print("  Solana:   SOL, USDC-SOL, WSOL, RAY, SRM, ORCA, MNGO")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h', 'help']:
            show_help()
        else:
            # Check specific asset
            asset = sys.argv[1]
            check_specific_asset(asset)
    else:
        # Show full wallet
        check_wallet()
