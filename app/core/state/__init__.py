"""
Paquete de gestión de estado de LICIPRO.

Exposición PEREZOSA (lazy) de los símbolos para no arrastrar dependencias de UI
(PyQt6, vía store.py) cuando solo se necesita el registro de bloqueos de edición
(edit_lock.py), que es puro y se usa desde la capa de backend (db_adapter).
"""
from typing import Any

__all__ = ["LiciproStore", "get_store", "EditLockRegistry", "get_edit_lock_registry"]


def __getattr__(name: str) -> Any:  # PEP 562
    if name in ("LiciproStore", "get_store"):
        from app.core.state import store as _store
        return getattr(_store, name)
    if name in ("EditLockRegistry", "get_edit_lock_registry"):
        from app.core.state import edit_lock as _edit_lock
        return getattr(_edit_lock, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
