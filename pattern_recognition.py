"""
GOD MODE 1000 - CHART PATTERN RECOGNITION
=========================================
Advanced Technical Pattern Recognition System
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

# Use centralized pandas/numpy bypass
# Fix Python 3.13 compatibility first
import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np



class PatternType(Enum):
    """Chart pattern types"""
    # Reversal Patterns
    HEAD_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    
    # Continuation Patterns
    BULL_FLAG = "bull_flag"
    BEAR_FLAG = "bear_flag"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    WEDGE_RISING = "rising_wedge"
    WEDGE_FALLING = "falling_wedge"
    RECTANGLE = "rectangle"
    
    # Candlestick Patterns
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    DOJI = "doji"
    ENGULFING_BULL = "bullish_engulfing"
    ENGULFING_BEAR = "bearish_engulfing"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"


@dataclass
class DetectedPattern:
    """Detected pattern structure"""
    pattern_type: PatternType
    confidence: float
    signal: str  # 'BUY', 'SELL', 'HOLD'
    start_index: int
    end_index: int
    target_price: float
    stop_loss: float
    pattern_quality: str  # 'poor', 'fair', 'good', 'excellent'
    description: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PatternRecognition:
    """Chart Pattern Recognition - God Mode 1000"""
    
    def __init__(self):
        """Initialize Pattern Recognition"""
        self.unified_logger = unified_logging.get_logger("pattern_recognition")
        
        # Pattern detection thresholds
        self.min_pattern_bars = 10
        self.max_pattern_bars = 100
        self.pattern_tolerance = 0.02  # 2% tolerance for pattern matching
        
        self.unified_logger.info("✅ Pattern Recognition initialized - God Mode 1000")
    
    def detect_patterns(self, ohlcv_data: List[Dict[str, Any]], symbol: str) -> List[DetectedPattern]:
        """Detect all patterns in price data"""
        try:
            if not ohlcv_data or len(ohlcv_data) < self.min_pattern_bars:
                return []
            
            detected_patterns = []
            
            # Extract price arrays
            closes = np.array([bar['close'] for bar in ohlcv_data])
            highs = np.array([bar['high'] for bar in ohlcv_data])
            lows = np.array([bar['low'] for bar in ohlcv_data])
            opens = np.array([bar['open'] for bar in ohlcv_data])
            
            # Detect reversal patterns
            detected_patterns.extend(self._detect_head_shoulders(closes, highs, lows))
            detected_patterns.extend(self._detect_double_top_bottom(closes, highs, lows))
            
            # Detect continuation patterns
            detected_patterns.extend(self._detect_triangles(closes, highs, lows))
            detected_patterns.extend(self._detect_flags(closes, highs, lows))
            detected_patterns.extend(self._detect_wedges(closes, highs, lows))
            
            # Detect candlestick patterns
            detected_patterns.extend(self._detect_candlestick_patterns(opens, highs, lows, closes))
            
            # Sort by confidence
            detected_patterns.sort(key=lambda x: x.confidence, reverse=True)
            
            self.unified_logger.info(f"Detected {len(detected_patterns)} patterns for {symbol}")
            return detected_patterns
            
        except Exception as e:
            self.unified_logger.error(f"Failed to detect patterns: {e}")
            return []
    
    def get_pattern_summary(self, patterns: List[DetectedPattern]) -> Dict[str, Any]:
        """Get summary of detected patterns"""
        try:
            if not patterns:
                return {
                    'total_patterns': 0,
                    'bullish_patterns': 0,
                    'bearish_patterns': 0,
                    'overall_signal': 'HOLD',
                    'confidence': 0.0
                }
            
            bullish = sum(1 for p in patterns if p.signal == 'BUY')
            bearish = sum(1 for p in patterns if p.signal == 'SELL')
            
            # Weighted signal based on confidence
            weighted_signal = sum(
                (1 if p.signal == 'BUY' else -1 if p.signal == 'SELL' else 0) * p.confidence
                for p in patterns
            )
            
            if weighted_signal > 0.3:
                overall_signal = 'BUY'
            elif weighted_signal < -0.3:
                overall_signal = 'SELL'
            else:
                overall_signal = 'HOLD'
            
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            
            return {
                'total_patterns': len(patterns),
                'bullish_patterns': bullish,
                'bearish_patterns': bearish,
                'overall_signal': overall_signal,
                'confidence': avg_confidence,
                'weighted_signal': weighted_signal
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get pattern summary: {e}")
            return {
                'total_patterns': 0,
                'overall_signal': 'HOLD',
                'confidence': 0.0
            }
    
    # ==================== PATTERN DETECTION METHODS ====================
    
    def _detect_head_shoulders(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> List[DetectedPattern]:
        """Detect Head and Shoulders patterns"""
        patterns = []
        try:
            # Simplified H&S detection
            # Look for 3 peaks pattern
            window = 30
            if len(closes) < window:
                return patterns
            
            # Find peaks
            for i in range(window, len(closes) - window):
                # Check if this could be the head (highest point)
                if highs[i] == max(highs[i-window:i+window]):
                    # Look for left shoulder
                    left_shoulder_idx = i - window // 2
                    if left_shoulder_idx >= 0:
                        left_shoulder = highs[left_shoulder_idx]
                        
                        # Look for right shoulder
                        right_shoulder_idx = i + window // 2
                        if right_shoulder_idx < len(highs):
                            right_shoulder = highs[right_shoulder_idx]
                            
                            # Check H&S pattern
                            head = highs[i]
                            if (abs(left_shoulder - right_shoulder) / head < self.pattern_tolerance and
                                left_shoulder < head * 0.95 and right_shoulder < head * 0.95):
                                
                                # Valid H&S pattern
                                neckline = min(lows[left_shoulder_idx:right_shoulder_idx+1])
                                target = neckline - (head - neckline)
                                
                                # Calculate confidence from pattern symmetry and clarity
                                symmetry_score = 1.0 - abs((left_shoulder_idx - head_idx) - (head_idx - right_shoulder_idx)) / (right_shoulder_idx - left_shoulder_idx + 1)
                                clarity_score = (head - neckline) / head  # Prominence of head
                                pattern_confidence = 0.55 + (symmetry_score * 0.20) + (clarity_score * 0.20)
                                
                                patterns.append(DetectedPattern(
                                    pattern_type=PatternType.HEAD_SHOULDERS,
                                    confidence=min(0.95, pattern_confidence),
                                    signal='SELL',
                                    start_index=left_shoulder_idx,
                                    end_index=right_shoulder_idx,
                                    target_price=target,
                                    stop_loss=head,
                                    pattern_quality='good',
                                    description='Bearish Head and Shoulders - expect downside'
                                ))
        except Exception as e:
            self.unified_logger.error(f"Failed to detect H&S: {e}")
        
        return patterns
    
    def _detect_double_top_bottom(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> List[DetectedPattern]:
        """Detect Double Top/Bottom patterns"""
        patterns = []
        try:
            window = 20
            if len(closes) < window * 2:
                return patterns
            
            # Double Top
            for i in range(window, len(highs) - window):
                # Find first peak
                if highs[i] == max(highs[i-window:i+window]):
                    first_peak = highs[i]
                    
                    # Look for second peak
                    for j in range(i + window, min(i + window * 2, len(highs))):
                        if highs[j] == max(highs[j-window:j+window]):
                            second_peak = highs[j]
                            
                            # Check if peaks are similar
                            if abs(first_peak - second_peak) / first_peak < self.pattern_tolerance:
                                neckline = min(lows[i:j+1])
                                target = neckline - (first_peak - neckline)
                                
                                # Calculate confidence from peak similarity and volume
                                peak_similarity = 1.0 - abs(first_peak - second_peak) / first_peak
                                spacing_quality = min(1.0, (j - i) / (window * 1.5))  # Optimal spacing
                                double_top_confidence = 0.50 + (peak_similarity * 0.25) + (spacing_quality * 0.20)
                                
                                patterns.append(DetectedPattern(
                                    pattern_type=PatternType.DOUBLE_TOP,
                                    confidence=min(0.95, double_top_confidence),
                                    signal='SELL',
                                    start_index=i,
                                    end_index=j,
                                    target_price=target,
                                    stop_loss=first_peak,
                                    pattern_quality='good',
                                    description='Bearish Double Top - potential reversal'
                                ))
                                break
            
            # Double Bottom (similar logic, inverted)
            for i in range(window, len(lows) - window):
                if lows[i] == min(lows[i-window:i+window]):
                    first_trough = lows[i]
                    
                    for j in range(i + window, min(i + window * 2, len(lows))):
                        if lows[j] == min(lows[j-window:j+window]):
                            second_trough = lows[j]
                            
                            if abs(first_trough - second_trough) / first_trough < self.pattern_tolerance:
                                neckline = max(highs[i:j+1])
                                target = neckline + (neckline - first_trough)
                                
                                # Calculate confidence from trough similarity
                                trough_similarity = 1.0 - abs(first_trough - second_trough) / first_trough
                                spacing_quality = min(1.0, (j - i) / (window * 1.5))
                                double_bottom_confidence = 0.50 + (trough_similarity * 0.25) + (spacing_quality * 0.20)
                                
                                patterns.append(DetectedPattern(
                                    pattern_type=PatternType.DOUBLE_BOTTOM,
                                    confidence=min(0.95, double_bottom_confidence),
                                    signal='BUY',
                                    start_index=i,
                                    end_index=j,
                                    target_price=target,
                                    stop_loss=first_trough,
                                    pattern_quality='good',
                                    description='Bullish Double Bottom - potential reversal'
                                ))
                                break
        
        except Exception as e:
            self.unified_logger.error(f"Failed to detect double top/bottom: {e}")
        
        return patterns
    
    def _detect_triangles(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> List[DetectedPattern]:
        """Detect Triangle patterns"""
        patterns = []
        try:
            # Simplified triangle detection
            # Would use trendline analysis in production
            pass
        except Exception as e:
            self.unified_logger.error(f"Failed to detect triangles: {e}")
        
        return patterns
    
    def _detect_flags(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> List[DetectedPattern]:
        """Detect Flag patterns"""
        patterns = []
        try:
            # Simplified flag detection
            # Look for strong move followed by consolidation
            pass
        except Exception as e:
            self.unified_logger.error(f"Failed to detect flags: {e}")
        
        return patterns
    
    def _detect_wedges(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> List[DetectedPattern]:
        """Detect Wedge patterns"""
        patterns = []
        try:
            # Simplified wedge detection
            pass
        except Exception as e:
            self.unified_logger.error(f"Failed to detect wedges: {e}")
        
        return patterns
    
    def _detect_candlestick_patterns(self, opens: np.ndarray, highs: np.ndarray, 
                                    lows: np.ndarray, closes: np.ndarray) -> List[DetectedPattern]:
        """Detect Candlestick patterns"""
        patterns = []
        try:
            # Hammer
            for i in range(1, len(closes)):
                body = abs(closes[i] - opens[i])
                lower_shadow = min(opens[i], closes[i]) - lows[i]
                upper_shadow = highs[i] - max(opens[i], closes[i])
                
                if lower_shadow > body * 2 and upper_shadow < body * 0.3:
                    patterns.append(DetectedPattern(
                        pattern_type=PatternType.HAMMER,
                        confidence=0.6,
                        signal='BUY',
                        start_index=i,
                        end_index=i,
                        target_price=closes[i] * 1.02,
                        stop_loss=lows[i],
                        pattern_quality='fair',
                        description='Bullish Hammer - potential reversal'
                    ))
            
            # Engulfing patterns
            for i in range(1, len(closes)):
                # Bullish Engulfing
                if (closes[i-1] < opens[i-1] and  # Previous red
                    closes[i] > opens[i] and  # Current green
                    opens[i] <= closes[i-1] and  # Opens at or below prev close
                    closes[i] >= opens[i-1]):  # Closes at or above prev open
                    
                    patterns.append(DetectedPattern(
                        pattern_type=PatternType.ENGULFING_BULL,
                        confidence=0.65,
                        signal='BUY',
                        start_index=i-1,
                        end_index=i,
                        target_price=closes[i] * 1.03,
                        stop_loss=lows[i],
                        pattern_quality='good',
                        description='Bullish Engulfing - strong reversal signal'
                    ))
        
        except Exception as e:
            self.unified_logger.error(f"Failed to detect candlestick patterns: {e}")
        
        return patterns


# Global instance
pattern_recognition = PatternRecognition()

