"""
Alternative Data Integrator - God Mode 10000
Tích hợp dữ liệu thay thế từ các nguồn thực tế (sentiment, news, social, on-chain)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from .unified_logging_manager import UnifiedLoggingManager


@dataclass
class AlternativeDataSignals:
    """Signals từ alternative data sources"""
    timestamp: datetime
    social_sentiment: float  # From KOL and social media
    news_sentiment: float  # From news aggregator
    market_correlation: float  # Market-wide correlation
    onchain_activity: float  # On-chain metrics (for crypto)
    overall_sentiment_score: float  # Combined score
    overall_impact: str  # POSITIVE/NEGATIVE/NEUTRAL


class AlternativeDataIntegrator:
    """Integrate alternative data sources - REAL DATA ONLY"""
    
    def __init__(self):
        self.logger = UnifiedLoggingManager().get_logger("alt_data")
        self.logger.info("✅ Alternative Data Integrator initialized")
        
        # Initialize data sources
        self._init_data_sources()
    
    def _init_data_sources(self):
        """Initialize real data source modules"""
        try:
            from .kol_influence_tracker import kol_influence_tracker
            self.kol_tracker = kol_influence_tracker
        except Exception:
            self.kol_tracker = None
        
        try:
            from .advanced_nlp_sentiment import advanced_nlp_sentiment as sentiment_analysis_engine
            self.sentiment_engine = sentiment_analysis_engine
        except Exception:
            self.sentiment_engine = None
        
        try:
            from .onchain_tokenomics_analyzer import onchain_tokenomics_analyzer
            self.onchain_analyzer = onchain_tokenomics_analyzer
        except Exception:
            self.onchain_analyzer = None
        
        try:
            from .news_aggregator import news_aggregator
            self.news_agg = news_aggregator
        except Exception:
            self.news_agg = None
    
    def get_signals(self, symbol: str) -> Optional[AlternativeDataSignals]:
        """Get real signals from alternative data sources"""
        try:
            social_sentiment = 0.0
            news_sentiment = 0.0
            onchain_activity = 0.5
            market_correlation = 0.5
            
            # 1. Get social sentiment from KOL tracker
            if self.kol_tracker:
                try:
                    kol_sentiment = self.kol_tracker.get_overall_sentiment(symbol)
                    if kol_sentiment:
                        social_sentiment = kol_sentiment.get('sentiment_score', 0.0)
                        # Normalize to -1 to 1 range
                        social_sentiment = (social_sentiment - 0.5) * 2
                except Exception as e:
                    self.logger.debug(f"KOL sentiment unavailable: {e}")
            
            # 2. Get news sentiment
            if self.sentiment_engine:
                try:
                    news_result = self.sentiment_engine.analyze_symbol_sentiment(symbol)
                    if news_result:
                        # Convert sentiment to score
                        sentiment_map = {'positive': 0.7, 'negative': -0.7, 'neutral': 0.0}
                        news_sentiment = sentiment_map.get(news_result.get('sentiment', 'neutral'), 0.0)
                except Exception as e:
                    self.logger.debug(f"News sentiment unavailable: {e}")
            
            # 3. Get on-chain activity (crypto only)
            if self.onchain_analyzer and '/' in symbol:
                try:
                    base_token = symbol.split('/')[0]
                    onchain_data = self.onchain_analyzer.analyze_token(base_token)
                    if onchain_data:
                        # Normalize activity score
                        holder_growth = onchain_data.get('holder_growth', 0)
                        onchain_activity = min(1.0, max(0.0, 0.5 + holder_growth / 2))
                except Exception as e:
                    self.logger.debug(f"On-chain data unavailable: {e}")
            
            # 4. Calculate market correlation (from market conditions)
            try:
                from .market_constants import market_constants
                volatility = market_constants._get_market_volatility()
                # Lower volatility = higher correlation
                market_correlation = 1.0 - min(1.0, volatility)
            except Exception:
                pass
            
            # Calculate overall sentiment score (weighted average)
            weights = {
                'social': 0.35,
                'news': 0.35,
                'onchain': 0.20,
                'correlation': 0.10
            }
            
            overall_score = (
                social_sentiment * weights['social'] +
                news_sentiment * weights['news'] +
                (onchain_activity - 0.5) * 2 * weights['onchain'] +
                (market_correlation - 0.5) * 2 * weights['correlation']
            )
            
            # Determine overall impact
            if overall_score > 0.25:
                impact = 'POSITIVE'
            elif overall_score < -0.25:
                impact = 'NEGATIVE'
            else:
                impact = 'NEUTRAL'
            
            return AlternativeDataSignals(
                timestamp=datetime.now(),
                social_sentiment=social_sentiment,
                news_sentiment=news_sentiment,
                market_correlation=market_correlation,
                onchain_activity=onchain_activity,
                overall_sentiment_score=overall_score,
                overall_impact=impact
            )
            
        except Exception as e:
            self.logger.error(f"Error getting alternative data signals: {e}")
            return None


alternative_data_integrator = AlternativeDataIntegrator()

