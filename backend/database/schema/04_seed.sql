-- Kairos Trading Database Seed Data
-- Sample data for testing and development

-- 1. Insert sample user profiles
INSERT INTO user_profiles (user_id, email, display_name, preferences, risk_tolerance) VALUES
('demo_user_1', 'demo@kairos.ai', 'Demo Trader', 
 '{"notifications": true, "theme": "dark", "trading_pairs": ["ETH/USDC", "BTC/USDC"]}', 'moderate'),
('demo_user_2', 'alice@kairos.ai', 'Alice Cooper', 
 '{"notifications": false, "theme": "light", "trading_pairs": ["ETH/USDC"]}', 'conservative'),
('admin_user', 'admin@kairos.ai', 'Kairos Admin', 
 '{"admin_level": "full", "notifications": true}', 'moderate')
ON CONFLICT (user_id) DO NOTHING;

-- 2. Insert sample trading sessions
INSERT INTO trading_sessions (
    id, user_id, session_name, status, start_time, 
    initial_portfolio_value, current_portfolio_value, 
    total_trades, successful_trades, total_volume, 
    ai_confidence_avg, risk_score
) VALUES
('11111111-1111-1111-1111-111111111111', 'demo_user_1', 'Morning Trading Session', 'active', 
 NOW() - INTERVAL '2 hours', 5000.00, 5245.30, 8, 7, 2500.00, 0.87, 'low'),
('22222222-2222-2222-2222-222222222222', 'demo_user_1', 'Swing Trading Strategy', 'completed', 
 NOW() - INTERVAL '2 days', 3000.00, 3456.78, 15, 12, 4200.00, 0.82, 'medium'),
('33333333-3333-3333-3333-333333333333', 'demo_user_2', 'Conservative Portfolio', 'active', 
 NOW() - INTERVAL '1 hour', 2000.00, 2034.50, 3, 3, 800.00, 0.91, 'low')
ON CONFLICT (id) DO NOTHING;

-- 3. Insert sample trades
INSERT INTO trades (
    session_id, trade_type, from_token, to_token, from_amount, to_amount, 
    price, status, ai_reasoning, ai_confidence, vincent_approval, vincent_risk_score
) VALUES
('11111111-1111-1111-1111-111111111111', 'swap', 'USDC', 'ETH', 500.00, 0.154, 3245.00, 'executed',
 'Strong bullish momentum detected. ETH showing support at $3200 level with increasing volume.', 0.89, true, 0.25),
('11111111-1111-1111-1111-111111111111', 'swap', 'ETH', 'WBTC', 0.077, 0.001234, 62500.00, 'executed',
 'Bitcoin correlation breaking down. WBTC showing relative strength vs ETH.', 0.76, true, 0.35),
('11111111-1111-1111-1111-111111111111', 'swap', 'USDC', 'UNI', 200.00, 28.57, 7.00, 'executed',
 'DeFi sector rotation. UNI governance proposal creating positive sentiment.', 0.82, true, 0.45),
('22222222-2222-2222-2222-222222222222', 'swap', 'USDC', 'ETH', 1000.00, 0.308, 3250.00, 'executed',
 'Major support level hold. Technical indicators suggest continuation pattern.', 0.85, true, 0.30),
('33333333-3333-3333-3333-333333333333', 'swap', 'USDC', 'ETH', 300.00, 0.092, 3260.00, 'executed',
 'Dollar cost averaging entry. Conservative position sizing for long-term hold.', 0.91, true, 0.15)
ON CONFLICT DO NOTHING;

-- 4. Insert sample AI strategies
INSERT INTO ai_strategies (
    session_id, strategy_name, strategy_type, strategy_description,
    strategy_parameters, performance_metrics, success_rate, total_return
) VALUES
('11111111-1111-1111-1111-111111111111', 'Momentum Scalping', 'momentum',
 'Short-term momentum trading based on volume and price action signals',
 '{"timeframe": "5m", "volume_threshold": 1.5, "rsi_oversold": 30, "rsi_overbought": 70}',
 '{"sharpe_ratio": 1.45, "max_drawdown": 0.08, "win_rate": 0.72}', 0.72, 0.15),
