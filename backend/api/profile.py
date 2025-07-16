#!/usr/bin/env python3
"""
User Profile Management API
Handles secure storage and retrieval of user profiles with encrypted API keys
"""

import os
import hashlib
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from cryptography.fernet import Fernet
from datetime import datetime
import uuid
from database.supabase_client import supabase_client

# Create FastAPI router
router = APIRouter(prefix="/api", tags=["profile"])

# Encryption key (in production, store this securely)
ENCRYPTION_KEY = os.getenv("PROFILE_ENCRYPTION_KEY", Fernet.generate_key())
if isinstance(ENCRYPTION_KEY, str):
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()

try:
    cipher_suite = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"⚠️ Encryption key issue: {e}")
    # Generate a new key if the current one is invalid
    ENCRYPTION_KEY = Fernet.generate_key()
    cipher_suite = Fernet(ENCRYPTION_KEY)
    print(f"🔑 Generated new encryption key: {ENCRYPTION_KEY.decode()}")
    print("Add this to your .env file: PROFILE_ENCRYPTION_KEY=" + ENCRYPTION_KEY.decode())

class UserProfileRequest(BaseModel):
    profile: Dict[str, Any]

class UserProfileResponse(BaseModel):
    success: bool
    profile: Optional[Dict[str, Any]] = None
    message: str = ""

def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for secure storage"""
    if not api_key:
        return ""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key for use"""
    if not encrypted_key:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_key.encode()).decode()
    except Exception:
        return ""

async def get_current_user_id() -> str:
    """Get current user ID (simplified for demo - implement proper auth)"""
    # TODO: Replace with actual authentication
    return "default"

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)) -> UserProfileResponse:
    """Get user profile with decrypted API keys"""
    try:
        # Query user profile from database
        result = supabase_client.client.table("user_profiles").select("*").eq("user_id", user_id).execute()
        
        if not result.data:
            # Return empty profile for new users
            return UserProfileResponse(
                success=True,
                profile={
                    "id": "",
                    "username": "",
                    "email": "",
                    "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
                    "wallet_address": "",
                    "recall_api_key": "",
                    "coinpanic_api_key": "",
                    "consent_terms": False,
                    "consent_risks": False,
                    "consent_data": False,
                    "created_at": "",
                    "updated_at": ""
                },
                message="New profile"
            )
        
        profile_data = result.data[0]
        
        # Decrypt API keys before sending to frontend
        decrypted_profile = {
            "id": profile_data["id"],
            "username": profile_data["username"],
            "email": profile_data["email"],
            "avatar_url": profile_data["avatar_url"],
            "wallet_address": profile_data.get("wallet_address", ""),
            "recall_api_key": decrypt_api_key(profile_data.get("recall_api_key_encrypted", "")),
            "coinpanic_api_key": decrypt_api_key(profile_data.get("coinpanic_api_key_encrypted", "")),
            "consent_terms": profile_data.get("consent_terms", False),
            "consent_risks": profile_data.get("consent_risks", False),
            "consent_data": profile_data.get("consent_data", False),
            "created_at": profile_data["created_at"],
            "updated_at": profile_data["updated_at"]
        }
        
        return UserProfileResponse(
            success=True,
            profile=decrypted_profile,
            message="Profile loaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading profile: {str(e)}")

@router.post("/profile")
async def save_profile(
    request: UserProfileRequest, 
    user_id: str = Depends(get_current_user_id)
) -> UserProfileResponse:
    """Save user profile with encrypted API keys"""
    try:
        profile = request.profile
        
        # Validate required fields
        if not profile.get("username") or not profile.get("email"):
            raise HTTPException(status_code=400, detail="Username and email are required")
        
        # Encrypt API keys before storage
        profile_data = {
            "user_id": user_id,
            "username": profile["username"],
            "email": profile["email"],
            "avatar_url": profile.get("avatar_url", ""),
            "wallet_address": profile.get("wallet_address", ""),
            "recall_api_key_encrypted": encrypt_api_key(profile.get("recall_api_key", "")),
            "coinpanic_api_key_encrypted": encrypt_api_key(profile.get("coinpanic_api_key", "")),
            "consent_terms": profile.get("consent_terms", False),
            "consent_risks": profile.get("consent_risks", False),
            "consent_data": profile.get("consent_data", False),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Check if profile exists
        existing = supabase_client.client.table("user_profiles").select("id").eq("user_id", user_id).execute()
        
        if existing.data:
            # Update existing profile
            result = supabase_client.client.table("user_profiles").update(profile_data).eq("user_id", user_id).execute()
        else:
            # Create new profile
            profile_data["id"] = str(uuid.uuid4())
            profile_data["created_at"] = datetime.utcnow().isoformat()
            result = supabase_client.client.table("user_profiles").insert(profile_data).execute()
        
        if result.data:
            # Return decrypted profile
            saved_profile = result.data[0]
            response_profile = {
                "id": saved_profile["id"],
                "username": saved_profile["username"],
                "email": saved_profile["email"],
                "avatar_url": saved_profile["avatar_url"],
                "wallet_address": saved_profile.get("wallet_address", ""),
                "recall_api_key": profile.get("recall_api_key", ""),
                "coinpanic_api_key": profile.get("coinpanic_api_key", ""),
                "consent_terms": saved_profile.get("consent_terms", False),
                "consent_risks": saved_profile.get("consent_risks", False),
                "consent_data": saved_profile.get("consent_data", False),
                "created_at": saved_profile["created_at"],
                "updated_at": saved_profile["updated_at"]
            }
            
            return UserProfileResponse(
                success=True,
                profile=response_profile,
                message="Profile saved successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save profile")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")

@router.get("/profile/api-keys/{user_id}")
async def get_user_api_keys(user_id: str) -> Dict[str, str]:
    """
    Internal endpoint for backend services to get decrypted API keys
    This should only be called by backend services, never expose to frontend
    """
    try:
        result = supabase_client.client.table("user_profiles").select(
            "recall_api_key_encrypted, coinpanic_api_key_encrypted"
        ).eq("user_id", user_id).execute()
        
        if not result.data:
            return {"recall_api_key": "", "coinpanic_api_key": ""}
        
        profile = result.data[0]
        return {
            "recall_api_key": decrypt_api_key(profile.get("recall_api_key_encrypted", "")),
            "coinpanic_api_key": decrypt_api_key(profile.get("coinpanic_api_key_encrypted", ""))
        }
        
    except Exception as e:
        print(f"Error getting API keys for user {user_id}: {e}")
        return {"recall_api_key": "", "coinpanic_api_key": ""}

# Export the router
profile_router = router
