#!/usr/bin/env python3
"""
CoinPanic API Integration for Cryptocurrency News
Enhanced with dynamic API key support from user profiles
"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

# Load environment variables
load_dotenv()

class CoinPanicAPI:
    """CoinPanic API client for crypto news with dynamic API key support"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinPanic API client
        
        Args:
            api_key: Optional API key. If not provided, falls back to environment variable
        """
        self.base_url = "https://cryptopanic.com/api/v1"
        self.api_key = api_key or os.getenv("COINPANIC_API_KEY")
        
    def set_api_key(self, api_key: str):
        """Set API key dynamically"""
        self.api_key = api_key
        
    def get_crypto_news(self, currencies=None, limit=5, kind="news", filter_type="hot"):
        """
        Get cryptocurrency news from CoinPanic (optimized for speed)
        
        Args:
            currencies: List of currency codes (e.g., ['BTC', 'ETH']) or None for all
            limit: Number of news items to return (default 5 for speed)
            kind: Type of posts ('news', 'media', 'all')
            filter_type: Filter type ('hot', 'new', 'bullish', 'bearish', 'important')
        """
        try:
            # Optimize parameters for faster response
            params = {
                'auth_token': self.api_key,
                'limit': min(limit, 20),  # Reduced max limit for speed
                'kind': kind,
                'filter': filter_type
            }
            
            if currencies:
                params['currencies'] = ','.join(currencies)
            
            # Set timeout for faster response
            response = requests.get(f"{self.base_url}/posts/", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                return self._format_news_data(data['results'])
            else:
                return {"error": "No news data found"}
                
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get news: {str(e)}"}
    
    def get_trending_news(self, limit=3):
        """Get trending cryptocurrency news (fast)"""
        return self.get_crypto_news(limit=limit, filter_type="hot")
    
    def get_currency_news(self, currency, limit=5):
        """Get news for a specific currency (fast)"""
        return self.get_crypto_news(currencies=[currency.upper()], limit=limit)
    
    def get_bullish_news(self, limit=5):
        """Get bullish cryptocurrency news (fast)"""
        return self.get_crypto_news(limit=limit, filter_type="bullish")
    
    def get_bearish_news(self, limit=5):
        """Get bearish cryptocurrency news (fast)"""
        return self.get_crypto_news(limit=limit, filter_type="bearish")
    
    def _format_news_data(self, news_items):
        """Format news data for display (optimized)"""
        formatted_news = []
        
        for item in news_items:
            try:
                # Extract only essential information for speed
                news_item = {
                    'title': item.get('title', 'No title'),
                    'url': item.get('url', ''),
                    'published_at': item.get('published_at', ''),
                    'source': item.get('source', {}).get('title', 'Unknown'),
                    'currencies': [c.get('code', '') for c in item.get('currencies', [])],
                    'votes': {
                        'positive': item.get('votes', {}).get('positive', 0),
                        'negative': item.get('votes', {}).get('negative', 0)
                    }
                }
                
                formatted_news.append(news_item)
                
            except Exception as e:
                # Skip malformed items
                continue
        
        return {
            'news': formatted_news,
            'count': len(formatted_news)
        }
    
    def format_news_for_display(self, news_data, show_summary=False):
        """Format news data for human-readable display (fast mode)"""
        if 'error' in news_data:
            return f"❌ Error getting news: {news_data['error']}"
        
        if not news_data.get('news'):
            return "📰 No news found"
        
        display = "\n📰 Crypto News:\n"
        
        for i, item in enumerate(news_data['news'], 1):
            display += f"{i}. {item['title']}\n"
            
            # Add currencies if available
            if item['currencies']:
                display += f"   🪙 {', '.join(item['currencies'])}"
            
            # Add sentiment quickly
            votes = item['votes']
            if votes['positive'] > 0 or votes['negative'] > 0:
                display += f" | 📊 +{votes['positive']}/-{votes['negative']}"
            
            display += "\n"
        
        return display

# Create global instance
coinpanic_api = CoinPanicAPI()

# Convenience functions (optimized)
def get_crypto_news(currencies=None, limit=5):
    """Get cryptocurrency news (fast)"""
    return coinpanic_api.get_crypto_news(currencies=currencies, limit=limit)

def get_trending_news(limit=3):
    """Get trending crypto news (fast)"""
    return coinpanic_api.get_trending_news(limit=limit)

def get_currency_news(currency, limit=5):
    """Get news for specific currency (fast)"""
    return coinpanic_api.get_currency_news(currency, limit=limit)

def get_bullish_news(limit=5):
    """Get bullish crypto news (fast)"""
    return coinpanic_api.get_bullish_news(limit=limit)

def get_bearish_news(limit=5):
    """Get bearish crypto news (fast)"""
    return coinpanic_api.get_bearish_news(limit=limit)