('22222222-2222-2222-2222-222222222222', 'ETH Swing Strategy', 'swing',
 'Medium-term swing trading focusing on ETH major support/resistance levels',
 '{"timeframe": "4h", "support_levels": [3200, 3000, 2800], "resistance_levels": [3500, 3800, 4000]}',
 '{"sharpe_ratio": 1.23, "max_drawdown": 0.12, "win_rate": 0.80}', 0.80, 0.25),
('33333333-3333-3333-3333-333333333333', 'Conservative DCA', 'dca',
 'Dollar cost averaging with conservative position sizing and blue-chip focus',
 '{"frequency": "daily", "amount": 100, "tokens": ["ETH", "BTC"], "rebalance_threshold": 0.1}',
 '{"sharpe_ratio": 0.95, "max_drawdown": 0.05, "win_rate": 0.95}', 0.95, 0.08)
ON CONFLICT DO NOTHING;

-- 5. Insert sample session analytics
INSERT INTO session_analytics (
    session_id, analytics_date, portfolio_value, daily_pnl, total_pnl,
    trades_count, successful_trades_count, volume_traded, avg_confidence
) VALUES
('11111111-1111-1111-1111-111111111111', CURRENT_DATE, 5245.30, 45.30, 245.30, 8, 7, 2500.00, 0.87),
('22222222-2222-2222-2222-222222222222', CURRENT_DATE - 1, 3456.78, 156.78, 456.78, 15, 12, 4200.00, 0.82),
('33333333-3333-3333-3333-333333333333', CURRENT_DATE, 2034.50, 34.50, 34.50, 3, 3, 800.00, 0.91)
ON CONFLICT (session_id, analytics_date) DO NOTHING;

-- 6. Insert sample portfolio holdings
INSERT INTO portfolio_holdings (
    session_id, token_symbol, balance, usd_value, avg_buy_price, allocation_percentage
) VALUES
('11111111-1111-1111-1111-111111111111', 'USDC', 2500.00, 2500.00, 1.00, 0.476),
('11111111-1111-1111-1111-111111111111', 'ETH', 0.847, 2745.30, 3240.00, 0.523),
('22222222-2222-2222-2222-222222222222', 'USDC', 1000.00, 1000.00, 1.00, 0.289),
('22222222-2222-2222-2222-222222222222', 'ETH', 0.755, 2456.78, 3255.00, 0.711),
('33333333-3333-3333-3333-333333333333', 'USDC', 1700.00, 1700.00, 1.00, 0.836),
('33333333-3333-3333-3333-333333333333', 'ETH', 0.103, 334.50, 3250.00, 0.164)
ON CONFLICT (session_id, token_symbol) DO NOTHING;

-- 7. Insert sample market data
INSERT INTO market_data (
    data_type, source, symbol, title, content, sentiment_score, importance_score, published_at
) VALUES
('news', 'coinpanic', 'ETH', 'Ethereum Upgrade Scheduled for Next Month',
 'Major Ethereum network upgrade expected to improve scalability and reduce fees.',
 0.8, 0.9, NOW() - INTERVAL '2 hours'),
('news', 'coinpanic', 'BTC', 'Bitcoin Reaches New Resistance Level',
 'Bitcoin testing key resistance at $67,000 with strong institutional buying.',
 0.6, 0.7, NOW() - INTERVAL '1 hour'),
('news', 'coinpanic', 'DeFi', 'DeFi TVL Reaches All-Time High',
 'Total value locked in DeFi protocols surpasses previous records amid growing adoption.',
 0.9, 0.8, NOW() - INTERVAL '30 minutes'),
('sentiment', 'social', 'ETH', 'Ethereum Social Sentiment Analysis',
 'Bullish sentiment predominant across social media platforms.',
 0.75, 0.6, NOW() - INTERVAL '15 minutes'),
