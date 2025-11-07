"""
GOD MODE 1000 - NEWS AGGREGATOR
================================
Real-time Crypto News Aggregation with Sentiment Analysis
"""

import time
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from advanced_nlp_sentiment import advanced_nlp_sentiment as sentiment_analyzer
except ImportError:
    sentiment_analyzer = None

try:
    from news_sources_config import (
        ALL_NEWS_SOURCES, SOURCES_BY_TIER, SOURCES_BY_MARKET,
        get_sources_by_credibility, get_sources_for_market,
        SourceTier, MarketFocus
    )
except ImportError:
    ALL_NEWS_SOURCES = []
    SOURCES_BY_TIER = {}
    SOURCES_BY_MARKET = {}
    get_sources_by_credibility = lambda x: []
    get_sources_for_market = lambda x, y: []
    SourceTier = None
    MarketFocus = None


class NewsSource(Enum):
    """News source types with credibility tiers"""
    # Tier 1: Official/Government sources (highest credibility)
    SEC = "sec"  # US Securities and Exchange Commission
    CFTC = "cftc"  # Commodity Futures Trading Commission
    FED = "federal_reserve"
    ECB = "european_central_bank"
    PBOC = "peoples_bank_china"
    FSB = "financial_stability_board"
    
    # Tier 2: Premium financial media (high credibility)
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    WSJOURNAL = "wall_street_journal"
    FINANCIAL_TIMES = "financial_times"
    
    # Tier 3: Crypto-focused media (good credibility)
    CRYPTOPANIC = "cryptopanic"
    COINDESK = "coindesk"
    COINTELEGRAPH = "cointelegraph"
    BITCOINCOM = "bitcoin_com"
    DECRYPT = "decrypt"
    THEBLOCK = "theblock"
    
    # Tier 4: Social media (lower credibility, needs verification)
    TWITTER = "twitter"
    REDDIT = "reddit"

class SourceCredibilityTier(Enum):
    """Source credibility tier classification"""
    OFFICIAL = 1.0  # Government/regulatory
    PREMIUM = 0.9  # Established financial media
    MAINSTREAM = 0.7  # Crypto-focused media
    SOCIAL = 0.5  # Social media/forums

class TimeHorizonNews(Enum):
    """Time horizon for news impact with weight factors"""
    IMMEDIATE = ("immediate", 1.5)  # <24 hours - highest urgency weight
    SHORT_TERM = ("short_term", 1.2)  # 1-7 days - high weight for swing trading
    MEDIUM_TERM = ("medium_term", 1.0)  # 7-30 days - baseline weight
    LONG_TERM = ("long_term", 0.8)  # >30 days - lower immediate weight but strategic value
    
    def __init__(self, label: str, weight: float):
        self.label = label
        self.weight = weight  # Impact weight for trading decisions


@dataclass
class NewsArticle:
    """News article data structure with enhanced scoring"""
    title: str
    url: str
    source: str
    published_at: datetime
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    summary: str = ""
    symbols: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    impact_score: float = 0.0
    # NEW: Enhanced classification and scoring
    credibility_score: float = 0.7  # Based on source tier
    credibility_tier: SourceCredibilityTier = SourceCredibilityTier.MAINSTREAM
    time_horizon: TimeHorizonNews = TimeHorizonNews.SHORT_TERM
    is_regulatory: bool = False  # Government/regulatory news
    urgency_level: float = 0.5  # 0-1, how urgent the news is
    market_moving_potential: float = 0.5  # 0-1, potential to move market


