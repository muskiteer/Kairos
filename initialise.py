import sqlite3

def init_db(db_file='trading_simulator.db'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create wallet_balances table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallet_balances (
            asset TEXT PRIMARY KEY,
            balance REAL NOT NULL
        )
    ''')

    # Create trade_log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            trade_type TEXT,  -- 'buy' or 'sell'
            asset TEXT,       -- e.g., BTC, ETH
            quantity REAL,
            price_per_unit REAL,
            total_value REAL,
            profit_loss REAL
        )
    ''')

    # Insert initial wallet balances with mock tokens for both networks
    initial_balances = [
        # Ethereum Mock Tokens
        ('USDC', 1000.0),    # Starting with 10,000 USDC
        ('WETH', 1.0),        # Starting with 5 WETH
        ('WBTC', 0.0),        # Starting with 0.5 WBTC
        ('DAI', 0.0),      # Starting with 2,000 DAI
        ('USDT', 0.0),     # Starting with 3,000 USDT
        
        # Solana Mock Tokens
        ('SOL', 0.0),       # Starting with 100 SOL
        ('USDC-SOL', 0.0), # Starting with 5,000 USDC on Solana
        ('WSOL', 0.0),       # Starting with 50 Wrapped SOL
        ('RAY', 0.0),      # Starting with 1,000 RAY
        ('SRM', 0.0),       # Starting with 500 SRM
    ]

    for asset, balance in initial_balances:
        cursor.execute('''
            INSERT OR IGNORE INTO wallet_balances (asset, balance) VALUES (?, ?)
        ''', (asset, balance))

    conn.commit()
    conn.close()
    print(f"Initialized database: {db_file}")
    print("💰 Initial wallet loaded with mock tokens:")
    print("   Ethereum: USDC, WETH, WBTC, DAI, USDT")
    print("   Solana:   SOL, USDC-SOL, WSOL, RAY, SRM")

if __name__ == '__main__':
    init_db()
