"""
Simple adapter registry for God Mode 1000.
Modules should register adapters by domain name (e.g., 'market', 'onchain', 'orderbook', 'news') using register_adapter.
This registry is intentionally minimal and thread-safe.
"""
from threading import RLock
from typing import Dict, Any

_lock = RLock()
_adapters: Dict[str, Any] = {}


def register_adapter(domain: str, adapter_obj: Any):
    with _lock:
        _adapters[domain] = adapter_obj


def get_adapter(domain: str):
    with _lock:
        return _adapters.get(domain)


def list_adapters():
    with _lock:
        return list(_adapters.keys())


def has_adapter(domain: str) -> bool:
    with _lock:
        return domain in _adapters


def clear_registry():
    with _lock:
        _adapters.clear()
