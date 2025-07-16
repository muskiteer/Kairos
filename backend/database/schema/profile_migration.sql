-- Migration: Add Profile Management Fields to existing user_profiles table
-- Run this SQL in your Supabase SQL editor

-- Add missing columns for profile management
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS username TEXT,
ADD COLUMN IF NOT EXISTS wallet_address TEXT,
ADD COLUMN IF NOT EXISTS recall_api_key_encrypted TEXT,
ADD COLUMN IF NOT EXISTS coinpanic_api_key_encrypted TEXT,
ADD COLUMN IF NOT EXISTS consent_terms BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS consent_risks BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS consent_data BOOLEAN DEFAULT false;

-- Update any existing records to have default values
UPDATE user_profiles 
SET 
    username = COALESCE(username, display_name, 'User_' || SUBSTRING(user_id, 1, 8)),
    consent_terms = COALESCE(consent_terms, false),
    consent_risks = COALESCE(consent_risks, false),
    consent_data = COALESCE(consent_data, false)
WHERE username IS NULL OR consent_terms IS NULL;

-- Disable RLS temporarily for development (enable this line if you have permission issues)
-- ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Insert a default profile for testing
INSERT INTO user_profiles (
    user_id, 
    username, 
    email, 
    display_name,
    avatar_url,
    consent_terms,
    consent_risks
) VALUES (
    'default', 
    'Demo User', 
    'demo@kairos.ai',
    'Demo User',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
    true,
    true
) ON CONFLICT (user_id) DO UPDATE SET
    username = EXCLUDED.username,
    email = EXCLUDED.email,
    avatar_url = EXCLUDED.avatar_url;

-- Verify the migration
SELECT 
    'Migration completed successfully!' as status,
    COUNT(*) as total_profiles,
    COUNT(CASE WHEN username IS NOT NULL THEN 1 END) as profiles_with_username,
    COUNT(CASE WHEN consent_terms = true THEN 1 END) as consented_profiles
FROM user_profiles;
