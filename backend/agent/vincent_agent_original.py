#!/usr/bin/env python3
"""
Vincent AI Agent Integration
Provides policy and compliance checks for trading decisions
"""

import os
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime

class VincentAgent:
    """Vincent AI Agent for policy and compliance checks"""
    
    def __init__(self):
        """Initialize Vincent AI client"""
        self.api_key = os.getenv("VINCENT_API_KEY")
        self.api_url = os.getenv("VINCENT_API_URL", "https://api.vincent.ai")
        
        if not self.api_key:
            print("⚠️ Vincent AI API key not found - running in demo mode")
            self.demo_mode = True
        else:
            self.demo_mode = False
    
    async def check_trade_policy(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a trade complies with policies"""
        if self.demo_mode:
            return self._demo_policy_check(trade_data)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/policy/check",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "trade_type": trade_data.get("trade_type"),
                        "from_token": trade_data.get("from_token"),
                        "to_token": trade_data.get("to_token"),
                        "amount": trade_data.get("amount"),
                        "user_risk_profile": trade_data.get("risk_profile", "moderate"),
                        "market_conditions": trade_data.get("market_conditions", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "approved": False,
                        "reason": f"Vincent API error: {response.status_code}",
                        "risk_score": 10
                    }
        except Exception as e:
            return {
                "approved": False,
                "reason": f"Vincent API connection error: {str(e)}",
                "risk_score": 10
            }
    
    async def get_risk_assessment(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive risk assessment of portfolio"""
        if self.demo_mode:
            return self._demo_risk_assessment(portfolio_data)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/risk/assess",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "portfolio": portfolio_data,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return self._demo_risk_assessment(portfolio_data)
        except Exception as e:
            return self._demo_risk_assessment(portfolio_data)
    
    async def validate_strategy(self, strategy_text: str, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a trading strategy against compliance rules"""
        if self.demo_mode:
            return self._demo_strategy_validation(strategy_text, market_context)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/strategy/validate",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "strategy": strategy_text,
                        "market_context": market_context,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return self._demo_strategy_validation(strategy_text, market_context)
        except Exception as e:
            return self._demo_strategy_validation(strategy_text, market_context)
    
    def _demo_policy_check(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Demo mode policy check with realistic responses"""
        amount = float(trade_data.get("amount", 0))
        from_token = trade_data.get("from_token", "").upper()
        to_token = trade_data.get("to_token", "").upper()
        
        # Simple risk-based approval logic for demo
        risk_score = 1
        reasons = []
        
        # High amount check
        if amount > 10000:
            risk_score += 3
            reasons.append("High trade amount detected")
        
        # Volatile token check
        volatile_tokens = ["SHIB", "DOGE", "MEME"]
        if any(token in volatile_tokens for token in [from_token, to_token]):
            risk_score += 2
            reasons.append("Trading volatile cryptocurrency")
        
        # Market timing check (simplified)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 1
            reasons.append("Trading outside optimal hours")
        
        approved = risk_score <= 5
        
        return {
            "approved": approved,
            "risk_score": risk_score,
            "reasons": reasons if not approved else ["Trade approved within risk parameters"],
            "recommendations": [
                "Consider dollar-cost averaging for large amounts",
                "Monitor market volatility before execution",
                "Set appropriate stop-loss levels"
            ],
            "compliance_status": "COMPLIANT" if approved else "REVIEW_REQUIRED",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _demo_risk_assessment(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Demo mode risk assessment"""
        return {
            "overall_risk": "MODERATE",
            "risk_score": 3.5,
            "diversification_score": 7.2,
            "volatility_assessment": "MEDIUM",
            "recommendations": [
                "Portfolio shows good diversification",
                "Consider reducing exposure to high-risk assets",
                "Maintain 10-20% stable coin allocation"
            ],
            "compliance_issues": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _demo_strategy_validation(self, strategy_text: str, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Demo mode strategy validation"""
        # Simple keyword-based validation for demo
        risk_keywords = ["aggressive", "all-in", "yolo", "moon"]
        conservative_keywords = ["conservative", "safe", "stable", "gradual"]
        
        has_risk = any(keyword in strategy_text.lower() for keyword in risk_keywords)
        has_conservative = any(keyword in strategy_text.lower() for keyword in conservative_keywords)
        
        if has_risk and not has_conservative:
            validation_score = 4
            status = "HIGH_RISK"
        elif has_conservative:
            validation_score = 8
            status = "APPROVED"
        else:
            validation_score = 6
            status = "MODERATE_RISK"
        
        return {
            "validation_score": validation_score,
            "status": status,
            "approved": validation_score >= 6,
            "concerns": ["High volatility exposure"] if has_risk else [],
            "suggestions": [
                "Consider implementing stop-loss mechanisms",
                "Add risk management parameters",
                "Include market condition checks"
            ],
            "compliance_notes": "Strategy reviewed for regulatory compliance",
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instance
vincent_agent = VincentAgent()
