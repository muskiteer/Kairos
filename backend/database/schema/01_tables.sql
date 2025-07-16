-- Kairos Trading Database Schema
-- Creates all tables for the Kairos AI Trading System

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL UNIQUE,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    risk_tolerance TEXT DEFAULT 'moderate' CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- 2. Trading Sessions Table
CREATE TABLE IF NOT EXISTS trading_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    session_name TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'terminated')),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    initial_portfolio_value DECIMAL(20, 8),
    current_portfolio_value DECIMAL(20, 8),
    final_portfolio JSONB DEFAULT '{}',
    initial_portfolio JSONB DEFAULT '{}',
    total_profit_loss DECIMAL(20, 8) DEFAULT 0,
    total_pnl DECIMAL(20, 8) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    total_volume DECIMAL(20, 8) DEFAULT 0,
    ai_confidence_avg DECIMAL(5, 4),
    risk_score TEXT DEFAULT 'low' CHECK (risk_score IN ('low', 'medium', 'high', 'critical')),
    session_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Trades Table
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES trading_sessions(id) ON DELETE CASCADE,
    trade_type TEXT NOT NULL CHECK (trade_type IN ('buy', 'sell', 'swap', 'limit', 'market')),
    from_token TEXT NOT NULL,
    to_token TEXT NOT NULL,
    from_amount DECIMAL(20, 8) NOT NULL,
    to_amount DECIMAL(20, 8),
    expected_amount DECIMAL(20, 8),
    price DECIMAL(20, 8),
    slippage DECIMAL(5, 4),
    gas_fee DECIMAL(20, 8),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'failed', 'cancelled')),
    transaction_hash TEXT,
    block_number BIGINT,
    ai_reasoning TEXT,
    ai_confidence DECIMAL(5, 4),
    market_conditions JSONB,
    vincent_approval BOOLEAN DEFAULT false,
    vincent_risk_score DECIMAL(5, 4),
    vincent_recommendations JSONB,
    execution_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT positive_amounts CHECK (from_amount > 0 AND (to_amount IS NULL OR to_amount > 0)),
    CONSTRAINT valid_confidence CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    CONSTRAINT valid_vincent_score CHECK (vincent_risk_score IS NULL OR (vincent_risk_score >= 0 AND vincent_risk_score <= 1))
);

-- 4. AI Strategies Table (with vector embeddings)
CREATE TABLE IF NOT EXISTS ai_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES trading_sessions(id) ON DELETE CASCADE,
    strategy_name TEXT NOT NULL,
    strategy_type TEXT NOT NULL CHECK (strategy_type IN ('momentum', 'arbitrage', 'dca', 'swing', 'scalping', 'hodl', 'custom')),
    strategy_description TEXT,
    strategy_parameters JSONB NOT NULL,
    performance_metrics JSONB,
    success_rate DECIMAL(5, 4),
    total_return DECIMAL(10, 6),
    max_drawdown DECIMAL(5, 4),
    sharpe_ratio DECIMAL(8, 4),
    win_rate DECIMAL(5, 4),
    avg_trade_duration INTERVAL,
    strategy_embedding vector(1536), -- OpenAI/Gemini embedding size
    market_conditions JSONB,
    risk_assessment JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_success_rate CHECK (success_rate IS NULL OR (success_rate >= 0 AND success_rate <= 1)),
    CONSTRAINT valid_win_rate CHECK (win_rate IS NULL OR (win_rate >= 0 AND win_rate <= 1))
);

-- 5. Session Analytics Table
CREATE TABLE IF NOT EXISTS session_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES trading_sessions(id) ON DELETE CASCADE,
    analytics_date DATE DEFAULT CURRENT_DATE,
    
    -- Performance Metrics
    portfolio_value DECIMAL(20, 8),
    daily_pnl DECIMAL(20, 8),
    total_pnl DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    realized_pnl DECIMAL(20, 8),
    
    -- Trading Metrics
    trades_count INTEGER DEFAULT 0,
    successful_trades_count INTEGER DEFAULT 0,
    failed_trades_count INTEGER DEFAULT 0,
    volume_traded DECIMAL(20, 8) DEFAULT 0,
    fees_paid DECIMAL(20, 8) DEFAULT 0,
    
    -- AI Metrics
    avg_confidence DECIMAL(5, 4),
    strategy_changes INTEGER DEFAULT 0,
    vincent_approvals INTEGER DEFAULT 0,
    vincent_rejections INTEGER DEFAULT 0,
    
    -- Risk Metrics
    portfolio_volatility DECIMAL(8, 6),
    value_at_risk DECIMAL(20, 8),
    max_position_size DECIMAL(5, 4),
    correlation_matrix JSONB,
    
    -- Market Metrics
    market_sentiment DECIMAL(5, 4), -- -1 (bearish) to 1 (bullish)
    news_sentiment DECIMAL(5, 4),
    social_sentiment DECIMAL(5, 4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate analytics for same session/date
    UNIQUE(session_id, analytics_date)
);

