import json
import argparse
from api.token_price import get_token_price_json
from api.token_balance import get_token_balance
from api.trades_history import get_portfolio as get_trades_history
from api.execute import trade_exec, token_addresses
from api.portfolio import get_portfolio

# Global user_id for CLI session
current_user_id = "default"

def set_user_id(user_id: str):
    """Set the current user ID for the CLI session"""
    global current_user_id
    current_user_id = user_id
    print(f"✅ User ID set to: {user_id}")

def print_menu():
    """Display the main menu options"""
    print("\n" + "="*50)
    print("         RECALL TRADING TERMINAL")
    print(f"         User: {current_user_id}")
    print("="*50)
    print("1. Check Token Price")
    print("2. Check Token Balance")
    print("3. View Trade History")
    print("4. Execute Trade")
    print("5. View Portfolio")
    print("6. Change User ID")
    print("7. Exit")
    print("="*50)

def check_token_price():
    """Handle token price checking"""
    print("\n📊 TOKEN PRICE CHECKER")
    print("-" * 30)
    print("Supported tokens:", ", ".join(token_addresses.keys()))
    
    while True:
        symbol = input("\nEnter token symbol (or 'back' to return): ").strip()
        if symbol.lower() == 'back':
            return
        
        if symbol.upper() in token_addresses:
            print(f"\n🔍 Fetching price for {symbol.upper()}...")
            result = get_token_price_json(symbol)
            print(json.dumps(result, indent=2))
            break
        else:
            print(f"❌ Unsupported token: {symbol}")

def check_token_balance():
    """Handle token balance checking"""
    print("\n💰 TOKEN BALANCE CHECKER")
    print("-" * 30)
    print("Supported tokens:", ", ".join(token_addresses.keys()))
    
    while True:
        symbol = input("\nEnter token symbol (or 'back' to return): ").strip()
        if symbol.lower() == 'back':
            return
        
        if symbol.upper() in token_addresses:
            print(f"\n🔍 Fetching balance for {symbol.upper()}...")
            result = get_token_balance(symbol)
            print(json.dumps(result, indent=2))
            break
        else:
            print(f"❌ Unsupported token: {symbol}")

def view_trade_history():
    """Handle trade history viewing"""
    print("\n📈 TRADE HISTORY")
    print("-" * 30)
    print("🔍 Fetching trade history...")
    result = get_trades_history(user_id=current_user_id)
    print(json.dumps(result, indent=2))

def execute_trade():
    """Handle trade execution"""
    print("\n🔄 TRADE EXECUTION")
    print("-" * 30)
    print("Supported tokens:", ", ".join(token_addresses.keys()))
    
    # Get from token
    while True:
        from_token = input("\nEnter token to trade FROM (or 'back' to return): ").strip()
        if from_token.lower() == 'back':
            return
        
        if from_token.upper() in token_addresses:
            break
        else:
            print(f"❌ Unsupported token: {from_token}")
    
    # Get to token
    while True:
        to_token = input("Enter token to trade TO: ").strip()
        if to_token.upper() in token_addresses:
            break
        else:
            print(f"❌ Unsupported token: {to_token}")
    
    # Get amount
    while True:
        try:
            amount = float(input("Enter amount to trade: ").strip())
            if amount > 0:
                break
            else:
                print("❌ Amount must be greater than 0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Check balance first
    print(f"\n🔍 Checking balance for {from_token.upper()}...")
    balance_info = get_token_balance(from_token)
    balance = balance_info.get("amount", 0)
    
    if balance < amount:
        print(f"❌ Insufficient balance!")
        print(f"   Available: {balance} {from_token.upper()}")
        print(f"   Required: {amount} {from_token.upper()}")
        return
    
    # Execute trade
    print(f"\n🔄 Executing trade: {amount} {from_token.upper()} → {to_token.upper()}")
    from_address = token_addresses[from_token.upper()]
    to_address = token_addresses[to_token.upper()]
    
    result = trade_exec(from_address, to_address, amount)
    if result:
        print("\n✅ Trade executed successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("\n❌ Trade failed!")

def view_portfolio():
    """Handle portfolio viewing"""
    print("\n👛 PORTFOLIO OVERVIEW")
    print("-" * 30)
    print("🔍 Fetching portfolio...")
    result = get_portfolio(user_id=current_user_id)
    print(json.dumps(result, indent=2))

def change_user_id():
    """Handle user ID change"""
    print("\n👤 CHANGE USER ID")
    print("-" * 30)
    print(f"Current user ID: {current_user_id}")
    new_user_id = input("Enter new user ID (or 'back' to return): ").strip()
    if new_user_id.lower() != 'back' and new_user_id:
        set_user_id(new_user_id)

def main():
    """Main interactive loop"""
    print("🚀 Welcome to Recall Trading Terminal!")
    
    # Check for command line arguments
    parser = argparse.ArgumentParser(description='Recall Trading Terminal')
    parser.add_argument('--user-id', default='default', help='User ID for API calls')
    args = parser.parse_args()
    
    # Set initial user ID
    set_user_id(args.user_id)
    
    while True:
        try:
            print_menu()
            choice = input("\nSelect an option (1-7): ").strip()
            
            if choice == '1':
                check_token_price()
            elif choice == '2':
                check_token_balance()
            elif choice == '3':
                view_trade_history()
            elif choice == '4':
                execute_trade()
            elif choice == '5':
                view_portfolio()
            elif choice == '6':
                change_user_id()
            elif choice == '7':
                print("\n👋 Thank you for using Recall Trading Terminal!")
                break
            else:
                print("❌ Invalid option. Please select 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()