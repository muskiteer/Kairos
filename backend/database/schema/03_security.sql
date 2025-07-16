-- Kairos Trading Database Security
-- Row Level Security (RLS) policies and security functions

-- Enable RLS on all user-data tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;

-- Create security functions
CREATE OR REPLACE FUNCTION auth.uid() 
RETURNS TEXT AS $$
BEGIN
    -- This function should return the current user ID from your auth system
    -- For now, we'll use a simple implementation
    RETURN COALESCE(current_setting('app.current_user_id', TRUE), 'anonymous');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION auth.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if current user is admin
    RETURN COALESCE(current_setting('app.user_role', TRUE), 'user') = 'admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 1. User Profiles Policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Admins can view all profiles" ON user_profiles
    FOR SELECT USING (auth.is_admin());

-- 2. Trading Sessions Policies
CREATE POLICY "Users can view own sessions" ON trading_sessions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update own sessions" ON trading_sessions
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can create own sessions" ON trading_sessions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Admins can view all sessions" ON trading_sessions
    FOR SELECT USING (auth.is_admin());

-- 3. Trades Policies
CREATE POLICY "Users can view own trades" ON trades
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = trades.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own trades" ON trades
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = trades.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own trades" ON trades
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = trades.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all trades" ON trades
    FOR SELECT USING (auth.is_admin());

-- 4. AI Strategies Policies
CREATE POLICY "Users can view own strategies" ON ai_strategies
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = ai_strategies.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own strategies" ON ai_strategies
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = ai_strategies.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own strategies" ON ai_strategies
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = ai_strategies.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all strategies" ON ai_strategies
    FOR SELECT USING (auth.is_admin());

-- 5. Session Analytics Policies
CREATE POLICY "Users can view own analytics" ON session_analytics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = session_analytics.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own analytics" ON session_analytics
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = session_analytics.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own analytics" ON session_analytics
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = session_analytics.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all analytics" ON session_analytics
    FOR SELECT USING (auth.is_admin());

-- 6. Portfolio Holdings Policies
CREATE POLICY "Users can view own holdings" ON portfolio_holdings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = portfolio_holdings.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own holdings" ON portfolio_holdings
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = portfolio_holdings.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own holdings" ON portfolio_holdings
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = portfolio_holdings.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all holdings" ON portfolio_holdings
    FOR SELECT USING (auth.is_admin());

-- 7. AI Conversations Policies
CREATE POLICY "Users can view own conversations" ON ai_conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = ai_conversations.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own conversations" ON ai_conversations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM trading_sessions 
            WHERE trading_sessions.id = ai_conversations.session_id 
            AND trading_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all conversations" ON ai_conversations
    FOR SELECT USING (auth.is_admin());

-- 8. Market Data - Public Read Access
-- Market data should be readable by all authenticated users
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read market data" ON market_data
    FOR SELECT USING (auth.uid() IS NOT NULL);

CREATE POLICY "System can insert market data" ON market_data
    FOR INSERT WITH CHECK (auth.is_admin() OR current_setting('app.system_role', TRUE) = 'data_collector');

-- 9. System Events - Admin Only
ALTER TABLE system_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view system events" ON system_events
    FOR SELECT USING (auth.is_admin());

CREATE POLICY "System can insert events" ON system_events
    FOR INSERT WITH CHECK (true); -- Allow system to log events

