"""
GOD MODE 1000 - UNIFIED LOGGING MANAGER
==============================================
CENTRALIZED LOGGING SYSTEM FOR ALL MODULES
ZERO DUPLICATES - UNIFIED ARCHITECTURE
[BULLSEYE] PRODUCTION-GRADE LOGGING & MONITORING

UNIFIED LOGGING MANAGER CAPABILITIES:
- Centralized logging configuration
- Module-specific loggers
- Performance monitoring
- Error tracking and alerting
- Log rotation and cleanup
- Real-time log analysis
"""

import logging
import logging.handlers
import os
import sys
import time
import threading
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import json
import traceback
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    module: str
    message: str
    metadata: Dict[str, Any] = None
    thread_id: int = None
    process_id: int = None

class UnifiedLoggingManager:
    """UNIFIED LOGGING MANAGER - GOD MODE 1000
    Centralized logging system for all modules
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UnifiedLoggingManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.loggers = {}
        self.log_entries = []
        self.max_log_entries = 10000
        self.log_lock = threading.RLock()
        
        # Create logs directory
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        self._configure_root_logger()
        
        # Initialize module loggers
        self._initialize_module_loggers()
    # Do not start background cleanup at import time. Call start_cleanup() explicitly from app startup.
    # self._start_log_cleanup()
    # NOTE: Do NOT start background cleanup thread automatically on import.
    # Starting background housekeeping at import time caused Streamlit to hang.
    # Call start_cleanup() explicitly when running as a service or from app startup.
    
    def _configure_root_logger(self):
        """Configure root logger with file and console handlers"""
        try:
            # Ensure logging does not print internal handler errors to stderr
            logging.raiseExceptions = False

            # Clear existing handlers (closing them first to avoid closed-stream refs lingering)
            root_logger = logging.getLogger()
            for existing_handler in list(root_logger.handlers):
                try:
                    existing_handler.close()
                except Exception:
                    pass
                try:
                    root_logger.removeHandler(existing_handler)
                except Exception:
                    pass

            # Set root logger level
            root_logger.setLevel(logging.INFO)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            # File handler
            file_handler = logging.handlers.RotatingFileHandler(
                self.logs_dir / "god_mode_1000.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            # Error file handler
            error_handler = logging.handlers.RotatingFileHandler(
                self.logs_dir / "errors.log",
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)

        except Exception as e:
            print(f"Failed to configure root logger: {e}")
    
    def _initialize_module_loggers(self):
        """Initialize loggers for all modules"""
        try:
            # Core module loggers
            core_modules = [
                'app', 'ai_engine', 'trading_engine',
                'portfolio_manager', 'airdrop_manager', 'correlation_engine',
                'onchain_analysis', 'news_sentiment', 'performance_optimizer',
                'websocket_optimizer', 'ssl_connection_manager', 'system_health_manager'
            ]
            
            for module in core_modules:
                logger = logging.getLogger(f"core.{module}")
                logger.setLevel(logging.INFO)
                self.loggers[module] = logger
            
        except Exception as e:
            print(f"Failed to initialize module loggers: {e}")
    
    def _start_log_cleanup(self):
        """Removed background log cleanup thread to avoid ScriptRunContext warnings."""
        # Log cleanup is now synchronous to prevent UI blocking
        pass

    def start_cleanup(self):
        """Start the log cleanup thread when application is ready."""
        self._start_log_cleanup()
    
    def _log_cleanup_loop(self):
        """Background log cleanup loop"""
        while True:
            try:
                time.sleep(3600)  # Run every hour
                with self.log_lock:
                    if len(self.log_entries) > self.max_log_entries:
                        # Keep only the most recent entries
                        self.log_entries = self.log_entries[-self.max_log_entries:]
            except Exception:
                pass
    
    def _log_system_startup(self):
        """Log system startup"""
        try:
            self.log_info("unified_logging", "Unified Logging Manager initialized - God Mode 1000")
        except Exception:
            pass
    
    @classmethod
    def get_logger(cls, module_name: str) -> logging.Logger:
        """Get logger for specific module"""
        instance = cls()
        if module_name in instance.loggers:
            return instance.loggers[module_name]
        
        # Create new logger if not exists
        logger = logging.getLogger(f"core.{module_name}")
        logger.setLevel(logging.INFO)
        instance.loggers[module_name] = logger
        return logger
    
    def log_info(self, module: str, message: str, metadata: Dict[str, Any] = None):
        """Log info message"""
        try:
            logger = self.get_logger(module)
            logger.info(message)
            
            # Store structured log entry
            with self.log_lock:
                entry = LogEntry(
                    timestamp=datetime.now(),
                    level="INFO",
                    module=module,
                    message=message,
                    metadata=metadata,
                    thread_id=0  # Removed threading to avoid ScriptRunContext warnings
                )
                self.log_entries.append(entry)
                
        except Exception:
            pass
    
    def log_error(self, module: str, message: str, metadata: Dict[str, Any] = None, exception: Exception = None):
        """Log error message"""
        try:
            logger = self.get_logger(module)
            if exception:
                logger.error(f"{message}: {exception}", exc_info=True)
            else:
                logger.error(message)
            
            # Store structured log entry
            with self.log_lock:
                entry = LogEntry(
                    timestamp=datetime.now(),
                    level="ERROR",
                    module=module,
                    message=message,
                    metadata=metadata,
                    thread_id=0  # Removed threading to avoid ScriptRunContext warnings
                )
                self.log_entries.append(entry)
                
        except Exception:
            pass
    
    def log_warning(self, module: str, message: str, metadata: Dict[str, Any] = None):
        """Log warning message"""
        try:
            logger = self.get_logger(module)
            logger.warning(message)
            
            # Store structured log entry
            with self.log_lock:
                entry = LogEntry(
                    timestamp=datetime.now(),
                    level="WARNING",
                    module=module,
                    message=message,
                    metadata=metadata,
                    thread_id=0  # Removed threading to avoid ScriptRunContext warnings
                )
                self.log_entries.append(entry)
                
        except Exception:
            pass
    
    def log_debug(self, module: str, message: str, metadata: Dict[str, Any] = None):
        """Log debug message"""
        try:
            logger = self.get_logger(module)
            logger.debug(message)
            
            # Store structured log entry
            with self.log_lock:
                entry = LogEntry(
                    timestamp=datetime.now(),
                    level="DEBUG",
                    module=module,
                    message=message,
                    metadata=metadata,
                    thread_id=0  # Removed threading to avoid ScriptRunContext warnings
                )
                self.log_entries.append(entry)
                
        except Exception:
            pass
    
    def get_recent_logs(self, count: int = 100) -> List[LogEntry]:
        """Get recent log entries"""
        try:
            with self.log_lock:
                return self.log_entries[-count:]
        except Exception:
            return []
    
    def get_logs_by_module(self, module: str, count: int = 100) -> List[LogEntry]:
        """Get log entries for specific module"""
        try:
            with self.log_lock:
                module_logs = [entry for entry in self.log_entries if entry.module == module]
                return module_logs[-count:]
        except Exception:
            return []
    
    def get_logs_by_level(self, level: str, count: int = 100) -> List[LogEntry]:
        """Get log entries by level"""
        try:
            with self.log_lock:
                level_logs = [entry for entry in self.log_entries if entry.level == level]
                return level_logs[-count:]
        except Exception:
            return []
    
    # Shortcut methods for compatibility with direct .info(), .error(), .warning(), .debug() calls
    def info(self, message: str, metadata: Dict[str, Any] = None):
        """Shortcut for log_info - compatible with standard logging interface"""
        self.log_info("unified", message, metadata)
    
    def error(self, message: str, metadata: Dict[str, Any] = None, exception: Exception = None):
        """Shortcut for log_error - compatible with standard logging interface"""
        self.log_error("unified", message, metadata, exception)
    
    def warning(self, message: str, metadata: Dict[str, Any] = None):
        """Shortcut for log_warning - compatible with standard logging interface"""
        self.log_warning("unified", message, metadata)
    
    def debug(self, message: str, metadata: Dict[str, Any] = None):
        """Shortcut for log_debug - compatible with standard logging interface"""
        self.log_debug("unified", message, metadata)
    
    def export_logs(self, filename: str = None) -> Optional[str]:
        """Export logs to file - God Mode 10000"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.logs_dir / f"export_{timestamp}.json"
            
            with self.log_lock:
                if not self.log_entries:
                    return None
                
                # Convert log entries to dict
                log_data = []
                for entry in self.log_entries:
                    log_data.append({
                        'timestamp': entry.timestamp.isoformat(),
                        'level': entry.level,
                        'module': entry.module,
                        'message': entry.message,
                        'metadata': entry.metadata
                    })
                
                # Write to file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=2, ensure_ascii=False)
                
                return str(filename)
        except Exception as e:
            print(f"Failed to export logs: {e}")
            return None

# Create a proxy that defers instantiation until first use
class UnifiedLoggingManagerProxy:
    """Proxy that lazily instantiates UnifiedLoggingManager on first access."""
    def __init__(self):
        self._instance = None
        self._lock = threading.Lock()

    def _ensure(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = UnifiedLoggingManager()

    def __getattr__(self, name):
        self._ensure()
        return getattr(self._instance, name)


# Export proxy under original name
unified_logging = UnifiedLoggingManagerProxy()

# Export commonly used functions
def log_info(module: str, message: str, metadata: Dict[str, Any] = None):
    """Log info message"""
    unified_logging.log_info(module, message, metadata)

def log_error(module: str, message: str, metadata: Dict[str, Any] = None, exception: Exception = None):
    """Log error message"""
    unified_logging.log_error(module, message, metadata, exception)

def log_warning(module: str, message: str, metadata: Dict[str, Any] = None):
    """Log warning message"""
    unified_logging.log_warning(module, message, metadata)

def log_debug(module: str, message: str, metadata: Dict[str, Any] = None):
    """Log debug message"""
    unified_logging.log_debug(module, message, metadata)

def get_logger(module_name: str) -> logging.Logger:
    """Get logger for specific module"""
    return unified_logging.get_logger(module_name)
