"""
Catálogo de Empresas propias.

DialogoGestionarEmpresas: ahora una subclase fina de BaseMasterManagerDialog
(componente genérico reutilizable). Mantiene la firma del constructor para no
romper a sus llamadores.

SeleccionarEmpresasDialog: selector MÚLTIPLE de empresas (checkboxes) — se
consolidó aquí desde el antiguo 'seleccionar_empresas_dialog.py'.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QAbstractItemView,
)

from app.ui.dialogs.base_master_dialog import BaseMasterManagerDialog, MasterEntityConfig


class DialogoGestionarEmpresas(BaseMasterManagerDialog):
    """Gestor del catálogo de empresas propias (CRUD + guardar)."""

    def __init__(self, parent, db, empresas_registradas: Optional[List[Dict[str, Any]]] = None):
        self.db = db

        def _load():
            if empresas_registradas is not None:
                return [dict(e) for e in empresas_registradas]
            return db.get_empresas_maestras() or []

        config = MasterEntityConfig(
            title="Gestor de Empresas",
            columns=[
                ("Nombre", "nombre"), ("RNC", "rnc"), ("Teléfono", "telefono"),
                ("Correo", "correo"), ("Dirección", "direccion"),
            ],
            form_fields=[
                ("Nombre", "nombre"), ("RNC", "rnc"), ("Teléfono", "telefono"),
                ("Correo", "correo"), ("Dirección", "direccion"), ("RPE", "rpe"),
                ("Representante", "representante"), ("Cargo del Representante", "cargo_representante"),
            ],
            load_fn=_load,
            save_fn=db.save_empresas_maestras,
            key_field="nombre",
            entity_name="empresa",
            en_uso_fn=getattr(db, "is_empresa_en_uso", None),
        )
        super().__init__(parent, config, mode=self.MODE_MANAGE)


class SeleccionarEmpresasDialog(QDialog):
    """
    Diálogo para seleccionar MÚLTIPLES empresas con búsqueda y checkboxes.
    Retorna los nombres seleccionados en self.resultado (lista de str).
    """
    def __init__(self, parent, todas_las_empresas, seleccion_actual=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Empresas Participantes")
        self.resize(500, 400)
        self.todas_las_empresas = sorted(todas_las_empresas, key=lambda x: x['nombre'])
        self.nombres_seleccionados = set(seleccion_actual or [])

        layout = QVBoxLayout(self)

        # Buscador
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self._populate_tree)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # TreeWidget con checkboxes
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nombre de la Empresa"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.tree, 1)
        self._populate_tree()

        # Botones
        btns = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.resultado = None

    def _populate_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        search_term = self.search_edit.text().lower()
        for empresa in self.todas_las_empresas:
            nombre = empresa['nombre']
            if search_term in nombre.lower():
                item = QTreeWidgetItem([nombre])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if nombre in self.nombres_seleccionados:
                    item.setCheckState(0, Qt.CheckState.Checked)
                else:
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                self.tree.addTopLevelItem(item)
        self.tree.blockSignals(False)

    def _on_item_changed(self, item, column):
        nombre = item.text(0)
        if item.checkState(0) == Qt.CheckState.Checked:
            self.nombres_seleccionados.add(nombre)
        else:
            self.nombres_seleccionados.discard(nombre)

    def accept(self):
        self.resultado = list(self.nombres_seleccionados)
        super().accept()
