"""
LiciproStore — State Store centralizado y reactivo (patrón Singleton).

Único punto de mutación del estado en memoria de la aplicación. Cada vez que el
estado cambia (carga, selección, edición de una licitación/lote/documento), el
Store:
  1. Muta su estado interno.
  2. Recalcula los KPIs invocando al servicio de dominio (fuente única de verdad).
  3. Emite señales nativas de Qt para que las vistas suscritas se actualicen
     automáticamente, sin recargas manuales.

Uso típico:
    from app.core.state.store import LiciproStore
    store = LiciproStore.instance()
    store.licitaciones_cargadas.connect(mi_slot)
    store.set_licitaciones(lista)
"""
from __future__ import annotations

from typing import Any, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.logic import domain_service


class LiciproStore(QObject):
    """Store global reactivo. Singleton: usar ``LiciproStore.instance()``."""

    # ----------------------------- Señales globales -----------------------------
    licitaciones_cargadas = pyqtSignal(list)            # nueva lista completa
    licitacion_seleccionada_changed = pyqtSignal(object)  # licitación seleccionada (o None)
    licitacion_actualizada = pyqtSignal(object)         # licitación mutada
    metricas_recomputadas = pyqtSignal(dict)            # KPIs recalculados

    _instance: Optional["LiciproStore"] = None

    @classmethod
    def instance(cls) -> "LiciproStore":
        """Devuelve la instancia única del Store (creándola la primera vez)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._licitaciones: List[Any] = []
        self._seleccionada: Optional[Any] = None
        self._metricas: dict = {}

    # ============================ Lectura (estado) ============================
    @property
    def licitaciones(self) -> List[Any]:
        return self._licitaciones

    @property
    def seleccionada(self) -> Optional[Any]:
        return self._seleccionada

    @property
    def metricas(self) -> dict:
        return dict(self._metricas)

    # ============================ Acciones (mutaciones) ============================
    def set_licitaciones(self, licitaciones: Optional[List[Any]]) -> None:
        """Reemplaza la colección completa en memoria y notifica a la UI."""
        self._licitaciones = list(licitaciones or [])

        # Reconciliar la selección: si la seleccionada ya no existe, limpiarla.
        if self._seleccionada is not None:
            vigente = self._find_same(self._seleccionada)
            if vigente is None:
                self.seleccionar_licitacion(None)
            elif vigente is not self._seleccionada:
                self._seleccionada = vigente
                self.licitacion_seleccionada_changed.emit(vigente)

        self._recompute_metrics()
        self.licitaciones_cargadas.emit(self._licitaciones)

    def seleccionar_licitacion(self, licitacion: Optional[Any]) -> None:
        """Cambia la licitación seleccionada y notifica. No re-emite si ya es la
        misma (evita trabajo/parpadeo redundante en la UI)."""
        if licitacion is self._seleccionada:
            return
        self._seleccionada = licitacion
        self.licitacion_seleccionada_changed.emit(licitacion)

    def actualizar_licitacion(self, licitacion: Any) -> None:
        """Inserta o reemplaza una licitación (upsert por id/numero), recalcula
        KPIs y emite la señal de actualización."""
        target = self._upsert(licitacion)
        self._recompute_metrics()
        self.licitacion_actualizada.emit(target)

    def actualizar_lote_en_licitacion(self, licitacion: Any, lote: Any) -> Any:
        """Actualiza (o inserta) un lote dentro de una licitación en memoria,
        recalcula KPIs y emite la señal de actualización.

        Devuelve la licitación efectivamente mutada (la vigente del store si
        existe, o la recibida)."""
        target = self._find_same(licitacion) or licitacion
        lotes = getattr(target, "lotes", None)
        if lotes is None:
            lotes = []
            try:
                setattr(target, "lotes", lotes)
            except Exception:
                pass

        numero = str(getattr(lote, "numero", "")).strip()
        for i, existente in enumerate(lotes):
            if str(getattr(existente, "numero", "")).strip() == numero:
                lotes[i] = lote
                break
        else:
            lotes.append(lote)

        # Asegurar que la licitación está en la colección.
        if self._find_same(target) is None:
            self._licitaciones.append(target)

        self._recompute_metrics()
        self.licitacion_actualizada.emit(target)
        return target

    def recomputar_metricas(self) -> dict:
        """Fuerza el recálculo de KPIs y emite la señal. Devuelve el dict."""
        self._recompute_metrics()
        return self.metricas

    # ============================ Internos ============================
    def _recompute_metrics(self) -> None:
        self._metricas = domain_service.calcular_metricas_globales(self._licitaciones)
        self.metricas_recomputadas.emit(dict(self._metricas))

    @staticmethod
    def _key(lic: Any) -> Optional[str]:
        """Clave de identidad: id si existe, si no numero_proceso normalizado."""
        if lic is None:
            return None
        lic_id = getattr(lic, "id", None)
        if lic_id not in (None, "", 0):
            return f"id:{lic_id}"
        num = (getattr(lic, "numero_proceso", None) or "").strip().upper()
        return f"num:{num}" if num else None

    def _find_same(self, lic: Any) -> Optional[Any]:
        """Encuentra en la colección la licitación equivalente (misma identidad)."""
        key = self._key(lic)
        if key is None:
            return lic if lic in self._licitaciones else None
        for existente in self._licitaciones:
            if self._key(existente) == key:
                return existente
        return None

    def _upsert(self, lic: Any) -> Any:
        """Inserta o reemplaza por identidad. Devuelve el objeto vigente."""
        key = self._key(lic)
        for i, existente in enumerate(self._licitaciones):
            if self._key(existente) == key:
                self._licitaciones[i] = lic
                return lic
        self._licitaciones.append(lic)
        return lic


def get_store() -> LiciproStore:
    """Acceso de conveniencia al Store global (Singleton)."""
    return LiciproStore.instance()
