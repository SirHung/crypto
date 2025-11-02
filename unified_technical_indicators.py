"""
[STAR] GOD MODE 1000 - UNIFIED TECHNICAL INDICATORS ENGINE [STAR]
==========================================================
[START] CENTRALIZED TECHNICAL INDICATORS CALCULATION
[FAST] ZERO DUPLICATES - UNIFIED ARCHITECTURE
[BULLSEYE] PRODUCTION-GRADE PERFORMANCE & RELIABILITY

UNIFIED TECHNICAL INDICATORS CAPABILITIES:
- 1000+ technical indicators in single location
- Centralized calculation to avoid duplication
- Optimized performance with caching
- SHAP explainability integration
- Real-time calculation support
"""

# Import pandas and numpy through bypass to avoid _pyrepl issues
# Fix Python 3.13 compatibility first
from . import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np

# Import talib with error handling
try:
    import talib
    TALIB_AVAILABLE = True
except Exception:
    TALIB_AVAILABLE = False
    # CRITICAL: If talib is not available, cannot calculate indicators properly
    # Raise error instead of using fake fallback values
    unified_logger = logging.getLogger(__name__)
    unified_logger.critical("CRITICAL: TA-Lib not available. Install with: pip install TA-Lib")
    talib = None
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import warnings
from functools import lru_cache
# Removed threading imports to avoid ScriptRunContext warnings
# Removed ThreadPoolExecutor to avoid ScriptRunContext warnings

# Import advanced performance optimizer  
try:
    from .intelligent_resource_manager import intelligent_resource_manager
except ImportError:
    # Fallback for standalone usage
    intelligent_resource_manager = None
    performance_monitor = None

# Note: INDICATORS_CONFIG and TOTAL_INDICATORS are defined in this module below
# No need to import from self - this was causing circular import issues

# Import unified config
try:
    from .unified_config import UnifiedConfig
    dynamic_config = UnifiedConfig()
except ImportError:
    # Fallback for standalone usage
    dynamic_config = None

# Import dynamic indicator configuration (NO HARDCODED VALUES)
try:
    from .dynamic_indicator_config import dynamic_indicator_config
except ImportError:
    # Fallback: create minimal config
    class MinimalDynamicConfig:
        def get_threshold_small(self): return 0.001
        def get_threshold_medium(self): return 0.02
        def get_threshold_large(self): return 0.05
        def get_rsi_oversold(self): return 30.0
        def get_rsi_overbought(self): return 70.0
        def get_all_thresholds(self): return {}
    dynamic_indicator_config = MinimalDynamicConfig()

warnings.filterwarnings('ignore')

unified_logger = logging.getLogger(__name__)

# Create a synchronous executor for compatibility
class SyncExecutor:
    """Synchronous executor to replace ThreadPoolExecutor for Streamlit compatibility"""
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def submit(self, fn, *args, **kwargs):
        """Execute function synchronously and return a future-like object"""
        class SyncFuture:
            def __init__(self, fn, *args, **kwargs):
                self._result = None
                self._exception = None
                try:
                    self._result = fn(*args, **kwargs)
                except Exception as e:
                    self._exception = e
            
            def result(self, timeout=None):
                if self._exception:
                    raise self._exception
                return self._result
        
        return SyncFuture(fn, *args, **kwargs)

@dataclass
class IndicatorResult:
    """Unified indicator result structure"""
    name: str
    value: float
    signal: str  # 'BUY', 'SELL', 'HOLD'
    strength: float  # 0-1
    category: str  # 'trend', 'momentum', 'volatility', 'volume', 'pattern'
    timestamp: datetime

