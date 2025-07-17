#!/usr/bin/env python3
"""
Dynamic API Key Manager with Lit Protocol Integration
Handles retrieval of user API keys from decentralized profiles
"""

import asyncio
from typing import Dict, Optional

class DynamicAPIManager:
    """Manages dynamic API keys from decentralized user profiles"""
    
    def __init__(self):
        self._api_key_cache = {}
        
    async def get_user_api_keys(self, wallet_address: str) -> Dict[str, str]:
        """Get API keys for a specific wallet address"""
        try:
            # Check cache first (optional optimization)
            if wallet_address in self._api_key_cache:
                return self._api_key_cache[wallet_address]
                
            # In production, this would fetch from Lit Protocol/IPFS
            # For now, return empty - frontend handles encryption/decryption
            api_keys = {"recall_api_key": "", "coinpanic_api_key": ""}
            
            # Cache for this session (optional)
            self._api_key_cache[wallet_address] = api_keys
            
            return api_keys
            
        except Exception as e:
            print(f"Error getting API keys for wallet {wallet_address}: {e}")
            return {"recall_api_key": "", "coinpanic_api_key": ""}
    
    def set_session_api_keys(self, wallet_address: str, api_keys: Dict[str, str]):
        """Set API keys for current session (from frontend decryption)"""
        self._api_key_cache[wallet_address] = api_keys
        print(f"✅ API keys cached for wallet: {wallet_address[:10]}...")
    
    def clear_cache(self, wallet_address: Optional[str] = None):
        """Clear cached API keys"""
        if wallet_address:
            self._api_key_cache.pop(wallet_address, None)
        else:
            self._api_key_cache.clear()

# Global instance
api_manager = DynamicAPIManager()
