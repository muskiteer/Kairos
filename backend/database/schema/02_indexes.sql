-- Kairos Trading Database Indexes
-- Performance optimization indexes for faster queries

-- 1. Trading Sessions Indexes
CREATE INDEX IF NOT EXISTS idx_trading_sessions_user_id ON trading_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_sessions_status ON trading_sessions(status);
CREATE INDEX IF NOT EXISTS idx_trading_sessions_created_at ON trading_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trading_sessions_user_status ON trading_sessions(user_id, status);

-- 2. Trades Indexes
CREATE INDEX IF NOT EXISTS idx_trades_session_id ON trades(session_id);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_execution_time ON trades(execution_time DESC);
CREATE INDEX IF NOT EXISTS idx_trades_from_token ON trades(from_token);
CREATE INDEX IF NOT EXISTS idx_trades_to_token ON trades(to_token);
CREATE INDEX IF NOT EXISTS idx_trades_trade_type ON trades(trade_type);
CREATE INDEX IF NOT EXISTS idx_trades_session_status ON trades(session_id, status);
CREATE INDEX IF NOT EXISTS idx_trades_session_time ON trades(session_id, execution_time DESC);

-- 3. AI Strategies Indexes
CREATE INDEX IF NOT EXISTS idx_ai_strategies_session_id ON ai_strategies(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_strategies_type ON ai_strategies(strategy_type);
CREATE INDEX IF NOT EXISTS idx_ai_strategies_active ON ai_strategies(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_strategies_performance ON ai_strategies(success_rate DESC, total_return DESC);

-- Vector similarity search index (for strategy recommendations)
CREATE INDEX IF NOT EXISTS idx_ai_strategies_embedding ON ai_strategies 
USING ivfflat (strategy_embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Session Analytics Indexes
CREATE INDEX IF NOT EXISTS idx_session_analytics_session_id ON session_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_session_analytics_date ON session_analytics(analytics_date DESC);
CREATE INDEX IF NOT EXISTS idx_session_analytics_session_date ON session_analytics(session_id, analytics_date);

-- 5. Portfolio Holdings Indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_session_id ON portfolio_holdings(session_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_token ON portfolio_holdings(token_symbol);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_value ON portfolio_holdings(usd_value DESC);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_updated ON portfolio_holdings(last_updated DESC);

-- 6. Market Data Indexes
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_type ON market_data(data_type);
CREATE INDEX IF NOT EXISTS idx_market_data_source ON market_data(source);
CREATE INDEX IF NOT EXISTS idx_market_data_published ON market_data(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_sentiment ON market_data(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_date ON market_data(symbol, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_type_date ON market_data(data_type, published_at DESC);

-- 7. AI Conversations Indexes
CREATE INDEX IF NOT EXISTS idx_ai_conversations_session_id ON ai_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_order ON ai_conversations(session_id, message_order);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_role ON ai_conversations(role);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_intent ON ai_conversations(intent);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_created ON ai_conversations(created_at DESC);

-- 8. System Events Indexes
CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_system_events_category ON system_events(event_category);
CREATE INDEX IF NOT EXISTS idx_system_events_session_id ON system_events(session_id);
CREATE INDEX IF NOT EXISTS idx_system_events_user_id ON system_events(user_id);
CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events(severity);
CREATE INDEX IF NOT EXISTS idx_system_events_created ON system_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_system_events_source ON system_events(source);

-- 9. User Profiles Indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_active ON user_profiles(is_active);

-- 10. Composite Indexes for Complex Queries

-- Session performance analysis
CREATE INDEX IF NOT EXISTS idx_session_performance ON trading_sessions(user_id, status, created_at DESC, current_portfolio_value);

-- Trade analysis by session and time
CREATE INDEX IF NOT EXISTS idx_trade_analysis ON trades(session_id, status, execution_time DESC, ai_confidence);

-- Strategy performance lookup
CREATE INDEX IF NOT EXISTS idx_strategy_performance ON ai_strategies(strategy_type, is_active, success_rate DESC, created_at DESC);

-- Market data time series
CREATE INDEX IF NOT EXISTS idx_market_timeseries ON market_data(symbol, data_type, published_at DESC);

-- Portfolio value tracking
CREATE INDEX IF NOT EXISTS idx_portfolio_tracking ON portfolio_holdings(session_id, last_updated DESC, usd_value DESC);

-- Analytics time series
CREATE INDEX IF NOT EXISTS idx_analytics_timeseries ON session_analytics(session_id, analytics_date DESC, portfolio_value);

-- 11. Partial Indexes for Active Data

-- Only index active sessions
CREATE INDEX IF NOT EXISTS idx_active_sessions ON trading_sessions(user_id, created_at DESC) 
WHERE status = 'active';

-- Only index successful trades
CREATE INDEX IF NOT EXISTS idx_successful_trades ON trades(session_id, execution_time DESC) 
WHERE status = 'executed';

-- Only index active strategies
CREATE INDEX IF NOT EXISTS idx_active_strategies ON ai_strategies(strategy_type, success_rate DESC) 
WHERE is_active = true;

-- Recent market data index (covering all data - can filter in queries)
CREATE INDEX IF NOT EXISTS idx_recent_market_data ON market_data(symbol, published_at DESC);

-- 12. JSONB Indexes for Metadata Queries

-- Session metadata
CREATE INDEX IF NOT EXISTS idx_session_metadata ON trading_sessions USING GIN (session_metadata);

-- Trade market conditions
CREATE INDEX IF NOT EXISTS idx_trade_market_conditions ON trades USING GIN (market_conditions);

-- Strategy parameters
CREATE INDEX IF NOT EXISTS idx_strategy_parameters ON ai_strategies USING GIN (strategy_parameters);

-- Analytics correlation matrix
CREATE INDEX IF NOT EXISTS idx_analytics_correlation ON session_analytics USING GIN (correlation_matrix);

-- Event data
CREATE INDEX IF NOT EXISTS idx_system_events_data ON system_events USING GIN (event_data);

-- 13. Text Search Indexes

-- Full text search on AI conversations
CREATE INDEX IF NOT EXISTS idx_conversations_text_search ON ai_conversations 
USING GIN (to_tsvector('english', content));

-- Full text search on market data
CREATE INDEX IF NOT EXISTS idx_market_data_text_search ON market_data 
USING GIN (to_tsvector('english', title || ' ' || COALESCE(content, '')));

-- 14. Statistics and Maintenance

-- Update table statistics
ANALYZE user_profiles;
ANALYZE trading_sessions;
ANALYZE trades;
ANALYZE ai_strategies;
ANALYZE session_analytics;
ANALYZE portfolio_holdings;
ANALYZE market_data;
ANALYZE ai_conversations;
ANALYZE system_events;

-- Create function to update statistics regularly
CREATE OR REPLACE FUNCTION update_table_statistics()
RETURNS void AS $$
BEGIN
    ANALYZE user_profiles;
    ANALYZE trading_sessions;
    ANALYZE trades;
    ANALYZE ai_strategies;
    ANALYZE session_analytics;
    ANALYZE portfolio_holdings;
    ANALYZE market_data;
    ANALYZE ai_conversations;
    ANALYZE system_events;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_table_statistics() IS 'Updates table statistics for query optimization';

-- Log index creation
INSERT INTO system_events (event_type, event_category, event_data, severity, source)
VALUES (
    'database_indexes_created',
    'system',
    ('{"indexes_created": true, "timestamp": "' || NOW() || '"}')::jsonb,
    'info',
    'database_setup'
);
