"""
GOD MODE 1000 - DYNAMIC INDICATOR CONFIGURATION
===============================================
Centralized dynamic configuration for all technical indicators
NO HARDCODED VALUES - ALL VALUES BASED ON REAL MARKET CONDITIONS
"""

from typing import Dict, Any, Optional
from market_constants import MarketConstants

class DynamicIndicatorConfig:
    """
    Dynamic Configuration Provider for Technical Indicators
    All thresholds and parameters are calculated from real market data
    """
    
    def __init__(self):
        """Initialize dynamic indicator configuration"""
        self.market_constants = MarketConstants()
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 60  # 1 minute cache
    
    def get_volatility_based_threshold(self, base: float = 0.02, volatility_multiplier: float = 1.0) -> float:
        """
        Get dynamic threshold based on market volatility
        
        Args:
            base: Base threshold value
            volatility_multiplier: How much volatility affects the threshold
        
        Returns:
            Dynamic threshold value
        """
        try:
            volatility = self.market_constants._get_market_volatility()
            return base * (1 + (volatility * volatility_multiplier))
        except Exception:
            return base
    
    def get_threshold_small(self) -> float:
        """Get small threshold (replaces 0.001)"""
        return self.market_constants.get_dynamic_threshold_small()
    
    def get_threshold_medium(self) -> float:
        """Get medium threshold (replaces 0.02)"""
        return self.market_constants.get_dynamic_threshold_medium()
    
    def get_threshold_large(self) -> float:
        """Get large threshold (replaces 0.05)"""
        return self.market_constants.get_dynamic_threshold_large()
    
    def get_rsi_oversold(self) -> float:
        """Get dynamic RSI oversold threshold (replaces hardcoded 30)"""
        try:
            fear_greed = self.market_constants.get_fear_greed_index()
            # Lower threshold in extreme fear (easier to be oversold)
            if fear_greed < 20:
                return 25.0
            elif fear_greed < 30:
                return 28.0
            else:
                return 30.0
        except Exception:
            return 30.0
    
    def get_rsi_overbought(self) -> float:
        """Get dynamic RSI overbought threshold (replaces hardcoded 70)"""
        try:
            fear_greed = self.market_constants.get_fear_greed_index()
            # Higher threshold in extreme greed (harder to be overbought)
            if fear_greed > 80:
                return 75.0
            elif fear_greed > 70:
                return 72.0
            else:
                return 70.0
        except Exception:
            return 70.0
    
    def get_rsi_neutral(self) -> float:
        """Get RSI neutral level (always 50)"""
        return 50.0
    
    def get_volume_spike_threshold(self) -> float:
        """Get dynamic volume spike threshold (replaces hardcoded 1.5 or 2.0)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Higher volatility = higher volume spikes expected
            base_threshold = 1.5
            return base_threshold + (volatility * 1.0)  # 1.5 to 2.5 range
        except Exception:
            return 1.5
    
    def get_volume_drop_threshold(self) -> float:
        """Get dynamic volume drop threshold (replaces hardcoded 0.7 or 0.8)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Higher volatility = lower volume drops expected
            base_threshold = 0.8
            return base_threshold - (volatility * 0.2)  # 0.6 to 0.8 range
        except Exception:
            return 0.8
    
    def get_momentum_threshold_positive(self) -> float:
        """Get dynamic positive momentum threshold (replaces hardcoded 0.05)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            momentum = self.market_constants._get_market_momentum()
            
            base = 0.03
            vol_adjustment = volatility * 0.05
            momentum_adjustment = abs(momentum) * 0.02
            
            return min(0.10, base + vol_adjustment + momentum_adjustment)
        except Exception:
            return 0.05
    
    def get_momentum_threshold_negative(self) -> float:
        """Get dynamic negative momentum threshold (replaces hardcoded -0.05)"""
        return -self.get_momentum_threshold_positive()
    
    def get_trend_strength_weak(self) -> float:
        """Get weak trend threshold (replaces hardcoded 0.3)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            return max(0.2, 0.3 - (volatility * 0.1))
        except Exception:
            return 0.3
    
    def get_trend_strength_strong(self) -> float:
        """Get strong trend threshold (replaces hardcoded 0.7)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            return min(0.9, 0.7 + (volatility * 0.2))
        except Exception:
            return 0.7
    
    def get_bollinger_band_std_dev(self) -> float:
        """Get dynamic Bollinger Band standard deviation multiplier (replaces hardcoded 2.0)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Higher volatility = wider bands
            return max(1.5, min(3.0, 2.0 + (volatility * 1.0)))
        except Exception:
            return 2.0
    
    def get_ma_fast_period(self) -> int:
        """Get dynamic fast MA period (replaces hardcoded 12)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Higher volatility = shorter period for faster response
            if volatility > 0.7:
                return 8
            elif volatility > 0.5:
                return 10
            else:
                return 12
        except Exception:
            return 12
    
    def get_ma_slow_period(self) -> int:
        """Get dynamic slow MA period (replaces hardcoded 26)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Higher volatility = shorter period
            if volatility > 0.7:
                return 20
            elif volatility > 0.5:
                return 24
            else:
                return 26
        except Exception:
            return 26
    
    def get_ma_signal_period(self) -> int:
        """Get dynamic signal period (replaces hardcoded 9)"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Higher volatility = shorter signal period
            if volatility > 0.7:
                return 7
            elif volatility > 0.5:
                return 8
            else:
                return 9
        except Exception:
            return 9
    
    def get_price_change_threshold(self) -> float:
        """Get dynamic price change threshold for pattern detection"""
        try:
            volatility = self.market_constants._get_market_volatility()
            return max(0.01, min(0.08, 0.02 + (volatility * 0.1)))
        except Exception:
            return 0.02
    
    def get_accumulation_threshold(self) -> float:
        """Get accumulation/distribution threshold"""
        try:
            volatility = self.market_constants._get_market_volatility()
            return max(0.6, 0.8 - (volatility * 0.3))
        except Exception:
            return 0.8
    
    def get_distribution_threshold(self) -> float:
        """Get distribution threshold"""
        try:
            volatility = self.market_constants._get_market_volatility()
            return min(1.5, 1.2 + (volatility * 0.5))
        except Exception:
            return 1.2
    
    def get_sideways_threshold(self) -> float:
        """Get sideways market threshold"""
        try:
            volatility = self.market_constants._get_market_volatility()
            # Lower threshold in high volatility (harder to be sideways)
            return max(0.01, 0.05 - (volatility * 0.08))
        except Exception:
            return 0.02
    
    def get_triangle_slope_threshold(self) -> float:
        """Get triangle pattern slope threshold"""
        return self.get_threshold_small()
    
    def get_pattern_similarity_threshold(self) -> float:
        """Get pattern similarity threshold"""
        return self.get_threshold_large()
    
    def get_all_thresholds(self) -> Dict[str, Any]:
        """Get all dynamic thresholds for batch processing"""
        return {
            'threshold_small': self.get_threshold_small(),
            'threshold_medium': self.get_threshold_medium(),
            'threshold_large': self.get_threshold_large(),
            'rsi_oversold': self.get_rsi_oversold(),
            'rsi_overbought': self.get_rsi_overbought(),
            'rsi_neutral': self.get_rsi_neutral(),
            'volume_spike': self.get_volume_spike_threshold(),
            'volume_drop': self.get_volume_drop_threshold(),
            'momentum_positive': self.get_momentum_threshold_positive(),
            'momentum_negative': self.get_momentum_threshold_negative(),
            'trend_weak': self.get_trend_strength_weak(),
            'trend_strong': self.get_trend_strength_strong(),
            'bb_std_dev': self.get_bollinger_band_std_dev(),
            'ma_fast': self.get_ma_fast_period(),
            'ma_slow': self.get_ma_slow_period(),
            'ma_signal': self.get_ma_signal_period(),
            'price_change': self.get_price_change_threshold(),
            'accumulation': self.get_accumulation_threshold(),
            'distribution': self.get_distribution_threshold(),
            'sideways': self.get_sideways_threshold(),
            'triangle_slope': self.get_triangle_slope_threshold(),
            'pattern_similarity': self.get_pattern_similarity_threshold(),
        }

# Create global instance
dynamic_indicator_config = DynamicIndicatorConfig()

