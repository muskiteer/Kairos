#!/usr/bin/env python3
"""
API Manager Utility
Handles retrieval of user-specific API keys from the database.
"""

from database.supabase_client import supabase_client
from typing import Dict

class APIManager:
    """Manages API key retrieval for different users."""

    def get_user_api_keys(self, user_id: str) -> Dict[str, str]:
        """
        Retrieves API keys for a given user from the Supabase 'profiles' table.
        This function is synchronous for simplicity.
        """
        try:
            print(f"🔑 Fetching API keys for user: {user_id}")
            
            # Query the 'profiles' table for the user's API keys
            # Note: .single() is used to get just one record.
            result = supabase_client.client.table("user_profiles").select(
                "recall_api_key_encrypted", "coinpanic_api_key_encrypted"
            ).eq("user_id", user_id).single().execute()
            
            if result.data:
                print("✅ API keys retrieved successfully.")
                # We need to decrypt these keys, assuming a utility function exists
                # For now, this part is simplified as the profile.py handles decryption
                return {
                    "recall_api_key_encrypted": result.data.get("recall_api_key_encrypted"),
                    "coinpanic_api_key_encrypted": result.data.get("coinpanic_api_key_encrypted"),
                }
            else:
                print(f"⚠️ No profile found for user {user_id}. API keys will be missing.")
                return {}

        except Exception as e:
            print(f"❌ Error fetching API keys for user {user_id}: {e}")
            # Return an empty dict on error to allow the agent to proceed with defaults
            return {}

# Create a global instance for easy importing
api_manager = APIManager()