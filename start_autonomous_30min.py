#!/usr/bin/env python3
"""
Kairos Autonomous Trading Agent - 30 Minute Session Starter
Quick script to start autonomous trading for 30 minutes
"""

import requests
import json
import time
import sys

def start_autonomous_trading():
    """Start autonomous trading for 30 minutes"""
    
    # API endpoint
    api_url = "http://localhost:8000/api/chat"
    
    # Request payload
    payload = {
        "message": "Start autonomous trading for 30 minutes",
        "user_id": f"autonomous_user_{int(time.time())}"
    }
    
    try:
        print("🚀 Starting Kairos Autonomous Trading Agent for 30 minutes...")
        print("📡 Sending request to API server...")
        
        # Make the request
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract session information
            session_id = result.get('data', {}).get('session_id')
            autonomous_params = result.get('data', {}).get('autonomous_params', {})
            
            print("✅ Autonomous trading session started successfully!")
            print(f"🆔 Session ID: {session_id}")
            print(f"⏰ Duration: {autonomous_params.get('duration_text', '30 minutes')}")
            print(f"🎯 End Time: {autonomous_params.get('end_time', 'Unknown')}")
            print(f"📊 Status: {result.get('data', {}).get('status', 'Unknown')}")
            
            print("\n🤖 The autonomous agent is now:")
            print("• Monitoring your portfolio continuously")
            print("• Analyzing market news and sentiment")
            print("• Making strategic trading decisions every 5 minutes")
            print("• Learning from each trade to improve performance")
            
            print(f"\n💬 You can check status with:")
            print(f"curl -X GET \"http://localhost:8000/api/autonomous/status/{session_id}\"")
            
            return session_id
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Kairos API server")
        print("💡 Make sure the API server is running:")
        print("   cd /home/muskiteer/Desktop/new-kairos/kairos/backend")
        print("   /home/muskiteer/Desktop/new-kairos/kairos/.venv/bin/python api_server.py")
        return None
        
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - the session may still have started")
        print("💡 Check the API server logs for confirmation")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def check_status(session_id):
    """Check the status of an autonomous trading session"""
    if not session_id:
        print("⚠️ No session ID provided")
        return
    
    try:
        status_url = f"http://localhost:8000/api/autonomous/status/{session_id}"
        response = requests.get(status_url, timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            if status.get("session_found"):
                session_data = status.get("session_data", {})
                performance = status.get("performance", {})
                
                print(f"\n📊 Session Status:")
                print(f"Status: {session_data.get('status', 'Unknown')}")
                print(f"Total Trades: {performance.get('total_trades', 0)}")
                print(f"Successful Trades: {performance.get('successful_trades', 0)}")
                print(f"Current Portfolio Value: ${performance.get('current_portfolio_value', 0):,.2f}")
                print(f"Total P&L: ${performance.get('total_profit_loss', 0):,.2f}")
            else:
                print("❌ Session not found or has ended")
        else:
            print(f"❌ Error checking status: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    print("🤖 Kairos Autonomous Trading Agent - 30 Minute Session")
    print("=" * 60)
    
    # Start the autonomous trading session
    session_id = start_autonomous_trading()
    
    if session_id:
        print(f"\n🎉 Session {session_id[:8]}... is now running!")
        
        # Ask if user wants to check status
        try:
            user_input = input("\n❓ Check status now? (y/n): ").lower().strip()
            if user_input in ['y', 'yes']:
                check_status(session_id)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        
        print(f"\n📝 Session will run for 30 minutes automatically.")
        print(f"🔗 You can check status anytime at: http://localhost:8000/api/autonomous/status/{session_id}")
    
    else:
        print("\n❌ Failed to start autonomous trading session")
        sys.exit(1)
