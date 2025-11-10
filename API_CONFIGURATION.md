# API CONFIGURATION - REAL EXCHANGE DATA ONLY

## 🎯 DATA SOURCES - 100% REAL EXCHANGE DATA

### NO FALLBACK POLICY
**User Requirement:** Remove ALL fallback/wrapper mechanisms

**Implementation:**
- ✅ NO yfinance fallback
- ✅ NO CoinGecko/CryptoCompare fallback
- ✅ NO fake/demo/placeholder data
- ✅ ONLY CCXT exchange APIs

**Result:** If all exchanges fail → Return 0 or empty list (NOT fake data)

---

## 📊 SUPPORTED EXCHANGES (11 Exchanges via CCXT)

### Primary Exchanges:
1. **Binance** - Largest global crypto exchange
   - Rate Limit: 50ms (higher rate supported)
   - Markets: 1000+ trading pairs
   - Reliability: Highest

2. **Bybit** - Major derivatives exchange
   - Rate Limit: 300ms (default)
   - Markets: 500+ trading pairs
   - Derivatives: Perpetuals, futures

3. **OKX** - Top tier exchange
   - Rate Limit: 300ms (default)
   - Markets: 400+ trading pairs
   - Advanced features

4. **Coinbase** - Major US exchange
   - Rate Limit: 300ms (default)
   - Markets: 200+ trading pairs
   - US regulated

5. **Kraken** - Established exchange
   - Rate Limit: 3000ms (slower)
   - Markets: 200+ trading pairs
   - European focused

### Secondary Exchanges:
6. **KuCoin** - Popular altcoin exchange
7. **Gate.io** - High volume exchange
8. **Huobi** - Major Asian exchange
9. **Bitfinex** - Advanced trading platform
10. **Bitget** - Derivatives focused
11. **MEXC** - Altcoin specialist

---

## ⚙️ RATE LIMIT CONFIGURATION

### Default Configuration:
```python
common_config = {
    'rateLimit': 300,  # 300ms between requests
    'enableRateLimit': True,  # Auto rate limiting
    'timeout': 45000,  # 45s timeout for slow connections
    'options': {
        'recvWindow': 60000,
        'defaultType': 'spot'
    },
    'retry': {
        'maxRetries': 3,
        'retryDelay': 1000  # 1s between retries
    }
}
```

### Exchange-Specific Limits:

| Exchange | Rate Limit | Notes |
|----------|-----------|-------|
| Binance | 50ms | Fastest, highest throughput |
| Bybit | 300ms | Standard |
| OKX | 300ms | Standard |
| Coinbase | 300ms | Standard |
| **Kraken** | **3000ms** | Slowest, most restrictive |
| KuCoin | 300ms | Standard |
| Gate.io | 300ms | Standard |
| Huobi | 300ms | Standard |
| Bitfinex | 300ms | Standard |
| Bitget | 300ms | Standard |
| MEXC | 300ms | Standard |

### Connection Pool Configuration:
```python
'agent': {
    'http': {
        'maxSockets': 100,  # Max parallel connections
        'keepAlive': True,
        'keepAliveMsecs': 30000,
        'maxFreeSockets': 50
    },
    'https': {
        'maxSockets': 100,
        'keepAlive': True,
        'keepAliveMsecs': 30000,
        'maxFreeSockets': 50
    }
}
```

---

## 📈 API ENDPOINT LIMITS

### Historical Data (OHLCV):
**Method:** `get_historical_data(symbol, timeframe, limit)`

**Exchange Limits:**
- **Binance**: 1000 candles per request (most common)
- **Bybit**: 200 candles per request
- **OKX**: 100-300 candles per request
- **Kraken**: 720 candles per request
- **Others**: Varies (100-1000)

**Our Implementation:**
- Chunk size: 200 candles per request (safe for all exchanges)
- Delay between chunks: 1.0 second
- Automatic chunking for large requests

**Example:**
- Request 1000 candles → 5 chunks of 200 → ~5 seconds total
- Request 5000 candles → 25 chunks of 200 → ~25 seconds total

### Real-Time Market Data:
**Method:** `get_market_data(symbol)`

**Data Retrieved:**
- Current price
- 24h change %
- 24h volume
- 24h high/low
- Timestamp

**Rate Limits:**
- Same as configured rate limits above
- Cached for 5 seconds to reduce API calls

### Symbol Lists:
**Methods:**
- `get_all_available_symbols()` - All symbols from all exchanges
- `get_top_symbols_by_volume(limit)` - Top N by 24h volume

