"""
GOD MODE 1000 - ADVANCED SEARCH ENGINE
Intelligent multi-source search for crypto coins with KOL influence
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import warnings
warnings.filterwarnings('ignore')

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from .real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None

try:
    from .kol_influence_tracker import kol_influence_tracker
except ImportError:
    kol_influence_tracker = None

try:
    from .advanced_nlp_sentiment import advanced_nlp_sentiment as sentiment_analysis_engine
except ImportError:
    sentiment_analysis_engine = None

try:
    from .onchain_tokenomics_analyzer import onchain_tokenomics_analyzer
except ImportError:
    onchain_tokenomics_analyzer = None

@dataclass
class SearchResult:
    """Search result with comprehensive data"""
    symbol: str
    name: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    score: float
    signals: List[str]
    kol_mentions: int
    sentiment_score: float
    tokenomics_score: float
    trending_rank: Optional[int]
    metadata: Dict[str, Any]

class AdvancedSearchEngine:
    """Multi-source intelligent search for crypto assets"""
    
    def __init__(self):
        """Initialize search engine"""
        try:
            self.unified_logger = unified_logging.get_logger("advanced_search")
            
            self.search_cache: Dict[str, Any] = {}
            self.cache_ttl = 300  # 5 minutes
            
            self.unified_logger.info("Advanced Search Engine initialized")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize search engine: {e}")
            raise
    
    async def search_coins(self, 
                          query: str = "",
                          filters: Dict[str, Any] = None,
                          limit: int = 50) -> List[SearchResult]:
        """
        Advanced search with multi-source data integration
        
        Args:
            query: Search query (coin name/symbol)
            filters: Search filters (price range, volume, etc.)
            limit: Max results
        """
        try:
            results = []
            filters = filters or {}
            
            # Get base coin list from market data
            if real_market_data_fetcher:
                all_symbols = real_market_data_fetcher.get_top_symbols_by_volume(limit=200)
            else:
                return []
            
            # Filter by query
            if query:
                query_upper = query.upper()
                filtered_symbols = [
                    s for s in all_symbols 
                    if query_upper in s.upper()
                ]
            else:
                filtered_symbols = all_symbols
            
            # Process each symbol
            for symbol in filtered_symbols[:limit]:
                try:
                    result = await self._analyze_symbol(symbol, filters)
                    if result and result.score > 0:
                        results.append(result)
                except Exception as e:
                    self.unified_logger.debug(f"Failed to analyze {symbol}: {e}")
                    continue
            
            # Sort by score
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Search failed: {e}")
            return []
    
    async def _analyze_symbol(self, symbol: str, filters: Dict[str, Any]) -> Optional[SearchResult]:
        """Analyze single symbol with all data sources"""
        try:
            # Market data
            market_data = real_market_data_fetcher.get_market_data(symbol) if real_market_data_fetcher else None
            if not market_data:
                return None
            
            price = market_data['price']
            change_24h = market_data['change_24h']
            volume_24h = market_data['volume_24h']
            
            # Apply filters
            if filters.get('min_price') and price < filters['min_price']:
                return None
            if filters.get('max_price') and price > filters['max_price']:
                return None
            if filters.get('min_volume') and volume_24h < filters['min_volume']:
                return None
            if filters.get('min_change') and change_24h < filters['min_change']:
                return None
            if filters.get('max_change') and change_24h > filters['max_change']:
                return None
            
            # Calculate score components
            score_components = {}
            signals = []
            
            # KOL influence
            kol_mentions = 0
            if kol_influence_tracker:
                try:
                    base_coin = symbol.split('/')[0]
                    trending = kol_influence_tracker.get_trending_coins(limit=50)
                    for coin_data in trending:
                        if coin_data['symbol'].upper() == base_coin.upper():
                            kol_mentions = coin_data['total_mentions']
                            score_components['kol'] = min(kol_mentions * 10, 30)
                            if kol_mentions > 0:
                                signals.append(f"🎯 {kol_mentions} KOL mentions")
                            break
                except Exception:
                    pass
            
            # Sentiment analysis
            sentiment_score = 0.5
            if sentiment_analysis_engine:
                try:
                    base_coin = symbol.split('/')[0]
                    sentiment_data = sentiment_analysis_engine.get_coin_sentiment(base_coin)
                    sentiment_score = sentiment_data.get('score', 0.5)
                    score_components['sentiment'] = (sentiment_score - 0.5) * 40
                    
                    if sentiment_score > 0.7:
                        signals.append(f"📈 Bullish sentiment {sentiment_score:.0%}")
                    elif sentiment_score < 0.3:
                        signals.append(f"📉 Bearish sentiment {sentiment_score:.0%}")
                except Exception:
                    pass
            
            # Tokenomics
            tokenomics_score = 50
            if onchain_tokenomics_analyzer:
                try:
                    base_coin = symbol.split('/')[0]
                    analysis = onchain_tokenomics_analyzer.analyze_coin(base_coin)
                    tokenomics_score = analysis.get('overall_score', 50)
                    score_components['tokenomics'] = (tokenomics_score - 50) / 2
                    
                    if tokenomics_score > 70:
                        signals.append("⛓️ Strong tokenomics")
                except Exception:
                    pass
            
            # Volume score
            if volume_24h > 100_000_000:  # $100M+
                score_components['volume'] = 15
                signals.append(f"💰 High volume ${volume_24h/1e6:.0f}M")
            elif volume_24h > 10_000_000:  # $10M+
                score_components['volume'] = 10
            else:
                score_components['volume'] = 5
            
            # Price action
            if change_24h > 10:
                score_components['momentum'] = 15
                signals.append(f"🚀 Strong pump +{change_24h:.1f}%")
            elif change_24h > 5:
                score_components['momentum'] = 10
                signals.append(f"📈 Rising +{change_24h:.1f}%")
            elif change_24h < -10:
                score_components['momentum'] = -10
                signals.append(f"📉 Falling {change_24h:.1f}%")
            else:
                score_components['momentum'] = 0
            
            # Calculate final score
            total_score = sum(score_components.values())
            total_score = max(0, min(100, total_score + 50))  # Normalize to 0-100
            
            # Market cap estimate
            market_cap = price * volume_24h * 10  # Rough estimate
            
            return SearchResult(
                symbol=symbol,
                name=symbol.split('/')[0],
                price=price,
                change_24h=change_24h,
                volume_24h=volume_24h,
                market_cap=market_cap,
                score=total_score,
                signals=signals,
                kol_mentions=kol_mentions,
                sentiment_score=sentiment_score,
                tokenomics_score=tokenomics_score,
                trending_rank=None,
                metadata={
                    'score_components': score_components,
                    'analyzed_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            self.unified_logger.debug(f"Failed to analyze {symbol}: {e}")
            return None
    
    def search_by_kol_influence(self, min_mentions: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Search coins by KOL mentions"""
        try:
            if not kol_influence_tracker:
                return []
            
            trending = kol_influence_tracker.get_trending_coins(limit=100)
            filtered = [
                coin for coin in trending 
                if coin['total_mentions'] >= min_mentions
            ]
            
            return filtered[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"KOL search failed: {e}")
            return []
    
    def search_by_sentiment(self, min_score: float = 0.6, limit: int = 20) -> List[Dict[str, Any]]:
        """Search coins by positive sentiment"""
        try:
            results = []
            
            if real_market_data_fetcher:
                symbols = real_market_data_fetcher.get_top_symbols_by_volume(limit=100)
            else:
                return []
            
            for symbol in symbols:
                try:
                    base_coin = symbol.split('/')[0]
                    if sentiment_analysis_engine:
                        sentiment = sentiment_analysis_engine.get_coin_sentiment(base_coin)
                        score = sentiment.get('score', 0.5)
                        
                        if score >= min_score:
                            results.append({
                                'symbol': symbol,
                                'sentiment_score': score,
                                'sentiment_label': sentiment.get('label', 'NEUTRAL')
                            })
                except Exception:
                    continue
            
            results.sort(key=lambda x: x['sentiment_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Sentiment search failed: {e}")
            return []
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        try:
            return {
                'cache_size': len(self.search_cache),
                'cache_ttl': self.cache_ttl,
                'modules_available': {
                    'market_data': real_market_data_fetcher is not None,
                    'kol_tracker': kol_influence_tracker is not None,
                    'sentiment': sentiment_analysis_engine is not None,
                    'tokenomics': onchain_tokenomics_analyzer is not None
                },
                'last_update': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.unified_logger.error(f"Failed to get stats: {e}")
            return {}

# Global instance
advanced_search_engine = AdvancedSearchEngine()

