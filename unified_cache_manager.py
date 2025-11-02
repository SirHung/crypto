"""
[STAR] GOD MODE 1000 - UNIFIED CACHE MANAGER 💫
===========================================
[START] CENTRALIZED CACHE & DATA STORAGE MANAGEMENT
[FAST] ZERO DUPLICATES - UNIFIED ARCHITECTURE
[BULLSEYE] PRODUCTION-GRADE CACHING & STORAGE

UNIFIED CACHE MANAGER CAPABILITIES:
- Centralized cache management for all modules
- Intelligent cache eviction and TTL
- Data storage coordination
- Memory optimization
- Performance monitoring
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import OrderedDict
import json
import pickle
import hashlib
from pathlib import Path
import sqlite3
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry structure"""
    key: str
    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0
    last_access: float = 0.0
    size_bytes: int = 0

class UnifiedCacheManager:
    """[STAR] UNIFIED CACHE MANAGER - GOD MODE 1000
    Centralized cache and data storage management
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UnifiedCacheManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.unified_logger = logger
        
        # Cache storage
        self.caches: Dict[str, OrderedDict] = {}
        self.cache_ttls: Dict[str, float] = {}
        self.cache_max_sizes: Dict[str, int] = {}
        self.cache_lock = threading.RLock()
        
        # Data storage
        self.data_storage = {}
        self.storage_lock = threading.RLock()
        
        # Performance metrics
        self.metrics = {
            'total_hits': 0,
            'total_misses': 0,
            'total_evictions': 0,
            'total_storage_operations': 0,
            'cache_sizes': {},
            'memory_usage': 0
        }
        
        # Initialize default caches
        self._initialize_default_caches()
        
        # Cache pre-warming
        self.prewarming_enabled = True
        self.prewarmed_keys = set()
        
    # Do NOT start cleanup thread at import time. Call start_cleanup() explicitly when app is ready.
    # self._start_cleanup_thread()
        
        # Pre-warm critical caches
        if self.prewarming_enabled:
            self._prewarm_critical_caches()
        
        self.unified_logger.info("[START] Unified Cache Manager initialized - God Mode 1000")
    
    async def initialize(self):
        """Initialize Cache Manager components"""
        self.unified_logger.info("Cache Manager ready for God Mode 1000")
    
    def _initialize_default_caches(self):
        """Initialize default cache configurations"""
        try:
            # Market data cache
            self.create_cache('market_data', max_size=10000, ttl=30)
            
            # AI predictions cache
            self.create_cache('ai_predictions', max_size=5000, ttl=300)
            
            # Trading signals cache
            self.create_cache('trading_signals', max_size=2000, ttl=60)
            
            # Portfolio data cache
            self.create_cache('portfolio_data', max_size=1000, ttl=120)
            
            # News sentiment cache
            self.create_cache('news_sentiment', max_size=3000, ttl=600)
            
            # On-chain data cache
            self.create_cache('onchain_data', max_size=2000, ttl=180)
            
            # Correlation data cache
            self.create_cache('correlation_data', max_size=1000, ttl=300)
            
            # Performance data cache
            self.create_cache('performance_data', max_size=500, ttl=60)
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize default caches: {e}")
    
    def create_cache(self, name: str, max_size: int = 1000, ttl: float = 300):
        """Create a new cache"""
        try:
            with self.cache_lock:
                if name not in self.caches:
                    self.caches[name] = OrderedDict()
                    self.cache_ttls[name] = ttl
                    self.cache_max_sizes[name] = max_size
                    self.metrics['cache_sizes'][name] = 0
                    self.unified_logger.info(f"Created cache: {name} (max_size={max_size}, ttl={ttl})")
                else:
                    self.unified_logger.warning(f"Cache {name} already exists")
        except Exception as e:
            self.unified_logger.error(f"Failed to create cache {name}: {e}")
    
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            with self.cache_lock:
                if cache_name not in self.caches:
                    self.metrics['total_misses'] += 1
                    return None
                
                cache = self.caches[cache_name]
                if key not in cache:
                    self.metrics['total_misses'] += 1
                    return None
                
                entry = cache[key]
                current_time = time.time()
                
                # Check if entry is expired
                if current_time - entry.timestamp > entry.ttl:
                    del cache[key]
                    self.metrics['total_misses'] += 1
                    self.metrics['total_evictions'] += 1
                    return None
                
                # Update access statistics
                entry.access_count += 1
                entry.last_access = current_time
                
                # Move to end (most recently used)
                cache.move_to_end(key)
                
                self.metrics['total_hits'] += 1
                return entry.value
                
        except Exception as e:
            self.unified_logger.error(f"Failed to get from cache {cache_name}: {e}")
            self.metrics['total_misses'] += 1
            return None
    
    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache"""
        try:
            with self.cache_lock:
                if cache_name not in self.caches:
                    self.unified_logger.warning(f"Cache {cache_name} does not exist")
                    return False
                
                cache = self.caches[cache_name]
                cache_ttl = ttl or self.cache_ttls[cache_name]
                max_size = self.cache_max_sizes[cache_name]
                
                # Calculate entry size
                try:
                    entry_size = len(pickle.dumps(value))
                except:
                    entry_size = 1024  # Default size
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    timestamp=time.time(),
                    ttl=cache_ttl,
                    size_bytes=entry_size
                )
                
                # Remove existing entry if it exists
                if key in cache:
                    del cache[key]
                
                # Check cache size limit
                while len(cache) >= max_size:
                    # Remove least recently used item
                    oldest_key, oldest_entry = cache.popitem(last=False)
                    self.metrics['total_evictions'] += 1
                    self.metrics['cache_sizes'][cache_name] -= oldest_entry.size_bytes
                
                # Add new entry
                cache[key] = entry
                self.metrics['cache_sizes'][cache_name] += entry_size
                
                return True
                
        except Exception as e:
            self.unified_logger.error(f"Failed to set cache {cache_name}: {e}")
            return False
    
    def delete(self, cache_name: str, key: str) -> bool:
        """Delete key from cache"""
        try:
            with self.cache_lock:
                if cache_name not in self.caches:
                    return False
                
                cache = self.caches[cache_name]
                if key not in cache:
                    return False
                
                entry = cache[key]
                del cache[key]
                self.metrics['cache_sizes'][cache_name] -= entry.size_bytes
                return True
                
        except Exception as e:
            self.unified_logger.error(f"Failed to delete from cache {cache_name}: {e}")
            return False
    
    def clear_cache(self, cache_name: str) -> bool:
        """Clear entire cache"""
        try:
            with self.cache_lock:
                if cache_name not in self.caches:
                    return False
                
                cache = self.caches[cache_name]
                cache.clear()
                self.metrics['cache_sizes'][cache_name] = 0
                return True
                
        except Exception as e:
            self.unified_logger.error(f"Failed to clear cache {cache_name}: {e}")
            return False
    
    def get_cache_stats(self, cache_name: str) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with self.cache_lock:
                if cache_name not in self.caches:
                    return {}
                
                cache = self.caches[cache_name]
                current_time = time.time()
                
                # Count expired entries
                expired_count = 0
                for entry in cache.values():
                    if current_time - entry.timestamp > entry.ttl:
                        expired_count += 1
                
                return {
                    'name': cache_name,
                    'size': len(cache),
                    'max_size': self.cache_max_sizes[cache_name],
                    'ttl': self.cache_ttls[cache_name],
                    'expired_entries': expired_count,
                    'memory_usage': self.metrics['cache_sizes'].get(cache_name, 0),
                    'hit_rate': self._calculate_hit_rate()
                }
                
        except Exception as e:
            self.unified_logger.error(f"Failed to get cache stats {cache_name}: {e}")
            return {}
    
    def _calculate_hit_rate(self) -> float:
        """Calculate overall cache hit rate"""
        try:
            total_requests = self.metrics['total_hits'] + self.metrics['total_misses']
            if total_requests == 0:
                return 0.0
            return self.metrics['total_hits'] / total_requests
        except:
            return 0.0

    def start_cleanup(self):
        """Public method to start cleanup thread when the application is ready."""
        self._start_cleanup_thread()
    
    def _cleanup_loop(self):
        """Background cache cleanup loop"""
        while True:
            try:
                time.sleep(60)  # Run every minute
                self._cleanup_expired_entries()
            except Exception:
                pass
    
    def _cleanup_expired_entries(self):
        """Remove expired entries from all caches"""
        try:
            with self.cache_lock:
                current_time = time.time()
                
                for cache_name, cache in self.caches.items():
                    expired_keys = []
                    
                    for key, entry in cache.items():
                        if current_time - entry.timestamp > entry.ttl:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        entry = cache[key]
                        del cache[key]
                        self.metrics['total_evictions'] += 1
                        self.metrics['cache_sizes'][cache_name] -= entry.size_bytes
                        
        except Exception as e:
            self.unified_logger.error(f"Failed to cleanup expired entries: {e}")
    
    def _prewarm_critical_caches(self):
        """Pre-warm critical caches with essential data"""
        try:
            # Pre-warm market data cache with common symbols
            common_symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT']
            for symbol in common_symbols:
                self.set('market_data', symbol, {'price': 0, 'volume': 0, 'timestamp': time.time()}, ttl=30)
            
            self.unified_logger.info("Critical caches pre-warmed successfully")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to pre-warm caches: {e}")
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall cache system statistics"""
        try:
            total_memory = sum(self.metrics['cache_sizes'].values())
            total_entries = sum(len(cache) for cache in self.caches.values())
            
            return {
                'total_caches': len(self.caches),
                'total_entries': total_entries,
                'total_memory_usage': total_memory,
                'total_hits': self.metrics['total_hits'],
                'total_misses': self.metrics['total_misses'],
                'total_evictions': self.metrics['total_evictions'],
                'hit_rate': self._calculate_hit_rate(),
                'cache_details': {name: self.get_cache_stats(name) for name in self.caches.keys()}
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get overall stats: {e}")
            return {}
    
    def emergency_cleanup(self):
        """Emergency cache cleanup for critical memory situations - INTELLIGENT OPTIMIZATION"""
        try:
            with self.cache_lock:
                # Calculate total memory usage before cleanup
                total_before = 0
                for cache_name, cache in self.caches.items():
                    for entry in cache.values():
                        if isinstance(entry, CacheEntry):
                            total_before += entry.size_bytes
                
                self.unified_logger.warning(f"🚨 EMERGENCY CACHE CLEANUP initiated - Total cache: {total_before / (1024**2):.2f} MB")
                
                # Stage 1: Remove expired entries
                expired_removed = 0
                current_time = time.time()
                for cache_name, cache in self.caches.items():
                    expired_keys = []
                    for key, entry in cache.items():
                        if isinstance(entry, CacheEntry) and (current_time - entry.timestamp) > entry.ttl:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del cache[key]
                        expired_removed += 1
                
                # Stage 2: Remove least recently used entries (aggressive 50% cleanup)
                lru_removed = 0
                for cache_name, cache in self.caches.items():
                    if len(cache) > 10:  # Only cleanup if cache has significant entries
                        # Sort by last access time
                        sorted_entries = sorted(
                            cache.items(),
                            key=lambda x: x[1].last_access if isinstance(x[1], CacheEntry) else 0
                        )
                        
                        # Remove oldest 50%
                        remove_count = len(sorted_entries) // 2
                        for key, _ in sorted_entries[:remove_count]:
                            del cache[key]
                            lru_removed += 1
                
                # Stage 3: Clear low-priority caches completely
                low_priority_caches = ['temporary', 'debug', 'test']
                for cache_name in low_priority_caches:
                    if cache_name in self.caches:
                        cleared = len(self.caches[cache_name])
                        self.caches[cache_name].clear()
                        lru_removed += cleared
                
                # Calculate memory freed
                total_after = 0
                for cache_name, cache in self.caches.items():
                    for entry in cache.values():
                        if isinstance(entry, CacheEntry):
                            total_after += entry.size_bytes
                
                freed_mb = (total_before - total_after) / (1024**2)
                
                self.unified_logger.info(
                    f"✅ Emergency cleanup completed: Removed {expired_removed} expired + {lru_removed} LRU entries. "
                    f"Freed {freed_mb:.2f} MB (Before: {total_before/(1024**2):.2f} MB → After: {total_after/(1024**2):.2f} MB)"
                )
                
                self.metrics['total_evictions'] += (expired_removed + lru_removed)
                
        except Exception as e:
            self.unified_logger.error(f"Emergency cleanup failed: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # FEATURE STORE METHODS (Merged from feature_store.py)
    # ═══════════════════════════════════════════════════════════════════
    
    def put_feature(self, name: str, value: Any, version: str = "v1", ttl: int = 300) -> bool:
        """Store a feature with TTL (merged from FeatureStore)"""
        try:
            cache_name = "feature_store"
            if cache_name not in self.caches:
                self.create_cache(cache_name, ttl=ttl, max_size=10000)
            
            self.set(cache_name, name, value, ttl=ttl)
            return True
        except Exception as e:
            self.unified_logger.error(f"Error storing feature: {e}")
            return False
    
    def get_feature(self, name: str) -> Optional[Any]:
        """Get a feature (merged from FeatureStore)"""
        try:
            cache_name = "feature_store"
            return self.get(cache_name, name)
        except Exception as e:
            self.unified_logger.error(f"Error getting feature: {e}")
            return None
    
    def get_feature_metadata(self, name: str) -> Optional[Dict]:
        """Get feature metadata (merged from FeatureStore)"""
        try:
            cache_name = "feature_store"
            if cache_name not in self.caches:
                return None
            
            if name not in self.caches[cache_name]:
                return None
            
            entry = self.caches[cache_name][name]
            if not isinstance(entry, CacheEntry):
                return None
            
            return {
                'name': name,
                'version': 'v1',
                'computed_at': datetime.fromtimestamp(entry.timestamp).isoformat(),
                'expires_at': datetime.fromtimestamp(entry.timestamp + entry.ttl).isoformat(),
                'age_seconds': time.time() - entry.timestamp,
                'access_count': entry.access_count
            }
        except Exception as e:
            self.unified_logger.error(f"Error getting metadata: {e}")
            return None


class UnifiedCacheManagerProxy:
    """Proxy that defers instantiation of UnifiedCacheManager until first access.
    Keeps the same public API via __getattr__.
    """
    def __init__(self):
        self._instance = None
        self._lock = threading.Lock()

    def _ensure(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = UnifiedCacheManager()

    def __getattr__(self, name):
        self._ensure()
        return getattr(self._instance, name)


# Export proxy under original name
unified_cache_manager = UnifiedCacheManagerProxy()

# ═══════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY: Aliases
# (Merged from feature_store.py - ALL FUNCTIONALITY NOW IN unified_cache_manager)
# ═══════════════════════════════════════════════════════════════════
unified_cache = unified_cache_manager  # Alias for consistency
feature_store = unified_cache_manager
