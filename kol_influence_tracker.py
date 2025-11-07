"""
GOD MODE 1000 - KOL INFLUENCE TRACKER
=====================================
Monitor and analyze Key Opinion Leaders (KOLs) and their impact on crypto markets
Track influential personalities, their predictions, and market reactions

FEATURES:
- Real-time KOL monitoring across multiple platforms
- Sentiment analysis of KOL posts and predictions
- Track accuracy of KOL predictions over time
- Measure market impact of KOL announcements
- Identify trending coins mentioned by influential KOLs
- Alert system for high-impact KOL activities
"""

import asyncio
import aiohttp
import requests
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import warnings
warnings.filterwarnings('ignore')

# Import unified components
try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from unified_config import unified_config
except ImportError:
    unified_config = None

try:
    from market_constants import market_constants
except ImportError:
    market_constants = None

try:
    from notification_system import notification_system, NotificationPriority
except ImportError:
    notification_system = None
    NotificationPriority = None

class KOLPlatform(Enum):
    """KOL platform types"""
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    REDDIT = "reddit"

class KOLInfluenceLevel(Enum):
    """KOL influence level"""
    MEGA = "mega"  # >1M followers
    MACRO = "macro"  # 100K-1M followers
    MICRO = "micro"  # 10K-100K followers
    NANO = "nano"  # <10K followers

class PredictionAccuracy(Enum):
    """Prediction accuracy rating"""
    EXCELLENT = "excellent"  # >80% accuracy
    GOOD = "good"  # 60-80% accuracy
    AVERAGE = "average"  # 40-60% accuracy
    POOR = "poor"  # <40% accuracy

@dataclass
class KOLProfile:
    """KOL profile data structure with enhanced credibility scoring"""
    kol_id: str
    name: str
    platform: KOLPlatform
    handle: str
    followers: int
    influence_level: KOLInfluenceLevel
    specialization: List[str]
    prediction_accuracy: float
    accuracy_rating: PredictionAccuracy
    total_predictions: int
    correct_predictions: int
    average_market_impact: float  # Average price change % after posts
    credibility_score: float  # 0-100 (composite score)
    last_active: datetime
    tracked_since: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    profile_url: str = ""
    bio: str = ""
    # ULTRA ENHANCED: Multi-horizon credibility metrics
    immediate_accuracy: float = 0.0  # Accuracy for <24h predictions (breaking news)
    short_term_accuracy: float = 0.0  # Accuracy for 1-7 day predictions (short swing trades)
    medium_term_accuracy: float = 0.0  # Accuracy for 7-30 day predictions (medium trends)
    long_term_accuracy: float = 0.0  # Accuracy for >30 day predictions (long-term holds)
    source_reliability: float = 0.8  # Base reliability (0-1)
    # Track prediction performance by time horizon
    immediate_predictions: int = 0
    short_term_predictions: int = 0
    medium_term_predictions: int = 0
    long_term_predictions: int = 0
    historical_consistency: float = 0.5  # Consistency over time (0-1)
    expertise_depth: float = 0.5  # Domain expertise level (0-1)
    bias_score: float = 0.5  # Lower = less biased (0-1)
    transparency_score: float = 0.5  # Data transparency (0-1)

class TimeHorizon(Enum):
    """Time horizon for predictions and signals"""
    IMMEDIATE = "immediate"  # <24 hours
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 7-30 days
    LONG_TERM = "long_term"  # >30 days

@dataclass
class KOLPost:
    """KOL post/announcement data structure with time horizon"""
    post_id: str
    kol_id: str
    platform: KOLPlatform
    content: str
    mentioned_coins: List[str]
    sentiment: str  # BULLISH, BEARISH, NEUTRAL
    sentiment_score: float
    confidence: float
    engagement: Dict[str, int]  # likes, retweets, comments
    timestamp: datetime
    post_url: str
    impact_measured: bool = False
    price_impact: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # NEW: Time horizon classification
    time_horizon: TimeHorizon = TimeHorizon.SHORT_TERM
    signal_strength: float = 0.5  # 0-1 based on credibility and confidence