class NewsAggregator:
    """News Aggregator - God Mode 1000"""
    
    def __init__(self):
        """Initialize News Aggregator"""
        self.unified_logger = unified_logging.get_logger("news_aggregator")
        self.sentiment_analyzer = sentiment_analyzer
        
        # News storage
        self.news_cache: List[NewsArticle] = []
        self.max_cache_size = 2000  # Increased for more sources
        
        # ENHANCED: Load 100+ news sources from configuration
        self.all_sources = ALL_NEWS_SOURCES if ALL_NEWS_SOURCES else []
        self.sources_by_tier = SOURCES_BY_TIER if SOURCES_BY_TIER else {}
        self.sources_by_market = SOURCES_BY_MARKET if SOURCES_BY_MARKET else {}
        
        # API endpoints (legacy + new sources)
        self.api_endpoints = {
            NewsSource.CRYPTOPANIC: "https://cryptopanic.com/api/v1/posts/",
            NewsSource.COINDESK: "https://api.coindesk.com/v1/news/",
            NewsSource.SEC: "https://www.sec.gov/cgi-bin/browse-edgar",
            NewsSource.CFTC: "https://www.cftc.gov/PressRoom/PressReleases/index.htm",
        }
        
        # Add RSS endpoints from configuration
        for source in self.all_sources:
            if source.api_endpoint and not source.requires_api_key:
                self.api_endpoints[source.name] = source.api_endpoint
        
        # Source credibility mapping - ENHANCED with 100+ sources
        self.source_credibility = {
            # Government/Regulatory (Tier 1)
            'sec': SourceCredibilityTier.OFFICIAL,
            'cftc': SourceCredibilityTier.OFFICIAL,
            'federal_reserve': SourceCredibilityTier.OFFICIAL,
            'ecb': SourceCredibilityTier.OFFICIAL,
            'bank_of_england': SourceCredibilityTier.OFFICIAL,
            'bank_of_japan': SourceCredibilityTier.OFFICIAL,
            'pboc': SourceCredibilityTier.OFFICIAL,
            
            # Premium Financial Media (Tier 2)
            'bloomberg': SourceCredibilityTier.PREMIUM,
            'reuters': SourceCredibilityTier.PREMIUM,
            'wall_street_journal': SourceCredibilityTier.PREMIUM,
            'financial_times': SourceCredibilityTier.PREMIUM,
            'cnbc': SourceCredibilityTier.PREMIUM,
            'marketwatch': SourceCredibilityTier.PREMIUM,
            
            # Crypto Media (Tier 3)
            'coindesk': SourceCredibilityTier.MAINSTREAM,
            'cointelegraph': SourceCredibilityTier.MAINSTREAM,
            'theblock': SourceCredibilityTier.MAINSTREAM,
            'decrypt': SourceCredibilityTier.MAINSTREAM,
            'cryptoslate': SourceCredibilityTier.MAINSTREAM,
            'beincrypto': SourceCredibilityTier.MAINSTREAM,
            
            # Forex Media (Tier 3)
            'forexlive': SourceCredibilityTier.MAINSTREAM,
            'fxstreet': SourceCredibilityTier.MAINSTREAM,
            'dailyfx': SourceCredibilityTier.MAINSTREAM,
            
            # Social Media (Tier 4)
            'twitter': SourceCredibilityTier.SOCIAL,
            'reddit': SourceCredibilityTier.SOCIAL,
        }
        
        # API keys (loaded from environment)
        import os
        self.api_keys = {
            'cryptopanic': os.getenv('CRYPTOPANIC_API_KEY', ''),
            'newsapi': os.getenv('NEWSAPI_KEY', ''),
            'twitter': os.getenv('TWITTER_API_KEY', ''),
            'reddit': os.getenv('REDDIT_API_KEY', ''),
        }
        
        # Cache settings
        self.cache_ttl = 300  # 5 minutes
        self.last_fetch_time = None
        
        source_count = len(self.all_sources)
        tier_breakdown = {
            'tier1': len([s for s in self.all_sources if s.tier == SourceTier.TIER_1_OFFICIAL]) if SourceTier else 0,
            'tier2': len([s for s in self.all_sources if s.tier == SourceTier.TIER_2_PREMIUM]) if SourceTier else 0,
            'tier3': len([s for s in self.all_sources if s.tier == SourceTier.TIER_3_MAINSTREAM]) if SourceTier else 0,
            'tier4': len([s for s in self.all_sources if s.tier == SourceTier.TIER_4_SOCIAL]) if SourceTier else 0,
        }
        
        self.unified_logger.info(
            f"✅ News Aggregator initialized - {source_count} sources "
            f"(T1: {tier_breakdown['tier1']}, T2: {tier_breakdown['tier2']}, "
            f"T3: {tier_breakdown['tier3']}, T4: {tier_breakdown['tier4']})"
        )
    
    def get_latest_news(self, limit: int = 50, symbols: Optional[List[str]] = None) -> List[NewsArticle]:
        """Get latest crypto news"""
        try:
            # Check if cache needs refresh
            if self._should_refresh_cache():
                self._fetch_all_news()
            
            # Filter by symbols if specified
            if symbols:
                filtered = [n for n in self.news_cache if any(s in n.symbols for s in symbols)]
                return filtered[:limit]
            
            return self.news_cache[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get latest news: {e}")
            return []
    
    def get_news_for_symbol(self, symbol: str, hours: int = 24, limit: int = 20) -> List[NewsArticle]:
        """Get news for specific symbol"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Filter news by symbol and time
            symbol_news = [
                n for n in self.news_cache
                if symbol in n.symbols and n.published_at >= cutoff_time
            ]
            
            # Sort by impact score and recency
            symbol_news.sort(key=lambda x: (x.impact_score, x.published_at), reverse=True)
            
            return symbol_news[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get news for {symbol}: {e}")
            return []
    
    def get_aggregated_news(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get aggregated news data with sentiment for a symbol - REQUIRED by ai_training_engine
        
        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH")
            hours: Time window in hours (default: 24)
            
        Returns:
            Dictionary with sentiment_score, article_count, and articles list
        """
        try:
            # Ensure cache is fresh
            if self._should_refresh_cache():
                self._fetch_all_news()
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Filter news by symbol and time
            symbol_news = [
                n for n in self.news_cache
                if symbol in n.symbols and n.published_at >= cutoff_time
            ]
            
            if not symbol_news:
                return {
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'article_count': 0,
                    'articles': [],
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'neutral_count': 0
                }
            
            # Calculate aggregated sentiment
            total_sentiment = sum(n.sentiment_score for n in symbol_news)
            avg_sentiment = total_sentiment / len(symbol_news)
            
            bullish_count = sum(1 for n in symbol_news if n.sentiment_score > 0.2)
            bearish_count = sum(1 for n in symbol_news if n.sentiment_score < -0.2)
            neutral_count = len(symbol_news) - bullish_count - bearish_count
            
            # Determine label
            if avg_sentiment > 0.3:
                label = 'very_bullish'
            elif avg_sentiment > 0.1:
                label = 'bullish'
            elif avg_sentiment < -0.3:
                label = 'very_bearish'
            elif avg_sentiment < -0.1:
                label = 'bearish'
            else:
                label = 'neutral'
            
            return {
                'sentiment_score': avg_sentiment,
                'sentiment_label': label,
                'article_count': len(symbol_news),
                'articles': symbol_news,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'neutral_count': neutral_count,
                'sentiment_trend': self._calculate_sentiment_trend(symbol_news)
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get aggregated news for {symbol}: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'article_count': 0,
                'articles': [],
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0
            }
    
    def get_sentiment_summary(self, symbol: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get aggregated sentiment from news"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Filter news
            if symbol:
                news = [n for n in self.news_cache if symbol in n.symbols and n.published_at >= cutoff_time]
            else:
                news = [n for n in self.news_cache if n.published_at >= cutoff_time]
            
            if not news:
                return {
                    'overall_sentiment': 0.0,
                    'sentiment_label': 'neutral',
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0
                }
            
            # Calculate sentiment stats
            total_sentiment = sum(n.sentiment_score for n in news)
            avg_sentiment = total_sentiment / len(news)
            
            bullish_count = sum(1 for n in news if n.sentiment_score > 0.2)
            bearish_count = sum(1 for n in news if n.sentiment_score < -0.2)
            neutral_count = len(news) - bullish_count - bearish_count
            
            # Determine label
            if avg_sentiment > 0.3:
                label = 'very_bullish'
            elif avg_sentiment > 0.1:
                label = 'bullish'
            elif avg_sentiment < -0.3:
                label = 'very_bearish'
            elif avg_sentiment < -0.1:
                label = 'bearish'
            else:
                label = 'neutral'
            
            return {
                'overall_sentiment': avg_sentiment,
                'sentiment_label': label,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'neutral_count': neutral_count,
                'total_articles': len(news),
                'sentiment_trend': self._calculate_sentiment_trend(news)
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get sentiment summary: {e}")
            return {
                'overall_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
    
    def get_trending_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending crypto topics"""
        try:
            # Extract keywords from recent news
            recent_news = [n for n in self.news_cache if 
                          (datetime.now(timezone.utc) - n.published_at).total_seconds() < 86400]
            
            if not recent_news:
                return []
            
            # Count symbol mentions
            symbol_counts = {}
            for article in recent_news:
                for symbol in article.symbols:
                    if symbol not in symbol_counts:
                        symbol_counts[symbol] = {
                            'count': 0,
                            'sentiment': 0.0,
                            'impact': 0.0
                        }
                    symbol_counts[symbol]['count'] += 1
                    symbol_counts[symbol]['sentiment'] += article.sentiment_score
                    symbol_counts[symbol]['impact'] += article.impact_score
            
            # Calculate averages and sort
            trending = []
            for symbol, data in symbol_counts.items():
                trending.append({
                    'symbol': symbol,
                    'mention_count': data['count'],
                    'avg_sentiment': data['sentiment'] / data['count'],
                    'total_impact': data['impact'],
                    'trend_score': data['count'] * (1 + abs(data['sentiment'] / data['count']))
                })
            
            trending.sort(key=lambda x: x['trend_score'], reverse=True)
            return trending[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get trending topics: {e}")
            return []
    
    def get_breaking_news(self, minutes: int = 30) -> List[NewsArticle]:
        """Get breaking news (very recent)"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            breaking = [n for n in self.news_cache if n.published_at >= cutoff_time]
            
            # Sort by impact and recency
            breaking.sort(key=lambda x: (x.impact_score, x.published_at), reverse=True)
            
            return breaking
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get breaking news: {e}")
            return []
    
    # ==================== PRIVATE METHODS ====================
    
    def _fetch_all_news(self):
        """Fetch news from all sources - ENHANCED with multiple RSS sources"""
        try:
            new_articles = []
            
            # Fetch from CryptoPanic (if API key available)
            cryptopanic_news = self._fetch_cryptopanic_news()
            if cryptopanic_news:
                new_articles.extend(cryptopanic_news)
                self.unified_logger.info(f"   📰 CryptoPanic: {len(cryptopanic_news)} articles")
            
            # Fetch from RSS sources (from configuration) - PARALLEL for speed
            rss_sources = [
                ('CoinDesk', 'https://www.coindesk.com/arc/outboundfeeds/rss/'),
                ('Cointelegraph', 'https://cointelegraph.com/rss'),
                ('Bitcoin Magazine', 'https://bitcoinmagazine.com/.rss/full/'),
                ('Decrypt', 'https://decrypt.co/feed'),
                ('CryptoSlate', 'https://cryptoslate.com/feed/'),
                ('The Block', 'https://www.theblock.co/rss.xml'),
                ('U.Today', 'https://u.today/rss'),
                ('BeInCrypto', 'https://beincrypto.com/feed/'),
            ]
            
            # Fetch RSS in parallel for performance
            from concurrent.futures import ThreadPoolExecutor, as_completed
            rss_articles = []
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_source = {
                    executor.submit(self._fetch_rss_feed, source_name, url): source_name 
                    for source_name, url in rss_sources
                }
                
                for future in as_completed(future_to_source, timeout=15):
                    source_name = future_to_source[future]
                    try:
                        articles = future.result()
                        if articles:
                            rss_articles.extend(articles)
                            self.unified_logger.debug(f"   📰 {source_name}: {len(articles)} articles")
                    except Exception as e:
                        self.unified_logger.debug(f"   ⚠️ {source_name} failed: {e}")
            
            if rss_articles:
                new_articles.extend(rss_articles)
                self.unified_logger.info(f"   📰 RSS Feeds: {len(rss_articles)} articles from {len(rss_sources)} sources")
            
            # Analyze sentiment for new articles (PARALLEL for speed)
            if self.sentiment_analyzer and new_articles:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []
                    for article in new_articles:
                        if not article.sentiment_score or article.sentiment_score == 0.0:
                            text = f"{article.title} {article.summary}"
                            future = executor.submit(self._analyze_article_sentiment, article, text)
                            futures.append(future)
                    
                    # Wait for all sentiment analysis to complete
                    for future in as_completed(futures, timeout=10):
                        try:
                            future.result()
                        except Exception as e:
                            self.unified_logger.debug(f"Sentiment analysis failed: {e}")
            
            # Add to cache (deduplicate by URL)
            existing_urls = {article.url for article in self.news_cache}
            unique_new_articles = [a for a in new_articles if a.url not in existing_urls]
            
            self.news_cache = unique_new_articles + self.news_cache
            
            # Trim cache
            if len(self.news_cache) > self.max_cache_size:
                self.news_cache = self.news_cache[:self.max_cache_size]
            
            self.last_fetch_time = datetime.now(timezone.utc)
            self.unified_logger.info(f"✅ Fetched {len(unique_new_articles)} new unique articles (total cache: {len(self.news_cache)})")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to fetch all news: {e}")
    
    def _fetch_cryptopanic_news(self) -> List[NewsArticle]:
        """Fetch from CryptoPanic API"""
        try:
            import os
            api_key = os.getenv('CRYPTOPANIC_API_KEY')
            if not api_key:
                return []
            
            url = self.api_endpoints.get(NewsSource.CRYPTOPANIC)
            params = {
                'auth_token': api_key,
                'public': 'true',
                'kind': 'news',
                'filter': 'hot'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for item in data.get('results', [])[:50]:
                    article = NewsArticle(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        source=item.get('source', {}).get('title', 'CryptoPanic'),
                        published_at=datetime.fromisoformat(item.get('published_at', '').replace('Z', '+00:00')),
                        symbols=[c['code'] for c in item.get('currencies', [])],
                        sentiment_score=0.0,
                        sentiment_label='neutral'
                    )
                    
                    # Calculate sentiment if analyzer available
                    if self.sentiment_analyzer:
                        try:
                            sentiment = self.sentiment_analyzer.analyze_text(article.title)
                            article.sentiment_score = sentiment.sentiment_score
                            article.sentiment_label = sentiment.sentiment_label
                        except:
                            pass
                    
                    articles.append(article)
                
                return articles
            return []
        except Exception as e:
            self.unified_logger.error(f"Failed to fetch CryptoPanic news: {e}")
            return []
    
    def _fetch_rss_feed(self, source_name: str, rss_url: str) -> List[NewsArticle]:
        """Fetch articles from RSS feed"""
        try:
            import feedparser
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:20]:  # Limit to 20 articles per source
                try:
                    # Parse published date
                    pub_date = datetime.now(timezone.utc)
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        import time as time_module
                        pub_date = datetime.fromtimestamp(
                            time_module.mktime(entry.published_parsed),
                            tz=timezone.utc
                        )
                    
                    # Extract title and summary
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    
                    # Clean HTML tags from summary
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = summary[:500]  # Limit summary length
                    
                    article = NewsArticle(
                        title=title,
                        summary=summary,
                        url=entry.get('link', ''),
                        source=source_name,
                        published_at=pub_date,
                        symbols=[],  # Will be extracted from text
                        sentiment_score=0.0,
                        sentiment_label='neutral',
                        credibility_score=self.source_credibility.get(source_name, 0.7),
                        impact_score=0.5
                    )
                    
                    # Extract crypto symbols from title and summary
                    text = (title + " " + summary).upper()
                    for symbol in ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'MATIC', 'AVAX', 'LINK']:
                        if symbol in text:
                            article.symbols.append(symbol)
                    
                    articles.append(article)
                    
                except Exception as entry_error:
                    self.unified_logger.debug(f"Error parsing RSS entry from {source_name}: {entry_error}")
                    continue
            
            return articles
            
        except Exception as e:
            self.unified_logger.debug(f"Failed to fetch RSS from {source_name}: {e}")
            return []
    
    def _analyze_article_sentiment(self, article: NewsArticle, text: str):
        """Analyze sentiment for an article (thread-safe)"""
        try:
            if self.sentiment_analyzer:
                sentiment = self.sentiment_analyzer.analyze_text(text)
                if sentiment:
                    article.sentiment_score = sentiment.get('score', sentiment.get('sentiment_score', 0.0))
                    article.sentiment_label = sentiment.get('label', sentiment.get('sentiment_label', 'neutral'))
        except Exception as e:
            self.unified_logger.debug(f"Sentiment analysis error: {e}")
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed"""
        if self.last_fetch_time is None:
            return True
        
        elapsed = (datetime.now(timezone.utc) - self.last_fetch_time).total_seconds()
        return elapsed >= self.cache_ttl
    
    def _calculate_sentiment_trend(self, news: List[NewsArticle]) -> str:
        """Calculate sentiment trend direction"""
        try:
            if len(news) < 5:
                return 'insufficient_data'
            
            # Split into older and newer half
            mid_point = len(news) // 2
            older_news = news[:mid_point]
            newer_news = news[mid_point:]
            
            older_sentiment = sum(n.sentiment_score for n in older_news) / len(older_news)
            newer_sentiment = sum(n.sentiment_score for n in newer_news) / len(newer_news)
            
            change = newer_sentiment - older_sentiment
            
            if change > 0.1:
                return 'improving'
            elif change < -0.1:
                return 'deteriorating'
            else:
                return 'stable'
        except:
            return 'unknown'


# Global instance
news_aggregator = NewsAggregator()