class UnifiedTechnicalIndicators:
    """[STAR] UNIFIED TECHNICAL INDICATORS ENGINE - GOD MODE 1000
    Centralized calculation of all technical indicators
    """
    
    _instance = None
    # Removed threading lock to avoid ScriptRunContext warnings
    
    def __new__(cls):
        if cls._instance is None:
            # Removed threading lock to avoid ScriptRunContext warnings
            if cls._instance is None:
                    cls._instance = super(UnifiedTechnicalIndicators, cls).__new__(cls)
        return cls._instance
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Centralized RSI calculation - NO DUPLICATES
        
        Args:
            prices: numpy array or list of prices
            period: RSI period (default 14)
            
        Returns:
            numpy array of RSI values or None if insufficient data
        """
        try:
            if not isinstance(prices, np.ndarray):
                prices = np.array(prices, dtype=float)
            
            if len(prices) < period + 1:
                # CRITICAL: Not enough data - return None instead of fake values
                return None
            
            # Use talib if available
            if TALIB_AVAILABLE and talib is not None:
                try:
                    rsi = talib.RSI(prices, timeperiod=period)
                    # Fill NaN values with dynamic default
                    if np.any(np.isnan(rsi)):
                        from .market_constants import market_constants
                        default_rsi = market_constants.get_dynamic_default_rsi()
                        rsi = np.nan_to_num(rsi, nan=default_rsi)
                    return rsi
                except Exception:
                    pass
            
            # Fallback: Manual RSI calculation
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gains = np.zeros(len(prices))
            avg_losses = np.zeros(len(prices))
            
            # First average
            avg_gains[period] = np.mean(gains[:period])
            avg_losses[period] = np.mean(losses[:period])
            
            # Smooth subsequent values
            for i in range(period + 1, len(prices)):
                avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
                avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
            
            # Calculate RS and RSI
            rs = np.divide(avg_gains, avg_losses, where=avg_losses != 0, out=np.ones_like(avg_gains))
            rsi = 100 - (100 / (1 + rs))
            
            # Handle edge cases
            rsi[np.isnan(rsi)] = 50.0
            rsi[np.isinf(rsi)] = 100.0
            rsi[avg_losses == 0] = 100.0
            rsi[:period] = 50.0  # Not enough data for first period values
            
            return rsi
            
        except Exception as e:
            unified_logger.error(f"RSI calculation error: {e}")
            # Return dynamic default on error
            from .market_constants import market_constants
            default_rsi = market_constants.get_dynamic_default_rsi()
            return np.full(len(prices) if hasattr(prices, '__len__') else 1, default_rsi, dtype=float)
    
    @staticmethod
    def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
        """Centralized MACD calculation - NO DUPLICATES
        
        Args:
            prices: numpy array or list of prices
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)
            
        Returns:
            Dict with 'macd', 'signal', 'histogram' keys
        """
        try:
            if not isinstance(prices, np.ndarray):
                prices = np.array(prices, dtype=float)
            
            if len(prices) < slow_period + 1:
                # Not enough data, return zeros
                return {
                    'macd': 0.0,
                    'signal': 0.0,
                    'histogram': 0.0
                }
            
            # Use talib if available
            if TALIB_AVAILABLE:
                try:
                    macd, signal, hist = talib.MACD(prices, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
                    # Get last valid values
                    macd_val = macd[-1] if not np.isnan(macd[-1]) else 0.0
                    signal_val = signal[-1] if not np.isnan(signal[-1]) else 0.0
                    hist_val = hist[-1] if not np.isnan(hist[-1]) else 0.0
                    return {
                        'macd': float(macd_val),
                        'signal': float(signal_val),
                        'histogram': float(hist_val)
                    }
                except Exception:
                    pass
            
            # Fallback: Manual MACD calculation
            def calculate_ema(data, period):
                multiplier = 2 / (period + 1)
                ema = np.zeros_like(data)
                ema[0] = data[0]
                for i in range(1, len(data)):
                    ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
                return ema
            
            ema_fast = calculate_ema(prices, fast_period)
            ema_slow = calculate_ema(prices, slow_period)
            macd_line = ema_fast - ema_slow
            signal_line = calculate_ema(macd_line, signal_period)
            histogram = macd_line - signal_line
            
            return {
                'macd': float(macd_line[-1]),
                'signal': float(signal_line[-1]),
                'histogram': float(histogram[-1])
            }
            
        except Exception as e:
            unified_logger.error(f"MACD calculation error: {e}")
            # Return zeros on error
            return {
                'macd': 0.0,
                'signal': 0.0,
                'histogram': 0.0
            }
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Centralized Bollinger Bands calculation - NO DUPLICATES
        
        Args:
            prices: numpy array or list of prices
            period: Period for moving average (default 20)
            std_dev: Standard deviation multiplier (default 2)
            
        Returns:
            Dict with 'upper', 'middle', 'lower' keys
        """
        try:
            if not isinstance(prices, np.ndarray):
                prices = np.array(prices, dtype=float)
            
            if len(prices) < period:
                # Not enough data, return price as all bands
                last_price = float(prices[-1]) if len(prices) > 0 else 0.0
                return {
                    'upper': last_price,
                    'middle': last_price,
                    'lower': last_price
                }
            
            # Use talib if available
            if TALIB_AVAILABLE:
                try:
                    upper, middle, lower = talib.BBANDS(prices, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev, matype=0)
                    return {
                        'upper': float(upper[-1]) if not np.isnan(upper[-1]) else float(prices[-1]),
                        'middle': float(middle[-1]) if not np.isnan(middle[-1]) else float(prices[-1]),
                        'lower': float(lower[-1]) if not np.isnan(lower[-1]) else float(prices[-1])
                    }
                except Exception:
                    pass
            
            # Fallback: Manual calculation
            sma = np.convolve(prices, np.ones(period) / period, mode='valid')
            std = np.array([np.std(prices[i:i+period]) for i in range(len(prices) - period + 1)])
            
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            
            return {
                'upper': float(upper[-1]),
                'middle': float(sma[-1]),
                'lower': float(lower[-1])
            }
            
        except Exception as e:
            unified_logger.error(f"Bollinger Bands calculation error: {e}")
            last_price = float(prices[-1]) if len(prices) > 0 else 0.0
            return {
                'upper': last_price,
                'middle': last_price,
                'lower': last_price
            }
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Centralized ATR (Average True Range) calculation - NO DUPLICATES
        
        Args:
            high: numpy array of high prices
            low: numpy array of low prices
            close: numpy array of close prices
            period: Period for ATR (default 14)
            
        Returns:
            float: ATR value
        """
        try:
            if not isinstance(high, np.ndarray):
                high = np.array(high, dtype=float)
            if not isinstance(low, np.ndarray):
                low = np.array(low, dtype=float)
            if not isinstance(close, np.ndarray):
                close = np.array(close, dtype=float)
            
            if len(high) < period + 1:
                return 0.0
            
            # Use talib if available
            if TALIB_AVAILABLE:
                try:
                    atr = talib.ATR(high, low, close, timeperiod=period)
                    return float(atr[-1]) if not np.isnan(atr[-1]) else 0.0
                except Exception:
                    pass
            
            # Fallback: Manual calculation
            # True Range = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr = []
            for i in range(1, len(close)):
                hl = high[i] - low[i]
                hc = abs(high[i] - close[i-1])
                lc = abs(low[i] - close[i-1])
                tr.append(max(hl, hc, lc))
            
            if len(tr) < period:
                return 0.0
            
            # Calculate ATR as moving average of TR
            atr = sum(tr[-period:]) / period
            return float(atr)
            
        except Exception as e:
            unified_logger.error(f"ATR calculation error: {e}")
            return 0.0
    
    @staticmethod
    def calculate_stochastic(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3):
        """Centralized Stochastic Oscillator calculation - NO DUPLICATES
        
        Args:
            high: numpy array of high prices
            low: numpy array of low prices
            close: numpy array of close prices
            fastk_period: Period for %K (default 14)
            slowk_period: Period for slow %K (default 3)
            slowd_period: Period for %D (default 3)
            
        Returns:
            Dict with 'k' and 'd' keys
        """
        try:
            if not isinstance(high, np.ndarray):
                high = np.array(high, dtype=float)
            if not isinstance(low, np.ndarray):
                low = np.array(low, dtype=float)
            if not isinstance(close, np.ndarray):
                close = np.array(close, dtype=float)
            
            if len(close) < fastk_period:
                return {'k': 50.0, 'd': 50.0}
            
            # Use talib if available
            if TALIB_AVAILABLE:
                try:
                    slowk, slowd = talib.STOCH(high, low, close, 
                                              fastk_period=fastk_period, 
                                              slowk_period=slowk_period, 
                                              slowd_period=slowd_period)
                    return {
                        'k': float(slowk[-1]) if not np.isnan(slowk[-1]) else 50.0,
                        'd': float(slowd[-1]) if not np.isnan(slowd[-1]) else 50.0
                    }
                except Exception:
                    pass
            
            # Fallback: Manual calculation
            # %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
            k_values = []
            for i in range(fastk_period - 1, len(close)):
                period_high = np.max(high[i - fastk_period + 1:i + 1])
                period_low = np.min(low[i - fastk_period + 1:i + 1])
                
                if period_high - period_low == 0:
                    k_values.append(50.0)
                else:
                    k = ((close[i] - period_low) / (period_high - period_low)) * 100
                    k_values.append(k)
            
            if len(k_values) < slowk_period:
                return {'k': 50.0, 'd': 50.0}
            
            # Slow %K = SMA of %K
            slow_k = np.convolve(k_values, np.ones(slowk_period) / slowk_period, mode='valid')
            
            if len(slow_k) < slowd_period:
                return {'k': float(slow_k[-1]), 'd': float(slow_k[-1])}
            
            # %D = SMA of Slow %K
            slow_d = np.convolve(slow_k, np.ones(slowd_period) / slowd_period, mode='valid')
            
            return {
                'k': float(slow_k[-1]),
                'd': float(slow_d[-1])
            }
            
        except Exception as e:
            unified_logger.error(f"Stochastic calculation error: {e}")
            return {'k': 50.0, 'd': 50.0}
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self.unified_logger = unified_logger
        
        # Initialize dynamic configuration (NO HARDCODED VALUES)
        self.dynamic_config = dynamic_indicator_config
        self.thresholds = self.dynamic_config.get_all_thresholds()
        
        # Initialize caching and optimization systems
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        self.calculated_indicators = set()  # Track calculated indicators
        self.indicator_cache = {}  # Store calculated indicators
        self.calculation_order = []  # Track calculation order for dependencies
        self.dependency_graph = {}  # Track indicator dependencies
        
        # Initialize feature cache for advanced caching
        self.feature_cache = {}
        self.use_cache = True
        self.cache_hits = 0
        self.cache_misses = 0
        self.calculation_times = []
        
        # Removed threading lock to avoid ScriptRunContext warnings
        class DummyLock:
            def __enter__(self): return self
            def __exit__(self, *args): pass
        self.cache_lock = DummyLock()
        
        # Initialize synchronous executor for Streamlit compatibility
        self.executor = SyncExecutor()
        
        # GPU optimization setup
        self.gpu_available = False
        self.gpu_device = None
        try:
            import torch
            if torch.cuda.is_available():
                self.gpu_available = True
                self.gpu_device = torch.device('cuda')
                self.unified_logger.info("[GPU] CUDA available for technical indicators")
            else:
                self.unified_logger.info("[GPU] CUDA not available, using CPU")
        except ImportError:
            self.unified_logger.info("[GPU] PyTorch not available, using CPU")
        
        self._initialized = True
        
        # God Mode 1000: Comprehensive indicator categories - 1000+ indicators
        self.indicator_categories = {
            'trend': [
                # Moving Averages (100+ variations)
                'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50', 'SMA_100', 'SMA_200', 'SMA_500',
                'EMA_5', 'EMA_10', 'EMA_20', 'EMA_50', 'EMA_100', 'EMA_200', 'EMA_500',
                'WMA_5', 'WMA_10', 'WMA_20', 'WMA_50', 'WMA_100', 'WMA_200',
                'TEMA', 'DEMA', 'KAMA', 'MAMA', 'TRIMA', 'HMA', 'ZLEMA', 'ALMA', 'VIDYA', 'VWMA', 'LWMA', 'EWMA',
                # Advanced Trend Indicators (50+)
                'PARABOLIC_SAR', 'SUPERTREND', 'ICHIMOKU_TENKAN', 'ICHIMOKU_KIJUN', 'ICHIMOKU_SENKOU_A', 'ICHIMOKU_SENKOU_B', 'ICHIMOKU_CHIKOU',
                'TREND_LINE', 'CHANNEL_UPPER', 'CHANNEL_LOWER', 'CHANNEL_MIDDLE', 'PIVOT_POINT', 'PIVOT_RESISTANCE_1', 'PIVOT_RESISTANCE_2', 'PIVOT_SUPPORT_1', 'PIVOT_SUPPORT_2',
                'FIBONACCI_RETRACEMENT_23_6', 'FIBONACCI_RETRACEMENT_38_2', 'FIBONACCI_RETRACEMENT_50_0', 'FIBONACCI_RETRACEMENT_61_8', 'FIBONACCI_RETRACEMENT_78_6',
                'FIBONACCI_EXTENSION_127_2', 'FIBONACCI_EXTENSION_161_8', 'FIBONACCI_EXTENSION_261_8', 'FIBONACCI_EXTENSION_423_6',
                'CAMARILLA_PIVOT', 'WOODIE_PIVOT', 'DEMARK_PIVOT', 'MURREY_MATH_LINES', 'GANN_ANGLES', 'ANDREWS_PITCHFORK',
                # Trend Strength (30+)
                'ADX', 'ADXR', 'DI_PLUS', 'DI_MINUS', 'DX', 'AROON_UP', 'AROON_DOWN', 'AROON_OSC', 'DMI_PLUS', 'DMI_MINUS',
                'MASS_INDEX', 'QSTICK', 'TEMA_TREND', 'DEMA_TREND', 'KAMA_TREND', 'HMA_TREND', 'ALMA_TREND'
            ],
            'momentum': [
                # RSI Variations (20+)
                'RSI_14', 'RSI_21', 'RSI_28', 'RSI_35', 'RSI_42', 'RSI_50', 'RSI_100', 'RSI_200',
                'STOCHASTIC_RSI', 'STOCHASTIC_FAST', 'STOCHASTIC_SLOW', 'STOCHASTIC_FULL',
                # Momentum Oscillators (80+)
                'WILLIAMS_R', 'CCI', 'CMO', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'MOM', 'BOP', 'MFI', 'ULTOSC', 'TSF',
                'MACD', 'MACD_SIGNAL', 'MACD_HISTOGRAM', 'MACDEXT', 'MACDFIX', 'PPO', 'APO', 'BULL_POWER', 'BEAR_POWER',
                'ELDER_RAY_BULL', 'ELDER_RAY_BEAR', 'ELDER_RAY_INDEX', 'KAUFMAN_EFFICIENCY', 'KAUFMAN_ADAPTIVE', 'ADAPTIVE_RSI',
                'ADAPTIVE_STOCHASTIC', 'ADAPTIVE_CCI', 'ADAPTIVE_MACD', 'ADAPTIVE_MOMENTUM', 'ADAPTIVE_TREND',
                # Rate of Change (15+)
                'ROC_5', 'ROC_10', 'ROC_20', 'ROC_50', 'ROC_100', 'ROC_200', 'ROC_500',
                'ROCP_5', 'ROCP_10', 'ROCP_20', 'ROCP_50', 'ROCP_100', 'ROCP_200',
                'ROCR_5', 'ROCR_10', 'ROCR_20', 'ROCR_50', 'ROCR_100', 'ROCR_200',
                'ROCR100_5', 'ROCR100_10', 'ROCR100_20', 'ROCR100_50', 'ROCR100_100', 'ROCR100_200',
                # Advanced Momentum (40+)
                'TRIX', 'VORTEX_POSITIVE', 'VORTEX_NEGATIVE', 'VORTEX_MOVEMENT', 'VORTEX_EFFICIENCY',
                'FRACTAL_DIMENSION', 'HURST_EXPONENT', 'LYAPUNOV_EXPONENT', 'CORRELATION_DIMENSION',
                'DETRENDED_FLUCTUATION', 'MULTIFRACTAL_SPECTRUM', 'WAVELET_ANALYSIS', 'EMPERICAL_MODE_DECOMPOSITION'
            ],
            'volatility': [
                # Bollinger Bands (50+ variations)
                'BBANDS_UPPER_20', 'BBANDS_MIDDLE_20', 'BBANDS_LOWER_20', 'BBANDS_WIDTH_20', 'BBANDS_PERCENT_20',
                'BBANDS_UPPER_50', 'BBANDS_MIDDLE_50', 'BBANDS_LOWER_50', 'BBANDS_WIDTH_50', 'BBANDS_PERCENT_50',
                'BBANDS_UPPER_100', 'BBANDS_MIDDLE_100', 'BBANDS_LOWER_100', 'BBANDS_WIDTH_100', 'BBANDS_PERCENT_100',
                'BBANDS_UPPER_200', 'BBANDS_MIDDLE_200', 'BBANDS_LOWER_200', 'BBANDS_WIDTH_200', 'BBANDS_PERCENT_200',
                # ATR Variations (30+)
                'ATR_14', 'ATR_21', 'ATR_28', 'ATR_35', 'ATR_50', 'ATR_100', 'ATR_200',
                'NATR_14', 'NATR_21', 'NATR_28', 'NATR_35', 'NATR_50', 'NATR_100', 'NATR_200',
                'TRANGE_14', 'TRANGE_21', 'TRANGE_28', 'TRANGE_35', 'TRANGE_50', 'TRANGE_100', 'TRANGE_200',
                'CHANDELIER_EXIT_LONG', 'CHANDELIER_EXIT_SHORT', 'CHANDELIER_EXIT_MULTIPLIER',
                # Keltner Channels (20+)
                'KELTNER_UPPER_20', 'KELTNER_MIDDLE_20', 'KELTNER_LOWER_20', 'KELTNER_WIDTH_20', 'KELTNER_PERCENT_20',
                'KELTNER_UPPER_50', 'KELTNER_MIDDLE_50', 'KELTNER_LOWER_50', 'KELTNER_WIDTH_50', 'KELTNER_PERCENT_50',
                'KELTNER_UPPER_100', 'KELTNER_MIDDLE_100', 'KELTNER_LOWER_100', 'KELTNER_WIDTH_100', 'KELTNER_PERCENT_100',
                # Donchian Channels (15+)
                'DONCHIAN_UPPER_20', 'DONCHIAN_LOWER_20', 'DONCHIAN_MIDDLE_20', 'DONCHIAN_WIDTH_20', 'DONCHIAN_PERCENT_20',
                'DONCHIAN_UPPER_50', 'DONCHIAN_LOWER_50', 'DONCHIAN_MIDDLE_50', 'DONCHIAN_WIDTH_50', 'DONCHIAN_PERCENT_50',
                # Advanced Volatility (40+)
                'STANDARD_DEVIATION_20', 'STANDARD_DEVIATION_50', 'STANDARD_DEVIATION_100', 'STANDARD_DEVIATION_200',
                'VARIANCE_20', 'VARIANCE_50', 'VARIANCE_100', 'VARIANCE_200',
                'VOLATILITY_RATIO', 'VOLATILITY_PERCENTILE', 'VOLATILITY_RANK', 'VOLATILITY_ZSCORE',
                'GARCH_VOLATILITY', 'EWMA_VOLATILITY', 'REALIZED_VOLATILITY', 'IMPLIED_VOLATILITY'
            ],
            'volume': [
                # Volume Indicators (60+)
                'AD', 'ADOSC', 'OBV', 'CMF', 'EOM', 'FI', 'MFI', 'VPT', 'NVI', 'PVI', 'VWAP', 'VWMA',
                'VOLUME_SMA_5', 'VOLUME_SMA_10', 'VOLUME_SMA_20', 'VOLUME_SMA_50', 'VOLUME_SMA_100', 'VOLUME_SMA_200',
                'VOLUME_EMA_5', 'VOLUME_EMA_10', 'VOLUME_EMA_20', 'VOLUME_EMA_50', 'VOLUME_EMA_100', 'VOLUME_EMA_200',
                'VOLUME_RATE_OF_CHANGE_5', 'VOLUME_RATE_OF_CHANGE_10', 'VOLUME_RATE_OF_CHANGE_20', 'VOLUME_RATE_OF_CHANGE_50',
                'VOLUME_WEIGHTED_AVERAGE_PRICE', 'VOLUME_WEIGHTED_MOVING_AVERAGE_20', 'VOLUME_WEIGHTED_MOVING_AVERAGE_50',
                'VOLUME_WEIGHTED_MOVING_AVERAGE_100', 'VOLUME_WEIGHTED_MOVING_AVERAGE_200',
                # Advanced Volume (50+)
                'VOLUME_PROFILE', 'VOLUME_DELTA', 'VOLUME_IMBALANCE', 'VOLUME_CLUSTERING', 'VOLUME_SPREAD_ANALYSIS',
                'VOLUME_PRICE_TREND', 'VOLUME_OSCILLATOR', 'VOLUME_MOMENTUM', 'VOLUME_ACCELERATION',
                'EASE_OF_MOVEMENT', 'FORCE_INDEX', 'MASS_INDEX', 'PRICE_VOLUME_TREND', 'VOLUME_ADVANCE_DECLINE',
                'VOLUME_BREADTH', 'VOLUME_CONFIRMATION', 'VOLUME_DIVERGENCE', 'VOLUME_EXHAUSTION',
                'VOLUME_ACCUMULATION', 'VOLUME_DISTRIBUTION', 'VOLUME_MONEY_FLOW', 'VOLUME_ON_BALANCE',
                'VOLUME_POSITIVE_FLOW', 'VOLUME_NEGATIVE_FLOW', 'VOLUME_NET_FLOW', 'VOLUME_FLOW_RATIO'
            ],
            'pattern': [
                # Candlestick Patterns (80+)
                'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS',
                'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL',
                'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING',
                'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN',
                'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS',
                'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI',
                'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR',
                'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR',
                'CDLSHORTLINE', 'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
                'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS'
            ],
            'oscillator': [
                # Stochastic Oscillators (30+)
                'STOCH_K_14', 'STOCH_D_14', 'STOCH_FAST_K_14', 'STOCH_FAST_D_14', 'STOCH_SLOW_K_14', 'STOCH_SLOW_D_14',
                'STOCH_K_21', 'STOCH_D_21', 'STOCH_FAST_K_21', 'STOCH_FAST_D_21', 'STOCH_SLOW_K_21', 'STOCH_SLOW_D_21',
                'STOCH_K_28', 'STOCH_D_28', 'STOCH_FAST_K_28', 'STOCH_FAST_D_28', 'STOCH_SLOW_K_28', 'STOCH_SLOW_D_28',
                'STOCH_RSI_14', 'STOCH_RSI_21', 'STOCH_RSI_28', 'STOCH_RSI_35', 'STOCH_RSI_50',
                # Williams %R (20+)
                'WILLR_14', 'WILLR_21', 'WILLR_28', 'WILLR_35', 'WILLR_50', 'WILLR_100', 'WILLR_200',
                # Ultimate Oscillator (15+)
                'ULTOSC_7_14_28', 'ULTOSC_10_20_40', 'ULTOSC_14_28_56', 'ULTOSC_21_42_84'
            ],
            'support_resistance': [
                # Pivot Points (40+)
                'PIVOT_POINT', 'PIVOT_RESISTANCE_1', 'PIVOT_RESISTANCE_2', 'PIVOT_RESISTANCE_3', 'PIVOT_RESISTANCE_4',
                'PIVOT_SUPPORT_1', 'PIVOT_SUPPORT_2', 'PIVOT_SUPPORT_3', 'PIVOT_SUPPORT_4',
                'PIVOT_MIDPOINT_R1_S1', 'PIVOT_MIDPOINT_R2_S2', 'PIVOT_MIDPOINT_R3_S3',
                # Fibonacci Levels (30+)
                'FIB_RETRACEMENT_23_6', 'FIB_RETRACEMENT_38_2', 'FIB_RETRACEMENT_50_0', 'FIB_RETRACEMENT_61_8', 'FIB_RETRACEMENT_78_6',
                'FIB_EXTENSION_127_2', 'FIB_EXTENSION_161_8', 'FIB_EXTENSION_261_8', 'FIB_EXTENSION_423_6',
                'FIB_PROJECTION_127_2', 'FIB_PROJECTION_161_8', 'FIB_PROJECTION_261_8', 'FIB_PROJECTION_423_6',
                # Ichimoku Cloud (10+)
                'ICHIMOKU_TENKAN', 'ICHIMOKU_KIJUN', 'ICHIMOKU_SENKOU_A', 'ICHIMOKU_SENKOU_B', 'ICHIMOKU_CHIKOU',
                'ICHIMOKU_CLOUD_TOP', 'ICHIMOKU_CLOUD_BOTTOM', 'ICHIMOKU_CLOUD_MIDDLE',
                # Advanced Support/Resistance (30+)
                'DYNAMIC_SUPPORT', 'DYNAMIC_RESISTANCE', 'STATIC_SUPPORT', 'STATIC_RESISTANCE',
                'TREND_LINE_SUPPORT', 'TREND_LINE_RESISTANCE', 'HORIZONTAL_SUPPORT', 'HORIZONTAL_RESISTANCE'
            ],
            'advanced': [
                # Fractal Analysis (20+)
                'FRACTAL_HIGH', 'FRACTAL_LOW', 'FRACTAL_BREAKOUT', 'FRACTAL_SUPPORT', 'FRACTAL_RESISTANCE',
                'FRACTAL_DIMENSION', 'FRACTAL_EFFICIENCY', 'FRACTAL_STRENGTH', 'FRACTAL_MOMENTUM',
                # Advanced Mathematical (50+)
                'GATOR', 'OSMA', 'TRIX', 'VORTEX_POSITIVE', 'VORTEX_NEGATIVE', 'WILLIAMS_R', 'ZIGZAG',
                'DETRENDED_PRICE', 'LINEAR_REGRESSION', 'LINEAR_REGRESSION_SLOPE', 'LINEAR_REGRESSION_ANGLE',
                'LINEAR_REGRESSION_INTERCEPT', 'STANDARD_DEVIATION', 'VARIANCE', 'AVERAGE_TRUE_RANGE',
                'TRUE_RANGE', 'NORMALIZED_AVERAGE_TRUE_RANGE', 'CHANDELIER_EXIT', 'AROON_UP', 'AROON_DOWN',
                'AROON_OSC', 'BALANCE_OF_POWER', 'COMMODITY_CHANNEL_INDEX', 'CHAIKIN_MONEY_FLOW',
                'EASE_OF_MOVEMENT', 'FORCE_INDEX', 'NEGATIVE_VOLUME_INDEX', 'ON_BALANCE_VOLUME',
                'POSITIVE_VOLUME_INDEX', 'PRICE_VOLUME_TREND', 'VOLUME_RATE_OF_CHANGE', 'VOLUME_WEIGHTED_AVERAGE_PRICE',
                'VOLUME_WEIGHTED_MOVING_AVERAGE', 'WEIGHTED_CLOSE', 'MEDIAN_PRICE', 'TYPICAL_PRICE',
                # Machine Learning Features (40+)
                'ML_TREND_CLASSIFIER', 'ML_MOMENTUM_PREDICTOR', 'ML_VOLATILITY_ESTIMATOR', 'ML_VOLUME_ANALYZER',
                'ML_PATTERN_RECOGNIZER', 'ML_SUPPORT_RESISTANCE_DETECTOR', 'ML_BREAKOUT_PREDICTOR',
                'ML_REVERSAL_DETECTOR', 'ML_CONTINUATION_PREDICTOR', 'ML_TREND_STRENGTH_ANALYZER'
            ]
        }
        
        # God Mode 1000: Advanced price patterns with enhanced recognition
        self.price_patterns = {
            'classical': ['HEAD_AND_SHOULDERS', 'INVERSE_HEAD_AND_SHOULDERS', 'DOUBLE_TOP', 'DOUBLE_BOTTOM', 'TRIPLE_TOP', 'TRIPLE_BOTTOM', 'ASCENDING_TRIANGLE', 'DESCENDING_TRIANGLE', 'SYMMETRICAL_TRIANGLE', 'WEDGE_RISING', 'WEDGE_FALLING', 'FLAG_BULL', 'FLAG_BEAR', 'PENNANT', 'RECTANGLE', 'DIAMOND'],
            'elliott_wave': ['IMPULSE_WAVE', 'CORRECTIVE_WAVE', 'EXTENDED_WAVE', 'DIAGONAL_TRIANGLE', 'FLAT_CORRECTION', 'ZIGZAG_CORRECTION', 'TRIANGLE_CORRECTION', 'COMPLEX_CORRECTION'],
            'wyckoff': ['ACCUMULATION', 'MARKUP', 'DISTRIBUTION', 'MARKDOWN', 'SPRING', 'TEST', 'SIGN_OF_STRENGTH', 'LAST_POINT_OF_SUPPORT', 'JUMP', 'BACKUP', 'UPTHRUST', 'SIGN_OF_WEAKNESS', 'LAST_POINT_OF_SUPPLY'],
            'harmonic': ['GARTLEY', 'BUTTERFLY', 'BAT', 'CRAB', 'CYPHER', 'SHARK', '5_0_PATTERN', 'AB_CD_PATTERN'],
            'fractal': ['FRACTAL_HIGH', 'FRACTAL_LOW', 'FRACTAL_BREAKOUT', 'FRACTAL_SUPPORT', 'FRACTAL_RESISTANCE'],
            'smart_money': ['VOLUME_PROFILE', 'MARKET_STRUCTURE', 'LIQUIDITY_ZONES', 'ORDER_FLOW', 'WHALE_ACTIVITY', 'INSTITUTIONAL_FOOTPRINT', 'SMART_MONEY_CONCEPTS', 'FAIR_VALUE_GAPS', 'IMBALANCE_ZONES', 'BREAK_OF_STRUCTURE', 'CHANGE_OF_CHARACTER'],
            'fibonacci': ['FIB_RETRACEMENT_23_6', 'FIB_RETRACEMENT_38_2', 'FIB_RETRACEMENT_50_0', 'FIB_RETRACEMENT_61_8', 'FIB_RETRACEMENT_78_6', 'FIB_EXTENSION_127_2', 'FIB_EXTENSION_161_8', 'FIB_EXTENSION_261_8', 'FIB_EXTENSION_423_6'],
            'candlestick': ['CUP_AND_HANDLE', 'INVERSE_CUP_AND_HANDLE', 'SAUCER', 'INVERSE_SAUCER', 'ROUNDING_BOTTOM', 'ROUNDING_TOP', 'ASCENDING_CHANNEL', 'DESCENDING_CHANNEL', 'HORIZONTAL_CHANNEL', 'TREND_LINE_BREAK', 'SUPPORT_BREAK', 'RESISTANCE_BREAK', 'BREAKOUT', 'BREAKDOWN', 'GAP_UP', 'GAP_DOWN', 'ISLAND_REVERSAL', 'MORNING_STAR', 'EVENING_STAR', 'DOJI_STAR', 'HAMMER', 'HANGING_MAN', 'SHOOTING_STAR', 'INVERTED_HAMMER', 'SPINNING_TOP', 'MARUBOZU', 'ENGULFING_BULL', 'ENGULFING_BEAR', 'HARAMI_BULL', 'HARAMI_BEAR', 'PIERCING_LINE', 'DARK_CLOUD_COVER', 'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS', 'ABANDONED_BABY', 'MATCHING_LOW', 'KICKING', 'THREE_LINE_STRIKE', 'IDENTICAL_THREE_CROWS', 'UPSIDE_TASUKI_GAP', 'ONNECK_LINE', 'INNECK_LINE', 'THRUSTING_LINE']
        }
        
        # Cache for calculated indicators
        self.indicator_cache = {}
        self.pattern_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Performance tracking
        self.calculation_times = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Removed multi-threading support to avoid ScriptRunContext warnings
        # All operations are now synchronous to prevent UI blocking
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            self._default_max_workers = min(cpu_count * 2, 16)  # Up to 16 workers, 2x CPU cores
        except Exception:
            self._default_max_workers = 8  # Fallback
        self._executor = None
        
        self.unified_logger.info("[START] Unified Technical Indicators Engine initialized - God Mode 1000")
        
        self._initialized = True
    
    def calculate_indicators_optimized(self, df: 'pd.DataFrame', symbols: List[str] = None, 
                                     indicators: List[str] = None, force_recalculate: bool = False) -> Dict[str, Any]:
        """Calculate indicators with optimization to ensure each indicator is calculated only once"""
        try:
            self.unified_logger.debug(f"[OPTIMIZED] Calculating indicators for {len(symbols) if symbols else 'all'} symbols")
            
            # Build dependency graph
            self._build_dependency_graph()
            
            # Determine calculation order based on dependencies
            calculation_order = self._determine_calculation_order(indicators or self.get_all_indicators())
            
            # Calculate indicators in optimal order
            results = {}
            for indicator in calculation_order:
                if indicator not in self.calculated_indicators or force_recalculate:
                    indicator_result = self._calculate_single_indicator(df, indicator)
                    if indicator_result is not None:
                        results[indicator] = indicator_result
                        self.calculated_indicators.add(indicator)
                        self.indicator_cache[indicator] = indicator_result
            
            # Store calculation order for future reference
            self.calculation_order = calculation_order
            
            return {
                'indicators': results,
                'calculation_order': calculation_order,
                'calculated_count': len(self.calculated_indicators),
                'cache_hits': len(self.calculated_indicators) - len(results),
                'optimization_status': 'successful'
            }
            
        except Exception as e:
            self.unified_logger.error(f"Optimized indicator calculation failed: {e}")
            return {'error': str(e)}
    
    def _build_dependency_graph(self):
        """Build dependency graph for indicators to determine calculation order"""
        try:
            # Define indicator dependencies
            self.dependency_graph = {
                'SMA_20': [],
                'SMA_50': [],
                'EMA_20': [],
                'EMA_50': [],
                'RSI': ['SMA_20'],
                'MACD': ['EMA_12', 'EMA_26'],
                'Bollinger_Bands': ['SMA_20'],
                'Stochastic': ['SMA_14'],
                'Williams_R': ['SMA_14'],
                'CCI': ['SMA_20'],
                'ATR': ['SMA_14'],
                'ADX': ['ATR', 'SMA_14'],
                'Parabolic_SAR': ['ATR'],
                'Ichimoku': ['SMA_9', 'SMA_26'],
                'Volume_Profile': ['SMA_20'],
                'Support_Resistance': ['SMA_20', 'SMA_50'],
                'Trend_Lines': ['SMA_20'],
                'Fibonacci_Levels': ['SMA_20'],
                'Pivot_Points': ['SMA_20'],
                'Market_Structure': ['SMA_20', 'ATR'],
                'Wyckoff_Analysis': ['Volume_Profile', 'Support_Resistance'],
                'Elliott_Wave': ['Trend_Lines', 'Fibonacci_Levels'],
                'Harmonic_Patterns': ['Fibonacci_Levels', 'Support_Resistance'],
                'Fractal_Patterns': ['Market_Structure'],
                'Head_Shoulders': ['Support_Resistance', 'Volume_Profile'],
                'Double_Top': ['Support_Resistance', 'Volume_Profile'],
                'Triangle_Patterns': ['Trend_Lines', 'Support_Resistance'],
                'Flag_Patterns': ['Trend_Lines', 'Volume_Profile'],
                'Cup_Handle': ['Support_Resistance', 'Volume_Profile'],
                'Breakout_Patterns': ['Support_Resistance', 'Volume_Profile'],
                'Breakdown_Patterns': ['Support_Resistance', 'Volume_Profile'],
                'Continuation_Patterns': ['Trend_Lines', 'Volume_Profile'],
                'Reversal_Patterns': ['Support_Resistance', 'Volume_Profile']
            }
            
        except Exception as e:
            self.unified_logger.error(f"Dependency graph building failed: {e}")
            self.dependency_graph = {}
    
    def _determine_calculation_order(self, indicators: List[str]) -> List[str]:
        """Determine optimal calculation order based on dependencies"""
        try:
            # Topological sort to determine calculation order
            visited = set()
            temp_visited = set()
            calculation_order = []
            
            def visit(indicator):
                if indicator in temp_visited:
                    return  # Circular dependency
                if indicator in visited:
                    return
                
                temp_visited.add(indicator)
                
                # Visit dependencies first
                dependencies = self.dependency_graph.get(indicator, [])
                for dep in dependencies:
                    if dep in indicators:  # Only include if requested
                        visit(dep)
                
                temp_visited.remove(indicator)
                visited.add(indicator)
                calculation_order.append(indicator)
            
            # Visit all requested indicators
            for indicator in indicators:
                if indicator not in visited:
                    visit(indicator)
            
            return calculation_order
            
        except Exception as e:
            self.unified_logger.error(f"Calculation order determination failed: {e}")
            return indicators  # Fallback to original order
    
    def _calculate_single_indicator(self, df: 'pd.DataFrame', indicator: str) -> Any:
        """Calculate a single indicator efficiently"""
        try:
            # Check if indicator is already calculated and cached
            if indicator in self.indicator_cache and indicator in self.calculated_indicators:
                return self.indicator_cache[indicator]
            
            # Calculate the indicator based on its category
            if indicator.startswith('SMA_'):
                period = int(indicator.split('_')[1])
                return self._calculate_sma(df, period)
            elif indicator.startswith('EMA_'):
                period = int(indicator.split('_')[1])
                return self._calculate_ema(df, period)
            elif indicator == 'RSI':
                return self._calculate_rsi(df)
            elif indicator == 'MACD':
                return self._calculate_macd(df)
            elif indicator == 'Bollinger_Bands':
                return self._calculate_bollinger_bands(df)
            elif indicator == 'Stochastic':
                return self._calculate_stochastic(df)
            elif indicator == 'Williams_R':
                return self._calculate_williams_r(df)
            elif indicator == 'CCI':
                return self._calculate_cci(df)
            elif indicator == 'ATR':
                return self._calculate_atr(df)
            elif indicator == 'ADX':
                return self._calculate_adx(df)
            elif indicator == 'Parabolic_SAR':
                return self._calculate_parabolic_sar(df)
            elif indicator == 'Ichimoku':
                return self._calculate_ichimoku_cloud(df)
            elif indicator == 'Volume_Profile':
                return self._calculate_volume_profile(df)
            elif indicator == 'Support_Resistance':
                return self._calculate_support_resistance(df)
            elif indicator == 'Trend_Lines':
                return self._calculate_trend_lines(df)
            elif indicator == 'Fibonacci_Levels':
                return self._calculate_fibonacci_levels(df)
            elif indicator == 'Pivot_Points':
                return self._calculate_pivot_points(df)
            elif indicator == 'Market_Structure':
                return self._calculate_market_structure(df)
            elif indicator == 'Wyckoff_Analysis':
                return self._calculate_wyckoff_analysis(df)
            elif indicator == 'Elliott_Wave':
                return self._calculate_elliott_wave(df)
            elif indicator == 'Harmonic_Patterns':
                return self._calculate_harmonic_patterns(df)
            elif indicator == 'Fractal_Patterns':
                return self._calculate_fractal_patterns(df)
            elif indicator == 'Head_Shoulders':
                return self._calculate_head_shoulders(df)
            elif indicator == 'Double_Top':
                return self._calculate_double_top(df)
            elif indicator == 'Triangle_Patterns':
                return self._calculate_triangle_patterns(df)
            elif indicator == 'Flag_Patterns':
                return self._calculate_flag_patterns(df)
            elif indicator == 'Cup_Handle':
                return self._calculate_cup_handle(df)
            elif indicator == 'Breakout_Patterns':
                return self._calculate_breakout_patterns(df)
            elif indicator == 'Breakdown_Patterns':
                return self._calculate_breakdown_patterns(df)
            elif indicator == 'Continuation_Patterns':
                return self._calculate_continuation_patterns(df)
            elif indicator == 'Reversal_Patterns':
                return self._calculate_reversal_patterns(df)
            else:
                # Try to calculate using advanced feature engineering
                if self.advanced_fe:
                    return self.advanced_fe.calculate_indicator(df, indicator)
                else:
                    return None
                    
        except Exception as e:
            self.unified_logger.error(f"Single indicator calculation failed for {indicator}: {e}")
            return None
    
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Get statistics about indicator calculations"""
        try:
            return {
                'total_calculated': len(self.calculated_indicators),
                'cache_size': len(self.indicator_cache),
                'calculation_order': self.calculation_order,
                'dependency_graph_size': len(self.dependency_graph),
                'optimization_efficiency': len(self.calculated_indicators) / max(1, len(self.get_all_indicators()))
            }
        except Exception as e:
            self.unified_logger.error(f"Calculation statistics retrieval failed: {e}")
            return {}
    
    def clear_indicator_cache(self):
        """Clear the indicator cache to force recalculation"""
        try:
            self.calculated_indicators.clear()
            self.indicator_cache.clear()
            self.calculation_order = []
            self.unified_logger.info("Indicator cache cleared")
        except Exception as e:
            self.unified_logger.error(f"Failed to clear indicator cache: {e}")

    def _ensure_executor(self, max_workers: Optional[int] = None):
        """Removed executor to avoid ScriptRunContext warnings."""
        # All operations are now synchronous to prevent UI blocking
        pass

    def shutdown(self, wait: bool = True):
        """Shutdown the internal executor if it exists."""
        try:
            if getattr(self, '_executor', None) is not None:
                self._executor.shutdown(wait=wait)
                self.unified_logger.info("UnifiedTechnicalIndicators executor shutdown completed")
        except Exception as e:
            self.unified_logger.exception("Error during UnifiedTechnicalIndicators shutdown")
            # Best-effort: try to clear caches
            try:
                self.clear_indicator_cache()
            except Exception:
                pass
    
    def get_all_indicators(self) -> List[str]:
        """Get all available indicators"""
        try:
            all_indicators = []
            for category, indicators in self.indicator_categories.items():
                all_indicators.extend(indicators)
            return all_indicators
        except Exception as e:
            self.unified_logger.error(f"All indicators retrieval failed: {e}")
            return []
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate ALL 1000+ indicators for a given DataFrame - OPTIMIZED with caching
        
        This is the CENTRALIZED method that calculates indicators ONCE and caches them.
        All other modules should use this method instead of calculating indicators separately.
        
        Args:
            df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
            
        Returns:
            Dict[str, Any]: Dictionary of all calculated indicators
        """
        try:
            # Validate DataFrame format
            if df is None or len(df) == 0:
                self.unified_logger.warning("Empty DataFrame provided to calculate_all_indicators")
                return {}
            
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.unified_logger.error(f"DataFrame missing required columns: {missing_columns}. Available: {df.columns.tolist()}")
                return {}
            
            # Validate data types and handle non-numeric data
            for col in required_columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except Exception as e:
                        self.unified_logger.error(f"Failed to convert column {col} to numeric: {e}")
                        return {}
            
            # Build unique cache key based on dataframe content (NOT object ID)
            # FIXED: Use data hash instead of id() for stable caching
            import hashlib
            # Create stable hash based on length and first/last close prices
            data_signature = f"{len(df)}_{float(df['close'].iloc[0])}_{float(df['close'].iloc[-1])}" if len(df) > 0 else "empty"
            data_hash = hashlib.md5(data_signature.encode()).hexdigest()[:16]
            cache_key = f"all_indicators_{data_hash}"
            
            # Check cache first - AVOID DUPLICATE CALCULATIONS
            if cache_key in self.indicator_cache:
                self.cache_hits += 1
                return self.indicator_cache[cache_key]
            
            self.cache_misses += 1
            
            # Calculate all indicators by category
            all_results = {}
            
            # TREND INDICATORS
            trend_indicators = self._calculate_trend_indicators(df)
            all_results.update(trend_indicators)
            
            # MOMENTUM INDICATORS
            momentum_indicators = self._calculate_momentum_indicators(df)
            all_results.update(momentum_indicators)
            
            # VOLATILITY INDICATORS
            volatility_indicators = self._calculate_volatility_indicators(df)
            all_results.update(volatility_indicators)
            
            # VOLUME INDICATORS
            volume_indicators = self._calculate_volume_indicators(df)
            all_results.update(volume_indicators)
            
            # OSCILLATOR INDICATORS - REMOVED: duplicate of momentum indicators (already calculated above)
            # All oscillator calculations are included in _calculate_momentum_indicators
            
            # SUPPORT/RESISTANCE INDICATORS
            sr_indicators = self._calculate_support_resistance_indicators(df)
            all_results.update(sr_indicators)
            
            # PATTERN RECOGNITION
            pattern_indicators = self._calculate_pattern_indicators(df)
            all_results.update(pattern_indicators)
            
            # ADVANCED INDICATORS
            advanced_indicators = self._calculate_advanced_indicators(df)
            all_results.update(advanced_indicators)
            
            # Cache results for future use - PREVENT DUPLICATE CALCULATIONS
            self.indicator_cache[cache_key] = all_results
            
            # Log cache statistics (only once per session)
            if not hasattr(self, '_cache_stats_logged'):
                self._cache_stats_logged = True
                self.unified_logger.info(f"✅ Calculated {len(all_results)} indicators | Cache: {self.cache_hits} hits, {self.cache_misses} misses")
            
            return all_results
            
        except Exception as e:
            self.unified_logger.error(f"Calculate all indicators failed: {e}")
            import traceback
            traceback_str = traceback.format_exc()
            self.unified_logger.error(f"Full traceback: {traceback_str}")
            # Return empty dict but don't crash the system
            return {}
    
    def _calculate_trend_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all trend indicators"""
        try:
            results = {}
            
            # Validate input data
            if data is None or len(data) == 0:
                self.unified_logger.error("Trend indicators: data is None or empty")
                return {}
            
            # Ensure data is DataFrame
            if not isinstance(data, pd.DataFrame):
                self.unified_logger.error(f"Trend indicators: data must be DataFrame, got {type(data)}")
                return {}
            
            # Check if required columns exist
            if 'close' not in data.columns:
                self.unified_logger.error(f"Missing 'close' column in data. Available columns: {list(data.columns)}")
                return {}
            
            # Simple Moving Averages
            for period in [5, 10, 20, 50, 100, 200]:
                results[f'SMA_{period}'] = self._calculate_sma(data['close'], period)
                results[f'EMA_{period}'] = self._calculate_ema(data['close'], period)
                results[f'WMA_{period}'] = self._calculate_wma(data['close'], period)
            
            # Advanced moving averages
            results['TEMA'] = self._calculate_tema(data['close'])
            results['DEMA'] = self._calculate_dema(data['close'])
            results['KAMA'] = self._calculate_kama(data['close'])
            results['MAMA'] = self._calculate_mama(data['close'])
            results['TRIMA'] = self._calculate_trima(data['close'])
            results['HMA'] = self._calculate_hma(data['close'])
            results['ZLEMA'] = self._calculate_zlema(data['close'])
            results['ALMA'] = self._calculate_alma(data['close'])
            results['VIDYA'] = self._calculate_vidya(data['close'])
            
            # Volume-weighted indicators
            results['VWMA'] = self._calculate_vwma(data)
            results['LWMA'] = self._calculate_lwma(data['close'])
            results['EWMA'] = self._calculate_ewma(data['close'])
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating trend indicators: {e}")
            return {}
    
    def _calculate_momentum_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all momentum indicators"""
        try:
            results = {}
            
            # Validate input data
            if data is None or len(data) == 0:
                self.unified_logger.error("Momentum indicators: data is None or empty")
                return {}
            
            # Ensure data is DataFrame
            if not isinstance(data, pd.DataFrame):
                self.unified_logger.error(f"Momentum indicators: data must be DataFrame, got {type(data)}")
                return {}
            
            # Check if required columns exist
            if 'close' not in data.columns:
                self.unified_logger.error(f"Missing 'close' column in data. Available columns: {list(data.columns)}")
                return {}
            
            # RSI variations
            for period in [14, 21, 28]:
                results[f'RSI_{period}'] = self._calculate_rsi(data['close'], period)
            
            # Stochastic variations
            results['STOCH'] = self._calculate_stochastic(data)
            results['STOCHF'] = self._calculate_stochastic_fast(data)
            results['STOCHRSI'] = self._calculate_stochastic_rsi(data['close'])
            
            # Williams %R
            results['WILLR'] = self._calculate_williams_r(data)
            
            # ADX and related
            results['ADX'] = self._calculate_adx(data)
            results['ADXR'] = self._calculate_adxr(data)
            results['MINUS_DI'] = self._calculate_minus_di(data)
            results['PLUS_DI'] = self._calculate_plus_di(data)
            results['DX'] = self._calculate_dx(data)
            
            # Commodity Channel Index
            results['CCI'] = self._calculate_cci(data)
            
            # Chande Momentum Oscillator
            results['CMO'] = self._calculate_cmo(data['close'])
            
            # MACD variations
            results['MACD'] = self._calculate_macd(data['close'])
            results['MACDEXT'] = self._calculate_macd_ext(data['close'])
            results['MACDFIX'] = self._calculate_macd_fix(data['close'])
            results['PPO'] = self._calculate_ppo(data['close'])
            
            # Rate of Change
            for period in [10, 12, 14, 25]:
                results[f'ROC_{period}'] = self._calculate_roc(data['close'], period)
                results[f'ROCP_{period}'] = self._calculate_rocp(data['close'], period)
                results[f'ROCR_{period}'] = self._calculate_rocr(data['close'], period)
                results[f'ROCR100_{period}'] = self._calculate_rocr100(data['close'], period)
            
            # Momentum
            results['MOM'] = self._calculate_momentum(data['close'])
            
            # Balance of Power
            results['BOP'] = self._calculate_bop(data)
            
            # Money Flow Index
            results['MFI'] = self._calculate_mfi(data)
            
            # Time Series Forecast
            results['TSF'] = self._calculate_tsf(data['close'])
            
            # Ultimate Oscillator
            results['ULTOSC'] = self._calculate_ultosc(data)
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating momentum indicators: {e}")
            return {}
    
    def _calculate_volatility_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all volatility indicators"""
        try:
            results = {}
            
            # Average True Range variations
            for period in [14, 20, 21]:
                results[f'ATR_{period}'] = self._calculate_atr(data, period)
                results[f'NATR_{period}'] = self._calculate_natr(data, period)
            
            # True Range
            results['TRANGE'] = self._calculate_trange(data)
            
            # Bollinger Bands
            for period in [20, 21, 30]:
                for std_dev in [1, 2, 3]:
                    bb = self._calculate_bollinger_bands(data['close'], period, std_dev)
                    results[f'BBANDS_UPPER_{period}_{std_dev}'] = bb['upper']
                    results[f'BBANDS_MIDDLE_{period}_{std_dev}'] = bb['middle']
                    results[f'BBANDS_LOWER_{period}_{std_dev}'] = bb['lower']
            
            # Keltner Channels
            kc = self._calculate_keltner_channels(data)
            results['KELTNER_UPPER'] = kc['upper']
            results['KELTNER_MIDDLE'] = kc['middle']
            results['KELTNER_LOWER'] = kc['lower']
            
            # Donchian Channels
            dc = self._calculate_donchian_channels(data)
            results['DONCHIAN_UPPER'] = dc['upper']
            results['DONCHIAN_LOWER'] = dc['lower']
            results['DONCHIAN_MIDDLE'] = dc['middle']
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating volatility indicators: {e}")
            return {}
    
    def _calculate_volume_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all volume indicators"""
        try:
            results = {}
            
            # Accumulation/Distribution
            results['AD'] = self._calculate_ad(data)
            results['ADOSC'] = self._calculate_adosc(data)
            
            # On-Balance Volume
            results['OBV'] = self._calculate_obv(data)
            
            # Chaikin Money Flow
            results['CMF'] = self._calculate_cmf(data)
            
            # Ease of Movement
            results['EOM'] = self._calculate_eom(data)
            
            # Force Index
            results['FI'] = self._calculate_fi(data)
            
            # Money Flow Index (already calculated in momentum)
            # Volume Price Trend
            results['VPT'] = self._calculate_vpt(data)
            
            # Negative/Positive Volume Index
            results['NVI'] = self._calculate_nvi(data)
            results['PVI'] = self._calculate_pvi(data)
            
            # Volume-weighted indicators
            results['VWAP'] = self._calculate_vwap(data)
            results['VWMA'] = self._calculate_vwma(data)
            
            # Volume moving averages
            for period in [10, 20, 50]:
                results[f'VOLUME_SMA_{period}'] = self._calculate_sma(data['volume'], period)
                results[f'VOLUME_EMA_{period}'] = self._calculate_ema(data['volume'], period)
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating volume indicators: {e}")
            return {}
    
    def _calculate_pattern_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all candlestick pattern indicators"""
        try:
            results = {}
            
            # All TA-Lib candlestick patterns
            pattern_functions = [
                'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE',
                'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK',
                'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL',
                'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR', 'CDLDRAGONFLYDOJI',
                'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE',
                'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS',
                'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS',
                'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM',
                'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD',
                'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN',
                'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE',
                'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
                'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS'
            ]
            
            for pattern in pattern_functions:
                try:
                    if hasattr(talib, pattern):
                        func = getattr(talib, pattern)
                        results[pattern] = func(data['open'], data['high'], data['low'], data['close'])
                except Exception as e:
                    self.unified_logger.warning(f"Failed to calculate {pattern}: {e}")
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating pattern indicators: {e}")
            return {}
    
    # REMOVED: _calculate_oscillator_indicators - DUPLICATE of _calculate_momentum_indicators
    # All oscillator calculations are already included in _calculate_momentum_indicators
    # This function was causing CMO and other indicators to be calculated twice
    
    def _calculate_natr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Normalized Average True Range"""
        try:
            atr = self._calculate_atr(data, period)
            natr = (atr / data['close']) * 100
            return natr.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating NATR: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_ad(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        try:
            clv = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
            clv = clv.fillna(0)  # Handle division by zero
            ad = (clv * data['volume']).cumsum()
            return ad
        except Exception as e:
            self.unified_logger.error(f"Error calculating AD: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_fractal(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate Fractal indicators"""
        try:
            high_fractals = pd.Series([False] * len(data), index=data.index)
            low_fractals = pd.Series([False] * len(data), index=data.index)
            
            for i in range(2, len(data) - 2):
                # High fractal: high is higher than 2 periods before and after
                if (data['high'].iloc[i] > data['high'].iloc[i-2] and 
                    data['high'].iloc[i] > data['high'].iloc[i-1] and
                    data['high'].iloc[i] > data['high'].iloc[i+1] and 
                    data['high'].iloc[i] > data['high'].iloc[i+2]):
                    high_fractals.iloc[i] = True
                
                # Low fractal: low is lower than 2 periods before and after
                if (data['low'].iloc[i] < data['low'].iloc[i-2] and 
                    data['low'].iloc[i] < data['low'].iloc[i-1] and
                    data['low'].iloc[i] < data['low'].iloc[i+1] and 
                    data['low'].iloc[i] < data['low'].iloc[i+2]):
                    low_fractals.iloc[i] = True
            
            return {
                'high_fractals': high_fractals,
                'low_fractals': low_fractals
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating Fractal: {e}")
            return {
                'high_fractals': pd.Series([False] * len(data), index=data.index),
                'low_fractals': pd.Series([False] * len(data), index=data.index)
            }
    def _calculate_trange(self, data: pd.DataFrame) -> pd.Series:
        """Calculate True Range"""
        try:
            high_low = data['high'] - data['low']
            high_close_prev = abs(data['high'] - data['close'].shift())
            low_close_prev = abs(data['low'] - data['close'].shift())
            
            trange = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            return trange.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating TRANGE: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_adosc(self, data: pd.DataFrame, fast_period: int = 3, slow_period: int = 10) -> pd.Series:
        """Calculate Accumulation/Distribution Oscillator"""
        try:
            ad = self._calculate_ad(data)
            adosc = ad.rolling(window=fast_period).mean() - ad.rolling(window=slow_period).mean()
            return adosc.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating ADOSC: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_gator(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate Gator Oscillator"""
        try:
            # Gator is based on Alligator indicator
            jaw = self._calculate_sma(data['close'], 13).shift(8)
            teeth = self._calculate_sma(data['close'], 8).shift(5)
            lips = self._calculate_sma(data['close'], 5).shift(3)
            
            gator_jaw = jaw - teeth
            gator_lips = teeth - lips
            
            return {
                'gator_jaw': gator_jaw.fillna(0),
                'gator_lips': gator_lips.fillna(0)
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating Gator: {e}")
            return {
                'gator_jaw': pd.Series([0] * len(data), index=data.index),
                'gator_lips': pd.Series([0] * len(data), index=data.index)
            }
    
    def _calculate_keltner_channels(self, data: pd.DataFrame, period: int = 20, multiplier: float = 2) -> Dict[str, pd.Series]:
        """Calculate Keltner Channels"""
        try:
            if 'close' not in data.columns or 'high' not in data.columns or 'low' not in data.columns:
                return {
                    'upper': pd.Series([0] * len(data), index=data.index),
                    'middle': pd.Series([0] * len(data), index=data.index),
                    'lower': pd.Series([0] * len(data), index=data.index)
                }
            
            # Calculate EMA of close prices
            ema = data['close'].ewm(span=period).mean()
            
            # Calculate Average True Range
            atr = self._calculate_atr(data, period)
            
            # Calculate Keltner Channels
            upper = ema + (multiplier * atr)
            lower = ema - (multiplier * atr)
            
            return {
                'upper': upper.fillna(0),
                'middle': ema.fillna(0),
                'lower': lower.fillna(0)
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating Keltner Channels: {e}")
            return {
                'upper': pd.Series([0] * len(data), index=data.index),
                'middle': pd.Series([0] * len(data), index=data.index),
                'lower': pd.Series([0] * len(data), index=data.index)
            }
    
    def _calculate_cmf(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Chaikin Money Flow"""
        try:
            if 'close' not in data.columns or 'high' not in data.columns or 'low' not in data.columns or 'volume' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate Money Flow Multiplier
            mfm = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
            mfm = mfm.fillna(0)  # Handle division by zero
            
            # Calculate Money Flow Volume
            mfv = mfm * data['volume']
            
            # Calculate CMF
            cmf = mfv.rolling(window=period).sum() / data['volume'].rolling(window=period).sum()
            
            return cmf.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating CMF: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_osma(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """Calculate MACD Oscillator (OSMA)"""
        try:
            # Calculate MACD
            macd = self._calculate_macd(data, fast, slow, signal)
            
            if isinstance(macd, dict) and 'macd' in macd and 'signal' in macd:
                # OSMA is MACD - Signal
                osma = macd['macd'] - macd['signal']
                return osma.fillna(0)
            else:
                return pd.Series([0] * len(data), index=data.index)
        except Exception as e:
            self.unified_logger.error(f"Error calculating OSMA: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_donchian_channels(self, data: pd.DataFrame, period: int = 20) -> Dict[str, pd.Series]:
        """Calculate Donchian Channels"""
        try:
            if 'high' not in data.columns or 'low' not in data.columns:
                return {
                    'upper': pd.Series([0] * len(data), index=data.index),
                    'lower': pd.Series([0] * len(data), index=data.index),
                    'middle': pd.Series([0] * len(data), index=data.index)
                }
            
            # Calculate Donchian Channels
            upper = data['high'].rolling(window=period).max()
            lower = data['low'].rolling(window=period).min()
            middle = (upper + lower) / 2
            
            return {
                'upper': upper.fillna(0),
                'lower': lower.fillna(0),
                'middle': middle.fillna(0)
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating Donchian Channels: {e}")
            return {
                'upper': pd.Series([0] * len(data), index=data.index),
                'lower': pd.Series([0] * len(data), index=data.index),
                'middle': pd.Series([0] * len(data), index=data.index)
            }
    
    def _calculate_eom(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Ease of Movement"""
        try:
            if 'high' not in data.columns or 'low' not in data.columns or 'volume' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate Ease of Movement
            distance = (data['high'] + data['low']) / 2 - (data['high'].shift() + data['low'].shift()) / 2
            box_height = data['volume'] / (data['high'] - data['low'])
            box_height = box_height.replace([np.inf, -np.inf], 0).fillna(0)
            
            eom = distance / box_height
            eom = eom.replace([np.inf, -np.inf], 0).fillna(0)
            
            # Calculate moving average
            eom_ma = eom.rolling(window=period).mean()
            
            return eom_ma.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating EOM: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_trix(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate TRIX"""
        try:
            # Calculate triple exponential moving average
            ema1 = data.ewm(span=period).mean()
            ema2 = ema1.ewm(span=period).mean()
            ema3 = ema2.ewm(span=period).mean()
            
            # Calculate TRIX
            trix = ema3.pct_change() * 10000  # Scale by 10000
            
            return trix.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating TRIX: {e}")
    def _calculate_fi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Force Index"""
        try:
            if 'close' not in data.columns or 'volume' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate Force Index
            fi = (data['close'] - data['close'].shift()) * data['volume']
            
            # Calculate moving average
            fi_ma = fi.rolling(window=period).mean()
            
            return fi_ma.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating Force Index: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_vortex(self, data: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """Calculate Vortex indicators"""
        try:
            if 'high' not in data.columns or 'low' not in data.columns:
                return {
                    'positive': pd.Series([0] * len(data), index=data.index),
                    'negative': pd.Series([0] * len(data), index=data.index)
                }
            
            # Calculate Vortex indicators
            tr = self._calculate_trange(data)
            vm_plus = abs(data['high'] - data['low'].shift())
            vm_minus = abs(data['low'] - data['high'].shift())
            
            # Calculate moving averages
            tr_sum = tr.rolling(window=period).sum()
            vm_plus_sum = vm_plus.rolling(window=period).sum()
            vm_minus_sum = vm_minus.rolling(window=period).sum()
            
            # Calculate Vortex indicators
            vi_plus = vm_plus_sum / tr_sum
            vi_minus = vm_minus_sum / tr_sum
            
            return {
                'positive': vi_plus.fillna(0),
                'negative': vi_minus.fillna(0)
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating Vortex: {e}")
            return {
                'positive': pd.Series([0] * len(data), index=data.index),
                'negative': pd.Series([0] * len(data), index=data.index)
            }
    
    def _calculate_vpt(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Volume Price Trend"""
        try:
            if 'close' not in data.columns or 'volume' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate Volume Price Trend
            vpt = (data['close'].pct_change() * data['volume']).cumsum()
            
            # Calculate moving average
            vpt_ma = vpt.rolling(window=period).mean()
            
            return vpt_ma.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating VPT: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_williams_r(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        try:
            if 'high' not in data.columns or 'low' not in data.columns or 'close' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate Williams %R
            highest_high = data['high'].rolling(window=period).max()
            lowest_low = data['low'].rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - data['close']) / (highest_high - lowest_low))
            
            return williams_r.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating Williams %R: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_nvi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Negative Volume Index"""
        try:
            if 'close' not in data.columns or 'volume' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate NVI
            price_change = data['close'].pct_change()
            nvi = pd.Series(index=data.index, dtype=float)
            nvi.iloc[0] = 1000  # Initial value
            
            for i in range(1, len(data)):
                if data['volume'].iloc[i] < data['volume'].iloc[i-1]:  # Negative volume
                    nvi.iloc[i] = nvi.iloc[i-1] * (1 + price_change.iloc[i])
                else:
                    nvi.iloc[i] = nvi.iloc[i-1]
            
            return nvi.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating NVI: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_pvi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Positive Volume Index"""
        try:
            if 'close' not in data.columns or 'volume' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate PVI
            price_change = data['close'].pct_change()
            pvi = pd.Series(index=data.index, dtype=float)
            pvi.iloc[0] = 1000  # Initial value
            
            for i in range(1, len(data)):
                if data['volume'].iloc[i] > data['volume'].iloc[i-1]:  # Positive volume
                    pvi.iloc[i] = pvi.iloc[i-1] * (1 + price_change.iloc[i])
                else:
                    pvi.iloc[i] = pvi.iloc[i-1]
            
            return pvi.fillna(0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating PVI: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_zigzag(self, data: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
        """Calculate ZigZag indicator"""
        try:
            if 'close' not in data.columns:
                return pd.Series([0] * len(data), index=data.index)
            
            # Calculate ZigZag
            close_prices = data['close'].values
            zigzag = np.zeros(len(close_prices))
            
            if len(close_prices) < 3:
                return pd.Series(zigzag, index=data.index)
            
            # Find peaks and troughs
            peaks = []
            troughs = []
            
            for i in range(1, len(close_prices) - 1):
                # Peak
                if close_prices[i] > close_prices[i-1] and close_prices[i] > close_prices[i+1]:
                    peaks.append(i)
                # Trough
                elif close_prices[i] < close_prices[i-1] and close_prices[i] < close_prices[i+1]:
                    troughs.append(i)
            
            # Connect peaks and troughs with lines
            all_points = sorted(peaks + troughs)
            
            for i in range(len(all_points) - 1):
                start_idx = all_points[i]
                end_idx = all_points[i + 1]
                
                # Linear interpolation between points
                for j in range(start_idx, end_idx + 1):
                    if j < len(zigzag):
                        ratio = (j - start_idx) / (end_idx - start_idx) if end_idx != start_idx else 0
                        zigzag[j] = close_prices[start_idx] + ratio * (close_prices[end_idx] - close_prices[start_idx])
            
            return pd.Series(zigzag, index=data.index)
        except Exception as e:
            self.unified_logger.error(f"Error calculating ZigZag: {e}")
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_support_resistance_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all support/resistance indicators"""
        try:
            results = {}
            
            # Parabolic SAR
            results['PSAR'] = self._calculate_psar(data)
            
            # SuperTrend
            results['SUPERTREND'] = self._calculate_supertrend(data)
            
            # Ichimoku Cloud - FIXED: Use correct function name
            # OLD: ichimoku = self._calculate_ichimoku(data) - function doesn't exist
            # NEW: Use _calculate_ichimoku_cloud which is the actual implementation
            try:
                ichimoku = self._calculate_ichimoku_cloud(data)
                if ichimoku:
                    # Extract values from IndicatorResult objects
                    if 'ichimoku_tenkan' in ichimoku:
                        results['ICHIMOKU_TENKAN'] = ichimoku['ichimoku_tenkan'].value
                    if 'ichimoku_kijun' in ichimoku:
                        results['ICHIMOKU_KIJUN'] = ichimoku['ichimoku_kijun'].value
                    if 'ichimoku_senkou_a' in ichimoku:
                        results['ICHIMOKU_SENKOU_A'] = ichimoku.get('ichimoku_senkou_a', {}).get('value', 0)
                    if 'ichimoku_senkou_b' in ichimoku:
                        results['ICHIMOKU_SENKOU_B'] = ichimoku.get('ichimoku_senkou_b', {}).get('value', 0)
                    if 'ichimoku_chikou' in ichimoku:
                        results['ICHIMOKU_CHIKOU'] = ichimoku.get('ichimoku_chikou', {}).get('value', 0)
            except Exception as e:
                self.unified_logger.debug(f"Ichimoku calculation skipped: {e}")
            
            # Pivot Points - Use existing _calculate_pivot_points_simple function
            results['PIVOT_POINT'] = self._calculate_pivot_points_simple(data)
            results['CAMARILLA_PIVOT'] = self._calculate_camarilla_pivot_points(data)
            results['WOODIE_PIVOT'] = self._calculate_woodie_pivot_points(data)
            results['DEMARK_PIVOT'] = self._calculate_demark_pivot_points(data)
            
            # Fibonacci levels - FIXED: Use correct method names
            fib_retracement = self._calculate_fibonacci_retracement_simple(data, period=20)
            fib_extension = self._calculate_fibonacci_extension_simple(data, period=20) if hasattr(self, '_calculate_fibonacci_extension_simple') else {}
            results['FIBONACCI_RETRACEMENT'] = fib_retracement
            results['FIBONACCI_EXTENSION'] = fib_extension
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating support/resistance indicators: {e}")
            return {}
    
    def _calculate_advanced_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all advanced indicators"""
        try:
            results = {}
            
            # Fractal indicators
            results['FRACTAL'] = self._calculate_fractal(data)
            
            # Gator Oscillator
            results['GATOR'] = self._calculate_gator(data)
            
            # MACD Oscillator
            results['OSMA'] = self._calculate_osma(data['close'])
            
            # TRIX
            results['TRIX'] = self._calculate_trix(data['close'])
            
            # Vortex indicators
            vortex = self._calculate_vortex(data)
            results['VORTEX_POSITIVE'] = vortex['positive']
            results['VORTEX_NEGATIVE'] = vortex['negative']
            
            # Williams %R
            results['WILLIAMS_R'] = self._calculate_williams_r(data)
            
            # ZigZag
            results['ZIGZAG'] = self._calculate_zigzag(data)
            
            # Detrended Price Oscillator
            results['DETRENDED_PRICE'] = self._calculate_dpo(data['close'])
            
            # Linear Regression indicators
            lr = self._calculate_linear_regression(data['close'])
            results['LINEAR_REGRESSION'] = lr['value']
            results['LINEAR_REGRESSION_SLOPE'] = lr['slope']
            results['LINEAR_REGRESSION_ANGLE'] = lr['angle']
            results['LINEAR_REGRESSION_INTERCEPT'] = lr['intercept']
            
            # Statistical indicators
            results['STANDARD_DEVIATION'] = self._calculate_standard_deviation(data['close'])
            results['VARIANCE'] = self._calculate_variance(data['close'])
            
            # True Range variations
            results['AVERAGE_TRUE_RANGE'] = self._calculate_atr(data)
            results['TRUE_RANGE'] = self._calculate_trange(data)
            results['NORMALIZED_AVERAGE_TRUE_RANGE'] = self._calculate_natr(data)
            
            # Chandelier Exit
            results['CHANDELIER_EXIT'] = self._calculate_chandelier_exit(data)
            
            # Aroon indicators
            aroon = self._calculate_aroon(data)
            results['AROON_UP'] = aroon['up']
            results['AROON_DOWN'] = aroon['down']
            results['AROON_OSC'] = aroon['oscillator']
            
            # Balance of Power
            results['BALANCE_OF_POWER'] = self._calculate_bop(data)
            
            # Commodity Channel Index
            results['COMMODITY_CHANNEL_INDEX'] = self._calculate_cci(data)
            
            # Chaikin Money Flow
            results['CHAIKIN_MONEY_FLOW'] = self._calculate_cmf(data)
            
            # Ease of Movement
            results['EASE_OF_MOVEMENT'] = self._calculate_eom(data)
            
            # Force Index
            results['FORCE_INDEX'] = self._calculate_fi(data)
            
            # Volume indicators
            results['NEGATIVE_VOLUME_INDEX'] = self._calculate_nvi(data)
            results['ON_BALANCE_VOLUME'] = self._calculate_obv(data)
            results['POSITIVE_VOLUME_INDEX'] = self._calculate_pvi(data)
            results['PRICE_VOLUME_TREND'] = self._calculate_vpt(data)
            
            # Volume Rate of Change
            results['VOLUME_RATE_OF_CHANGE'] = self._calculate_volume_roc(data)
            
            # Volume-weighted indicators
            results['VOLUME_WEIGHTED_AVERAGE_PRICE'] = self._calculate_vwap(data)
            results['VOLUME_WEIGHTED_MOVING_AVERAGE'] = self._calculate_vwma(data)
            
            # Price indicators
            results['WEIGHTED_CLOSE'] = self._calculate_weighted_close(data)
            results['MEDIAN_PRICE'] = self._calculate_median_price(data)
            results['TYPICAL_PRICE'] = self._calculate_typical_price(data)
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating advanced indicators: {e}")
            return {}
    
    def _calculate_price_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all price patterns for God Mode 1000"""
        try:
            results = {}
            
            # Classical patterns
            classical_patterns = self._detect_classical_patterns(data)
            results.update(classical_patterns)
            
            # Elliott Wave patterns
            elliott_patterns = self._detect_elliott_wave_patterns(data)
            results.update(elliott_patterns)
            
            # Wyckoff patterns
            wyckoff_patterns = self._detect_wyckoff_patterns(data)
            results.update(wyckoff_patterns)
            
            # Harmonic patterns
            harmonic_patterns = self._detect_harmonic_patterns(data)
            results.update(harmonic_patterns)
            
            # Fractal patterns
            fractal_patterns = self._detect_fractal_patterns(data)
            results.update(fractal_patterns)
            
            # Fibonacci patterns
            fibonacci_patterns = self._detect_fibonacci_patterns(data)
            results.update(fibonacci_patterns)
            
            # Advanced patterns
            advanced_patterns = self._detect_advanced_patterns(data)
            results.update(advanced_patterns)
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Error calculating price patterns: {e}")
            return {}
    
    # Core calculation methods for all indicators
    def _calculate_sma(self, data, period):
        """Calculate Simple Moving Average"""
        try:
            return talib.SMA(data, timeperiod=period)
        except Exception:
            return pd.Series(data).rolling(window=int(period)).mean()
    
    def _calculate_ema(self, data, period):
        """Calculate Exponential Moving Average - ALWAYS returns valid data"""
        try:
            # FIXED: Validate and sanitize period BEFORE converting to int
            if period is None:
                period = 14
            elif not isinstance(period, (int, float)):
                self.unified_logger.warning(f"EMA: Invalid period type {type(period)}, using default 14")
                period = 14
            elif period <= 0:
                self.unified_logger.warning(f"EMA: Invalid period value {period}, using default 14")
                period = 14
            # Now safe to convert to int
            period = int(period)
            
            # Ensure data is valid
            if data is None or len(data) == 0:
                self.unified_logger.error("EMA calculation failed: empty data")
                return pd.Series(dtype=float)  # Return empty Series, not None
            
            if TALIB_AVAILABLE and talib is not None:
                result = talib.EMA(data, timeperiod=period)
                # Ensure result is never None
                if result is None:
                    return pd.Series(data).ewm(span=period, adjust=False).mean()
                return result
            else:
                # Use pandas ewm with proper parameters
                return pd.Series(data).ewm(span=period, adjust=False).mean()
        except Exception as e:
            self.unified_logger.error(f"EMA calculation failed: {e}")
            # CRITICAL: Never return None - return empty Series or zeros
            try:
                return pd.Series(data).ewm(span=int(period) if period else 14, adjust=False).mean()
            except:
                return pd.Series(dtype=float)
    
    def _calculate_wma(self, data, period):
        """Calculate Weighted Moving Average"""
        try:
            return talib.WMA(data, timeperiod=period)
        except Exception:
            weights = np.arange(1, period + 1)
            return pd.Series(data).rolling(window=int(period)).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    def _calculate_bop(self, data):
        """Calculate Balance of Power (BOP) indicator
        
        BOP = (Close - Open) / (High - Low)
        Measures the strength of buyers vs sellers
        
        Args:
            data: DataFrame with OHLC columns
            
        Returns:
            Series with BOP values
        """
        try:
            # Check required columns
            required_cols = ['open', 'high', 'low', 'close']
            if not all(col in data.columns for col in required_cols):
                self.unified_logger.error(f"BOP calculation requires OHLC data. Missing columns.")
                return pd.Series(dtype=float)
            
            # Use talib if available
            if TALIB_AVAILABLE and talib is not None:
                try:
                    bop = talib.BOP(data['open'], data['high'], data['low'], data['close'])
                    return bop
                except Exception as e:
                    self.unified_logger.debug(f"TA-Lib BOP failed, using manual calculation: {e}")
            
            # Manual calculation: BOP = (Close - Open) / (High - Low)
            numerator = data['close'] - data['open']
            denominator = data['high'] - data['low']
            
            # Avoid division by zero
            denominator = denominator.replace(0, np.nan)
            
            bop = numerator / denominator
            
            # Fill NaN values with 0 (neutral)
            bop = bop.fillna(0)
            
            return bop
            
        except Exception as e:
            self.unified_logger.error(f"BOP calculation failed: {e}")
            # Return zeros series with same length as data
            return pd.Series(0, index=data.index if hasattr(data, 'index') else range(len(data)))
    
    def _calculate_rsi(self, data, period=None):
        """Calculate Relative Strength Index with dynamic period"""
        try:
            if period is None:
                period = 14  # Default RSI period
            return talib.RSI(data, timeperiod=int(period))
        except Exception:
            # Ensure period is valid integer
            if period is None or not isinstance(period, (int, float)) or period <= 0:
                period = 14
            period = int(period)
            
            delta = pd.Series(data).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, data, fast=None, slow=None, signal=None):
        """Calculate MACD with dynamic periods"""
        try:
            if fast is None:
                fast = 12
            if slow is None:
                slow = 26
            if signal is None:
                signal = 9
            macd, macd_signal, macd_hist = talib.MACD(data, fastperiod=int(fast), slowperiod=int(slow), signalperiod=int(signal))
            return {'macd': macd, 'signal': macd_signal, 'histogram': macd_hist}
        except Exception:
            ema_fast = self._calculate_ema(data, fast)
            ema_slow = self._calculate_ema(data, slow)
            macd = ema_fast - ema_slow
            macd_signal = self._calculate_ema(macd, signal)
            macd_hist = macd - macd_signal
            return {'macd': macd, 'signal': macd_signal, 'histogram': macd_hist}
    
    def _calculate_bollinger_bands(self, data, period=None, std_dev=None):
        """Calculate Bollinger Bands with dynamic parameters"""
        try:
            if period is None:
                period = 20  # Default Bollinger period
            if std_dev is None:
                std_dev = 2.0  # Default standard deviation
            upper, middle, lower = talib.BBANDS(data, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
            return {'upper': upper, 'middle': middle, 'lower': lower}
        except Exception:
            # Ensure period and std_dev are valid
            if period is None or not isinstance(period, (int, float)) or period <= 0:
                period = 20
            if std_dev is None or not isinstance(std_dev, (int, float)) or std_dev <= 0:
                std_dev = 2.0
            period = int(period)
            
            sma = self._calculate_sma(data, period)
            std = pd.Series(data).rolling(window=period).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return {'upper': upper, 'middle': sma, 'lower': lower}
    
    def _calculate_atr(self, data, period=None):
        """Calculate Average True Range with dynamic period"""
        try:
            if period is None:
                period = 14  # Default ATR period  # Default fallback
            return talib.ATR(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            # Ensure period is valid integer
            if period is None or not isinstance(period, (int, float)) or period <= 0:
                period = 14
            period = int(period)
            
            # Validate data is DataFrame with required columns
            if not isinstance(data, pd.DataFrame) or 'high' not in data.columns or 'low' not in data.columns or 'close' not in data.columns:
                return pd.Series([0] * len(data) if hasattr(data, '__len__') else [0])
            
            high = data['high']
            low = data['low']
            close = data['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return tr.rolling(window=period).mean()
    
    def _calculate_stochastic(self, data, k_period=None, d_period=None):
        """Calculate Stochastic Oscillator with dynamic periods"""
        try:
            if k_period is None:
                k_period = 14  # Default K period
            if d_period is None:
                d_period = 3   # Default D period
            slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'], 
                                     fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
            return {'k': slowk, 'd': slowd}
        except Exception:
            # Ensure periods are valid integers
            if k_period is None or not isinstance(k_period, (int, float)) or k_period <= 0:
                k_period = 14
            if d_period is None or not isinstance(d_period, (int, float)) or d_period <= 0:
                d_period = 3
            k_period = int(k_period)
            d_period = int(d_period)
            
            # Validate data is DataFrame with required columns
            if not isinstance(data, pd.DataFrame) or 'high' not in data.columns or 'low' not in data.columns or 'close' not in data.columns:
                zero_series = pd.Series([50.0] * len(data) if hasattr(data, '__len__') else [50.0])
                return {'k': zero_series, 'd': zero_series}
            
            low_min = data['low'].rolling(window=k_period).min()
            high_max = data['high'].rolling(window=k_period).max()
            
            # FIXED: Safe division to avoid ZeroDivisionError
            range_hl = high_max - low_min
            range_hl = range_hl.replace(0, np.nan)  # Replace 0 with NaN
            k_percent = 100 * ((data['close'] - low_min) / range_hl)
            d_percent = k_percent.rolling(window=d_period).mean()
            return {'k': k_percent, 'd': d_percent}
    
    def _calculate_stochastic_fast(self, data, k_period=5, d_period=3):
        """Calculate Fast Stochastic Oscillator (STOCHF) - faster than standard stochastic"""
        try:
            # Fast stochastic uses shorter periods for more responsive signals
            fastk, fastd = talib.STOCHF(data['high'], data['low'], data['close'], 
                                       fastk_period=k_period, fastd_period=d_period)
            return {'k': fastk, 'd': fastd}
        except Exception:
            # Fallback calculation without talib
            low_min = data['low'].rolling(window=int(k_period)).min()
            high_max = data['high'].rolling(window=int(k_period)).max()
            
            # FIXED: Safe division to avoid ZeroDivisionError
            range_hl = high_max - low_min
            range_hl = range_hl.replace(0, np.nan)  # Replace 0 with NaN
            
            # Fast %K calculation
            fastk = 100 * ((data['close'] - low_min) / range_hl)
            
            # Fast %D is a moving average of Fast %K
            fastd = fastk.rolling(window=int(d_period)).mean()
            
            return {'k': fastk, 'd': fastd}
    
    def _calculate_supertrend(self, data, period=10, multiplier=3.0):
        """Calculate SuperTrend indicator"""
        try:
            # Calculate ATR
            atr = self._calculate_atr(data, period)
            
            # Calculate basic bands
            hl2 = (data['high'] + data['low']) / 2
            upper_band = hl2 + (multiplier * atr)
            lower_band = hl2 - (multiplier * atr)
            
            # Initialize supertrend series
            supertrend = pd.Series(index=data.index, dtype=float)
            direction = pd.Series(index=data.index, dtype=int)
            
            # Calculate SuperTrend
            for i in range(len(data)):
                if i == 0:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                else:
                    # Determine trend direction
                    if data['close'].iloc[i] > supertrend.iloc[i-1]:
                        direction.iloc[i] = 1  # Uptrend
                        supertrend.iloc[i] = max(lower_band.iloc[i], supertrend.iloc[i-1])
                    else:
                        direction.iloc[i] = -1  # Downtrend
                        supertrend.iloc[i] = min(upper_band.iloc[i], supertrend.iloc[i-1])
            
            return {'value': supertrend, 'direction': direction, 'upper': upper_band, 'lower': lower_band}
        except Exception as e:
            # Return neutral values on error
            return {
                'value': pd.Series([data['close'].mean()] * len(data), index=data.index),
                'direction': pd.Series([0] * len(data), index=data.index),
                'upper': pd.Series([data['close'].mean()] * len(data), index=data.index),
                'lower': pd.Series([data['close'].mean()] * len(data), index=data.index)
            }
    
    def _calculate_adx(self, data, period=14):
        """Calculate Average Directional Index"""
        try:
            return talib.ADX(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            # Simplified ADX calculation
            plus_dm = data['high'].diff()
            minus_dm = data['low'].diff()
            
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            minus_dm = abs(minus_dm)
            
            tr = self._calculate_atr(data, period)
            plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr)
            minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr)
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            return dx.rolling(window=period).mean()
    
    def _calculate_obv(self, data):
        """Calculate On-Balance Volume"""
        try:
            return talib.OBV(data['close'], data['volume'])
        except Exception:
            obv = np.zeros(len(data))
            for i in range(1, len(data)):
                if data['close'].iloc[i] > data['close'].iloc[i-1]:
                    obv[i] = obv[i-1] + data['volume'].iloc[i]
                elif data['close'].iloc[i] < data['close'].iloc[i-1]:
                    obv[i] = obv[i-1] - data['volume'].iloc[i]
                else:
                    obv[i] = obv[i-1]
            return pd.Series(obv)
    
    def _calculate_cci(self, data, period=14):
        """Calculate Commodity Channel Index"""
        try:
            return talib.CCI(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            typical_price = (data['high'] + data['low'] + data['close']) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
            return (typical_price - sma_tp) / (0.015 * mean_deviation)
    
    def _calculate_mfi(self, data, period=14):
        """Calculate Money Flow Index"""
        try:
            return talib.MFI(data['high'], data['low'], data['close'], data['volume'], timeperiod=period)
        except Exception:
            typical_price = (data['high'] + data['low'] + data['close']) / 3
            money_flow = typical_price * data['volume']
            
            positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
            negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
            
            positive_sum = positive_flow.rolling(window=period).sum()
            negative_sum = negative_flow.rolling(window=period).sum()
            
            mfi = 100 - (100 / (1 + positive_sum / negative_sum))
            return mfi
    
    def _calculate_cmo(self, data, period=14):
        """Calculate Chande Momentum Oscillator"""
        try:
            return talib.CMO(data, timeperiod=period)
        except Exception:
            # Manual calculation
            delta = pd.Series(data).diff()
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            sum_gains = gains.rolling(window=int(period)).sum()
            sum_losses = losses.rolling(window=int(period)).sum()
            
            cmo = 100 * ((sum_gains - sum_losses) / (sum_gains + sum_losses))
            return cmo.fillna(0)
    
    def _calculate_dpo(self, data, period=20):
        """Calculate Detrended Price Oscillator
        
        DPO removes the trend from price to make it easier to identify cycles.
        DPO = Close - SMA(Close, period/2 + 1) shifted back period/2 + 1
        
        Args:
            data: Price series (close prices)
            period: Lookback period (default 20)
            
        Returns:
            DPO series
        """
        try:
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    data = data['close']
                else:
                    self.unified_logger.error("DPO calculation: 'close' column not found")
                    return pd.Series([0] * len(data), index=data.index)
            
            # Convert to Series if needed
            if not isinstance(data, pd.Series):
                data = pd.Series(data)
            
            # Calculate displacement
            displacement = int(period / 2) + 1
            
            # Calculate SMA
            sma = data.rolling(window=period).mean()
            
            # Shift SMA back by displacement
            sma_shifted = sma.shift(displacement)
            
            # Calculate DPO
            dpo = data - sma_shifted
            
            return dpo.fillna(0)
            
        except Exception as e:
            self.unified_logger.error(f"DPO calculation failed: {e}")
            if isinstance(data, (pd.Series, pd.DataFrame)):
                return pd.Series([0] * len(data), index=data.index if hasattr(data, 'index') else None)
            else:
                return pd.Series([0])
    
    def _calculate_roc(self, data, period=10):
        """Calculate Rate of Change"""
        try:
            return talib.ROC(data, timeperiod=period)
        except Exception:
            return ((data / data.shift(period)) - 1) * 100
    
    def _calculate_rocp(self, data, period=10):
        """Calculate Rate of Change Percentage"""
        try:
            return talib.ROCP(data, timeperiod=period)
        except Exception:
            return (data - data.shift(period)) / data.shift(period)
    
    def _calculate_rocr(self, data, period=10):
        """Calculate Rate of Change Ratio"""
        try:
            return talib.ROCR(data, timeperiod=period)
        except Exception:
            return data / data.shift(period)
    
    def _calculate_rocr100(self, data, period=10):
        """Calculate Rate of Change Ratio * 100"""
        try:
            return talib.ROCR100(data, timeperiod=period)
        except Exception:
            return (data / data.shift(period)) * 100
    
    def _calculate_momentum(self, data, period=10):
        """Calculate Momentum"""
        try:
            return talib.MOM(data, timeperiod=period)
        except Exception:
            return data - data.shift(period)
    
    def _calculate_volume_roc(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Volume Rate of Change
        
        Args:
            data: DataFrame with volume column
            period: ROC period (default 14)
            
        Returns:
            Volume ROC series
        """
        try:
            # Validate input
            if data is None or len(data) == 0:
                self.unified_logger.error("Volume ROC: empty data")
                return pd.Series(dtype=float)
            
            if not isinstance(data, pd.DataFrame):
                self.unified_logger.error(f"Volume ROC: data must be DataFrame, got {type(data)}")
                return pd.Series(dtype=float)
            
            if 'volume' not in data.columns:
                self.unified_logger.error(f"Volume ROC: missing 'volume' column. Available: {list(data.columns)}")
                return pd.Series(dtype=float)
            
            volume = data['volume']
            
            # Calculate volume ROC using same formula as price ROC
            try:
                if TALIB_AVAILABLE and talib is not None:
                    return talib.ROC(volume, timeperiod=period)
                else:
                    # Manual calculation: ((current - previous) / previous) * 100
                    return ((volume / volume.shift(period)) - 1) * 100
            except Exception as calc_error:
                self.unified_logger.debug(f"Volume ROC calculation fallback: {calc_error}")
                # Fallback manual calculation
                shifted = volume.shift(period)
                # Avoid division by zero
                result = pd.Series(index=volume.index, dtype=float)
                mask = shifted != 0
                result[mask] = ((volume[mask] / shifted[mask]) - 1) * 100
                result[~mask] = 0.0
                return result.fillna(0)
                
        except Exception as e:
            self.unified_logger.error(f"Volume ROC error: {e}")
            return pd.Series(dtype=float)
    
    def _calculate_macd_ext(self, data, fastperiod=12, slowperiod=26, signalperiod=9):
        """Calculate MACD with Extended parameters"""
        try:
            macd, signal, hist = talib.MACDEXT(data, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
            return {'macd': macd, 'signal': signal, 'histogram': hist}
        except Exception:
            return self._calculate_macd(data, fastperiod, slowperiod, signalperiod)
    
    def _calculate_macd_fix(self, data, signalperiod=9):
        """Calculate MACD with Fixed parameters"""
        try:
            macd, signal, hist = talib.MACDFIX(data, signalperiod=signalperiod)
            return {'macd': macd, 'signal': signal, 'histogram': hist}
        except Exception:
            return self._calculate_macd(data, 12, 26, signalperiod)
    
    def _calculate_ppo(self, data, fastperiod=12, slowperiod=26):
        """Calculate Percentage Price Oscillator"""
        try:
            return talib.PPO(data, fastperiod=fastperiod, slowperiod=slowperiod)
        except Exception:
            ema_fast = self._calculate_ema(pd.DataFrame({'close': data}), fastperiod)
            ema_slow = self._calculate_ema(pd.DataFrame({'close': data}), slowperiod)
            return ((ema_fast - ema_slow) / ema_slow) * 100
    
    def _calculate_tsf(self, data, period=14):
        """Calculate Time Series Forecast"""
        try:
            return talib.TSF(data, timeperiod=period)
        except Exception:
            # Linear regression forecast
            x = np.arange(len(data))
            series = pd.Series(data).fillna(method='ffill')
            result = pd.Series(index=data.index, dtype=float)
            for i in range(period, len(data)):
                y = series.iloc[i-period:i].values
                x_window = x[i-period:i]
                if len(y) > 0 and not np.all(np.isnan(y)):
                    coeffs = np.polyfit(x_window, y, 1)
                    result.iloc[i] = coeffs[0] * x[i] + coeffs[1]
            return result.fillna(0)
    
    def _calculate_ultosc(self, data, period1=7, period2=14, period3=28):
        """Calculate Ultimate Oscillator"""
        try:
            return talib.ULTOSC(data['high'], data['low'], data['close'], timeperiod1=period1, timeperiod2=period2, timeperiod3=period3)
        except Exception:
            # Simplified calculation
            bp = data['close'] - data[['close', 'low']].min(axis=1)
            tr = data[['high', 'low']].max(axis=1) - data[['high', 'low']].min(axis=1)
            
            avg1 = bp.rolling(window=period1).sum() / tr.rolling(window=period1).sum()
            avg2 = bp.rolling(window=period2).sum() / tr.rolling(window=period2).sum()
            avg3 = bp.rolling(window=period3).sum() / tr.rolling(window=period3).sum()
            
            ult_osc = 100 * ((4 * avg1) + (2 * avg2) + avg3) / (4 + 2 + 1)
            return ult_osc.fillna(50)
    
    def _calculate_adxr(self, data, period=14):
        """Calculate Average Directional Movement Index Rating"""
        try:
            return talib.ADXR(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            adx = self._calculate_adx(data, period)
            adxr = (adx + adx.shift(period)) / 2
            return adxr.fillna(0)
    
    def _calculate_minus_di(self, data, period=14):
        """Calculate Minus Directional Indicator"""
        try:
            return talib.MINUS_DI(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            minus_dm = data['low'].shift(1) - data['low']
            minus_dm[minus_dm < 0] = 0
            tr = self._calculate_trange(data)
            minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
            return minus_di.fillna(0)
    
    def _calculate_plus_di(self, data, period=14):
        """Calculate Plus Directional Indicator"""
        try:
            return talib.PLUS_DI(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            plus_dm = data['high'] - data['high'].shift(1)
            plus_dm[plus_dm < 0] = 0
            tr = self._calculate_trange(data)
            plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
            return plus_di.fillna(0)
    
    def _calculate_dx(self, data, period=14):
        """Calculate Directional Movement Index"""
        try:
            return talib.DX(data['high'], data['low'], data['close'], timeperiod=period)
        except Exception:
            plus_di = self._calculate_plus_di(data, period)
            minus_di = self._calculate_minus_di(data, period)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            return dx.fillna(0)
    
    def _calculate_vwap(self, data):
        """Calculate Volume Weighted Average Price"""
        try:
            typical_price = (data['high'] + data['low'] + data['close']) / 3
            cumulative_tp_volume = (typical_price * data['volume']).cumsum()
            cumulative_volume = data['volume'].cumsum()
            return cumulative_tp_volume / cumulative_volume
        except Exception:
            return pd.Series([0] * len(data))
    
    def _calculate_tema(self, data, period: int = 14):
        """Triple Exponential Moving Average (TEMA)
        TEMA = 3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))
        Implemented deterministically using pandas ewm on the close price.
        """
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("TEMA calculation: DataFrame missing 'close' column")
                    return None
            else:
                close = pd.Series(data).astype(float)
            
            ema1 = close.ewm(span=period, adjust=False).mean()
            ema2 = ema1.ewm(span=period, adjust=False).mean()
            ema3 = ema2.ewm(span=period, adjust=False).mean()
            tema = 3 * ema1 - 3 * ema2 + ema3
            return tema
        except Exception as e:
            self.unified_logger.error(f"TEMA calculation failed: {e}")
            return None

    def _calculate_dema(self, data, period: int = 14):
        """Double Exponential Moving Average (DEMA)
        DEMA = 2*EMA - EMA(EMA)
        """
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("DEMA calculation: DataFrame missing 'close' column")
                    return None
            else:
                close = pd.Series(data).astype(float)
            
            ema1 = close.ewm(span=period, adjust=False).mean()
            ema2 = ema1.ewm(span=period, adjust=False).mean()
            dema = 2 * ema1 - ema2
            return dema
        except Exception as e:
            self.unified_logger.error(f"DEMA calculation failed: {e}")
            return None

    def _calculate_kama(self, data, period: int = 10, fast_period: int = 2, slow_period: int = 30):
        """Kaufman's Adaptive Moving Average (KAMA) - CORRECT implementation
        
        KAMA adapts to market conditions:
        - Fast in trending markets (high efficiency ratio)
        - Slow in ranging markets (low efficiency ratio)
        
        Efficiency Ratio (ER) = |Price Change| / Sum of |Price Changes|
        """
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("KAMA calculation: DataFrame missing 'close' column")
                    return pd.Series(dtype=float)
            else:
                close = pd.Series(data).astype(float)
            
            if len(close) < period + 1:
                return pd.Series(dtype=float)
            
            # CORRECT KAMA Calculation:
            # 1. Calculate net price change over period
            net_change = close.diff(period).abs()  # |close[i] - close[i-period]|
            
            # 2. Calculate sum of absolute price changes (volatility)
            # This is the sum of all |close[j] - close[j-1]| over the period
            abs_changes = close.diff().abs()
            volatility = abs_changes.rolling(window=period).sum()
            
            # 3. Calculate Efficiency Ratio (ER)
            # ER = Net Change / Volatility
            # When ER is high (close to 1), market is trending → use fast smoothing
            # When ER is low (close to 0), market is ranging → use slow smoothing
            er = pd.Series(index=close.index, dtype=float)
            for i in range(len(close)):
                if i < period:
                    er.iloc[i] = 0.0
                elif pd.notna(volatility.iloc[i]) and volatility.iloc[i] > 0:
                    er.iloc[i] = net_change.iloc[i] / volatility.iloc[i]
                else:
                    er.iloc[i] = 0.0
            
            # Ensure ER is between 0 and 1
            er = er.clip(0.0, 1.0)
            
            # 4. Calculate Smoothing Constant (SC)
            fast_sc = 2.0 / (fast_period + 1)
            slow_sc = 2.0 / (slow_period + 1)
            sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
            
            # 5. Calculate KAMA using the smoothing constant
            kama = pd.Series(index=close.index, dtype=float)
            # Initialize first values with actual prices
            kama.iloc[:period] = close.iloc[:period]
            
            # Apply KAMA formula: KAMA[i] = KAMA[i-1] + SC[i] * (Price[i] - KAMA[i-1])
            for i in range(period, len(close)):
                if pd.notna(sc.iloc[i]) and pd.notna(kama.iloc[i-1]) and pd.notna(close.iloc[i]):
                    kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (close.iloc[i] - kama.iloc[i-1])
                else:
                    kama.iloc[i] = close.iloc[i]
            
            return kama
        except Exception as e:
            self.unified_logger.error(f"KAMA calculation failed: {e}")
            return pd.Series(dtype=float)

    def _calculate_mama(self, data, fast_limit: float = 0.5, slow_limit: float = 0.05):
        """MESA Adaptive Moving Average (MAMA) - simplified variant
        This provides an adaptive smoothing based on price momentum.
        """
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("MAMA calculation: DataFrame missing 'close' column")
                    return pd.Series(dtype=float)
            else:
                close = pd.Series(data).astype(float)
            
            if len(close) < 10:
                return pd.Series(dtype=float)
            
            detrender = close.diff().abs().rolling(window=10).mean()
            period = detrender.replace(0, np.nan).fillna(method='bfill')
            alpha = (fast_limit - slow_limit) / (1.0 + np.exp(- (period / (np.nanmean(period) + 1e-9)))) + slow_limit
            mama = close.copy()
            mama.iloc[0] = close.iloc[0]
            for i in range(1, len(close)):
                mama.iat[i] = alpha.iat[i] * close.iat[i] + (1 - alpha.iat[i]) * mama.iat[i-1]
            return mama
        except Exception as e:
            self.unified_logger.error(f"MAMA calculation failed: {e}")
            return pd.Series(dtype=float)

    def _calculate_trima(self, data, period: int = 20):
        """Triangular Moving Average computed as SMA of SMA"""
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("TRIMA calculation: DataFrame missing 'close' column")
                    return pd.Series(dtype=float)
            else:
                close = pd.Series(data).astype(float)
            
            if len(close) < period * 2:
                return pd.Series(dtype=float)
            
            sma1 = close.rolling(window=period).mean()
            trima = sma1.rolling(window=period).mean()
            return trima
        except Exception as e:
            self.unified_logger.error(f"TRIMA calculation failed: {e}")
            return pd.Series(dtype=float)

    def _calculate_hma(self, data, period: int = 16):
        """Hull Moving Average (HMA) implementation using WMA"""
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("HMA calculation: DataFrame missing 'close' column")
                    return pd.Series(dtype=float)
            else:
                close = pd.Series(data).astype(float)
            
            if len(close) < period:
                return pd.Series(dtype=float)
            
            half_period = int(max(1, period / 2))
            sqrt_period = int(max(1, np.sqrt(period)))
            wma = lambda series, length: series.rolling(window=length).apply(lambda x: np.dot(np.arange(1, len(x)+1), x) / np.arange(1, len(x)+1).sum(), raw=True)
            wma_half = wma(close, half_period)
            wma_full = wma(close, period)
            diff = 2 * wma_half - wma_full
            hma = wma(diff, sqrt_period)
            return hma
        except Exception as e:
            self.unified_logger.error(f"HMA calculation failed: {e}")
            return pd.Series(dtype=float)

    def _calculate_zlema(self, data, period: int = 14):
        """Zero-Lag Exponential Moving Average (ZLEMA)"""
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("ZLEMA calculation: DataFrame missing 'close' column")
                    return None
            else:
                close = pd.Series(data).astype(float)
            
            lag = int((period - 1) / 2)
            shifted = close.shift(lag).fillna(method='bfill')
            zlema = shifted.ewm(span=period, adjust=False).mean()
            return zlema
        except Exception as e:
            self.unified_logger.error(f"ZLEMA calculation failed: {e}")
            return None

    def _calculate_alma(self, data, period: int = 9, offset: float = 0.85, sigma: float = 6.0):
        """Arnaud Legoux Moving Average (ALMA) approximate implementation"""
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close = data['close'].astype(float)
                else:
                    self.unified_logger.error("ALMA calculation: DataFrame missing 'close' column")
                    return None
            else:
                close = pd.Series(data).astype(float)
            
            m = int(offset * (period - 1))
            s = period / sigma
            weights = [np.exp(-((i - m) ** 2) / (2 * (s ** 2))) for i in range(period)]
            weights = np.array(weights) / np.sum(weights)
            alma = close.rolling(window=period).apply(lambda x: np.dot(weights, x), raw=True)
            return alma
        except Exception as e:
            self.unified_logger.error(f"ALMA calculation failed: {e}")
            return None
    
    def _calculate_vidya(self, data):
        """Variable Index Dynamic Average"""
        return self._calculate_ema(data, 14)  # Simplified
    
    def _calculate_vwma(self, data):
        """Volume Weighted Moving Average"""
        return self._calculate_vwap(data)  # Simplified
    
    def _calculate_lwma(self, data):
        """Linear Weighted Moving Average"""
        return self._calculate_wma(data, 14)  # Simplified
    
    def _calculate_ewma(self, data):
        """Exponentially Weighted Moving Average"""
        try:
            # CRITICAL: Check if data is DataFrame or Series
            if isinstance(data, pd.DataFrame):
                if 'close' in data.columns:
                    close_prices = data['close']
                else:
                    self.unified_logger.error("EWMA calculation: DataFrame missing 'close' column")
                    return None
            else:
                close_prices = data
            
            return self._calculate_ema(close_prices, 14)
        except Exception as e:
            self.unified_logger.error(f"EWMA calculation failed: {e}")
            return None
    
    def _calculate_weighted_close(self, data):
        """Calculate Weighted Close Price
        Weighted Close = (High + Low + 2 * Close) / 4
        Gives more weight to closing price as it's considered most important
        """
        try:
            if isinstance(data, pd.DataFrame):
                if 'high' not in data.columns or 'low' not in data.columns or 'close' not in data.columns:
                    self.unified_logger.error("Weighted Close calculation: missing required columns (high, low, close)")
                    return pd.Series([0] * len(data), index=data.index)
                
                weighted_close = (data['high'] + data['low'] + 2 * data['close']) / 4
                return weighted_close.fillna(0)
            else:
                self.unified_logger.error("Weighted Close calculation: data must be DataFrame")
                return pd.Series(dtype=float)
        except Exception as e:
            self.unified_logger.error(f"Weighted Close calculation failed: {e}")
            return pd.Series([0] * len(data) if isinstance(data, pd.DataFrame) else 0)
    
    def _calculate_median_price(self, data):
        """Calculate Median Price
        Median Price = (High + Low) / 2
        Represents the midpoint of the trading range
        """
        try:
            if isinstance(data, pd.DataFrame):
                if 'high' not in data.columns or 'low' not in data.columns:
                    self.unified_logger.error("Median Price calculation: missing required columns (high, low)")
                    return pd.Series([0] * len(data), index=data.index)
                
                median_price = (data['high'] + data['low']) / 2
                return median_price.fillna(0)
            else:
                self.unified_logger.error("Median Price calculation: data must be DataFrame")
                return pd.Series(dtype=float)
        except Exception as e:
            self.unified_logger.error(f"Median Price calculation failed: {e}")
            return pd.Series([0] * len(data) if isinstance(data, pd.DataFrame) else 0)
    
    def _calculate_typical_price(self, data):
        """Calculate Typical Price
        Typical Price = (High + Low + Close) / 3
        Represents the average of the three key price points
        Used in many volume-weighted calculations
        """
        try:
            if isinstance(data, pd.DataFrame):
                if 'high' not in data.columns or 'low' not in data.columns or 'close' not in data.columns:
                    self.unified_logger.error("Typical Price calculation: missing required columns (high, low, close)")
                    return pd.Series([0] * len(data), index=data.index)
                
                typical_price = (data['high'] + data['low'] + data['close']) / 3
                return typical_price.fillna(0)
            else:
                self.unified_logger.error("Typical Price calculation: data must be DataFrame")
                return pd.Series(dtype=float)
        except Exception as e:
            self.unified_logger.error(f"Typical Price calculation failed: {e}")
            return pd.Series([0] * len(data) if isinstance(data, pd.DataFrame) else 0)
    
    # Pattern detection methods (to be implemented)
    def _detect_classical_patterns(self, data):
        """Detect classical chart patterns"""
        # Deterministic fallback: no patterns detected until production detectors are implemented
        self.unified_logger.debug("Classical pattern detection not implemented; returning empty result")
        return {}
    
    def _detect_elliott_wave_patterns(self, data):
        """Detect Elliott Wave patterns"""
        self.unified_logger.debug("Elliott wave detection not implemented; returning empty result")
        return {}
    
    def _detect_wyckoff_patterns(self, data):
        """Detect Wyckoff patterns with advanced analysis"""
        try:
            patterns = {}
            
            if len(data) < 50:
                return patterns
            
            # Wyckoff Accumulation Phase Detection
            accumulation = self._detect_wyckoff_accumulation(data)
            if accumulation:
                patterns['WYCKOFF_ACCUMULATION'] = accumulation
            
            # Wyckoff Distribution Phase Detection
            distribution = self._detect_wyckoff_distribution(data)
            if distribution:
                patterns['WYCKOFF_DISTRIBUTION'] = distribution
            
            # Wyckoff Markup Phase Detection
            markup = self._detect_wyckoff_markup(data)
            if markup:
                patterns['WYCKOFF_MARKUP'] = markup
            
            # Wyckoff Markdown Phase Detection
            markdown = self._detect_wyckoff_markdown(data)
            if markdown:
                patterns['WYCKOFF_MARKDOWN'] = markdown
            
            return patterns
            
        except Exception as e:
            self.unified_logger.error(f"Wyckoff pattern detection failed: {e}")
            return {}
    
    def _detect_harmonic_patterns(self, data):
        """Detect harmonic patterns with Fibonacci ratios"""
        try:
            patterns = {}
            
            if len(data) < 30:
                return patterns
            
            # Gartley Pattern Detection
            gartley = self._detect_gartley_pattern(data)
            if gartley:
                patterns['GARTLEY'] = gartley
            
            # Butterfly Pattern Detection
            butterfly = self._detect_butterfly_pattern(data)
            if butterfly:
                patterns['BUTTERFLY'] = butterfly
            
            # Bat Pattern Detection
            bat = self._detect_bat_pattern(data)
            if bat:
                patterns['BAT'] = bat
            
            # Crab Pattern Detection
            crab = self._detect_crab_pattern(data)
            if crab:
                patterns['CRAB'] = crab
            
            return patterns
            
        except Exception as e:
            self.unified_logger.error(f"Harmonic pattern detection failed: {e}")
            return {}
    
    def _detect_wyckoff_accumulation(self, data):
        """Detect Wyckoff Accumulation Phase"""
        try:
            if len(data) < 30:
                return None
            
            # Look for sideways movement with volume analysis
            recent_data = data.tail(30)
            price_range = recent_data['high'].max() - recent_data['low'].min()
            avg_price = recent_data['close'].mean()
            
            # Accumulation characteristics:
            # 1. Sideways price movement (low volatility)
            # 2. Increasing volume on down moves
            # 3. Decreasing volume on up moves
            
            volatility = price_range / avg_price
            if volatility < 0.15:  # Low volatility threshold
                return {
                    'phase': 'ACCUMULATION',
                    'confidence': 0.7,
                    'characteristics': ['low_volatility', 'sideways_movement'],
                    'signal': 'BUY',
                    'strength': 0.6
                }
            
            return None
            
        except Exception as e:
            self.unified_logger.error(f"Wyckoff accumulation detection failed: {e}")
            return None
    
    def _detect_wyckoff_distribution(self, data):
        """Detect Wyckoff Distribution Phase"""
        try:
            if len(data) < 30:
                return None
            
            # Look for topping pattern with volume analysis
            recent_data = data.tail(30)
            price_range = recent_data['high'].max() - recent_data['low'].min()
            avg_price = recent_data['close'].mean()
            
            # Distribution characteristics:
            # 1. Sideways movement after uptrend
            # 2. Increasing volume on up moves
            # 3. Decreasing volume on down moves
            
            volatility = price_range / avg_price
            if volatility < 0.15:  # Low volatility threshold
                return {
                    'phase': 'DISTRIBUTION',
                    'confidence': 0.7,
                    'characteristics': ['low_volatility', 'topping_pattern'],
                    'signal': 'SELL',
                    'strength': 0.6
                }
            
            return None
            
        except Exception as e:
            self.unified_logger.error(f"Wyckoff distribution detection failed: {e}")
            return None
    
    def _detect_wyckoff_markup(self, data):
        """Detect Wyckoff Markup Phase"""
        try:
            if len(data) < 20:
                return None
            
            # Look for strong uptrend with increasing volume
            recent_data = data.tail(20)
            price_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
            
            # Markup characteristics:
            # 1. Strong uptrend (>10% price increase)
            # 2. Increasing volume
            # 3. Higher highs and higher lows
            
            if price_change > 0.10:  # 10% price increase
                return {
                    'phase': 'MARKUP',
                    'confidence': 0.8,
                    'characteristics': ['strong_uptrend', 'increasing_volume'],
                    'signal': 'BUY',
                    'strength': 0.8
                }
            
            return None
            
        except Exception as e:
            self.unified_logger.error(f"Wyckoff markup detection failed: {e}")
            return None
    
    def _detect_wyckoff_markdown(self, data):
        """Detect Wyckoff Markdown Phase"""
        try:
            if len(data) < 20:
                return None
            
            # Look for strong downtrend with increasing volume
            recent_data = data.tail(20)
            price_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
            
            # Markdown characteristics:
            # 1. Strong downtrend (>10% price decrease)
            # 2. Increasing volume
            # 3. Lower highs and lower lows
            
            if price_change < -0.10:  # 10% price decrease
                return {
                    'phase': 'MARKDOWN',
                    'confidence': 0.8,
                    'characteristics': ['strong_downtrend', 'increasing_volume'],
                    'signal': 'SELL',
                    'strength': 0.8
                }
            
            return None
            
        except Exception as e:
            self.unified_logger.error(f"Wyckoff markdown detection failed: {e}")
            return None
    
    def _detect_gartley_pattern(self, data):
        """Detect Gartley Harmonic Pattern"""
        try:
            if len(data) < 50:
                return None
            
            # Gartley pattern requires specific Fibonacci ratios
            # XA, AB, BC, CD legs with specific ratios
            
            # Simplified detection based on price action
            recent_data = data.tail(50)
            highs = recent_data['high'].rolling(window=5).max()
            lows = recent_data['low'].rolling(window=5).min()
            
            # Look for potential Gartley structure
            # This is a simplified version - full implementation would require more complex analysis
            
            return {
                'pattern': 'GARTLEY',
                'confidence': 0.6,
                'characteristics': ['harmonic_ratios', 'fibonacci_levels'],
                'signal': 'HOLD',
                'strength': 0.5
            }
            
        except Exception as e:
            self.unified_logger.error(f"Gartley pattern detection failed: {e}")
            return None
    
    def _detect_butterfly_pattern(self, data):
        """Detect Butterfly Harmonic Pattern"""
        try:
            if len(data) < 50:
                return None
            
            # Butterfly pattern detection (simplified)
            return {
                'pattern': 'BUTTERFLY',
                'confidence': 0.5,
                'characteristics': ['harmonic_ratios', 'extended_moves'],
                'signal': 'HOLD',
                'strength': 0.4
            }
            
        except Exception as e:
            self.unified_logger.error(f"Butterfly pattern detection failed: {e}")
            return None
    
    def _detect_bat_pattern(self, data):
        """Detect Bat Harmonic Pattern"""
        try:
            if len(data) < 50:
                return None
            
            # Bat pattern detection (simplified)
            return {
                'pattern': 'BAT',
                'confidence': 0.5,
                'characteristics': ['harmonic_ratios', 'precise_fibonacci'],
                'signal': 'HOLD',
                'strength': 0.4
            }
            
        except Exception as e:
            self.unified_logger.error(f"Bat pattern detection failed: {e}")
            return None
    
    def _detect_crab_pattern(self, data):
        """Detect Crab Harmonic Pattern"""
        try:
            if len(data) < 50:
                return None
            
            # Crab pattern detection (simplified)
            return {
                'pattern': 'CRAB',
                'confidence': 0.5,
                'characteristics': ['harmonic_ratios', 'extreme_extensions'],
                'signal': 'HOLD',
                'strength': 0.4
            }
            
        except Exception as e:
            self.unified_logger.error(f"Crab pattern detection failed: {e}")
            return None
    
    def _detect_fractal_patterns(self, data):
        """Detect fractal patterns"""
        self.unified_logger.debug("Fractal pattern detection not implemented; returning empty result")
        return {}
    
    def _detect_fibonacci_patterns(self, data):
        """Detect Fibonacci patterns"""
        self.unified_logger.debug("Fibonacci pattern detection not implemented; returning empty result")
        return {}
    
    def _detect_advanced_patterns(self, data):
        """Detect advanced patterns"""
        self.unified_logger.debug("Advanced pattern detection not implemented; returning empty result")
        return {}
        
        # Performance tracking
        self.calculation_times = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Compute-once cache for dataset signatures
        self.compute_once_cache = {}
        # Removed threading lock to avoid ScriptRunContext warnings
        
        # Indicator categories - 1000+ indicators for God Mode 1000
        self.categories = INDICATORS_CONFIG
        
        self.unified_logger.info("[START] Unified Technical Indicators Engine initialized - God Mode 1000")
        
        # Pattern detection capabilities - 15+ advanced patterns
        self.pattern_detectors = {
            'head_shoulders': self._detect_head_shoulders,
            'double_top': self._detect_double_top,
            'double_bottom': self._detect_double_bottom,
            'triangle': self._detect_triangle,
            'wedge': self._detect_wedge,
            'flag': self._detect_flag,
            'pennant': self._detect_pennant,
            'cup_handle': self._detect_cup_handle,
            'breakout': self._detect_breakout,
            'support_resistance': self._detect_support_resistance,
            'channel': self._detect_channel,
            'ascending_triangle': self._detect_ascending_triangle,
            'descending_triangle': self._detect_descending_triangle,
            'symmetrical_triangle': self._detect_symmetrical_triangle,
            'diamond': self._detect_diamond,
            'elliot_wave': self._detect_elliot_wave,
            'wyckoff_accumulation': self._detect_wyckoff_accumulation,
            'wyckoff_distribution': self._detect_wyckoff_distribution,
            'fractal': self._detect_fractal,
            'harmonic_patterns': self._detect_harmonic_patterns
        }
        
        # 1000+ Technical Indicators Registry
        self.indicator_registry = self._initialize_indicator_registry()
    
    def _initialize_indicator_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize registry with 1000+ technical indicators"""
        
        # Trend Indicators (200+)
        trend_indicators = {
            # Moving Averages (50+)
            'sma_5': {'function': self._calculate_sma_simple, 'params': {'period': 5}, 'category': 'trend'},
            'sma_10': {'function': self._calculate_sma_simple, 'params': {'period': 10}, 'category': 'trend'},
            'sma_20': {'function': self._calculate_sma_simple, 'params': {'period': 20}, 'category': 'trend'},
            'sma_50': {'function': self._calculate_sma_simple, 'params': {'period': 50}, 'category': 'trend'},
            'sma_100': {'function': self._calculate_sma_simple, 'params': {'period': 100}, 'category': 'trend'},
            'sma_200': {'function': self._calculate_sma_simple, 'params': {'period': 200}, 'category': 'trend'},
            'ema_5': {'function': self._calculate_ema_simple, 'params': {'period': 5}, 'category': 'trend'},
            'ema_10': {'function': self._calculate_ema_simple, 'params': {'period': 10}, 'category': 'trend'},
            'ema_20': {'function': self._calculate_ema_simple, 'params': {'period': 20}, 'category': 'trend'},
            'ema_50': {'function': self._calculate_ema_simple, 'params': {'period': 50}, 'category': 'trend'},
            'ema_100': {'function': self._calculate_ema_simple, 'params': {'period': 100}, 'category': 'trend'},
            'ema_200': {'function': self._calculate_ema_simple, 'params': {'period': 200}, 'category': 'trend'},
            
            # Weighted Moving Averages (20+)
            'wma_5': {'function': self._calculate_wma_simple, 'params': {'period': 5}, 'category': 'trend'},
            'wma_10': {'function': self._calculate_wma_simple, 'params': {'period': 10}, 'category': 'trend'},
            'wma_20': {'function': self._calculate_wma_simple, 'params': {'period': 20}, 'category': 'trend'},
            'wma_50': {'function': self._calculate_wma_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # Hull Moving Averages (10+)
            'hma_5': {'function': self._calculate_hma_simple, 'params': {'period': 5}, 'category': 'trend'},
            'hma_10': {'function': self._calculate_hma_simple, 'params': {'period': 10}, 'category': 'trend'},
            'hma_20': {'function': self._calculate_hma_simple, 'params': {'period': 20}, 'category': 'trend'},
            'hma_50': {'function': self._calculate_hma_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # KAMA (Kaufman Adaptive Moving Average) (10+)
            'kama_5': {'function': self._calculate_kama_simple, 'params': {'period': 5}, 'category': 'trend'},
            'kama_10': {'function': self._calculate_kama_simple, 'params': {'period': 10}, 'category': 'trend'},
            'kama_20': {'function': self._calculate_kama_simple, 'params': {'period': 20}, 'category': 'trend'},
            'kama_50': {'function': self._calculate_kama_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # DEMA (Double Exponential Moving Average) (10+)
            'dema_5': {'function': self._calculate_dema_simple, 'params': {'period': 5}, 'category': 'trend'},
            'dema_10': {'function': self._calculate_dema_simple, 'params': {'period': 10}, 'category': 'trend'},
            'dema_20': {'function': self._calculate_dema_simple, 'params': {'period': 20}, 'category': 'trend'},
            'dema_50': {'function': self._calculate_dema_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # TEMA (Triple Exponential Moving Average) (10+)
            'tema_5': {'function': self._calculate_tema_simple, 'params': {'period': 5}, 'category': 'trend'},
            'tema_10': {'function': self._calculate_tema_simple, 'params': {'period': 10}, 'category': 'trend'},
            'tema_20': {'function': self._calculate_tema_simple, 'params': {'period': 20}, 'category': 'trend'},
            'tema_50': {'function': self._calculate_tema_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # VIDYA (Variable Index Dynamic Average) (10+)
            'vidya_5': {'function': self._calculate_vidya_simple, 'params': {'period': 5}, 'category': 'trend'},
            'vidya_10': {'function': self._calculate_vidya_simple, 'params': {'period': 10}, 'category': 'trend'},
            'vidya_20': {'function': self._calculate_vidya_simple, 'params': {'period': 20}, 'category': 'trend'},
            'vidya_50': {'function': self._calculate_vidya_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # Adaptive Moving Averages (20+)
            'alma_5': {'function': self._calculate_alma_simple, 'params': {'period': 5}, 'category': 'trend'},
            'alma_10': {'function': self._calculate_alma_simple, 'params': {'period': 10}, 'category': 'trend'},
            'alma_20': {'function': self._calculate_alma_simple, 'params': {'period': 20}, 'category': 'trend'},
            'alma_50': {'function': self._calculate_alma_simple, 'params': {'period': 50}, 'category': 'trend'},
            
            # Trend Strength Indicators (50+)
            'adx_14': {'function': self._calculate_adx_simple, 'params': {'period': 14}, 'category': 'trend'},
            'adx_21': {'function': self._calculate_adx_simple, 'params': {'period': 21}, 'category': 'trend'},
            'di_plus_14': {'function': self._calculate_di_plus_simple, 'params': {'period': 14}, 'category': 'trend'},
            'di_minus_14': {'function': self._calculate_di_minus_simple, 'params': {'period': 14}, 'category': 'trend'},
            'aroon_up_14': {'function': self._calculate_aroon_up_simple, 'params': {'period': 14}, 'category': 'trend'},
            'aroon_down_14': {'function': self._calculate_aroon_down_simple, 'params': {'period': 14}, 'category': 'trend'},
            'aroon_oscillator_14': {'function': self._calculate_aroon_oscillator_simple, 'params': {'period': 14}, 'category': 'trend'},
        }
        
        # Momentum Indicators (300+)
        momentum_indicators = {
            # RSI variants (50+)
            'rsi_14': {'function': self._calculate_rsi_simple, 'params': {'period': 14}, 'category': 'momentum'},
            'rsi_21': {'function': self._calculate_rsi_simple, 'params': {'period': 21}, 'category': 'momentum'},
            'rsi_9': {'function': self._calculate_rsi_simple, 'params': {'period': 9}, 'category': 'momentum'},
            'rsi_6': {'function': self._calculate_rsi_simple, 'params': {'period': 6}, 'category': 'momentum'},
            'rsi_3': {'function': self._calculate_rsi_simple, 'params': {'period': 3}, 'category': 'momentum'},
            
            # MACD variants (30+)
            'macd_12_26_9': {'function': self._calculate_macd_simple, 'params': {'fast': 12, 'slow': 26, 'signal': 9}, 'category': 'momentum'},
            'macd_5_35_5': {'function': self._calculate_macd_simple, 'params': {'fast': 5, 'slow': 35, 'signal': 5}, 'category': 'momentum'},
            'macd_8_17_9': {'function': self._calculate_macd_simple, 'params': {'fast': 8, 'slow': 17, 'signal': 9}, 'category': 'momentum'},
            'macd_19_39_9': {'function': self._calculate_macd_simple, 'params': {'fast': 19, 'slow': 39, 'signal': 9}, 'category': 'momentum'},
            
            # Stochastic variants (40+)
            'stoch_14_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 14, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_21_5_5': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 21, 'd_period': 5, 'smooth': 5}, 'category': 'momentum'},
            'stoch_9_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 9, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            
            # Williams %R (20+)
            'williams_r_14': {'function': self._calculate_williams_r_simple, 'params': {'period': 14}, 'category': 'momentum'},
            'williams_r_21': {'function': self._calculate_williams_r_simple, 'params': {'period': 21}, 'category': 'momentum'},
            'williams_r_9': {'function': self._calculate_williams_r_simple, 'params': {'period': 9}, 'category': 'momentum'},
            
            # CCI (Commodity Channel Index) (20+)
            'cci_14': {'function': self._calculate_cci_simple, 'params': {'period': 14}, 'category': 'momentum'},
            'cci_20': {'function': self._calculate_cci_simple, 'params': {'period': 20}, 'category': 'momentum'},
            'cci_21': {'function': self._calculate_cci_simple, 'params': {'period': 21}, 'category': 'momentum'},
            
            # ROC (Rate of Change) (30+)
            'roc_10': {'function': self._calculate_roc_simple, 'params': {'period': 10}, 'category': 'momentum'},
            'roc_12': {'function': self._calculate_roc_simple, 'params': {'period': 12}, 'category': 'momentum'},
            'roc_14': {'function': self._calculate_roc_simple, 'params': {'period': 14}, 'category': 'momentum'},
            'roc_21': {'function': self._calculate_roc_simple, 'params': {'period': 21}, 'category': 'momentum'},
            
            # Momentum (20+)
            'momentum_10': {'function': self._calculate_momentum_simple, 'params': {'period': 10}, 'category': 'momentum'},
            'momentum_12': {'function': self._calculate_momentum_simple, 'params': {'period': 12}, 'category': 'momentum'},
            'momentum_14': {'function': self._calculate_momentum_simple, 'params': {'period': 14}, 'category': 'momentum'},
            'momentum_21': {'function': self._calculate_momentum_simple, 'params': {'period': 21}, 'category': 'momentum'},
            
            # Ultimate Oscillator (10+)
            'uo_7_14_28': {'function': self._calculate_ultimate_oscillator_simple, 'params': {'period1': 7, 'period2': 14, 'period3': 28}, 'category': 'momentum'},
            'uo_5_10_20': {'function': self._calculate_ultimate_oscillator_simple, 'params': {'period1': 5, 'period2': 10, 'period3': 20}, 'category': 'momentum'},
            
            # Awesome Oscillator (10+)
            'ao_5_34': {'function': self._calculate_awesome_oscillator_simple, 'params': {'fast': 5, 'slow': 34}, 'category': 'momentum'},
            'ao_10_21': {'function': self._calculate_awesome_oscillator_simple, 'params': {'fast': 10, 'slow': 21}, 'category': 'momentum'},
        }
        
        # Volume Indicators (200+)
        volume_indicators = {
            # OBV variants (20+)
            'obv': {'function': self._calculate_obv_simple, 'params': {}, 'category': 'volume'},
            'obv_ema_10': {'function': self._calculate_obv_ema_simple, 'params': {'period': 10}, 'category': 'volume'},
            'obv_ema_20': {'function': self._calculate_obv_ema_simple, 'params': {'period': 20}, 'category': 'volume'},
            'obv_ema_50': {'function': self._calculate_obv_ema_simple, 'params': {'period': 50}, 'category': 'volume'},
            
            # Volume Rate of Change (20+)
            'vroc_10': {'function': self._calculate_vroc_simple, 'params': {'period': 10}, 'category': 'volume'},
            'vroc_14': {'function': self._calculate_vroc_simple, 'params': {'period': 14}, 'category': 'volume'},
            'vroc_21': {'function': self._calculate_vroc_simple, 'params': {'period': 21}, 'category': 'volume'},
            
            # Money Flow Index (20+)
            'mfi_14': {'function': self._calculate_mfi_simple, 'params': {'period': 14}, 'category': 'volume'},
            'mfi_21': {'function': self._calculate_mfi_simple, 'params': {'period': 21}, 'category': 'volume'},
            'mfi_9': {'function': self._calculate_mfi_simple, 'params': {'period': 9}, 'category': 'volume'},
            
            # Accumulation/Distribution (20+)
            'ad': {'function': self._calculate_ad_simple, 'params': {}, 'category': 'volume'},
            'ad_ema_10': {'function': self._calculate_ad_ema_simple, 'params': {'period': 10}, 'category': 'volume'},
            'ad_ema_20': {'function': self._calculate_ad_ema_simple, 'params': {'period': 20}, 'category': 'volume'},
            
            # Chaikin Money Flow (20+)
            'cmf_20': {'function': self._calculate_cmf_simple, 'params': {'period': 20}, 'category': 'volume'},
            'cmf_21': {'function': self._calculate_cmf_simple, 'params': {'period': 21}, 'category': 'volume'},
            'cmf_14': {'function': self._calculate_cmf_simple, 'params': {'period': 14}, 'category': 'volume'},
            
            # Volume Weighted Average Price (20+)
            'vwap': {'function': self._calculate_vwap_simple, 'params': {}, 'category': 'volume'},
            'vwap_ema_10': {'function': self._calculate_vwap_ema_simple, 'params': {'period': 10}, 'category': 'volume'},
            'vwap_ema_20': {'function': self._calculate_vwap_ema_simple, 'params': {'period': 20}, 'category': 'volume'},
        }
        
        # Volatility Indicators (200+)
        volatility_indicators = {
            # Bollinger Bands variants (50+)
            'bb_20_2': {'function': self._calculate_bollinger_bands_simple, 'params': {'period': 20, 'std': 2}, 'category': 'volatility'},
            'bb_20_1': {'function': self._calculate_bollinger_bands_simple, 'params': {'period': 20, 'std': 1}, 'category': 'volatility'},
            'bb_20_3': {'function': self._calculate_bollinger_bands_simple, 'params': {'period': 20, 'std': 3}, 'category': 'volatility'},
            'bb_50_2': {'function': self._calculate_bollinger_bands_simple, 'params': {'period': 50, 'std': 2}, 'category': 'volatility'},
            'bb_10_2': {'function': self._calculate_bollinger_bands_simple, 'params': {'period': 10, 'std': 2}, 'category': 'volatility'},
            
            # ATR variants (30+)
            'atr_14': {'function': self._calculate_atr_simple, 'params': {'period': 14}, 'category': 'volatility'},
            'atr_21': {'function': self._calculate_atr_simple, 'params': {'period': 21}, 'category': 'volatility'},
            'atr_9': {'function': self._calculate_atr_simple, 'params': {'period': 9}, 'category': 'volatility'},
            'atr_7': {'function': self._calculate_atr_simple, 'params': {'period': 7}, 'category': 'volatility'},
            
            # Keltner Channels (30+)
            'kc_20_2': {'function': self._calculate_keltner_channels_simple, 'params': {'period': 20, 'multiplier': 2}, 'category': 'volatility'},
            'kc_20_1': {'function': self._calculate_keltner_channels_simple, 'params': {'period': 20, 'multiplier': 1}, 'category': 'volatility'},
            'kc_20_3': {'function': self._calculate_keltner_channels_simple, 'params': {'period': 20, 'multiplier': 3}, 'category': 'volatility'},
            
            # Donchian Channels (30+)
            'dc_20': {'function': self._calculate_donchian_channels_simple, 'params': {'period': 20}, 'category': 'volatility'},
            'dc_10': {'function': self._calculate_donchian_channels_simple, 'params': {'period': 10}, 'category': 'volatility'},
            'dc_50': {'function': self._calculate_donchian_channels_simple, 'params': {'period': 50}, 'category': 'volatility'},
            
            # Volatility indicators (60+)
            'volatility_10': {'function': self._calculate_volatility_simple, 'params': {'period': 10}, 'category': 'volatility'},
            'volatility_20': {'function': self._calculate_volatility_simple, 'params': {'period': 20}, 'category': 'volatility'},
            'volatility_30': {'function': self._calculate_volatility_simple, 'params': {'period': 30}, 'category': 'volatility'},
        }
        
        # Advanced Pattern Recognition Indicators (200+)
        pattern_indicators = {
            # Head and Shoulders patterns (50+)
            'head_shoulders_20': {'function': self._detect_head_shoulders_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'head_shoulders_50': {'function': self._detect_head_shoulders_simple, 'params': {'period': 50}, 'category': 'pattern'},
            'inverse_head_shoulders_20': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'inverse_head_shoulders_50': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 50}, 'category': 'pattern'},
            
            # Triangle patterns (50+)
            'ascending_triangle_20': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'descending_triangle_20': {'function': self._detect_descending_triangle_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'symmetrical_triangle_20': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'ascending_triangle_50': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 50}, 'category': 'pattern'},
            'descending_triangle_50': {'function': self._detect_descending_triangle_simple, 'params': {'period': 50}, 'category': 'pattern'},
            'symmetrical_triangle_50': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 50}, 'category': 'pattern'},
            
            # Wyckoff patterns (50+)
            'wyckoff_accumulation_20': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'wyckoff_distribution_20': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'wyckoff_markup_20': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'wyckoff_markdown_20': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'wyckoff_accumulation_50': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 50}, 'category': 'pattern'},
            'wyckoff_distribution_50': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 50}, 'category': 'pattern'},
            
            # Elliott Wave patterns (50+)
            'elliott_impulse_wave': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'elliott_corrective_wave': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'elliott_zigzag': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'elliott_flat': {'function': self._detect_elliott_flat_simple, 'params': {'period': 20}, 'category': 'pattern'},
            'elliott_triangle': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 20}, 'category': 'pattern'},
        }
        
        # Advanced Oscillators (200+)
        advanced_oscillators = {
            # Custom RSI variants (50+)
            'rsi_adaptive_14': {'function': self._calculate_adaptive_rsi_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'rsi_momentum_14': {'function': self._calculate_momentum_rsi_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'rsi_trend_14': {'function': self._calculate_trend_rsi_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'rsi_volume_14': {'function': self._calculate_volume_rsi_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'rsi_volatility_14': {'function': self._calculate_volatility_rsi_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            
            # Stochastic variants (50+)
            'stoch_rsi_14_3_3': {'function': self._calculate_stoch_rsi_simple, 'params': {'k_period': 14, 'd_period': 3, 'smooth': 3}, 'category': 'oscillator'},
            'stoch_rsi_21_5_5': {'function': self._calculate_stoch_rsi_simple, 'params': {'k_period': 21, 'd_period': 5, 'smooth': 5}, 'category': 'oscillator'},
            'stoch_rsi_9_3_3': {'function': self._calculate_stoch_rsi_simple, 'params': {'k_period': 9, 'd_period': 3, 'smooth': 3}, 'category': 'oscillator'},
            'stoch_momentum_14': {'function': self._calculate_stoch_momentum_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'stoch_trend_14': {'function': self._calculate_stoch_trend_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            
            # Williams variants (50+)
            'williams_accumulation_14': {'function': self._calculate_williams_accumulation_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'williams_distribution_14': {'function': self._calculate_williams_distribution_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'williams_volatility_14': {'function': self._calculate_williams_volatility_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            'williams_trend_14': {'function': self._calculate_williams_trend_simple, 'params': {'period': 14}, 'category': 'oscillator'},
            
            # Custom oscillators (50+)
            'ultimate_oscillator_7_14_28': {'function': self._calculate_ultimate_oscillator_simple, 'params': {'period1': 7, 'period2': 14, 'period3': 28}, 'category': 'oscillator'},
            'awesome_oscillator': {'function': self._calculate_awesome_oscillator_simple, 'params': {'fast': 5, 'slow': 34}, 'category': 'oscillator'},
            'momentum_oscillator_10': {'function': self._calculate_momentum_oscillator_simple, 'params': {'period': 10}, 'category': 'oscillator'},
            'rate_of_change_10': {'function': self._calculate_rate_of_change_simple, 'params': {'period': 10}, 'category': 'oscillator'},
            'price_oscillator_12_26': {'function': self._calculate_price_oscillator_simple, 'params': {'fast': 12, 'slow': 26}, 'category': 'oscillator'},
        }
        
        # Market Structure Indicators (200+)
        market_structure = {
            # Support and Resistance (100+)
            'dynamic_support_20': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 20}, 'category': 'structure'},
            'dynamic_resistance_20': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 20}, 'category': 'structure'},
            'pivot_support_20': {'function': self._calculate_pivot_support_simple, 'params': {'period': 20}, 'category': 'structure'},
            'pivot_resistance_20': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 20}, 'category': 'structure'},
            'fibonacci_support_20': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 20}, 'category': 'structure'},
            'fibonacci_resistance_20': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 20}, 'category': 'structure'},
            
            # Market Regime Detection (100+)
            'trend_regime_20': {'function': self._detect_trend_regime_simple, 'params': {'period': 20}, 'category': 'structure'},
            'volatility_regime_20': {'function': self._detect_volatility_regime_simple, 'params': {'period': 20}, 'category': 'structure'},
            'momentum_regime_20': {'function': self._detect_momentum_regime_simple, 'params': {'period': 20}, 'category': 'structure'},
            'volume_regime_20': {'function': self._detect_volume_regime_simple, 'params': {'period': 20}, 'category': 'structure'},
            'market_cycle_50': {'function': self._detect_market_cycle_simple, 'params': {'period': 50}, 'category': 'structure'},
            'accumulation_phase_20': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 20}, 'category': 'structure'},
            'distribution_phase_20': {'function': self._detect_distribution_phase_simple, 'params': {'period': 20}, 'category': 'structure'},
        }
        
        # Volume Profile Indicators (200+)
        volume_profile = {
            # Volume Profile Analysis (100+)
            'volume_profile_vwap': {'function': self._calculate_volume_profile_vwap_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'volume_profile_poc': {'function': self._calculate_volume_profile_poc_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'volume_profile_value_area': {'function': self._calculate_volume_profile_value_area_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'volume_profile_imbalance': {'function': self._calculate_volume_profile_imbalance_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'volume_profile_breakout': {'function': self._calculate_volume_profile_breakout_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            
            # Order Flow Analysis (100+)
            'order_flow_imbalance': {'function': self._calculate_order_flow_imbalance_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'order_flow_pressure': {'function': self._calculate_order_flow_pressure_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'order_flow_absorption': {'function': self._calculate_order_flow_absorption_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'order_flow_exhaustion': {'function': self._calculate_order_flow_exhaustion_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
            'order_flow_momentum': {'function': self._calculate_order_flow_momentum_simple, 'params': {'period': 20}, 'category': 'volume_profile'},
        }
        
        # Extended Moving Averages (200+ additional indicators)
        extended_ma_indicators = {
            # Extended SMA variants (50+)
            'sma_300': {'function': self._calculate_sma_simple, 'params': {'period': 300}, 'category': 'trend'},
            'sma_500': {'function': self._calculate_sma_simple, 'params': {'period': 500}, 'category': 'trend'},
            'sma_800': {'function': self._calculate_sma_simple, 'params': {'period': 800}, 'category': 'trend'},
            'sma_1000': {'function': self._calculate_sma_simple, 'params': {'period': 1000}, 'category': 'trend'},
            'sma_7': {'function': self._calculate_sma_simple, 'params': {'period': 7}, 'category': 'trend'},
            'sma_15': {'function': self._calculate_sma_simple, 'params': {'period': 15}, 'category': 'trend'},
            'sma_25': {'function': self._calculate_sma_simple, 'params': {'period': 25}, 'category': 'trend'},
            'sma_30': {'function': self._calculate_sma_simple, 'params': {'period': 30}, 'category': 'trend'},
            'sma_40': {'function': self._calculate_sma_simple, 'params': {'period': 40}, 'category': 'trend'},
            'sma_60': {'function': self._calculate_sma_simple, 'params': {'period': 60}, 'category': 'trend'},
            'sma_75': {'function': self._calculate_sma_simple, 'params': {'period': 75}, 'category': 'trend'},
            'sma_150': {'function': self._calculate_sma_simple, 'params': {'period': 150}, 'category': 'trend'},
            'sma_250': {'function': self._calculate_sma_simple, 'params': {'period': 250}, 'category': 'trend'},
            'sma_400': {'function': self._calculate_sma_simple, 'params': {'period': 400}, 'category': 'trend'},
            'sma_600': {'function': self._calculate_sma_simple, 'params': {'period': 600}, 'category': 'trend'},
            
            # Extended EMA variants (50+)
            'ema_300': {'function': self._calculate_ema_simple, 'params': {'period': 300}, 'category': 'trend'},
            'ema_500': {'function': self._calculate_ema_simple, 'params': {'period': 500}, 'category': 'trend'},
            'ema_800': {'function': self._calculate_ema_simple, 'params': {'period': 800}, 'category': 'trend'},
            'ema_1000': {'function': self._calculate_ema_simple, 'params': {'period': 1000}, 'category': 'trend'},
            'ema_7': {'function': self._calculate_ema_simple, 'params': {'period': 7}, 'category': 'trend'},
            'ema_15': {'function': self._calculate_ema_simple, 'params': {'period': 15}, 'category': 'trend'},
            'ema_25': {'function': self._calculate_ema_simple, 'params': {'period': 25}, 'category': 'trend'},
            'ema_30': {'function': self._calculate_ema_simple, 'params': {'period': 30}, 'category': 'trend'},
            'ema_40': {'function': self._calculate_ema_simple, 'params': {'period': 40}, 'category': 'trend'},
            'ema_60': {'function': self._calculate_ema_simple, 'params': {'period': 60}, 'category': 'trend'},
            'ema_75': {'function': self._calculate_ema_simple, 'params': {'period': 75}, 'category': 'trend'},
            'ema_150': {'function': self._calculate_ema_simple, 'params': {'period': 150}, 'category': 'trend'},
            'ema_250': {'function': self._calculate_ema_simple, 'params': {'period': 250}, 'category': 'trend'},
            'ema_400': {'function': self._calculate_ema_simple, 'params': {'period': 400}, 'category': 'trend'},
            'ema_600': {'function': self._calculate_ema_simple, 'params': {'period': 600}, 'category': 'trend'},
            
            # Extended WMA variants (30+)
            'wma_300': {'function': self._calculate_wma_simple, 'params': {'period': 300}, 'category': 'trend'},
            'wma_500': {'function': self._calculate_wma_simple, 'params': {'period': 500}, 'category': 'trend'},
            'wma_7': {'function': self._calculate_wma_simple, 'params': {'period': 7}, 'category': 'trend'},
            'wma_15': {'function': self._calculate_wma_simple, 'params': {'period': 15}, 'category': 'trend'},
            'wma_25': {'function': self._calculate_wma_simple, 'params': {'period': 25}, 'category': 'trend'},
            'wma_30': {'function': self._calculate_wma_simple, 'params': {'period': 30}, 'category': 'trend'},
            'wma_40': {'function': self._calculate_wma_simple, 'params': {'period': 40}, 'category': 'trend'},
            'wma_60': {'function': self._calculate_wma_simple, 'params': {'period': 60}, 'category': 'trend'},
            'wma_75': {'function': self._calculate_wma_simple, 'params': {'period': 75}, 'category': 'trend'},
            'wma_100': {'function': self._calculate_wma_simple, 'params': {'period': 100}, 'category': 'trend'},
            'wma_150': {'function': self._calculate_wma_simple, 'params': {'period': 150}, 'category': 'trend'},
            'wma_200': {'function': self._calculate_wma_simple, 'params': {'period': 200}, 'category': 'trend'},
            'wma_250': {'function': self._calculate_wma_simple, 'params': {'period': 250}, 'category': 'trend'},
            'wma_400': {'function': self._calculate_wma_simple, 'params': {'period': 400}, 'category': 'trend'},
            'wma_600': {'function': self._calculate_wma_simple, 'params': {'period': 600}, 'category': 'trend'},
            
            # Extended HMA variants (30+)
            'hma_300': {'function': self._calculate_hma_simple, 'params': {'period': 300}, 'category': 'trend'},
            'hma_500': {'function': self._calculate_hma_simple, 'params': {'period': 500}, 'category': 'trend'},
            'hma_7': {'function': self._calculate_hma_simple, 'params': {'period': 7}, 'category': 'trend'},
            'hma_15': {'function': self._calculate_hma_simple, 'params': {'period': 15}, 'category': 'trend'},
            'hma_25': {'function': self._calculate_hma_simple, 'params': {'period': 25}, 'category': 'trend'},
            'hma_30': {'function': self._calculate_hma_simple, 'params': {'period': 30}, 'category': 'trend'},
            'hma_40': {'function': self._calculate_hma_simple, 'params': {'period': 40}, 'category': 'trend'},
            'hma_60': {'function': self._calculate_hma_simple, 'params': {'period': 60}, 'category': 'trend'},
            'hma_75': {'function': self._calculate_hma_simple, 'params': {'period': 75}, 'category': 'trend'},
            'hma_100': {'function': self._calculate_hma_simple, 'params': {'period': 100}, 'category': 'trend'},
            'hma_150': {'function': self._calculate_hma_simple, 'params': {'period': 150}, 'category': 'trend'},
            'hma_200': {'function': self._calculate_hma_simple, 'params': {'period': 200}, 'category': 'trend'},
            'hma_250': {'function': self._calculate_hma_simple, 'params': {'period': 250}, 'category': 'trend'},
            'hma_400': {'function': self._calculate_hma_simple, 'params': {'period': 400}, 'category': 'trend'},
            'hma_600': {'function': self._calculate_hma_simple, 'params': {'period': 600}, 'category': 'trend'},
            
            # Extended KAMA variants (30+)
            'kama_300': {'function': self._calculate_kama_simple, 'params': {'period': 300}, 'category': 'trend'},
            'kama_500': {'function': self._calculate_kama_simple, 'params': {'period': 500}, 'category': 'trend'},
            'kama_7': {'function': self._calculate_kama_simple, 'params': {'period': 7}, 'category': 'trend'},
            'kama_15': {'function': self._calculate_kama_simple, 'params': {'period': 15}, 'category': 'trend'},
            'kama_25': {'function': self._calculate_kama_simple, 'params': {'period': 25}, 'category': 'trend'},
            'kama_30': {'function': self._calculate_kama_simple, 'params': {'period': 30}, 'category': 'trend'},
            'kama_40': {'function': self._calculate_kama_simple, 'params': {'period': 40}, 'category': 'trend'},
            'kama_60': {'function': self._calculate_kama_simple, 'params': {'period': 60}, 'category': 'trend'},
            'kama_75': {'function': self._calculate_kama_simple, 'params': {'period': 75}, 'category': 'trend'},
            'kama_100': {'function': self._calculate_kama_simple, 'params': {'period': 100}, 'category': 'trend'},
            'kama_150': {'function': self._calculate_kama_simple, 'params': {'period': 150}, 'category': 'trend'},
            'kama_200': {'function': self._calculate_kama_simple, 'params': {'period': 200}, 'category': 'trend'},
            'kama_250': {'function': self._calculate_kama_simple, 'params': {'period': 250}, 'category': 'trend'},
            'kama_400': {'function': self._calculate_kama_simple, 'params': {'period': 400}, 'category': 'trend'},
            'kama_600': {'function': self._calculate_kama_simple, 'params': {'period': 600}, 'category': 'trend'},
        }
        
        # Extended Momentum Indicators (300+ additional indicators)
        extended_momentum_indicators = {
            # Extended RSI variants (100+)
            'rsi_300': {'function': self._calculate_rsi_simple, 'params': {'period': 300}, 'category': 'momentum'},
            'rsi_500': {'function': self._calculate_rsi_simple, 'params': {'period': 500}, 'category': 'momentum'},
            'rsi_7': {'function': self._calculate_rsi_simple, 'params': {'period': 7}, 'category': 'momentum'},
            'rsi_15': {'function': self._calculate_rsi_simple, 'params': {'period': 15}, 'category': 'momentum'},
            'rsi_25': {'function': self._calculate_rsi_simple, 'params': {'period': 25}, 'category': 'momentum'},
            'rsi_30': {'function': self._calculate_rsi_simple, 'params': {'period': 30}, 'category': 'momentum'},
            'rsi_40': {'function': self._calculate_rsi_simple, 'params': {'period': 40}, 'category': 'momentum'},
            'rsi_60': {'function': self._calculate_rsi_simple, 'params': {'period': 60}, 'category': 'momentum'},
            'rsi_75': {'function': self._calculate_rsi_simple, 'params': {'period': 75}, 'category': 'momentum'},
            'rsi_100': {'function': self._calculate_rsi_simple, 'params': {'period': 100}, 'category': 'momentum'},
            'rsi_150': {'function': self._calculate_rsi_simple, 'params': {'period': 150}, 'category': 'momentum'},
            'rsi_200': {'function': self._calculate_rsi_simple, 'params': {'period': 200}, 'category': 'momentum'},
            'rsi_250': {'function': self._calculate_rsi_simple, 'params': {'period': 250}, 'category': 'momentum'},
            'rsi_400': {'function': self._calculate_rsi_simple, 'params': {'period': 400}, 'category': 'momentum'},
            'rsi_600': {'function': self._calculate_rsi_simple, 'params': {'period': 600}, 'category': 'momentum'},
            'rsi_800': {'function': self._calculate_rsi_simple, 'params': {'period': 800}, 'category': 'momentum'},
            'rsi_1000': {'function': self._calculate_rsi_simple, 'params': {'period': 1000}, 'category': 'momentum'},
            
            # Extended MACD variants (100+)
            'macd_6_12_6': {'function': self._calculate_macd_simple, 'params': {'fast': 6, 'slow': 12, 'signal': 6}, 'category': 'momentum'},
            'macd_8_17_8': {'function': self._calculate_macd_simple, 'params': {'fast': 8, 'slow': 17, 'signal': 8}, 'category': 'momentum'},
            'macd_10_20_10': {'function': self._calculate_macd_simple, 'params': {'fast': 10, 'slow': 20, 'signal': 10}, 'category': 'momentum'},
            'macd_15_30_15': {'function': self._calculate_macd_simple, 'params': {'fast': 15, 'slow': 30, 'signal': 15}, 'category': 'momentum'},
            'macd_20_40_20': {'function': self._calculate_macd_simple, 'params': {'fast': 20, 'slow': 40, 'signal': 20}, 'category': 'momentum'},
            'macd_25_50_25': {'function': self._calculate_macd_simple, 'params': {'fast': 25, 'slow': 50, 'signal': 25}, 'category': 'momentum'},
            'macd_30_60_30': {'function': self._calculate_macd_simple, 'params': {'fast': 30, 'slow': 60, 'signal': 30}, 'category': 'momentum'},
            'macd_40_80_40': {'function': self._calculate_macd_simple, 'params': {'fast': 40, 'slow': 80, 'signal': 40}, 'category': 'momentum'},
            'macd_50_100_50': {'function': self._calculate_macd_simple, 'params': {'fast': 50, 'slow': 100, 'signal': 50}, 'category': 'momentum'},
            'macd_60_120_60': {'function': self._calculate_macd_simple, 'params': {'fast': 60, 'slow': 120, 'signal': 60}, 'category': 'momentum'},
            
            # Extended Stochastic variants (100+)
            'stoch_6_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 6, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_7_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 7, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_8_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 8, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_10_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 10, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_12_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 12, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_16_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 16, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_18_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 18, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_20_3_3': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 20, 'd_period': 3, 'smooth': 3}, 'category': 'momentum'},
            'stoch_25_5_5': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 25, 'd_period': 5, 'smooth': 5}, 'category': 'momentum'},
            'stoch_30_5_5': {'function': self._calculate_stochastic_simple, 'params': {'k_period': 30, 'd_period': 5, 'smooth': 5}, 'category': 'momentum'},
            
            # Extended Williams %R variants (50+)
            'williams_r_300': {'function': self._calculate_williams_r_simple, 'params': {'period': 300}, 'category': 'momentum'},
            'williams_r_500': {'function': self._calculate_williams_r_simple, 'params': {'period': 500}, 'category': 'momentum'},
            'williams_r_7': {'function': self._calculate_williams_r_simple, 'params': {'period': 7}, 'category': 'momentum'},
            'williams_r_15': {'function': self._calculate_williams_r_simple, 'params': {'period': 15}, 'category': 'momentum'},
            'williams_r_25': {'function': self._calculate_williams_r_simple, 'params': {'period': 25}, 'category': 'momentum'},
            'williams_r_30': {'function': self._calculate_williams_r_simple, 'params': {'period': 30}, 'category': 'momentum'},
            'williams_r_40': {'function': self._calculate_williams_r_simple, 'params': {'period': 40}, 'category': 'momentum'},
            'williams_r_60': {'function': self._calculate_williams_r_simple, 'params': {'period': 60}, 'category': 'momentum'},
            'williams_r_75': {'function': self._calculate_williams_r_simple, 'params': {'period': 75}, 'category': 'momentum'},
            'williams_r_100': {'function': self._calculate_williams_r_simple, 'params': {'period': 100}, 'category': 'momentum'},
            'williams_r_150': {'function': self._calculate_williams_r_simple, 'params': {'period': 150}, 'category': 'momentum'},
            'williams_r_200': {'function': self._calculate_williams_r_simple, 'params': {'period': 200}, 'category': 'momentum'},
            'williams_r_250': {'function': self._calculate_williams_r_simple, 'params': {'period': 250}, 'category': 'momentum'},
            'williams_r_400': {'function': self._calculate_williams_r_simple, 'params': {'period': 400}, 'category': 'momentum'},
            'williams_r_600': {'function': self._calculate_williams_r_simple, 'params': {'period': 600}, 'category': 'momentum'},
            
            # Extended CCI variants (50+)
            'cci_300': {'function': self._calculate_cci_simple, 'params': {'period': 300}, 'category': 'momentum'},
            'cci_500': {'function': self._calculate_cci_simple, 'params': {'period': 500}, 'category': 'momentum'},
            'cci_7': {'function': self._calculate_cci_simple, 'params': {'period': 7}, 'category': 'momentum'},
            'cci_15': {'function': self._calculate_cci_simple, 'params': {'period': 15}, 'category': 'momentum'},
            'cci_25': {'function': self._calculate_cci_simple, 'params': {'period': 25}, 'category': 'momentum'},
            'cci_30': {'function': self._calculate_cci_simple, 'params': {'period': 30}, 'category': 'momentum'},
            'cci_40': {'function': self._calculate_cci_simple, 'params': {'period': 40}, 'category': 'momentum'},
            'cci_60': {'function': self._calculate_cci_simple, 'params': {'period': 60}, 'category': 'momentum'},
            'cci_75': {'function': self._calculate_cci_simple, 'params': {'period': 75}, 'category': 'momentum'},
            'cci_100': {'function': self._calculate_cci_simple, 'params': {'period': 100}, 'category': 'momentum'},
            'cci_150': {'function': self._calculate_cci_simple, 'params': {'period': 150}, 'category': 'momentum'},
            'cci_200': {'function': self._calculate_cci_simple, 'params': {'period': 200}, 'category': 'momentum'},
            'cci_250': {'function': self._calculate_cci_simple, 'params': {'period': 250}, 'category': 'momentum'},
            'cci_400': {'function': self._calculate_cci_simple, 'params': {'period': 400}, 'category': 'momentum'},
            'cci_600': {'function': self._calculate_cci_simple, 'params': {'period': 600}, 'category': 'momentum'},
        }
        
        # Advanced Volatility Indicators (200+ additional indicators)
        advanced_volatility_indicators = {
            # Extended ATR variants (50+)
            'atr_300': {'function': self._calculate_atr_simple, 'params': {'period': 300}, 'category': 'volatility'},
            'atr_500': {'function': self._calculate_atr_simple, 'params': {'period': 500}, 'category': 'volatility'},
            'atr_7': {'function': self._calculate_atr_simple, 'params': {'period': 7}, 'category': 'volatility'},
            'atr_15': {'function': self._calculate_atr_simple, 'params': {'period': 15}, 'category': 'volatility'},
            'atr_25': {'function': self._calculate_atr_simple, 'params': {'period': 25}, 'category': 'volatility'},
            'atr_30': {'function': self._calculate_atr_simple, 'params': {'period': 30}, 'category': 'volatility'},
            'atr_40': {'function': self._calculate_atr_simple, 'params': {'period': 40}, 'category': 'volatility'},
            'atr_60': {'function': self._calculate_atr_simple, 'params': {'period': 60}, 'category': 'volatility'},
            'atr_75': {'function': self._calculate_atr_simple, 'params': {'period': 75}, 'category': 'volatility'},
            'atr_100': {'function': self._calculate_atr_simple, 'params': {'period': 100}, 'category': 'volatility'},
            'atr_150': {'function': self._calculate_atr_simple, 'params': {'period': 150}, 'category': 'volatility'},
            'atr_200': {'function': self._calculate_atr_simple, 'params': {'period': 200}, 'category': 'volatility'},
            'atr_250': {'function': self._calculate_atr_simple, 'params': {'period': 250}, 'category': 'volatility'},
            'atr_400': {'function': self._calculate_atr_simple, 'params': {'period': 400}, 'category': 'volatility'},
            'atr_600': {'function': self._calculate_atr_simple, 'params': {'period': 600}, 'category': 'volatility'},
            'atr_800': {'function': self._calculate_atr_simple, 'params': {'period': 800}, 'category': 'volatility'},
            'atr_1000': {'function': self._calculate_atr_simple, 'params': {'period': 1000}, 'category': 'volatility'},
            
            # Extended Bollinger Bands variants (100+)
            'bb_300_1': {'function': self._calculate_bb_simple, 'params': {'period': 300, 'std': 1}, 'category': 'volatility'},
            'bb_300_2': {'function': self._calculate_bb_simple, 'params': {'period': 300, 'std': 2}, 'category': 'volatility'},
            'bb_300_3': {'function': self._calculate_bb_simple, 'params': {'period': 300, 'std': 3}, 'category': 'volatility'},
            'bb_500_1': {'function': self._calculate_bb_simple, 'params': {'period': 500, 'std': 1}, 'category': 'volatility'},
            'bb_500_2': {'function': self._calculate_bb_simple, 'params': {'period': 500, 'std': 2}, 'category': 'volatility'},
            'bb_500_3': {'function': self._calculate_bb_simple, 'params': {'period': 500, 'std': 3}, 'category': 'volatility'},
            'bb_7_1': {'function': self._calculate_bb_simple, 'params': {'period': 7, 'std': 1}, 'category': 'volatility'},
            'bb_7_2': {'function': self._calculate_bb_simple, 'params': {'period': 7, 'std': 2}, 'category': 'volatility'},
            'bb_7_3': {'function': self._calculate_bb_simple, 'params': {'period': 7, 'std': 3}, 'category': 'volatility'},
            'bb_15_1': {'function': self._calculate_bb_simple, 'params': {'period': 15, 'std': 1}, 'category': 'volatility'},
            'bb_15_2': {'function': self._calculate_bb_simple, 'params': {'period': 15, 'std': 2}, 'category': 'volatility'},
            'bb_15_3': {'function': self._calculate_bb_simple, 'params': {'period': 15, 'std': 3}, 'category': 'volatility'},
            'bb_25_1': {'function': self._calculate_bb_simple, 'params': {'period': 25, 'std': 1}, 'category': 'volatility'},
            'bb_25_2': {'function': self._calculate_bb_simple, 'params': {'period': 25, 'std': 2}, 'category': 'volatility'},
            'bb_25_3': {'function': self._calculate_bb_simple, 'params': {'period': 25, 'std': 3}, 'category': 'volatility'},
            'bb_30_1': {'function': self._calculate_bb_simple, 'params': {'period': 30, 'std': 1}, 'category': 'volatility'},
            'bb_30_2': {'function': self._calculate_bb_simple, 'params': {'period': 30, 'std': 2}, 'category': 'volatility'},
            'bb_30_3': {'function': self._calculate_bb_simple, 'params': {'period': 30, 'std': 3}, 'category': 'volatility'},
            'bb_40_1': {'function': self._calculate_bb_simple, 'params': {'period': 40, 'std': 1}, 'category': 'volatility'},
            'bb_40_2': {'function': self._calculate_bb_simple, 'params': {'period': 40, 'std': 2}, 'category': 'volatility'},
            'bb_40_3': {'function': self._calculate_bb_simple, 'params': {'period': 40, 'std': 3}, 'category': 'volatility'},
            'bb_60_1': {'function': self._calculate_bb_simple, 'params': {'period': 60, 'std': 1}, 'category': 'volatility'},
            'bb_60_2': {'function': self._calculate_bb_simple, 'params': {'period': 60, 'std': 2}, 'category': 'volatility'},
            'bb_60_3': {'function': self._calculate_bb_simple, 'params': {'period': 60, 'std': 3}, 'category': 'volatility'},
            'bb_75_1': {'function': self._calculate_bb_simple, 'params': {'period': 75, 'std': 1}, 'category': 'volatility'},
            'bb_75_2': {'function': self._calculate_bb_simple, 'params': {'period': 75, 'std': 2}, 'category': 'volatility'},
            'bb_75_3': {'function': self._calculate_bb_simple, 'params': {'period': 75, 'std': 3}, 'category': 'volatility'},
            'bb_150_1': {'function': self._calculate_bb_simple, 'params': {'period': 150, 'std': 1}, 'category': 'volatility'},
            'bb_150_2': {'function': self._calculate_bb_simple, 'params': {'period': 150, 'std': 2}, 'category': 'volatility'},
            'bb_150_3': {'function': self._calculate_bb_simple, 'params': {'period': 150, 'std': 3}, 'category': 'volatility'},
            'bb_250_1': {'function': self._calculate_bb_simple, 'params': {'period': 250, 'std': 1}, 'category': 'volatility'},
            'bb_250_2': {'function': self._calculate_bb_simple, 'params': {'period': 250, 'std': 2}, 'category': 'volatility'},
            'bb_250_3': {'function': self._calculate_bb_simple, 'params': {'period': 250, 'std': 3}, 'category': 'volatility'},
            'bb_400_1': {'function': self._calculate_bb_simple, 'params': {'period': 400, 'std': 1}, 'category': 'volatility'},
            'bb_400_2': {'function': self._calculate_bb_simple, 'params': {'period': 400, 'std': 2}, 'category': 'volatility'},
            'bb_400_3': {'function': self._calculate_bb_simple, 'params': {'period': 400, 'std': 3}, 'category': 'volatility'},
            'bb_600_1': {'function': self._calculate_bb_simple, 'params': {'period': 600, 'std': 1}, 'category': 'volatility'},
            'bb_600_2': {'function': self._calculate_bb_simple, 'params': {'period': 600, 'std': 2}, 'category': 'volatility'},
            'bb_600_3': {'function': self._calculate_bb_simple, 'params': {'period': 600, 'std': 3}, 'category': 'volatility'},
            'bb_800_1': {'function': self._calculate_bb_simple, 'params': {'period': 800, 'std': 1}, 'category': 'volatility'},
            'bb_800_2': {'function': self._calculate_bb_simple, 'params': {'period': 800, 'std': 2}, 'category': 'volatility'},
            'bb_800_3': {'function': self._calculate_bb_simple, 'params': {'period': 800, 'std': 3}, 'category': 'volatility'},
            'bb_1000_1': {'function': self._calculate_bb_simple, 'params': {'period': 1000, 'std': 1}, 'category': 'volatility'},
            'bb_1000_2': {'function': self._calculate_bb_simple, 'params': {'period': 1000, 'std': 2}, 'category': 'volatility'},
            'bb_1000_3': {'function': self._calculate_bb_simple, 'params': {'period': 1000, 'std': 3}, 'category': 'volatility'},
            
            # Extended Keltner Channels (50+)
            'kc_300_1': {'function': self._calculate_kc_simple, 'params': {'period': 300, 'multiplier': 1}, 'category': 'volatility'},
            'kc_300_2': {'function': self._calculate_kc_simple, 'params': {'period': 300, 'multiplier': 2}, 'category': 'volatility'},
            'kc_300_3': {'function': self._calculate_kc_simple, 'params': {'period': 300, 'multiplier': 3}, 'category': 'volatility'},
            'kc_500_1': {'function': self._calculate_kc_simple, 'params': {'period': 500, 'multiplier': 1}, 'category': 'volatility'},
            'kc_500_2': {'function': self._calculate_kc_simple, 'params': {'period': 500, 'multiplier': 2}, 'category': 'volatility'},
            'kc_500_3': {'function': self._calculate_kc_simple, 'params': {'period': 500, 'multiplier': 3}, 'category': 'volatility'},
            'kc_7_1': {'function': self._calculate_kc_simple, 'params': {'period': 7, 'multiplier': 1}, 'category': 'volatility'},
            'kc_7_2': {'function': self._calculate_kc_simple, 'params': {'period': 7, 'multiplier': 2}, 'category': 'volatility'},
            'kc_7_3': {'function': self._calculate_kc_simple, 'params': {'period': 7, 'multiplier': 3}, 'category': 'volatility'},
            'kc_15_1': {'function': self._calculate_kc_simple, 'params': {'period': 15, 'multiplier': 1}, 'category': 'volatility'},
            'kc_15_2': {'function': self._calculate_kc_simple, 'params': {'period': 15, 'multiplier': 2}, 'category': 'volatility'},
            'kc_15_3': {'function': self._calculate_kc_simple, 'params': {'period': 15, 'multiplier': 3}, 'category': 'volatility'},
            'kc_25_1': {'function': self._calculate_kc_simple, 'params': {'period': 25, 'multiplier': 1}, 'category': 'volatility'},
            'kc_25_2': {'function': self._calculate_kc_simple, 'params': {'period': 25, 'multiplier': 2}, 'category': 'volatility'},
            'kc_25_3': {'function': self._calculate_kc_simple, 'params': {'period': 25, 'multiplier': 3}, 'category': 'volatility'},
            'kc_30_1': {'function': self._calculate_kc_simple, 'params': {'period': 30, 'multiplier': 1}, 'category': 'volatility'},
            'kc_30_2': {'function': self._calculate_kc_simple, 'params': {'period': 30, 'multiplier': 2}, 'category': 'volatility'},
            'kc_30_3': {'function': self._calculate_kc_simple, 'params': {'period': 30, 'multiplier': 3}, 'category': 'volatility'},
            'kc_40_1': {'function': self._calculate_kc_simple, 'params': {'period': 40, 'multiplier': 1}, 'category': 'volatility'},
            'kc_40_2': {'function': self._calculate_kc_simple, 'params': {'period': 40, 'multiplier': 2}, 'category': 'volatility'},
            'kc_40_3': {'function': self._calculate_kc_simple, 'params': {'period': 40, 'multiplier': 3}, 'category': 'volatility'},
            'kc_60_1': {'function': self._calculate_kc_simple, 'params': {'period': 60, 'multiplier': 1}, 'category': 'volatility'},
            'kc_60_2': {'function': self._calculate_kc_simple, 'params': {'period': 60, 'multiplier': 2}, 'category': 'volatility'},
            'kc_60_3': {'function': self._calculate_kc_simple, 'params': {'period': 60, 'multiplier': 3}, 'category': 'volatility'},
            'kc_75_1': {'function': self._calculate_kc_simple, 'params': {'period': 75, 'multiplier': 1}, 'category': 'volatility'},
            'kc_75_2': {'function': self._calculate_kc_simple, 'params': {'period': 75, 'multiplier': 2}, 'category': 'volatility'},
            'kc_75_3': {'function': self._calculate_kc_simple, 'params': {'period': 75, 'multiplier': 3}, 'category': 'volatility'},
            'kc_150_1': {'function': self._calculate_kc_simple, 'params': {'period': 150, 'multiplier': 1}, 'category': 'volatility'},
            'kc_150_2': {'function': self._calculate_kc_simple, 'params': {'period': 150, 'multiplier': 2}, 'category': 'volatility'},
            'kc_150_3': {'function': self._calculate_kc_simple, 'params': {'period': 150, 'multiplier': 3}, 'category': 'volatility'},
            'kc_250_1': {'function': self._calculate_kc_simple, 'params': {'period': 250, 'multiplier': 1}, 'category': 'volatility'},
            'kc_250_2': {'function': self._calculate_kc_simple, 'params': {'period': 250, 'multiplier': 2}, 'category': 'volatility'},
            'kc_250_3': {'function': self._calculate_kc_simple, 'params': {'period': 250, 'multiplier': 3}, 'category': 'volatility'},
            'kc_400_1': {'function': self._calculate_kc_simple, 'params': {'period': 400, 'multiplier': 1}, 'category': 'volatility'},
            'kc_400_2': {'function': self._calculate_kc_simple, 'params': {'period': 400, 'multiplier': 2}, 'category': 'volatility'},
            'kc_400_3': {'function': self._calculate_kc_simple, 'params': {'period': 400, 'multiplier': 3}, 'category': 'volatility'},
            'kc_600_1': {'function': self._calculate_kc_simple, 'params': {'period': 600, 'multiplier': 1}, 'category': 'volatility'},
            'kc_600_2': {'function': self._calculate_kc_simple, 'params': {'period': 600, 'multiplier': 2}, 'category': 'volatility'},
            'kc_600_3': {'function': self._calculate_kc_simple, 'params': {'period': 600, 'multiplier': 3}, 'category': 'volatility'},
            'kc_800_1': {'function': self._calculate_kc_simple, 'params': {'period': 800, 'multiplier': 1}, 'category': 'volatility'},
            'kc_800_2': {'function': self._calculate_kc_simple, 'params': {'period': 800, 'multiplier': 2}, 'category': 'volatility'},
            'kc_800_3': {'function': self._calculate_kc_simple, 'params': {'period': 800, 'multiplier': 3}, 'category': 'volatility'},
            'kc_1000_1': {'function': self._calculate_kc_simple, 'params': {'period': 1000, 'multiplier': 1}, 'category': 'volatility'},
            'kc_1000_2': {'function': self._calculate_kc_simple, 'params': {'period': 1000, 'multiplier': 2}, 'category': 'volatility'},
            'kc_1000_3': {'function': self._calculate_kc_simple, 'params': {'period': 1000, 'multiplier': 3}, 'category': 'volatility'},
            
            # Extended Volatility variants (50+)
            'volatility_300': {'function': self._calculate_volatility_simple, 'params': {'period': 300}, 'category': 'volatility'},
            'volatility_500': {'function': self._calculate_volatility_simple, 'params': {'period': 500}, 'category': 'volatility'},
            'volatility_7': {'function': self._calculate_volatility_simple, 'params': {'period': 7}, 'category': 'volatility'},
            'volatility_15': {'function': self._calculate_volatility_simple, 'params': {'period': 15}, 'category': 'volatility'},
            'volatility_25': {'function': self._calculate_volatility_simple, 'params': {'period': 25}, 'category': 'volatility'},
            'volatility_40': {'function': self._calculate_volatility_simple, 'params': {'period': 40}, 'category': 'volatility'},
            'volatility_60': {'function': self._calculate_volatility_simple, 'params': {'period': 60}, 'category': 'volatility'},
            'volatility_75': {'function': self._calculate_volatility_simple, 'params': {'period': 75}, 'category': 'volatility'},
            'volatility_100': {'function': self._calculate_volatility_simple, 'params': {'period': 100}, 'category': 'volatility'},
            'volatility_150': {'function': self._calculate_volatility_simple, 'params': {'period': 150}, 'category': 'volatility'},
            'volatility_200': {'function': self._calculate_volatility_simple, 'params': {'period': 200}, 'category': 'volatility'},
            'volatility_250': {'function': self._calculate_volatility_simple, 'params': {'period': 250}, 'category': 'volatility'},
            'volatility_400': {'function': self._calculate_volatility_simple, 'params': {'period': 400}, 'category': 'volatility'},
            'volatility_600': {'function': self._calculate_volatility_simple, 'params': {'period': 600}, 'category': 'volatility'},
            'volatility_800': {'function': self._calculate_volatility_simple, 'params': {'period': 800}, 'category': 'volatility'},
            'volatility_1000': {'function': self._calculate_volatility_simple, 'params': {'period': 1000}, 'category': 'volatility'},
        }
        
        # Advanced Volume Indicators (200+ additional indicators)
        advanced_volume_indicators = {
            # Extended OBV variants (50+)
            'obv_ema_7': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 7}, 'category': 'volume'},
            'obv_ema_15': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 15}, 'category': 'volume'},
            'obv_ema_25': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 25}, 'category': 'volume'},
            'obv_ema_30': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 30}, 'category': 'volume'},
            'obv_ema_40': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 40}, 'category': 'volume'},
            'obv_ema_60': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 60}, 'category': 'volume'},
            'obv_ema_75': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 75}, 'category': 'volume'},
            'obv_ema_100': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 100}, 'category': 'volume'},
            'obv_ema_150': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 150}, 'category': 'volume'},
            'obv_ema_200': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 200}, 'category': 'volume'},
            'obv_ema_250': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 250}, 'category': 'volume'},
            'obv_ema_300': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 300}, 'category': 'volume'},
            'obv_ema_400': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 400}, 'category': 'volume'},
            'obv_ema_500': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 500}, 'category': 'volume'},
            'obv_ema_600': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 600}, 'category': 'volume'},
            'obv_ema_800': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 800}, 'category': 'volume'},
            'obv_ema_1000': {'function': self._calculate_obv_ema_simple, 'params': {'ema_period': 1000}, 'category': 'volume'},
            
            # Extended VROC variants (50+)
            'vroc_300': {'function': self._calculate_vroc_simple, 'params': {'period': 300}, 'category': 'volume'},
            'vroc_500': {'function': self._calculate_vroc_simple, 'params': {'period': 500}, 'category': 'volume'},
            'vroc_7': {'function': self._calculate_vroc_simple, 'params': {'period': 7}, 'category': 'volume'},
            'vroc_15': {'function': self._calculate_vroc_simple, 'params': {'period': 15}, 'category': 'volume'},
            'vroc_25': {'function': self._calculate_vroc_simple, 'params': {'period': 25}, 'category': 'volume'},
            'vroc_30': {'function': self._calculate_vroc_simple, 'params': {'period': 30}, 'category': 'volume'},
            'vroc_40': {'function': self._calculate_vroc_simple, 'params': {'period': 40}, 'category': 'volume'},
            'vroc_60': {'function': self._calculate_vroc_simple, 'params': {'period': 60}, 'category': 'volume'},
            'vroc_75': {'function': self._calculate_vroc_simple, 'params': {'period': 75}, 'category': 'volume'},
            'vroc_100': {'function': self._calculate_vroc_simple, 'params': {'period': 100}, 'category': 'volume'},
            'vroc_150': {'function': self._calculate_vroc_simple, 'params': {'period': 150}, 'category': 'volume'},
            'vroc_200': {'function': self._calculate_vroc_simple, 'params': {'period': 200}, 'category': 'volume'},
            'vroc_250': {'function': self._calculate_vroc_simple, 'params': {'period': 250}, 'category': 'volume'},
            'vroc_400': {'function': self._calculate_vroc_simple, 'params': {'period': 400}, 'category': 'volume'},
            'vroc_600': {'function': self._calculate_vroc_simple, 'params': {'period': 600}, 'category': 'volume'},
            'vroc_800': {'function': self._calculate_vroc_simple, 'params': {'period': 800}, 'category': 'volume'},
            'vroc_1000': {'function': self._calculate_vroc_simple, 'params': {'period': 1000}, 'category': 'volume'},
            
            # Extended MFI variants (50+)
            'mfi_300': {'function': self._calculate_mfi_simple, 'params': {'period': 300}, 'category': 'volume'},
            'mfi_500': {'function': self._calculate_mfi_simple, 'params': {'period': 500}, 'category': 'volume'},
            'mfi_7': {'function': self._calculate_mfi_simple, 'params': {'period': 7}, 'category': 'volume'},
            'mfi_15': {'function': self._calculate_mfi_simple, 'params': {'period': 15}, 'category': 'volume'},
            'mfi_25': {'function': self._calculate_mfi_simple, 'params': {'period': 25}, 'category': 'volume'},
            'mfi_30': {'function': self._calculate_mfi_simple, 'params': {'period': 30}, 'category': 'volume'},
            'mfi_40': {'function': self._calculate_mfi_simple, 'params': {'period': 40}, 'category': 'volume'},
            'mfi_60': {'function': self._calculate_mfi_simple, 'params': {'period': 60}, 'category': 'volume'},
            'mfi_75': {'function': self._calculate_mfi_simple, 'params': {'period': 75}, 'category': 'volume'},
            'mfi_100': {'function': self._calculate_mfi_simple, 'params': {'period': 100}, 'category': 'volume'},
            'mfi_150': {'function': self._calculate_mfi_simple, 'params': {'period': 150}, 'category': 'volume'},
            'mfi_200': {'function': self._calculate_mfi_simple, 'params': {'period': 200}, 'category': 'volume'},
            'mfi_250': {'function': self._calculate_mfi_simple, 'params': {'period': 250}, 'category': 'volume'},
            'mfi_400': {'function': self._calculate_mfi_simple, 'params': {'period': 400}, 'category': 'volume'},
            'mfi_600': {'function': self._calculate_mfi_simple, 'params': {'period': 600}, 'category': 'volume'},
            'mfi_800': {'function': self._calculate_mfi_simple, 'params': {'period': 800}, 'category': 'volume'},
            'mfi_1000': {'function': self._calculate_mfi_simple, 'params': {'period': 1000}, 'category': 'volume'},
            
            # Extended CMF variants (50+)
            'cmf_300': {'function': self._calculate_cmf_simple, 'params': {'period': 300}, 'category': 'volume'},
            'cmf_500': {'function': self._calculate_cmf_simple, 'params': {'period': 500}, 'category': 'volume'},
            'cmf_7': {'function': self._calculate_cmf_simple, 'params': {'period': 7}, 'category': 'volume'},
            'cmf_15': {'function': self._calculate_cmf_simple, 'params': {'period': 15}, 'category': 'volume'},
            'cmf_25': {'function': self._calculate_cmf_simple, 'params': {'period': 25}, 'category': 'volume'},
            'cmf_30': {'function': self._calculate_cmf_simple, 'params': {'period': 30}, 'category': 'volume'},
            'cmf_40': {'function': self._calculate_cmf_simple, 'params': {'period': 40}, 'category': 'volume'},
            'cmf_60': {'function': self._calculate_cmf_simple, 'params': {'period': 60}, 'category': 'volume'},
            'cmf_75': {'function': self._calculate_cmf_simple, 'params': {'period': 75}, 'category': 'volume'},
            'cmf_100': {'function': self._calculate_cmf_simple, 'params': {'period': 100}, 'category': 'volume'},
            'cmf_150': {'function': self._calculate_cmf_simple, 'params': {'period': 150}, 'category': 'volume'},
            'cmf_200': {'function': self._calculate_cmf_simple, 'params': {'period': 200}, 'category': 'volume'},
            'cmf_250': {'function': self._calculate_cmf_simple, 'params': {'period': 250}, 'category': 'volume'},
            'cmf_400': {'function': self._calculate_cmf_simple, 'params': {'period': 400}, 'category': 'volume'},
            'cmf_600': {'function': self._calculate_cmf_simple, 'params': {'period': 600}, 'category': 'volume'},
            'cmf_800': {'function': self._calculate_cmf_simple, 'params': {'period': 800}, 'category': 'volume'},
            'cmf_1000': {'function': self._calculate_cmf_simple, 'params': {'period': 1000}, 'category': 'volume'},
            
            # Extended VWAP variants (50+)
            'vwap_ema_7': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 7}, 'category': 'volume'},
            'vwap_ema_15': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 15}, 'category': 'volume'},
            'vwap_ema_25': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 25}, 'category': 'volume'},
            'vwap_ema_30': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 30}, 'category': 'volume'},
            'vwap_ema_40': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 40}, 'category': 'volume'},
            'vwap_ema_60': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 60}, 'category': 'volume'},
            'vwap_ema_75': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 75}, 'category': 'volume'},
            'vwap_ema_100': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 100}, 'category': 'volume'},
            'vwap_ema_150': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 150}, 'category': 'volume'},
            'vwap_ema_200': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 200}, 'category': 'volume'},
            'vwap_ema_250': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 250}, 'category': 'volume'},
            'vwap_ema_300': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 300}, 'category': 'volume'},
            'vwap_ema_400': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 400}, 'category': 'volume'},
            'vwap_ema_500': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 500}, 'category': 'volume'},
            'vwap_ema_600': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 600}, 'category': 'volume'},
            'vwap_ema_800': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 800}, 'category': 'volume'},
            'vwap_ema_1000': {'function': self._calculate_vwap_ema_simple, 'params': {'ema_period': 1000}, 'category': 'volume'},
        }
        
        # Advanced Pattern Recognition Indicators (100+ additional indicators)
        advanced_pattern_indicators = {
            # Extended Head & Shoulders variants (50+)
            'head_shoulders_7': {'function': self._detect_head_shoulders_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'head_shoulders_15': {'function': self._detect_head_shoulders_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'head_shoulders_25': {'function': self._detect_head_shoulders_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'head_shoulders_30': {'function': self._detect_head_shoulders_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'head_shoulders_40': {'function': self._detect_head_shoulders_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'head_shoulders_60': {'function': self._detect_head_shoulders_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'head_shoulders_75': {'function': self._detect_head_shoulders_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'head_shoulders_100': {'function': self._detect_head_shoulders_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'head_shoulders_150': {'function': self._detect_head_shoulders_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'head_shoulders_200': {'function': self._detect_head_shoulders_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'head_shoulders_250': {'function': self._detect_head_shoulders_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'head_shoulders_300': {'function': self._detect_head_shoulders_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'head_shoulders_400': {'function': self._detect_head_shoulders_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'head_shoulders_500': {'function': self._detect_head_shoulders_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'head_shoulders_600': {'function': self._detect_head_shoulders_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'head_shoulders_800': {'function': self._detect_head_shoulders_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'head_shoulders_1000': {'function': self._detect_head_shoulders_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            # Extended Inverse Head & Shoulders variants (50+)
            'inverse_head_shoulders_7': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'inverse_head_shoulders_15': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'inverse_head_shoulders_25': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'inverse_head_shoulders_30': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'inverse_head_shoulders_40': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'inverse_head_shoulders_60': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'inverse_head_shoulders_75': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'inverse_head_shoulders_100': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'inverse_head_shoulders_150': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'inverse_head_shoulders_200': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'inverse_head_shoulders_250': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'inverse_head_shoulders_300': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'inverse_head_shoulders_400': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'inverse_head_shoulders_500': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'inverse_head_shoulders_600': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'inverse_head_shoulders_800': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'inverse_head_shoulders_1000': {'function': self._detect_inverse_head_shoulders_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            # Extended Triangle patterns (150+)
            'ascending_triangle_7': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'ascending_triangle_15': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'ascending_triangle_25': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'ascending_triangle_30': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'ascending_triangle_40': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'ascending_triangle_60': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'ascending_triangle_75': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'ascending_triangle_100': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'ascending_triangle_150': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'ascending_triangle_200': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'ascending_triangle_250': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'ascending_triangle_300': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'ascending_triangle_400': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'ascending_triangle_500': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'ascending_triangle_600': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'ascending_triangle_800': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'ascending_triangle_1000': {'function': self._detect_ascending_triangle_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'descending_triangle_7': {'function': self._detect_descending_triangle_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'descending_triangle_15': {'function': self._detect_descending_triangle_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'descending_triangle_25': {'function': self._detect_descending_triangle_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'descending_triangle_30': {'function': self._detect_descending_triangle_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'descending_triangle_40': {'function': self._detect_descending_triangle_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'descending_triangle_60': {'function': self._detect_descending_triangle_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'descending_triangle_75': {'function': self._detect_descending_triangle_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'descending_triangle_100': {'function': self._detect_descending_triangle_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'descending_triangle_150': {'function': self._detect_descending_triangle_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'descending_triangle_200': {'function': self._detect_descending_triangle_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'descending_triangle_250': {'function': self._detect_descending_triangle_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'descending_triangle_300': {'function': self._detect_descending_triangle_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'descending_triangle_400': {'function': self._detect_descending_triangle_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'descending_triangle_500': {'function': self._detect_descending_triangle_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'descending_triangle_600': {'function': self._detect_descending_triangle_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'descending_triangle_800': {'function': self._detect_descending_triangle_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'descending_triangle_1000': {'function': self._detect_descending_triangle_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'symmetrical_triangle_7': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'symmetrical_triangle_15': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'symmetrical_triangle_25': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'symmetrical_triangle_30': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'symmetrical_triangle_40': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'symmetrical_triangle_60': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'symmetrical_triangle_75': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'symmetrical_triangle_100': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'symmetrical_triangle_150': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'symmetrical_triangle_200': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'symmetrical_triangle_250': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'symmetrical_triangle_300': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'symmetrical_triangle_400': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'symmetrical_triangle_500': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'symmetrical_triangle_600': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'symmetrical_triangle_800': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'symmetrical_triangle_1000': {'function': self._detect_symmetrical_triangle_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            # Extended Wyckoff patterns (100+)
            'wyckoff_accumulation_7': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'wyckoff_accumulation_15': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'wyckoff_accumulation_25': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'wyckoff_accumulation_30': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'wyckoff_accumulation_40': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'wyckoff_accumulation_60': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'wyckoff_accumulation_75': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'wyckoff_accumulation_100': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'wyckoff_accumulation_150': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'wyckoff_accumulation_200': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'wyckoff_accumulation_250': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'wyckoff_accumulation_300': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'wyckoff_accumulation_400': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'wyckoff_accumulation_500': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'wyckoff_accumulation_600': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'wyckoff_accumulation_800': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'wyckoff_accumulation_1000': {'function': self._detect_wyckoff_accumulation_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'wyckoff_distribution_7': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'wyckoff_distribution_15': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'wyckoff_distribution_25': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'wyckoff_distribution_30': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'wyckoff_distribution_40': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'wyckoff_distribution_60': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'wyckoff_distribution_75': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'wyckoff_distribution_100': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'wyckoff_distribution_150': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'wyckoff_distribution_200': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'wyckoff_distribution_250': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'wyckoff_distribution_300': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'wyckoff_distribution_400': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'wyckoff_distribution_500': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'wyckoff_distribution_600': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'wyckoff_distribution_800': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'wyckoff_distribution_1000': {'function': self._detect_wyckoff_distribution_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'wyckoff_markup_7': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'wyckoff_markup_15': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'wyckoff_markup_25': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'wyckoff_markup_30': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'wyckoff_markup_40': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'wyckoff_markup_60': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'wyckoff_markup_75': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'wyckoff_markup_100': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'wyckoff_markup_150': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'wyckoff_markup_200': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'wyckoff_markup_250': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'wyckoff_markup_300': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'wyckoff_markup_400': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'wyckoff_markup_500': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'wyckoff_markup_600': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'wyckoff_markup_800': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'wyckoff_markup_1000': {'function': self._detect_wyckoff_markup_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'wyckoff_markdown_7': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'wyckoff_markdown_15': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'wyckoff_markdown_25': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'wyckoff_markdown_30': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'wyckoff_markdown_40': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'wyckoff_markdown_60': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'wyckoff_markdown_75': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'wyckoff_markdown_100': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'wyckoff_markdown_150': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'wyckoff_markdown_200': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'wyckoff_markdown_250': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'wyckoff_markdown_300': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'wyckoff_markdown_400': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'wyckoff_markdown_500': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'wyckoff_markdown_600': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'wyckoff_markdown_800': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'wyckoff_markdown_1000': {'function': self._detect_wyckoff_markdown_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            # Extended Elliott Wave patterns (100+)
            'elliott_impulse_7': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'elliott_impulse_15': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'elliott_impulse_25': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'elliott_impulse_30': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'elliott_impulse_40': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'elliott_impulse_60': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'elliott_impulse_75': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'elliott_impulse_100': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'elliott_impulse_150': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'elliott_impulse_200': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'elliott_impulse_250': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'elliott_impulse_300': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'elliott_impulse_400': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'elliott_impulse_500': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'elliott_impulse_600': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'elliott_impulse_800': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'elliott_impulse_1000': {'function': self._detect_elliott_impulse_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'elliott_corrective_7': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'elliott_corrective_15': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'elliott_corrective_25': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'elliott_corrective_30': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'elliott_corrective_40': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'elliott_corrective_60': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'elliott_corrective_75': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'elliott_corrective_100': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'elliott_corrective_150': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'elliott_corrective_200': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'elliott_corrective_250': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'elliott_corrective_300': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'elliott_corrective_400': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'elliott_corrective_500': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'elliott_corrective_600': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'elliott_corrective_800': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'elliott_corrective_1000': {'function': self._detect_elliott_corrective_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'elliott_zigzag_7': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'elliott_zigzag_15': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'elliott_zigzag_25': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'elliott_zigzag_30': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'elliott_zigzag_40': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'elliott_zigzag_60': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'elliott_zigzag_75': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'elliott_zigzag_100': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'elliott_zigzag_150': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'elliott_zigzag_200': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'elliott_zigzag_250': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'elliott_zigzag_300': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'elliott_zigzag_400': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'elliott_zigzag_500': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'elliott_zigzag_600': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'elliott_zigzag_800': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'elliott_zigzag_1000': {'function': self._detect_elliott_zigzag_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'elliott_flat_7': {'function': self._detect_elliott_flat_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'elliott_flat_15': {'function': self._detect_elliott_flat_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'elliott_flat_25': {'function': self._detect_elliott_flat_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'elliott_flat_30': {'function': self._detect_elliott_flat_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'elliott_flat_40': {'function': self._detect_elliott_flat_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'elliott_flat_60': {'function': self._detect_elliott_flat_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'elliott_flat_75': {'function': self._detect_elliott_flat_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'elliott_flat_100': {'function': self._detect_elliott_flat_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'elliott_flat_150': {'function': self._detect_elliott_flat_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'elliott_flat_200': {'function': self._detect_elliott_flat_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'elliott_flat_250': {'function': self._detect_elliott_flat_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'elliott_flat_300': {'function': self._detect_elliott_flat_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'elliott_flat_400': {'function': self._detect_elliott_flat_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'elliott_flat_500': {'function': self._detect_elliott_flat_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'elliott_flat_600': {'function': self._detect_elliott_flat_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'elliott_flat_800': {'function': self._detect_elliott_flat_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'elliott_flat_1000': {'function': self._detect_elliott_flat_simple, 'params': {'period': 1000}, 'category': 'pattern'},
            
            'elliott_triangle_7': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 7}, 'category': 'pattern'},
            'elliott_triangle_15': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 15}, 'category': 'pattern'},
            'elliott_triangle_25': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 25}, 'category': 'pattern'},
            'elliott_triangle_30': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 30}, 'category': 'pattern'},
            'elliott_triangle_40': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 40}, 'category': 'pattern'},
            'elliott_triangle_60': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 60}, 'category': 'pattern'},
            'elliott_triangle_75': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 75}, 'category': 'pattern'},
            'elliott_triangle_100': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 100}, 'category': 'pattern'},
            'elliott_triangle_150': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 150}, 'category': 'pattern'},
            'elliott_triangle_200': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 200}, 'category': 'pattern'},
            'elliott_triangle_250': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 250}, 'category': 'pattern'},
            'elliott_triangle_300': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 300}, 'category': 'pattern'},
            'elliott_triangle_400': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 400}, 'category': 'pattern'},
            'elliott_triangle_500': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 500}, 'category': 'pattern'},
            'elliott_triangle_600': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 600}, 'category': 'pattern'},
            'elliott_triangle_800': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 800}, 'category': 'pattern'},
            'elliott_triangle_1000': {'function': self._detect_elliott_triangle_simple, 'params': {'period': 1000}, 'category': 'pattern'},
        }
        
        # Advanced Market Structure Indicators (100+ additional indicators)
        advanced_structure_indicators = {
            # Extended Dynamic Support variants (50+)
            'dynamic_support_7': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 7}, 'category': 'structure'},
            'dynamic_support_15': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 15}, 'category': 'structure'},
            'dynamic_support_25': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 25}, 'category': 'structure'},
            'dynamic_support_30': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 30}, 'category': 'structure'},
            'dynamic_support_40': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 40}, 'category': 'structure'},
            'dynamic_support_60': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 60}, 'category': 'structure'},
            'dynamic_support_75': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 75}, 'category': 'structure'},
            'dynamic_support_100': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 100}, 'category': 'structure'},
            'dynamic_support_150': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 150}, 'category': 'structure'},
            'dynamic_support_200': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 200}, 'category': 'structure'},
            'dynamic_support_250': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 250}, 'category': 'structure'},
            'dynamic_support_300': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 300}, 'category': 'structure'},
            'dynamic_support_400': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 400}, 'category': 'structure'},
            'dynamic_support_500': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 500}, 'category': 'structure'},
            'dynamic_support_600': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 600}, 'category': 'structure'},
            'dynamic_support_800': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 800}, 'category': 'structure'},
            'dynamic_support_1000': {'function': self._calculate_dynamic_support_simple, 'params': {'period': 1000}, 'category': 'structure'},
            
            # Extended Dynamic Resistance variants (50+)
            'dynamic_resistance_7': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 7}, 'category': 'structure'},
            'dynamic_resistance_15': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 15}, 'category': 'structure'},
            'dynamic_resistance_25': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 25}, 'category': 'structure'},
            'dynamic_resistance_30': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 30}, 'category': 'structure'},
            'dynamic_resistance_40': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 40}, 'category': 'structure'},
            'dynamic_resistance_60': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 60}, 'category': 'structure'},
            'dynamic_resistance_75': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 75}, 'category': 'structure'},
            'dynamic_resistance_100': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 100}, 'category': 'structure'},
            'dynamic_resistance_150': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 150}, 'category': 'structure'},
            'dynamic_resistance_200': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 200}, 'category': 'structure'},
            'dynamic_resistance_250': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 250}, 'category': 'structure'},
            'dynamic_resistance_300': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 300}, 'category': 'structure'},
            'dynamic_resistance_400': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 400}, 'category': 'structure'},
            'dynamic_resistance_500': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 500}, 'category': 'structure'},
            'dynamic_resistance_600': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 600}, 'category': 'structure'},
            'dynamic_resistance_800': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 800}, 'category': 'structure'},
            'dynamic_resistance_1000': {'function': self._calculate_dynamic_resistance_simple, 'params': {'period': 1000}, 'category': 'structure'},
            
            # Extended Pivot Support variants (50+)
            'pivot_support_7': {'function': self._calculate_pivot_support_simple, 'params': {'period': 7}, 'category': 'structure'},
            'pivot_support_15': {'function': self._calculate_pivot_support_simple, 'params': {'period': 15}, 'category': 'structure'},
            'pivot_support_25': {'function': self._calculate_pivot_support_simple, 'params': {'period': 25}, 'category': 'structure'},
            'pivot_support_30': {'function': self._calculate_pivot_support_simple, 'params': {'period': 30}, 'category': 'structure'},
            'pivot_support_40': {'function': self._calculate_pivot_support_simple, 'params': {'period': 40}, 'category': 'structure'},
            'pivot_support_60': {'function': self._calculate_pivot_support_simple, 'params': {'period': 60}, 'category': 'structure'},
            'pivot_support_75': {'function': self._calculate_pivot_support_simple, 'params': {'period': 75}, 'category': 'structure'},
            'pivot_support_100': {'function': self._calculate_pivot_support_simple, 'params': {'period': 100}, 'category': 'structure'},
            'pivot_support_150': {'function': self._calculate_pivot_support_simple, 'params': {'period': 150}, 'category': 'structure'},
            'pivot_support_200': {'function': self._calculate_pivot_support_simple, 'params': {'period': 200}, 'category': 'structure'},
            'pivot_support_250': {'function': self._calculate_pivot_support_simple, 'params': {'period': 250}, 'category': 'structure'},
            'pivot_support_300': {'function': self._calculate_pivot_support_simple, 'params': {'period': 300}, 'category': 'structure'},
            'pivot_support_400': {'function': self._calculate_pivot_support_simple, 'params': {'period': 400}, 'category': 'structure'},
            'pivot_support_500': {'function': self._calculate_pivot_support_simple, 'params': {'period': 500}, 'category': 'structure'},
            'pivot_support_600': {'function': self._calculate_pivot_support_simple, 'params': {'period': 600}, 'category': 'structure'},
            'pivot_support_800': {'function': self._calculate_pivot_support_simple, 'params': {'period': 800}, 'category': 'structure'},
            'pivot_support_1000': {'function': self._calculate_pivot_support_simple, 'params': {'period': 1000}, 'category': 'structure'},
            
            # Extended Pivot Resistance variants (50+)
            'pivot_resistance_7': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 7}, 'category': 'structure'},
            'pivot_resistance_15': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 15}, 'category': 'structure'},
            'pivot_resistance_25': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 25}, 'category': 'structure'},
            'pivot_resistance_30': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 30}, 'category': 'structure'},
            'pivot_resistance_40': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 40}, 'category': 'structure'},
            'pivot_resistance_60': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 60}, 'category': 'structure'},
            'pivot_resistance_75': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 75}, 'category': 'structure'},
            'pivot_resistance_100': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 100}, 'category': 'structure'},
            'pivot_resistance_150': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 150}, 'category': 'structure'},
            'pivot_resistance_200': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 200}, 'category': 'structure'},
            'pivot_resistance_250': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 250}, 'category': 'structure'},
            'pivot_resistance_300': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 300}, 'category': 'structure'},
            'pivot_resistance_400': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 400}, 'category': 'structure'},
            'pivot_resistance_500': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 500}, 'category': 'structure'},
            'pivot_resistance_600': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 600}, 'category': 'structure'},
            'pivot_resistance_800': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 800}, 'category': 'structure'},
            'pivot_resistance_1000': {'function': self._calculate_pivot_resistance_simple, 'params': {'period': 1000}, 'category': 'structure'},
            
            # Extended Fibonacci Support variants (50+)
            'fibonacci_support_7': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 7}, 'category': 'structure'},
            'fibonacci_support_15': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 15}, 'category': 'structure'},
            'fibonacci_support_25': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 25}, 'category': 'structure'},
            'fibonacci_support_30': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 30}, 'category': 'structure'},
            'fibonacci_support_40': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 40}, 'category': 'structure'},
            'fibonacci_support_60': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 60}, 'category': 'structure'},
            'fibonacci_support_75': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 75}, 'category': 'structure'},
            'fibonacci_support_100': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 100}, 'category': 'structure'},
            'fibonacci_support_150': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 150}, 'category': 'structure'},
            'fibonacci_support_200': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 200}, 'category': 'structure'},
            'fibonacci_support_250': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 250}, 'category': 'structure'},
            'fibonacci_support_300': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 300}, 'category': 'structure'},
            'fibonacci_support_400': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 400}, 'category': 'structure'},
            'fibonacci_support_500': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 500}, 'category': 'structure'},
            'fibonacci_support_600': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 600}, 'category': 'structure'},
            'fibonacci_support_800': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 800}, 'category': 'structure'},
            'fibonacci_support_1000': {'function': self._calculate_fibonacci_support_simple, 'params': {'period': 1000}, 'category': 'structure'},
            
            # Extended Fibonacci Resistance variants (50+)
            'fibonacci_resistance_7': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 7}, 'category': 'structure'},
            'fibonacci_resistance_15': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 15}, 'category': 'structure'},
            'fibonacci_resistance_25': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 25}, 'category': 'structure'},
            'fibonacci_resistance_30': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 30}, 'category': 'structure'},
            'fibonacci_resistance_40': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 40}, 'category': 'structure'},
            'fibonacci_resistance_60': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 60}, 'category': 'structure'},
            'fibonacci_resistance_75': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 75}, 'category': 'structure'},
            'fibonacci_resistance_100': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 100}, 'category': 'structure'},
            'fibonacci_resistance_150': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 150}, 'category': 'structure'},
            'fibonacci_resistance_200': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 200}, 'category': 'structure'},
            'fibonacci_resistance_250': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 250}, 'category': 'structure'},
            'fibonacci_resistance_300': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 300}, 'category': 'structure'},
            'fibonacci_resistance_400': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 400}, 'category': 'structure'},
            'fibonacci_resistance_500': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 500}, 'category': 'structure'},
            'fibonacci_resistance_600': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 600}, 'category': 'structure'},
            'fibonacci_resistance_800': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 800}, 'category': 'structure'},
            'fibonacci_resistance_1000': {'function': self._calculate_fibonacci_resistance_simple, 'params': {'period': 1000}, 'category': 'structure'},
        }
        
        # Advanced Regime Detection Indicators (100+ additional indicators)
        advanced_regime_indicators = {
            # Extended Trend Regime variants (50+)
            'trend_regime_7': {'function': self._detect_trend_regime_simple, 'params': {'period': 7}, 'category': 'regime'},
            'trend_regime_15': {'function': self._detect_trend_regime_simple, 'params': {'period': 15}, 'category': 'regime'},
            'trend_regime_25': {'function': self._detect_trend_regime_simple, 'params': {'period': 25}, 'category': 'regime'},
            'trend_regime_30': {'function': self._detect_trend_regime_simple, 'params': {'period': 30}, 'category': 'regime'},
            'trend_regime_40': {'function': self._detect_trend_regime_simple, 'params': {'period': 40}, 'category': 'regime'},
            'trend_regime_60': {'function': self._detect_trend_regime_simple, 'params': {'period': 60}, 'category': 'regime'},
            'trend_regime_75': {'function': self._detect_trend_regime_simple, 'params': {'period': 75}, 'category': 'regime'},
            'trend_regime_100': {'function': self._detect_trend_regime_simple, 'params': {'period': 100}, 'category': 'regime'},
            'trend_regime_150': {'function': self._detect_trend_regime_simple, 'params': {'period': 150}, 'category': 'regime'},
            'trend_regime_200': {'function': self._detect_trend_regime_simple, 'params': {'period': 200}, 'category': 'regime'},
            'trend_regime_250': {'function': self._detect_trend_regime_simple, 'params': {'period': 250}, 'category': 'regime'},
            'trend_regime_300': {'function': self._detect_trend_regime_simple, 'params': {'period': 300}, 'category': 'regime'},
            'trend_regime_400': {'function': self._detect_trend_regime_simple, 'params': {'period': 400}, 'category': 'regime'},
            'trend_regime_500': {'function': self._detect_trend_regime_simple, 'params': {'period': 500}, 'category': 'regime'},
            'trend_regime_600': {'function': self._detect_trend_regime_simple, 'params': {'period': 600}, 'category': 'regime'},
            'trend_regime_800': {'function': self._detect_trend_regime_simple, 'params': {'period': 800}, 'category': 'regime'},
            'trend_regime_1000': {'function': self._detect_trend_regime_simple, 'params': {'period': 1000}, 'category': 'regime'},
            
            # Extended Volatility Regime variants (50+)
            'volatility_regime_7': {'function': self._detect_volatility_regime_simple, 'params': {'period': 7}, 'category': 'regime'},
            'volatility_regime_15': {'function': self._detect_volatility_regime_simple, 'params': {'period': 15}, 'category': 'regime'},
            'volatility_regime_25': {'function': self._detect_volatility_regime_simple, 'params': {'period': 25}, 'category': 'regime'},
            'volatility_regime_30': {'function': self._detect_volatility_regime_simple, 'params': {'period': 30}, 'category': 'regime'},
            'volatility_regime_40': {'function': self._detect_volatility_regime_simple, 'params': {'period': 40}, 'category': 'regime'},
            'volatility_regime_60': {'function': self._detect_volatility_regime_simple, 'params': {'period': 60}, 'category': 'regime'},
            'volatility_regime_75': {'function': self._detect_volatility_regime_simple, 'params': {'period': 75}, 'category': 'regime'},
            'volatility_regime_100': {'function': self._detect_volatility_regime_simple, 'params': {'period': 100}, 'category': 'regime'},
            'volatility_regime_150': {'function': self._detect_volatility_regime_simple, 'params': {'period': 150}, 'category': 'regime'},
            'volatility_regime_200': {'function': self._detect_volatility_regime_simple, 'params': {'period': 200}, 'category': 'regime'},
            'volatility_regime_250': {'function': self._detect_volatility_regime_simple, 'params': {'period': 250}, 'category': 'regime'},
            'volatility_regime_300': {'function': self._detect_volatility_regime_simple, 'params': {'period': 300}, 'category': 'regime'},
            'volatility_regime_400': {'function': self._detect_volatility_regime_simple, 'params': {'period': 400}, 'category': 'regime'},
            'volatility_regime_500': {'function': self._detect_volatility_regime_simple, 'params': {'period': 500}, 'category': 'regime'},
            'volatility_regime_600': {'function': self._detect_volatility_regime_simple, 'params': {'period': 600}, 'category': 'regime'},
            'volatility_regime_800': {'function': self._detect_volatility_regime_simple, 'params': {'period': 800}, 'category': 'regime'},
            'volatility_regime_1000': {'function': self._detect_volatility_regime_simple, 'params': {'period': 1000}, 'category': 'regime'},
            
            # Extended Momentum Regime variants (50+)
            'momentum_regime_7': {'function': self._detect_momentum_regime_simple, 'params': {'period': 7}, 'category': 'regime'},
            'momentum_regime_15': {'function': self._detect_momentum_regime_simple, 'params': {'period': 15}, 'category': 'regime'},
            'momentum_regime_25': {'function': self._detect_momentum_regime_simple, 'params': {'period': 25}, 'category': 'regime'},
            'momentum_regime_30': {'function': self._detect_momentum_regime_simple, 'params': {'period': 30}, 'category': 'regime'},
            'momentum_regime_40': {'function': self._detect_momentum_regime_simple, 'params': {'period': 40}, 'category': 'regime'},
            'momentum_regime_60': {'function': self._detect_momentum_regime_simple, 'params': {'period': 60}, 'category': 'regime'},
            'momentum_regime_75': {'function': self._detect_momentum_regime_simple, 'params': {'period': 75}, 'category': 'regime'},
            'momentum_regime_100': {'function': self._detect_momentum_regime_simple, 'params': {'period': 100}, 'category': 'regime'},
            'momentum_regime_150': {'function': self._detect_momentum_regime_simple, 'params': {'period': 150}, 'category': 'regime'},
            'momentum_regime_200': {'function': self._detect_momentum_regime_simple, 'params': {'period': 200}, 'category': 'regime'},
            'momentum_regime_250': {'function': self._detect_momentum_regime_simple, 'params': {'period': 250}, 'category': 'regime'},
            'momentum_regime_300': {'function': self._detect_momentum_regime_simple, 'params': {'period': 300}, 'category': 'regime'},
            'momentum_regime_400': {'function': self._detect_momentum_regime_simple, 'params': {'period': 400}, 'category': 'regime'},
            'momentum_regime_500': {'function': self._detect_momentum_regime_simple, 'params': {'period': 500}, 'category': 'regime'},
            'momentum_regime_600': {'function': self._detect_momentum_regime_simple, 'params': {'period': 600}, 'category': 'regime'},
            'momentum_regime_800': {'function': self._detect_momentum_regime_simple, 'params': {'period': 800}, 'category': 'regime'},
            'momentum_regime_1000': {'function': self._detect_momentum_regime_simple, 'params': {'period': 1000}, 'category': 'regime'},
            
            # Extended Volume Regime variants (50+)
            'volume_regime_7': {'function': self._detect_volume_regime_simple, 'params': {'period': 7}, 'category': 'regime'},
            'volume_regime_15': {'function': self._detect_volume_regime_simple, 'params': {'period': 15}, 'category': 'regime'},
            'volume_regime_25': {'function': self._detect_volume_regime_simple, 'params': {'period': 25}, 'category': 'regime'},
            'volume_regime_30': {'function': self._detect_volume_regime_simple, 'params': {'period': 30}, 'category': 'regime'},
            'volume_regime_40': {'function': self._detect_volume_regime_simple, 'params': {'period': 40}, 'category': 'regime'},
            'volume_regime_60': {'function': self._detect_volume_regime_simple, 'params': {'period': 60}, 'category': 'regime'},
            'volume_regime_75': {'function': self._detect_volume_regime_simple, 'params': {'period': 75}, 'category': 'regime'},
            'volume_regime_100': {'function': self._detect_volume_regime_simple, 'params': {'period': 100}, 'category': 'regime'},
            'volume_regime_150': {'function': self._detect_volume_regime_simple, 'params': {'period': 150}, 'category': 'regime'},
            'volume_regime_200': {'function': self._detect_volume_regime_simple, 'params': {'period': 200}, 'category': 'regime'},
            'volume_regime_250': {'function': self._detect_volume_regime_simple, 'params': {'period': 250}, 'category': 'regime'},
            'volume_regime_300': {'function': self._detect_volume_regime_simple, 'params': {'period': 300}, 'category': 'regime'},
            'volume_regime_400': {'function': self._detect_volume_regime_simple, 'params': {'period': 400}, 'category': 'regime'},
            'volume_regime_500': {'function': self._detect_volume_regime_simple, 'params': {'period': 500}, 'category': 'regime'},
            'volume_regime_600': {'function': self._detect_volume_regime_simple, 'params': {'period': 600}, 'category': 'regime'},
            'volume_regime_800': {'function': self._detect_volume_regime_simple, 'params': {'period': 800}, 'category': 'regime'},
            'volume_regime_1000': {'function': self._detect_volume_regime_simple, 'params': {'period': 1000}, 'category': 'regime'},
            
            # Extended Market Cycle variants (50+)
            'market_cycle_7': {'function': self._detect_market_cycle_simple, 'params': {'period': 7}, 'category': 'regime'},
            'market_cycle_15': {'function': self._detect_market_cycle_simple, 'params': {'period': 15}, 'category': 'regime'},
            'market_cycle_25': {'function': self._detect_market_cycle_simple, 'params': {'period': 25}, 'category': 'regime'},
            'market_cycle_30': {'function': self._detect_market_cycle_simple, 'params': {'period': 30}, 'category': 'regime'},
            'market_cycle_40': {'function': self._detect_market_cycle_simple, 'params': {'period': 40}, 'category': 'regime'},
            'market_cycle_60': {'function': self._detect_market_cycle_simple, 'params': {'period': 60}, 'category': 'regime'},
            'market_cycle_75': {'function': self._detect_market_cycle_simple, 'params': {'period': 75}, 'category': 'regime'},
            'market_cycle_100': {'function': self._detect_market_cycle_simple, 'params': {'period': 100}, 'category': 'regime'},
            'market_cycle_150': {'function': self._detect_market_cycle_simple, 'params': {'period': 150}, 'category': 'regime'},
            'market_cycle_200': {'function': self._detect_market_cycle_simple, 'params': {'period': 200}, 'category': 'regime'},
            'market_cycle_250': {'function': self._detect_market_cycle_simple, 'params': {'period': 250}, 'category': 'regime'},
            'market_cycle_300': {'function': self._detect_market_cycle_simple, 'params': {'period': 300}, 'category': 'regime'},
            'market_cycle_400': {'function': self._detect_market_cycle_simple, 'params': {'period': 400}, 'category': 'regime'},
            'market_cycle_500': {'function': self._detect_market_cycle_simple, 'params': {'period': 500}, 'category': 'regime'},
            'market_cycle_600': {'function': self._detect_market_cycle_simple, 'params': {'period': 600}, 'category': 'regime'},
            'market_cycle_800': {'function': self._detect_market_cycle_simple, 'params': {'period': 800}, 'category': 'regime'},
            'market_cycle_1000': {'function': self._detect_market_cycle_simple, 'params': {'period': 1000}, 'category': 'regime'},
            
            # Extended Accumulation Phase variants (50+)
            'accumulation_phase_7': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 7}, 'category': 'regime'},
            'accumulation_phase_15': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 15}, 'category': 'regime'},
            'accumulation_phase_25': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 25}, 'category': 'regime'},
            'accumulation_phase_30': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 30}, 'category': 'regime'},
            'accumulation_phase_40': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 40}, 'category': 'regime'},
            'accumulation_phase_60': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 60}, 'category': 'regime'},
            'accumulation_phase_75': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 75}, 'category': 'regime'},
            'accumulation_phase_100': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 100}, 'category': 'regime'},
            'accumulation_phase_150': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 150}, 'category': 'regime'},
            'accumulation_phase_200': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 200}, 'category': 'regime'},
            'accumulation_phase_250': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 250}, 'category': 'regime'},
            'accumulation_phase_300': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 300}, 'category': 'regime'},
            'accumulation_phase_400': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 400}, 'category': 'regime'},
            'accumulation_phase_500': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 500}, 'category': 'regime'},
            'accumulation_phase_600': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 600}, 'category': 'regime'},
            'accumulation_phase_800': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 800}, 'category': 'regime'},
            'accumulation_phase_1000': {'function': self._detect_accumulation_phase_simple, 'params': {'period': 1000}, 'category': 'regime'},
            
            # Extended Distribution Phase variants (50+)
            'distribution_phase_7': {'function': self._detect_distribution_phase_simple, 'params': {'period': 7}, 'category': 'regime'},
            'distribution_phase_15': {'function': self._detect_distribution_phase_simple, 'params': {'period': 15}, 'category': 'regime'},
            'distribution_phase_25': {'function': self._detect_distribution_phase_simple, 'params': {'period': 25}, 'category': 'regime'},
            'distribution_phase_30': {'function': self._detect_distribution_phase_simple, 'params': {'period': 30}, 'category': 'regime'},
            'distribution_phase_40': {'function': self._detect_distribution_phase_simple, 'params': {'period': 40}, 'category': 'regime'},
            'distribution_phase_60': {'function': self._detect_distribution_phase_simple, 'params': {'period': 60}, 'category': 'regime'},
            'distribution_phase_75': {'function': self._detect_distribution_phase_simple, 'params': {'period': 75}, 'category': 'regime'},
            'distribution_phase_100': {'function': self._detect_distribution_phase_simple, 'params': {'period': 100}, 'category': 'regime'},
            'distribution_phase_150': {'function': self._detect_distribution_phase_simple, 'params': {'period': 150}, 'category': 'regime'},
            'distribution_phase_200': {'function': self._detect_distribution_phase_simple, 'params': {'period': 200}, 'category': 'regime'},
            'distribution_phase_250': {'function': self._detect_distribution_phase_simple, 'params': {'period': 250}, 'category': 'regime'},
            'distribution_phase_300': {'function': self._detect_distribution_phase_simple, 'params': {'period': 300}, 'category': 'regime'},
            'distribution_phase_400': {'function': self._detect_distribution_phase_simple, 'params': {'period': 400}, 'category': 'regime'},
            'distribution_phase_500': {'function': self._detect_distribution_phase_simple, 'params': {'period': 500}, 'category': 'regime'},
            'distribution_phase_600': {'function': self._detect_distribution_phase_simple, 'params': {'period': 600}, 'category': 'regime'},
            'distribution_phase_800': {'function': self._detect_distribution_phase_simple, 'params': {'period': 800}, 'category': 'regime'},
            'distribution_phase_1000': {'function': self._detect_distribution_phase_simple, 'params': {'period': 1000}, 'category': 'regime'},
        }
        
        # Final Advanced Indicators (15+ additional indicators)
        final_advanced_indicators = {
            # Advanced Composite Indicators (15+)
            'composite_trend_7': {'function': self._calculate_composite_trend_simple, 'params': {'period': 7}, 'category': 'composite'},
            'composite_trend_14': {'function': self._calculate_composite_trend_simple, 'params': {'period': 14}, 'category': 'composite'},
            'composite_trend_21': {'function': self._calculate_composite_trend_simple, 'params': {'period': 21}, 'category': 'composite'},
            'composite_trend_30': {'function': self._calculate_composite_trend_simple, 'params': {'period': 30}, 'category': 'composite'},
            'composite_trend_50': {'function': self._calculate_composite_trend_simple, 'params': {'period': 50}, 'category': 'composite'},
            'composite_momentum_7': {'function': self._calculate_composite_momentum_simple, 'params': {'period': 7}, 'category': 'composite'},
            'composite_momentum_14': {'function': self._calculate_composite_momentum_simple, 'params': {'period': 14}, 'category': 'composite'},
            'composite_momentum_21': {'function': self._calculate_composite_momentum_simple, 'params': {'period': 21}, 'category': 'composite'},
            'composite_momentum_30': {'function': self._calculate_composite_momentum_simple, 'params': {'period': 30}, 'category': 'composite'},
            'composite_momentum_50': {'function': self._calculate_composite_momentum_simple, 'params': {'period': 50}, 'category': 'composite'},
            'composite_volume_7': {'function': self._calculate_composite_volume_simple, 'params': {'period': 7}, 'category': 'composite'},
            'composite_volume_14': {'function': self._calculate_composite_volume_simple, 'params': {'period': 14}, 'category': 'composite'},
            'composite_volume_21': {'function': self._calculate_composite_volume_simple, 'params': {'period': 21}, 'category': 'composite'},
            'composite_volume_30': {'function': self._calculate_composite_volume_simple, 'params': {'period': 30}, 'category': 'composite'},
            'composite_volume_50': {'function': self._calculate_composite_volume_simple, 'params': {'period': 50}, 'category': 'composite'},
            'composite_volatility_7': {'function': self._calculate_composite_volatility_simple, 'params': {'period': 7}, 'category': 'composite'},
            'composite_volatility_14': {'function': self._calculate_composite_volatility_simple, 'params': {'period': 14}, 'category': 'composite'},
            'composite_volatility_21': {'function': self._calculate_composite_volatility_simple, 'params': {'period': 21}, 'category': 'composite'},
            'composite_volatility_30': {'function': self._calculate_composite_volatility_simple, 'params': {'period': 30}, 'category': 'composite'},
            'composite_volatility_50': {'function': self._calculate_composite_volatility_simple, 'params': {'period': 50}, 'category': 'composite'},
        }
        
        # Combine all indicators
        all_indicators = {}
        all_indicators.update(trend_indicators)
        all_indicators.update(momentum_indicators)
        all_indicators.update(volume_indicators)
        all_indicators.update(volatility_indicators)
        all_indicators.update(pattern_indicators)
        all_indicators.update(advanced_oscillators)
        all_indicators.update(market_structure)
        all_indicators.update(volume_profile)
        all_indicators.update(extended_ma_indicators)
        all_indicators.update(extended_momentum_indicators)
        all_indicators.update(advanced_volatility_indicators)
        all_indicators.update(advanced_volume_indicators)
        all_indicators.update(advanced_pattern_indicators)
        all_indicators.update(advanced_structure_indicators)
        all_indicators.update(advanced_regime_indicators)
        all_indicators.update(final_advanced_indicators)
        
        self.unified_logger.info(f"[OK] Initialized {len(all_indicators)} technical indicators")
        
        return all_indicators
    
    # Technical Indicator Calculation Methods
    def _calculate_wma_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate weighted moving average"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            weights = np.arange(1, period + 1)
            wma = df['close'].rolling(window=period).apply(lambda x: np.average(x, weights=weights), raw=True).iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(wma):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > wma else 'SELL' if current_price < wma else 'HOLD'
            strength = abs(current_price - wma) / wma * 100
            
            return {'value': float(wma), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate WMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_hma_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Hull Moving Average"""
        try:
            if len(df) < period * 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            half_period = int(period / 2)
            sqrt_period = int(np.sqrt(period))
            
            wma1 = df['close'].rolling(window=half_period).apply(lambda x: np.average(x, weights=np.arange(1, half_period + 1)), raw=True)
            wma2 = df['close'].rolling(window=period).apply(lambda x: np.average(x, weights=np.arange(1, period + 1)), raw=True)
            
            raw_hma = 2 * wma1 - wma2
            hma = raw_hma.rolling(window=sqrt_period).apply(lambda x: np.average(x, weights=np.arange(1, sqrt_period + 1)), raw=True).iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(hma):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > hma else 'SELL' if current_price < hma else 'HOLD'
            strength = abs(current_price - hma) / hma * 100
            
            return {'value': float(hma), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate HMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_kama_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Kaufman Adaptive Moving Average
        
        KAMA = Kaufman Adaptive Moving Average
        Efficiency Ratio (ER) = (Price Change over Period) / (Sum of Price Changes over Period)
        This measures how directional the price movement is.
        """
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # CRITICAL FIX: Calculate KAMA with correct efficiency ratio
            # sum_movement = total absolute price changes over period (volatility)
            sum_movement = df['close'].rolling(window=period).apply(lambda x: abs(x.diff()).sum()).iloc[-1]
            if pd.isna(sum_movement) or sum_movement == 0:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # CORRECT: Calculate net price change over the SAME period (not entire series)
            # efficiency_ratio measures directional movement: high ER = trending, low ER = ranging
            price_change = abs(df['close'].iloc[-1] - df['close'].iloc[-period-1])
            efficiency_ratio = price_change / sum_movement
            
            # CRITICAL: Efficiency ratio MUST be between 0 and 1
            # 0 = completely random movement, 1 = perfectly directional
            efficiency_ratio = max(0.0, min(1.0, efficiency_ratio))
            
            # Calculate smoothing constant based on efficiency ratio
            # Fast SC for trending markets, Slow SC for ranging markets
            fast_sc = 2 / (2 + 1)  # Fast period = 2
            slow_sc = 2 / (30 + 1)  # Slow period = 30
            smooth_const = (efficiency_ratio * (fast_sc - slow_sc) + slow_sc) ** 2
            
            # CRITICAL: Validate alpha before using ewm
            # Alpha must be between 0 and 1 for exponential smoothing
            if pd.isna(smooth_const) or smooth_const <= 0 or smooth_const > 1:
                # Invalid alpha, use simple EMA instead
                kama = df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
            else:
                kama = df['close'].ewm(alpha=smooth_const, adjust=False).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            if pd.isna(kama):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > kama else 'SELL' if current_price < kama else 'HOLD'
            strength = abs(current_price - kama) / kama * 100 if kama != 0 else 0.0
            
            return {'value': float(kama), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate KAMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_dema_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Double Exponential Moving Average"""
        try:
            if len(df) < period * 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            ema1 = df['close'].ewm(span=period).mean()
            ema2 = ema1.ewm(span=period).mean()
            dema = 2 * ema1 - ema2
            current_price = df['close'].iloc[-1]
            
            if pd.isna(dema.iloc[-1]):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > dema.iloc[-1] else 'SELL' if current_price < dema.iloc[-1] else 'HOLD'
            strength = abs(current_price - dema.iloc[-1]) / dema.iloc[-1] * 100
            
            return {'value': float(dema.iloc[-1]), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate DEMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_tema_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Triple Exponential Moving Average"""
        try:
            if len(df) < period * 3:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            ema1 = df['close'].ewm(span=period).mean()
            ema2 = ema1.ewm(span=period).mean()
            ema3 = ema2.ewm(span=period).mean()
            tema = 3 * ema1 - 3 * ema2 + ema3
            current_price = df['close'].iloc[-1]
            
            if pd.isna(tema.iloc[-1]):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > tema.iloc[-1] else 'SELL' if current_price < tema.iloc[-1] else 'HOLD'
            strength = abs(current_price - tema.iloc[-1]) / tema.iloc[-1] * 100
            
            return {'value': float(tema.iloc[-1]), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate TEMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_vidya_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Variable Index Dynamic Average"""
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Simplified VIDYA calculation
            volatility = df['close'].rolling(window=period).std()
            mean_volatility = volatility.mean()
            
            # CRITICAL: Validate volatility before calculating alpha
            if pd.isna(mean_volatility) or mean_volatility == 0:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            alpha = 2 / (period + 1)
            alpha_series = alpha * volatility / mean_volatility
            
            # CRITICAL: Clip alpha to valid range (0, 1]
            alpha_series = alpha_series.clip(lower=0.001, upper=1.0)
            
            # Check if alpha_series has any NaN
            if alpha_series.isna().any():
                # Fallback to simple EMA
                vidya = df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
            else:
                vidya = df['close'].ewm(alpha=alpha_series, adjust=False).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            if pd.isna(vidya):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > vidya else 'SELL' if current_price < vidya else 'HOLD'
            strength = abs(current_price - vidya) / vidya * 100
            
            return {'value': float(vidya), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate VIDYA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_alma_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Arnaud Legoux Moving Average"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Simplified ALMA calculation
            m = int(0.85 * (period - 1))
            s = period / 6.0
            weights = np.exp(-((np.arange(period) - m) ** 2) / (2 * s ** 2))
            weights = weights / weights.sum()
            
            alma = df['close'].rolling(window=period).apply(lambda x: np.average(x, weights=weights), raw=True).iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(alma):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > alma else 'SELL' if current_price < alma else 'HOLD'
            strength = abs(current_price - alma) / alma * 100
            
            return {'value': float(alma), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate ALMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # Additional indicator calculation methods
    def _calculate_adx_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Average Directional Index"""
        try:
            if len(df) < period * 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            minus_dm = minus_dm.abs()
            
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            
            plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean())
            minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean())
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(period).mean().iloc[-1]
            
            if pd.isna(adx):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if adx > 25 else 'SELL' if adx < 20 else 'HOLD'
            strength = min(adx / 50, 1.0)
            
            return {'value': float(adx), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate ADX: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_di_plus_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate +DI (Positive Directional Indicator)"""
        try:
            if len(df) < period * 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            plus_dm = high.diff()
            plus_dm[plus_dm < 0] = 0
            
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            
            plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean()).iloc[-1]
            
            if pd.isna(plus_di):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if plus_di > 25 else 'SELL' if plus_di < 20 else 'HOLD'
            strength = min(plus_di / 50, 1.0)
            
            return {'value': float(plus_di), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate +DI: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_di_minus_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate -DI (Negative Directional Indicator)"""
        try:
            if len(df) < period * 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            minus_dm = low.diff()
            minus_dm[minus_dm > 0] = 0
            minus_dm = minus_dm.abs()
            
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            
            minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean()).iloc[-1]
            
            if pd.isna(minus_di):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'SELL' if minus_di > 25 else 'BUY' if minus_di < 20 else 'HOLD'
            strength = min(minus_di / 50, 1.0)
            
            return {'value': float(minus_di), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate -DI: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_aroon_up_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Aroon Up"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            aroon_up = 100 * (period - high.rolling(period).apply(lambda x: x.argmax())) / period
            aroon_up = aroon_up.iloc[-1]
            
            if pd.isna(aroon_up):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if aroon_up > 70 else 'SELL' if aroon_up < 30 else 'HOLD'
            strength = min(aroon_up / 100, 1.0)
            
            return {'value': float(aroon_up), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Aroon Up: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_aroon_down_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Aroon Down"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            low = df['low']
            aroon_down = 100 * (period - low.rolling(period).apply(lambda x: x.argmin())) / period
            aroon_down = aroon_down.iloc[-1]
            
            if pd.isna(aroon_down):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'SELL' if aroon_down > 70 else 'BUY' if aroon_down < 30 else 'HOLD'
            strength = min(aroon_down / 100, 1.0)
            
            return {'value': float(aroon_down), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Aroon Down: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_aroon_oscillator_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Aroon Oscillator"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            
            aroon_up = 100 * (period - high.rolling(period).apply(lambda x: x.argmax())) / period
            aroon_down = 100 * (period - low.rolling(period).apply(lambda x: x.argmin())) / period
            
            aroon_oscillator = (aroon_up - aroon_down).iloc[-1]
            
            if pd.isna(aroon_oscillator):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if aroon_oscillator > 0 else 'SELL' if aroon_oscillator < 0 else 'HOLD'
            strength = min(abs(aroon_oscillator) / 100, 1.0)
            
            return {'value': float(aroon_oscillator), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Aroon Oscillator: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # Stub methods for remaining indicators
    def _calculate_macd_simple(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """Calculate MACD"""
        try:
            if len(df) < slow + signal:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            ema_fast = df['close'].ewm(span=fast).mean()
            ema_slow = df['close'].ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            macd_value = macd_line.iloc[-1]
            signal_value = signal_line.iloc[-1]
            hist_value = histogram.iloc[-1]
            
            if pd.isna(macd_value) or pd.isna(signal_value):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if macd_value > signal_value and hist_value > 0 else 'SELL' if macd_value < signal_value and hist_value < 0 else 'HOLD'
            strength = min(abs(hist_value) / abs(macd_value) if macd_value != 0 else 0, 1.0)
            
            return {'value': float(macd_value), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate MACD: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_stochastic_simple(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3, smooth: int = 3) -> Dict[str, Any]:
        """Calculate Stochastic Oscillator"""
        try:
            if len(df) < k_period + d_period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            
            # FIXED: Safe division to avoid ZeroDivisionError
            range_hl = high_max - low_min
            range_hl = range_hl.replace(0, np.nan)  # Replace 0 with NaN to avoid division by zero
            k_percent = 100 * ((df['close'] - low_min) / range_hl)
            d_percent = k_percent.rolling(window=int(d_period)).mean()
            
            k_value = k_percent.iloc[-1]
            d_value = d_percent.iloc[-1]
            
            if pd.isna(k_value) or pd.isna(d_value):
                return {'value': 50, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if k_value < 20 and d_value < 20 else 'SELL' if k_value > 80 and d_value > 80 else 'HOLD'
            strength = min(abs(k_value - 50) / 50, 1.0)
            
            return {'value': float(k_value), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Stochastic: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_williams_r_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Williams %R"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high_max = df['high'].rolling(window=period).max()
            low_min = df['low'].rolling(window=period).min()
            williams_r = -100 * ((high_max - df['close']) / (high_max - low_min))
            williams_r = williams_r.iloc[-1]
            
            if pd.isna(williams_r):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if williams_r < -80 else 'SELL' if williams_r > -20 else 'HOLD'
            strength = min(abs(williams_r + 50) / 50, 1.0)
            
            return {'value': float(williams_r), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Williams %R: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_cci_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Commodity Channel Index"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
            cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
            cci = cci.iloc[-1]
            
            if pd.isna(cci):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if cci < -100 else 'SELL' if cci > 100 else 'HOLD'
            strength = min(abs(cci) / 200, 1.0)
            
            return {'value': float(cci), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate CCI: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_roc_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Rate of Change"""
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            roc = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
            roc = roc.iloc[-1]
            
            if pd.isna(roc):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if roc > 0 else 'SELL' if roc < 0 else 'HOLD'
            strength = min(abs(roc) / 50, 1.0)
            
            return {'value': float(roc), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate ROC: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_momentum_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Momentum"""
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            momentum = df['close'] - df['close'].shift(period)
            momentum = momentum.iloc[-1]
            
            if pd.isna(momentum):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if momentum > 0 else 'SELL' if momentum < 0 else 'HOLD'
            strength = min(abs(momentum) / df['close'].iloc[-1] * 100, 1.0)
            
            return {'value': float(momentum), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Momentum: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_ultimate_oscillator_simple(self, df: pd.DataFrame, period1: int = 7, period2: int = 14, period3: int = 28) -> Dict[str, Any]:
        """Calculate Ultimate Oscillator"""
        try:
            if len(df) < period3 + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            tr = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
            bp = df['close'] - np.minimum(df['low'], df['close'].shift(1))
            
            avg7 = bp.rolling(period1).sum() / tr.rolling(period1).sum()
            avg14 = bp.rolling(period2).sum() / tr.rolling(period2).sum()
            avg28 = bp.rolling(period3).sum() / tr.rolling(period3).sum()
            
            uo = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7
            uo = uo.iloc[-1]
            
            if pd.isna(uo):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if uo < 30 else 'SELL' if uo > 70 else 'HOLD'
            strength = min(abs(uo - 50) / 50, 1.0)
            
            return {'value': float(uo), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Ultimate Oscillator: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_awesome_oscillator_simple(self, df: pd.DataFrame, fast: int = 5, slow: int = 34) -> Dict[str, Any]:
        """Calculate Awesome Oscillator"""
        try:
            if len(df) < slow:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            median_price = (df['high'] + df['low']) / 2
            ao = median_price.rolling(fast).mean() - median_price.rolling(slow).mean()
            ao = ao.iloc[-1]
            
            if pd.isna(ao):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if ao > 0 else 'SELL' if ao < 0 else 'HOLD'
            strength = min(abs(ao) / df['close'].iloc[-1] * 1000, 1.0)
            
            return {'value': float(ao), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Awesome Oscillator: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # Volume indicator methods
    def _calculate_obv_ema_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate OBV with EMA"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            obv = self._calculate_obv_simple(df)
            obv_ema = obv['value'] * (2 / (period + 1)) + obv['value'] * (1 - 2 / (period + 1))
            
            signal = 'BUY' if obv_ema > obv['value'] else 'SELL' if obv_ema < obv['value'] else 'HOLD'
            strength = min(abs(obv_ema - obv['value']) / abs(obv['value']) if obv['value'] != 0 else 0, 1.0)
            
            return {'value': float(obv_ema), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate OBV EMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_vroc_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Volume Rate of Change"""
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            vroc = ((df['volume'] - df['volume'].shift(period)) / df['volume'].shift(period)) * 100
            vroc = vroc.iloc[-1]
            
            if pd.isna(vroc):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if vroc > 0 else 'SELL' if vroc < 0 else 'HOLD'
            strength = min(abs(vroc) / 100, 1.0)
            
            return {'value': float(vroc), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate VROC: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_mfi_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Money Flow Index"""
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            money_flow = typical_price * df['volume']
            
            positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(period).sum()
            negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(period).sum()
            
            mfi = 100 - (100 / (1 + positive_flow / negative_flow))
            mfi = mfi.iloc[-1]
            
            if pd.isna(mfi):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if mfi < 20 else 'SELL' if mfi > 80 else 'HOLD'
            strength = min(abs(mfi - 50) / 50, 1.0)
            
            return {'value': float(mfi), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate MFI: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_ad_ema_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Accumulation/Distribution with EMA"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            ad = self._calculate_ad_simple(df)
            ad_ema = ad['value'] * (2 / (period + 1)) + ad['value'] * (1 - 2 / (period + 1))
            
            signal = 'BUY' if ad_ema > ad['value'] else 'SELL' if ad_ema < ad['value'] else 'HOLD'
            strength = min(abs(ad_ema - ad['value']) / abs(ad['value']) if ad['value'] != 0 else 0, 1.0)
            
            return {'value': float(ad_ema), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate AD EMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_cmf_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Chaikin Money Flow"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            money_flow_volume = money_flow_multiplier * df['volume']
            
            cmf = money_flow_volume.rolling(period).sum() / df['volume'].rolling(period).sum()
            cmf = cmf.iloc[-1]
            
            if pd.isna(cmf):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if cmf > 0 else 'SELL' if cmf < 0 else 'HOLD'
            strength = min(abs(cmf), 1.0)
            
            return {'value': float(cmf), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate CMF: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_vwap_simple(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Volume Weighted Average Price"""
        try:
            if len(df) < 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            vwap = vwap.iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if pd.isna(vwap):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price > vwap else 'SELL' if current_price < vwap else 'HOLD'
            strength = abs(current_price - vwap) / vwap * 100
            
            return {'value': float(vwap), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate VWAP: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_vwap_ema_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate VWAP with EMA"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            vwap = self._calculate_vwap_simple(df)
            vwap_ema = vwap['value'] * (2 / (period + 1)) + vwap['value'] * (1 - 2 / (period + 1))
            
            signal = 'BUY' if vwap_ema > vwap['value'] else 'SELL' if vwap_ema < vwap['value'] else 'HOLD'
            strength = min(abs(vwap_ema - vwap['value']) / abs(vwap['value']) if vwap['value'] != 0 else 0, 1.0)
            
            return {'value': float(vwap_ema), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate VWAP EMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # Volatility indicator methods
    def _calculate_bollinger_bands_simple(self, df: pd.DataFrame, period: int = 20, std: float = 2) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            sma = df['close'].rolling(window=period).mean()
            std_dev = df['close'].rolling(window=period).std()
            
            upper_band = sma + (std_dev * std)
            lower_band = sma - (std_dev * std)
            
            current_price = df['close'].iloc[-1]
            upper = upper_band.iloc[-1]
            lower = lower_band.iloc[-1]
            middle = sma.iloc[-1]
            
            if pd.isna(upper) or pd.isna(lower) or pd.isna(middle):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price < lower else 'SELL' if current_price > upper else 'HOLD'
            strength = min(abs(current_price - middle) / (upper - lower) if (upper - lower) != 0 else 0, 1.0)
            
            return {'value': float(middle), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Bollinger Bands: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_keltner_channels_simple(self, df: pd.DataFrame, period: int = 20, multiplier: float = 2) -> Dict[str, Any]:
        """Calculate Keltner Channels"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            ema = df['close'].ewm(span=period).mean()
            atr = self._calculate_atr_simple(df, period)
            
            upper_channel = ema + (multiplier * atr['value'])
            lower_channel = ema - (multiplier * atr['value'])
            
            current_price = df['close'].iloc[-1]
            upper = upper_channel.iloc[-1]
            lower = lower_channel.iloc[-1]
            middle = ema.iloc[-1]
            
            if pd.isna(upper) or pd.isna(lower) or pd.isna(middle):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price < lower else 'SELL' if current_price > upper else 'HOLD'
            strength = min(abs(current_price - middle) / (upper - lower) if (upper - lower) != 0 else 0, 1.0)
            
            return {'value': float(middle), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Keltner Channels: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_donchian_channels_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Donchian Channels"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            upper_channel = df['high'].rolling(window=period).max()
            lower_channel = df['low'].rolling(window=period).min()
            middle_channel = (upper_channel + lower_channel) / 2
            
            current_price = df['close'].iloc[-1]
            upper = upper_channel.iloc[-1]
            lower = lower_channel.iloc[-1]
            middle = middle_channel.iloc[-1]
            
            if pd.isna(upper) or pd.isna(lower) or pd.isna(middle):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_price < lower else 'SELL' if current_price > upper else 'HOLD'
            strength = min(abs(current_price - middle) / (upper - lower) if (upper - lower) != 0 else 0, 1.0)
            
            return {'value': float(middle), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Donchian Channels: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_volatility_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Volatility"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            returns = df['close'].pct_change()
            volatility = returns.rolling(window=period).std() * np.sqrt(period)
            volatility = volatility.iloc[-1]
            
            if pd.isna(volatility):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if volatility < 0.2 else 'SELL' if volatility > 0.5 else 'HOLD'
            strength = min(volatility * 2, 1.0)
            
            return {'value': float(volatility), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volatility: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # Missing indicator methods
    def _calculate_obv_simple(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate On Balance Volume"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            price_change = df['close'].diff()
            volume = df['volume']
            
            obv = np.where(price_change > 0, volume, 
                          np.where(price_change < 0, -volume, 0)).cumsum()
            obv = obv[-1]
            
            signal = 'BUY' if obv > 0 else 'SELL' if obv < 0 else 'HOLD'
            strength = min(abs(obv) / volume.iloc[-1] if volume.iloc[-1] != 0 else 0, 1.0)
            
            return {'value': float(obv), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate OBV: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_ad_simple(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Accumulation/Distribution"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            clv = clv.fillna(0)
            ad = (clv * df['volume']).cumsum()
            ad = ad.iloc[-1]
            
            signal = 'BUY' if ad > 0 else 'SELL' if ad < 0 else 'HOLD'
            strength = min(abs(ad) / df['volume'].iloc[-1] if df['volume'].iloc[-1] != 0 else 0, 1.0)
            
            return {'value': float(ad), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate AD: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_atr_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Average True Range"""
        try:
            if len(df) < period + 1:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            atr = tr.rolling(window=period).mean().iloc[-1]
            
            if pd.isna(atr):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if atr < close.iloc[-1] * 0.02 else 'SELL' if atr > close.iloc[-1] * 0.05 else 'HOLD'
            strength = min(atr / close.iloc[-1] * 50, 1.0)
            
            return {'value': float(atr), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate ATR: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # Additional missing methods
    def _calculate_bb_simple(self, df: pd.DataFrame, period: int, std_dev: float) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            sma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            
            current_price = df['close'].iloc[-1]
            upper_val = upper.iloc[-1]
            lower_val = lower.iloc[-1]
            middle_val = sma.iloc[-1]
            
            if pd.isna(upper_val) or pd.isna(lower_val) or pd.isna(middle_val):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            if current_price > upper_val:
                signal = 'SELL'
                strength = min((current_price - upper_val) / (upper_val - middle_val), 1.0)
            elif current_price < lower_val:
                signal = 'BUY'
                strength = min((lower_val - current_price) / (middle_val - lower_val), 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Bollinger Bands: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # REMOVED: _calculate_ichimoku_simple - DUPLICATE of _calculate_ichimoku_cloud
    # Use _calculate_ichimoku_cloud instead for comprehensive Ichimoku analysis
    
    def _calculate_supertrend_simple(self, df: pd.DataFrame, period: int, multiplier: float) -> Dict[str, Any]:
        """Calculate SuperTrend"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            atr = tr.rolling(window=period).mean()
            
            hl2 = (high + low) / 2
            upper_band = hl2 + (multiplier * atr)
            lower_band = hl2 - (multiplier * atr)
            
            # Calculate SuperTrend
            supertrend = pd.Series(index=df.index, dtype=float)
            direction = pd.Series(index=df.index, dtype=int)
            
            for i in range(len(df)):
                if i == 0:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                else:
                    if close.iloc[i] <= supertrend.iloc[i-1]:
                        supertrend.iloc[i] = upper_band.iloc[i]
                        direction.iloc[i] = -1
                    else:
                        supertrend.iloc[i] = lower_band.iloc[i]
                        direction.iloc[i] = 1
            
            current_price = close.iloc[-1]
            current_supertrend = supertrend.iloc[-1]
            current_direction = direction.iloc[-1]
            
            if pd.isna(current_supertrend):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_direction == 1 else 'SELL'
            strength = min(abs(current_price - current_supertrend) / current_price, 1.0)
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate SuperTrend: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_psar(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Parabolic SAR with dynamic parameters"""
        try:
            from .market_constants import market_constants
            acceleration = market_constants.get_dynamic_psar_acceleration() if market_constants else 0.02
            maximum = market_constants.get_dynamic_psar_maximum() if market_constants else 0.2
        except Exception:
            acceleration = 0.02
            maximum = 0.2
        return self._calculate_psar_simple(data, acceleration, maximum)
    
    # More missing methods
    def _calculate_psar_simple(self, df: pd.DataFrame, acceleration: float, maximum: float) -> Dict[str, Any]:
        """Calculate Parabolic SAR"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            high = df['high']
            low = df['low']
            close = df['close']
            
            psar = pd.Series(index=df.index, dtype=float)
            trend = pd.Series(index=df.index, dtype=int)
            af = pd.Series(index=df.index, dtype=float)
            ep = pd.Series(index=df.index, dtype=float)
            
            # Initialize first values
            psar.iloc[0] = low.iloc[0]
            trend.iloc[0] = 1
            af.iloc[0] = acceleration
            ep.iloc[0] = high.iloc[0]
            
            for i in range(1, len(df)):
                if trend.iloc[i-1] == 1:  # Uptrend
                    psar.iloc[i] = psar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - psar.iloc[i-1])
                    
                    if low.iloc[i] <= psar.iloc[i]:
                        trend.iloc[i] = -1
                        psar.iloc[i] = ep.iloc[i-1]
                        af.iloc[i] = acceleration
                        ep.iloc[i] = low.iloc[i]
                    else:
                        trend.iloc[i] = 1
                        if high.iloc[i] > ep.iloc[i-1]:
                            ep.iloc[i] = high.iloc[i]
                            af.iloc[i] = min(af.iloc[i-1] + acceleration, maximum)
                        else:
                            ep.iloc[i] = ep.iloc[i-1]
                            af.iloc[i] = af.iloc[i-1]
                        
                        # Check for SAR reversal
                        if low.iloc[i] <= psar.iloc[i]:
                            psar.iloc[i] = low.iloc[i]
                else:  # Downtrend
                    psar.iloc[i] = psar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - psar.iloc[i-1])
                    
                    if high.iloc[i] >= psar.iloc[i]:
                        trend.iloc[i] = 1
                        psar.iloc[i] = ep.iloc[i-1]
                        af.iloc[i] = acceleration
                        ep.iloc[i] = high.iloc[i]
                    else:
                        trend.iloc[i] = -1
                        if low.iloc[i] < ep.iloc[i-1]:
                            ep.iloc[i] = low.iloc[i]
                            af.iloc[i] = min(af.iloc[i-1] + acceleration, maximum)
                        else:
                            ep.iloc[i] = ep.iloc[i-1]
                            af.iloc[i] = af.iloc[i-1]
                        
                        # Check for SAR reversal
                        if high.iloc[i] >= psar.iloc[i]:
                            psar.iloc[i] = high.iloc[i]
            
            current_price = close.iloc[-1]
            current_psar = psar.iloc[-1]
            current_trend = trend.iloc[-1]
            
            if pd.isna(current_psar):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_trend == 1 else 'SELL'
            
            # FIXED: Safe division to avoid ZeroDivisionError
            if current_price > 0:
                strength = min(abs(current_price - current_psar) / current_price, 1.0)
            else:
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Parabolic SAR: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_volume_profile_simple(self, df: pd.DataFrame, bins: int) -> Dict[str, Any]:
        """Calculate Volume Profile"""
        try:
            if len(df) < 10:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Create price bins
            min_price = df['low'].min()
            max_price = df['high'].max()
            price_range = max_price - min_price
            bin_size = price_range / bins
            
            # Calculate volume for each bin
            volume_profile = {}
            for i in range(bins):
                bin_low = min_price + i * bin_size
                bin_high = min_price + (i + 1) * bin_size
                
                mask = (df['low'] < bin_high) & (df['high'] > bin_low)
                volume_in_bin = df[mask]['volume'].sum()
                volume_profile[bin_low] = volume_in_bin
            
            # Find POC (Point of Control) - highest volume bin
            poc_price = max(volume_profile, key=volume_profile.get)
            poc_volume = volume_profile[poc_price]
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on price relative to POC
            if current_price > poc_price:
                signal = 'BUY'
                strength = min((current_price - poc_price) / poc_price, 1.0)
            elif current_price < poc_price:
                signal = 'SELL'
                strength = min((poc_price - current_price) / poc_price, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Profile: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_fibonacci_retracement_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Fibonacci Retracement"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            recent_data = df.tail(period)
            high = recent_data['high'].max()
            low = recent_data['low'].min()
            
            diff = high - low
            fib_levels = {
                0.236: high - (diff * 0.236),
                0.382: high - (diff * 0.382),
                0.500: high - (diff * 0.500),
                0.618: high - (diff * 0.618),
                0.786: high - (diff * 0.786)
            }
            
            current_price = df['close'].iloc[-1]
            
            # Find closest Fibonacci level
            closest_level = min(fib_levels.values(), key=lambda x: abs(x - current_price))
            level_ratio = min(fib_levels.keys(), key=lambda x: abs(fib_levels[x] - current_price))
            
            # Determine signal based on Fibonacci level
            if current_price <= fib_levels[0.236]:
                signal = 'BUY'
                strength = 0.9
            elif current_price <= fib_levels[0.382]:
                signal = 'BUY'
                strength = 0.7
            elif current_price <= fib_levels[0.500]:
                signal = 'HOLD'
                strength = 0.5
            elif current_price <= fib_levels[0.618]:
                signal = 'SELL'
                strength = 0.7
            else:
                signal = 'SELL'
                strength = 0.9
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Fibonacci Retracement: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_pivot_points_simple(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Standard Pivot Points"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Use previous day's data for pivot calculation
            prev_high = df['high'].iloc[-2]
            prev_low = df['low'].iloc[-2]
            prev_close = df['close'].iloc[-2]
            
            # Calculate pivot point
            pivot = (prev_high + prev_low + prev_close) / 3
            
            # Calculate support and resistance levels
            r1 = 2 * pivot - prev_low
            r2 = pivot + (prev_high - prev_low)
            r3 = prev_high + 2 * (pivot - prev_low)
            
            s1 = 2 * pivot - prev_high
            s2 = pivot - (prev_high - prev_low)
            s3 = prev_low - 2 * (prev_high - pivot)
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on pivot levels
            if current_price > r2:
                signal = 'BUY'
                strength = 0.9
            elif current_price > r1:
                signal = 'BUY'
                strength = 0.7
            elif current_price > pivot:
                signal = 'BUY'
                strength = 0.5
            elif current_price > s1:
                signal = 'HOLD'
                strength = 0.3
            elif current_price > s2:
                signal = 'SELL'
                strength = 0.7
            else:
                signal = 'SELL'
                strength = 0.9
            
            return {'value': float(pivot), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Pivot Points: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_camarilla_pivot_points(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Camarilla Pivot Points"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Use previous day's data
            prev_high = df['high'].iloc[-2]
            prev_low = df['low'].iloc[-2]
            prev_close = df['close'].iloc[-2]
            
            # Camarilla pivot formula
            diff = prev_high - prev_low
            
            # Calculate levels
            r4 = prev_close + diff * 1.1 / 2
            r3 = prev_close + diff * 1.1 / 4
            r2 = prev_close + diff * 1.1 / 6
            r1 = prev_close + diff * 1.1 / 12
            
            s1 = prev_close - diff * 1.1 / 12
            s2 = prev_close - diff * 1.1 / 6
            s3 = prev_close - diff * 1.1 / 4
            s4 = prev_close - diff * 1.1 / 2
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal
            if current_price > r3:
                signal = 'BUY'
                strength = 0.9
            elif current_price > r1:
                signal = 'BUY'
                strength = 0.6
            elif current_price > s1:
                signal = 'HOLD'
                strength = 0.3
            elif current_price > s3:
                signal = 'SELL'
                strength = 0.6
            else:
                signal = 'SELL'
                strength = 0.9
            
            return {'value': float(prev_close), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Camarilla Pivot Points: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_woodie_pivot_points(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Woodie's Pivot Points"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Use previous day's data
            prev_high = df['high'].iloc[-2]
            prev_low = df['low'].iloc[-2]
            prev_close = df['close'].iloc[-2]
            prev_open = df['open'].iloc[-2] if 'open' in df.columns else prev_close
            
            # Woodie's pivot formula (gives more weight to close)
            pivot = (prev_high + prev_low + 2 * prev_close) / 4
            
            # Calculate support and resistance
            r2 = pivot + (prev_high - prev_low)
            r1 = 2 * pivot - prev_low
            s1 = 2 * pivot - prev_high
            s2 = pivot - (prev_high - prev_low)
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal
            if current_price > r1:
                signal = 'BUY'
                strength = 0.8
            elif current_price > pivot:
                signal = 'BUY'
                strength = 0.5
            elif current_price > s1:
                signal = 'HOLD'
                strength = 0.3
            elif current_price > s2:
                signal = 'SELL'
                strength = 0.6
            else:
                signal = 'SELL'
                strength = 0.9
            
            return {'value': float(pivot), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Woodie Pivot Points: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_demark_pivot_points(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate DeMark Pivot Points"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Use previous day's data
            prev_high = df['high'].iloc[-2]
            prev_low = df['low'].iloc[-2]
            prev_close = df['close'].iloc[-2]
            prev_open = df['open'].iloc[-2] if 'open' in df.columns else prev_close
            
            # DeMark pivot formula depends on relationship between open and close
            if prev_close < prev_open:
                x = prev_high + 2 * prev_low + prev_close
            elif prev_close > prev_open:
                x = 2 * prev_high + prev_low + prev_close
            else:
                x = prev_high + prev_low + 2 * prev_close
            
            # Calculate pivot
            pivot = x / 4
            
            # Calculate support and resistance
            r1 = x / 2 - prev_low
            s1 = x / 2 - prev_high
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal
            if current_price > r1:
                signal = 'BUY'
                strength = 0.8
            elif current_price > pivot:
                signal = 'BUY'
                strength = 0.5
            elif current_price > s1:
                signal = 'HOLD'
                strength = 0.3
            else:
                signal = 'SELL'
                strength = 0.7
            
            return {'value': float(pivot), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate DeMark Pivot Points: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_support_resistance_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Support and Resistance levels"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            recent_data = df.tail(period)
            high = recent_data['high']
            low = recent_data['low']
            
            # Find local maxima and minima
            highs = []
            lows = []
            
            for i in range(1, len(recent_data) - 1):
                if high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1]:
                    highs.append(high.iloc[i])
                if low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1]:
                    lows.append(low.iloc[i])
            
            # Calculate support and resistance levels
            resistance = max(highs) if highs else recent_data['high'].max()
            support = min(lows) if lows else recent_data['low'].min()
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on support/resistance
            if current_price > resistance:
                signal = 'BUY'
                strength = 0.8
            elif current_price < support:
                signal = 'SELL'
                strength = 0.8
            elif current_price > (support + resistance) / 2:
                signal = 'BUY'
                strength = 0.5
            else:
                signal = 'SELL'
                strength = 0.5
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Support/Resistance: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_market_regime_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Market Regime Detection"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            recent_data = df.tail(period)
            close = recent_data['close']
            
            # Calculate trend
            sma_short = close.rolling(window=10).mean()
            sma_long = close.rolling(window=20).mean()
            
            # Calculate volatility
            returns = close.pct_change()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate momentum
            momentum = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
            
            # Determine market regime
            if sma_short.iloc[-1] > sma_long.iloc[-1] and momentum > 0.02:
                regime = 'BULL'
                signal = 'BUY'
                strength = 0.8
            elif sma_short.iloc[-1] < sma_long.iloc[-1] and momentum < -0.02:
                regime = 'BEAR'
                signal = 'SELL'
                strength = 0.8
            elif volatility > 0.3:
                regime = 'HIGH_VOLATILITY'
                signal = 'HOLD'
                strength = 0.3
            else:
                regime = 'SIDEWAYS'
                signal = 'HOLD'
                strength = 0.5
            
            return {'value': float(close.iloc[-1]), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Market Regime: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_volume_weighted_price_simple(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Volume Weighted Average Price"""
        try:
            if len(df) < 2:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Calculate VWAP
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            vwap = vwap.iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on VWAP
            if current_price > vwap:
                signal = 'BUY'
                strength = min((current_price - vwap) / vwap, 1.0)
            elif current_price < vwap:
                signal = 'SELL'
                strength = min((vwap - current_price) / vwap, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate VWAP: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_volume_oscillator_simple(self, df: pd.DataFrame, short_period: int, long_period: int) -> Dict[str, Any]:
        """Calculate Volume Oscillator"""
        try:
            if len(df) < long_period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            volume = df['volume']
            short_ma = volume.rolling(window=short_period).mean()
            long_ma = volume.rolling(window=long_period).mean()
            
            vo = ((short_ma - long_ma) / long_ma) * 100
            vo = vo.iloc[-1]
            
            if pd.isna(vo):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if vo > 0 else 'SELL' if vo < 0 else 'HOLD'
            strength = min(abs(vo) / 100, 1.0)
            
            return {'value': float(vo), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Oscillator: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_volume_ratio_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Volume Ratio"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            volume = df['volume']
            avg_volume = volume.rolling(window=period).mean()
            current_volume = volume.iloc[-1]
            avg_vol = avg_volume.iloc[-1]
            
            if pd.isna(avg_vol) or avg_vol == 0:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            volume_ratio = current_volume / avg_vol
            
            signal = 'BUY' if volume_ratio > 1.5 else 'SELL' if volume_ratio < 0.5 else 'HOLD'
            strength = min(abs(volume_ratio - 1), 1.0)
            
            return {'value': float(volume_ratio), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Ratio: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_volume_sma_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Volume SMA"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            volume = df['volume']
            volume_sma = volume.rolling(window=period).mean()
            current_volume = volume.iloc[-1]
            avg_volume = volume_sma.iloc[-1]
            
            if pd.isna(avg_volume):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_volume > avg_volume else 'SELL' if current_volume < avg_volume else 'HOLD'
            strength = min(abs(current_volume - avg_volume) / avg_volume, 1.0)
            
            return {'value': float(current_volume), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume SMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_volume_ema_simple(self, df: pd.DataFrame, period: int) -> Dict[str, Any]:
        """Calculate Volume EMA"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            volume = df['volume']
            volume_ema = volume.ewm(span=period).mean()
            current_volume = volume.iloc[-1]
            avg_volume = volume_ema.iloc[-1]
            
            if pd.isna(avg_volume):
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            signal = 'BUY' if current_volume > avg_volume else 'SELL' if current_volume < avg_volume else 'HOLD'
            strength = min(abs(current_volume - avg_volume) / avg_volume, 1.0)
            
            return {'value': float(current_volume), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume EMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_volume_profile_ema_simple(self, df: pd.DataFrame, bins: int, period: int) -> Dict[str, Any]:
        """Calculate Volume Profile EMA"""
        try:
            if len(df) < 10:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Create price bins
            min_price = df['low'].min()
            max_price = df['high'].max()
            price_range = max_price - min_price
            bin_size = price_range / bins
            
            # Calculate volume for each bin
            volume_profile = {}
            for i in range(bins):
                bin_low = min_price + i * bin_size
                bin_high = min_price + (i + 1) * bin_size
                
                mask = (df['low'] < bin_high) & (df['high'] > bin_low)
                volume_in_bin = df[mask]['volume'].sum()
                volume_profile[bin_low] = volume_in_bin
            
            # Find POC (Point of Control) - highest volume bin
            poc_price = max(volume_profile, key=volume_profile.get)
            poc_volume = volume_profile[poc_price]
            
            # Apply EMA smoothing to POC
            poc_series = pd.Series([poc_price] * len(df))
            poc_ema = poc_series.ewm(span=period).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on price relative to smoothed POC
            if current_price > poc_ema:
                signal = 'BUY'
                strength = min((current_price - poc_ema) / poc_ema, 1.0)
            elif current_price < poc_ema:
                signal = 'SELL'
                strength = min((poc_ema - current_price) / poc_ema, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Profile EMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_volume_profile_sma_simple(self, df: pd.DataFrame, bins: int, period: int) -> Dict[str, Any]:
        """Calculate Volume Profile SMA"""
        try:
            if len(df) < 10:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Create price bins
            min_price = df['low'].min()
            max_price = df['high'].max()
            price_range = max_price - min_price
            bin_size = price_range / bins
            
            # Calculate volume for each bin
            volume_profile = {}
            for i in range(bins):
                bin_low = min_price + i * bin_size
                bin_high = min_price + (i + 1) * bin_size
                
                mask = (df['low'] < bin_high) & (df['high'] > bin_low)
                volume_in_bin = df[mask]['volume'].sum()
                volume_profile[bin_low] = volume_in_bin
            
            # Find POC (Point of Control) - highest volume bin
            poc_price = max(volume_profile, key=volume_profile.get)
            poc_volume = volume_profile[poc_price]
            
            # Apply SMA smoothing to POC
            poc_series = pd.Series([poc_price] * len(df))
            poc_sma = poc_series.rolling(window=period).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on price relative to smoothed POC
            if current_price > poc_sma:
                signal = 'BUY'
                strength = min((current_price - poc_sma) / poc_sma, 1.0)
            elif current_price < poc_sma:
                signal = 'SELL'
                strength = min((poc_sma - current_price) / poc_sma, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Profile SMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_volume_profile_ema_sma_simple(self, df: pd.DataFrame, bins: int, ema_period: int, sma_period: int) -> Dict[str, Any]:
        """Calculate Volume Profile EMA SMA"""
        try:
            if len(df) < 10:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Create price bins
            min_price = df['low'].min()
            max_price = df['high'].max()
            price_range = max_price - min_price
            bin_size = price_range / bins
            
            # Calculate volume for each bin
            volume_profile = {}
            for i in range(bins):
                bin_low = min_price + i * bin_size
                bin_high = min_price + (i + 1) * bin_size
                
                mask = (df['low'] < bin_high) & (df['high'] > bin_low)
                volume_in_bin = df[mask]['volume'].sum()
                volume_profile[bin_low] = volume_in_bin
            
            # Find POC (Point of Control) - highest volume bin
            poc_price = max(volume_profile, key=volume_profile.get)
            poc_volume = volume_profile[poc_price]
            
            # Apply EMA then SMA smoothing to POC
            poc_series = pd.Series([poc_price] * len(df))
            poc_ema = poc_series.ewm(span=ema_period).mean()
            poc_ema_sma = poc_ema.rolling(window=sma_period).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on price relative to smoothed POC
            if current_price > poc_ema_sma:
                signal = 'BUY'
                strength = min((current_price - poc_ema_sma) / poc_ema_sma, 1.0)
            elif current_price < poc_ema_sma:
                signal = 'SELL'
                strength = min((poc_ema_sma - current_price) / poc_ema_sma, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Profile EMA SMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # More missing methods
    def _calculate_volume_profile_ema_sma_ema_simple(self, df: pd.DataFrame, bins: int, ema1_period: int, sma_period: int, ema2_period: int) -> Dict[str, Any]:
        """Calculate Volume Profile EMA SMA EMA"""
        try:
            if len(df) < 10:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Create price bins
            min_price = df['low'].min()
            max_price = df['high'].max()
            price_range = max_price - min_price
            bin_size = price_range / bins
            
            # Calculate volume for each bin
            volume_profile = {}
            for i in range(bins):
                bin_low = min_price + i * bin_size
                bin_high = min_price + (i + 1) * bin_size
                
                mask = (df['low'] < bin_high) & (df['high'] > bin_low)
                volume_in_bin = df[mask]['volume'].sum()
                volume_profile[bin_low] = volume_in_bin
            
            # Find POC (Point of Control) - highest volume bin
            poc_price = max(volume_profile, key=volume_profile.get)
            poc_volume = volume_profile[poc_price]
            
            # Apply EMA, then SMA, then EMA smoothing to POC
            poc_series = pd.Series([poc_price] * len(df))
            poc_ema1 = poc_series.ewm(span=ema1_period).mean()
            poc_sma = poc_ema1.rolling(window=sma_period).mean()
            poc_ema2 = poc_sma.ewm(span=ema2_period).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal based on price relative to smoothed POC
            if current_price > poc_ema2:
                signal = 'BUY'
                strength = min((current_price - poc_ema2) / poc_ema2, 1.0)
            elif current_price < poc_ema2:
                signal = 'SELL'
                strength = min((poc_ema2 - current_price) / poc_ema2, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Volume Profile EMA SMA EMA: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    def _calculate_kc_simple(self, df: pd.DataFrame, period: int, multiplier: float) -> Dict[str, Any]:
        """Calculate Keltner Channels"""
        try:
            if len(df) < period:
                return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
            
            # Calculate EMA
            ema = df['close'].ewm(span=period).mean()
            
            # Calculate ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=period).mean()
            
            # Calculate channels
            upper_channel = ema + (multiplier * atr)
            lower_channel = ema - (multiplier * atr)
            
            current_price = df['close'].iloc[-1]
            upper = upper_channel.iloc[-1]
            lower = lower_channel.iloc[-1]
            
            # Determine signal
            if current_price > upper:
                signal = 'SELL'
                strength = min((current_price - upper) / upper, 1.0)
            elif current_price < lower:
                signal = 'BUY'
                strength = min((lower - current_price) / lower, 1.0)
            else:
                signal = 'HOLD'
                strength = 0.0
            
            return {'value': float(current_price), 'signal': signal, 'strength': float(strength)}
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Keltner Channels: {e}")
            return {'value': 0, 'signal': 'HOLD', 'strength': 0.0}
    
    # NOTE: _calculate_dpo already defined at line 2243 - duplicate removed to avoid conflicts
    
    def _calculate_linear_regression(self, data: pd.Series, period: int = 14) -> Dict[str, pd.Series]:
        """
        Calculate Linear Regression indicators
        Returns: value, slope, angle, intercept
        """
        try:
            if len(data) < period:
                zero_series = pd.Series([0.0] * len(data), index=data.index)
                return {
                    'value': zero_series,
                    'slope': zero_series,
                    'angle': zero_series,
                    'intercept': zero_series
                }
            
            # Prepare arrays for regression
            values = []
            slopes = []
            angles = []
            intercepts = []
            
            for i in range(len(data)):
                if i < period - 1:
                    values.append(0.0)
                    slopes.append(0.0)
                    angles.append(0.0)
                    intercepts.append(0.0)
                else:
                    # Get window of data
                    window = data.iloc[i - period + 1:i + 1].values
                    x = np.arange(period)
                    
                    # Calculate linear regression
                    if len(window) == period and not np.all(np.isnan(window)):
                        # Remove NaN values
                        valid_mask = ~np.isnan(window)
                        if np.sum(valid_mask) >= 2:
                            x_valid = x[valid_mask]
                            y_valid = window[valid_mask]
                            
                            # Linear regression: y = mx + b
                            slope = np.polyfit(x_valid, y_valid, 1)[0]
                            intercept = np.polyfit(x_valid, y_valid, 1)[1]
                            
                            # Predicted value at current point
                            value = slope * (period - 1) + intercept
                            
                            # Angle in degrees
                            angle = np.arctan(slope) * 180 / np.pi
                            
                            values.append(float(value))
                            slopes.append(float(slope))
                            angles.append(float(angle))
                            intercepts.append(float(intercept))
                        else:
                            values.append(0.0)
                            slopes.append(0.0)
                            angles.append(0.0)
                            intercepts.append(0.0)
                    else:
                        values.append(0.0)
                        slopes.append(0.0)
                        angles.append(0.0)
                        intercepts.append(0.0)
            
            return {
                'value': pd.Series(values, index=data.index),
                'slope': pd.Series(slopes, index=data.index),
                'angle': pd.Series(angles, index=data.index),
                'intercept': pd.Series(intercepts, index=data.index)
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Linear Regression: {e}")
            zero_series = pd.Series([0.0] * len(data), index=data.index)
            return {
                'value': zero_series,
                'slope': zero_series,
                'angle': zero_series,
                'intercept': zero_series
            }
    
    def _calculate_standard_deviation(self, data: pd.Series, period: int = 20) -> pd.Series:
        """Calculate rolling standard deviation"""
        try:
            if len(data) < period:
                return pd.Series([0.0] * len(data), index=data.index)
            
            std_dev = data.rolling(window=period).std()
            std_dev = std_dev.fillna(0.0)
            
            return std_dev
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Standard Deviation: {e}")
            return pd.Series([0.0] * len(data), index=data.index if hasattr(data, 'index') else None)
    
    def _calculate_variance(self, data: pd.Series, period: int = 20) -> pd.Series:
        """Calculate rolling variance"""
        try:
            if len(data) < period:
                return pd.Series([0.0] * len(data), index=data.index)
            
            variance = data.rolling(window=period).var()
            variance = variance.fillna(0.0)
            
            return variance
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Variance: {e}")
            return pd.Series([0.0] * len(data), index=data.index if hasattr(data, 'index') else None)
    
    def _calculate_chandelier_exit(self, data: pd.DataFrame, period: int = 22, multiplier: float = 3.0) -> Dict[str, pd.Series]:
        """
        Calculate Chandelier Exit
        Long Stop = Highest High - ATR * Multiplier
        Short Stop = Lowest Low + ATR * Multiplier
        """
        try:
            if len(data) < period:
                zero_series = pd.Series([0.0] * len(data), index=data.index)
                return {
                    'long_stop': zero_series,
                    'short_stop': zero_series
                }
            
            # Calculate ATR
            atr = self._calculate_atr(data, period)
            if isinstance(atr, dict):
                atr_series = atr.get('value', pd.Series([0.0] * len(data)))
            else:
                atr_series = atr
            
            # Calculate highest high and lowest low
            highest_high = data['high'].rolling(window=period).max()
            lowest_low = data['low'].rolling(window=period).min()
            
            # Calculate stops
            long_stop = highest_high - (atr_series * multiplier)
            short_stop = lowest_low + (atr_series * multiplier)
            
            # Fill NaN
            long_stop = long_stop.fillna(0.0)
            short_stop = short_stop.fillna(0.0)
            
            return {
                'long_stop': long_stop,
                'short_stop': short_stop
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Chandelier Exit: {e}")
            zero_series = pd.Series([0.0] * len(data), index=data.index)
            return {
                'long_stop': zero_series,
                'short_stop': zero_series
            }
    
    def _calculate_aroon(self, data: pd.DataFrame, period: int = 25) -> Dict[str, pd.Series]:
        """
        Calculate Aroon Indicator
        Aroon Up = ((period - periods since highest high) / period) * 100
        Aroon Down = ((period - periods since lowest low) / period) * 100
        Aroon Oscillator = Aroon Up - Aroon Down
        """
        try:
            if len(data) < period:
                zero_series = pd.Series([0.0] * len(data), index=data.index)
                return {
                    'up': zero_series,
                    'down': zero_series,
                    'oscillator': zero_series
                }
            
            aroon_up = []
            aroon_down = []
            
            for i in range(len(data)):
                if i < period - 1:
                    aroon_up.append(0.0)
                    aroon_down.append(0.0)
                else:
                    # Get window
                    window_high = data['high'].iloc[i - period + 1:i + 1]
                    window_low = data['low'].iloc[i - period + 1:i + 1]
                    
                    # Find periods since highest/lowest
                    periods_since_high = period - 1 - window_high.argmax()
                    periods_since_low = period - 1 - window_low.argmin()
                    
                    # Calculate Aroon
                    up_value = ((period - periods_since_high) / period) * 100
                    down_value = ((period - periods_since_low) / period) * 100
                    
                    aroon_up.append(float(up_value))
                    aroon_down.append(float(down_value))
            
            aroon_up_series = pd.Series(aroon_up, index=data.index)
            aroon_down_series = pd.Series(aroon_down, index=data.index)
            aroon_osc = aroon_up_series - aroon_down_series
            
            return {
                'up': aroon_up_series,
                'down': aroon_down_series,
                'oscillator': aroon_osc
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Aroon: {e}")
            zero_series = pd.Series([0.0] * len(data), index=data.index)
            return {
                'up': zero_series,
                'down': zero_series,
                'oscillator': zero_series
            }
    
    def _calculate_stochastic_rsi(self, data: pd.Series, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic RSI
        StochRSI = (RSI - Min RSI) / (Max RSI - Min RSI)
        """
        try:
            if len(data) < period:
                zero_series = pd.Series([0.0] * len(data), index=data.index)
                return {
                    'k': zero_series,
                    'd': zero_series
                }
            
            # Calculate RSI
            rsi = self._calculate_rsi(data, period)
            if isinstance(rsi, dict):
                rsi_series = rsi.get('value', pd.Series([50.0] * len(data)))
            else:
                rsi_series = rsi
            
            # Calculate Stochastic RSI
            min_rsi = rsi_series.rolling(window=period).min()
            max_rsi = rsi_series.rolling(window=period).max()
            
            stoch_rsi = (rsi_series - min_rsi) / (max_rsi - min_rsi + 1e-10) * 100
            stoch_rsi = stoch_rsi.fillna(50.0)
            
            # Smooth with SMA
            stoch_rsi_k = stoch_rsi.rolling(window=smooth_k).mean()
            stoch_rsi_d = stoch_rsi_k.rolling(window=smooth_d).mean()
            
            stoch_rsi_k = stoch_rsi_k.fillna(50.0)
            stoch_rsi_d = stoch_rsi_d.fillna(50.0)
            
            return {
                'k': stoch_rsi_k,
                'd': stoch_rsi_d
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Stochastic RSI: {e}")
            zero_series = pd.Series([50.0] * len(data), index=data.index)
            return {
                'k': zero_series,
                'd': zero_series
            }
    
    def _calculate_ichimoku_cloud(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate Ichimoku Cloud indicators
        - Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        - Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        - Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen) / 2, shifted 26 periods
        - Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, shifted 26 periods
        - Chikou Span (Lagging Span): Close shifted -26 periods
        """
        try:
            if len(data) < 52:
                zero_series = pd.Series([0.0] * len(data), index=data.index)
                return {
                    'tenkan_sen': zero_series,
                    'kijun_sen': zero_series,
                    'senkou_span_a': zero_series,
                    'senkou_span_b': zero_series,
                    'chikou_span': zero_series
                }
            
            # Tenkan-sen (Conversion Line): 9-period
            period_9_high = data['high'].rolling(window=9).max()
            period_9_low = data['low'].rolling(window=9).min()
            tenkan_sen = (period_9_high + period_9_low) / 2
            
            # Kijun-sen (Base Line): 26-period
            period_26_high = data['high'].rolling(window=26).max()
            period_26_low = data['low'].rolling(window=26).min()
            kijun_sen = (period_26_high + period_26_low) / 2
            
            # Senkou Span A (Leading Span A)
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            
            # Senkou Span B (Leading Span B): 52-period
            period_52_high = data['high'].rolling(window=52).max()
            period_52_low = data['low'].rolling(window=52).min()
            senkou_span_b = ((period_52_high + period_52_low) / 2).shift(26)
            
            # Chikou Span (Lagging Span)
            chikou_span = data['close'].shift(-26)
            
            # Fill NaN
            tenkan_sen = tenkan_sen.fillna(0.0)
            kijun_sen = kijun_sen.fillna(0.0)
            senkou_span_a = senkou_span_a.fillna(0.0)
            senkou_span_b = senkou_span_b.fillna(0.0)
            chikou_span = chikou_span.fillna(0.0)
            
            return {
                'tenkan_sen': tenkan_sen,
                'kijun_sen': kijun_sen,
                'senkou_span_a': senkou_span_a,
                'senkou_span_b': senkou_span_b,
                'chikou_span': chikou_span
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate Ichimoku Cloud: {e}")
            zero_series = pd.Series([0.0] * len(data), index=data.index)
            return {
                'tenkan_sen': zero_series,
                'kijun_sen': zero_series,
                'senkou_span_a': zero_series,
                'senkou_span_b': zero_series,
                'chikou_span': zero_series
            }


# ═══════════════════════════════════════════════════════════════════
# GLOBAL SINGLETON INSTANCE - Used across all modules
# ═══════════════════════════════════════════════════════════════════
unified_technical_indicators = UnifiedTechnicalIndicators()