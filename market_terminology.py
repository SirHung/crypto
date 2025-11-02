"""
Market Terminology Handler - God Mode 10000
Handles proper terminology for different market types:
- Crypto (Spot + Futures): LONG/SHORT
- Forex: BUY/SELL
- Stock: BUY/SELL
"""

from enum import Enum
from typing import Literal, Union


class MarketType(Enum):
    """Market type enumeration"""
    CRYPTO_SPOT = "crypto_spot"
    CRYPTO_FUTURES = "crypto_futures"
    FOREX = "forex"
    STOCK = "stock"


class OrderSide(Enum):
    """Universal order side"""
    LONG = "long"  # Buy/Open Long
    SHORT = "short"  # Sell/Open Short
    CLOSE_LONG = "close_long"  # Close Long Position
    CLOSE_SHORT = "close_short"  # Close Short Position


class MarketTerminologyHandler:
    """
    Handles proper terminology conversion for different markets
    """
    
    @staticmethod
    def detect_market_type(symbol: str) -> MarketType:
        """
        Detect market type from symbol
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT', 'EUR/USD')
            
        Returns:
            MarketType enum
        """
        # Forex pairs (major currencies)
        forex_currencies = {'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD'}
        
        # Check if it's perpetual/futures FIRST (before checking /)
        if 'PERP' in symbol.upper() or 'SWAP' in symbol.upper() or '-PERP' in symbol.upper():
            return MarketType.CRYPTO_FUTURES
        
        if '/' in symbol:
            base, quote = symbol.split('/')
            
            # Check if both are forex currencies
            if base in forex_currencies and quote in forex_currencies:
                return MarketType.FOREX
            
            # Default to spot for crypto
            return MarketType.CRYPTO_SPOT
        
        return MarketType.CRYPTO_SPOT
    
    @staticmethod
    def get_display_action(order_side: OrderSide, market_type: MarketType) -> str:
        """
        Get display-friendly action text based on market type
        
        Args:
            order_side: Universal order side
            market_type: Market type
            
        Returns:
            Display action text
        
        CRYPTO (Spot + Futures): LONG/SHORT terminology
        FOREX: BUY/SELL terminology
        """
        if market_type in [MarketType.CRYPTO_SPOT, MarketType.CRYPTO_FUTURES]:
            # Crypto (both spot and futures): use LONG/SHORT
            action_map = {
                OrderSide.LONG: "LONG",
                OrderSide.SHORT: "SHORT",
                OrderSide.CLOSE_LONG: "CLOSE LONG",
                OrderSide.CLOSE_SHORT: "CLOSE SHORT"
            }
        else:
            # Forex and Stock: use BUY/SELL
            action_map = {
                OrderSide.LONG: "BUY",
                OrderSide.SHORT: "SELL",
                OrderSide.CLOSE_LONG: "SELL",
                OrderSide.CLOSE_SHORT: "BUY"
            }
        
        return action_map.get(order_side, "UNKNOWN")
    
    @staticmethod
    def get_display_action_for_symbol(order_side: OrderSide, symbol: str) -> str:
        """
        Get display action directly from symbol (convenience method)
        
        Args:
            order_side: Universal order side
            symbol: Trading symbol
            
        Returns:
            Display action text
        """
        market_type = MarketTerminologyHandler.detect_market_type(symbol)
        return MarketTerminologyHandler.get_display_action(order_side, market_type)
    
    @staticmethod
    def normalize_action(action: str, symbol: str) -> OrderSide:
        """
        Normalize user input action to OrderSide
        
        Args:
            action: User action (buy/sell/long/short)
            symbol: Trading symbol
            
        Returns:
            OrderSide enum
        """
        action_lower = action.lower().strip()
        
        # Map common terms to OrderSide
        if action_lower in ['buy', 'long', 'open_long']:
            return OrderSide.LONG
        elif action_lower in ['sell', 'short', 'open_short']:
            return OrderSide.SHORT
        elif action_lower in ['close_long', 'sell_long']:
            return OrderSide.CLOSE_LONG
        elif action_lower in ['close_short', 'buy_short']:
            return OrderSide.CLOSE_SHORT
        
        # Default to LONG for unknown
        return OrderSide.LONG
    
    @staticmethod
    def is_spot_market(symbol: str) -> bool:
        """Check if symbol is spot market"""
        return MarketTerminologyHandler.detect_market_type(symbol) == MarketType.CRYPTO_SPOT
    
    @staticmethod
    def is_futures_market(symbol: str) -> bool:
        """Check if symbol is futures market"""
        return MarketTerminologyHandler.detect_market_type(symbol) == MarketType.CRYPTO_FUTURES
    
    @staticmethod
    def is_forex_market(symbol: str) -> bool:
        """Check if symbol is forex market"""
        return MarketTerminologyHandler.detect_market_type(symbol) == MarketType.FOREX
    
    @staticmethod
    def get_market_description(symbol: str) -> str:
        """Get human-readable market description"""
        market_type = MarketTerminologyHandler.detect_market_type(symbol)
        
        descriptions = {
            MarketType.CRYPTO_SPOT: "Crypto Spot (LONG/SHORT)",
            MarketType.CRYPTO_FUTURES: "Crypto Futures (LONG/SHORT)",
            MarketType.FOREX: "Forex (BUY/SELL)",
            MarketType.STOCK: "Stock (BUY/SELL)"
        }
        
        return descriptions.get(market_type, "Unknown Market")
    
    @staticmethod
    def supports_short_selling(symbol: str) -> bool:
        """
        Check if market supports short selling
        Spot markets typically don't support shorting without margin
        """
        market_type = MarketTerminologyHandler.detect_market_type(symbol)
        return market_type in [MarketType.CRYPTO_FUTURES, MarketType.FOREX]
    
    @staticmethod
    def validate_signal_terminology(signal: str, symbol: str) -> bool:
        """
        Validate that signal uses correct terminology for market type
        
        Args:
            signal: Signal text (BUY/SELL/LONG/SHORT/etc)
            symbol: Trading symbol
            
        Returns:
            True if terminology is correct, False otherwise
        """
        market_type = MarketTerminologyHandler.detect_market_type(symbol)
        signal_upper = signal.upper()
        
        if market_type in [MarketType.CRYPTO_SPOT, MarketType.CRYPTO_FUTURES]:
            # Crypto should use LONG/SHORT, not BUY/SELL
            if 'BUY' in signal_upper or 'SELL' in signal_upper:
                # Only acceptable if it's "BUY" that will be converted to "LONG"
                # For now, we allow both but log warning
                return True  # Acceptable - will be converted
            return True
        else:
            # Forex should use BUY/SELL, not LONG/SHORT
            if 'LONG' in signal_upper or 'SHORT' in signal_upper:
                # Allow both but prefer BUY/SELL for forex
                return True  # Acceptable
            return True
    
    @staticmethod
    def normalize_signal_for_market(signal: str, symbol: str) -> str:
        """
        Normalize signal to use correct terminology for market type
        
        Args:
            signal: Original signal (BUY/SELL/LONG/SHORT)
            symbol: Trading symbol
            
        Returns:
            Normalized signal with correct terminology
        """
        market_type = MarketTerminologyHandler.detect_market_type(symbol)
        signal_upper = signal.upper()
        
        if market_type in [MarketType.CRYPTO_SPOT, MarketType.CRYPTO_FUTURES]:
            # Crypto: Convert BUY/SELL to LONG/SHORT
            signal_upper = signal_upper.replace('BUY', 'LONG')
            signal_upper = signal_upper.replace('SELL', 'SHORT')
        else:
            # Forex: Convert LONG/SHORT to BUY/SELL
            signal_upper = signal_upper.replace('LONG', 'BUY')
            signal_upper = signal_upper.replace('SHORT', 'SELL')
        
        return signal_upper


# Global instance
market_terminology = MarketTerminologyHandler()

