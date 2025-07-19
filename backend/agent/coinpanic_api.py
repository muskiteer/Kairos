import feedparser
from datetime import datetime
from typing import Optional, List, Dict, Any


class CoinPanicAPI:
    """RSS-based crypto news fetcher (simulating CoinPanic behavior)"""

    def __init__(self, api_key: Optional[str] = None):
        self.rss_feeds = [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cointelegraph.com/rss",
            "https://cryptoslate.com/feed/"
        ]

    def get_crypto_news(self, currencies=None, limit=50, kind="news", filter_type="hot"):
        try:
            return {
                "news": self._fetch_rss_news(limit=limit),
                "count": limit
            }
        except Exception as e:
            return {"error": f"Failed to fetch RSS news: {str(e)}"}

    def get_trending_news(self, limit=3):
        return self.get_crypto_news(limit=limit)

    def get_currency_news(self, currency, limit=5):
        return self.get_crypto_news(limit=limit)  # RSS feeds don't filter by currency

    def get_bullish_news(self, limit=5):
        return self.get_crypto_news(limit=limit)  # Simulated, no actual sentiment

    def get_bearish_news(self, limit=5):
        return self.get_crypto_news(limit=limit)  # Simulated, no actual sentiment

    def _fetch_rss_news(self, limit=50):
        seen_titles = set()
        news_items = []

        for url in self.rss_feeds:
            feed = feedparser.parse(url)
            feed_items = 0  # Track per feed

            for entry in feed.entries:
                if feed_items >= limit:
                    break
                title = entry.get('title', 'No title')
                if title not in seen_titles:
                    seen_titles.add(title)
                    news_items.append({
                        'title': title,
                        'url': entry.get('link', ''),
                        'published_at': entry.get('published', ''),
                        'source': feed.feed.get('title', 'Unknown'),
                        'currencies': [],
                        'votes': {'positive': 0, 'negative': 0}
                    })
                    feed_items += 1

        # Sort news by latest
        news_items.sort(key=lambda x: x['published_at'], reverse=True)
        return news_items


# 🔓 Top-level helper functions for external imports

_coinpanic_instance = CoinPanicAPI()

def get_crypto_news(currencies=None, limit=50, kind="news", filter_type="hot"):
    return _coinpanic_instance.get_crypto_news(currencies, limit, kind, filter_type)

def get_trending_news(limit=3):
    return _coinpanic_instance.get_trending_news(limit)

def get_currency_news(currency, limit=5):
    return _coinpanic_instance.get_currency_news(currency, limit)

def get_bullish_news(limit=5):
    return _coinpanic_instance.get_bullish_news(limit)

def get_bearish_news(limit=5):
    return _coinpanic_instance.get_bearish_news(limit)


# ✅ Main block for standalone execution
if __name__ == "__main__":
    print("📰 Latest Crypto News:\n")
    result = get_crypto_news(limit=10)
    if "news" in result:
        for i, item in enumerate(result["news"], start=1):
            print(f"{i}. {item['title']}")
            print(f"   📅 {item['published_at']}")
            print(f"   🔗 {item['url']}")
            print(f"   📰 Source: {item['source']}")
            print("-" * 60)
    else:
        print("❌ Error:", result.get("error"))
