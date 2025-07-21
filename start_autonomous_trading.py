#!/usr/bin/env python3
#test:ignore

"""
Enhanced Kairos Autonomous Trading Agent - Variable Duration Session Starter
Now with enhanced AI, multi-chain support, and comprehensive database integration
"""

import requests
import json
import time
import sys

def get_user_duration():
    """Get trading duration from user input"""
    duration_options = {
        '1': {'text': '10 minutes', 'minutes': 10},
        '2': {'text': '30 minutes', 'minutes': 30},
        '3': {'text': '1 hour', 'minutes': 60},
        '4': {'text': '2 hours', 'minutes': 120},
        '5': {'text': '5 hours', 'minutes': 300},
        '6': {'text': '12 hours', 'minutes': 720},
        '7': {'text': '24 hours', 'minutes': 1440}
    }
    
    print("⏰ Select trading duration:")
    print("=" * 40)
    for key, value in duration_options.items():
        print(f"{key}. {value['text']} ({value['minutes']} minutes)")
    print("=" * 40)
    
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice in duration_options:
                selected = duration_options[choice]
                print(f"✅ Selected: {selected['text']} ({selected['minutes']} minutes)")
                return selected['text'], selected['minutes']
            else:
                print("❌ Invalid choice. Please enter a number between 1-7.")
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error reading input: {e}")

def start_autonomous_trading(duration_text=None, duration_minutes=None):
    """Start enhanced autonomous trading for specified duration"""
    
    # If duration not provided, ask user
    if not duration_text or not duration_minutes:
        duration_text, duration_minutes = get_user_duration()
        print()  # Add spacing
    
    # API endpoint
    api_url = "http://localhost:8000/api/chat"
    
    # Generate a consistent user ID that we can use later
    user_id = f"autonomous_user_{int(time.time())}"
    
    # Enhanced request payload with dynamic duration
    payload = {
        "message": f"Start enhanced autonomous trading for {duration_text} with AI integration",
        "user_id": user_id,
        "duration_minutes": duration_minutes  # Include duration in minutes for the API
    }
    
    try:
        print(f"🚀 Starting Enhanced Kairos Autonomous Trading Agent for {duration_text}...")
        print("🧠 Features: Gemini AI, Multi-chain support, SOL/WBTC/ETH trading")
        print("📡 Sending request to Enhanced API server...")
        
        # Make the request
        response = requests.post(api_url, json=payload, timeout=180)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract session information
            session_id = result.get('data', {}).get('session_id')
            autonomous_params = result.get('data', {}).get('autonomous_params', {})
            
            print("✅ Enhanced Autonomous trading session started successfully!")
            print(f"🆔 Session ID: {session_id}")
            print(f"👤 User ID: {user_id}")
            print(f"⏰ Duration: {autonomous_params.get('duration_text', duration_text)}")
            print(f"🕒 Duration Minutes: {duration_minutes}")
            print(f"🎯 End Time: {autonomous_params.get('end_time', 'Unknown')}")
            print(f"📊 Status: {result.get('data', {}).get('status', 'Unknown')}")
            print(f"🧠 AI Engine: {result.get('data', {}).get('ai_engine', 'Enhanced')}")
            
            # Show enhanced capabilities
            supported_tokens = result.get('data', {}).get('supported_tokens', [])
            supported_chains = result.get('data', {}).get('supported_chains', [])
            
            print("\n🤖 The Enhanced Autonomous Agent is now:")
            print("• 🧠 Using Gemini AI for intelligent trading decisions")
            print("• 🌐 Monitoring multi-chain portfolio (Ethereum + Solana)")
            print("• 📊 Analyzing market news and sentiment with AI")
            print("• 💱 Trading SOL, WBTC, ETH with enhanced price APIs")
            print("• 🎯 Making strategic decisions every 3-5 minutes")
            print("• 📈 Learning from each trade with comprehensive metrics")
            print("• 💾 Storing all decisions in enhanced database")
            print("• 📄 Generating PDF reports automatically")
            
            if supported_tokens:
                print(f"\n🪙 Supported tokens ({len(supported_tokens)}): {', '.join(supported_tokens[:10])}{'...' if len(supported_tokens) > 10 else ''}")
            if supported_chains:
                print(f"🔗 Supported chains: {', '.join(supported_chains)}")
            
            print(f"\n💬 Enhanced monitoring commands:")
            print(f"curl -X GET \"http://localhost:8000/api/autonomous/status/{session_id}?user_id={user_id}\"")
            print(f"curl -X GET \"http://localhost:8000/api/ai/insights/{user_id}\"")
            
            return session_id, user_id, duration_text, duration_minutes  # Return all values
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None, None, None, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Kairos API server")
        print("💡 Make sure the API server is running:")
        print("   cd /home/kali/Dev/Kairos/backend")
        print("   /home/kali/Dev/Kairos/.venv/bin/python api_server.py")
        return None, None, None, None
        
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - the session may still have started")
        print("💡 Check the API server logs for confirmation")
        return None, None, None, None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None, None, None

