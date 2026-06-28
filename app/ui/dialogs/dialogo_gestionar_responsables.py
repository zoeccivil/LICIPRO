"""
Catálogo de Responsables / Departamentos.

DialogoGestionarResponsables: subclase fina del componente genérico
BaseMasterManagerDialog (CRUD + guardar).
"""
from __future__ import annotations

from app.core.db_adapter import DatabaseAdapter
from app.ui.dialogs.base_master_dialog import BaseMasterManagerDialog, MasterEntityConfig


class DialogoGestionarResponsables(BaseMasterManagerDialog):
    """Gestor del catálogo de responsables (CRUD + guardar)."""

    def __init__(self, parent, db: DatabaseAdapter):
        self.db = db
        config = MasterEntityConfig(
            title="Catálogo de Responsables",
            columns=[("Nombre del Responsable o Departamento", "nombre")],
            form_fields=[("Nombre", "nombre")],
            load_fn=lambda: db.get_responsables_maestros() or [],
            save_fn=db.save_responsables_maestros,
            key_field="nombre",
            entity_name="responsable",
        )
        super().__init__(parent, config, mode=self.MODE_MANAGE)
