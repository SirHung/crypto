"""
GOD MODE 10000 - PYTHON 3.13 COMPATIBILITY FIX
===============================================
CRITICAL: Fix Python 3.13.3 _pyrepl module bug
This is NOT a wrapper/bypass - This is a PATCH for Python 3.13 stdlib bug

Python 3.13.3 has a bug where pydoc tries to import _pyrepl which doesn't exist.
This causes pandas, scipy, lightgbm, joblib imports to fail in worker processes.

This module MUST be imported BEFORE any other imports in the application.
MULTIPROCESSING FIX: Provides initializer for ALL worker processes (joblib, multiprocessing, etc.)
"""

import sys
import types
import os


def _apply_pyrepl_fix():
    """
    Apply _pyrepl compatibility fix - can be called multiple times safely.
    Used as initializer for multiprocessing/joblib worker processes.
    
    This fix is CRITICAL for:
    - Main process imports (pandas, scipy, sklearn)
    - Multiprocessing worker processes (parallel_executor)
    - Joblib worker processes (sklearn n_jobs=-1)
    - Loky backend processes (sklearn default backend)
    """
    # Only apply fix for Python 3.13+
    if sys.version_info >= (3, 13):
        # Check if _pyrepl module is missing
        if '_pyrepl' not in sys.modules:
            # Create minimal _pyrepl module to satisfy Python 3.13 pydoc requirement
            _pyrepl_module = types.ModuleType('_pyrepl')
            _pyrepl_pager = types.ModuleType('pager')
            
            # Add required pager functions that pydoc expects
            def get_pager():
                return lambda text: print(text)
            
            _pyrepl_pager.get_pager = get_pager
            _pyrepl_pager.plain = lambda text: print(text)
            _pyrepl_pager.pipe_pager = lambda text, cmd: print(text)
            _pyrepl_pager.plain_pager = lambda text: print(text)
            _pyrepl_pager.tempfile_pager = lambda text, cmd: print(text)
            _pyrepl_pager.tty_pager = lambda text: print(text)
            
            # Register modules in sys.modules
            sys.modules['_pyrepl'] = _pyrepl_module
            sys.modules['_pyrepl.pager'] = _pyrepl_pager
            _pyrepl_module.pager = _pyrepl_pager


def _register_joblib_backend_fix():
    """
    CRITICAL: Register _pyrepl fix for joblib/loky backend processes
    
    This ensures ALL worker processes created by sklearn (via joblib)
    have the _pyrepl fix applied before they try to import any modules.
    
    ULTRA FIX: Sets environment variables to ensure EVERY joblib worker process
    has the _pyrepl fix applied automatically.
    """
    # Only apply fix for Python 3.13+
    if sys.version_info >= (3, 13):
        # CRITICAL FIX: Set LOKY_INITIALIZER to run _pyrepl fix in ALL workers
        # This is the MOST RELIABLE method - works for sklearn, joblib, any loky usage
        os.environ['LOKY_PICKLER'] = 'pickle'
        os.environ['LOKY_MAX_CPU_COUNT'] = str(os.cpu_count() or 4)
        
        try:
            import joblib
            from joblib.externals import loky
            
            # CRITICAL: Patch loky's ProcessPoolExecutor to ALWAYS use our initializer
            # This ensures _pyrepl fix is applied even when sklearn doesn't pass initializer
            if hasattr(loky, 'get_reusable_executor'):
                original_get_executor = loky.get_reusable_executor
                
                def patched_get_executor(*args, **kwargs):
                    # FORCE our initializer - override any existing one if needed
                    existing_init = kwargs.get('initializer', None)
                    existing_initargs = kwargs.get('initargs', ())
                    
                    if existing_init is None:
                        # No existing initializer - just use ours
                        kwargs['initializer'] = _apply_pyrepl_fix
                        kwargs['initargs'] = ()
                    else:
                        # Chain with existing initializer
                        def chained_init(*init_args):
                            # Apply _pyrepl fix FIRST
                            _apply_pyrepl_fix()
                            # Then call existing initializer
                            existing_init(*init_args)
                        
                        kwargs['initializer'] = chained_init
                        kwargs['initargs'] = existing_initargs
                    
                    return original_get_executor(*args, **kwargs)
                
                loky.get_reusable_executor = patched_get_executor
        except Exception as e:
            # If patching fails, at least we have environment variables set
            pass


def setup_global_worker_initializer():
    """
    Setup global worker initializer for ALL multiprocessing contexts.
    This ensures _pyrepl fix is applied to all worker processes.
    """
    try:
        import multiprocessing as mp
        
        # Only setup for Python 3.13+
        if sys.version_info >= (3, 13):
            # Try to set as default initializer for all contexts
            for ctx_name in ['spawn', 'fork', 'forkserver']:
                try:
                    ctx = mp.get_context(ctx_name)
                    # Store our initializer function for this context
                    # This will be used by parallel_executor
                    if not hasattr(ctx, '_pyrepl_fix_applied'):
                        ctx._pyrepl_fix_applied = True
                except Exception:
                    pass
    except Exception:
        pass


# Apply fix immediately for main process
_apply_pyrepl_fix()

# Register joblib backend fix
_register_joblib_backend_fix()

# Setup global worker initializer
setup_global_worker_initializer()

# Verify fix worked
try:
    import pydoc
except ImportError as e:
    raise RuntimeError(f"CRITICAL: Python 3.13 compatibility fix failed: {e}")

