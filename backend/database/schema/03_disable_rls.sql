-- Kairos Trading Database - Disable RLS
-- Disable Row Level Security for development/testing

-- Disable RLS on all tables
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE trading_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE trades DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_strategies DISABLE ROW LEVEL SECURITY;
ALTER TABLE session_analytics DISABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings DISABLE ROW LEVEL SECURITY;
ALTER TABLE market_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE system_events DISABLE ROW LEVEL SECURITY;

-- Drop any existing RLS policies (optional cleanup)
DROP POLICY IF EXISTS user_profiles_policy ON user_profiles;
DROP POLICY IF EXISTS trading_sessions_policy ON trading_sessions;
DROP POLICY IF EXISTS trades_policy ON trades;
DROP POLICY IF EXISTS ai_strategies_policy ON ai_strategies;
DROP POLICY IF EXISTS session_analytics_policy ON session_analytics;
DROP POLICY IF EXISTS portfolio_holdings_policy ON portfolio_holdings;
DROP POLICY IF EXISTS market_data_policy ON market_data;
DROP POLICY IF EXISTS ai_conversations_policy ON ai_conversations;
DROP POLICY IF EXISTS system_events_policy ON system_events;

-- Grant full access to postgres role
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Grant access to anon role for API usage
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon;

COMMENT ON SCHEMA public IS 'RLS disabled for Kairos Trading System - Full access mode';