@dataclass
class KOLPrediction:
    """KOL prediction tracking with enhanced time horizon"""
    prediction_id: str
    kol_id: str
    coin: str
    prediction_type: str  # PRICE_TARGET, BREAKOUT, DUMP, etc.
    prediction_details: str
    target_price: Optional[float]
    timeframe: str
    confidence: float
    timestamp: datetime
    outcome: Optional[str] = None  # SUCCESS, FAILED, PENDING
    actual_result: Optional[Dict[str, Any]] = None
    measured_at: Optional[datetime] = None
    # NEW: Enhanced classification
    time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM
    credibility_adjusted_confidence: float = 0.5  # Adjusted by KOL credibility

@dataclass
class KOLMarketImpact:
    """Measured market impact of KOL activity"""
    kol_id: str
    post_id: str
    coin: str
    price_before: float
    price_after_1h: float
    price_after_4h: float
    price_after_24h: float
    volume_change: float
    sentiment_change: float
    timestamp: datetime

class KOLInfluenceTracker:
    """
    Advanced KOL Influence Tracker - God Mode 1000
    
    Monitor and analyze Key Opinion Leaders (KOLs) impact on crypto markets
    Track predictions, measure accuracy, and alert on high-impact activities
    """
    
    def __init__(self):
        """Initialize KOL Influence Tracker"""
        try:
            self.unified_logger = unified_logging.get_logger("kol_tracker")
            
            # KOL database
            self.kol_profiles: Dict[str, KOLProfile] = {}
            self.kol_posts: List[KOLPost] = []
            self.kol_predictions: List[KOLPrediction] = []
            self.market_impacts: List[KOLMarketImpact] = []
            
            # Initialize with well-known crypto KOLs
            self._initialize_known_kols()

            # REMOVED: Demo/sample data - ONLY use real data from Twitter API
            # System will start with empty posts and fetch real data via monitor_kol_activity()
            # or add_kol_post() when real social media data is available

            # Monitoring settings
            self.monitoring_active = False
            self.check_interval = 300  # Check every 5 minutes
            self.max_history_size = 10000
            
            # Coin extraction patterns
            self.coin_patterns = [
                r'\$([A-Z]{3,10})',  # $BTC, $ETH
                r'\b([A-Z]{3,10})/USDT?\b',  # BTC/USDT
                r'\b(Bitcoin|Ethereum|Cardano|Solana|Polygon|Avalanche|Polkadot)\b'
            ]
            
            # Sentiment keywords
            self.bullish_keywords = [
                'bullish', 'moon', 'pump', 'buy', 'long', 'breakout', 
                'bullrun', 'accumulate', 'gem', 'rocket', '🚀', '📈',
                'undervalued', 'strong buy', 'all time high', 'ATH'
            ]
            
            self.bearish_keywords = [
                'bearish', 'dump', 'sell', 'short', 'breakdown', 
                'crash', 'exit', 'avoid', 'overvalued', '📉', '⚠️',
                'bubble', 'scam', 'rug pull', 'warning'
            ]
            
            self.unified_logger.info("KOL Influence Tracker initialized - God Mode 1000")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize KOL Tracker: {e}")
            raise
    
    def _initialize_known_kols(self):
        """Initialize database with well-known crypto KOLs"""
        try:
            # Top crypto influencers (real profiles)
            known_kols = [
                {
                    'kol_id': 'kol_1',
                    'name': 'Michael Saylor',
                    'platform': KOLPlatform.TWITTER,
                    'handle': '@saylor',
                    'followers': 3200000,
                    'specialization': ['BTC', 'Macro'],
                    'verified': True
                },
                {
                    'kol_id': 'kol_2',
                    'name': 'Vitalik Buterin',
                    'platform': KOLPlatform.TWITTER,
                    'handle': '@VitalikButerin',
                    'followers': 5100000,
                    'specialization': ['ETH', 'DeFi', 'Technology'],
                    'verified': True
                },
                {
                    'kol_id': 'kol_3',
                    'name': 'CZ (Changpeng Zhao)',
                    'platform': KOLPlatform.TWITTER,
                    'handle': '@cz_binance',
                    'followers': 8500000,
                    'specialization': ['BNB', 'Exchange', 'Market'],
                    'verified': True
                },
                {
                    'kol_id': 'kol_4',
                    'name': 'Cathie Wood',
                    'platform': KOLPlatform.TWITTER,
                    'handle': '@CathieDWood',
                    'followers': 1800000,
                    'specialization': ['BTC', 'Investment', 'Macro'],
                    'verified': True
                },
                {
                    'kol_id': 'kol_5',
                    'name': 'PlanB',
                    'platform': KOLPlatform.TWITTER,
                    'handle': '@100trillionUSD',
                    'followers': 2000000,
                    'specialization': ['BTC', 'S2F Model', 'Analysis'],
                    'verified': True
                }
            ]
            
            for kol_data in known_kols:
                # Determine influence level based on followers
                followers = kol_data['followers']
                if followers >= 1000000:
                    influence_level = KOLInfluenceLevel.MEGA
                elif followers >= 100000:
                    influence_level = KOLInfluenceLevel.MACRO
                elif followers >= 10000:
                    influence_level = KOLInfluenceLevel.MICRO
                else:
                    influence_level = KOLInfluenceLevel.NANO
                
                profile = KOLProfile(
                    kol_id=kol_data['kol_id'],
                    name=kol_data['name'],
                    platform=kol_data['platform'],
                    handle=kol_data['handle'],
                    followers=followers,
                    influence_level=influence_level,
                    specialization=kol_data['specialization'],
                    prediction_accuracy=0.0,
                    accuracy_rating=PredictionAccuracy.AVERAGE,
                    total_predictions=0,
                    correct_predictions=0,
                    average_market_impact=0.0,
                    credibility_score=75.0,  # Default credibility
                    last_active=datetime.now(timezone.utc),
                    verified=kol_data['verified']
                )
                
                self.kol_profiles[profile.kol_id] = profile
            
            self.unified_logger.info(f"Initialized {len(self.kol_profiles)} known KOLs")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize known KOLs: {e}")
    # DELETED: _add_sample_activity_data() - DEMO/FAKE DATA REMOVED
    # System now requires REAL data from Twitter API or other social media sources
    # Use monitor_kol_activity() or add_kol_post() with actual API data only

    def add_kol_profile(self, profile: KOLProfile) -> bool:
        """Add new KOL profile to tracking"""
        try:
            self.kol_profiles[profile.kol_id] = profile
            self.unified_logger.info(f"Added KOL profile: {profile.name}")
            return True
        except Exception as e:
            self.unified_logger.error(f"Failed to add KOL profile: {e}")
            return False
    
    def track_kol_post(self, post: KOLPost) -> bool:
        """Track new KOL post and analyze impact"""
        try:
            # Extract mentioned coins
            mentioned_coins = self._extract_coins(post.content)
            post.mentioned_coins = mentioned_coins
            
            # Analyze sentiment
            sentiment_result = self._analyze_sentiment(post.content)
            post.sentiment = sentiment_result['sentiment']
            post.sentiment_score = sentiment_result['score']
            post.confidence = sentiment_result['confidence']
            
            # Store post
            self.kol_posts.append(post)
            
            # Trim history if needed
            if len(self.kol_posts) > self.max_history_size:
                self.kol_posts = self.kol_posts[-self.max_history_size:]
            
            # Send alert for high-impact KOLs
            if post.kol_id in self.kol_profiles:
                kol = self.kol_profiles[post.kol_id]
                if kol.influence_level in [KOLInfluenceLevel.MEGA, KOLInfluenceLevel.MACRO]:
                    if mentioned_coins and post.sentiment in ['BULLISH', 'BEARISH']:
                        self._send_kol_alert(kol, post)
            
            self.unified_logger.info(f"Tracked post from {post.kol_id}: {len(mentioned_coins)} coins mentioned")
            return True
            
        except Exception as e:
            self.unified_logger.error(f"Failed to track KOL post: {e}")
            return False
    
    def _extract_coins(self, text: str) -> List[str]:
        """Extract mentioned cryptocurrency symbols from text"""
        try:
            coins = set()
            
            # Apply all coin extraction patterns
            for pattern in self.coin_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    coin = match.upper()
                    # Map common names to symbols
                    coin_mapping = {
                        'BITCOIN': 'BTC',
                        'ETHEREUM': 'ETH',
                        'CARDANO': 'ADA',
                        'SOLANA': 'SOL',
                        'POLYGON': 'MATIC',
                        'AVALANCHE': 'AVAX',
                        'POLKADOT': 'DOT'
                    }
                    coin = coin_mapping.get(coin, coin)
                    if len(coin) >= 3 and len(coin) <= 10:
                        coins.add(coin)
            
            return list(coins)
            
        except Exception as e:
            self.unified_logger.error(f"Failed to extract coins: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of KOL post"""
        try:
            text_lower = text.lower()
            
            # Count bullish and bearish keywords
            bullish_count = sum(1 for keyword in self.bullish_keywords if keyword.lower() in text_lower)
            bearish_count = sum(1 for keyword in self.bearish_keywords if keyword.lower() in text_lower)
            
            total_keywords = bullish_count + bearish_count
            
            if total_keywords == 0:
                return {
                    'sentiment': 'NEUTRAL',
                    'score': 0.5,
                    'confidence': 0.3
                }
            
            # Calculate sentiment score (0 = bearish, 1 = bullish)
            sentiment_score = bullish_count / total_keywords if total_keywords > 0 else 0.5
            confidence = min(total_keywords / 10, 0.95)  # Max 95% confidence
            
            # Determine sentiment label
            if sentiment_score >= 0.6:
                sentiment = 'BULLISH'
            elif sentiment_score <= 0.4:
                sentiment = 'BEARISH'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'confidence': confidence
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to analyze sentiment: {e}")
            return {'sentiment': 'NEUTRAL', 'score': 0.5, 'confidence': 0.3}
    
    def _send_kol_alert(self, kol: KOLProfile, post: KOLPost):
        """Send alert for high-impact KOL activity"""
        try:
            if notification_system and NotificationPriority:
                alert_message = (
                    f"🎯 KOL Alert: {kol.name} ({kol.handle})\n"
                    f"Sentiment: {post.sentiment}\n"
                    f"Coins: {', '.join(post.mentioned_coins)}\n"
                    f"Credibility: {kol.credibility_score:.0f}/100"
                )
                
                notification_system.send_notification(
                    title="KOL Market Signal",
                    message=alert_message,
                    priority=NotificationPriority.HIGH
                )
        except Exception as e:
            self.unified_logger.error(f"Failed to send KOL alert: {e}")
    
    def add_prediction(self, prediction: KOLPrediction) -> bool:
        """Add KOL prediction for tracking"""
        try:
            self.kol_predictions.append(prediction)
            self.unified_logger.info(f"Added prediction from {prediction.kol_id} for {prediction.coin}")
            return True
        except Exception as e:
            self.unified_logger.error(f"Failed to add prediction: {e}")
            return False
    
    def update_prediction_outcome(self, prediction_id: str, outcome: str, actual_result: Dict[str, Any]) -> bool:
        """Update prediction outcome after measurement"""
        try:
            for prediction in self.kol_predictions:
                if prediction.prediction_id == prediction_id:
                    prediction.outcome = outcome
                    prediction.actual_result = actual_result
                    prediction.measured_at = datetime.now(timezone.utc)
                    
                    # Update KOL stats
                    if prediction.kol_id in self.kol_profiles:
                        kol = self.kol_profiles[prediction.kol_id]
                        kol.total_predictions += 1
                        if outcome == 'SUCCESS':
                            kol.correct_predictions += 1
                        
                        # Recalculate accuracy
                        if kol.total_predictions > 0:
                            kol.prediction_accuracy = kol.correct_predictions / kol.total_predictions
                            
                            # Update accuracy rating
                            if kol.prediction_accuracy >= 0.8:
                                kol.accuracy_rating = PredictionAccuracy.EXCELLENT
                            elif kol.prediction_accuracy >= 0.6:
                                kol.accuracy_rating = PredictionAccuracy.GOOD
                            elif kol.prediction_accuracy >= 0.4:
                                kol.accuracy_rating = PredictionAccuracy.AVERAGE
                            else:
                                kol.accuracy_rating = PredictionAccuracy.POOR
                            
                            # Update credibility score
                            kol.credibility_score = min(95, kol.prediction_accuracy * 100 + 15)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.unified_logger.error(f"Failed to update prediction outcome: {e}")
            return False
    
    def get_kol_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top KOLs ranked by credibility and accuracy"""
        try:
            rankings = []
            
            for kol in self.kol_profiles.values():
                rankings.append({
                    'name': kol.name,
                    'handle': kol.handle,
                    'platform': kol.platform.value,
                    'followers': kol.followers,
                    'influence_level': kol.influence_level.value,
                    'credibility_score': kol.credibility_score,
                    'prediction_accuracy': kol.prediction_accuracy * 100,
                    'accuracy_rating': kol.accuracy_rating.value,
                    'total_predictions': kol.total_predictions,
                    'specialization': kol.specialization,
                    'verified': kol.verified
                })
            
            # Sort by credibility score
            rankings.sort(key=lambda x: x['credibility_score'], reverse=True)
            
            return rankings[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get KOL rankings: {e}")
            return []
    
    def get_recent_kol_activity(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent KOL activity"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            recent_posts = [
                post for post in self.kol_posts
                if post.timestamp >= cutoff_time
            ]
            
            # Sort by timestamp (most recent first)
            recent_posts.sort(key=lambda x: x.timestamp, reverse=True)
            
            activity = []
            for post in recent_posts[:limit]:
                kol = self.kol_profiles.get(post.kol_id)
                if kol:
                    activity.append({
                        'kol_name': kol.name,
                        'kol_handle': kol.handle,
                        'platform': post.platform.value,
                        'content': post.content[:200],  # Truncate long posts
                        'mentioned_coins': post.mentioned_coins,
                        'sentiment': post.sentiment,
                        'sentiment_score': post.sentiment_score,
                        'confidence': post.confidence,
                        'credibility_score': kol.credibility_score,
                        'timestamp': post.timestamp.isoformat(),
                        'post_url': post.post_url
                    })
            
            return activity
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get recent KOL activity: {e}")
            return []
    
    def get_coin_kol_sentiment(self, coin: str) -> Dict[str, Any]:
        """Get aggregated KOL sentiment for a specific coin"""
        try:
            # Get recent posts mentioning this coin
            recent_posts = [
                post for post in self.kol_posts
                if coin in post.mentioned_coins
                and (datetime.now(timezone.utc) - post.timestamp).days < 7
            ]
            
            if not recent_posts:
                return {
                    'coin': coin,
                    'overall_sentiment': 'NEUTRAL',
                    'sentiment_score': 0.5,
                    'confidence': 0.0,
                    'kol_count': 0,
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'neutral_count': 0
                }
            
            # Calculate weighted sentiment (weighted by KOL credibility)
            weighted_sentiment_sum = 0
            total_weight = 0
            bullish_count = 0
            bearish_count = 0
            neutral_count = 0
            
            for post in recent_posts:
                kol = self.kol_profiles.get(post.kol_id)
                if kol:
                    weight = kol.credibility_score / 100
                    weighted_sentiment_sum += post.sentiment_score * weight
                    total_weight += weight
                    
                    if post.sentiment == 'BULLISH':
                        bullish_count += 1
                    elif post.sentiment == 'BEARISH':
                        bearish_count += 1
                    else:
                        neutral_count += 1
            
            overall_sentiment_score = weighted_sentiment_sum / total_weight if total_weight > 0 else 0.5
            
            # Determine overall sentiment
            if overall_sentiment_score >= 0.6:
                overall_sentiment = 'BULLISH'
            elif overall_sentiment_score <= 0.4:
                overall_sentiment = 'BEARISH'
            else:
                overall_sentiment = 'NEUTRAL'
            
            # Calculate confidence based on number of KOLs and agreement
            kol_count = len(set(post.kol_id for post in recent_posts))
            agreement = max(bullish_count, bearish_count, neutral_count) / len(recent_posts)
            confidence = min(0.95, (kol_count / 10) * agreement)
            
            return {
                'coin': coin,
                'overall_sentiment': overall_sentiment,
                'sentiment_score': overall_sentiment_score,
                'confidence': confidence,
                'kol_count': kol_count,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'neutral_count': neutral_count,
                'recent_posts': len(recent_posts)
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get coin KOL sentiment: {e}")
            return {
                'coin': coin,
                'overall_sentiment': 'NEUTRAL',
                'sentiment_score': 0.5,
                'confidence': 0.0,
                'kol_count': 0
            }
    
    def get_trending_coins_from_kols(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending coins based on KOL mentions"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            recent_posts = [
                post for post in self.kol_posts
                if post.timestamp >= cutoff_time
            ]
            
            # Count coin mentions with credibility weighting
            coin_scores = {}
            
            for post in recent_posts:
                kol = self.kol_profiles.get(post.kol_id)
                if kol:
                    weight = kol.credibility_score / 100
                    for coin in post.mentioned_coins:
                        if coin not in coin_scores:
                            coin_scores[coin] = {
                                'mention_count': 0,
                                'weighted_score': 0,
                                'bullish_mentions': 0,
                                'bearish_mentions': 0
                            }
                        
                        coin_scores[coin]['mention_count'] += 1
                        coin_scores[coin]['weighted_score'] += weight
                        
                        if post.sentiment == 'BULLISH':
                            coin_scores[coin]['bullish_mentions'] += 1
                        elif post.sentiment == 'BEARISH':
                            coin_scores[coin]['bearish_mentions'] += 1
            
            # Convert to list and sort
            trending = []
            for coin, scores in coin_scores.items():
                trending.append({
                    'coin': coin,
                    'mention_count': scores['mention_count'],
                    'weighted_score': scores['weighted_score'],
                    'bullish_mentions': scores['bullish_mentions'],
                    'bearish_mentions': scores['bearish_mentions'],
                    'net_sentiment': scores['bullish_mentions'] - scores['bearish_mentions']
                })
            
            # Sort by weighted score
            trending.sort(key=lambda x: x['weighted_score'], reverse=True)
            
            return trending[:limit]
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get trending coins: {e}")
            return []
    
    def get_tracker_stats(self) -> Dict[str, Any]:
        """Get KOL tracker statistics"""
        try:
            return {
                'total_kols': len(self.kol_profiles),
                'verified_kols': sum(1 for kol in self.kol_profiles.values() if kol.verified),
                'mega_influencers': sum(1 for kol in self.kol_profiles.values() if kol.influence_level == KOLInfluenceLevel.MEGA),
                'macro_influencers': sum(1 for kol in self.kol_profiles.values() if kol.influence_level == KOLInfluenceLevel.MACRO),
                'total_posts_tracked': len(self.kol_posts),
                'total_predictions': len(self.kol_predictions),
                'pending_predictions': sum(1 for p in self.kol_predictions if p.outcome is None),
                'successful_predictions': sum(1 for p in self.kol_predictions if p.outcome == 'SUCCESS'),
                'monitoring_active': self.monitoring_active,
                'last_update': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.unified_logger.error(f"Failed to get tracker stats: {e}")
            return {}

# Create global instance
kol_influence_tracker = KOLInfluenceTracker()