-- Create security audit functions
CREATE OR REPLACE FUNCTION log_security_event(
    p_event_type TEXT,
    p_user_id TEXT DEFAULT NULL,
    p_details JSONB DEFAULT '{}'
)
RETURNS void AS $$
BEGIN
    INSERT INTO system_events (
        event_type,
        event_category,
        user_id,
        event_data,
        severity,
        source
    ) VALUES (
        p_event_type,
        'security',
        COALESCE(p_user_id, auth.uid()),
        p_details,
        'info',
        'security_audit'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check user permissions
CREATE OR REPLACE FUNCTION check_user_session_access(
    p_session_id UUID,
    p_user_id TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM trading_sessions 
        WHERE id = p_session_id 
        AND user_id = COALESCE(p_user_id, auth.uid())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to validate trade permissions
CREATE OR REPLACE FUNCTION validate_trade_access(
    p_trade_id UUID,
    p_user_id TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM trades t
        JOIN trading_sessions s ON t.session_id = s.id
        WHERE t.id = p_trade_id 
        AND s.user_id = COALESCE(p_user_id, auth.uid())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Data retention policies
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete old market data (older than 6 months)
    DELETE FROM market_data 
    WHERE published_at < NOW() - INTERVAL '6 months';
    
    -- Delete old system events (older than 3 months, except errors)
    DELETE FROM system_events 
    WHERE created_at < NOW() - INTERVAL '3 months'
    AND severity NOT IN ('error', 'critical');
    
    -- Archive completed sessions older than 1 year
    UPDATE trading_sessions 
    SET session_metadata = session_metadata || '{"archived": true}'::jsonb
    WHERE end_time < NOW() - INTERVAL '1 year'
    AND status = 'completed'
    AND (session_metadata->>'archived')::boolean IS NOT TRUE;
    
    -- Log cleanup
    PERFORM log_security_event('data_cleanup', 'system', '{"cleanup_date": "' || NOW() || '"}');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create triggers for security auditing
CREATE OR REPLACE FUNCTION audit_sensitive_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log any changes to trading sessions
    IF TG_TABLE_NAME = 'trading_sessions' THEN
        PERFORM log_security_event(
            'session_' || TG_OP,
            NEW.user_id,
            jsonb_build_object(
                'session_id', NEW.id,
                'operation', TG_OP,
                'table', TG_TABLE_NAME
            )
        );
    END IF;
    
    -- Log any changes to trades
    IF TG_TABLE_NAME = 'trades' THEN
        PERFORM log_security_event(
            'trade_' || TG_OP,
            (SELECT user_id FROM trading_sessions WHERE id = NEW.session_id),
            jsonb_build_object(
                'trade_id', NEW.id,
                'session_id', NEW.session_id,
                'operation', TG_OP,
                'table', TG_TABLE_NAME
            )
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit triggers
CREATE TRIGGER audit_trading_sessions
    AFTER INSERT OR UPDATE ON trading_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_sensitive_changes();

CREATE TRIGGER audit_trades
    AFTER INSERT OR UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION audit_sensitive_changes();

-- Create role-based access functions
CREATE OR REPLACE FUNCTION create_user_role(p_user_id TEXT, p_role TEXT DEFAULT 'user')
RETURNS void AS $$
BEGIN
    -- Set user role in session
    PERFORM set_config('app.user_role', p_role, false);
    PERFORM set_config('app.current_user_id', p_user_id, false);
    
    -- Log role assignment
    PERFORM log_security_event(
        'role_assigned',
        p_user_id,
        jsonb_build_object('role', p_role)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- API key validation function
CREATE OR REPLACE FUNCTION validate_api_access(p_api_key TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- In production, this would validate against a proper API key table
    -- For now, we'll check against environment or return true for development
    RETURN p_api_key IS NOT NULL AND LENGTH(p_api_key) > 10;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Security status view
CREATE OR REPLACE VIEW security_status AS
SELECT 
    'RLS Enabled' as security_feature,
    COUNT(*) as tables_protected
FROM information_schema.tables t
JOIN pg_class c ON c.relname = t.table_name
WHERE t.table_schema = 'public'
AND c.relrowsecurity = true
UNION ALL
SELECT 
    'Active Policies' as security_feature,
    COUNT(*) as tables_protected
FROM pg_policies
WHERE schemaname = 'public';

COMMENT ON VIEW security_status IS 'Overview of database security features';

-- Log security setup completion
DO $$
BEGIN
    PERFORM log_security_event(
        'security_policies_created',
        'system',
        ('{"rls_enabled": true, "policies_created": true, "timestamp": "' || NOW() || '"}')::jsonb
    );
END $$;