def check_status(session_id, user_id):
    """Check the status of an autonomous trading session"""
    if not session_id:
        print("⚠️ No session ID provided")
        return
    
    try:
        # First, test basic connectivity
        print("🔍 Testing API server connectivity...")
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ API server is responsive")
        else:
            print(f"⚠️ API server health check returned: {health_response.status_code}")
        
        status_url = f"http://localhost:8000/api/autonomous/status/{session_id}?user_id={user_id}"
        print(f"🔍 Checking status at: {status_url}")
        print(f"⏱️  Making request with 30-second timeout...")
        response = requests.get(status_url, timeout=30)
        
        if response.status_code == 200:
            status = response.json()
            print(f"📥 Raw response: {json.dumps(status, indent=2)}")
            
            if status.get("session_found"):
                session_data = status.get("session_data", {})
                performance = status.get("performance", {})
                
                print(f"\n📊 Session Status:")
                print(f"Status: {session_data.get('status', 'Unknown')}")
                print(f"Total Trades: {performance.get('total_trades', 0)}")
                print(f"Successful Trades: {performance.get('successful_trades', 0)}")
                print(f"Current Portfolio Value: ${performance.get('current_portfolio_value', 0):,.2f}")
                print(f"Total P&L: ${performance.get('total_profit_loss', 0):,.2f}")
                
                # Show additional session info
                params = session_data.get('params', {})
                print(f"\n⚙️ Session Parameters:")
                print(f"Duration: {params.get('duration_text', 'Unknown')}")
                print(f"Testing Mode: {params.get('testing_mode', 'Unknown')}")
                print(f"Risk Level: {params.get('risk_level', 'Unknown')}")
                
                # Show PDF report info if available
                if status.get('pdf_generated'):
                    print(f"\n📄 PDF Report Generated:")
                    print(f"File: {status.get('pdf_report_filename', 'Unknown')}")
                    print(f"Path: {status.get('pdf_report_path', 'Unknown')}")
                    print(f"Download URL: http://localhost:8000{status.get('pdf_report_url', '')}")
                elif 'pdf_generated' in status:
                    print(f"\n📄 PDF Report: ❌ {status.get('pdf_error', 'Generation failed')}")
                
            else:
                print("❌ Session not found or has ended")
                print(f"Message: {status.get('message', 'No details')}")
                print(f"Total active sessions: {status.get('total_active_sessions', 0)}")
                print(f"Searched users: {status.get('searched_users', [])}")
                if "found_in_user" in status:
                    print(f"Found in different user: {status['found_in_user']}")
        else:
            print(f"❌ Error checking status: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Status request timed out after 30 seconds")
        print("💡 This suggests the API server may be stuck or overloaded")
        print("🔧 Try restarting the API server or check its logs")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure the API server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    print("🤖 Kairos Autonomous Trading Agent - Variable Duration Session")
    print("=" * 70)
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        if len(sys.argv) >= 4:
            session_id = sys.argv[2]
            user_id = sys.argv[3]
            print(f"🔍 Checking status for session {session_id[:8]}... with user {user_id}")
            check_status(session_id, user_id)
        else:
            print("❌ Usage: python start_autonomous_30min.py status <session_id> <user_id>")
        sys.exit(0)
    
    # Check for preset duration arguments
    preset_duration = None
    preset_minutes = None
    
    if len(sys.argv) > 1:
        duration_arg = sys.argv[1].lower()
        duration_presets = {
            '10m': ('10 minutes', 10),
            '30m': ('30 minutes', 30), 
            '1h': ('1 hour', 60),
            '2h': ('2 hours', 120),
            '5h': ('5 hours', 300),
            '12h': ('12 hours', 720),
            '24h': ('24 hours', 1440)
        }
        
        if duration_arg in duration_presets:
            preset_duration, preset_minutes = duration_presets[duration_arg]
            print(f"🚀 Quick start with preset duration: {preset_duration}")
        else:
            print(f"❌ Invalid duration preset: {duration_arg}")
            print("💡 Available presets: 10m, 30m, 1h, 2h, 5h, 12h, 24h")
            print("💡 Or run without arguments for interactive selection")
            sys.exit(1)
    
    # Start the autonomous trading session
    session_id, user_id, duration_text, duration_minutes = start_autonomous_trading(
        preset_duration, preset_minutes
    )
    
    if session_id and user_id:
        print(f"\n🎉 Session {session_id[:8]}... is now running for {duration_text}!")
        
        # Show estimated completion time
        from datetime import datetime, timedelta
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        print(f"⏰ Estimated completion: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ask if user wants to check status
        try:
            user_input = input("\n❓ Check status now? (y/n): ").lower().strip()
            if user_input in ['y', 'yes']:
                check_status(session_id, user_id)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        
        print(f"\n📝 Session will run for {duration_text} automatically.")
        print(f"🔗 You can check status anytime at: http://localhost:8000/api/autonomous/status/{session_id}?user_id={user_id}")
        print(f"📋 Or use: python start_autonomous_30min.py status {session_id} {user_id}")
        print(f"📄 PDF reports will be auto-generated and saved to /tmp/")
        
        # Show helpful commands
        print(f"\n💡 Helpful commands:")
        print(f"   Check status: python start_autonomous_30min.py status {session_id} {user_id}")
        print(f"   Quick 10min:  python start_autonomous_30min.py 10m")
        print(f"   Quick 1hr:    python start_autonomous_30min.py 1h")
        print(f"   Quick 24hr:   python start_autonomous_30min.py 24h")
    
    else:
        print("\n❌ Failed to start autonomous trading session")
        sys.exit(1)
