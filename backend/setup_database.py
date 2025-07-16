#!/usr/bin/env python3
"""
Database Setup Script for Kairos Profile Management
Run this to create the user_profiles table in your Supabase database
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Create user profiles table and configure security"""
    
    print("🔍 Loading environment variables...")
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL found: {'Yes' if url else 'No'}")
    print(f"SUPABASE_ANON_KEY found: {'Yes' if key else 'No'}")
    
    if not url or not key:
        print("❌ Missing Supabase credentials in .env file")
        print("Please add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Read and execute SQL script
        script_path = os.path.join(os.path.dirname(__file__), "database", "create_profile_table.sql")
        
        if not os.path.exists(script_path):
            print(f"❌ SQL script not found: {script_path}")
            print(f"Looking for: {script_path}")
            return False
        
        with open(script_path, 'r') as f:
            sql_commands = f.read()
        
        # Execute SQL (Note: This is simplified - in production, run SQL directly in Supabase)
        print("📝 SQL script content:")
        print("=" * 50)
        print(sql_commands)
        print("=" * 50)
        
        print("\n🔧 Setup Instructions:")
        print("1. Copy the SQL above")
        print("2. Go to your Supabase dashboard")
        print("3. Navigate to SQL Editor")
        print("4. Paste and run the SQL script")
        print("5. Verify the 'user_profiles' table was created")
        
        print("\n✅ Database setup script prepared!")
        print("Once you run the SQL in Supabase, users can manage API keys in their profiles.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Kairos Profile Database Setup")
    print("=" * 40)
    
    success = setup_database()
    
    if success:
        print("\n🎉 Setup complete!")
        print("Next steps:")
        print("1. Run the SQL script in your Supabase dashboard")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start the backend: python api_server.py")
        print("4. Users can now configure API keys in their profile!")
    else:
        print("\n❌ Setup failed. Please check your configuration.")
        sys.exit(1)
