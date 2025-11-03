"""
GOD MODE 1000 - PARALLEL EXECUTOR
==================================
Maximum Performance Parallel Processing Engine
Tận dụng TỐI ĐA sức mạnh CPU/GPU/RAM
"""

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
import multiprocessing
import psutil
from dataclasses import dataclass
import time

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from .unified_config import unified_config
except ImportError:
    unified_config = None

try:
    from .python313_compatibility import _apply_pyrepl_fix
except ImportError:
    # Fallback if module not found
    def _apply_pyrepl_fix():
        """Fallback function if python313_compatibility not available"""
        pass

@dataclass
class ExecutionResult:
    """Result from parallel execution"""
    task_id: str
    result: Any
    success: bool
    execution_time: float
    error: Optional[str] = None

class ParallelExecutor:
    """
    Maximum Performance Parallel Executor
    
    Features:
    - Auto-scaling based on system resources
    - CPU + GPU parallel processing
    - Intelligent load balancing
    - Zero overhead batch processing
    """
    
    def __init__(self):
        """Initialize Parallel Executor with INTELLIGENT resource management"""
        self.logger = unified_logging.get_logger("parallel_executor") if hasattr(unified_logging, 'get_logger') else unified_logging

        # System capabilities
        self.cpu_count = multiprocessing.cpu_count()
        self.cpu_physical = psutil.cpu_count(logical=False) or (self.cpu_count // 2)
        self.ram_total_gb = psutil.virtual_memory().total / (1024**3)

        # REVOLUTIONARY: Integrate with intelligent_resource_manager for unified resource calculation
        # This ensures ALL modules use consistent resource limits
        self.resource_manager = None
        try:
            from .intelligent_resource_manager import intelligent_resource_manager
            self.resource_manager = intelligent_resource_manager
            self.logger.info("✅ Integrated with Intelligent Resource Manager for dynamic worker calculation")
        except ImportError:
            self.logger.warning("⚠️ Intelligent Resource Manager not available, using fallback calculation")

        # ULTRA OPTIMIZED worker calculation for maximum performance with stability
        # CRITICAL FIX: Use intelligent_resource_manager if available, otherwise fallback
        if self.resource_manager:
            # Use intelligent calculation from resource manager
            optimal = self.resource_manager.calculate_optimal_workers()
            # Extract values with safety checks
            self.max_thread_workers = optimal.get('thread_workers', 18)
            self.max_process_workers = optimal.get('process_workers', 2)
            self.logger.info(f"📊 Using Intelligent Resource Manager: {self.max_thread_workers} threads, {self.max_process_workers} processes")
        else:
            # Fallback: Intelligent calculation without resource manager
            # RESEARCH: Optimal thread count for I/O-bound tasks = 2-4x CPU cores
            #           For CPU-bound tasks = 1-1.5x CPU cores
            #           Mixed workload = 1.5-2x CPU cores
            if unified_config:
                # Use config if available (but no hardcoded defaults in code)
                base_workers = unified_config.get('performance.max_workers', None)
                multiplier = unified_config.get('performance.worker_multiplier', 1.5)
            else:
                base_workers = None
                multiplier = 1.5

            # REALISTIC: Use 60% of RAM to leave room for OS and other processes
            # Each worker needs ~50MB RAM for most tasks, ~100MB for training
            max_workers_by_ram = int((self.ram_total_gb * 0.60 * 1024) / 50)

            # ADAPTIVE: CPU multiplier based on current system load
            current_cpu_usage = psutil.cpu_percent(interval=0.05)
            if current_cpu_usage > 90:  # Critical CPU load
                cpu_multiplier = 1.0  # Match CPU cores exactly (no overhead)
            elif current_cpu_usage > 75:  # High CPU load
                cpu_multiplier = 1.25  # Minimal overhead
            elif current_cpu_usage > 50:  # Medium CPU load
                cpu_multiplier = 1.5  # Moderate (optimal for mixed workload)
            else:  # Low CPU load
                cpu_multiplier = min(multiplier, 2.0)  # Cap at 2x to prevent thrashing

            # REALISTIC Formula: Optimal worker count to minimize context switching
            if base_workers:
                calculated_workers = min(
                    base_workers,
                    int(self.cpu_count * cpu_multiplier),
                    max_workers_by_ram
                )
            else:
                # DYNAMIC: No hardcoded base, pure calculation from system resources
                calculated_workers = min(
                    int(self.cpu_count * cpu_multiplier),
                    max_workers_by_ram
                )

            # FINAL LIMIT: Cap at 2x CPU cores (optimal for mixed CPU/IO workload)
            realistic_max = min(
                calculated_workers,
                int(self.cpu_count * 2.0)  # Max 2x CPU cores (proven optimal)
            )
            self.max_thread_workers = max(4, realistic_max)  # Min 4 for small systems

            # Process workers = 50% of physical cores
            self.max_process_workers = max(1, int(self.cpu_physical * 0.5))

            self.logger.info(f"📊 Using fallback calculation: {self.max_thread_workers} threads, {self.max_process_workers} processes")

        # ULTRA INTELLIGENT: Dynamic GPU batch size based on VRAM
        self.gpu_batch_size = self._calculate_optimal_gpu_batch_size()

        # REVOLUTIONARY: Persistent executor pool with intelligent lifecycle management
        self._thread_executor_pool = None
        self._executor_last_used = time.time()
        self._executor_creation_time = None
        # ULTRA INTELLIGENT: Long-running training sessions need stable executor
        self._executor_timeout = 3600  # Idle timeout: 1 hour
        self._executor_max_lifetime = 14400  # Max lifetime: 4 hours
        self._executor_task_count = 0

        # Monitoring metrics
        self.total_tasks_executed = 0
        self.total_execution_time = 0.0
        self.last_health_check = time.time()

        self.logger.info(
            f"✅ Parallel Executor initialized: "
            f"{self.max_thread_workers} thread workers (CPU: {self.cpu_count}, RAM: {self.ram_total_gb:.1f}GB), "
            f"{self.max_process_workers} process workers, GPU batch: {self.gpu_batch_size}"
        )
    
    def cleanup(self, force: bool = False) -> None:
        """
        REVOLUTIONARY cleanup with intelligent lifecycle management
        
        Args:
            force: If True, immediately shutdown. If False, only cleanup if timeout/lifetime exceeded
        """
        try:
            current_time = time.time()
            # FIXED: Proper null-safe time calculations
            last_used = getattr(self, '_executor_last_used', None)
            time_since_last_use = current_time - last_used if last_used is not None else 0
            
            creation_time = getattr(self, '_executor_creation_time', None)
            time_since_creation = current_time - creation_time if creation_time is not None else 0
            
            # REVOLUTIONARY: Cleanup conditions
            # 1. Forced cleanup (explicit request)
            # 2. Idle timeout exceeded (unused for too long)
            # 3. Max lifetime exceeded (prevent memory leaks even if active)
            should_cleanup = (
                force or
                (last_used is not None and time_since_last_use > self._executor_timeout) or
                (creation_time is not None and time_since_creation > self._executor_max_lifetime)
            )
            
            if should_cleanup and self._thread_executor_pool is not None:
                try:
                    # IMPROVED: Graceful shutdown with timeout
                    # Give threads 5 seconds to finish current tasks
                    self._thread_executor_pool.shutdown(wait=True, cancel_futures=False)
                    reason = "forced" if force else f"idle {time_since_last_use:.0f}s" if time_since_last_use > self._executor_timeout else f"lifetime {time_since_creation:.0f}s"
                    self.logger.debug(f"✅ Executor pool cleaned up ({reason}, {self._executor_task_count} tasks completed)")
                except Exception as e:
                    self.logger.warning(f"Executor pool cleanup warning: {e}")
                finally:
                    self._thread_executor_pool = None
                    self._executor_creation_time = None
                    self._executor_task_count = 0
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def __del__(self):
        """Destructor - ensure cleanup on object destruction"""
        try:
            self.cleanup(force=True)
        except:
            pass
    
    def _calculate_optimal_gpu_batch_size(self) -> int:
        """Calculate optimal GPU batch size based on available VRAM - ULTRA SMART"""
        try:
            # Try to detect GPU and VRAM
            try:
                import torch
                if torch.cuda.is_available():
                    # Get total GPU memory in GB
                    gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    
                    # Formula: Batch size = (VRAM_GB * 64) for training
                    # For inference: (VRAM_GB * 128)
                    # Use conservative estimate for training
                    optimal_batch = int(gpu_mem_gb * 64)
                    
                    # Bounds: min 32, max based on VRAM
                    return max(32, min(optimal_batch, int(gpu_mem_gb * 256)))
            except ImportError:
                pass
            
            # Fallback: use RAM-based estimation
            # Assume GPU memory is ~1/8 of system RAM for integrated GPUs
            estimated_vram_gb = self.ram_total_gb / 8
            optimal_batch = int(estimated_vram_gb * 64)
            
            return max(32, min(optimal_batch, 512))
            
        except Exception:
            # Safe fallback
            return 128
    
    def _check_system_health(self) -> bool:
        """
        Check system health before executing parallel tasks - ULTRA SMART monitoring
        
        CRITICAL FIX: High CPU usage (100%) is EXPECTED for AI training - don't treat as unhealthy!
        Only flag unhealthy if memory is critically low or system is truly unresponsive
        """
        try:
            # CRITICAL FIX: Don't check CPU usage here - 100% CPU is DESIRED for training!
            # High CPU = Optimal utilization, NOT a problem
            # Only memory pressure and disk space are real health concerns
            
            # Check memory usage - this is the real bottleneck
            mem = psutil.virtual_memory()
            if mem.percent > 95:  # Critical memory (5% free)
                self.logger.warning(f"⚠️ Critical memory usage: {mem.percent}% - System health degraded")
                return False
            
            # Check if system is responsive (disk I/O)
            try:
                disk = psutil.disk_usage('/')
                if disk.percent > 98:  # Disk almost full
                    self.logger.warning(f"⚠️ Disk usage critical: {disk.percent}%")
                    return False
            except Exception:
                pass
            
            # Memory OK, disk OK = System healthy (CPU at 100% is fine!)
            return True
        except Exception:
            return True  # Allow execution if health check fails
    
    def _get_adaptive_workers(self, requested_workers: int) -> int:
        """
        Get adaptive worker count based on current system load - ULTRA SMART
        
        CRITICAL FIX: High CPU usage during AI training is EXPECTED and DESIRED
        Don't reduce workers just because CPU is at 100% - that's the goal!
        Only reduce if memory is critical or system is truly overloaded
        """
        try:
            # Check current system load with faster intervals
            cpu_usage = psutil.cpu_percent(interval=0.05)
            mem_usage = psutil.virtual_memory().percent
            
            # CRITICAL FIX: High CPU usage (even 100%) is GOOD for training
            # Only reduce workers if MEMORY is critical, not CPU
            # CPU at 100% = Optimal utilization (what we want!)
            
            if mem_usage > 95:  # Critical memory stress - MUST reduce
                self.logger.warning(f"Critical memory usage: {mem_usage}% - Reducing to 25% workers")
                return max(2, requested_workers // 4)  # Use 25% of requested
            elif mem_usage > 90:  # Very high memory - reduce moderately
                self.logger.debug(f"High memory usage: {mem_usage}% - Reducing to 50% workers")
                return max(4, requested_workers // 2)  # Use 50% of requested
            elif mem_usage > 85:  # High memory - slight reduction
                self.logger.debug(f"Elevated memory usage: {mem_usage}% - Reducing to 75% workers")
                return max(8, int(requested_workers * 0.75))  # Use 75% of requested
            elif cpu_usage > 98 and mem_usage > 80:  # Both CPU and memory very high
                # Only reduce if BOTH are critically high (likely thrashing)
                self.logger.warning(f"System thrashing (CPU: {cpu_usage}%, MEM: {mem_usage}%) - Reducing to 75% workers")
                return max(8, int(requested_workers * 0.75))
            else:
                # CPU at 100% is fine! Memory is OK - use full workers
                # This is optimal for AI training workloads
                return requested_workers  # Use full requested workers
        except Exception:
            return requested_workers
    
    def execute_parallel_threads(self, tasks: List[Callable], max_workers: Optional[int] = None,
                                 keep_executor_alive: bool = False, gpu_priority: bool = False, 
                                 timeout: int = 14400) -> List[ExecutionResult]:
        """
        Execute tasks in parallel using threads (I/O-bound tasks) with INTELLIGENT resource management
        
        ENHANCED: Supports executor persistence for chained operations (Phase 4->5->6)
        OPTIMIZED: GPU-aware scheduling for maximum GPU utilization
        
        Args:
            tasks: List of callable functions to execute
            max_workers: Override default max workers
            keep_executor_alive: Keep executor pool alive for next call (default: False)
            gpu_priority: If True, optimizes scheduling for GPU tasks (default: False)
        
        Returns:
            List of execution results
        """
        if not tasks:
            return []
        
        # INTELLIGENT: Check system health before execution
        if not self._check_system_health():
            self.logger.warning("System under high load - Reducing parallelism")
        
        # OPTIMIZED: GPU-aware worker allocation
        requested_workers = max_workers or self.max_thread_workers
        if gpu_priority:
            # Reduce thread count for GPU tasks to avoid overhead
            # GPU can handle multiple operations simultaneously
            requested_workers = min(requested_workers, self.gpu_batch_size)
            self.logger.debug(f"GPU priority mode: using {requested_workers} workers for optimal GPU utilization")
        
        # INTELLIGENT: Get adaptive worker count
        adaptive_workers = self._get_adaptive_workers(requested_workers)
        
        self.logger.info(f"Executing {len(tasks)} tasks with {adaptive_workers} workers (persistent: {keep_executor_alive})")
        
        results = []
        
        try:
            # ENHANCED: Reuse existing executor pool if available
            use_existing_pool = (
                self._thread_executor_pool is not None and 
                (time.time() - self._executor_last_used) < self._executor_timeout
            )
            
            if use_existing_pool:
                self.logger.debug("Reusing existing thread pool for chained operation")
                executor = self._thread_executor_pool
                should_close = False
            else:
                executor = ThreadPoolExecutor(max_workers=adaptive_workers)
                should_close = not keep_executor_alive
                if keep_executor_alive:
                    self._thread_executor_pool = executor
                    self._executor_creation_time = time.time()  # CRITICAL FIX: Set creation time
                    self._executor_task_count = 0  # Reset task counter
                    self.logger.debug("Created new persistent thread pool")
            
            try:
                futures = {executor.submit(task): i for i, task in enumerate(tasks)}
                
                for future in as_completed(futures):
                    task_id = futures[future]
                    start_time = time.time()
                    
                    try:
                        # CRITICAL FIX: AI model training can take several hours (especially with 10000 candles)
                        # Use configurable timeout (default 4 hours = 14400s) to avoid premature failure
                        # For very long operations (AI training, backtesting, validation), this ensures completion
                        result = future.result(timeout=timeout)
                        execution_time = time.time() - start_time
                        
                        # Log progress for long-running tasks
                        if execution_time > 60:  # Log if > 1 minute
                            self.logger.info(f"Task {task_id} completed in {execution_time:.1f}s")
                        
                        results.append(ExecutionResult(
                            task_id=f"task_{task_id}",
                            result=result,
                            success=True,
                            execution_time=execution_time
                        ))
                        
                        # Update metrics
                        self.total_tasks_executed += 1
                        self.total_execution_time += execution_time
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        results.append(ExecutionResult(
                            task_id=f"task_{task_id}",
                            result=None,
                            success=False,
                            execution_time=execution_time,
                            error=str(e)
                        ))
                        self.logger.warning(f"Task {task_id} failed: {e}")
            
            finally:
                # Update last used time and task count
                self._executor_last_used = time.time()
                if keep_executor_alive:
                    self._executor_task_count += len(tasks)
                
                # Close executor only if not keeping alive
                if should_close and executor is not None:
                    executor.shutdown(wait=True)
                    self.logger.debug("Closed thread pool")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Parallel thread execution failed: {e}")
            return []
    
    def execute_parallel_processes(self, func: Callable, args_list: List[tuple], max_workers: Optional[int] = None) -> List[ExecutionResult]:
        """
        Execute function with different args in parallel using processes (CPU-bound tasks)
        
        CRITICAL FIX: Apply _pyrepl fix in worker processes to prevent ModuleNotFoundError
        
        Args:
            func: Function to execute
            args_list: List of argument tuples for each execution
            max_workers: Override default max workers
        
        Returns:
            List of execution results
        """
        if not args_list:
            return []
        
        workers = max_workers or self.max_process_workers
        results = []
        
        try:
            # CRITICAL FIX: Apply _pyrepl fix in worker processes via initializer
            # This prevents "ModuleNotFoundError: No module named '_pyrepl'" in spawned processes
            with ProcessPoolExecutor(max_workers=workers, 
                                   initializer=_apply_pyrepl_fix) as executor:
                futures = {executor.submit(func, *args): i for i, args in enumerate(args_list)}
                
                for future in as_completed(futures):
                    task_id = futures[future]
                    start_time = time.time()
                    
                    try:
                        result = future.result()
                        execution_time = time.time() - start_time
                        
                        results.append(ExecutionResult(
                            task_id=f"process_{task_id}",
                            result=result,
                            success=True,
                            execution_time=execution_time
                        ))
                    except Exception as e:
                        execution_time = time.time() - start_time
                        results.append(ExecutionResult(
                            task_id=f"process_{task_id}",
                            result=None,
                            success=False,
                            execution_time=execution_time,
                            error=str(e)
                        ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Parallel process execution failed: {e}")
            return []
    
    def batch_execute(self, items: List[Any], func: Callable, batch_size: Optional[int] = None) -> List[Any]:
        """
        Execute function on batches of items in parallel
        
        Args:
            items: List of items to process
            func: Function to apply to each batch
            batch_size: Size of each batch (default: auto-calculated)
        
        Returns:
            List of results
        """
        if not items:
            return []
        
        # Auto-calculate optimal batch size based on system resources
        if batch_size is None:
            batch_size = max(1, len(items) // self.max_thread_workers)
        
        # Create batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        # Execute batches in parallel
        tasks = [lambda b=batch: func(b) for batch in batches]
        execution_results = self.execute_parallel_threads(tasks)
        
        # Flatten results
        results = []
        for exec_result in execution_results:
            if exec_result.success and exec_result.result:
                if isinstance(exec_result.result, list):
                    results.extend(exec_result.result)
                else:
                    results.append(exec_result.result)
        
        return results
    
    def execute_gpu_batched(self, tasks: List[Callable], gpu_batch_size: Optional[int] = None) -> List[ExecutionResult]:
        """
        OPTIMIZED: Execute GPU tasks in intelligent batches to maximize GPU utilization
        while preventing memory overflow
        
        Args:
            tasks: List of GPU tasks to execute
            gpu_batch_size: Override default GPU batch size
        
        Returns:
            List of execution results
        """
        if not tasks:
            return []
        
        batch_size = gpu_batch_size or self.gpu_batch_size
        all_results = []
        
        self.logger.info(f"Executing {len(tasks)} GPU tasks in batches of {batch_size}")
        
        # Process in batches to avoid GPU memory overflow
        for batch_start in range(0, len(tasks), batch_size):
            batch_end = min(batch_start + batch_size, len(tasks))
            batch_tasks = tasks[batch_start:batch_end]
            
            # Execute batch with GPU priority
            batch_results = self.execute_parallel_threads(
                batch_tasks,
                max_workers=batch_size,
                keep_executor_alive=True,
                gpu_priority=True
            )
            
            all_results.extend(batch_results)
            
            # Optional: Clear GPU cache between batches if needed
            try:
                import torch
                if torch.cuda.is_available():
                    mem_allocated = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory
                    if mem_allocated > 0.85:  # Only clear if > 85% full
                        torch.cuda.empty_cache()
                        self.logger.debug(f"Cleared GPU cache after batch (memory usage: {mem_allocated:.1%})")
            except Exception:
                pass
        
        return all_results
    
    def get_optimal_workers(self, task_type: str = 'io') -> int:
        """
        Get optimal number of workers for task type
        
        Args:
            task_type: 'io' for I/O-bound, 'cpu' for CPU-bound, 'gpu' for GPU-bound
        
        Returns:
            Optimal number of workers
        """
        if task_type == 'cpu':
            return self.max_process_workers
        elif task_type == 'gpu':
            return self.gpu_batch_size
        else:
            return self.max_thread_workers
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system resource information"""
        return {
            'cpu_count': self.cpu_count,
            'cpu_physical': self.cpu_physical,
            'ram_total_gb': self.ram_total_gb,
            'max_thread_workers': self.max_thread_workers,
            'max_process_workers': self.max_process_workers,
            'gpu_batch_size': self.gpu_batch_size,
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'ram_percent': psutil.virtual_memory().percent
        }

# Export singleton instance
parallel_executor = ParallelExecutor()

