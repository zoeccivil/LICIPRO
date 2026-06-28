"""
Catálogo de Instituciones.

DialogoGestionarInstituciones: gestor (CRUD) — subclase fina del componente
genérico BaseMasterManagerDialog.

DialogoSeleccionarInstitucion: selector de UNA institución — consolidado aquí
desde el antiguo 'dialogo_seleccionar_institucion.py'. Usa el modo "select" del
componente base y preserva la API que esperan los llamadores
(institucion_seleccionada, get_selected_data, _seleccionar_item_por_nombre).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.ui.dialogs.base_master_dialog import BaseMasterManagerDialog, MasterEntityConfig


def _instituciones_config(db) -> MasterEntityConfig:
    return MasterEntityConfig(
        title="Gestor de Instituciones",
        columns=[
            ("Nombre", "nombre"), ("RNC", "rnc"), ("Teléfono", "telefono"),
            ("Correo", "correo"), ("Dirección", "direccion"),
        ],
        form_fields=[
            ("Nombre", "nombre"), ("RNC", "rnc"), ("Teléfono", "telefono"),
            ("Correo", "correo"), ("Dirección", "direccion"),
        ],
        load_fn=lambda: db.get_instituciones_maestras() or [],
        save_fn=db.save_instituciones_maestras,
        key_field="nombre",
        entity_name="institución",
        en_uso_fn=getattr(db, "is_institucion_en_uso", None),
    )


class DialogoGestionarInstituciones(BaseMasterManagerDialog):
    """Gestor del catálogo de instituciones (CRUD + guardar)."""

    def __init__(self, parent, db):
        self.db = db
        super().__init__(parent, _instituciones_config(db), mode=self.MODE_MANAGE)


class DialogoSeleccionarInstitucion(BaseMasterManagerDialog):
    """Selector de una institución del catálogo maestro (modo selección)."""

    def __init__(self, parent, db_adapter):
        self.db = db_adapter
        super().__init__(parent, _instituciones_config(db_adapter), mode=self.MODE_SELECT)
        self.setWindowTitle("Seleccionar Institución")
        # Atributo de compatibilidad esperado por los llamadores.
        self.institucion_seleccionada: Optional[Dict[str, Any]] = None

    def _accept_selection(self) -> None:
        item = self._current()
        if item:
            self.institucion_seleccionada = item
        super()._accept_selection()

    # Compatibilidad con la API previa usada por los llamadores.
    def _seleccionar_item_por_nombre(self, nombre: str) -> None:
        self.seleccionar_por_clave(nombre)

    def refrescar_lista(self, seleccionar_nombre: Optional[str] = None) -> None:
        self._items = list(self.config.load_fn() or [])
        self._sort()
        self._populate()
        if seleccionar_nombre:
            self.seleccionar_por_clave(seleccionar_nombre)
