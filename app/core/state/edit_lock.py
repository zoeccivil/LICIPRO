"""
Registro de bloqueos de edición (Edit Lock Registry) — thread-safe.

Coordina la concurrencia entre:
  * el flujo de EDICIÓN local (LicitationDetailsWindow, en el hilo de la UI), y
  * la SINCRONIZACIÓN en tiempo real de Firestore (on_snapshot, en un hilo de
    fondo del SDK).

Cuando el usuario abre una licitación para editarla, la ventana "adquiere" el
bloqueo de ese ID. Mientras el bloqueo esté activo, el callback de on_snapshot
del adaptador IGNORA la actualización remota de ese ID concreto y preserva la
versión local en edición, evitando pisar cambios que el usuario aún está
escribiendo (Optimistic Locking sutil).

Módulo PURO: solo usa la librería estándar (threading). No depende de PyQt6 ni
de Firestore, por lo que puede importarse con seguridad desde el backend.
"""
from __future__ import annotations

import threading
from typing import Any, Optional, Set


class EditLockRegistry:
    """Conjunto thread-safe de IDs de licitación en edición activa."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._editing: Set[str] = set()

    @staticmethod
    def _norm(lic_id: Any) -> Optional[str]:
        if lic_id in (None, "", 0):
            return None
        return str(lic_id)

    def acquire(self, lic_id: Any) -> None:
        """Marca un ID como en edición (idempotente)."""
        key = self._norm(lic_id)
        if key is None:
            return
        with self._lock:
            self._editing.add(key)

    def release(self, lic_id: Any) -> None:
        """Libera el bloqueo de un ID (idempotente)."""
        key = self._norm(lic_id)
        if key is None:
            return
        with self._lock:
            self._editing.discard(key)

    def is_locked(self, lic_id: Any) -> bool:
        key = self._norm(lic_id)
        if key is None:
            return False
        with self._lock:
            return key in self._editing

    def snapshot(self) -> Set[str]:
        """Copia atómica del conjunto de IDs bloqueados."""
        with self._lock:
            return set(self._editing)

    def clear(self) -> None:
        with self._lock:
            self._editing.clear()


_registry: Optional[EditLockRegistry] = None
_registry_lock = threading.Lock()


def get_edit_lock_registry() -> EditLockRegistry:
    """Devuelve el registro global de bloqueos de edición (Singleton thread-safe)."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = EditLockRegistry()
    return _registry
