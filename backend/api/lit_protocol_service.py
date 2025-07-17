#!/usr/bin/env python3
"""
Dynamic API Service for Lit Protocol Integration
Handles decentralized API key management and replaces database profile functions
"""

import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import os

class LitProtocolAPIService:
    """Service for handling decentralized API management without database"""
    
    def __init__(self):
        self.user_api_cache = {}  # In-memory cache for session
        self.initialized = False
        
    def initialize(self):
        """Initialize the Lit Protocol service"""
        try:
            print("🔐 Initializing Lit Protocol API Service...")
            # In production, this would connect to Lit Protocol nodes
            # For now, we just mark as initialized
            self.initialized = True
            print("✅ Lit Protocol service initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Lit Protocol initialization failed: {e}")
            self.initialized = False
        
    async def get_user_api_keys(self, wallet_address: str) -> Dict[str, str]:
        """
        Get API keys for a user from their decentralized profile
        This would normally query Lit Protocol/IPFS, but for now returns empty
        In production, this would integrate with the frontend's Lit Protocol service
        """
        try:
            # Check cache first
            if wallet_address in self.user_api_cache:
                return self.user_api_cache[wallet_address]
                
            # In production, this would:
            # 1. Query IPFS for user's encrypted profile
            # 2. Use Lit Protocol to decrypt API keys
            # 3. Return decrypted keys
            
            # For now, return empty keys - frontend handles the encryption
            return {
                "recall_api_key": "",
                "coinpanic_api_key": ""
            }
            
        except Exception as e:
            print(f"Error getting API keys for wallet {wallet_address}: {e}")
            return {"recall_api_key": "", "coinpanic_api_key": ""}
    
    def set_session_api_keys(self, wallet_address: str, api_keys: Dict[str, str]):
        """Set API keys for current session (temporary cache)"""
        self.user_api_cache[wallet_address] = api_keys
        
    def clear_cache(self):
        """Clear API key cache"""
        self.user_api_cache.clear()

# Global instance
lit_api_service = LitProtocolAPIService()

# Legacy functions for backward compatibility
async def get_user_api_keys(user_id: str) -> Dict[str, str]:
    """Legacy function - now uses wallet address instead of user_id"""
    return await lit_api_service.get_user_api_keys(user_id)

def create_user_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function for profile creation
    Now returns success since profiles are handled by Lit Protocol
    """
    return {
        "success": True,
        "message": "Profile creation handled by Lit Protocol",
        "profile": profile_data
    }

def update_user_profile(wallet_address: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function for profile updates
    Now returns success since profiles are handled by Lit Protocol
    """
    return {
        "success": True,
        "message": "Profile updates handled by Lit Protocol",
        "profile": profile_data
    }

def get_user_profile(wallet_address: str) -> Optional[Dict[str, Any]]:
    """
    Legacy function for profile retrieval
    Returns None since profiles are now decentralized
    """
    return None

# Report generation without email
class DecentralizedReportGenerator:
    """Generate reports for browser download instead of email"""
    
    def __init__(self):
        self.reports_cache = {}
    
    async def generate_trading_report(self, session_id: str, trading_data: Dict[str, Any]) -> str:
        """Generate trading report and return download URL/path"""
        try:
            # Generate report content
            report_content = self._generate_report_content(trading_data)
            
            # Create report file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kairos_trading_report_{session_id}_{timestamp}.json"
            
            # Store in cache for download
            self.reports_cache[filename] = {
                "content": report_content,
                "generated_at": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            return filename
            
        except Exception as e:
            print(f"Error generating trading report: {e}")
            return None
    
    def _generate_report_content(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive trading report content"""
        return {
            "report_type": "Kairos Trading Session Report",
            "generated_at": datetime.now().isoformat(),
            "session_data": trading_data,
            "summary": {
                "total_trades": trading_data.get("total_trades", 0),
                "session_duration": trading_data.get("duration", "Unknown"),
                "performance": trading_data.get("performance", {}),
                "ai_insights": trading_data.get("ai_insights", [])
            },
            "trades": trading_data.get("trades", []),
            "analytics": trading_data.get("analytics", {}),
            "recommendations": trading_data.get("recommendations", []),
            "disclaimer": "This report is for paper trading simulation only. No real funds were used."
        }
    
    def get_report(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get report content for download"""
        return self.reports_cache.get(filename)
    
    def cleanup_old_reports(self, max_age_hours: int = 24):
        """Clean up old reports from cache"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for filename, report_data in self.reports_cache.items():
            report_time = datetime.fromisoformat(report_data["generated_at"]).timestamp()
            if report_time < cutoff_time:
                to_remove.append(filename)
        
        for filename in to_remove:
            del self.reports_cache[filename]

# Global instance
report_generator = DecentralizedReportGenerator()
