"""
GOD MODE 1000 - SHARED UTILITIES
=================================
Common utility functions to eliminate code duplication across modules
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone, timedelta
from functools import wraps
import warnings
warnings.filterwarnings('ignore')


class SharedUtilities:
    """Shared utility functions used across multiple modules - NO CODE DUPLICATION"""
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safe division with zero-check - used across 10+ modules"""
        try:
            if denominator == 0 or denominator is None:
                return default
            return numerator / denominator
        except Exception:
            return default
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change - used in market data, whale monitor, etc."""
        try:
            if old_value == 0:
                return 0.0
            return ((new_value - old_value) / abs(old_value)) * 100
        except Exception:
            return 0.0
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """Clamp value between min and max"""
        return max(min_value, min(value, max_value))
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Convert value to float safely"""
        try:
            if value is None or value == '':
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Convert value to int safely"""
        try:
            if value is None or value == '':
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def timestamp_to_datetime(timestamp: Any) -> Optional[datetime]:
        """Convert various timestamp formats to datetime"""
        try:
            if isinstance(timestamp, datetime):
                return timestamp
            elif isinstance(timestamp, (int, float)):
                if timestamp > 10**10:
                    return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                else:
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            elif isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return None
        except Exception:
            return None
    
    @staticmethod
    def format_large_number(value: float) -> str:
        """Format large numbers with K, M, B suffixes"""
        try:
            abs_value = abs(value)
            sign = '-' if value < 0 else ''
            
            if abs_value >= 1_000_000_000:
                return f"{sign}{abs_value/1_000_000_000:.2f}B"
            elif abs_value >= 1_000_000:
                return f"{sign}{abs_value/1_000_000:.2f}M"
            elif abs_value >= 1_000:
                return f"{sign}{abs_value/1_000:.2f}K"
            else:
                return f"{sign}{abs_value:.2f}"
        except Exception:
            return "0"
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Generate deterministic cache key from arguments"""
        try:
            key_data = {
                'args': str(args),
                'kwargs': sorted(kwargs.items())
            }
            key_string = json.dumps(key_data, sort_keys=True)
            return hashlib.md5(key_string.encode()).hexdigest()
        except Exception:
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI - DELEGATES to unified_technical_indicators, returns None if no real data"""
        try:
            from unified_technical_indicators import UnifiedTechnicalIndicators
            import numpy as np
            prices_array = np.array(prices) if not isinstance(prices, np.ndarray) else prices
            result = UnifiedTechnicalIndicators.calculate_rsi(prices_array, period)
            
            # CRITICAL: Return None if result is None (insufficient data)
            if result is None:
                return None
            
            if hasattr(result, '__len__') and len(result) > 0:
                last_value = result[-1]
                return float(last_value) if not np.isnan(last_value) else None
            return None
        except Exception as e:
            # CRITICAL: No fallback calculation - must use centralized version only
            # Return None to indicate error
            return None
    
    @staticmethod
    def calculate_volatility(prices: List[float], window: int = 20) -> float:
        """Calculate price volatility (standard deviation %)"""
        try:
            if len(prices) < window:
                window = len(prices)
            
            recent_prices = prices[-window:]
            mean_price = sum(recent_prices) / len(recent_prices)
            variance = sum((p - mean_price) ** 2 for p in recent_prices) / len(recent_prices)
            volatility = variance ** 0.5
            
            return (volatility / mean_price) * 100 if mean_price > 0 else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Normalize trading pair symbol"""
        try:
            symbol = symbol.strip().upper()
            if '/' not in symbol:
                if not any(quote in symbol for quote in ['USDT', 'USD', 'BTC', 'ETH']):
                    symbol = f"{symbol}/USDT"
            return symbol
        except Exception:
            return symbol
    
    @staticmethod
    def validate_address(address: str, blockchain: str = 'eth') -> bool:
        """Validate blockchain address format"""
        try:
            if not address:
                return False
            
            if blockchain.lower() in ['eth', 'bsc', 'polygon']:
                return address.startswith('0x') and len(address) == 42
            elif blockchain.lower() == 'btc':
                return len(address) >= 26 and len(address) <= 35
            else:
                return len(address) > 10
        except Exception:
            return False
    
    @staticmethod
    def exponential_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate exponential backoff delay"""
        try:
            delay = base_delay * (2 ** attempt)
            return min(delay, max_delay)
        except Exception:
            return base_delay


# Create global instance
shared_utilities = SharedUtilities()

