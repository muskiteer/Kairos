#!/usr/bin/env python3
"""
Dynamic API Key Manager
Handles retrieval of user API keys from profiles
"""

import asyncio
from typing import Dict, Optional
from api.profile import get_user_api_keys

class DynamicAPIManager:
    """Manages dynamic API keys from user profiles"""
    
    def __init__(self):
        self._api_key_cache = {}
        
    async def get_user_api_keys(self, user_id: str) -> Dict[str, str]:
        """Get API keys for a specific user"""
        try:
            # Check cache first (optional optimization)
            if user_id in self._api_key_cache:
                return self._api_key_cache[user_id]
                
            # Fetch from database
            api_keys = await get_user_api_keys(user_id)
            
            # Cache for this session (optional)
            self._api_key_cache[user_id] = api_keys
            
            return api_keys
            
        except Exception as e:
            print(f"Error getting API keys for user {user_id}: {e}")
            return {"recall_api_key": "", "coinpanic_api_key": ""}
    
    def clear_cache(self, user_id: Optional[str] = None):
        """Clear cached API keys"""
        if user_id:
            self._api_key_cache.pop(user_id, None)
        else:
            self._api_key_cache.clear()

# Global instance
api_manager = DynamicAPIManager()