**Caching:**
- Cached for 300 seconds (5 minutes)
- Prevents excessive API calls

---

## 🔄 RETRY MECHANISM

### Automatic Retries:
```python
'retry': {
    'maxRetries': 3,  # Retry up to 3 times
    'retryDelay': 1000  # Wait 1 second between retries
}
```

### Retry Logic:
1. First attempt fails → Wait 1 second → Retry
2. Second attempt fails → Wait 1 second → Retry
3. Third attempt fails → Wait 1 second → Retry
4. All retries failed → Return 0 or [] (NO fake data)

---

## ⚠️ ERROR HANDLING

### When Exchange API Fails:

**Historical Data:**
```python
# Returns empty list if all exchanges fail
return []  # NOT fake data
```

**Market Data:**
```python
# Returns zero values if all exchanges fail
return {
    'price': 0.0,
    'change_24h': 0.0,
    'volume': 0.0,
    'high_24h': 0.0,
    'low_24h': 0.0,
    'timestamp': datetime.now(timezone.utc),
    'exchange': None
}
# NOT fake data - honest "no data available"
```

### Error Messages:
```
❌ CRITICAL: All exchanges failed for BTC/USDT. Returning 0 values.
❌ CRITICAL: All exchanges failed for BTC/USDT 1h historical data. Returning empty list.
```

---

## 🚀 PERFORMANCE OPTIMIZATION

### Caching Strategy:
1. **Data Cache:**
   - Historical data: 60 seconds TTL
   - Market data: 5 seconds TTL
   - Symbol lists: 300 seconds TTL

2. **Connection Pooling:**
   - Keep-alive connections
   - 100 max sockets per protocol
   - 50 free sockets maintained

3. **Parallel Fetching:**
   - Try multiple exchanges simultaneously
   - Return data from first successful exchange
   - Fallthrough to next exchange if first fails

### Multi-Exchange Strategy:
```
Request → Try Binance (fastest)
          ↓ Failed?
          Try OKX
          ↓ Failed?
          Try Bybit
          ↓ Failed?
          Try others...
          ↓ All failed?
          Return 0/[] (NO fake data)
```

---

## 📝 IMPORTANT NOTES

### 1. API Keys:
- **Current:** All exchanges use PUBLIC endpoints (no API key required)
- **Public endpoints:** Read-only market data
- **Private endpoints:** Would need API keys (for trading)

### 2. Rate Limit Best Practices:
- Always enable rate limiting (`enableRateLimit: True`)
- Use larger delays for Kraken (3000ms)
- Implement chunking for large data requests
- Add delays between chunks (1 second)

### 3. Network Resilience:
- 45 second timeout for slow connections
- 3 automatic retries
- Connection pooling to reuse connections
- Keep-alive to maintain connections

### 4. Data Quality:
- ✅ 100% real exchange data
- ✅ NO fake/demo/placeholder data
- ✅ NO fallback APIs (yfinance, CoinGecko, etc.)
- ✅ Return 0 or [] if data unavailable (honest)

---

## 🔍 VERIFICATION

### Check Data Source:
Every market data response includes:
```python
{
    'exchange': 'binance',  # Source exchange name
    'timestamp': datetime.now(timezone.utc),  # When data was fetched
    ...
}
```

### Verify No Fallback:
```bash
# Search codebase for fallback code
grep -r "yfinance\|coingecko\|cryptocompare" --include="*.py"
# Should return: No results (all removed)
```

---

## 📊 MONITORING

### Log Messages to Monitor:

**Success:**
```
✅ Binance exchange initialized
✅ Fetched 200 candles from Binance for BTC/USDT
✅ Market data from Binance: BTC/USDT = $43,250
```

**Warnings:**
```
⚠️ No candles fetched from Binance for UNKNOWN/USDT
⚠️ Large data request: 5000 candles = 25 chunks
```

**Errors:**
```
❌ CRITICAL: All exchanges failed for BTC/USDT. Returning 0 values.
Failed to fetch from Binance: Connection timeout
```

---

## 🎯 SUMMARY

**Data Philosophy:**
- Real data only, always
- No fallbacks, no fake data
- Return 0 or [] if unavailable (honest failure)
- User sees real market conditions only

**API Configuration:**
- 11 major exchanges via CCXT
- Rate limits: 50ms (Binance) to 3000ms (Kraken)
- Auto retry, connection pooling, caching
- Public endpoints (no API keys needed)

**Result:**
✅ 100% REAL EXCHANGE DATA
❌ NO fallback mechanisms
❌ NO fake/demo/placeholder data
✅ Honest error handling (return 0, not fake data)
