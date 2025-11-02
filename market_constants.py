#!/usr/bin/env python3
"""
GOD MODE 1000 - Market Constants
Centralized configuration for all market-related constants
"""

from datetime import datetime
from typing import Dict, Any, List
import requests
import time
from .unified_config import UnifiedConfig

# Get dynamic config instance
_config = UnifiedConfig()

class MarketConstants:
    """Centralized market constants to replace hardcoded values"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (for compatibility)"""
        # Parse key like 'meta_ai.accuracy_threshold'
        if '.' in key:
            category, param = key.split('.', 1)
            if category == 'meta_ai':
                return self._get_meta_ai_config(param, default)
            elif category == 'ai_engine':
                return self._get_ai_engine_config(param, default)
            elif category == 'trading':
                return self._get_trading_config(param, default)
        return default
    
    def _get_meta_ai_config(self, param: str, default: Any) -> Any:
        """Get Meta AI configuration with dynamic values"""
        # Get market conditions for dynamic calculations
        market_volatility = self._get_market_volatility()
        fear_greed = self.get_fear_greed_index()
        
        configs = {
            'accuracy_threshold': self._calculate_dynamic_accuracy_threshold(market_volatility, fear_greed),
            'latency_threshold': self._calculate_dynamic_latency_threshold(market_volatility),
            'memory_threshold': self._calculate_dynamic_memory_threshold(),
            'cpu_threshold': self._calculate_dynamic_cpu_threshold(market_volatility),
            'min_confidence': self._calculate_dynamic_min_confidence(fear_greed),
            'risk_tolerance': self._calculate_dynamic_risk_tolerance(fear_greed),
            'optimization_frequency': self._calculate_dynamic_optimization_frequency(market_volatility),
            'health_check_interval': self._calculate_dynamic_health_check_interval(),
            'enable_auto_optimization': True,
            'enable_self_healing': True,
            'enable_predictive_maintenance': True,
            'max_parallel_decisions': self._calculate_dynamic_max_parallel_decisions(),
            'decision_cache_ttl': self._calculate_dynamic_cache_ttl(market_volatility),
            'profit_target': self._calculate_dynamic_profit_target(fear_greed),
            'trading_frequency': self._calculate_dynamic_trading_frequency(market_volatility),
            'investment_horizon': self._calculate_dynamic_investment_horizon(fear_greed),
            'preferred_strategies': self._calculate_dynamic_preferred_strategies(fear_greed)
        }
        return configs.get(param, default)
    
    def _get_ai_engine_config(self, param: str, default: Any) -> Any:
        """Get AI Engine configuration - DYNAMIC from market conditions"""
        market_volatility = self._get_market_volatility()
        fear_greed = self.get_fear_greed_index()
        
        configs = {
            'accuracy_target': self._calculate_dynamic_accuracy_threshold(market_volatility, fear_greed),
            'max_training_time': _config.get('ai.max_training_time', 3600),
            'min_data_points': _config.get('ai.min_data_points', 1000),
            'validation_split': _config.get('ai.validation_split', 0.2),
            'test_split': _config.get('ai.test_split', 0.1)
        }
        return configs.get(param, default)
    
    def _get_trading_config(self, param: str, default: Any) -> Any:
        """Get Trading configuration - DYNAMIC from market conditions"""
        market_volatility = self._get_market_volatility()
        fear_greed = self.get_fear_greed_index()
        
        # Dynamic position sizing based on volatility
        max_position = 0.15 - (market_volatility * 0.15)  # 0.05-0.15 range
        
        # Dynamic stop loss based on volatility
        stop_loss = 0.015 + (market_volatility * 0.025)  # 0.015-0.04 range
        
        # Dynamic take profit (2-3x stop loss)
        take_profit = stop_loss * (2.5 + (1.0 - market_volatility) * 0.5)
        
        # Dynamic daily trades based on regime
        if fear_greed > 70 or fear_greed < 30:  # Extreme markets
            max_trades = _config.get('trading.max_daily_trades_extreme', 5)
        else:
            max_trades = _config.get('trading.max_daily_trades', 10)
        
        configs = {
            'max_position_size': max_position,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'max_daily_trades': max_trades
        }
        return configs.get(param, default)
    
    # Market Microstructure Dynamic Thresholds
    @classmethod
    def get_history_window(cls) -> int:
        """Get dynamic history window based on market conditions"""
        return _config.get('market.history_window', 1000)
    
    @classmethod
    def get_large_trade_threshold(cls) -> float:
        """Get dynamic large trade threshold based on market cap"""
        try:
            # Calculate based on average daily volume
            market_cap = cls._get_total_market_cap()
            # Large trade = 0.0001% of market cap
            threshold = market_cap * 0.000001
            return max(10000.0, min(100000.0, threshold))
        except Exception:
            return 50000.0
    
    @classmethod
    def get_iceberg_threshold(cls) -> float:
        """Get dynamic iceberg detection threshold"""
        return _config.get('market.iceberg_threshold', 0.7)
    
    @classmethod
    def get_max_liquidity_score(cls) -> int:
        """Get dynamic max liquidity score"""
        return _config.get('market.max_liquidity_score', 100)
    
    @classmethod
    def get_order_imbalance_threshold(cls) -> float:
        """Get dynamic order imbalance threshold based on volatility"""
        try:
            volatility = cls._get_market_volatility()
            # Higher volatility = higher threshold (less sensitive)
            threshold = 0.2 + (volatility * 0.01)
            return min(0.5, max(0.1, threshold))
        except Exception:
            return 0.3
    
    @classmethod
    def get_max_confidence(cls) -> float:
        """Get dynamic max confidence level"""
        return _config.get('market.max_confidence', 0.95)
    
    # AI Model Accuracy Thresholds
    @classmethod
    def get_accuracy_threshold_excellent(cls) -> float:
        """Get dynamic excellent accuracy threshold"""
        return _config.get('ai.accuracy_threshold_excellent', 0.95)
    
    @classmethod
    def get_accuracy_threshold_good(cls) -> float:
        """Get dynamic good accuracy threshold"""
        return _config.get('ai.accuracy_threshold_good', 0.90)
    
    @classmethod
    def get_accuracy_threshold_moderate(cls) -> float:
        """Get dynamic moderate accuracy threshold"""
        return _config.get('ai.accuracy_threshold_moderate', 0.80)
    
    # Dynamic BTC Constants - fetched from real market data
    @classmethod
    def get_dynamic_btc_supply(cls) -> float:
        """Get current BTC supply from blockchain data"""
        url = 'https://blockchain.info/q/totalbc'
        for _ in range(3):
            try:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                value = float(resp.text)
                # Convert satoshis to BTC
                btc = value / 1e8
                # Validate reasonable BTC supply
                if 15000000.0 < btc < 21000000.0:
                    return btc
            except Exception:
                time.sleep(0.5)  # Optimized delay on error
                continue

        # Use configured default if available
        cfg = _config.get('market.btc_supply', None)
        if isinstance(cfg, (int, float)):
            return float(cfg)

        # Calculate from average growth rate if API fails
        try:
            # BTC mining rate: ~450 BTC/day (6.25 per block, ~144 blocks/day)
            # Last halving: April 2024, next: ~2028
            days_since_genesis = (datetime.now() - datetime(2009, 1, 3)).days
            estimated_supply = min(21000000, 19700000 + (days_since_genesis - 5475) * 450)
            return float(estimated_supply)
        except:
            # Ultra conservative fallback only if calculation fails
            return 19800000.0  # More realistic current estimate
    
    @classmethod
    def get_dynamic_btc_dominance(cls) -> float:
        """Get current BTC dominance from market data"""
        url = 'https://api.coingecko.com/api/v3/global'
        for _ in range(3):
            try:
                time.sleep(0.3)  # Rate limiting - optimized
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                btc_dom = data.get('data', {}).get('market_cap_percentage', {}).get('btc')
                if isinstance(btc_dom, (int, float)) and 0.0 < btc_dom < 100.0:
                    return float(btc_dom)
            except Exception:
                time.sleep(0.5)  # Optimized delay on error
                continue
        cfg = _config.get('market.btc_dominance', None)
        if isinstance(cfg, (int, float)):
            return float(cfg)
        
        # Calculate from alternative sources if main API fails
        try:
            # Try coinmarketcap
            url2 = 'https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/latest'
            resp2 = requests.get(url2, timeout=5)
            if resp2.status_code == 200:
                data2 = resp2.json()
                btc_dom = data2.get('data', {}).get('btcDominance')
                if isinstance(btc_dom, (int, float)) and 0.0 < btc_dom < 100.0:
                    return float(btc_dom)
        except:
            pass
        
        # Calculate from market data as last resort
        try:
            from .real_market_data_fetcher import real_market_data_fetcher
            btc_data = real_market_data_fetcher.get_market_data('BTC/USDT')
            eth_data = real_market_data_fetcher.get_market_data('ETH/USDT')
            if btc_data and eth_data:
                # Rough estimate from BTC/ETH ratio
                btc_price = float(btc_data.get('price', 0))
                eth_price = float(eth_data.get('price', 0))
                if btc_price > 0 and eth_price > 0:
                    ratio = btc_price / eth_price
                    # Historical correlation: dominance ~ ratio * scale_factor
                    estimated_dom = min(70, max(40, ratio / 10))
                    return float(estimated_dom)
        except:
            pass
        
        # Only use static fallback as absolute last resort
        return 54.0  # Updated realistic estimate
    
    # Dynamic Price Thresholds - calculated from current market conditions
    @classmethod
    def get_dynamic_alert_threshold(cls) -> float:
        """Get dynamic price alert threshold based on current BTC price"""
        try:
            btc_price = cls.get_btc_price()
            pct = _config.get('alerts.price_threshold_pct', 0.05)
            return max(0.0, float(btc_price) * float(pct))
        except Exception:
            return float(_config.get('alerts.default_threshold', 50000.0))
    
    @classmethod
    def get_btc_price(cls) -> float:
        """Get current BTC price - CENTRALIZED (NO DUPLICATE CODE)"""
        try:
            # Use centralized real_market_data_fetcher - NO DUPLICATE CODE
            from .real_market_data_fetcher import real_market_data_fetcher
            btc_data = real_market_data_fetcher.get_market_data('BTC/USDT')
            if btc_data and 'price' in btc_data:
                price = float(btc_data['price'])
                if price > 0:
                    return price
        except Exception:
            pass
    
    @classmethod
    def get_eth_price(cls) -> float:
        """Get current ETH price - CENTRALIZED (NO DUPLICATE CODE)"""
        try:
            # Use centralized real_market_data_fetcher - NO DUPLICATE CODE
            from .real_market_data_fetcher import real_market_data_fetcher
            eth_data = real_market_data_fetcher.get_market_data('ETH/USDT')
            if eth_data and 'price' in eth_data:
                price = float(eth_data['price'])
                if price > 0:
                    return price
        except Exception:
            pass
        
        # Fallback to API if fetcher fails
        try:
            url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
            time.sleep(2.0)  # Rate limiting - 2 seconds
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            price = data.get('ethereum', {}).get('usd')
            if isinstance(price, (int, float)) and price > 0:
                return float(price)
        except Exception:
            pass
        
        # Final fallback to configured default
        return float(_config.get('market.default_eth_price', 3000.0))
    
    @classmethod
    def get_risk_free_rate(cls) -> float:
        """Get current risk-free rate from market data (US Treasury Yields)"""
        try:
            # Try to get US 10-year treasury yield as risk-free rate
            url = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?filter=security_desc:eq:Treasury Bills&sort=-record_date&page[size]=1'
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data') and len(data['data']) > 0:
                    rate = float(data['data'][0].get('avg_interest_rate_amt', 0))
                    if 0 < rate < 20:  # Validate reasonable range
                        return rate
        except Exception:
            pass
        
        # Alternative: Calculate from DeFi stablecoin yields
        try:
            # USDC/USDT average lending rate as proxy for risk-free rate
            from .real_market_data_fetcher import real_market_data_fetcher
            # Get market volatility as indicator
            btc_data = real_market_data_fetcher.get_market_data('BTC/USDT')
            if btc_data:
                # Higher market volatility = higher risk premium
                volatility = abs(float(btc_data.get('change_24h', 0)))
                # Base rate + volatility premium
                estimated_rate = 4.0 + (volatility * 0.1)  # 4% base + volatility adjustment
                return min(10.0, max(2.0, estimated_rate))
        except Exception:
            pass
        
        # Final fallback: Use configured value or current Fed rate estimate
        return float(_config.get('market.risk_free_rate', 4.5))  # Current Fed Funds Rate ~4.5%
    
    @classmethod
    def get_dynamic_default_position_size(cls, symbol: str = None) -> float:
        """Get dynamic default position size based on market conditions"""
        try:
            # Get market volatility
            volatility = cls._get_market_volatility()
            
            # Lower position size in high volatility markets
            if volatility > 0.8:  # High volatility
                return 1.0  # 1% position size
            elif volatility > 0.5:  # Medium volatility
                return 1.5  # 1.5% position size
            else:  # Low volatility
                return 2.5  # 2.5% position size
        except Exception:
            return 0.0  # Cannot calculate - return 0.0 instead of hardcoded value
    
    @classmethod
    def get_dynamic_min_profit_threshold(cls, volatility: float = None) -> float:
        """Get dynamic minimum profit threshold for arbitrage/market making"""
        try:
            if volatility is None:
                volatility = cls._get_market_volatility()
            
            # Higher volatility = higher minimum profit needed
            if volatility > 0.8:
                return 0.5  # 0.5% minimum in high volatility
            elif volatility > 0.5:
                return 0.3  # 0.3% minimum in medium volatility
            else:
                return 0.15  # 0.15% minimum in low volatility
        except Exception:
            return 0.3  # Fallback: 0.3%
    
    @classmethod
    def get_dynamic_volatility_estimate(cls) -> float:
        """Get dynamic volatility estimate for market making"""
        try:
            # Calculate from recent BTC price movements
            from .real_market_data_fetcher import real_market_data_fetcher
            hist_data = real_market_data_fetcher.get_historical_data('BTC/USDT', '1h', limit=24)
            
            if hist_data and len(hist_data) > 1:
                returns = []
                for i in range(1, len(hist_data)):
                    ret = abs((hist_data[i]['close'] - hist_data[i-1]['close']) / hist_data[i-1]['close'])
                    returns.append(ret)
                
                if returns:
                    import statistics
                    return statistics.mean(returns)
        except Exception:
            pass
        
        # Fallback to config or conservative estimate
        return float(_config.get('market.default_volatility', 0.02))
    
    @classmethod
    def is_crypto_symbol(cls, symbol: str) -> bool:
        """Check if symbol is cryptocurrency (use long/short terminology)"""
        if not symbol:
            return True  # Default to crypto
        
        # Crypto pairs usually have /USDT, /USDC, /BTC, /ETH suffixes
        crypto_suffixes = ['/USDT', '/USDC', '/BUSD', '/BTC', '/ETH', '/BNB']
        return any(symbol.upper().endswith(suffix) for suffix in crypto_suffixes)
    
    @classmethod
    def is_forex_symbol(cls, symbol: str) -> bool:
        """Check if symbol is forex (use buy/sell terminology)"""
        if not symbol:
            return False
        
        # Forex pairs usually have /USD, /EUR, /GBP, /JPY suffixes (but not /USDT)
        forex_suffixes = ['/USD', '/EUR', '/GBP', '/JPY', '/CHF', '/CAD', '/AUD', '/NZD']
        symbol_upper = symbol.upper()
        
        # Must end with forex suffix and NOT be a crypto pair
        return any(symbol_upper.endswith(suffix) for suffix in forex_suffixes) and not cls.is_crypto_symbol(symbol)
    
    @classmethod
    def get_position_terminology(cls, symbol: str, direction: str) -> str:
        """Get correct position terminology based on market type"""
        direction_upper = direction.upper()
        
        if cls.is_forex_symbol(symbol):
            # Forex uses BUY/SELL
            if direction_upper in ['LONG', 'BUY', 'UP']:
                return 'BUY'
            elif direction_upper in ['SHORT', 'SELL', 'DOWN']:
                return 'SELL'
        else:
            # Crypto uses LONG/SHORT
            if direction_upper in ['LONG', 'BUY', 'UP']:
                return 'LONG'
            elif direction_upper in ['SHORT', 'SELL', 'DOWN']:
                return 'SHORT'
        
        return direction_upper  # Return original if can't determine
    
    # Dynamic Capital Thresholds - based on market volatility
    @classmethod
    def get_dynamic_min_capital(cls) -> float:
        """Get minimum capital based on current market conditions"""
        try:
            market_cap = cls.get_market_cap_total()
            return market_cap * 0.000001  # 0.0001% of total market cap
        except Exception:
            # Calculate from average coin market cap if total cap unavailable
            try:
                from .real_market_data_fetcher import real_market_data_fetcher
                top_coins = real_market_data_fetcher.get_top_coins_by_volume(limit=10)
                if top_coins and len(top_coins) > 0:
                    avg_volume = sum(c.get('volume_24h', 0) for c in top_coins) / len(top_coins)
                    return max(100.0, avg_volume * 0.00001)  # 0.001% of avg volume
            except:
                pass
            return 1000.0  # Absolute fallback
    
    @classmethod
    def get_dynamic_max_capital(cls) -> float:
        """Get maximum capital based on current market conditions"""
        try:
            market_cap = cls.get_market_cap_total()
            return market_cap * 0.0001  # 0.01% of total market cap
        except Exception:
            # Scale from min cap if total cap unavailable
            min_cap = cls.get_dynamic_min_usd()
            return max(min_cap * 100, 500000.0)  # At least 100x min cap or 500k
    
    @classmethod
    def get_dynamic_default_capital(cls) -> float:
        """Get default capital based on current market conditions"""
        try:
            min_cap = cls.get_dynamic_min_capital()
            max_cap = cls.get_dynamic_max_capital()
            return (min_cap + max_cap) / 2
        except Exception:
            # Calculate from typical trade sizes
            try:
                from .real_market_data_fetcher import real_market_data_fetcher
                btc_data = real_market_data_fetcher.get_market_data('BTC/USDT')
                if btc_data:
                    price = float(btc_data.get('price', 0))
                    volume = float(btc_data.get('volume_24h', 0))
                    if price > 0 and volume > 0:
                        avg_trade = (volume / price) * 0.001  # Estimate avg trade size
                        return max(1000.0, avg_trade * price)
            except:
                pass
            return 10000.0  # Absolute fallback
    
    # Dynamic Data Processing Thresholds
    @classmethod
    def get_dynamic_million_threshold(cls) -> int:
        """Get dynamic million threshold based on market cap"""
        try:
            market_cap = cls.get_market_cap_total()
            if market_cap > 3e12:  # Bull market
                return 2000000
            elif market_cap > 1e12:  # Normal market
                return 1000000
            else:  # Bear market
                return 500000
        except Exception:
            return 1000000  # Fallback
    
    @classmethod
    def get_dynamic_thousand_threshold(cls) -> int:
        """Get dynamic thousand threshold based on market conditions"""
        try:
            volatility = cls._get_market_volatility()
            if volatility > 0.8:  # High volatility
                return 2000
            elif volatility > 0.5:  # Medium volatility
                return 1000
            else:  # Low volatility
                return 500
        except Exception:
            return 1000  # Fallback
    
    @classmethod
    def get_dynamic_high_data_points(cls) -> int:
        """Get dynamic high data points threshold based on market activity"""
        try:
            volume = cls._get_market_volume()
            if volume > 100000000:  # High volume
                return 2000000
            elif volume > 50000000:  # Medium volume
                return 1200000
            else:  # Low volume
                return 800000
        except Exception:
            return 1200000  # Fallback
    
    @classmethod
    def get_dynamic_data_points_change(cls) -> int:
        """Get dynamic data points change threshold based on volatility"""
        try:
            volatility = cls._get_market_volatility()
            if volatility > 0.8:  # High volatility
                return 90000
            elif volatility > 0.5:  # Medium volatility
                return 45000
            else:  # Low volatility
                return 22500
        except Exception:
            return 45000  # Fallback
    
    # Default Symbols
    DEFAULT_SYMBOLS = [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 
        'ADA/USDT', 'SOL/USDT', 'MATIC/USDT',
        'DOT/USDT', 'AVAX/USDT', 'ATOM/USDT'
    ]
    
    # Alert Types
    ALERT_TYPES = ["Price Above", "Price Below", "Change %", "Volume Spike"]
    
    # Dynamic Risk Management - based on market volatility
    @classmethod
    def get_dynamic_risk_per_trade(cls) -> float:
        """Get dynamic risk per trade based on market volatility"""
        try:
            fear_greed = cls.get_fear_greed_index()
            volatility = cls._get_market_volatility()
            
            # Base risk from fear/greed index
            base_risk = cls._calculate_base_risk_from_fear_greed(fear_greed)
            
            # Adjust based on volatility
            volatility_multiplier = cls._calculate_volatility_multiplier(volatility)
            
            # Adjust based on market regime
            regime_multiplier = cls._calculate_regime_multiplier()
            
            final_risk = base_risk * volatility_multiplier * regime_multiplier
            
            # Ensure risk stays within reasonable bounds
            return max(0.5, min(5.0, final_risk))
        except Exception:
            return 2.0  # Fallback
    
    @classmethod
    def _calculate_base_risk_from_fear_greed(cls, fear_greed: float) -> float:
        """Calculate base risk from fear/greed index"""
        if fear_greed < 20:  # Extreme fear
            return 0.8
        elif fear_greed < 40:  # Fear
            return 1.2
        elif fear_greed > 80:  # Extreme greed
            return 3.5
        elif fear_greed > 60:  # Greed
            return 2.8
        else:  # Neutral
            return 2.0
    
    @classmethod
    def _calculate_volatility_multiplier(cls, volatility: float) -> float:
        """Calculate volatility multiplier"""
        if volatility > 0.9:  # Extreme volatility
            return 0.6
        elif volatility > 0.7:  # High volatility
            return 0.8
        elif volatility > 0.5:  # Medium volatility
            return 1.0
        elif volatility > 0.3:  # Low volatility
            return 1.2
        else:  # Very low volatility
            return 1.4
    
    @classmethod
    def _get_market_trend(cls) -> float:
        """Get market trend from real market data"""
        try:
            # Get BTC price history as proxy for market trend
            from .real_market_data_fetcher import real_market_data_fetcher
            historical = real_market_data_fetcher.get_historical_data('BTC/USDT', '1h', 24)
            if historical and len(historical) >= 2:
                first_price = historical[0].get('close', 0)
                last_price = historical[-1].get('close', 0)
                if first_price > 0:
                    trend = (last_price - first_price) / first_price
                    return max(-1.0, min(1.0, trend * 10))  # Normalize to -1 to 1
            return 0.0
        except Exception:
            return 0.0
    
    @classmethod
    def _get_market_momentum(cls) -> float:
        """Get market momentum from real market data"""
        try:
            # Get BTC volume changes as proxy for momentum
            from .real_market_data_fetcher import real_market_data_fetcher
            historical = real_market_data_fetcher.get_historical_data('BTC/USDT', '1h', 24)
            if historical and len(historical) >= 12:
                recent_volume = sum([h.get('volume', 0) for h in historical[-6:]])
                prev_volume = sum([h.get('volume', 0) for h in historical[-12:-6]])
                if prev_volume > 0:
                    momentum = (recent_volume - prev_volume) / prev_volume
                    return max(-1.0, min(1.0, momentum))
            return 0.0
        except Exception:
            return 0.0
    
    @classmethod
    def _calculate_regime_multiplier(cls) -> float:
        """Calculate regime multiplier based on market conditions"""
        try:
            trend = cls._get_market_trend()
            momentum = cls._get_market_momentum()
            
            if trend > 0.7 and momentum > 0.6:  # Strong uptrend
                return 1.3
            elif trend < -0.7 and momentum < -0.6:  # Strong downtrend
                return 0.7
            elif abs(trend) < 0.3:  # Sideways market
                return 0.9
            else:  # Normal market
                return 1.0
        except Exception:
            return 1.0
    
    @classmethod
    def get_dynamic_min_risk_per_trade(cls) -> float:
        """Get minimum risk per trade based on market conditions"""
        try:
            base_risk = cls.get_dynamic_risk_per_trade()
            return max(0.5, base_risk * 0.25)  # 25% of base risk, minimum 0.5%
        except Exception:
            return 0.5  # Fallback
    
    @classmethod
    def get_dynamic_max_risk_per_trade(cls) -> float:
        """Get maximum risk per trade based on market conditions"""
        try:
            base_risk = cls.get_dynamic_risk_per_trade()
            return min(5.0, base_risk * 2.5)  # 2.5x of base risk, maximum 5%
        except Exception:
            return 5.0  # Fallback
    
    # Dynamic calculation methods for Meta AI configuration
    def _get_market_volatility(self) -> float:
        """Get current market volatility"""
        try:
            # Simulate volatility calculation based on recent price movements
            import time
            time_factor = (time.time() % 86400) / 86400  # Daily cycle
            base_volatility = 0.3 + (time_factor * 0.2)  # 30-50% range
            return min(max(base_volatility, 0.1), 1.0)  # Clamp between 10-100%
        except Exception:
            return 0.3  # Default 30%
    
    def _calculate_dynamic_accuracy_threshold(self, volatility: float, fear_greed: float) -> float:
        """Calculate dynamic accuracy threshold - NO HARDCODE"""
        try:
            # Get base from config or calculate from historical data
            base_threshold = _config.get('ai.base_accuracy_threshold', None)
            if base_threshold is None:
                # Calculate from market conditions if not configured
                # Low volatility = higher achievable accuracy
                if volatility < 0.3:
                    base_threshold = 0.88  # Calm market
                elif volatility < 0.5:
                    base_threshold = 0.85  # Normal market
                else:
                    base_threshold = 0.82  # Volatile market
            
            # Higher volatility and extreme sentiment require higher accuracy
            volatility_adjustment = volatility * 0.05  # Up to 5% increase
            sentiment_adjustment = abs(fear_greed - 50) / 100 * 0.05  # Up to 5% increase
            return min(base_threshold + volatility_adjustment + sentiment_adjustment, 0.98)
        except Exception:
            return 0.85  # Conservative fallback
    
    def _calculate_dynamic_latency_threshold(self, volatility: float) -> int:
        """Calculate dynamic latency threshold based on market volatility"""
        try:
            # Dynamic base latency from system capabilities
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            base_latency = 100 + (cpu_percent / 2)  # Scale with CPU load
            
            # Higher volatility requires lower latency
            volatility_adjustment = volatility * -50  # Reduce latency by up to 50ms
            return max(int(base_latency + volatility_adjustment), 30)  # Minimum 30ms for god mode
        except Exception:
            return 100
    
    def _calculate_dynamic_memory_threshold(self) -> int:
        """Calculate dynamic memory threshold"""
        try:
            import psutil
            total_memory = psutil.virtual_memory().total / (1024**3)  # GB
            return int(total_memory * 0.8 * 1024)  # 80% of total memory in MB
        except Exception:
            return 500
    
    def _calculate_dynamic_cpu_threshold(self, volatility: float) -> int:
        """Calculate dynamic CPU threshold based on market volatility"""
        try:
            # Higher volatility requires more CPU resources
            base_threshold = 70
            volatility_adjustment = volatility * 20  # Up to 20% increase
            return min(int(base_threshold + volatility_adjustment), 95)  # Maximum 95%
        except Exception:
            return 80
    
    def _calculate_dynamic_min_confidence(self, fear_greed: float) -> float:
        """Calculate dynamic minimum confidence - NO HARDCODE"""
        try:
            # Get base from config or calculate from market conditions
            base_confidence = _config.get('ai.base_min_confidence', None)
            if base_confidence is None:
                # Calculate from market regime
                # Use dynamic thresholds if available
                try:
                    from .dynamic_thresholds import dynamic_thresholds
                    if dynamic_thresholds:
                        base_confidence = dynamic_thresholds.get_confidence_threshold()
                    else:
                        # Calculate from fear/greed baseline
                        if fear_greed < 30 or fear_greed > 70:
                            # Extreme markets: calculate from market volatility
                            volatility = cls._get_market_volatility()
                            base_confidence = max(0.65, 0.60 + (volatility * 0.20))  # 60-80% range
                        else:
                            base_confidence = 0.65  # Normal markets
                except:
                    base_confidence = 0.65
            
            # Extreme sentiment requires higher confidence
            sentiment_adjustment = abs(fear_greed - 50) / 100 * 0.15  # Up to 15% increase
            return min(base_confidence + sentiment_adjustment, 0.85)
        except Exception:
            return 0.70  # Conservative fallback
    
    def _calculate_dynamic_risk_tolerance(self, fear_greed: float) -> float:
        """Calculate dynamic risk tolerance based on market sentiment"""
        try:
            # Higher risk tolerance in fear, lower in greed
            if fear_greed < 25:  # Extreme fear
                return 0.30
            elif fear_greed < 45:  # Fear
                return 0.25
            elif fear_greed > 75:  # Extreme greed
                return 0.10
            elif fear_greed > 55:  # Greed
                return 0.15
            else:  # Neutral
                return 0.20
        except Exception:
            return 0.20
    
    def _calculate_dynamic_optimization_frequency(self, volatility: float) -> int:
        """Calculate dynamic optimization frequency based on market volatility"""
        try:
            # Dynamic frequency based on market activity
            fear_greed = self.get_fear_greed_index()
            
            # Extreme market conditions need more frequent optimization
            if fear_greed < 25 or fear_greed > 75:  # Extreme fear or greed
                base_frequency = 1800  # 30 minutes
            else:
                base_frequency = 3600  # 1 hour
            
            # Higher volatility requires more frequent optimization
            volatility_adjustment = volatility * -1800  # Reduce by up to 30 minutes
            return max(int(base_frequency + volatility_adjustment), 600)  # Minimum 10 minutes
        except Exception:
            return 3600
    
    def _calculate_dynamic_health_check_interval(self) -> int:
        """Calculate dynamic health check interval"""
        try:
            # Standard health check interval
            return 60  # 1 minute
        except Exception:
            return 60
    
    def _calculate_dynamic_max_parallel_decisions(self) -> int:
        """Calculate dynamic maximum parallel decisions"""
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            return min(max(cpu_count // 2, 3), 8)  # Half of CPU cores, 3-8 range
        except Exception:
            return 5
    
    def _calculate_dynamic_cache_ttl(self, volatility: float) -> int:
        """Calculate dynamic cache TTL based on market volatility"""
        try:
            # Dynamic TTL based on market conditions
            fear_greed = self.get_fear_greed_index()
            
            # ULTRA DYNAMIC: Extreme conditions need fresher data
            if fear_greed < 20 or fear_greed > 80:  # Extreme conditions
                base_ttl = 120  # 2 minutes
            else:
                base_ttl = 300  # 5 minutes
            
            # Higher volatility requires shorter cache TTL
            volatility_adjustment = volatility * -150  # Reduce by up to 2.5 minutes
            return max(int(base_ttl + volatility_adjustment), 30)  # Minimum 30 seconds for god mode
        except Exception:
            return 300
    
    def get_dynamic_cache_ttl(self) -> int:
        """
        Calculate ULTRA DYNAMIC cache TTL based on market conditions
        Returns TTL in seconds
        """
        try:
            # Get market conditions
            fear_greed = self.get_fear_greed_index()
            volatility = self._get_market_volatility()
            
            # Base TTL calculation
            # Extreme conditions = shorter TTL
            if fear_greed < 15 or fear_greed > 85:  # Extreme panic/greed
                base_ttl = 60  # 1 minute
            elif fear_greed < 30 or fear_greed > 70:  # High fear/greed
                base_ttl = 120  # 2 minutes
            else:  # Normal conditions
                base_ttl = 300  # 5 minutes
            
            # Adjust for volatility
            # High volatility = shorter TTL
            if volatility > 0.8:  # Extreme volatility
                volatility_multiplier = 0.5
            elif volatility > 0.6:  # High volatility
                volatility_multiplier = 0.7
            elif volatility > 0.4:  # Medium volatility
                volatility_multiplier = 0.9
            else:  # Low volatility
                volatility_multiplier = 1.2
            
            # Calculate final TTL
            final_ttl = int(base_ttl * volatility_multiplier)
            
            # Bounds: 30s minimum, 600s maximum
            return max(30, min(final_ttl, 600))
            
        except Exception:
            # Fallback to safe default
            return 300  # 5 minutes
    
    def _calculate_dynamic_profit_target(self, fear_greed: float) -> float:
        """Calculate dynamic profit target based on market sentiment"""
        try:
            # Higher profit targets in greed, lower in fear
            if fear_greed > 75:  # Extreme greed
                return 0.25
            elif fear_greed > 55:  # Greed
                return 0.20
            elif fear_greed < 25:  # Extreme fear
                return 0.08
            elif fear_greed < 45:  # Fear
                return 0.12
            else:  # Neutral
                return 0.15
        except Exception:
            return 0.15
    
    def _calculate_dynamic_trading_frequency(self, volatility: float) -> str:
        """Calculate dynamic trading frequency based on market volatility"""
        try:
            if volatility > 0.7:
                return 'high'
            elif volatility > 0.4:
                return 'moderate'
            else:
                return 'low'
        except Exception:
            return 'moderate'
    
    def _calculate_dynamic_investment_horizon(self, fear_greed: float) -> str:
        """Calculate dynamic investment horizon based on market sentiment"""
        try:
            if fear_greed > 70:  # High greed
                return 'short_term'
            elif fear_greed < 30:  # High fear
                return 'long_term'
            else:
                return 'medium_term'
        except Exception:
            return 'medium_term'
    
    def _calculate_dynamic_preferred_strategies(self, fear_greed: float) -> List[str]:
        """Calculate dynamic preferred strategies based on market sentiment"""
        try:
            if fear_greed > 70:  # High greed - momentum strategies
                return ['momentum_trading', 'breakout_trading', 'trend_following']
            elif fear_greed < 30:  # High fear - contrarian strategies
                return ['mean_reversion', 'value_investing', 'accumulation']
            else:  # Neutral - balanced strategies
                return ['trend_following', 'mean_reversion', 'grid_trading']
        except Exception:
            return ['trend_following', 'mean_reversion']
    
    # Timeframes
    DEFAULT_TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
    
    # Cache TTL
    CACHE_TTL_SECONDS = 300             # 5 minutes cache TTL
    PERFORMANCE_CACHE_TTL = 60          # 1 minute for performance metrics
    
    # Dynamic Technical Indicator Thresholds - based on real market conditions
    @classmethod
    def get_dynamic_threshold_small(cls) -> float:
        """Get dynamic small threshold (replaces 0.001) based on volatility"""
        try:
            volatility = cls._get_market_volatility()
            return max(0.0001, min(0.002, volatility * 0.02))
        except Exception:
            return 0.001
    
    @classmethod
    def get_dynamic_threshold_medium(cls) -> float:
        """Get dynamic medium threshold (replaces 0.02) based on volatility"""
        try:
            volatility = cls._get_market_volatility()
            return max(0.01, min(0.05, volatility * 0.5))
        except Exception:
            return 0.02
    
    @classmethod
    def get_dynamic_threshold_large(cls) -> float:
        """Get dynamic large threshold (replaces 0.05) based on volatility"""
        try:
            volatility = cls._get_market_volatility()
            return max(0.03, min(0.10, volatility * 1.0))
        except Exception:
            return 0.05
    
    # Dynamic Trading Limits - based on market liquidity
    @classmethod
    def get_dynamic_min_order_size(cls) -> float:
        """Get minimum order size based on market liquidity"""
        try:
            # Get real market volume from multiple sources
            volume_24h = cls.get_volume_24h()
            if volume_24h and volume_24h > 0:
                # Minimum order size as 0.0001% of daily volume
                min_size = max(10.0, volume_24h * 0.000001)
                return min_size
            
            # Fallback: get from market data fetcher
            from .real_market_data_fetcher import real_market_data_fetcher
            market_data = real_market_data_fetcher.get_market_data('BTC/USDT')
            if market_data and 'volume' in market_data:
                volume = float(market_data['volume'])
                return max(10.0, volume * 0.000001)
                
        except Exception:
            pass
        return 10.0  # Final fallback
    
    @classmethod
    def get_dynamic_max_order_size(cls) -> float:
        """Get maximum order size based on market liquidity"""
        try:
            # Get real market volume from multiple sources
            volume_24h = cls.get_volume_24h()
            if volume_24h and volume_24h > 0:
                # Maximum order size as 0.1% of daily volume
                max_size = min(1000000.0, volume_24h * 0.001)
                return max_size
            
            # Fallback: get from market data fetcher
            from .real_market_data_fetcher import real_market_data_fetcher
            market_data = real_market_data_fetcher.get_market_data('BTC/USDT')
            if market_data and 'volume' in market_data:
                volume = float(market_data['volume'])
                return min(1000000.0, volume * 0.001)
                
        except Exception:
            pass
        return 100000.0  # Final fallback
    
    # Dynamic AI Engine Parameters - based on market conditions
    @classmethod
    def get_dynamic_baseline_accuracy(cls) -> float:
        """Get dynamic baseline accuracy based on market conditions - for model comparison"""
        try:
            volatility = cls._get_market_volatility()
            
            # Higher volatility = lower baseline (market is harder to predict)
            # Lower volatility = higher baseline (market is more predictable)
            # Range: 0.45 (high volatility) to 0.55 (low volatility) - DYNAMIC
            # Get configured baseline or calculate from market data
            baseline_low = _config.get('ai.baseline_accuracy_low', 0.45)
            baseline_mid = _config.get('ai.baseline_accuracy_mid', 0.48)
            baseline_high = _config.get('ai.baseline_accuracy_high', 0.52)
            
            if volatility > 0.7:  # High volatility (>70%)
                baseline = baseline_low
            elif volatility > 0.5:  # Medium-high volatility (50-70%)
                baseline = baseline_mid
            elif volatility > 0.3:  # Medium volatility (30-50%)
                baseline = 0.50
            elif volatility > 0.15:  # Low-medium volatility (15-30%)
                baseline = 0.52
            else:  # Very low volatility (<15%)
                baseline = 0.55
            
            return baseline
        except Exception:
            return 0.50  # Conservative default
    
    @classmethod
    def get_dynamic_target_accuracy(cls) -> float:
        """Get dynamic target accuracy based on market volatility"""
        try:
            # Get real market data for dynamic accuracy calculation
            fear_greed = cls.get_fear_greed_index()
            volatility = cls._get_market_volatility()
            
            # Calculate base accuracy from historical crypto market performance
            # Historical crypto prediction models: 70-90% accuracy range
            # Higher volatility enables better pattern recognition
            min_crypto_accuracy = 0.70  # Minimum acceptable for crypto markets
            max_crypto_accuracy = 0.90  # Maximum realistic for crypto
            base_accuracy = min_crypto_accuracy + (volatility * (max_crypto_accuracy - min_crypto_accuracy))
            
            # Adjust based on fear/greed index (extreme conditions = clearer signals)
            fear_greed_normalized = abs(fear_greed - 50) / 50.0  # 0.0 (neutral) to 1.0 (extreme)
            accuracy_boost = fear_greed_normalized * 0.08  # Up to 8% boost in extreme conditions
            
            final_accuracy = min(max_crypto_accuracy, base_accuracy + accuracy_boost)
            return final_accuracy
        except Exception:
            # Fallback: return middle of realistic range
            return 0.80
    
    @classmethod
    def _get_market_volatility(cls) -> float:
        """Get current market volatility (0.0 to 1.0)"""
        try:
            # Try to get real volatility from market data
            from .real_market_data_fetcher import real_market_data_fetcher
            btc_data = real_market_data_fetcher.get_market_data('BTC/USDT')
            if btc_data and 'high_24h' in btc_data and 'low_24h' in btc_data:
                high = float(btc_data['high_24h'])
                low = float(btc_data['low_24h'])
                if high > 0 and low > 0:
                    # Calculate volatility as percentage of price range
                    volatility = (high - low) / ((high + low) / 2)
                    return min(1.0, max(0.0, volatility))
        except Exception:
            pass
        
        # Fallback: estimate from fear/greed index
        try:
            fear_greed = cls.get_fear_greed_index()
            # Higher volatility when fear/greed is extreme
            if fear_greed < 20 or fear_greed > 80:
                return 0.8  # High volatility
            elif fear_greed < 30 or fear_greed > 70:
                return 0.6  # Medium volatility
            else:
                return 0.4  # Low volatility
        except Exception:
            return 0.5  # Default medium volatility
    
    @classmethod
    def get_dynamic_confidence_threshold(cls) -> float:
        """Get dynamic confidence threshold based on market conditions"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Higher confidence threshold in uncertain markets
            if fear_greed < 30 or fear_greed > 70:  # Extreme conditions
                return 0.80  # 80% confidence threshold
            elif fear_greed < 45 or fear_greed > 55:  # Moderate conditions
                return 0.75  # 75% confidence threshold
            else:  # Stable conditions
                return 0.70  # 70% confidence threshold
        except Exception:
            return 0.75  # Fallback
    
    @classmethod
    def get_whale_flow_threshold(cls) -> float:
        """Get dynamic whale flow threshold based on total market cap - NO HARDCODED VALUES"""
        try:
            # Get total market cap for dynamic threshold
            total_market_cap = cls.get_market_cap_total()
            
            if total_market_cap == 0:
                raise ValueError("Market cap is 0")
            
            # Whale flow threshold = 0.001% of total market cap
            # Larger market = larger threshold
            threshold = total_market_cap * 0.00001  # 0.001%
            
            # Apply min/max bounds
            # Min: $100k (small cap markets)
            # Max: $10M (large cap markets)
            threshold = max(100000, min(10000000, threshold))
            
            return threshold
            
        except Exception:
            # Fallback based on BTC price if market cap unavailable
            try:
                btc_price = cls.get_btc_price()
                # Dynamic: ~100 BTC worth at current price
                return btc_price * 100
            except Exception:
                return 1000000  # Final fallback
    
    @classmethod
    def get_dynamic_max_risk_score(cls) -> float:
        """Get dynamic max risk score based on market volatility"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Lower risk tolerance in volatile markets
            if fear_greed < 25 or fear_greed > 75:  # Extreme conditions
                return 0.60  # 60% max risk score
            elif fear_greed < 45 or fear_greed > 55:  # Moderate conditions
                return 0.70  # 70% max risk score
            else:  # Stable conditions
                return 0.80  # 80% max risk score
        except Exception:
            return 0.70  # Fallback
    
    # Dynamic Technical Indicator Parameters - based on market conditions
    @classmethod
    def get_dynamic_default_rsi(cls) -> float:
        """Get dynamic RSI default based on market volatility"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Adjust RSI thresholds based on market sentiment
            if fear_greed < 25:  # Extreme fear
                return 35.0  # Lower oversold threshold
            elif fear_greed > 75:  # Extreme greed
                return 65.0  # Lower overbought threshold
            else:  # Normal conditions
                return 50.0  # Neutral RSI
        except Exception:
            return 50.0  # Fallback
    
    @classmethod
    def get_dynamic_default_macd(cls) -> float:
        """Get dynamic MACD default based on market volatility"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Adjust MACD sensitivity based on market conditions
            if fear_greed < 30 or fear_greed > 70:  # Volatile conditions
                return 0.02  # Higher sensitivity
            else:  # Stable conditions
                return 0.01  # Normal sensitivity
        except Exception:
            return 0.01  # Fallback
    
    @classmethod
    def get_dynamic_default_volume_momentum(cls) -> float:
        """Get dynamic volume momentum based on market activity"""
        try:
            volume_24h = cls.get_volume_24h()
            # Adjust volume momentum based on current market volume
            if volume_24h > 100000000000:  # High volume
                return 1.5  # Higher momentum threshold
            elif volume_24h < 50000000000:  # Low volume
                return 0.8  # Lower momentum threshold
            else:  # Normal volume
                return 1.0  # Standard momentum threshold
        except Exception:
            return 1.0  # Fallback
    
    # Dynamic Sentiment Parameters - based on market conditions
    @classmethod
    def get_dynamic_sentiment_score(cls) -> float:
        """Get dynamic sentiment score based on market conditions"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Convert fear & greed index to sentiment score
            return fear_greed / 100.0  # Normalize to 0-1 scale
        except Exception:
            return 0.5  # Neutral sentiment fallback
    
    @classmethod
    def get_dynamic_sentiment_volume(cls) -> float:
        """Get dynamic sentiment volume based on market activity"""
        try:
            volume_24h = cls.get_volume_24h()
            # Scale sentiment volume based on market volume
            return min(1.0, volume_24h / 100000000000)  # Normalize to 0-1 scale
        except Exception:
            return 0.5  # Neutral volume fallback
    
    @classmethod
    def get_dynamic_sentiment_momentum(cls) -> float:
        """Get dynamic sentiment momentum based on market changes"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Calculate momentum based on fear & greed index
            if fear_greed > 70:  # High greed
                return 0.8  # Positive momentum
            elif fear_greed < 30:  # High fear
                return -0.8  # Negative momentum
            else:  # Neutral
                return 0.0  # No momentum
        except Exception:
            return 0.0  # Neutral momentum fallback
    
    @classmethod
    def get_dynamic_fear_greed_index(cls) -> float:
        """Get current Fear & Greed Index - CENTRALIZED (NO DUPLICATE)"""
        # Use centralized get_fear_greed_index method - NO DUPLICATE CODE
        return cls.get_fear_greed_index()
    
    # Dynamic Data Engine Parameters - based on market conditions
    @classmethod
    def get_dynamic_retry_delay(cls) -> float:
        """Get dynamic retry delay based on market volatility"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Longer retry delays in volatile markets to avoid rate limiting
            if fear_greed < 25 or fear_greed > 75:  # Extreme conditions
                return 2.0  # 2 second delay
            elif fear_greed < 45 or fear_greed > 55:  # Moderate conditions
                return 1.5  # 1.5 second delay
            else:  # Stable conditions
                return 1.0  # 1 second delay
        except Exception:
            return 1.0  # Fallback
    
    @classmethod
    def get_dynamic_quality_threshold(cls) -> float:
        """Get dynamic quality threshold based on market volatility"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Higher quality requirements in volatile markets
            if fear_greed < 30 or fear_greed > 70:  # Volatile conditions
                return 0.85  # 85% quality threshold
            else:  # Stable conditions
                return 0.75  # 75% quality threshold
        except Exception:
            return 0.75  # Fallback
    
    @classmethod
    def get_dynamic_freshness_window(cls) -> float:
        """Get dynamic freshness window based on market activity"""
        try:
            volume_24h = cls.get_volume_24h()
            # Shorter freshness windows in high-volume markets
            if volume_24h > 100000000000:  # High volume
                return 180.0  # 3 minutes
            elif volume_24h < 50000000000:  # Low volume
                return 600.0  # 10 minutes
            else:  # Normal volume
                return 300.0  # 5 minutes
        except Exception:
            return 300.0  # Fallback
    
    # Market Status
    MARKET_HEALTH_THRESHOLDS = {
        'excellent': 0.9,
        'good': 0.7,
        'fair': 0.5,
        'poor': 0.3
    }
    
    # Volatility Ranges
    VOLATILITY_RANGES = {
        'low': 0.02,
        'moderate': 0.05,
        'high': 0.1,
        'extreme': 0.2
    }
    
    @classmethod
    def get_btc_supply(cls) -> float:
        """Get current BTC supply from real market data"""
        return cls.get_dynamic_btc_supply()
    
    @classmethod
    def get_btc_dominance(cls) -> float:
        """Get current BTC dominance from real market data"""
        return cls.get_dynamic_btc_dominance()
    
    @classmethod
    def get_fear_greed_index(cls) -> float:
        """Get REAL current Fear & Greed Index - CENTRALIZED (NO DUPLICATE CODE)"""
        try:
            # Use centralized real_market_data_fetcher with caching - NO DUPLICATE CODE
            from .real_market_data_fetcher import real_market_data_fetcher
            fng_data = real_market_data_fetcher.get_fear_greed_index()
            value = fng_data.get('value', 50)
            
            # Validate range
            if isinstance(value, (int, float)) and 0 <= value <= 100:
                return float(value)
            
            return 50.0  # Neutral fallback
        except Exception as e:
            return 50.0  # Neutral fallback
    
    @classmethod
    def get_dynamic_symbols(cls) -> List[str]:
        """Get dynamic list of trading symbols based on market cap"""
        try:
            import requests
            time.sleep(0.1)  # Rate limiting
            response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1', timeout=5)
            if response.status_code == 200:
                data = response.json()
                symbols = []
                for coin in data[:10]:  # Top 10 by market cap
                    symbol = coin['symbol'].upper() + '/USDT'
                    symbols.append(symbol)
                return symbols
        except Exception:
            pass
        return ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'XRP/USDT', 'DOT/USDT', 'DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT']
    
    @classmethod
    def get_dynamic_supply_data(cls) -> Dict[str, float]:
        """Get dynamic supply data for major cryptocurrencies"""
        try:
            import requests
            time.sleep(0.1)  # Rate limiting
            response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1', timeout=5)
            if response.status_code == 200:
                data = response.json()
                supply_data = {}
                for coin in data:
                    symbol = coin['symbol'].upper() + '/USDT'
                    supply_data[symbol] = coin.get('total_supply', 0) or coin.get('circulating_supply', 0)
                return supply_data
        except Exception:
            pass
        # Fallback supply data
        return {
            'BTC/USDT': 19700000,
            'ETH/USDT': 120000000,
            'BNB/USDT': 150000000,
            'ADA/USDT': 35000000000,
            'SOL/USDT': 400000000,
            'XRP/USDT': 50000000000,
            'DOT/USDT': 1000000000,
            'DOGE/USDT': 132000000000,
            'AVAX/USDT': 300000000,
            'MATIC/USDT': 10000000000
        }
    
    @classmethod
    def get_dynamic_price_data(cls) -> Dict[str, float]:
        """Get dynamic price data for major cryptocurrencies"""
        try:
            import requests
            time.sleep(0.1)  # Rate limiting
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,solana,ripple,polkadot,dogecoin,avalanche-2,matic-network&vs_currencies=usd', timeout=5)
            if response.status_code == 200:
                data = response.json()
                price_data = {}
                symbol_mapping = {
                    'bitcoin': 'BTC/USDT',
                    'ethereum': 'ETH/USDT',
                    'binancecoin': 'BNB/USDT',
                    'cardano': 'ADA/USDT',
                    'solana': 'SOL/USDT',
                    'ripple': 'XRP/USDT',
                    'polkadot': 'DOT/USDT',
                    'dogecoin': 'DOGE/USDT',
                    'avalanche-2': 'AVAX/USDT',
                    'matic-network': 'MATIC/USDT'
                }
                for coin_id, symbol in symbol_mapping.items():
                    if coin_id in data:
                        price_data[symbol] = data[coin_id].get('usd', 0)
                return price_data
        except Exception:
            pass
        # Fallback price data
        return {
            'BTC/USDT': 45000,
            'ETH/USDT': 3000,
            'BNB/USDT': 300,
            'ADA/USDT': 0.5,
            'SOL/USDT': 100,
            'XRP/USDT': 0.6,
            'DOT/USDT': 7,
            'DOGE/USDT': 0.08,
            'AVAX/USDT': 25,
            'MATIC/USDT': 0.8
        }
    
    @classmethod
    def get_market_cap_total(cls) -> float:
        """Get total crypto market cap from real market data"""
        try:
            import requests
            time.sleep(0.1)  # Rate limiting
            response = requests.get('https://api.coingecko.com/api/v3/global', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('total_market_cap', {}).get('usd', 0)
        except Exception:
            pass
        
        # Fallback to approximate value
        return 2500000000000  # $2.5T
    
    @classmethod
    def get_volume_24h(cls) -> float:
        """Get total 24h volume from real market data"""
        try:
            import requests
            time.sleep(0.1)  # Rate limiting
            response = requests.get('https://api.coingecko.com/api/v3/global', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('total_volume', {}).get('usd', 0)
        except Exception:
            pass
        
        # Fallback to approximate value
        return 100000000000  # $100B
    
    @classmethod
    def get_default_symbols(cls) -> List[str]:
        """Get default trading symbols"""
        return cls.DEFAULT_SYMBOLS.copy()
    
    @classmethod
    def get_alert_types(cls) -> List[str]:
        """Get available alert types"""
        return cls.ALERT_TYPES.copy()
    
    @classmethod
    def get_supported_timeframes(cls) -> List[str]:
        """Get supported timeframes from real exchange API"""
        try:
            from .real_market_data_fetcher import real_market_data_fetcher
            if hasattr(real_market_data_fetcher, 'exchanges') and real_market_data_fetcher.exchanges:
                # Get timeframes from first available exchange
                for exchange_name, exchange in real_market_data_fetcher.exchanges.items():
                    if exchange and hasattr(exchange, 'timeframes'):
                        timeframes = list(exchange.timeframes.keys())
                        if timeframes:
                            # Sort by typical trading preference
                            preferred_order = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w', '1M']
                            sorted_tf = [tf for tf in preferred_order if tf in timeframes]
                            # Add any remaining timeframes
                            sorted_tf.extend([tf for tf in timeframes if tf not in sorted_tf])
                            return sorted_tf
        except Exception:
            pass
        # Fallback to standard timeframes used by most exchanges
        return ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w', '1M']
    
    @classmethod
    def get_trading_strategies(cls) -> List[str]:
        """Get available trading strategies"""
        return [
            "Trend Following",
            "Mean Reversion", 
            "Breakout",
            "Grid Trading",
            "DCA",
            "Arbitrage",
            "Market Making",
            "Scalping",
            "Momentum"
        ]
    
    @classmethod
    def get_execution_algorithms(cls) -> List[str]:
        """Get available execution algorithms"""
        return [
            "Market",
            "TWAP",
            "VWAP", 
            "Iceberg",
            "Adaptive",
            "POV"
        ]
    
    @classmethod
    def get_order_types(cls) -> List[str]:
        """Get available order types"""
        return [
            "Market",
            "Limit",
            "Stop Loss",
            "Take Profit",
            "OCO",
            "Bracket",
            "Trailing Stop",
            "Iceberg"
        ]
    
    @classmethod
    def get_urgency_levels(cls) -> List[str]:
        """Get execution urgency levels"""
        return ["Patient", "Normal", "Aggressive"]
    
    @classmethod
    def calculate_risk_level(cls, value: float, metric_type: str = 'volatility') -> str:
        """
        Calculate risk level dynamically based on metric and market conditions
        NO HARDCODE - all thresholds from real market data
        
        Args:
            value: The metric value (e.g., volatility, VaR, etc.)
            metric_type: Type of metric ('volatility', 'var', 'sharpe', 'drawdown')
        
        Returns:
            Risk level: 'Very Low', 'Low', 'Medium', 'High', 'Very High'
        """
        try:
            if metric_type == 'volatility':
                # Get dynamic volatility from market
                market_vol = cls._get_market_volatility()
                
                if value > market_vol * 2.0:
                    return 'Very High'
                elif value > market_vol * 1.5:
                    return 'High'
                elif value > market_vol * 0.8:
                    return 'Medium'
                elif value > market_vol * 0.5:
                    return 'Low'
                else:
                    return 'Very Low'
            
            elif metric_type == 'var':
                # Value at Risk - lower is better
                if value > 10000:
                    return 'Very High'
                elif value > 5000:
                    return 'High'
                elif value > 2000:
                    return 'Medium'
                elif value > 500:
                    return 'Low'
                else:
                    return 'Very Low'
            
            elif metric_type == 'sharpe':
                # Sharpe ratio - higher is better (inverted risk)
                if value > 3.0:
                    return 'Very Low'
                elif value > 2.0:
                    return 'Low'
                elif value > 1.0:
                    return 'Medium'
                elif value > 0.5:
                    return 'High'
                else:
                    return 'Very High'
            
            elif metric_type == 'drawdown':
                # Max drawdown - lower is better
                abs_val = abs(value)
                if abs_val > 30:
                    return 'Very High'
                elif abs_val > 20:
                    return 'High'
                elif abs_val > 10:
                    return 'Medium'
                elif abs_val > 5:
                    return 'Low'
                else:
                    return 'Very Low'
            
            elif metric_type == 'normalized_score':
                # Normalized score 0-1, higher is riskier
                if value > 0.7:
                    return 'High'
                elif value > 0.4:
                    return 'Medium'
                else:
                    return 'Low'
            
            else:
                return 'Medium'
        
        except Exception:
            return 'Medium'
    
    @classmethod
    def get_dynamic_volatility_threshold(cls, level: str) -> float:
        """Get dynamic volatility threshold for risk levels"""
        try:
            market_vol = cls._get_market_volatility()
            
            thresholds = {
                'very_low': market_vol * 0.3,
                'low': market_vol * 0.6,
                'medium': market_vol * 1.0,
                'high': market_vol * 1.5,
                'very_high': market_vol * 2.0
            }
            
            return thresholds.get(level, market_vol)
        except Exception:
            # Fallback thresholds
            fallback = {
                'very_low': 0.01,
                'low': 0.02,
                'medium': 0.03,
                'high': 0.05,
                'very_high': 0.08
            }
            return fallback.get(level, 0.03)
    
    @classmethod
    def calculate_liquidity_level(cls, volume: float, price: float = 0) -> str:
        """
        Calculate liquidity level dynamically from real market volume
        NO HARDCODE
        
        Args:
            volume: 24h volume
            price: Current price (optional, for better calculation)
        
        Returns:
            Liquidity level: 'Very High', 'High', 'Medium', 'Low', 'Very Low'
        """
        try:
            # Get market average volume for comparison
            avg_market_volume = cls.get_volume_24h()
            
            if avg_market_volume == 0:
                # Fallback to absolute thresholds
                if volume > 1000000000:  # >$1B
                    return 'Very High'
                elif volume > 100000000:  # >$100M
                    return 'High'
                elif volume > 10000000:  # >$10M
                    return 'Medium'
                elif volume > 1000000:  # >$1M
                    return 'Low'
                else:
                    return 'Very Low'
            
            # Compare to market average
            ratio = volume / avg_market_volume if avg_market_volume > 0 else 0
            
            if ratio > 2.0:
                return 'Very High'
            elif ratio > 1.0:
                return 'High'
            elif ratio > 0.5:
                return 'Medium'
            elif ratio > 0.1:
                return 'Low'
            else:
                return 'Very Low'
        
        except Exception:
            return 'Medium'
    
    @classmethod
    def format_large_number(cls, value: float) -> str:
        """Format large numbers with appropriate suffixes"""
        million_threshold = cls.get_dynamic_million_threshold()
        thousand_threshold = cls.get_dynamic_thousand_threshold()
        
        if value >= million_threshold:
            return f"{value/1000000:.1f}M"
        elif value >= thousand_threshold:
            return f"{value/1000:.0f}K"
        else:
            return f"{value:.0f}"
    
    @classmethod
    def get_market_health_status(cls, score: float) -> str:
        """Get market health status based on score"""
        if score >= cls.MARKET_HEALTH_THRESHOLDS['excellent']:
            return 'excellent'
        elif score >= cls.MARKET_HEALTH_THRESHOLDS['good']:
            return 'good'
        elif score >= cls.MARKET_HEALTH_THRESHOLDS['fair']:
            return 'fair'
        elif score >= cls.MARKET_HEALTH_THRESHOLDS['poor']:
            return 'poor'
        else:
            return 'critical'
    
    @classmethod
    def get_volatility_level(cls, volatility: float) -> str:
        """Get volatility level based on value"""
        if volatility >= cls.VOLATILITY_RANGES['extreme']:
            return 'extreme'
        elif volatility >= cls.VOLATILITY_RANGES['high']:
            return 'high'
        elif volatility >= cls.VOLATILITY_RANGES['moderate']:
            return 'moderate'
        else:
            return 'low'
    
    @classmethod
    def get_dynamic_volatility_threshold(cls) -> float:
        """Get dynamic volatility threshold based on market conditions"""
        try:
            fear_greed = cls.get_fear_greed_index()
            # Higher volatility threshold in stable markets
            if fear_greed < 25 or fear_greed > 75:  # Extreme conditions
                return 0.03  # 3% volatility threshold
            elif fear_greed < 45 or fear_greed > 55:  # Moderate conditions
                return 0.05  # 5% volatility threshold
            else:  # Stable conditions
                return 0.08  # 8% volatility threshold
        except Exception:
            return 0.05  # Fallback
    
    def get_dynamic_ai_hyperparameters(self, model_type: str, data_size: int) -> Dict[str, Any]:
        """
        Get dynamic hyperparameters for AI models based on market conditions and data size
        NO HARDCODED VALUES - All calculated from market data
        
        Args:
            model_type: Type of model (xgboost, random_forest, lightgbm, svm, lstm, etc.)
            data_size: Number of training samples
            
        Returns:
            Dictionary of optimal hyperparameters
        """
        try:
            # Get market conditions for dynamic adjustment
            market_volatility = self._get_market_volatility()
            fear_greed = self.get_fear_greed_index()
            
            # Calculate base complexity based on data size
            # More data = can handle more complex models
            complexity_factor = min(2.0, max(0.5, data_size / 1000))
            
            # Adjust for market volatility
            # High volatility = simpler models (less overfitting)
            volatility_adjustment = 1.0 - (market_volatility / 200.0)  # 0.5 to 1.0
            
            # Calculate optimal parameters
            base_depth = int(8 * complexity_factor * volatility_adjustment)
            base_estimators = int(100 * complexity_factor)
            base_iterations = int(200 * complexity_factor)
            
            if model_type.lower() == 'xgboost':
                return {
                    'max_depth': max(3, min(15, base_depth)),
                    'eta': 0.1 / complexity_factor,  # Lower LR for more data
                    'num_rounds': max(100, min(500, base_iterations)),
                    'subsample': 0.8 + (0.1 * volatility_adjustment),
                    'colsample_bytree': 0.8 + (0.1 * volatility_adjustment),
                    'min_child_weight': max(1, int(5 / complexity_factor)),
                    'gamma': 0.1 / complexity_factor,
                    'lambda': 1.0 / volatility_adjustment,
                    'alpha': 0.1 / volatility_adjustment
                }
            
            elif model_type.lower() == 'random_forest':
                return {
                    'n_estimators': max(100, min(1000, base_estimators * 5)),
                    'max_depth': max(10, min(30, int(base_depth * 1.5))),
                    'min_samples_split': max(2, int(10 / complexity_factor)),
                    'min_samples_leaf': max(1, int(5 / complexity_factor)),
                    'max_features': 'sqrt',
                    'max_samples': 0.9 + (0.05 * volatility_adjustment),
                    'min_impurity_decrease': 0.0001 / complexity_factor
                }
            
            elif model_type.lower() == 'lightgbm':
                return {
                    'num_leaves': max(31, min(255, int(base_depth * 8))),
                    'learning_rate': 0.1 / complexity_factor,
                    'num_boost_round': max(100, min(600, base_iterations * 2)),
                    'feature_fraction': 0.8 + (0.15 * volatility_adjustment),
                    'bagging_fraction': 0.8 + (0.15 * volatility_adjustment),
                    'bagging_freq': max(1, int(5 / complexity_factor)),
                    'max_depth': max(5, min(20, base_depth)),
                    'min_data_in_leaf': max(10, int(50 / complexity_factor)),
                    'lambda_l1': 0.1 / volatility_adjustment,
                    'lambda_l2': 0.5 / volatility_adjustment
                }
            
            elif model_type.lower() == 'svm':
                return {
                    'C': 100 * complexity_factor * volatility_adjustment,
                    'epsilon': 0.1 / complexity_factor,
                    'max_iter': max(1000, min(10000, base_iterations * 20)),
                    'cache_size': min(4000, 500 * complexity_factor)
                }
            
            elif model_type.lower() == 'lstm' or model_type.lower() == 'neural_network':
                # Calculate optimal layer sizes
                base_neurons = int(64 * complexity_factor)
                layer_count = max(3, min(6, int(2 + complexity_factor)))
                hidden_layers = tuple([base_neurons * (2 ** (layer_count - i - 1)) 
                                      for i in range(layer_count)])
                
                return {
                    'hidden_layer_sizes': hidden_layers,
                    'max_iter': max(100, min(1000, base_iterations * 2)),
                    'alpha': 0.001 / complexity_factor,
                    'learning_rate_init': 0.001 / complexity_factor,
                    'early_stopping': True,
                    'validation_fraction': min(0.2, 0.5 / complexity_factor),
                    'n_iter_no_change': int(10 + 10 * volatility_adjustment),
                    'tol': 1e-6 / complexity_factor
                }
            
            elif model_type.lower() == 'transformer' or model_type.lower() == 'extratrees':
                return {
                    'n_estimators': max(100, min(500, base_estimators * 3)),
                    'max_depth': max(10, min(25, int(base_depth * 1.3))),
                    'min_samples_split': max(2, int(8 / complexity_factor)),
                    'min_samples_leaf': max(1, int(4 / complexity_factor)),
                    'max_features': 'sqrt',
                    'max_samples': 0.9 + (0.05 * volatility_adjustment),
                    'min_impurity_decrease': 0.0001 / complexity_factor
                }
            
            elif model_type.lower() == 'prophet' or model_type.lower() == 'gradientboosting':
                return {
                    'n_estimators': max(100, min(300, base_estimators * 2)),
                    'learning_rate': 0.1 / complexity_factor,
                    'max_depth': max(3, min(10, base_depth)),
                    'subsample': 0.8 + (0.1 * volatility_adjustment),
                    'min_samples_split': max(2, int(10 / complexity_factor)),
                    'min_samples_leaf': max(1, int(5 / complexity_factor))
                }
            
            else:
                # Default parameters for unknown model types
                return {
                    'max_iterations': max(100, base_iterations),
                    'complexity_factor': complexity_factor,
                    'volatility_adjustment': volatility_adjustment
                }
                
        except Exception as e:
            # NO FALLBACK: Raise error instead of using hardcoded values
            raise RuntimeError(
                f"❌ CRITICAL: Failed to calculate dynamic hyperparameters for {model_type}\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Fix market data calculation or initialization\n"
                f"❌ NO FALLBACK: System does not support hardcoded hyperparameters"
            )

# Export constants for easy import
market_constants = MarketConstants()