-- 6. Portfolio Holdings Table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES trading_sessions(id) ON DELETE CASCADE,
    token_symbol TEXT NOT NULL,
    token_address TEXT,
    balance DECIMAL(20, 8) NOT NULL DEFAULT 0,
    usd_value DECIMAL(20, 8),
    avg_buy_price DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    allocation_percentage DECIMAL(5, 4),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint for session + token
    UNIQUE(session_id, token_symbol),
    
    -- Constraints
    CONSTRAINT positive_balance CHECK (balance >= 0),
    CONSTRAINT valid_allocation CHECK (allocation_percentage IS NULL OR (allocation_percentage >= 0 AND allocation_percentage <= 1))
);

-- 7. News and Market Data Table
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_type TEXT NOT NULL CHECK (data_type IN ('news', 'price', 'volume', 'sentiment', 'social')),
    source TEXT NOT NULL, -- 'coinpanic', 'coingecko', etc.
    symbol TEXT,
    title TEXT,
    content TEXT,
    url TEXT,
    sentiment_score DECIMAL(5, 4), -- -1 (negative) to 1 (positive)
    importance_score DECIMAL(5, 4), -- 0 to 1
    price_data JSONB,
    metadata JSONB,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. AI Conversations Table
CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES trading_sessions(id) ON DELETE CASCADE,
    message_order INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    intent TEXT,
    confidence DECIMAL(5, 4),
    actions_taken JSONB,
    reasoning TEXT,
    suggestions JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint for conversation order within session
    UNIQUE(session_id, message_order)
);

-- 9. System Events Log Table
CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    event_category TEXT NOT NULL CHECK (event_category IN ('trade', 'session', 'error', 'system', 'ai', 'security')),
    session_id UUID REFERENCES trading_sessions(id),
    user_id TEXT,
    event_data JSONB NOT NULL,
    severity TEXT DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    source TEXT NOT NULL, -- 'api_server', 'copilot', 'vincent', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trading_sessions_updated_at BEFORE UPDATE ON trading_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_strategies_updated_at BEFORE UPDATE ON ai_strategies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_session_analytics_updated_at BEFORE UPDATE ON session_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW session_summary AS
SELECT 
    s.id,
    s.user_id,
    s.session_name,
    s.status,
    s.start_time,
    s.end_time,
    s.total_trades,
    s.successful_trades,
    CASE 
        WHEN s.total_trades > 0 THEN (s.successful_trades::DECIMAL / s.total_trades) * 100
        ELSE 0 
    END as success_rate_percentage,
    s.current_portfolio_value,
    s.ai_confidence_avg,
    s.risk_score,
    COUNT(t.id) as actual_trade_count,
    COALESCE(a.total_pnl, 0) as total_pnl
FROM trading_sessions s
LEFT JOIN trades t ON s.id = t.session_id
LEFT JOIN session_analytics a ON s.id = a.session_id AND a.analytics_date = CURRENT_DATE
GROUP BY s.id, a.total_pnl;

-- Performance optimization: Create materialized view for analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_analytics AS
SELECT 
    analytics_date,
    COUNT(DISTINCT session_id) as active_sessions,
    SUM(trades_count) as total_trades,
    AVG(avg_confidence) as avg_ai_confidence,
    SUM(volume_traded) as total_volume,
    AVG(portfolio_value) as avg_portfolio_value
FROM session_analytics
GROUP BY analytics_date
ORDER BY analytics_date DESC;

-- Create refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_daily_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW daily_analytics;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE user_profiles IS 'User account information and preferences';
COMMENT ON TABLE trading_sessions IS 'Individual trading sessions with metadata';
COMMENT ON TABLE trades IS 'Individual trade records with AI reasoning';
COMMENT ON TABLE ai_strategies IS 'AI-generated trading strategies with vector embeddings';
COMMENT ON TABLE session_analytics IS 'Performance analytics and metrics';
COMMENT ON TABLE portfolio_holdings IS 'Current portfolio positions';
COMMENT ON TABLE market_data IS 'Market data, news, and sentiment information';
COMMENT ON TABLE ai_conversations IS 'Chat conversation history';
COMMENT ON TABLE system_events IS 'System event logs for monitoring';

-- Grant permissions (adjust as needed for your setup)
-- Note: In production, create specific roles with limited permissions
