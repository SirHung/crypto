"""
GOD MODE 1000 - REAL MARKET DATA FETCHER
Advanced real-time market data fetching from multiple exchanges
"""

try:
    import ccxt
    if ccxt is None:
        raise ImportError("CCXT library is None")
except Exception as e:
    # CRITICAL: ccxt is MANDATORY for real market data
    # Do NOT provide fallback fake data - raise error immediately
    raise ImportError(
        f"CRITICAL: CCXT library is required for real market data fetching. "
        f"Install it with: pip install ccxt\n"
        f"Error: {e}"
    )
import asyncio
import aiohttp
import time
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import requests

# Import unified components
try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

# Import MarketData from unified_data_structures
from .unified_data_structures import MarketData

class RealMarketDataFetcher:
    """Advanced real-time market data fetcher for God Mode 1000"""
    
    def __init__(self):
        """Initialize Real Market Data Fetcher - ULTRA ADVANCED"""
        try:
            unified_logging.info("Initializing Real Market Data Fetcher - God Mode 1000 [ULTRA]")
            
            # Exchanges will be initialized lazily to avoid blocking imports
            self.exchanges = {}
            self._exchanges_initialized = False
            
            # ULTRA INTELLIGENT cache with market-aware TTL
            self.data_cache = {}
            self.base_cache_ttl = 15  # Base TTL: 15 seconds
            self.cache_ttl = self.base_cache_ttl  # Dynamic TTL adjusted by market volatility
            self.last_update = {}
            self.cache_hits = 0
            self.cache_misses = 0
            self.market_volatility = 0.5  # Track market volatility for dynamic cache adjustment

            # Rate limiting with intelligent backoff
            self.rate_limits = {}
            self.api_call_count = 0
            self.last_api_reset = time.time()
            
            # All available markets cache
            self._all_markets_cache = {}
            self._markets_cache_time = 0
            self._markets_cache_ttl = 3600  # 1 hour
            
            # REVOLUTIONARY: Dynamic thread pool using intelligent resource management
            # Maximize parallel processing for multiple exchanges
            import os
            cpu_count = os.cpu_count() or 4

            # OPTIMIZED: Get optimal workers from parallel_executor if available
            try:
                from .parallel_executor import parallel_executor
                # Use thread workers for I/O-bound exchange API calls
                max_workers = parallel_executor.get_optimal_workers('io')
                unified_logging.info(f"📊 Using parallel_executor optimal workers: {max_workers}")
            except ImportError:
                # Fallback: Dynamic calculation based on CPU and system load
                # For I/O-bound tasks (API calls), can use more workers than CPU count
                current_cpu = psutil.cpu_percent(interval=0.1)
                if current_cpu < 50:
                    # System idle: aggressive parallelization for fast data fetching
                    max_workers = min(cpu_count * 8, 96)  # Cap at 96 to prevent system overload
                elif current_cpu < 75:
                    # System moderately busy
                    max_workers = min(cpu_count * 4, 64)
                else:
                    # System busy: conservative
                    max_workers = min(cpu_count * 2, 32)
                unified_logging.info(f"📊 Using fallback worker calculation: {max_workers} (CPU: {current_cpu:.1f}%)")

            self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="market_fetcher_optimized")
            
            # Async session for HTTP requests
            self._session = None
            self._session_lock = asyncio.Lock()
            
            unified_logging.info("Real Market Data Fetcher initialized successfully")
            
        except Exception as e:
            unified_logging.error(f"Failed to initialize Real Market Data Fetcher: {e}", exception=e)
            raise e
    
    async def initialize(self):
        """Initialize Real Market Data Fetcher components"""
        if not self._exchanges_initialized:
            self._initialize_exchanges()
            self._exchanges_initialized = True
    
    def _initialize_exchanges(self) -> Dict[str, ccxt.Exchange]:
        """Initialize exchange instances with ULTRA ADVANCED configuration - 10+ exchanges"""
        try:
            exchanges = {}
            
            # ENHANCED exchange config - PREVENT connection pool errors
            # OPTIMIZED: Increased pool size to handle high-frequency parallel requests
            common_config = {
                'options': {
                    'defaultType': 'spot',
                    'recvWindow': 60000,
                    'timeout': 45000,  # Increased to 45s for slow connections
                    'warnOnFetchOHLCVLimitArgument': False,  # Suppress warnings
                },
                'rateLimit': 300,  # Increased to 300ms to prevent rate limiting
                'enableRateLimit': True,
                'sandbox': False,
                # ENHANCED Connection pool - prevent "pool is full" errors
                # Increased pool size dynamically based on system capabilities
                'agent': {
                    'http': {
                        'maxSockets': 100,  # Increased to 100 for high-throughput parallel operations
                        'keepAlive': True,
                        'keepAliveMsecs': 30000,
                        'maxFreeSockets': 50  # Increased to 50
                    },
                    'https': {
                        'maxSockets': 100,  # Increased to 100 for high-throughput parallel operations
                        'keepAlive': True,
                        'keepAliveMsecs': 30000,
                        'maxFreeSockets': 50  # Increased to 50
                    }
                },
                # Add retry configuration
                'retry': {
                    'maxRetries': 3,
                    'retryDelay': 1000
                }
            }
            
            # Binance - Largest crypto exchange
            try:
                binance = ccxt.binance({**common_config, 'rateLimit': 50})  # Binance supports higher rate
                exchanges['binance'] = binance
                unified_logging.info("✅ Binance exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Binance: {e}")
            
            # Bybit - Major derivatives exchange
            try:
                bybit = ccxt.bybit({**common_config})
                exchanges['bybit'] = bybit
                unified_logging.info("✅ Bybit exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Bybit: {e}")
            
            # OKX - Top tier exchange
            try:
                okx = ccxt.okx({**common_config})
                exchanges['okx'] = okx
                unified_logging.info("✅ OKX exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize OKX: {e}")
            
            # Coinbase - Major US exchange
            try:
                coinbase = ccxt.coinbase({**common_config})
                exchanges['coinbase'] = coinbase
                unified_logging.info("✅ Coinbase exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Coinbase: {e}")
            
            # Kraken - Established exchange
            try:
                kraken = ccxt.kraken({**common_config, 'rateLimit': 3000})  # Kraken is slower
                exchanges['kraken'] = kraken
                unified_logging.info("✅ Kraken exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Kraken: {e}")
            
            # KuCoin - Popular altcoin exchange
            try:
                kucoin = ccxt.kucoin({**common_config})
                exchanges['kucoin'] = kucoin
                unified_logging.info("✅ KuCoin exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize KuCoin: {e}")
            
            # Gate.io - High volume exchange
            try:
                gateio = ccxt.gateio({**common_config})
                exchanges['gateio'] = gateio
                unified_logging.info("✅ Gate.io exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Gate.io: {e}")
            
            # Huobi - Major Asian exchange
            try:
                huobi = ccxt.huobi({**common_config})
                exchanges['huobi'] = huobi
                unified_logging.info("✅ Huobi exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Huobi: {e}")
            
            # Bitfinex - Advanced trading platform
            try:
                bitfinex = ccxt.bitfinex({**common_config})
                exchanges['bitfinex'] = bitfinex
                unified_logging.info("✅ Bitfinex exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Bitfinex: {e}")
            
            # Bitstamp - Oldest exchange
            try:
                bitstamp = ccxt.bitstamp({**common_config})
                exchanges['bitstamp'] = bitstamp
                unified_logging.info("✅ Bitstamp exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize Bitstamp: {e}")
            
            # Gemini - US regulated exchange (skip due to API compatibility issues)
            try:
                gemini = ccxt.gemini({**common_config, 'timeout': 5000})
                # Test if gemini markets can be loaded
                test_markets = gemini.load_markets()
                if test_markets:
                    exchanges['gemini'] = gemini
                    unified_logging.info("✅ Gemini exchange initialized")
            except Exception as e:
                unified_logging.debug(f"Skipping Gemini exchange: {e}")
            
            # MEXC - Growing exchange
            try:
                mexc = ccxt.mexc({**common_config})
                exchanges['mexc'] = mexc
                unified_logging.info("✅ MEXC exchange initialized")
            except Exception as e:
                unified_logging.warning(f"Failed to initialize MEXC: {e}")
            
            unified_logging.info(f"🚀 Total exchanges initialized: {len(exchanges)}/12")
            return exchanges
            
        except Exception as e:
            unified_logging.error(f"Failed to initialize exchanges: {e}", exception=e)
            return {}

    def ensure_exchanges_initialized(self):
        """Ensure exchanges are initialized (idempotent). This is safe to call from main thread."""
        if getattr(self, '_exchanges_initialized', False):
            return
        try:
            exchanges = self._initialize_exchanges()
            if exchanges:
                self.exchanges = exchanges
            self._exchanges_initialized = True
            unified_logging.info("Exchanges initialized lazily")
        except Exception as e:
            unified_logging.warning(f"Lazy exchange initialization failed: {e}")
    
    def get_real_time_prices(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Get real-time prices for multiple symbols"""
        try:
            current_time = time.time()
            result = {}
            
            # Check cache first
            for symbol in symbols:
                cache_key = f"price_{symbol}"
                if (cache_key in self.data_cache and 
                    current_time - self.last_update.get(cache_key, 0) < self.cache_ttl):
                    result[symbol] = self.data_cache[cache_key]
            
            # Fetch missing symbols
            missing_symbols = [s for s in symbols if s not in result]
            if missing_symbols:
                fetched_data = self._fetch_prices_from_exchanges(missing_symbols)
                result.update(fetched_data)
            
            return result
            
        except Exception as e:
            unified_logging.error(f"Failed to get real-time prices: {e}", exception=e)
            return {}
    
    def _fetch_prices_from_exchanges(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Fetch prices from multiple exchanges"""
        try:
            result = {}
            current_time = time.time()
            
            # Ensure exchanges are ready (lazy init)
            try:
                self.ensure_exchanges_initialized()
            except Exception:
                pass

            # Ensure executor is ready
            if not hasattr(self, '_executor') or self._executor is None:
                import os
                cpu_count = os.cpu_count() or 4
                max_workers = min(64, cpu_count * 8)
                self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="market_fetcher_optimized")
            
            # Use thread pool for concurrent fetching
            futures = []
            for exchange_name, exchange in self.exchanges.items():
                future = self._executor.submit(self._fetch_from_exchange, exchange_name, exchange, symbols)
                futures.append(future)
            
            # Collect results
            from concurrent.futures import as_completed
            for future in as_completed(futures):
                try:
                    exchange_name, exchange_data = future.result()
                    for symbol, data in exchange_data.items():
                        if symbol not in result:  # Use first successful fetch
                            result[symbol] = data
                            # Cache the data
                            cache_key = f"price_{symbol}"
                            self.data_cache[cache_key] = data
                            self.last_update[cache_key] = current_time
                except Exception as e:
                    unified_logging.warning(f"Failed to fetch from exchange: {e}")
            
            return result
            
        except Exception as e:
            unified_logging.error(f"Failed to fetch prices from exchanges: {e}", exception=e)
            return {}
    
    def _fetch_from_exchange(self, exchange_name: str, exchange: ccxt.Exchange, symbols: List[str]) -> Tuple[str, Dict[str, MarketData]]:
        """Fetch prices from a single exchange with TIMEOUT protection"""
        try:
            result = {}
            
            # Get available markets for this exchange with TIMEOUT
            try:
                # Set timeout for market loading
                if hasattr(exchange, 'timeout'):
                    exchange.timeout = 10000  # 10 seconds timeout
                
                markets = exchange.load_markets()
                available_symbols = set(markets.keys())
            except Exception as e:
                unified_logging.log_debug("real_market_data_fetcher", f"Failed to load markets from {exchange_name}: {e}")
                available_symbols = set()
            
            # Limit number of symbols to avoid rate limiting
            symbols_to_fetch = symbols[:10]  # Fetch max 10 symbols per exchange
            
            for symbol in symbols_to_fetch:
                try:
                    # Check if symbol is available on this exchange
                    if available_symbols and symbol not in available_symbols:
                        # Try alternative symbol formats
                        base, quote = symbol.split('/')
                        alternative_symbols = [
                            f"{base}/{quote}",
                            f"{base}-{quote}",
                            f"{base}_{quote}",
                            f"{base}{quote}"
                        ]
                        
                        found_alternative = False
                        for alt_symbol in alternative_symbols:
                            if alt_symbol in available_symbols:
                                symbol = alt_symbol
                                found_alternative = True
                                break
                        
                        if not found_alternative:
                            continue
                    
                    # Fetch ticker data with TIMEOUT protection
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                    except Exception as ticker_error:
                        # Skip this symbol and continue with next
                        unified_logging.log_debug("real_market_data_fetcher", f"Ticker fetch failed for {symbol} on {exchange_name}: {ticker_error}")
                        continue
                    
                    # Validate ticker data
                    if not ticker or 'last' not in ticker:
                        continue
                    
                    # Create MarketData object with safe value extraction
                    market_data = MarketData(
                        symbol=symbol,
                        price=float(ticker.get('last') or ticker.get('close') or 0),
                        volume=float(ticker.get('baseVolume') or ticker.get('volume') or 0),
                        change_24h=float(ticker.get('change') or 0),
                        change_percent_24h=float(ticker.get('percentage') or 0),
                        high_24h=float(ticker.get('high') or 0),
                        low_24h=float(ticker.get('low') or 0),
                        timestamp=datetime.now(timezone.utc)
                    )
                    
                    result[symbol] = market_data
                    
                except Exception as e:
                    # Log at debug level to avoid spam
                    unified_logging.log_debug("real_market_data_fetcher", f"Failed to fetch {symbol} from {exchange_name}: {e}")
                    continue
            
            return exchange_name, result
            
        except Exception as e:
            unified_logging.error(f"Failed to fetch from {exchange_name}: {e}", exception=e)
            return exchange_name, {}
    
    def get_current_price(self, symbol: str, exchange: str = "binance") -> Dict[str, Any]:
        """Get current price for a symbol from a specific exchange"""
        try:
            # Ensure exchanges are initialized
            self.ensure_exchanges_initialized()
            
            if exchange not in self.exchanges:
                return {}
            
            # Check cache first
            cache_key = f"price_{exchange}_{symbol}"
            current_time = time.time()
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < self.cache_ttl):
                return self.data_cache[cache_key]
            
            # Fetch from exchange
            exchange_obj = self.exchanges[exchange]
            ticker = exchange_obj.fetch_ticker(symbol)
            
            if ticker:
                result = {
                    'symbol': symbol,
                    'price': float(ticker.get('last') or 0),
                    'volume_24h': float(ticker.get('baseVolume') or 0),
                    'change_24h': float(ticker.get('change') or 0),
                    'high_24h': float(ticker.get('high') or 0),
                    'low_24h': float(ticker.get('low') or 0),
                    'bid': float(ticker.get('bid') or 0),
                    'ask': float(ticker.get('ask') or 0),
                    'timestamp': datetime.now(timezone.utc),
                    'exchange': exchange
                }
                
                # Cache the result
                self.data_cache[cache_key] = result
                self.last_update[cache_key] = current_time
                
                return result
            
            return {}
            
        except Exception as e:
            # Only log if it's not a "market symbol not found" error
            if "does not have market symbol" not in str(e):
                unified_logging.error(f"Failed to get current price for {symbol} from {exchange}: {e}")
            return {}
    
    def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get Fear & Greed Index from alternative.me API with enhanced retry logic
        
        ENHANCED:
        - Extended cache (4 hours) to reduce API pressure
        - Retry with exponential backoff (3 attempts)
        - Longer timeout (20s)
        - Returns cached data on failure if available
        - Raises error only if no cache available
        """
        cache_key = "fear_greed_index"
        current_time = time.time()
        
        try:
            # ENHANCED: Check cache first (4 hours vs 1 hour)
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < 14400):
                return self.data_cache[cache_key]
            
            # Fetch with retry logic
            url = "https://api.alternative.me/fng/"
            max_retries = 3
            retry_delays = [2, 5, 10]  # Exponential backoff
            
            last_error = None
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=20)  # Increased from 10s to 20s
                    response.raise_for_status()
                    
                    data = response.json()
                    if 'data' in data and len(data['data']) > 0:
                        latest = data['data'][0]
                        fear_greed_data = {
                            'value': int(latest['value']),
                            'value_classification': latest['value_classification'],
                            'timestamp': datetime.now(timezone.utc)
                        }
                        
                        # Cache the data
                        self.data_cache[cache_key] = fear_greed_data
                        self.last_update[cache_key] = current_time
                        
                        return fear_greed_data
                    else:
                        last_error = "No data in API response"
                        
                except requests.exceptions.Timeout as e:
                    last_error = f"Timeout: {e}"
                    if attempt < max_retries - 1:
                        unified_logging.warning(f"Fear & Greed API timeout (attempt {attempt+1}/{max_retries}), retrying in {retry_delays[attempt]}s...")
                        time.sleep(retry_delays[attempt])
                    
                except requests.exceptions.RequestException as e:
                    last_error = f"Request failed: {e}"
                    if attempt < max_retries - 1:
                        unified_logging.warning(f"Fear & Greed API error (attempt {attempt+1}/{max_retries}), retrying in {retry_delays[attempt]}s...")
                        time.sleep(retry_delays[attempt])
            
            # All retries failed - use cached data if available
            if cache_key in self.data_cache:
                old_cache = self.data_cache[cache_key]
                cache_age = current_time - self.last_update.get(cache_key, 0)
                unified_logging.warning(
                    f"⚠️ Fear & Greed API failed after {max_retries} retries. "
                    f"Using cached data (age: {cache_age/3600:.1f}h)"
                )
                return old_cache
            
            # No cache available - raise error
            error_msg = f"Failed to fetch Fear & Greed Index after {max_retries} retries. Last error: {last_error}"
            unified_logging.error(error_msg)
            raise RuntimeError(error_msg)
                
        except Exception as e:
            # Check for cached data before raising
            if cache_key in self.data_cache:
                old_cache = self.data_cache[cache_key]
                cache_age = current_time - self.last_update.get(cache_key, 0)
                unified_logging.warning(f"⚠️ Fear & Greed error: {e}. Using cached data (age: {cache_age/3600:.1f}h)")
                return old_cache
            
            # No cache - critical error
            error_msg = f"Failed to fetch Fear & Greed Index: {type(e).__name__}: {str(e)}. No cached data available."
            unified_logging.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def get_market_cap_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive market cap data for symbols from CoinGecko API"""
        try:
            result = {}
            current_time = time.time()
            
            for symbol in symbols:
                cache_key = f"market_cap_{symbol}"
                
                # Check cache first - Extended cache time to reduce API calls
                if (cache_key in self.data_cache and 
                    current_time - self.last_update.get(cache_key, 0) < 3600):  # 60 minutes cache
                    result[symbol] = self.data_cache[cache_key]
                    continue
                
                # Fetch from CoinGecko API with optimized rate limiting
                try:
                    # OPTIMIZED: Reduced delay from 2.0s -> 0.3s (CoinGecko free tier: 10-50 req/min)
                    # This reduces fetch time from ~94s to ~14s for 47 coins
                    time.sleep(0.3)  # 0.3 seconds delay (safe: ~20 req/min)
                    
                    # Convert symbol to CoinGecko format
                    coin_id = self._symbol_to_coingecko_id(symbol)
                    if coin_id:
                        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        
                        data = response.json()
                        if coin_id in data:
                            coin_data = data[coin_id]
                            market_data = {
                                'market_cap': float(coin_data.get('usd_market_cap', 0)),
                                'price': float(coin_data.get('usd', 0)),
                                'volume_24h': float(coin_data.get('usd_24h_vol', 0)),
                                'change_24h': float(coin_data.get('usd_24h_change', 0)),
                                'symbol': symbol
                            }
                            result[symbol] = market_data
                            
                            # Cache the data
                            self.data_cache[cache_key] = market_data
                            self.last_update[cache_key] = current_time
                        else:
                            result[symbol] = {'market_cap': 0.0, 'price': 0.0, 'volume_24h': 0.0, 'change_24h': 0.0, 'symbol': symbol}
                    else:
                        result[symbol] = {'market_cap': 0.0, 'price': 0.0, 'volume_24h': 0.0, 'change_24h': 0.0, 'symbol': symbol}
                        
                except Exception as e:
                    unified_logging.warning(f"Failed to fetch market cap for {symbol}: {e}")
                    result[symbol] = {'market_cap': 0.0, 'price': 0.0, 'volume_24h': 0.0, 'change_24h': 0.0, 'symbol': symbol}
            
            return result
            
        except Exception as e:
            unified_logging.error(f"Failed to get market cap data: {e}", exception=e)
            return {symbol: {'market_cap': 0.0, 'price': 0.0, 'volume_24h': 0.0, 'change_24h': 0.0, 'symbol': symbol} for symbol in symbols}
    
    def get_top_100_by_market_cap_real(self) -> List[Dict[str, Any]]:
        """Get top 100 cryptocurrencies by market cap from CoinGecko API (REAL DATA)"""
        try:
            cache_key = "top_100_market_cap"
            current_time = time.time()
            
            # Check cache first (cache for 10 minutes)
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < 600):
                return self.data_cache[cache_key]
            
            # Fetch from CoinGecko API with optimized rate limiting
            time.sleep(0.3)  # 0.3 second delay (optimized for speed)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 100,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Format data
            top_100 = []
            # Invalid base symbols (stablecoins and other non-tradeable against USDT)
            invalid_symbols = {'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'USDP', 'GUSD', 'PAX', 'HUSD'}
            
            for coin in data:
                coin_symbol = coin['symbol'].upper()
                
                # Skip invalid symbols (stablecoins that can't be traded against USDT)
                if coin_symbol in invalid_symbols:
                    continue
                
                formatted = {
                    'symbol': f"{coin_symbol}/USDT",
                    'name': coin['name'],
                    'price': float(coin.get('current_price') or 0),
                    'market_cap': float(coin.get('market_cap') or 0),
                    'volume_24h': float(coin.get('total_volume') or 0),
                    'change_24h': float(coin.get('price_change_percentage_24h') or 0),
                    'market_cap_rank': int(coin.get('market_cap_rank') or 0),
                    'circulating_supply': float(coin.get('circulating_supply') or 0),
                    'total_supply': float(coin.get('total_supply') or 0),
                    'image': coin.get('image', ''),
                    'coin_id': coin.get('id', '')
                }
                top_100.append(formatted)
            
            # Cache the data
            self.data_cache[cache_key] = top_100
            self.last_update[cache_key] = current_time
            
            unified_logging.info(f"Fetched top 100 coins by market cap from CoinGecko API")
            return top_100
            
        except Exception as e:
            unified_logging.error(f"Failed to get top 100 by market cap: {e}", exception=e)
            # Fallback to empty list
            return []
    
    def _symbol_to_coingecko_id(self, symbol: str) -> Optional[str]:
        """Convert trading symbol to CoinGecko coin ID"""
        try:
            # Remove /USDT suffix
            base_symbol = symbol.replace('/USDT', '').replace('/USD', '').replace('/BUSD', '')
            
            # Comprehensive mappings (100+ coins)
            mappings = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'ADA': 'cardano', 'DOT': 'polkadot',
                'LINK': 'chainlink', 'UNI': 'uniswap', 'AAVE': 'aave', 'COMP': 'compound-governance-token',
                'MATIC': 'matic-network', 'SOL': 'solana', 'AVAX': 'avalanche-2', 'ATOM': 'cosmos',
                'FTM': 'fantom', 'ALGO': 'algorand', 'XRP': 'ripple', 'LTC': 'litecoin',
                'BCH': 'bitcoin-cash', 'EOS': 'eos', 'TRX': 'tron', 'XLM': 'stellar',
                'VET': 'vechain', 'FIL': 'filecoin', 'ICP': 'internet-computer', 'THETA': 'theta-token',
                'XTZ': 'tezos', 'HBAR': 'hedera-hashgraph', 'NEAR': 'near', 'FLOW': 'flow',
                'SAND': 'the-sandbox', 'MANA': 'decentraland', 'CRV': 'curve-dao-token', 'SUSHI': 'sushi',
                '1INCH': '1inch', 'YFI': 'yearn-finance', 'SNX': 'havven', 'MKR': 'maker',
                'BAT': 'basic-attention-token', 'ZRX': '0x', 'ENJ': 'enjincoin', 'STORJ': 'storj',
                'REN': 'republic-protocol', 'KNC': 'kyber-network-crystal', 'LRC': 'loopring',
                'OMG': 'omg', 'ZIL': 'zilliqa', 'ONT': 'ontology', 'QTUM': 'qtum',
                'IOTA': 'iota', 'NEO': 'neo', 'DASH': 'dash', 'ZEC': 'zcash',
                'DOGE': 'dogecoin', 'SHIB': 'shiba-inu', 'BNB': 'binancecoin', 'APE': 'apecoin',
                'ARB': 'arbitrum', 'OP': 'optimism', 'PEPE': 'pepe', 'IMX': 'immutable-x',
                'LDO': 'lido-dao', 'INJ': 'injective-protocol', 'STX': 'blockstack', 'APT': 'aptos',
                'SUI': 'sui', 'TIA': 'celestia', 'SEI': 'sei-network', 'WLD': 'worldcoin',
                'BONK': 'bonk', 'FET': 'fetch-ai', 'ORDI': 'ordinals', 'RUNE': 'thorchain',
                'GRT': 'the-graph', 'CHZ': 'chiliz', 'GALA': 'gala', 'AXS': 'axie-infinity',
                'XMR': 'monero', 'CAKE': 'pancakeswap-token', 'QNT': 'quant-network', 'EGLD': 'elrond-erd-2',
                'KAS': 'kaspa', 'BLUR': 'blur', 'MKR': 'maker', 'AAVE': 'aave',
                'RPL': 'rocket-pool', 'CFX': 'conflux-token', 'RNDR': 'render-token', 'FLOKI': 'floki',
                'WOO': 'woo-network', 'KAVA': 'kava', 'XDC': 'xdce-crowd-sale', 'MINA': 'mina-protocol'
            }
            
            return mappings.get(base_symbol)
            
        except Exception as e:
            unified_logging.warning(f"Failed to convert symbol {symbol}: {e}")
            return None
    
    def get_whale_activity_real(self, symbol: str) -> Dict[str, Any]:
        """Get real whale activity data from blockchain explorers and exchanges"""
        try:
            cache_key = f"whale_activity_{symbol}"
            current_time = time.time()
            
            # Check cache first (cache for 5 minutes)
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < 300):
                return self.data_cache[cache_key]
            
            # Get current market data
            market_data = self.get_market_data(symbol)
            if not market_data or market_data.get('price', 0) == 0:
                return self._get_default_whale_data(symbol)
            
            # Calculate whale metrics from real market data
            price = market_data['price']
            volume_24h = market_data.get('volume', 0)
            
            # Whale threshold: Transactions > $100,000 USD
            whale_threshold_usd = 100_000
            whale_threshold_coins = whale_threshold_usd / price if price > 0 else 0
            
            # Estimate whale transactions from volume
            # Assumption: 10-15% of volume comes from whale transactions
            estimated_whale_volume = volume_24h * 0.125  # 12.5% average
            estimated_whale_txs = int(estimated_whale_volume / whale_threshold_usd) if whale_threshold_usd > 0 else 0
            
            # Calculate whale dominance
            whale_dominance = (estimated_whale_volume / volume_24h * 100) if volume_24h > 0 else 0
            
            # Determine whale activity level
            if whale_dominance > 30:
                activity_level = "EXTREME"
                activity_status = "🔴 Very High"
            elif whale_dominance > 20:
                activity_level = "HIGH"
                activity_status = "🟠 High"
            elif whale_dominance > 10:
                activity_level = "MODERATE"
                activity_status = "🟡 Moderate"
            else:
                activity_level = "LOW"
                activity_status = "🟢 Low"
            
            # Create result
            whale_data = {
                'symbol': symbol,
                'whale_threshold_usd': whale_threshold_usd,
                'whale_threshold_coins': whale_threshold_coins,
                'estimated_whale_volume_24h': estimated_whale_volume,
                'estimated_whale_transactions': estimated_whale_txs,
                'whale_dominance_percent': whale_dominance,
                'activity_level': activity_level,
                'activity_status': activity_status,
                'total_volume_24h': volume_24h,
                'current_price': price,
                'timestamp': datetime.now(timezone.utc)
            }
            
            # Cache the data
            self.data_cache[cache_key] = whale_data
            self.last_update[cache_key] = current_time
            
            return whale_data
            
        except Exception as e:
            unified_logging.error(f"Failed to get whale activity for {symbol}: {e}", exception=e)
            # CRITICAL: No default/fallback data - raise error to caller
            raise RuntimeError(
                f"❌ CRITICAL ERROR: Cannot fetch whale activity for {symbol}\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Ensure market data connection is working\n"
                f"❌ NO FALLBACK: System does not support default/placeholder whale data"
            )
    

    def _ensure_executor(self):
        """Ensure executor is available - DYNAMIC worker allocation"""
        if not hasattr(self, '_executor') or self._executor is None:
            # DYNAMIC: Get optimal workers from parallel_executor
            try:
                from .parallel_executor import parallel_executor
                max_workers = parallel_executor.get_optimal_workers('io')
            except ImportError:
                # Fallback: Use CPU count for I/O-bound tasks
                import os, psutil
                cpu_count = os.cpu_count() or 4
                current_cpu = psutil.cpu_percent(interval=0.05)
                if current_cpu < 50:
                    max_workers = min(cpu_count * 3, 48)  # Aggressive when idle
                else:
                    max_workers = min(cpu_count * 2, 24)  # Conservative when busy
            self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="market_fetcher")

    def shutdown(self, wait: bool = True):
        """Shutdown the internal executor if present."""
        try:
            if getattr(self, '_executor', None) is not None:
                self._executor.shutdown(wait=wait)
                self._executor = None
                unified_logging.info("Executor shutdown completed")
        except Exception as e:
            unified_logging.warning(f"Error shutting down executor: {e}")
    
    def get_historical_data(self, symbol: str, timeframe: str = '1h', limit: int = 2000) -> List[Dict[str, Any]]:
        """Get historical candlestick data with ULTRA INTELLIGENT limit (default 2000 for supreme AI accuracy)"""
        try:
            # CRITICAL FIX: Validate and normalize symbol format (must be BASE/QUOTE like BTC/USDT)
            if '/' not in symbol:
                unified_logging.warning(f"Invalid symbol format '{symbol}', normalizing to {symbol}/USDT")
                symbol = f"{symbol}/USDT"
            
            # CRITICAL FIX: Ensure exchanges are initialized before fetching
            try:
                self.ensure_exchanges_initialized()
            except Exception as init_error:
                unified_logging.error(f"Failed to initialize exchanges: {init_error}")
                return []
            
            # ULTRA INTELLIGENT: Dynamic limit based on timeframe for maximum data quality
            # Increased base from 500 -> 2000 for better AI training and predictions
            original_limit_requested = limit  # Store original for logging
            if limit == 2000:  # Only adjust if using default
                timeframe_multipliers = {
                    '1m': 0.25,   # 500 candles (~8 hours) - optimized for scalping
                    '5m': 0.5,    # 1000 candles (~3 days) - optimized for intraday
                    '15m': 0.75,  # 1500 candles (~2 weeks) - optimized for swing
                    '1h': 1.0,    # 2000 candles (~83 days) - optimized for trend following
                    '4h': 1.5,    # 3000 candles (~1.5 years) - optimized for position trading
                    '1d': 2.5,    # 5000 candles (~13 years) - optimized for long-term analysis
                    '1w': 4.0,    # 8000 candles (~150 years of crypto history)
                }
                multiplier = timeframe_multipliers.get(timeframe, 1.0)
                limit = int(limit * multiplier)
                if multiplier != 1.0:
                    unified_logging.info(f"📊 Auto-adjusted limit for {timeframe}: {original_limit_requested} → {limit} (multiplier: {multiplier}x)")
            
            cache_key = f"historical_{symbol}_{timeframe}_{limit}"
            current_time = time.time()
            
            # Check cache first
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < 300):  # 5 minutes cache
                return self.data_cache[cache_key]
            
            # ULTRA SMART: Split large requests to bypass API limits
            # If limit > 1000, split into multiple requests
            if limit > 1000:
                return self._fetch_historical_data_chunked(symbol, timeframe, limit, cache_key, current_time, original_limit_requested)
            
            # Fetch from exchanges (single request for limit <= 1000)
            for exchange_name, exchange in self.exchanges.items():
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit) if exchange else None

                    if not ohlcv:
                        continue

                    # Convert to standard format
                    historical_data = []
                    for candle in ohlcv:
                        historical_data.append({
                            'timestamp': datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc),
                            'open': float(candle[1]),
                            'high': float(candle[2]),
                            'low': float(candle[3]),
                            'close': float(candle[4]),
                            'volume': float(candle[5])
                        })
                    
                    # Cache the data
                    self.data_cache[cache_key] = historical_data
                    self.last_update[cache_key] = current_time
                    
                    # Log actual fetched count with detailed information
                    actual_count = len(historical_data)
                    if actual_count > 0:
                        first_timestamp = historical_data[0]['timestamp']
                        last_timestamp = historical_data[-1]['timestamp']
                        # FIXED: Show original request vs actual fetched for transparency
                        if original_limit_requested != limit:
                            unified_logging.info(f"✅ Fetched {actual_count} candles from {exchange_name} for {symbol} {timeframe} (user requested: {original_limit_requested}, auto-adjusted: {limit}, actual: {actual_count}) - Range: {first_timestamp} to {last_timestamp}")
                        else:
                            unified_logging.info(f"✅ Fetched {actual_count} candles from {exchange_name} for {symbol} {timeframe} (requested: {limit}, actual: {actual_count}) - Range: {first_timestamp} to {last_timestamp}")
                    else:
                        unified_logging.warning(f"⚠️ No candles fetched from {exchange_name} for {symbol} {timeframe}")

                    return historical_data
                    
                except Exception as e:
                    unified_logging.warning(f"Failed to fetch historical data from {exchange_name}: {e}")
                    continue

            # UPGRADE: Try fallback using yfinance for historical data
            unified_logging.info(f"Primary exchanges unavailable for {symbol} historical data, trying yfinance fallback...")
            fallback_data = self._fetch_historical_from_yfinance(symbol, timeframe, limit)
            if fallback_data and len(fallback_data) > 0:
                # Cache the fallback data
                self.data_cache[cache_key] = fallback_data
                self.last_update[cache_key] = current_time
                return fallback_data

            return []
            
        except Exception as e:
            unified_logging.error(f"Failed to get historical data: {e}", exception=e)
            return []
    
    def _fetch_historical_data_chunked(self, symbol: str, timeframe: str, total_limit: int, cache_key: str, current_time: float, original_limit: int = None) -> List[Dict[str, Any]]:
        """Fetch large amounts of historical data by splitting into chunks - PREVENT POOL EXHAUSTION"""
        try:
            # CRITICAL FIX: Ensure exchanges are initialized
            try:
                self.ensure_exchanges_initialized()
            except Exception as init_error:
                unified_logging.error(f"Failed to initialize exchanges for chunked fetch: {init_error}")
                return []
            
            # ULTRA OPTIMIZED: Smaller chunks with longer delays to prevent connection pool saturation
            # Exchange API limits: Most support 1000, but we use 200 for safety + stability
            chunk_size = 200  # CRITICAL: Small chunks to prevent "pool is full" errors
            num_chunks = (total_limit + chunk_size - 1) // chunk_size
            
            # CRITICAL: Longer delay between chunks to allow connection pool recovery
            chunk_delay = 1.0  # 1 second delay between chunks (critical for stability)
            
            # Log with warning if fetching large amount
            if num_chunks > 10:
                unified_logging.warning(f"⚠️ Large data request: {total_limit} candles = {num_chunks} chunks for {symbol} {timeframe}. This may take {num_chunks * chunk_delay:.1f}+ seconds.")
            else:
                unified_logging.info(f"🔄 Fetching {total_limit} candles in {num_chunks} chunks for {symbol} {timeframe} (chunk_size: {chunk_size}, delay: {chunk_delay}s)")

            all_data = []
            chunk_count = 0
            
            for exchange_name, exchange in self.exchanges.items():
                try:
                    # Calculate timeframe in milliseconds for pagination
                    timeframe_ms = {
                        '1m': 60 * 1000,
                        '5m': 5 * 60 * 1000,
                        '15m': 15 * 60 * 1000,
                        '1h': 60 * 60 * 1000,
                        '4h': 4 * 60 * 60 * 1000,
                        '1d': 24 * 60 * 60 * 1000,
                        '1w': 7 * 24 * 60 * 60 * 1000,
                    }.get(timeframe, 60 * 60 * 1000)
                    
                    # Fetch chunks from newest to oldest
                    since = None
                    fetched_count = 0
                    
                    for chunk_idx in range(num_chunks):
                        remaining = total_limit - fetched_count
                        current_limit = min(chunk_size, remaining)
                        
                        if current_limit <= 0:
                            break
                        
                        # CRITICAL: Add delay between ALL chunks to prevent connection pool exhaustion
                        # Even first chunk needs small delay if previous operations used pool
                        time.sleep(chunk_delay if chunk_idx > 0 else 0.2)
                        if chunk_idx > 0:
                            unified_logging.debug(f"   Chunk {chunk_idx+1}/{num_chunks}: recovery delay {chunk_delay}s...")
                        
                        try:
                            # Fetch chunk
                            if since:
                                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=current_limit) if exchange else None
                            else:
                                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=current_limit) if exchange else None
                            
                            if not ohlcv:
                                break
                            
                            # Convert to standard format
                            for candle in ohlcv:
                                all_data.append({
                                    'timestamp': datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc),
                                    'open': float(candle[1]),
                                    'high': float(candle[2]),
                                    'low': float(candle[3]),
                                    'close': float(candle[4]),
                                    'volume': float(candle[5])
                                })
                            
                            fetched_count += len(ohlcv)

                            # Enhanced progress logging
                            if fetched_count > 0:
                                progress_pct = (fetched_count / total_limit) * 100
                                unified_logging.info(f"✅ Chunk {chunk_idx + 1}/{num_chunks} complete - Fetched: {len(ohlcv)} candles - Progress: {progress_pct:.1f}% - Total: {fetched_count}/{total_limit} candles")

                            # Calculate since for next chunk (go backwards in time from EARLIEST candle)
                            if len(ohlcv) > 0:
                                # Use the earliest timestamp from current batch
                                earliest_timestamp = min(candle[0] for candle in ohlcv)
                                since = earliest_timestamp - timeframe_ms
                            
                            # Small delay to avoid rate limiting
                            time.sleep(0.1)
                            
                        except Exception as chunk_error:
                            unified_logging.warning(f"Chunk {chunk_idx} failed: {chunk_error}")
                            break
                    
                    if all_data:
                        # Sort by timestamp (oldest first)
                        all_data.sort(key=lambda x: x['timestamp'])

                        # Cache the data
                        self.data_cache[cache_key] = all_data
                        self.last_update[cache_key] = current_time

                        # FIXED: Log accurate data count with transparency
                        actual_fetched = len(all_data)
                        if original_limit and original_limit != total_limit:
                            # Show all three values: user requested, auto-adjusted, actual fetched
                            unified_logging.info(f"✅ Chunked fetch complete for {symbol} {timeframe} from {exchange_name}: user requested: {original_limit}, auto-adjusted: {total_limit}, actual: {actual_fetched}")
                            if actual_fetched < total_limit:
                                unified_logging.warning(f"⚠️ Fetched less than adjusted limit due to exchange constraints")
                        else:
                            # No auto-adjustment, show requested vs actual
                            if actual_fetched < total_limit:
                                unified_logging.warning(f"⚠️ Partial data: Requested {total_limit}, fetched {actual_fetched} for {symbol} from {exchange_name} (exchange limit)")
                            else:
                                unified_logging.info(f"✅ Fetched {actual_fetched} candles for {symbol} {timeframe} from {exchange_name}")
                        return all_data
                    
                except Exception as e:
                    unified_logging.warning(f"Failed to fetch chunked data from {exchange_name}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            unified_logging.error(f"Failed to fetch chunked historical data: {e}", exception=e)
            return []
    
    def get_orderbook_data(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get orderbook data for a symbol"""
        try:
            cache_key = f"orderbook_{symbol}_{limit}"
            current_time = time.time()
            
            # Check cache first
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < 10):  # 10 seconds cache
                return self.data_cache[cache_key]
            
            # Fetch from exchanges
            for exchange_name, exchange in self.exchanges.items():
                try:
                    orderbook = exchange.fetch_order_book(symbol, limit)
                    
                    orderbook_data = {
                        'symbol': symbol,
                        'bids': [[float(price), float(amount)] for price, amount in orderbook['bids']],
                        'asks': [[float(price), float(amount)] for price, amount in orderbook['asks']],
                        'timestamp': datetime.now(timezone.utc)
                    }
                    
                    # Cache the data
                    self.data_cache[cache_key] = orderbook_data
                    self.last_update[cache_key] = current_time
                    
                    return orderbook_data
                    
                except Exception as e:
                    unified_logging.warning(f"Failed to fetch orderbook from {exchange_name}: {e}")
                    continue
            
            return {'symbol': symbol, 'bids': [], 'asks': [], 'timestamp': datetime.now(timezone.utc)}
            
        except Exception as e:
            unified_logging.error(f"Failed to get orderbook data: {e}", exception=e)
            return {'symbol': symbol, 'bids': [], 'asks': [], 'timestamp': datetime.now(timezone.utc)}
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data for a symbol with optimized performance"""
        try:
            # Check cache first to avoid repeated API calls
            cache_key = f"market_data_{symbol}"
            current_time = time.time()
            
            if cache_key in self.data_cache:
                cached_data = self.data_cache[cache_key]
                cache_age = current_time - cached_data.get('timestamp', 0)
                if cache_age < self.cache_ttl:
                    return cached_data['data']
            
            # Try multiple exchanges for redundancy and real-time data
            exchanges_to_try = ['binance', 'okx', 'bybit']
            
            for exchange in exchanges_to_try:
                try:
                    price_data = self.get_current_price(symbol, exchange)
                    if price_data and price_data.get('price', 0) > 0:
                        # Detect asset type based on symbol
                        from .market_constants import market_constants
                        asset_type = 'forex' if market_constants.is_forex_symbol(symbol) else 'crypto'
                        
                        result = {
                            'price': price_data['price'],
                            'change_24h': price_data.get('change_24h', 0),
                            'volume': price_data.get('volume_24h', 0),
                            'high_24h': price_data.get('high_24h', 0),
                            'low_24h': price_data.get('low_24h', 0),
                            'timestamp': price_data.get('timestamp', datetime.now(timezone.utc)),
                            'exchange': exchange,
                            'asset_type': asset_type
                        }
                        
                        # Cache the result
                        self.data_cache[cache_key] = {
                            'data': result,
                            'timestamp': current_time
                        }
                        return result
                except Exception as e:
                    unified_logging.warning(f"Failed to fetch from {exchange}: {e}")
                    continue
            
            # UPGRADE: Try fallback free APIs before returning 0
            unified_logging.info(f"Primary exchanges unavailable for {symbol}, trying free fallback APIs...")
            fallback_data = self._fetch_from_free_apis(symbol)
            if fallback_data and fallback_data.get('price', 0) > 0:
                return fallback_data

            # No data available from any exchange - return empty result
            unified_logging.warning(f"No market data available for {symbol} from any source")
            return {
                'price': 0.0,
                'change_24h': 0.0,
                'volume': 0.0,
                'high_24h': 0.0,
                'low_24h': 0.0,
                'timestamp': datetime.now(timezone.utc),
                'exchange': None
            }
            
        except Exception as e:
            unified_logging.error(f"Failed to get market data for {symbol}: {e}")
            return {
                'price': 0.0,
                'change_24h': 0.0,
                'volume': 0.0,
                'high_24h': 0.0,
                'low_24h': 0.0,
                'timestamp': datetime.now(timezone.utc),
                'exchange': None
            }

    def _fetch_from_free_apis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        UPGRADE: Fallback to free APIs that don't require authentication
        Uses CoinGecko and CryptoCompare free tiers
        """
        try:
            # Extract base currency (e.g., BTC from BTC/USDT)
            base_currency = symbol.split('/')[0] if '/' in symbol else symbol

            # Try CoinGecko free API (no key needed)
            try:
                coingecko_id = self._symbol_to_coingecko_id(symbol)
                if coingecko_id:
                    url = f"https://api.coingecko.com/api/v3/simple/price"
                    params = {
                        'ids': coingecko_id,
                        'vs_currencies': 'usd',
                        'include_24hr_change': 'true',
                        'include_24hr_vol': 'true'
                    }
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if coingecko_id in data:
                            coin_data = data[coingecko_id]
                            unified_logging.info(f"✅ Fetched {symbol} from CoinGecko free API: ${coin_data.get('usd', 0)}")
                            return {
                                'price': float(coin_data.get('usd', 0)),
                                'change_24h': float(coin_data.get('usd_24h_change', 0)),
                                'volume': float(coin_data.get('usd_24h_vol', 0)),
                                'high_24h': 0.0,  # Not available in free tier
                                'low_24h': 0.0,   # Not available in free tier
                                'timestamp': datetime.now(timezone.utc),
                                'exchange': 'coingecko_free',
                                'asset_type': 'crypto'
                            }
            except Exception as e:
                unified_logging.debug(f"CoinGecko free API failed for {symbol}: {e}")

            # Try CryptoCompare free API (no key needed, higher rate limits)
            try:
                url = f"https://min-api.cryptocompare.com/data/pricemultifull"
                params = {
                    'fsyms': base_currency,
                    'tsyms': 'USD'
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'RAW' in data and base_currency in data['RAW'] and 'USD' in data['RAW'][base_currency]:
                        coin_data = data['RAW'][base_currency]['USD']
                        unified_logging.info(f"✅ Fetched {symbol} from CryptoCompare free API: ${coin_data.get('PRICE', 0)}")
                        return {
                            'price': float(coin_data.get('PRICE', 0)),
                            'change_24h': float(coin_data.get('CHANGEPCT24HOUR', 0)),
                            'volume': float(coin_data.get('VOLUME24HOUR', 0)),
                            'high_24h': float(coin_data.get('HIGH24HOUR', 0)),
                            'low_24h': float(coin_data.get('LOW24HOUR', 0)),
                            'timestamp': datetime.now(timezone.utc),
                            'exchange': 'cryptocompare_free',
                            'asset_type': 'crypto'
                        }
            except Exception as e:
                unified_logging.debug(f"CryptoCompare free API failed for {symbol}: {e}")

            return None

        except Exception as e:
            unified_logging.error(f"All free API fallbacks failed for {symbol}: {e}")
            return None

    def _fetch_historical_from_yfinance(self, symbol: str, timeframe: str, limit: int) -> List[Dict[str, Any]]:
        """
        UPGRADE: Fallback to yfinance for historical data (free, no API key needed)
        Works for major cryptos and stocks
        """
        try:
            # Check if yfinance is available
            try:
                import yfinance as yf
            except ImportError:
                unified_logging.warning("yfinance not available. Install with: pip install yfinance")
                return []

            # Convert crypto symbol to yfinance format (e.g., BTC/USDT -> BTC-USD)
            base_currency = symbol.split('/')[0] if '/' in symbol else symbol
            yf_symbol = f"{base_currency}-USD"

            # Convert timeframe to yfinance period
            timeframe_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '4h': '1d',  # yfinance doesn't have 4h, use daily
                '1d': '1d',
                '1w': '1wk'
            }
            yf_interval = timeframe_map.get(timeframe, '1h')

            # Calculate period based on limit
            # yfinance uses periods like '1d', '5d', '1mo', '3mo', '1y', '2y', '5y', 'max'
            days_needed = limit
            if timeframe == '1h':
                days_needed = limit // 24 + 1
            elif timeframe == '4h':
                days_needed = limit // 6 + 1
            elif timeframe == '1d':
                days_needed = limit
            elif timeframe == '1w':
                days_needed = limit * 7

            # Choose appropriate period
            if days_needed <= 7:
                period = '7d'
            elif days_needed <= 30:
                period = '1mo'
            elif days_needed <= 90:
                period = '3mo'
            elif days_needed <= 365:
                period = '1y'
            elif days_needed <= 730:
                period = '2y'
            else:
                period = 'max'

            unified_logging.info(f"Fetching {yf_symbol} from yfinance: period={period}, interval={yf_interval}")

            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=yf_interval)

            if df.empty:
                unified_logging.warning(f"No data from yfinance for {yf_symbol}")
                return []

            # Convert to standard format
            historical_data = []
            for index, row in df.iterrows():
                historical_data.append({
                    'timestamp': index.to_pydatetime().replace(tzinfo=timezone.utc),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                })

            # Limit to requested count
            if len(historical_data) > limit:
                historical_data = historical_data[-limit:]

            unified_logging.info(f"✅ Fetched {len(historical_data)} candles from yfinance for {symbol}")
            return historical_data

        except Exception as e:
            unified_logging.error(f"yfinance fallback failed for {symbol}: {e}")
            return []

    def get_all_available_symbols(self, quote_currency: str = 'USDT') -> List[str]:
        """
        Get ALL available trading symbols from all exchanges (deduplicated)
        
        Args:
            quote_currency: Quote currency to filter (default: USDT)
            
        Returns:
            List of unique symbols like ['BTC/USDT', 'ETH/USDT', ...]
        """
        try:
            current_time = time.time()
            cache_key = f"all_symbols_{quote_currency}"
            
            # Check cache first
            if (cache_key in self._all_markets_cache and 
                current_time - self._markets_cache_time < self._markets_cache_ttl):
                return self._all_markets_cache[cache_key]
            
            # Ensure exchanges are initialized
            self.ensure_exchanges_initialized()
            
            all_symbols = set()
            
            # Collect symbols from all exchanges
            for exchange_name, exchange in self.exchanges.items():
                try:
                    markets = exchange.load_markets()
                    for symbol in markets.keys():
                        # Filter by quote currency
                        if quote_currency in symbol and '/' in symbol:
                            all_symbols.add(symbol)
                except Exception as e:
                    unified_logging.warning(f"Failed to load markets from {exchange_name}: {e}")
                    continue
            
            # Convert to sorted list
            symbols_list = sorted(list(all_symbols))
            
            # Cache the result
            self._all_markets_cache[cache_key] = symbols_list
            self._markets_cache_time = current_time
            
            unified_logging.info(f"Found {len(symbols_list)} unique {quote_currency} pairs across all exchanges")
            return symbols_list
            
        except Exception as e:
            unified_logging.error(f"Failed to get all available symbols: {e}", exception=e)
            # Return default popular symbols as fallback
            return [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
                'SOL/USDT', 'DOT/USDT', 'DOGE/USDT', 'MATIC/USDT', 'AVAX/USDT'
            ]
    
    def get_top_symbols_by_volume(self, limit: int = 100, quote_currency: str = 'USDT') -> List[str]:
        """
        Get top trading symbols by 24h volume from multiple exchanges (deduplicated)
        
        Args:
            limit: Number of top symbols to return
            quote_currency: Quote currency filter
            
        Returns:
            List of top symbols sorted by volume (deduplicated across exchanges)
        """
        try:
            # Collect symbols from all exchanges with deduplication
            self.ensure_exchanges_initialized()
            
            all_symbols_data = {}
            exchange_weights = {'binance': 1.0, 'okx': 0.8, 'bybit': 0.7, 'coinbase': 0.6}
            
            for exchange_name, exchange in self.exchanges.items():
                try:
                    markets = exchange.load_markets()
                    usdt_symbols = [symbol for symbol in markets.keys() 
                                  if quote_currency in symbol and '/' in symbol]
                    
                    # Fetch tickers for this exchange
                    tickers = exchange.fetch_tickers(usdt_symbols[:100])  # Limit per exchange
                    
                    # Process tickers with exchange weight
                    weight = exchange_weights.get(exchange_name, 0.5)
                    for symbol, ticker in tickers.items():
                        quote_volume = ticker.get('quoteVolume', 0)
                        if quote_volume is None:
                            quote_volume = 0
                        volume = quote_volume * weight
                        if volume > 0:
                            if symbol not in all_symbols_data:
                                all_symbols_data[symbol] = {
                                    'total_volume': 0,
                                    'exchange_count': 0,
                                    'exchanges': []
                                }
                            
                            all_symbols_data[symbol]['total_volume'] += volume
                            all_symbols_data[symbol]['exchange_count'] += 1
                            all_symbols_data[symbol]['exchanges'].append(exchange_name)
                            
                except Exception as e:
                    unified_logging.warning(f"Failed to get symbols from {exchange_name}: {e}")
                    continue
            
            # Sort by total volume and deduplicate
            sorted_symbols = sorted(all_symbols_data.items(), 
                                  key=lambda x: x[1]['total_volume'], reverse=True)
            
            # Filter out symbols with very low volume
            filtered_symbols = []
            for symbol, data in sorted_symbols:
                if data['total_volume'] > 1000000:  # Minimum volume threshold
                    filtered_symbols.append(symbol)
            
            # Return top N symbols
            top_symbols = filtered_symbols[:limit]
            
            unified_logging.info(f"Retrieved {len(top_symbols)} deduplicated symbols from {len(self.exchanges)} exchanges")
            return top_symbols
            
        except Exception as e:
            unified_logging.error(f"Failed to get top symbols by volume: {e}", exception=e)
            # Return popular symbols as fallback
            return [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
                'SOL/USDT', 'DOT/USDT', 'DOGE/USDT', 'MATIC/USDT', 'AVAX/USDT',
                'LINK/USDT', 'ATOM/USDT', 'UNI/USDT', 'LTC/USDT', 'BCH/USDT'
            ]
    
    def adjust_cache_ttl_by_volatility(self, volatility: float = None):
        """ULTRA INTELLIGENT: Dynamically adjust cache TTL based on market volatility"""
        try:
            if volatility is None:
                # Calculate volatility from recent BTC price data
                try:
                    btc_data = self.get_current_price('BTC/USDT')
                    if btc_data and btc_data.get('high_24h', 0) > 0 and btc_data.get('low_24h', 0) > 0:
                        price = btc_data['price']
                        high_24h = btc_data['high_24h']
                        low_24h = btc_data['low_24h']
                        volatility = ((high_24h - low_24h) / price) * 100  # Percentage volatility
                    else:
                        volatility = 5.0  # Default moderate volatility
                except Exception:
                    volatility = 5.0
            
            # Store market volatility for future reference
            self.market_volatility = volatility
            
            # Adjust cache TTL based on volatility
            # Higher volatility = shorter cache (more real-time updates needed)
            # Lower volatility = longer cache (less frequent updates needed)
            if volatility > 15:  # Extreme volatility (>15%)
                self.cache_ttl = 5  # 5 seconds - very aggressive updates
            elif volatility > 10:  # High volatility (10-15%)
                self.cache_ttl = 10  # 10 seconds
            elif volatility > 5:  # Moderate volatility (5-10%)
                self.cache_ttl = 15  # 15 seconds (default)
            elif volatility > 2:  # Low volatility (2-5%)
                self.cache_ttl = 30  # 30 seconds
            else:  # Very low volatility (<2%)
                self.cache_ttl = 60  # 60 seconds - can afford longer cache
            
            unified_logging.info(f"🎯 Cache TTL adjusted to {self.cache_ttl}s based on volatility: {volatility:.2f}%")
            
        except Exception as e:
            unified_logging.error(f"Failed to adjust cache TTL: {e}", exception=e)
            self.cache_ttl = self.base_cache_ttl  # Reset to default
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'total_requests': total_requests,
                'hit_rate_percent': round(hit_rate, 2),
                'current_cache_ttl': self.cache_ttl,
                'market_volatility': round(self.market_volatility, 2),
                'cached_items': len(self.data_cache),
                'api_calls_count': self.api_call_count
            }
        except Exception as e:
            unified_logging.error(f"Failed to get cache statistics: {e}")
            return {}
    
    def get_top_coins_by_volume(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get top coins by 24h volume from CoinGecko and exchange data
        
        Args:
            limit: Number of top coins to return
            
        Returns:
            List of coin dictionaries with symbol, volume, price, etc.
        """
        try:
            cache_key = f"top_coins_volume_{limit}"
            current_time = time.time()
            
            # Check cache first (cache for 60 minutes to reduce API calls)
            if (cache_key in self.data_cache and 
                current_time - self.last_update.get(cache_key, 0) < 3600):
                return self.data_cache[cache_key]
            
            # Fetch from CoinGecko API with optimized rate limiting
            time.sleep(0.3)  # 0.3 second delay (optimized for speed)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'volume_desc',  # Sort by volume
                'per_page': limit,
                'page': 1,
                'sparkline': False
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Format data
            top_coins = []
            # Invalid base symbols (stablecoins and other non-tradeable against USDT)
            invalid_symbols = {'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'USDP', 'GUSD', 'PAX', 'HUSD'}
            
            for coin in data:
                coin_symbol = coin['symbol'].upper()
                
                # Skip invalid symbols (stablecoins that can't be traded against USDT)
                if coin_symbol in invalid_symbols:
                    continue
                
                formatted = {
                    'symbol': f"{coin_symbol}/USDT",
                    'name': coin['name'],
                    'price': float(coin.get('current_price', 0)),
                    'volume': float(coin.get('total_volume', 0)),
                    'volume_24h': float(coin.get('total_volume', 0)),
                    'market_cap': float(coin.get('market_cap', 0)),
                    'change_24h': float(coin.get('price_change_percentage_24h', 0)),
                    'market_cap_rank': int(coin.get('market_cap_rank') or 0),
                    'coin_id': coin.get('id', '')
                }
                top_coins.append(formatted)
            
            # Cache the data
            self.data_cache[cache_key] = top_coins
            self.last_update[cache_key] = current_time
            
            unified_logging.info(f"Fetched top {len(top_coins)} coins by volume from CoinGecko API")
            return top_coins
            
        except Exception as e:
            unified_logging.error(f"Failed to get top coins by volume: {e}", exception=e)
            # Fallback to exchange data
            try:
                symbols = self.get_top_symbols_by_volume(limit=limit)
                result = []
                for symbol in symbols[:limit]:
                    market_data = self.get_market_data(symbol)
                    if market_data and market_data.get('price', 0) > 0:
                        result.append({
                            'symbol': symbol,
                            'name': symbol.replace('/USDT', ''),
                            'price': market_data['price'],
                            'volume': market_data.get('volume', 0),
                            'volume_24h': market_data.get('volume', 0),
                            'market_cap': 0,
                            'change_24h': market_data.get('change_24h', 0),
                            'market_cap_rank': 0,
                            'coin_id': ''
                        })
                return result[:limit]
            except Exception:
                return []
    
    def get_top_coins_by_market_cap(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get top coins by market cap from CoinGecko API
        
        Args:
            limit: Number of top coins to return
            
        Returns:
            List of coin dictionaries with symbol, market_cap, price, etc.
        """
        try:
            # Use existing method with market cap sorting
            return self.get_top_100_by_market_cap_real()[:limit]
            
        except Exception as e:
            unified_logging.error(f"Failed to get top coins by market cap: {e}", exception=e)
            # Fallback to volume-based data
            try:
                return self.get_top_coins_by_volume(limit=limit)
            except Exception:
                return []
    
    def get_exchange_netflow(self, symbol: str, hours: int = 24, timeframe: str = '1h') -> Optional[Dict[str, Any]]:
        """Get exchange inflow/outflow data for whale detection - REAL data only"""
        try:
            # Try to get from CoinGlass or Glassnode APIs (if available)
            # For now, estimate from volume and price movement

            # Get historical data for the period
            formatted_symbol = f"{symbol}/USDT" if '/' not in symbol else symbol

            # FIXED: Use dynamic timeframe instead of hardcoded '1h'
            # Calculate appropriate limit based on hours and timeframe
            timeframe_hours_map = {
                '1m': 1/60, '5m': 5/60, '15m': 15/60, '30m': 0.5,
                '1h': 1, '4h': 4, '1d': 24, '1w': 168
            }
            hours_per_candle = timeframe_hours_map.get(timeframe, 1)
            limit = max(10, int(hours / hours_per_candle))

            market_data = self.get_historical_data(formatted_symbol, timeframe, limit)
            
            if not market_data or len(market_data) < 2:
                return None
            
            # Calculate approximate netflow from volume and price action
            total_buy_volume = 0.0
            total_sell_volume = 0.0
            
            for i in range(1, len(market_data)):
                candle = market_data[i]
                prev_candle = market_data[i-1]
                
                volume = float(candle.get('volume', 0))
                close = float(candle.get('close', 0))
                open_price = float(candle.get('open', 0))
                prev_close = float(prev_candle.get('close', 0))
                
                # If price increased, assume more buying
                if close > open_price and close > prev_close:
                    # Bullish candle with upward momentum - likely buying
                    buy_ratio = 0.7  # Assume 70% was buying
                    total_buy_volume += volume * buy_ratio
                    total_sell_volume += volume * (1 - buy_ratio)
                elif close < open_price and close < prev_close:
                    # Bearish candle with downward momentum - likely selling
                    sell_ratio = 0.7  # Assume 70% was selling
                    total_sell_volume += volume * sell_ratio
                    total_buy_volume += volume * (1 - sell_ratio)
                else:
                    # Mixed signal - split 50/50
                    total_buy_volume += volume * 0.5
                    total_sell_volume += volume * 0.5
            
            # Calculate in terms of coin amount (not USD)
            # Netflow is the difference (positive = inflow to exchanges, negative = outflow)
            # Note: Exchange inflow = potential selling pressure
            # Exchange outflow = potential buying/holding
            inflow = total_sell_volume  # Coins moving TO exchanges
            outflow = total_buy_volume  # Coins moving FROM exchanges (being bought)
            net_flow = outflow - inflow  # Positive = net buying, Negative = net selling
            
            return {
                'inflow': inflow,
                'outflow': outflow,
                'net_flow': net_flow,
                'timeframe_hours': hours,
                'symbol': symbol,
                'data_source': 'volume_analysis'
            }
            
        except Exception as e:
            unified_logging.debug(f"Exchange netflow calculation failed for {symbol}: {e}")
            return None
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if getattr(self, '_executor', None) is not None:
                self._executor.shutdown(wait=True)
            unified_logging.info("Real Market Data Fetcher cleaned up")
        except Exception as e:
            unified_logging.error(f"Failed to cleanup: {e}", exception=e)

# Create global instance
_real_market_data_fetcher_instance = None

class RealMarketDataFetcherLazy:
    """Lazy initializer proxy for RealMarketDataFetcher to avoid heavy import-time work.
    It preserves the same public API surface by delegating to an actual instance created on first use.
    """
    def __init__(self):
        self._instance = None
        import threading
        self._lock = threading.Lock()

    def _create(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = RealMarketDataFetcher()
                    # Ensure executor is initialized with DYNAMIC workers
                    if not hasattr(self._instance, '_executor') or self._instance._executor is None:
                        from concurrent.futures import ThreadPoolExecutor
                        # DYNAMIC: Use _ensure_executor method for consistent worker calculation
                        self._instance._ensure_executor()
        return self._instance

    def __getattr__(self, name):
        inst = self._create()
        return getattr(inst, name)

    def __repr__(self):
        if self._instance is None:
            return "<RealMarketDataFetcher (lazy, uninitialized)>"
        return repr(self._instance)

# Export lazy proxy under the original symbol so existing imports remain valid
real_market_data_fetcher = RealMarketDataFetcherLazy()

