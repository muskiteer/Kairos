#!/usr/bin/env python3
"""
Add test profile with API keys
Run this to populate the database with a default user profile containing API keys
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.profile import profile_router
from dotenv import load_dotenv

load_dotenv()

async def add_test_profile():
    """Add a test profile with API keys"""
    
    test_profile = {
        "username": "Demo User",
        "email": "demo@kairos.ai",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
        "wallet_address": "",
        "recall_api_key": os.getenv("RECALL_API_KEY", ""),
        "coinpanic_api_key": os.getenv("COINPANIC_API_KEY", ""),
        "consent_terms": True,
        "consent_risks": True,
        "consent_data": True
    }
    
    print("🔧 Adding test profile with API keys...")
    print(f"Recall API Key: {test_profile['recall_api_key'][:20]}..." if test_profile['recall_api_key'] else "No Recall API Key")
    print(f"CoinPanic API Key: {test_profile['coinpanic_api_key'][:20]}..." if test_profile['coinpanic_api_key'] else "No CoinPanic API Key")
    
    try:
        # Import and use the profile save function
        from api.profile import save_profile, UserProfileRequest
        
        request = UserProfileRequest(profile=test_profile)
        result = await save_profile(request, "default")
        
        if result.success:
            print("✅ Test profile added successfully!")
            print(f"Profile ID: {result.profile['id']}")
        else:
            print(f"❌ Failed to add profile: {result.message}")
            
    except Exception as e:
        print(f"❌ Error adding test profile: {e}")

if __name__ == "__main__":
    print("🚀 Kairos Profile Setup")
    print("=" * 40)
    
    asyncio.run(add_test_profile())
    
    print("\n🎉 Setup complete!")
    print("Next steps:")
    print("1. Make sure your database migration is complete")
    print("2. Start the backend: python api_server.py")
    print("3. Test the profile system!")
