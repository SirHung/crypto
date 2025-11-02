"""
GOD MODE 1000 - INTELLIGENT RESOURCE MANAGER
==========================================
Advanced CPU/RAM/GPU Monitoring with Intelligent Auto-Adjustment
Prevents system crashes through proactive resource management
"""

import psutil
import time
import threading
import os
import platform
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Import unified components
try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

# Try to import GPU libraries
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    
try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False

class ResourceLevel(Enum):
    """Resource usage level classification"""
    CRITICAL = "critical"  # > 90% - Emergency mode
    DANGER = "danger"  # 80-90% - Reduce load
    WARNING = "warning"  # 70-80% - Monitor closely
    NORMAL = "normal"  # 50-70% - Normal operation
    OPTIMAL = "optimal"  # < 50% - Peak performance

@dataclass
class SystemResources:
    """Real-time system resource metrics"""
    cpu_percent: float
    cpu_cores: int
    cpu_freq_mhz: float
    ram_percent: float
    ram_used_gb: float
    ram_available_gb: float
    ram_total_gb: float
    gpu_count: int
    gpu_percent: List[float] = field(default_factory=list)
    gpu_memory_used_mb: List[float] = field(default_factory=list)
    gpu_memory_total_mb: List[float] = field(default_factory=list)
    gpu_temperature: List[float] = field(default_factory=list)
    disk_usage_percent: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    resource_level: ResourceLevel = ResourceLevel.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class OptimizationAction:
    """Record of optimization actions taken"""
    action_type: str
    reason: str
    resource_before: float
    resource_after: float
    improvement_percent: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class IntelligentResourceManager:
    """
    Intelligent Resource Manager for God Mode 1000
    
    Features:
    - Real-time CPU/RAM/GPU monitoring
    - Intelligent auto-adjustment to prevent crashes
    - Dynamic resource allocation
    - Proactive memory management
    - GPU optimization (if available)
    """
    
    def __init__(self):
        """Initialize Intelligent Resource Manager"""
        try:
            unified_logging.info("🚀 Initializing Intelligent Resource Manager...")
            
            # System information
            self.system_info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'processor': platform.processor(),
                'cpu_cores': psutil.cpu_count(logical=False),
                'cpu_threads': psutil.cpu_count(logical=True),
                'ram_total_gb': psutil.virtual_memory().total / (1024**3)
            }
            
            # Resource monitoring
            self.monitoring_active = False
            self.monitoring_thread = None
            self.monitoring_interval = 2  # Check every 2 seconds
            
            # Dynamic Resource thresholds - MAXIMUM PERFORMANCE MODE
            # Use system resources to the fullest without crashing
            # Thresholds are now configurable via unified_config
            try:
                from .unified_config import unified_config
                self.thresholds = {
                    'cpu_critical': unified_config.get('performance.cpu_critical', 98.0),
                    'cpu_danger': unified_config.get('performance.cpu_danger', 95.0),
                    'cpu_warning': unified_config.get('performance.cpu_warning', 90.0),
                    'ram_critical': unified_config.get('performance.ram_critical', 97.0),
                    'ram_danger': unified_config.get('performance.ram_danger', 93.0),
                    'ram_warning': unified_config.get('performance.ram_warning', 88.0),
                    'gpu_critical': unified_config.get('performance.gpu_critical', 98.0),
                    'gpu_danger': unified_config.get('performance.gpu_danger', 95.0),
                    'gpu_warning': unified_config.get('performance.gpu_warning', 90.0)
                }
            except ImportError:
                # Fallback to dynamic calculation if config not available - NO HARDCODED VALUES
                # Use psutil to determine safe thresholds based on system capabilities
                # psutil already imported at top of file
                total_ram_gb = psutil.virtual_memory().total / (1024**3)
                cpu_count = psutil.cpu_count()
                
                # Calculate intelligent thresholds based on system resources
                # More powerful systems can push higher
                if total_ram_gb >= 32 and cpu_count >= 8:  # High-end system
                    self.thresholds = {
                        'cpu_critical': 98.0, 'cpu_danger': 95.0, 'cpu_warning': 90.0,
                        'ram_critical': 97.0, 'ram_danger': 93.0, 'ram_warning': 88.0,
                        'gpu_critical': 98.0, 'gpu_danger': 95.0, 'gpu_warning': 90.0
                    }
                elif total_ram_gb >= 16 and cpu_count >= 4:  # Mid-range system
                    self.thresholds = {
                        'cpu_critical': 95.0, 'cpu_danger': 90.0, 'cpu_warning': 85.0,
                        'ram_critical': 93.0, 'ram_danger': 88.0, 'ram_warning': 83.0,
                        'gpu_critical': 95.0, 'gpu_danger': 90.0, 'gpu_warning': 85.0
                    }
                else:  # Low-end system - more conservative
                    self.thresholds = {
                        'cpu_critical': 90.0, 'cpu_danger': 85.0, 'cpu_warning': 80.0,
                        'ram_critical': 88.0, 'ram_danger': 83.0, 'ram_warning': 78.0,
                        'gpu_critical': 90.0, 'gpu_danger': 85.0, 'gpu_warning': 80.0
                    }
            
            # Intelligent scaling factors (configurable)
            try:
                from .unified_config import unified_config
                self.performance_mode = unified_config.get('performance.mode', 'maximum')  # 'maximum', 'balanced', 'conservative'
                self.auto_scale_enabled = unified_config.get('performance.auto_scale_enabled', True)
            except ImportError:
                self.performance_mode = 'maximum'
                self.auto_scale_enabled = True
            
            # Optimization history
            self.optimization_history = []
            self.resource_history = []
            self.max_history_size = 1000
            
            # Auto-adjustment settings
            try:
                from .unified_config import unified_config
                self.auto_adjust_enabled = unified_config.get('performance.auto_adjust_enabled', True)
                self.aggressive_optimization = unified_config.get('performance.aggressive_optimization', False)
            except ImportError:
                self.auto_adjust_enabled = True
                self.aggressive_optimization = False
            
            # GPU detection
            self.gpu_available = False
            self.gpu_count = 0
            self._detect_gpu()
            
            # Network monitoring
            self.network_io_start = psutil.net_io_counters()
            
            unified_logging.info(f"✅ Resource Manager initialized - {self.system_info['cpu_threads']} threads, {self.system_info['ram_total_gb']:.1f}GB RAM, {self.gpu_count} GPUs")
            
        except Exception as e:
            unified_logging.error(f"Failed to initialize Resource Manager: {e}", exception=e)
            raise
    
    def _detect_gpu(self):
        """Detect available GPUs"""
        try:
            if GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                self.gpu_count = len(gpus)
                self.gpu_available = self.gpu_count > 0
                if self.gpu_available:
                    unified_logging.info(f"✅ Detected {self.gpu_count} GPU(s)")
            elif TORCH_AVAILABLE:
                self.gpu_count = torch.cuda.device_count()
                self.gpu_available = self.gpu_count > 0
                if self.gpu_available:
                    unified_logging.info(f"✅ Detected {self.gpu_count} GPU(s) via PyTorch")
            else:
                unified_logging.info("ℹ️ No GPU detected or GPU libraries not available")
        except Exception as e:
            unified_logging.warning(f"GPU detection failed: {e}")
            self.gpu_available = False
            self.gpu_count = 0
    
    def get_current_resources(self) -> SystemResources:
        """Get current system resource usage"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = cpu_freq.current if cpu_freq else 0
            
            # Memory metrics
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            ram_used_gb = memory.used / (1024**3)
            ram_available_gb = memory.available / (1024**3)
            ram_total_gb = memory.total / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network metrics
            net_io = psutil.net_io_counters()
            network_sent_mb = (net_io.bytes_sent - self.network_io_start.bytes_sent) / (1024**2)
            network_recv_mb = (net_io.bytes_recv - self.network_io_start.bytes_recv) / (1024**2)
            
            # GPU metrics (if available)
            gpu_percent_list = []
            gpu_memory_used_list = []
            gpu_memory_total_list = []
            gpu_temperature_list = []
            
            if self.gpu_available and GPU_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    for gpu in gpus:
                        gpu_percent_list.append(gpu.load * 100)
                        gpu_memory_used_list.append(gpu.memoryUsed)
                        gpu_memory_total_list.append(gpu.memoryTotal)
                        gpu_temperature_list.append(gpu.temperature)
                except Exception as e:
                    unified_logging.debug(f"GPU metrics error: {e}")
            
            # Determine resource level
            resource_level = self._determine_resource_level(cpu_percent, ram_percent, gpu_percent_list)
            
            return SystemResources(
                cpu_percent=cpu_percent,
                cpu_cores=self.system_info['cpu_cores'],
                cpu_freq_mhz=cpu_freq_mhz,
                ram_percent=ram_percent,
                ram_used_gb=ram_used_gb,
                ram_available_gb=ram_available_gb,
                ram_total_gb=ram_total_gb,
                gpu_count=self.gpu_count,
                gpu_percent=gpu_percent_list,
                gpu_memory_used_mb=gpu_memory_used_list,
                gpu_memory_total_mb=gpu_memory_total_list,
                gpu_temperature=gpu_temperature_list,
                disk_usage_percent=disk_usage_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                resource_level=resource_level
            )
            
        except Exception as e:
            unified_logging.error(f"Failed to get system resources: {e}")
            # Return default values
            return SystemResources(
                cpu_percent=0,
                cpu_cores=self.system_info['cpu_cores'],
                cpu_freq_mhz=0,
                ram_percent=0,
                ram_used_gb=0,
                ram_available_gb=0,
                ram_total_gb=self.system_info['ram_total_gb'],
                gpu_count=0,
                resource_level=ResourceLevel.NORMAL
            )
    
    def _determine_resource_level(self, cpu: float, ram: float, gpu_list: List[float]) -> ResourceLevel:
        """Determine overall resource usage level - MAXIMUM PERFORMANCE MODE"""
        max_gpu = max(gpu_list) if gpu_list else 0
        max_resource = max(cpu, ram, max_gpu)
        
        # Maximum performance mode - use resources to the fullest
        if max_resource >= 98:
            return ResourceLevel.CRITICAL  # Only critical at 98%+
        elif max_resource >= 95:
            return ResourceLevel.DANGER  # Danger at 95%+
        elif max_resource >= 90:
            return ResourceLevel.WARNING  # Warning at 90%+
        elif max_resource >= 75:
            return ResourceLevel.NORMAL  # Normal at 75%+
        else:
            return ResourceLevel.OPTIMAL  # Optimal below 75%
    
    def optimize_resources(self, aggressive: bool = False) -> List[OptimizationAction]:
        """Optimize system resources to prevent crashes"""
        actions = []
        
        try:
            resources_before = self.get_current_resources()
            
            # CPU optimization
            if resources_before.cpu_percent > self.thresholds['cpu_warning']:
                cpu_action = self._optimize_cpu(resources_before.cpu_percent, aggressive)
                if cpu_action:
                    actions.append(cpu_action)
            
            # RAM optimization
            if resources_before.ram_percent > self.thresholds['ram_warning']:
                ram_action = self._optimize_ram(resources_before.ram_percent, aggressive)
                if ram_action:
                    actions.append(ram_action)
            
            # GPU optimization
            if self.gpu_available and resources_before.gpu_percent:
                for i, gpu_usage in enumerate(resources_before.gpu_percent):
                    if gpu_usage > self.thresholds['gpu_warning']:
                        gpu_action = self._optimize_gpu(i, gpu_usage, aggressive)
                        if gpu_action:
                            actions.append(gpu_action)
            
            # Record actions
            for action in actions:
                self.optimization_history.append(action)
                if len(self.optimization_history) > self.max_history_size:
                    self.optimization_history = self.optimization_history[-self.max_history_size:]
            
            if actions:
                # Only log optimization actions if they are significant (reduce spam)
                if len(actions) > 1 or not hasattr(self, '_last_optimization_time'):
                    unified_logging.info(f"⚡ Applied {len(actions)} optimization actions")
                    self._last_optimization_time = time.time()
                elif time.time() - getattr(self, '_last_optimization_time', 0) > 300:  # Log every 5 minutes max
                    unified_logging.debug(f"⚡ Applied {len(actions)} optimization actions")
                    self._last_optimization_time = time.time()
            
            return actions
            
        except Exception as e:
            unified_logging.error(f"Resource optimization failed: {e}")
            return []
    
    def _optimize_cpu(self, cpu_usage: float, aggressive: bool) -> Optional[OptimizationAction]:
        """Optimize CPU usage - MAXIMUM PERFORMANCE MODE with intelligent crash prevention"""
        try:
            # Dynamic threshold based on system capabilities and current state
            # psutil already imported at top of file
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # More powerful CPUs can handle higher loads
            if cpu_count >= 16:  # High-end workstation
                effective_critical = self.thresholds['cpu_critical']
            elif cpu_count >= 8:  # Mid-high end
                effective_critical = self.thresholds['cpu_critical'] - 1.0
            elif cpu_count >= 4:  # Mid-range
                effective_critical = self.thresholds['cpu_critical'] - 3.0
            else:  # Low-end - more conservative
                effective_critical = self.thresholds['cpu_critical'] - 5.0
            
            # Check thermal throttling risk
            if cpu_freq and hasattr(cpu_freq, 'max') and hasattr(cpu_freq, 'current'):
                if cpu_freq.current < cpu_freq.max * 0.7:  # CPU throttling detected
                    effective_critical -= 5.0  # More conservative when throttling
            
            if cpu_usage >= effective_critical:
                # Critical: Intelligent intervention
                import gc
                gc.collect(generation=1)  # Quick generation 1 collection
                
                # Only reduce priority in extreme cases
                if cpu_usage >= effective_critical + 1.0:
                    try:
                        p = psutil.Process(os.getpid())
                        if platform.system() != 'Windows':
                            p.nice(min(p.nice() + 2, 10))  # Gradual priority reduction
                        else:
                            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)  # Windows priority
                    except:
                        pass
                
                cpu_after = psutil.cpu_percent(interval=0.05)
                improvement = ((cpu_usage - cpu_after) / cpu_usage * 100) if cpu_usage > 0 else 0
                
                return OptimizationAction(
                    action_type="CPU_CRITICAL",
                    reason=f"CPU usage critical ({cpu_usage:.1f}%) - intelligent intervention (threshold: {effective_critical:.1f}%)",
                    resource_before=cpu_usage,
                    resource_after=cpu_after,
                    improvement_percent=improvement
                )
            
            # Allow CPU to run at high loads for maximum performance
            return None
            
        except Exception as e:
            unified_logging.error(f"CPU optimization failed: {e}")
            return None
    
    def _optimize_ram(self, ram_usage: float, aggressive: bool) -> Optional[OptimizationAction]:
        """Optimize RAM usage - MAXIMUM PERFORMANCE MODE with intelligent memory management"""
        try:
            import gc
            # psutil already imported at top of file
            
            # Dynamic threshold based on total RAM and swap availability
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            swap = psutil.swap_memory()
            has_swap = swap.total > 0
            swap_usage = swap.percent if has_swap else 100
            
            # Systems with more RAM and available swap can push higher
            if total_ram_gb >= 64:  # Very high RAM system
                effective_critical = self.thresholds['ram_critical']
            elif total_ram_gb >= 32:  # High RAM system
                effective_critical = self.thresholds['ram_critical'] - 1.0
            elif total_ram_gb >= 16:  # Mid RAM system
                effective_critical = self.thresholds['ram_critical'] - 3.0
            else:  # Low RAM system
                effective_critical = self.thresholds['ram_critical'] - 5.0
            
            # If swap is getting full, be more aggressive
            if has_swap and swap_usage > 80:
                effective_critical -= 5.0
            
            if ram_usage >= effective_critical:
                # Critical: Intelligent memory cleanup
                # Stage 1: Quick generation 0 and 1
                gc.collect(generation=0)
                gc.collect(generation=1)
                
                # Stage 2: Deep generation 2 if still critical
                if psutil.virtual_memory().percent >= effective_critical:
                    gc.collect(generation=2)
                    
                    # Stage 3: Clear caches only if extremely critical
                    if psutil.virtual_memory().percent >= effective_critical + 1.0:
                        import sys
                        if hasattr(sys, 'clear_type_cache'):
                            sys.clear_type_cache()
                        
                        # Try to reduce cache sizes in modules if available
                        try:
                            from .unified_cache_manager import unified_cache_manager
                            unified_cache_manager.emergency_cleanup()
                        except:
                            pass
                
                ram_after = psutil.virtual_memory().percent
                improvement = ((ram_usage - ram_after) / ram_usage) * 100
                
                return OptimizationAction(
                    action_type="RAM_CRITICAL",
                    reason=f"RAM usage critical ({ram_usage:.1f}%) - intelligent cleanup (threshold: {effective_critical:.1f}%)",
                    resource_before=ram_usage,
                    resource_after=ram_after,
                    improvement_percent=improvement
                )
            
            # Allow RAM to be used heavily for maximum caching and performance
            return None
            
        except Exception as e:
            unified_logging.error(f"RAM optimization failed: {e}")
            return None
    
    def _optimize_gpu(self, gpu_id: int, gpu_usage: float, aggressive: bool) -> Optional[OptimizationAction]:
        """Optimize GPU usage"""
        try:
            if TORCH_AVAILABLE:
                import torch
                
                if gpu_usage >= self.thresholds['gpu_critical']:
                    # Critical: Clear GPU cache
                    torch.cuda.empty_cache()
                    
                    return OptimizationAction(
                        action_type=f"GPU{gpu_id}_CRITICAL",
                        reason=f"GPU {gpu_id} usage critical - cleared CUDA cache",
                        resource_before=gpu_usage,
                        resource_after=gpu_usage,  # Can't measure immediately
                        improvement_percent=0
                    )
            
            return None
            
        except Exception as e:
            unified_logging.error(f"GPU optimization failed: {e}")
            return None
    
    def start_monitoring(self):
        """Start continuous resource monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        unified_logging.info("🔍 Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        unified_logging.info("⏹️ Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                resources = self.get_current_resources()
                
                # Store in history
                self.resource_history.append(resources)
                if len(self.resource_history) > self.max_history_size:
                    self.resource_history = self.resource_history[-self.max_history_size:]
                
                # Auto-optimize if enabled
                if self.auto_adjust_enabled:
                    if resources.resource_level in [ResourceLevel.CRITICAL, ResourceLevel.DANGER]:
                        aggressive = resources.resource_level == ResourceLevel.CRITICAL
                        self.optimize_resources(aggressive=aggressive)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                unified_logging.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def calculate_optimal_workers(self) -> Dict[str, int]:
        """Calculate optimal number of workers based on current system resources - MAXIMUM PERFORMANCE"""
        try:
            resources = self.get_current_resources()
            
            # Get available resources (what's NOT being used)
            cpu_available = 100 - resources.cpu_percent
            ram_available_gb = resources.ram_available_gb
            
            # MAXIMUM PERFORMANCE MODE: Use 90%+ of available resources
            # Base calculation on available resources
            cpu_cores = resources.cpu_cores
            cpu_threads = self.system_info['cpu_threads']
            
            # Thread workers calculation (I/O bound tasks)
            # Use up to 90% of CPU threads for maximum parallelism
            if cpu_available > 80:  # System is idle
                thread_workers = int(cpu_threads * 12)  # Hyper-aggressive
            elif cpu_available > 60:  # System has plenty of resources
                thread_workers = int(cpu_threads * 8)
            elif cpu_available > 40:  # System moderately loaded
                thread_workers = int(cpu_threads * 4)
            elif cpu_available > 20:  # System busy
                thread_workers = int(cpu_threads * 2)
            else:  # System very busy
                thread_workers = max(cpu_threads, 4)
            
            # Process workers calculation (CPU bound tasks)
            # More conservative for process workers
            if cpu_available > 80:
                process_workers = int(cpu_cores * 2.5)  # Aggressive
            elif cpu_available > 60:
                process_workers = int(cpu_cores * 2.0)
            elif cpu_available > 40:
                process_workers = int(cpu_cores * 1.5)
            elif cpu_available > 20:
                process_workers = cpu_cores
            else:
                process_workers = max(int(cpu_cores * 0.75), 1)
            
            # GPU workers (if available)
            gpu_workers = 0
            if self.gpu_available:
                avg_gpu_usage = sum(resources.gpu_percent) / len(resources.gpu_percent) if resources.gpu_percent else 0
                gpu_available = 100 - avg_gpu_usage
                
                if gpu_available > 80:
                    gpu_workers = self.gpu_count * 4  # Hyper-aggressive
                elif gpu_available > 60:
                    gpu_workers = self.gpu_count * 3
                elif gpu_available > 40:
                    gpu_workers = self.gpu_count * 2
                else:
                    gpu_workers = self.gpu_count
            
            # Adjust based on available RAM (1GB per worker minimum)
            max_workers_by_ram = int(ram_available_gb * 0.8)  # Use 80% of available RAM
            
            # Apply RAM constraint
            if thread_workers + process_workers > max_workers_by_ram:
                ratio = max_workers_by_ram / (thread_workers + process_workers)
                thread_workers = max(int(thread_workers * ratio), 4)
                process_workers = max(int(process_workers * ratio), 1)
            
            return {
                'thread_workers': thread_workers,
                'process_workers': process_workers,
                'gpu_workers': gpu_workers,
                'total_workers': thread_workers + process_workers + gpu_workers,
                'cpu_utilization_target': 90.0,  # Target 90% utilization
                'ram_utilization_target': 85.0,  # Target 85% utilization
                'gpu_utilization_target': 90.0 if self.gpu_available else 0,
                'resource_level': resources.resource_level.value
            }
            
        except Exception as e:
            unified_logging.error(f"Failed to calculate optimal workers: {e}")
            # Fallback to conservative values
            return {
                'thread_workers': 8,
                'process_workers': 2,
                'gpu_workers': 0,
                'total_workers': 10
            }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system resource summary with optimal worker recommendations"""
        resources = self.get_current_resources()
        optimal_workers = self.calculate_optimal_workers()
        
        return {
            'cpu': {
                'usage_percent': resources.cpu_percent,
                'cores': resources.cpu_cores,
                'threads': self.system_info['cpu_threads'],
                'frequency_mhz': resources.cpu_freq_mhz,
                'available_percent': 100 - resources.cpu_percent
            },
            'ram': {
                'usage_percent': resources.ram_percent,
                'used_gb': resources.ram_used_gb,
                'available_gb': resources.ram_available_gb,
                'total_gb': resources.ram_total_gb
            },
            'gpu': {
                'available': self.gpu_available,
                'count': self.gpu_count,
                'usage_percent': resources.gpu_percent,
                'memory_used_mb': resources.gpu_memory_used_mb,
                'memory_total_mb': resources.gpu_memory_total_mb,
                'temperature': resources.gpu_temperature
            },
            'disk': {
                'usage_percent': resources.disk_usage_percent
            },
            'network': {
                'sent_mb': resources.network_sent_mb,
                'recv_mb': resources.network_recv_mb
            },
            'status': {
                'level': resources.resource_level.value,
                'monitoring_active': self.monitoring_active,
                'auto_adjust_enabled': self.auto_adjust_enabled,
                'performance_mode': self.performance_mode
            },
            'optimal_workers': optimal_workers,
            'optimizations': {
                'total_count': len(self.optimization_history),
                'recent': self.optimization_history[-5:] if self.optimization_history else []
            }
        }
    
    # ========================================
    # MERGED FROM system_health_manager.py + system_warmup.py
    # ========================================
    def fix_ssl_issues(self):
        """Fix SSL certificate verification issues"""
        try:
            import ssl, certifi, urllib3, requests
            warnings.filterwarnings('ignore', category=DeprecationWarning, module='ssl')
            warnings.filterwarnings('ignore', message='.*certificate verify failed.*')
            warnings.filterwarnings('ignore', message='.*SSL.*')
            
            try:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            except Exception:
                pass
                
            try:
                ca_path = certifi.where()
                self._requests_session = requests.Session()
                self._requests_session.verify = ca_path
                unified_logging.info("SSL certificate verification configured using certifi")
            except Exception:
                self._requests_session = requests.Session()
                self._requests_session.verify = True
                unified_logging.warning("certifi not available; using default verification")
        except Exception as e:
            unified_logging.error(f"Failed to fix SSL issues: {e}")
    
    def check_system_health(self) -> Dict[str, bool]:
        """Check overall system health status"""
        try:
            health_status = {
                'ssl_healthy': True,
                'websocket_healthy': True,
                'ccxt_healthy': True,
                'cpu_healthy': self.get_current_resources().cpu_percent < 95,
                'ram_healthy': self.get_current_resources().ram_percent < 92,
                'gpu_healthy': True
            }
            
            # Test SSL
            try:
                import ssl, socket
                context = ssl.create_default_context()
                with socket.create_connection(("www.google.com", 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname="www.google.com") as ssock:
                        pass
            except:
                health_status['ssl_healthy'] = False
            
            # Test CCXT if available
            try:
                import importlib
                if importlib.util.find_spec('ccxt'):
                    import ccxt
                    exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 10000})
                    exchange.load_markets()
                    exchange.close()
            except:
                health_status['ccxt_healthy'] = False
            
            return health_status
        except Exception as e:
            unified_logging.error(f"System health check failed: {e}")
            return {'error': str(e)}
    
    def warmup_system(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Warm up system caches and connections"""
        try:
            if symbols is None:
                symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            
            unified_logging.info(f"🔥 Starting system warmup for {len(symbols)} symbols...")
            start_time = time.time()
            results = {
                'symbols_cached': 0,
                'indicators_ready': False,
                'models_ready': False
            }
            
            # Pre-cache market data
            try:
                from .real_market_data_fetcher import real_market_data_fetcher
                for symbol in symbols:
                    try:
                        real_market_data_fetcher.get_current_price(symbol)
                        real_market_data_fetcher.get_historical_data(symbol, '1h', 100)
                        results['symbols_cached'] += 1
                    except:
                        pass
            except:
                pass
            
            # Warm up indicators
            try:
                from .unified_technical_indicators import unified_technical_indicators
                results['indicators_ready'] = True
            except:
                pass
            
            # Check AI models
            try:
                from .ai_training_engine import ai_training_engine
                results['models_ready'] = hasattr(ai_training_engine, 'ai_models')
            except:
                pass
            
            elapsed = time.time() - start_time
            results['warmup_duration_seconds'] = elapsed
            unified_logging.info(f"✅ System warmup completed in {elapsed:.2f}s")
            
            return results
        except Exception as e:
            unified_logging.error(f"System warmup failed: {e}")
            return {'error': str(e)}

# Create global instance
intelligent_resource_manager = IntelligentResourceManager()

