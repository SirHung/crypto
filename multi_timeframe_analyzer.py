"""
GOD MODE 1000 - MULTI-TIMEFRAME ANALYZER
========================================
Advanced Multi-Timeframe Technical Analysis System
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from unified_technical_indicators import unified_technical_indicators
except ImportError:
    unified_technical_indicators = None

try:
    from real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None


class Timeframe(Enum):
    """Standard timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class TrendDirection(Enum):
    """Trend direction"""
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"


@dataclass
class TimeframeAnalysis:
    """Analysis for single timeframe"""
    timeframe: str
    trend: TrendDirection
    trend_strength: float
    support_levels: List[float]
    resistance_levels: List[float]
    key_indicators: Dict[str, Any]
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float


@dataclass
class MTFAnalysis:
    """Multi-Timeframe Analysis Result"""
    symbol: str
    timeframe_analyses: Dict[str, TimeframeAnalysis]
    overall_trend: TrendDirection
    overall_signal: str
    overall_confidence: float
    alignment_score: float  # How aligned are the timeframes
    best_entry_timeframe: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MultiTimeframeAnalyzer:
    """Multi-Timeframe Analyzer - God Mode 1000"""
    
    def __init__(self):
        """Initialize MTF Analyzer"""
        self.unified_logger = unified_logging.get_logger("mtf_analyzer")
        self.technical_indicators = unified_technical_indicators
        self.market_data_fetcher = real_market_data_fetcher
        
        # Standard timeframe sets
        self.default_timeframes = [
            Timeframe.M15.value,
            Timeframe.H1.value,
            Timeframe.H4.value,
            Timeframe.D1.value
        ]
        
        self.unified_logger.info("✅ Multi-Timeframe Analyzer initialized - God Mode 1000")
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: Optional[List[str]] = None) -> MTFAnalysis:
        """Perform multi-timeframe analysis"""
        try:
            if timeframes is None:
                timeframes = self.default_timeframes
            
            # Analyze each timeframe
            timeframe_analyses = {}
            for tf in timeframes:
                analysis = self._analyze_single_timeframe(symbol, tf)
                if analysis:
                    timeframe_analyses[tf] = analysis
            
            if not timeframe_analyses:
                return self._create_default_mtf_analysis(symbol)
            
            # Calculate overall metrics
            overall_trend = self._determine_overall_trend(timeframe_analyses)
            overall_signal = self._determine_overall_signal(timeframe_analyses)
            overall_confidence = self._calculate_overall_confidence(timeframe_analyses)
            alignment_score = self._calculate_alignment_score(timeframe_analyses)
            best_entry_tf = self._find_best_entry_timeframe(timeframe_analyses)
            
            return MTFAnalysis(
                symbol=symbol,
                timeframe_analyses=timeframe_analyses,
                overall_trend=overall_trend,
                overall_signal=overall_signal,
                overall_confidence=overall_confidence,
                alignment_score=alignment_score,
                best_entry_timeframe=best_entry_tf
            )
            
        except Exception as e:
            self.unified_logger.error(f"Failed to perform MTF analysis: {e}")
            return self._create_default_mtf_analysis(symbol)
    
    def get_trend_alignment(self, symbol: str) -> Dict[str, Any]:
        """Check trend alignment across timeframes"""
        try:
            mtf_analysis = self.analyze_multi_timeframe(symbol)
            
            # Count trend directions
            bullish_count = sum(1 for tf in mtf_analysis.timeframe_analyses.values() 
                              if 'bullish' in tf.trend.value.lower())
            bearish_count = sum(1 for tf in mtf_analysis.timeframe_analyses.values() 
                              if 'bearish' in tf.trend.value.lower())
            neutral_count = sum(1 for tf in mtf_analysis.timeframe_analyses.values() 
                              if tf.trend == TrendDirection.NEUTRAL)
            
            total = len(mtf_analysis.timeframe_analyses)
            
            # Determine alignment
            if bullish_count >= total * 0.75:
                alignment = 'strong_bullish'
                recommendation = 'All timeframes align bullish - strong buy opportunity'
            elif bearish_count >= total * 0.75:
                alignment = 'strong_bearish'
                recommendation = 'All timeframes align bearish - strong sell opportunity'
            elif bullish_count > bearish_count:
                alignment = 'weak_bullish'
                recommendation = 'Mixed signals with bullish bias - wait for confirmation'
            elif bearish_count > bullish_count:
                alignment = 'weak_bearish'
                recommendation = 'Mixed signals with bearish bias - wait for confirmation'
            else:
                alignment = 'conflicted'
                recommendation = 'Conflicting signals - stay out or wait for clarity'
            
            return {
                'alignment': alignment,
                'alignment_score': mtf_analysis.alignment_score,
                'recommendation': recommendation,
                'bullish_timeframes': bullish_count,
                'bearish_timeframes': bearish_count,
                'neutral_timeframes': neutral_count,
                'total_timeframes': total
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get trend alignment: {e}")
            return {
                'alignment': 'unknown',
                'alignment_score': 0.0,
                'recommendation': 'Analysis failed'
            }
    
    def find_confluence_zones(self, symbol: str) -> Dict[str, Any]:
        """Find price zones where multiple timeframes show S/R"""
        try:
            mtf_analysis = self.analyze_multi_timeframe(symbol)
            
            # Collect all support/resistance levels
            all_support = []
            all_resistance = []
            
            for tf_analysis in mtf_analysis.timeframe_analyses.values():
                all_support.extend(tf_analysis.support_levels)
                all_resistance.extend(tf_analysis.resistance_levels)
            
            # Find confluence zones (levels that appear in multiple timeframes)
            support_confluence = self._find_confluence_levels(all_support)
            resistance_confluence = self._find_confluence_levels(all_resistance)
            
            return {
                'support_zones': support_confluence,
                'resistance_zones': resistance_confluence,
                'strongest_support': support_confluence[0] if support_confluence else None,
                'strongest_resistance': resistance_confluence[0] if resistance_confluence else None
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to find confluence zones: {e}")
            return {
                'support_zones': [],
                'resistance_zones': []
            }
    
    def get_best_trading_timeframe(self, symbol: str, trading_style: str = 'swing') -> Dict[str, Any]:
        """Recommend best timeframe for trading style"""
        try:
            mtf_analysis = self.analyze_multi_timeframe(symbol)
            
            # Timeframe recommendations by style
            style_timeframes = {
                'scalping': [Timeframe.M1.value, Timeframe.M5.value],
                'day_trading': [Timeframe.M15.value, Timeframe.M30.value, Timeframe.H1.value],
                'swing': [Timeframe.H4.value, Timeframe.D1.value],
                'position': [Timeframe.D1.value, Timeframe.W1.value]
            }
            
            recommended_tfs = style_timeframes.get(trading_style, [Timeframe.H1.value])
            
            # Find best timeframe from analysis
            best_tf = mtf_analysis.best_entry_timeframe
            best_analysis = mtf_analysis.timeframe_analyses.get(best_tf)
            
            return {
                'recommended_timeframe': best_tf,
                'trading_style': trading_style,
                'signal': best_analysis.signal if best_analysis else 'HOLD',
                'confidence': best_analysis.confidence if best_analysis else 0.0,
                'alternative_timeframes': recommended_tfs
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get best trading timeframe: {e}")
            return {
                'recommended_timeframe': Timeframe.H1.value,
                'trading_style': trading_style,
                'signal': 'HOLD',
                'confidence': 0.0
            }
    
    # ==================== PRIVATE METHODS ====================
    
    def _analyze_single_timeframe(self, symbol: str, timeframe: str) -> Optional[TimeframeAnalysis]:
        """Analyze single timeframe"""
        try:
            # Get market data for timeframe
            # This is simplified - real implementation would fetch historical data
            market_data = {'price': 0, 'volume_24h': 0}
            if self.market_data_fetcher:
                data = self.market_data_fetcher.get_current_price(symbol)
                if data:
                    market_data = data
            
            if market_data.get('price', 0) == 0:
                return None
            
            # Determine trend (simplified)
            trend = TrendDirection.NEUTRAL
            trend_strength = 0.5
            
            # Get indicators
            key_indicators = {}
            if self.technical_indicators:
                # This would use real historical data
                pass
            
            # Simple signal determination
            signal = 'HOLD'
            confidence = 0.5
            
            return TimeframeAnalysis(
                timeframe=timeframe,
                trend=trend,
                trend_strength=trend_strength,
                support_levels=[market_data['price'] * 0.98, market_data['price'] * 0.95],
                resistance_levels=[market_data['price'] * 1.02, market_data['price'] * 1.05],
                key_indicators=key_indicators,
                signal=signal,
                confidence=confidence
            )
            
        except Exception as e:
            self.unified_logger.error(f"Failed to analyze timeframe {timeframe}: {e}")
            return None
    
    def _determine_overall_trend(self, analyses: Dict[str, TimeframeAnalysis]) -> TrendDirection:
        """Determine overall trend from all timeframes"""
        try:
            if not analyses:
                return TrendDirection.NEUTRAL
            
            # Weight longer timeframes more heavily
            weights = {
                Timeframe.M15.value: 1.0,
                Timeframe.H1.value: 1.5,
                Timeframe.H4.value: 2.0,
                Timeframe.D1.value: 3.0,
                Timeframe.W1.value: 4.0
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for tf, analysis in analyses.items():
                weight = weights.get(tf, 1.0)
                
                # Convert trend to score
                if analysis.trend == TrendDirection.STRONG_BULLISH:
                    score = 2.0
                elif analysis.trend == TrendDirection.BULLISH:
                    score = 1.0
                elif analysis.trend == TrendDirection.BEARISH:
                    score = -1.0
                elif analysis.trend == TrendDirection.STRONG_BEARISH:
                    score = -2.0
                else:
                    score = 0.0
                
                weighted_score += score * weight
                total_weight += weight
            
            avg_score = weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Convert back to trend
            if avg_score >= 1.5:
                return TrendDirection.STRONG_BULLISH
            elif avg_score >= 0.5:
                return TrendDirection.BULLISH
            elif avg_score <= -1.5:
                return TrendDirection.STRONG_BEARISH
            elif avg_score <= -0.5:
                return TrendDirection.BEARISH
            else:
                return TrendDirection.NEUTRAL
                
        except Exception as e:
            self.unified_logger.error(f"Failed to determine overall trend: {e}")
            return TrendDirection.NEUTRAL
    
    def _determine_overall_signal(self, analyses: Dict[str, TimeframeAnalysis]) -> str:
        """Determine overall signal"""
        try:
            buy_count = sum(1 for a in analyses.values() if a.signal == 'BUY')
            sell_count = sum(1 for a in analyses.values() if a.signal == 'SELL')
            
            if buy_count > sell_count and buy_count >= len(analyses) * 0.6:
                return 'BUY'
            elif sell_count > buy_count and sell_count >= len(analyses) * 0.6:
                return 'SELL'
            else:
                return 'HOLD'
        except:
            return 'HOLD'
    
    def _calculate_overall_confidence(self, analyses: Dict[str, TimeframeAnalysis]) -> float:
        """Calculate overall confidence"""
        try:
            if not analyses:
                return 0.0
            
            confidences = [a.confidence for a in analyses.values()]
            return sum(confidences) / len(confidences)
        except:
            return 0.0
    
    def _calculate_alignment_score(self, analyses: Dict[str, TimeframeAnalysis]) -> float:
        """Calculate how aligned the timeframes are"""
        try:
            if len(analyses) < 2:
                return 1.0
            
            signals = [a.signal for a in analyses.values()]
            
            # Calculate agreement
            buy_pct = signals.count('BUY') / len(signals)
            sell_pct = signals.count('SELL') / len(signals)
            
            # Alignment is highest when one signal dominates
            alignment = max(buy_pct, sell_pct)
            return alignment
        except:
            return 0.0
    
    def _find_best_entry_timeframe(self, analyses: Dict[str, TimeframeAnalysis]) -> str:
        """Find best timeframe for entry"""
        try:
            if not analyses:
                return Timeframe.H1.value
            
            # Find timeframe with highest confidence
            best_tf = max(analyses.items(), key=lambda x: x[1].confidence)
            return best_tf[0]
        except:
            return Timeframe.H1.value
    
    def _find_confluence_levels(self, levels: List[float], tolerance: float = 0.02) -> List[Dict[str, Any]]:
        """Find levels that cluster together (confluence)"""
        try:
            if not levels:
                return []
            
            # Sort levels
            sorted_levels = sorted(levels)
            
            # Find clusters
            clusters = []
            current_cluster = [sorted_levels[0]]
            
            for level in sorted_levels[1:]:
                if abs(level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                    current_cluster.append(level)
                else:
                    if len(current_cluster) >= 2:  # At least 2 levels in confluence
                        avg_level = sum(current_cluster) / len(current_cluster)
                        clusters.append({
                            'level': avg_level,
                            'strength': len(current_cluster),
                            'range': (min(current_cluster), max(current_cluster))
                        })
                    current_cluster = [level]
            
            # Check last cluster
            if len(current_cluster) >= 2:
                avg_level = sum(current_cluster) / len(current_cluster)
                clusters.append({
                    'level': avg_level,
                    'strength': len(current_cluster),
                    'range': (min(current_cluster), max(current_cluster))
                })
            
            # Sort by strength
            clusters.sort(key=lambda x: x['strength'], reverse=True)
            return clusters
            
        except Exception as e:
            self.unified_logger.error(f"Failed to find confluence levels: {e}")
            return []
    
    def _create_default_mtf_analysis(self, symbol: str) -> MTFAnalysis:
        """Create default MTF analysis when data unavailable"""
        return MTFAnalysis(
            symbol=symbol,
            timeframe_analyses={},
            overall_trend=TrendDirection.NEUTRAL,
            overall_signal='HOLD',
            overall_confidence=0.0,
            alignment_score=0.0,
            best_entry_timeframe=Timeframe.H1.value
        )


# Global instance
multi_timeframe_analyzer = MultiTimeframeAnalyzer()

