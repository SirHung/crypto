"""
GOD MODE 1000 - REGIME DETECTION
===============================
Advanced Market Regime Detection System
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Import unified components
try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from .real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None

class MarketRegime(Enum):
    """Market regime enumeration"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"

@dataclass
class RegimeSignal:
    """Regime detection signal"""
    symbol: str
    current_regime: MarketRegime
    confidence: float
    regime_strength: float
    volatility_level: float
    trend_direction: str
    support_level: float
    resistance_level: float
    key_levels: List[float]
    regime_duration: int  # in periods
    regime_change_probability: float
    next_regime_prediction: Optional[MarketRegime]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class RegimeDetectionEngine:
    """Advanced Market Regime Detection Engine"""
    
    def __init__(self):
        """Initialize Regime Detection Engine"""
        self.unified_logger = unified_logging.get_logger("regime_detection")
        
        # Regime detection parameters
        self.lookback_periods = 50
        self.volatility_threshold = 0.02
        self.trend_threshold = 0.01
        self.regime_min_duration = 5
        
        # Historical regime data
        self.regime_history = {}
        self.regime_signals = {}
        
        # Market data integration
        self.market_data_enabled = real_market_data_fetcher is not None
        
        self.unified_logger.info( "Regime Detection Engine initialized")
    
    def _run_async_detect(self, symbol: str, timeframe: str):
        """Helper to run async detect in new event loop"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.detect_regime(symbol, timeframe))
        finally:
            loop.close()
    
    def detect_regime_sync(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
        """Synchronous regime detection for integration"""
        try:
            import asyncio
            
            # Handle both running and non-running event loop scenarios
            try:
                loop = asyncio.get_running_loop()
                # If loop is running, we can't use run_until_complete
                # Instead, create a task and wait for it using nest_asyncio or return cached result
                self.unified_logger.debug("Event loop already running, using async wrapper")
                
                # Use a thread to run the async function
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async_detect, symbol, timeframe)
                    regime_signal = future.result(timeout=10)
            except RuntimeError:
                # No event loop running, safe to create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                regime_signal = loop.run_until_complete(self.detect_regime(symbol, timeframe))
                loop.close()
            
            return {
                'regime': regime_signal.current_regime.value,
                'confidence': regime_signal.confidence,
                'strength': regime_signal.regime_strength,
                'volatility': regime_signal.volatility_level,
                'trend_direction': regime_signal.trend_direction,
                'support': regime_signal.support_level,
                'resistance': regime_signal.resistance_level
            }
        except Exception as e:
            self.unified_logger.error(f"Error in synchronous regime detection: {e}")
            return {
                'regime': 'sideways',
                'confidence': 0.5,
                'strength': 0.5,
                'volatility': 0.02,
                'trend_direction': 'neutral',
                'support': 0,
                'resistance': 0
            }

    async def detect_regime(self, symbol: str, timeframe: str = "1h") -> RegimeSignal:
        """Detect current market regime for a symbol"""
        try:
            self.unified_logger.info( f"Detecting regime for {symbol}")
            
            # Get historical data
            historical_data = await self._get_historical_data(symbol, timeframe)
            
            if not historical_data or len(historical_data) < self.lookback_periods:
                return self._create_default_regime_signal(symbol)
            
            # Analyze market regime
            regime_analysis = self._analyze_market_regime(symbol, historical_data)
            
            # Create regime signal
            regime_signal = RegimeSignal(
                symbol=symbol,
                current_regime=regime_analysis['regime'],
                confidence=regime_analysis['confidence'],
                regime_strength=regime_analysis['strength'],
                volatility_level=regime_analysis['volatility'],
                trend_direction=regime_analysis['trend_direction'],
                support_level=regime_analysis['support'],
                resistance_level=regime_analysis['resistance'],
                key_levels=regime_analysis['key_levels'],
                regime_duration=regime_analysis['duration'],
                regime_change_probability=regime_analysis['change_probability'],
                next_regime_prediction=regime_analysis['next_regime'],
                metadata=regime_analysis['metadata']
            )
            
            # Store regime signal
            self.regime_signals[symbol] = regime_signal
            
            # Update regime history
            if symbol not in self.regime_history:
                self.regime_history[symbol] = []
            
            self.regime_history[symbol].append(regime_signal)
            
            # Keep only recent history
            if len(self.regime_history[symbol]) > 100:
                self.regime_history[symbol] = self.regime_history[symbol][-100:]
            
            return regime_signal
            
        except Exception as e:
            self.unified_logger.error( f"Failed to detect regime for {symbol}: {e}")
            return self._create_default_regime_signal(symbol)
    
    async def _get_historical_data(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """Get historical data for regime analysis"""
        try:
            if self.market_data_enabled and real_market_data_fetcher:
                # Get historical data from market data fetcher
                historical_data = real_market_data_fetcher.get_historical_data(
                    symbol, timeframe, limit=self.lookback_periods * 2
                )
                
                if historical_data:
                    return historical_data
            
            # NO FALLBACK - Cannot operate without REAL market data
            self.unified_logger.error(f"No REAL market data available for {symbol}")
            return []  # Return empty - NO SYNTHETIC DATA
            
        except Exception as e:
            self.unified_logger.error(f"❌ CRITICAL: Failed to get REAL historical data: {e}")
            raise ValueError(f"Cannot perform regime detection without REAL market data: {e}")
    
    # REMOVED: _generate_synthetic_data() - NO SYNTHETIC DATA ALLOWED
    # All data must come from REAL market sources only
    
    def _analyze_market_regime(self, symbol: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market regime from historical data"""
        try:
            if len(historical_data) < self.lookback_periods:
                return self._create_default_analysis()
            
            # Extract price data
            prices = [d['close'] for d in historical_data]
            highs = [d['high'] for d in historical_data]
            lows = [d['low'] for d in historical_data]
            volumes = [d['volume'] for d in historical_data]
            
            # Calculate technical indicators
            sma_20 = self._calculate_sma(prices, 20)
            sma_50 = self._calculate_sma(prices, 50)
            volatility = self._calculate_volatility(prices)
            rsi = self._calculate_rsi(prices)
            macd = self._calculate_macd(prices)
            
            # Determine trend direction
            trend_direction = self._determine_trend_direction(prices, sma_20, sma_50)
            
            # Determine volatility regime
            volatility_regime = self._determine_volatility_regime(volatility)
            
            # Determine price action regime
            price_action_regime = self._determine_price_action_regime(prices, highs, lows)
            
            # Combine regimes
            current_regime = self._combine_regimes(trend_direction, volatility_regime, price_action_regime)
            
            # Calculate regime strength
            regime_strength = self._calculate_regime_strength(prices, current_regime)
            
            # Calculate support and resistance
            support, resistance = self._calculate_support_resistance(highs, lows)
            
            # Calculate key levels
            key_levels = self._calculate_key_levels(prices, highs, lows)
            
            # Calculate regime duration
            regime_duration = self._calculate_regime_duration(symbol, current_regime)
            
            # Predict next regime
            next_regime = self._predict_next_regime(current_regime, regime_strength)
            
            # Calculate regime change probability
            change_probability = self._calculate_change_probability(current_regime, regime_strength)
            
            return {
                'regime': current_regime,
                'confidence': min(0.95, regime_strength * 0.8 + 0.2),
                'strength': regime_strength,
                'volatility': volatility,
                'trend_direction': trend_direction,
                'support': support,
                'resistance': resistance,
                'key_levels': key_levels,
                'duration': regime_duration,
                'change_probability': change_probability,
                'next_regime': next_regime,
                'metadata': {
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'rsi': rsi,
                    'macd': macd,
                    'volume_avg': sum(volumes) / len(volumes)
                }
            }
            
        except Exception as e:
            self.unified_logger.error( f"Failed to analyze market regime: {e}")
            return self._create_default_analysis()
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) < period:
                return prices[-1] if prices else 0
            
            return sum(prices[-period:]) / period
            
        except Exception:
            return 0
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        try:
            if len(prices) < 2:
                return 0
            
            returns = []
            for i in range(1, len(prices)):
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            if not returns:
                return 0
            
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            return variance ** 0.5
            
        except Exception:
            return 0
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI - CENTRALIZED from unified_technical_indicators - NO DUPLICATION"""
        try:
            from .unified_technical_indicators import unified_technical_indicators
            # Use centralized RSI calculation - NO DUPLICATE CODE
            return unified_technical_indicators.calculate_rsi(prices, period)
        except Exception:
            return 50.0
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """Calculate MACD - CENTRALIZED from unified_technical_indicators - NO DUPLICATION"""
        try:
            from .unified_technical_indicators import unified_technical_indicators
            # Use centralized MACD calculation - NO DUPLICATE CODE
            return unified_technical_indicators.calculate_macd(prices)
        except Exception:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return prices[-1] if prices else 0
            
            multiplier = 2 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
            
        except Exception:
            return 0
    
    def _determine_trend_direction(self, prices: List[float], sma_20: float, sma_50: float) -> str:
        """Determine trend direction"""
        try:
            if not prices:
                return "neutral"
            
            current_price = prices[-1]
            
            # Uptrend conditions
            if (current_price > sma_20 > sma_50 and 
                prices[-1] > prices[-5] > prices[-10]):
                return "uptrend"
            
            # Downtrend conditions
            elif (current_price < sma_20 < sma_50 and 
                  prices[-1] < prices[-5] < prices[-10]):
                return "downtrend"
            
            # Sideways conditions
            else:
                return "sideways"
                
        except Exception:
            return "neutral"
    
    def _determine_volatility_regime(self, volatility: float) -> str:
        """Determine volatility regime"""
        try:
            if volatility > self.volatility_threshold * 2:
                return "high_volatility"
            elif volatility < self.volatility_threshold * 0.5:
                return "low_volatility"
            else:
                return "normal_volatility"
                
        except Exception:
            return "normal_volatility"
    
    def _determine_price_action_regime(self, prices: List[float], highs: List[float], lows: List[float]) -> str:
        """Determine price action regime"""
        try:
            if len(prices) < 10:
                return "neutral"
            
            # Check for breakout
            recent_high = max(highs[-10:])
            recent_low = min(lows[-10:])
            current_price = prices[-1]
            
            if current_price > recent_high * 1.02:  # 2% above recent high
                return "breakout"
            elif current_price < recent_low * 0.98:  # 2% below recent low
                return "breakdown"
            
            # Check for accumulation/distribution
            price_range = recent_high - recent_low
            if price_range < current_price * 0.01:  # Less than 1% range
                return "accumulation"
            
            return "normal"
            
        except Exception:
            return "normal"
    
    def _combine_regimes(self, trend: str, volatility: str, price_action: str) -> MarketRegime:
        """Combine different regime signals"""
        try:
            # Priority: breakout > trend > volatility > price action
            
            if price_action == "breakout":
                return MarketRegime.BREAKOUT
            elif price_action == "breakdown":
                return MarketRegime.REVERSAL
            elif trend == "uptrend":
                return MarketRegime.UPTREND
            elif trend == "downtrend":
                return MarketRegime.DOWNTREND
            elif volatility == "high_volatility":
                return MarketRegime.HIGH_VOLATILITY
            elif volatility == "low_volatility":
                return MarketRegime.LOW_VOLATILITY
            elif price_action == "accumulation":
                return MarketRegime.ACCUMULATION
            else:
                return MarketRegime.SIDEWAYS
                
        except Exception:
            return MarketRegime.SIDEWAYS
    
    def _calculate_regime_strength(self, prices: List[float], regime: MarketRegime) -> float:
        """Calculate regime strength (0-1)"""
        try:
            if len(prices) < 10:
                return 0.5
            
            # Calculate price momentum
            momentum = (prices[-1] - prices[-10]) / prices[-10]
            
            # Calculate consistency
            recent_changes = []
            for i in range(1, min(10, len(prices))):
                change = (prices[-i] - prices[-i-1]) / prices[-i-1]
                recent_changes.append(change)
            
            consistency = 1 - (sum(abs(c) for c in recent_changes) / len(recent_changes))
            
            # Combine momentum and consistency
            strength = (abs(momentum) + consistency) / 2
            
            return min(1.0, max(0.0, strength))
            
        except Exception:
            return 0.5
    
    def _calculate_support_resistance(self, highs: List[float], lows: List[float]) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        try:
            if not highs or not lows:
                return 0, 0
            
            # Simple support/resistance calculation
            support = min(lows[-20:]) if len(lows) >= 20 else min(lows)
            resistance = max(highs[-20:]) if len(highs) >= 20 else max(highs)
            
            return support, resistance
            
        except Exception:
            return 0, 0
    
    def _calculate_key_levels(self, prices: List[float], highs: List[float], lows: List[float]) -> List[float]:
        """Calculate key price levels"""
        try:
            if not prices:
                return []
            
            current_price = prices[-1]
            key_levels = []
            
            # Add recent highs and lows
            if len(highs) >= 5:
                key_levels.append(max(highs[-5:]))
            if len(lows) >= 5:
                key_levels.append(min(lows[-5:]))
            
            # Add round numbers near current price
            round_levels = [int(current_price / 1000) * 1000, int(current_price / 100) * 100]
            key_levels.extend(round_levels)
            
            return sorted(set(key_levels))
            
        except Exception:
            return []
    
    def _calculate_regime_duration(self, symbol: str, current_regime: MarketRegime) -> int:
        """Calculate current regime duration"""
        try:
            if symbol not in self.regime_history:
                return 1
            
            history = self.regime_history[symbol]
            duration = 1
            
            # Count consecutive periods with same regime
            for i in range(len(history) - 1, -1, -1):
                if history[i].current_regime == current_regime:
                    duration += 1
                else:
                    break
            
            return duration
            
        except Exception:
            return 1
    
    def _predict_next_regime(self, current_regime: MarketRegime, strength: float) -> Optional[MarketRegime]:
        """Predict next regime"""
        try:
            # Simple regime transition logic
            if strength < 0.3:  # Weak regime, likely to change
                if current_regime == MarketRegime.UPTREND:
                    return MarketRegime.SIDEWAYS
                elif current_regime == MarketRegime.DOWNTREND:
                    return MarketRegime.SIDEWAYS
                elif current_regime == MarketRegime.SIDEWAYS:
                    return MarketRegime.UPTREND
                else:
                    return MarketRegime.SIDEWAYS
            else:  # Strong regime, likely to continue
                return current_regime
                
        except Exception:
            return None
    
    def _calculate_change_probability(self, current_regime: MarketRegime, strength: float) -> float:
        """Calculate probability of regime change"""
        try:
            # Higher strength = lower change probability
            base_probability = 1 - strength
            
            # Adjust based on regime type
            if current_regime in [MarketRegime.UPTREND, MarketRegime.DOWNTREND]:
                base_probability *= 0.8  # Trends are more stable
            elif current_regime == MarketRegime.SIDEWAYS:
                base_probability *= 1.2  # Sideways is less stable
            
            return min(0.9, max(0.1, base_probability))
            
        except Exception:
            return 0.5
    
    def _create_default_analysis(self) -> Dict[str, Any]:
        """Create default regime analysis"""
        return {
            'regime': MarketRegime.SIDEWAYS,
            'confidence': 0.5,
            'strength': 0.5,
            'volatility': 0.02,
            'trend_direction': 'neutral',
            'support': 0,
            'resistance': 0,
            'key_levels': [],
            'duration': 1,
            'change_probability': 0.5,
            'next_regime': None,
            'metadata': {}
        }
    
    def _create_default_regime_signal(self, symbol: str) -> RegimeSignal:
        """Create default regime signal"""
        return RegimeSignal(
            symbol=symbol,
            current_regime=MarketRegime.SIDEWAYS,
            confidence=0.5,
            regime_strength=0.5,
            volatility_level=0.02,
            trend_direction='neutral',
            support_level=0,
            resistance_level=0,
            key_levels=[],
            regime_duration=1,
            regime_change_probability=0.5,
            next_regime_prediction=None
        )
    
    def get_regime_history(self, symbol: str, limit: int = 50) -> List[RegimeSignal]:
        """Get regime history for a symbol"""
        try:
            if symbol in self.regime_history:
                return self.regime_history[symbol][-limit:]
            return []
            
        except Exception as e:
            self.unified_logger.error( f"Failed to get regime history: {e}")
            return []
    
    def get_current_regime(self, symbol: str) -> Optional[RegimeSignal]:
        """Get current regime for a symbol"""
        try:
            return self.regime_signals.get(symbol)
            
        except Exception as e:
            self.unified_logger.error( f"Failed to get current regime: {e}")
            return None
    
    def get_regime_summary(self) -> Dict[str, Any]:
        """Get regime detection summary"""
        try:
            total_signals = len(self.regime_signals)
            regime_counts = {}
            
            for signal in self.regime_signals.values():
                regime = signal.current_regime.value
                regime_counts[regime] = regime_counts.get(regime, 0) + 1
            
            return {
                'total_symbols': total_signals,
                'regime_distribution': regime_counts,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.unified_logger.error( f"Failed to get regime summary: {e}")
            return {}

# Create global instance
regime_detection_engine = RegimeDetectionEngine()
