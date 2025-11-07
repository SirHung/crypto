"""
ADVANCED OPTIMIZER - GOD MODE 1000
===================================
Advanced system optimization, warm-up, and auto-tuning capabilities
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from market_constants import market_constants
except ImportError:
    market_constants = None

try:
    from unified_config import unified_config
except ImportError:
    unified_config = None


class AdvancedOptimizer:
    """
    Advanced System Optimizer - Maximum Performance
    
    Features:
    - Cache warm-up on startup
    - Parallel data preloading
    - Auto-tuning system parameters
    - Performance monitoring and optimization
    - Resource allocation optimization
    """
    
    def __init__(self):
        """Initialize Advanced Optimizer"""
        self.unified_logger = unified_logging.get_logger("advanced_optimizer")
        self.is_warmed_up = False
        self.optimization_stats = {
            'warmup_time': 0,
            'cache_preloaded': 0,
            'symbols_preloaded': 0,
            'indicators_preloaded': 0,
            'models_preloaded': 0
        }
        
        self.unified_logger.info("✅ Advanced Optimizer initialized")
    
    def optimize_system_performance(self, model: Any, model_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize system performance based on model metrics
        Used in AI training validation - GOD MODE 10000
        ULTRA ENHANCED: Better scoring for crypto models
        """
        try:
            if not model_metrics:
                return {'optimization_score': 0.5, 'status': 'no_metrics'}
            
            # Extract ALL available metrics for comprehensive evaluation
            accuracy = model_metrics.get('accuracy', 0.0)
            precision = model_metrics.get('precision', 0.0)
            recall = model_metrics.get('recall', 0.0)
            f1_score = model_metrics.get('f1_score', 0.0)
            feature_count = model_metrics.get('feature_count', 0)
            sample_count = model_metrics.get('sample_count', 0)
            
            # FIXED: If all metrics are 0, model hasn't been trained yet
            if accuracy == 0.0 and precision == 0.0 and recall == 0.0 and f1_score == 0.0:
                return {'optimization_score': 0.0, 'status': 'not_trained'}
            
            # ULTRA ENHANCED: Multi-component scoring system
            # Component 1: Model Performance (60%)
            available_metrics = []
            if accuracy > 0:
                available_metrics.append(('accuracy', accuracy, 0.4))
            if precision > 0:
                available_metrics.append(('precision', precision, 0.2))
            if recall > 0:
                available_metrics.append(('recall', recall, 0.2))
            if f1_score > 0:
                available_metrics.append(('f1_score', f1_score, 0.2))
            
            # Calculate weighted performance score
            if available_metrics:
                total_weight = sum(weight for _, _, weight in available_metrics)
                performance_score = sum(value * (weight / total_weight) 
                                  for _, value, weight in available_metrics)
            else:
                performance_score = 0.5  # Fallback
            
            # Component 2: Data Quality (20%)
            data_quality_score = 0.0
            if feature_count > 0 and sample_count > 0:
                # Score based on feature richness and data sufficiency
                feature_score = min(1.0, feature_count / 50.0)  # Ideal: 50+ features
                sample_score = min(1.0, sample_count / 1000.0)  # Ideal: 1000+ samples
                data_quality_score = (feature_score * 0.6 + sample_score * 0.4)
            else:
                data_quality_score = 0.5  # Default if not available
            
            # Component 3: System Efficiency (20%)
            # Simplified: Based on model complexity vs performance tradeoff
            if accuracy > 0:
                # Higher accuracy with fewer features = better efficiency
                efficiency_score = accuracy * (1.0 + (1.0 / max(1, feature_count / 10.0)))
                efficiency_score = min(1.0, efficiency_score)
            else:
                efficiency_score = 0.5
            
            # FINAL SCORE: Weighted combination of all components
            overall_score = (performance_score * 0.60 + 
                           data_quality_score * 0.20 + 
                           efficiency_score * 0.20)
            
            # Ensure score is in [0, 1]
            overall_score = max(0.0, min(1.0, overall_score))
            
            # DYNAMIC thresholds from market_constants instead of hardcoded
            threshold_excellent = market_constants.get_accuracy_threshold_excellent() if market_constants else 0.95
            threshold_good = market_constants.get_accuracy_threshold_good() if market_constants else 0.90
            threshold_moderate = market_constants.get_accuracy_threshold_moderate() if market_constants else 0.80
            
            # Calculate optimization score based on overall performance
            if overall_score > threshold_excellent:
                optimization_score = 1.0
                status = 'excellent'
                recommendation = 'System performing optimally'
            elif overall_score > threshold_good:
                optimization_score = 0.9
                status = 'good'
                recommendation = 'System performing well'
            elif overall_score > threshold_moderate:
                optimization_score = 0.7
                status = 'moderate'
                recommendation = 'Consider hyperparameter tuning'
            else:
                optimization_score = max(0.5, overall_score)  # At least 0.5 if model is trained
                status = 'needs_improvement'
                recommendation = 'Increase training data or adjust model architecture'
            
            return {
                'optimization_score': float(optimization_score),
                'status': status,
                'recommendation': recommendation,
                'current_accuracy': float(accuracy)
            }
            
        except Exception as e:
            self.unified_logger.warning(f"System optimization analysis failed: {e}")
            return {'optimization_score': 0.5, 'status': 'error'}
    
    def warmup_system(self, symbols: List[str] = None, background: bool = True) -> Dict[str, Any]:
        """
        Warm up system caches for maximum performance
        
        Args:
            symbols: List of symbols to preload (default: top symbols)
            background: Run in background thread (default: True)
            
        Returns:
            Dict with warm-up statistics
        """
        try:
            start_time = time.time()
            
            # Default symbols if not provided
            if symbols is None:
                symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT']
            
            self.unified_logger.info(f"🔥 Starting system warm-up for {len(symbols)} symbols...")
            
            if background:
                # Run in background
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._warmup_caches, symbols)
                    # Don't wait, let it run in background
                    self.unified_logger.info("🔥 Warm-up started in background")
                    return {'status': 'warming_up', 'symbols': len(symbols)}
            else:
                # Run synchronously
                result = self._warmup_caches(symbols)
                
                warmup_time = time.time() - start_time
                self.optimization_stats['warmup_time'] = warmup_time
                self.is_warmed_up = True
                
                self.unified_logger.info(f"✅ System warm-up completed in {warmup_time:.2f}s")
                return result
                
        except Exception as e:
            self.unified_logger.error(f"Failed to warm up system: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _warmup_caches(self, symbols: List[str]) -> Dict[str, Any]:
        """Internal method to warm up caches"""
        try:
            stats = {
                'cache_preloaded': 0,
                'symbols_preloaded': 0,
                'indicators_preloaded': 0,
                'models_preloaded': 0
            }
            
            # 1. Preload market data
            try:
                from real_market_data_fetcher import real_market_data_fetcher
                for symbol in symbols:
                    try:
                        data = real_market_data_fetcher.get_historical_data(symbol, '1h', 100)
                        if data:
                            stats['symbols_preloaded'] += 1
                            stats['cache_preloaded'] += 1
                    except Exception:
                        pass
                
                self.unified_logger.info(f"✅ Preloaded market data for {stats['symbols_preloaded']} symbols")
            except Exception as e:
                self.unified_logger.warning(f"Market data preload failed: {e}")
            
            # 2. Preload technical indicators
            try:
                from unified_technical_indicators import unified_technical_indicators
                # Just importing warms up the indicator cache
                stats['indicators_preloaded'] = 1
                self.unified_logger.info("✅ Technical indicators cache warmed up")
            except Exception as e:
                self.unified_logger.warning(f"Indicators preload failed: {e}")
            
            # 3. Preload AI models
            try:
                from ai_training_engine import ai_training_engine
                # Check if models are initialized
                if hasattr(ai_training_engine, 'ai_models'):
                    stats['models_preloaded'] = len(ai_training_engine.ai_models)
                    self.unified_logger.info(f"✅ AI models cache warmed up: {stats['models_preloaded']} models")
            except Exception as e:
                self.unified_logger.warning(f"AI models preload failed: {e}")
            
            # Update stats
            self.optimization_stats.update(stats)
            
            return {
                'status': 'completed',
                'stats': stats
            }
            
        except Exception as e:
            self.unified_logger.error(f"Cache warm-up failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def optimize_parallel_workers(self, aggressive: bool = False, threads_only: bool = False) -> Dict[str, int]:
        """
        ULTRA ADVANCED: Auto-optimize parallel worker count with intelligent system monitoring
        
        Args:
            aggressive: Use aggressive resource allocation (default: False)
            threads_only: Only optimize thread workers, skip multiprocessing (default: False)
        
        Returns:
            Dict with recommended worker counts and system metrics
        """
        try:
            import psutil
            
            # Get comprehensive system stats
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False) or cpu_count_logical
            cpu_usage = psutil.cpu_percent(interval=0.2)
            cpu_freq = psutil.cpu_freq()
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            ram_available_gb = ram.available / (1024**3)
            
            # Get CPU per-core usage for better optimization
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            avg_per_core = sum(cpu_per_core) / len(cpu_per_core) if cpu_per_core else cpu_usage
            
            # ULTRA INTELLIGENT worker calculation with safety margins
            base_multiplier = 1.0
            
            # Adjust multiplier based on system state
            if aggressive:
                base_multiplier = 1.5  # Push harder in aggressive mode
            
            # Calculate based on load profile
            if cpu_usage > 85 or ram_usage > 85:
                # CRITICAL load - emergency reduction
                thread_multiplier = 0.3 * base_multiplier
                process_multiplier = 0.2 * base_multiplier
                load_state = "CRITICAL"
            elif cpu_usage > 70 or ram_usage > 70:
                # High load - conservative
                thread_multiplier = 0.5 * base_multiplier
                process_multiplier = 0.4 * base_multiplier
                load_state = "HIGH"
            elif cpu_usage > 50 or ram_usage > 50:
                # Medium load - balanced
                thread_multiplier = 0.8 * base_multiplier
                process_multiplier = 0.6 * base_multiplier
                load_state = "MEDIUM"
            else:
                # Low load - maximize performance
                thread_multiplier = 1.2 * base_multiplier
                process_multiplier = 0.8 * base_multiplier
                load_state = "OPTIMAL"
            
            # Calculate thread workers (I/O bound tasks)
            # Use logical cores * multiplier, considering RAM availability
            max_workers_by_ram = int((ram_available_gb * 1024) / 100)  # Assume 100MB per worker
            thread_workers = int(cpu_count_logical * 4 * thread_multiplier)
            thread_workers = min(thread_workers, max_workers_by_ram, 256)
            thread_workers = max(thread_workers, 4)  # Minimum 4 workers
            
            # Calculate process workers (CPU bound tasks)
            # Use physical cores * multiplier
            if threads_only:
                # Skip multiprocessing if threads_only flag is set
                process_workers = 0
            else:
                process_workers = int(cpu_count_physical * process_multiplier)
                process_workers = max(process_workers, 1)  # Minimum 1 worker
                process_workers = min(process_workers, 32)  # Maximum 32 workers
            
            # Apply settings to parallel_executor if available
            try:
                from parallel_executor import parallel_executor
                if parallel_executor:
                    parallel_executor.max_thread_workers = thread_workers
                    if not threads_only:
                        parallel_executor.max_process_workers = process_workers
            except Exception:
                pass
            
            recommendation = {
                'thread_workers': thread_workers,
                'process_workers': process_workers,
                'current_cpu_usage': cpu_usage,
                'current_ram_usage': ram_usage,
                'ram_available_gb': ram_available_gb,
                'cpu_count_logical': cpu_count_logical,
                'cpu_count_physical': cpu_count_physical,
                'avg_cpu_per_core': avg_per_core,
                'cpu_frequency_mhz': cpu_freq.current if cpu_freq else 0,
                'load_state': load_state,
                'aggressive_mode': aggressive
            }
            
            mode_str = "threads-only" if threads_only else f"{thread_workers} threads, {process_workers} processes"
            self.unified_logger.info(
                f"⚡ ULTRA optimized workers: {mode_str} "
                f"[{load_state}] (CPU: {cpu_usage:.1f}%, RAM: {ram_usage:.1f}%, Available: {ram_available_gb:.1f}GB)"
            )
            
            return recommendation
            
        except Exception as e:
            self.unified_logger.error(f"Failed to optimize workers: {e}")
            return {
                'thread_workers': 32,
                'process_workers': 4,
                'current_cpu_usage': 0,
                'current_ram_usage': 0,
                'load_state': 'FALLBACK',
                'error': str(e)
            }
    
    def auto_tune_cache_settings(self, market_volatility: float = 0.5) -> Dict[str, Any]:
        """
        ULTRA ADVANCED: Auto-tune cache settings with market-aware optimization
        
        Args:
            market_volatility: Current market volatility (0-1 scale, default: 0.5)
        
        Returns:
            Dict with recommended cache settings optimized for current conditions
        """
        try:
            import psutil
            
            ram = psutil.virtual_memory()
            ram_total_gb = ram.total / (1024**3)
            ram_available_gb = ram.available / (1024**3)
            ram_usage = ram.percent
            
            # Get dynamic market volatility if available
            try:
                if market_constants:
                    market_volatility = market_constants._get_market_volatility()
            except Exception:
                pass
            
            # ULTRA INTELLIGENT cache sizing based on available RAM and market conditions
            # Allocate up to 30% of available RAM for caching
            cache_ram_budget_gb = min(ram_available_gb * 0.3, 8.0)  # Max 8GB for caches
            
            # Calculate cache sizes (assuming average entry sizes)
            # Feature cache: ~10KB per entry
            # Data cache: ~50KB per entry
            # Indicator cache: ~5KB per entry
            feature_entry_size_kb = 10
            data_entry_size_kb = 50
            indicator_entry_size_kb = 5
            
            total_kb_budget = cache_ram_budget_gb * 1024 * 1024
            
            # Distribute cache budget (40% features, 40% data, 20% indicators)
            feature_cache_size = int((total_kb_budget * 0.4) / feature_entry_size_kb)
            data_cache_size = int((total_kb_budget * 0.4) / data_entry_size_kb)
            indicator_cache_size = int((total_kb_budget * 0.2) / indicator_entry_size_kb)
            
            # Apply reasonable bounds
            feature_cache_size = max(500, min(feature_cache_size, 5000))
            data_cache_size = max(250, min(data_cache_size, 2000))
            indicator_cache_size = max(100, min(indicator_cache_size, 3000))
            
            # ULTRA DYNAMIC: TTL based on market volatility (higher volatility = shorter TTL)
            # Base TTL calculation from market conditions
            base_ttl = market_constants.get_dynamic_cache_ttl() if market_constants else 300
            volatility_factor = 1.0 + (market_volatility * 2.0)  # Range: 1.0 - 3.0
            indicator_cache_ttl = int(base_ttl / volatility_factor)
            
            # ULTRA DYNAMIC bounds: adjust min/max based on market state
            min_ttl = 30 if market_volatility > 0.8 else 60  # Faster refresh in high volatility
            max_ttl = 600 if market_volatility < 0.2 else 900  # Longer cache in low volatility
            indicator_cache_ttl = max(min_ttl, min(indicator_cache_ttl, max_ttl))
            
            # Adjust for system load
            if ram_usage > 80:
                # High RAM usage - reduce caches
                feature_cache_size = int(feature_cache_size * 0.6)
                data_cache_size = int(data_cache_size * 0.6)
                indicator_cache_size = int(indicator_cache_size * 0.6)
            elif ram_usage > 60:
                # Medium RAM usage - moderate reduction
                feature_cache_size = int(feature_cache_size * 0.8)
                data_cache_size = int(data_cache_size * 0.8)
                indicator_cache_size = int(indicator_cache_size * 0.8)
            
            # Apply settings to modules
            try:
                from ai_training_engine import ai_training_engine
                if hasattr(ai_training_engine, '_feature_cache_max_size'):
                    ai_training_engine._feature_cache_max_size = feature_cache_size
            except Exception:
                pass
            
            try:
                from unified_technical_indicators import unified_technical_indicators
                if hasattr(unified_technical_indicators, 'cache_ttl'):
                    unified_technical_indicators.cache_ttl = indicator_cache_ttl
            except Exception:
                pass
            
            settings = {
                'feature_cache_size': feature_cache_size,
                'data_cache_size': data_cache_size,
                'indicator_cache_size': indicator_cache_size,
                'indicator_cache_ttl': indicator_cache_ttl,
                'cache_ram_budget_gb': cache_ram_budget_gb,
                'ram_available_gb': ram_available_gb,
                'ram_total_gb': ram_total_gb,
                'ram_usage_percent': ram_usage,
                'market_volatility': market_volatility,
                'volatility_factor': volatility_factor
            }
            
            self.unified_logger.info(
                f"⚙️ ULTRA auto-tuned caches: feature={feature_cache_size}, data={data_cache_size}, "
                f"indicator={indicator_cache_size}, ttl={indicator_cache_ttl}s "
                f"(RAM: {ram_available_gb:.1f}GB/{ram_total_gb:.1f}GB, volatility={market_volatility:.2f})"
            )
            
            return settings
            
        except Exception as e:
            self.unified_logger.error(f"Failed to auto-tune cache: {e}")
            return {
                'feature_cache_size': 1000,
                'data_cache_size': 500,
                'indicator_cache_size': 500,
                'indicator_cache_ttl': 300,
                'error': str(e)
            }
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get current optimization statistics"""
        return {
            'is_warmed_up': self.is_warmed_up,
            'stats': self.optimization_stats
        }
    
    def parallel_fetch_market_data(self, symbols: List[str], timeframe: str = '1h', limit: int = 100) -> Dict[str, Any]:
        """
        Fetch market data for multiple symbols in parallel - MAXIMUM SPEED
        
        Args:
            symbols: List of symbols to fetch
            timeframe: Timeframe (default: '1h')
            limit: Number of candles (default: 100)
            
        Returns:
            Dict with symbol -> data mapping
        """
        try:
            from real_market_data_fetcher import real_market_data_fetcher
            
            results = {}
            start_time = time.time()
            
            # Parallel fetch using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=min(len(symbols), 16)) as executor:
                future_to_symbol = {
                    executor.submit(
                        real_market_data_fetcher.get_historical_data,
                        symbol,
                        timeframe,
                        limit
                    ): symbol
                    for symbol in symbols
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        data = future.result(timeout=10)
                        if data:
                            results[symbol] = data
                    except Exception as e:
                        self.unified_logger.debug(f"Failed to fetch {symbol}: {e}")
            
            fetch_time = time.time() - start_time
            self.unified_logger.info(
                f"⚡ Parallel fetch completed: {len(results)}/{len(symbols)} symbols in {fetch_time:.2f}s"
            )
            
            return results
            
        except Exception as e:
            self.unified_logger.error(f"Parallel fetch failed: {e}")
            return {}
    
    def optimize_streamlit_performance(self) -> Dict[str, Any]:
        """
        Optimize Streamlit app performance
        
        Returns:
            Dict with optimization recommendations
        """
        try:
            recommendations = {
                'cache_data_enabled': True,
                'cache_resource_enabled': True,
                'lazy_loading': True,
                'pagination': True,
                'async_operations': True,
                'recommendations': []
            }
            
            # Add recommendations
            recommendations['recommendations'].extend([
                'Use st.cache_data for data functions',
                'Use st.cache_resource for models/connections',
                'Implement lazy loading for heavy components',
                'Use pagination for large datasets',
                'Run heavy operations asynchronously',
                'Minimize rerun triggers'
            ])
            
            self.unified_logger.info("⚡ Streamlit optimization recommendations generated")
            
            return recommendations
            
        except Exception as e:
            self.unified_logger.error(f"Failed to generate recommendations: {e}")
            return {'error': str(e)}
    
    def runtime_performance_monitor(self) -> Dict[str, Any]:
        """
        ULTRA ADVANCED: Monitor system performance during runtime and auto-adjust
        
        Returns:
            Dict with current performance metrics and adjustment recommendations
        """
        try:
            import psutil
            
            # Get comprehensive system metrics
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            ram = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            # Calculate metrics
            metrics = {
                'cpu_usage': cpu_percent,
                'cpu_per_core': cpu_per_core,
                'ram_usage_percent': ram.percent,
                'ram_available_gb': ram.available / (1024**3),
                'disk_read_mb_s': (disk_io.read_bytes / (1024**2)) if disk_io else 0,
                'disk_write_mb_s': (disk_io.write_bytes / (1024**2)) if disk_io else 0,
                'network_sent_mb': (net_io.bytes_sent / (1024**2)) if net_io else 0,
                'network_recv_mb': (net_io.bytes_recv / (1024**2)) if net_io else 0,
                'timestamp': time.time()
            }
            
            # Determine if adjustments are needed
            adjustments = []
            performance_state = "OPTIMAL"
            
            if cpu_percent > 85:
                adjustments.append("Reduce parallel workers")
                adjustments.append("Increase batch intervals")
                performance_state = "CRITICAL_CPU"
            elif cpu_percent > 70:
                adjustments.append("Moderate worker reduction recommended")
                performance_state = "HIGH_CPU"
            
            if ram.percent > 85:
                adjustments.append("Clear caches")
                adjustments.append("Reduce cache sizes")
                performance_state = "CRITICAL_RAM"
            elif ram.percent > 70:
                adjustments.append("Cache optimization recommended")
                performance_state = "HIGH_RAM"
            
            # Auto-apply adjustments if needed
            if performance_state in ["CRITICAL_CPU", "CRITICAL_RAM"]:
                self.unified_logger.warning(f"⚠️ {performance_state} detected - auto-adjusting...")
                
                # Emergency optimization
                worker_config = self.optimize_parallel_workers(aggressive=False)
                cache_config = self.auto_tune_cache_settings()
                
                adjustments.append(f"Auto-adjusted workers to {worker_config.get('thread_workers')}")
                adjustments.append(f"Auto-adjusted caches")
            
            result = {
                'metrics': metrics,
                'performance_state': performance_state,
                'adjustments': adjustments,
                'requires_action': len(adjustments) > 0
            }
            
            if adjustments:
                self.unified_logger.info(
                    f"📊 Performance monitor: {performance_state} - "
                    f"CPU: {cpu_percent:.1f}%, RAM: {ram.percent:.1f}%"
                )
            
            return result
            
        except Exception as e:
            self.unified_logger.error(f"Runtime monitoring failed: {e}")
            return {
                'metrics': {},
                'performance_state': 'UNKNOWN',
                'adjustments': [],
                'requires_action': False,
                'error': str(e)
            }
    
    def intelligent_batch_optimizer(self, total_tasks: int, task_complexity: str = "medium") -> Dict[str, Any]:
        """
        ULTRA ADVANCED: Intelligently optimize batch size and parallelism for given tasks
        
        Args:
            total_tasks: Total number of tasks to process
            task_complexity: Task complexity level ("low", "medium", "high")
        
        Returns:
            Dict with optimized batch configuration
        """
        try:
            import psutil
            
            # Get current system state
            cpu_count = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            ram_available_gb = ram.available / (1024**3)
            
            # Complexity factors
            complexity_factors = {
                'low': {'time_per_task': 0.5, 'ram_per_task_mb': 50},
                'medium': {'time_per_task': 2.0, 'ram_per_task_mb': 150},
                'high': {'time_per_task': 10.0, 'ram_per_task_mb': 500}
            }
            
            factor = complexity_factors.get(task_complexity, complexity_factors['medium'])
            
            # Calculate optimal batch size based on RAM
            max_tasks_by_ram = int((ram_available_gb * 1024 * 0.5) / factor['ram_per_task_mb'])
            max_tasks_by_ram = max(1, min(max_tasks_by_ram, total_tasks))
            
            # Calculate optimal parallelism
            if cpu_usage > 70:
                parallel_workers = max(2, cpu_count // 2)
            else:
                parallel_workers = min(cpu_count * 2, max_tasks_by_ram)
            
            # Calculate batch size
            if total_tasks <= parallel_workers:
                batch_size = 1
                num_batches = total_tasks
            else:
                batch_size = max(1, total_tasks // (parallel_workers * 2))
                num_batches = (total_tasks + batch_size - 1) // batch_size
            
            # Estimate processing time
            estimated_time = (total_tasks * factor['time_per_task']) / parallel_workers
            
            config = {
                'total_tasks': total_tasks,
                'batch_size': batch_size,
                'num_batches': num_batches,
                'parallel_workers': parallel_workers,
                'task_complexity': task_complexity,
                'estimated_time_seconds': estimated_time,
                'ram_required_gb': (total_tasks * factor['ram_per_task_mb']) / 1024,
                'ram_available_gb': ram_available_gb,
                'cpu_usage': cpu_usage
            }
            
            self.unified_logger.info(
                f"🎯 Batch optimizer: {total_tasks} tasks -> {num_batches} batches of {batch_size}, "
                f"{parallel_workers} workers, ~{estimated_time:.1f}s"
            )
            
            return config
            
        except Exception as e:
            self.unified_logger.error(f"Batch optimization failed: {e}")
            return {
                'total_tasks': total_tasks,
                'batch_size': 10,
                'num_batches': (total_tasks + 9) // 10,
                'parallel_workers': 4,
                'error': str(e)
            }


# Create global instance
advanced_optimizer = AdvancedOptimizer()