('price', 'coingecko', 'ETH', 'Ethereum Price Update',
 'ETH trading at $3,245 with 24h volume of $15.2B',
 0.0, 0.5, NOW() - INTERVAL '5 minutes')
ON CONFLICT DO NOTHING;

-- 8. Insert sample AI conversations
INSERT INTO ai_conversations (
    session_id, message_order, role, content, intent, confidence, reasoning
) VALUES
('11111111-1111-1111-1111-111111111111', 1, 'user', 'I want to buy some ETH with 500 USDC', 'trade_request', 0.95, NULL),
('11111111-1111-1111-1111-111111111111', 2, 'assistant', 
 'I''ll analyze the market conditions for ETH... Current price is $3,245 with strong bullish momentum. Executing trade: 500 USDC → 0.154 ETH',
 'trade_executed', 0.89, 'Strong bullish momentum detected with volume confirmation'),
('11111111-1111-1111-1111-111111111111', 3, 'user', 'How is my portfolio performing?', 'portfolio_inquiry', 0.98, NULL),
('11111111-1111-1111-1111-111111111111', 4, 'assistant',
 'Your portfolio is performing well! Current value: $5,245.30 (+4.9%). You have 8 trades with 87.5% success rate.',
 'portfolio_analysis', 0.92, 'Portfolio analysis based on current holdings and trade history'),
('33333333-3333-3333-3333-333333333333', 1, 'user', 'What''s a safe way to start trading?', 'strategy_discussion', 0.85, NULL),
('33333333-3333-3333-3333-333333333333', 2, 'assistant',
 'For beginners, I recommend dollar-cost averaging with major cryptocurrencies like ETH and BTC. Start small and gradually increase exposure.',
 'strategy_discussion', 0.91, 'Conservative approach recommended for new traders')
ON CONFLICT (session_id, message_order) DO NOTHING;

-- 9. Insert sample system events
INSERT INTO system_events (
    event_type, event_category, event_data, severity, source
) VALUES
('database_initialized', 'system', '{"tables_created": 9, "indexes_created": 45}', 'info', 'database_setup'),
('user_session_started', 'session', '{"user_id": "demo_user_1", "session_id": "11111111-1111-1111-1111-111111111111"}', 'info', 'api_server'),
('trade_executed', 'trade', '{"trade_id": "sample", "amount": 500, "success": true}', 'info', 'copilot'),
('ai_strategy_generated', 'ai', '{"strategy_type": "momentum", "confidence": 0.87}', 'info', 'copilot'),
('vincent_policy_check', 'ai', '{"approved": true, "risk_score": 0.25}', 'info', 'vincent')
ON CONFLICT DO NOTHING;

-- 10. Refresh materialized views
REFRESH MATERIALIZED VIEW daily_analytics;

-- 11. Update table statistics
SELECT update_table_statistics();

-- 12. Verify data integrity
DO $$
DECLARE
    session_count INTEGER;
    trade_count INTEGER;
    strategy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO session_count FROM trading_sessions;
    SELECT COUNT(*) INTO trade_count FROM trades;
    SELECT COUNT(*) INTO strategy_count FROM ai_strategies;
    
    RAISE NOTICE 'Seed data inserted successfully:';
    RAISE NOTICE '  Trading Sessions: %', session_count;
    RAISE NOTICE '  Trades: %', trade_count;
    RAISE NOTICE '  AI Strategies: %', strategy_count;
    
    -- Log successful seeding
    INSERT INTO system_events (event_type, event_category, event_data, severity, source)
    VALUES (
        'seed_data_completed',
        'system',
        jsonb_build_object(
            'sessions', session_count,
            'trades', trade_count,
            'strategies', strategy_count,
            'timestamp', NOW()
        ),
        'info',
        'database_seed'
    );
END $$;

-- 13. Create sample vector embeddings (simplified for demonstration)
UPDATE ai_strategies 
SET strategy_embedding = array_fill(random(), ARRAY[1536])::vector
WHERE strategy_embedding IS NULL;

COMMENT ON FUNCTION update_table_statistics() IS 'Seed data provides sample trading sessions, trades, and AI strategies for development and testing';
