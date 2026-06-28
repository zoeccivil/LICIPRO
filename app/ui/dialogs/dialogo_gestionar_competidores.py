"""
Catálogo de Competidores.

DialogoGestionarCompetidores: gestor (CRUD) — subclase fina del componente
genérico BaseMasterManagerDialog.

DialogoSeleccionarCompetidores: selector MÚLTIPLE de competidores (checkboxes) —
consolidado aquí desde el antiguo 'dialogo_seleccionar_competidores.py'.
"""
from __future__ import annotations
from typing import Any, Dict, List, Set

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QDialogButtonBox, QLabel,
)

from app.core.models import Oferente
from app.ui.dialogs.base_master_dialog import BaseMasterManagerDialog, MasterEntityConfig


class DialogoGestionarCompetidores(BaseMasterManagerDialog):
    """Gestor del catálogo de competidores (CRUD + guardar)."""

    def __init__(self, parent, db):
        self.db = db
        config = MasterEntityConfig(
            title="Catálogo de Competidores",
            columns=[
                ("Nombre", "nombre"), ("RNC", "rnc"),
                ("No. RPE", "rpe"), ("Representante", "representante"),
            ],
            form_fields=[
                ("Nombre", "nombre"), ("RNC", "rnc"),
                ("No. RPE", "rpe"), ("Representante", "representante"),
            ],
            load_fn=lambda: db.get_competidores_maestros() or [],
            save_fn=db.save_competidores_maestros,
            key_field="nombre",
            entity_name="competidor",
        )
        super().__init__(parent, config, mode=self.MODE_MANAGE)


# Índices de columnas para el selector múltiple
COL_SEL = 0
COL_NOMBRE = 1
COL_RNC = 2


class DialogoSeleccionarCompetidores(QDialog):
    """
    Diálogo para seleccionar MÚLTIPLES competidores de una lista maestra, con búsqueda.
    """
    def __init__(self, parent,
                 competidores_maestros: List[Dict[str, Any]],
                 oferentes_actuales: List[Oferente]):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Competidores desde Catálogo")
        self.setMinimumSize(600, 450)

        nombres_actuales_lower = {o.nombre.lower() for o in oferentes_actuales}
        self.competidores_disponibles = sorted(
            [c for c in competidores_maestros if c.get('nombre', '').lower() not in nombres_actuales_lower],
            key=lambda x: x.get('nombre', '')
        )
        self.competidores_filtrados = self.competidores_disponibles[:]

        self.seleccionados: Set[str] = set()
        self.result: List[Dict[str, Any]] = []

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._filtrar_y_poblar)

        self._build_ui()
        self._poblar_tabla()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filtrar por nombre o RNC...")
        self.search_edit.textChanged.connect(self._search_timer.start)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sel.", "Nombre del Competidor", "RNC"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(COL_SEL, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_NOMBRE, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(COL_RNC, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(COL_RNC, 120)
        main_layout.addWidget(self.table)

        self.table.cellClicked.connect(self._on_cell_clicked)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _filtrar_y_poblar(self):
        termino = self.search_edit.text().strip().lower()
        if not termino:
            self.competidores_filtrados = self.competidores_disponibles[:]
        else:
            self.competidores_filtrados = [
                c for c in self.competidores_disponibles
                if termino in c.get('nombre', '').lower() or termino in (c.get('rnc', '') or '').lower()
            ]
        self._poblar_tabla()

    def _poblar_tabla(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.competidores_filtrados))

        for row, comp_dict in enumerate(self.competidores_filtrados):
            nombre = comp_dict.get('nombre', '')
            rnc = comp_dict.get('rnc', '')

            item_sel = QTableWidgetItem()
            item_sel.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_state = Qt.CheckState.Checked if nombre in self.seleccionados else Qt.CheckState.Unchecked
            item_sel.setCheckState(check_state)
            item_sel.setData(Qt.ItemDataRole.UserRole, nombre)
            self.table.setItem(row, COL_SEL, item_sel)

            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, COL_NOMBRE, item_nombre)

            item_rnc = QTableWidgetItem(rnc)
            item_rnc.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, COL_RNC, item_rnc)

    def _on_cell_clicked(self, row: int, column: int):
        item_sel = self.table.item(row, COL_SEL)
        if not item_sel:
            return
        nombre = item_sel.data(Qt.ItemDataRole.UserRole)
        if not nombre:
            return
        current_state = item_sel.checkState()
        new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
        item_sel.setCheckState(new_state)
        if new_state == Qt.CheckState.Checked:
            self.seleccionados.add(nombre)
        else:
            self.seleccionados.discard(nombre)

    def accept(self):
        self.result = [
            comp_dict for comp_dict in self.competidores_disponibles
            if comp_dict.get('nombre') in self.seleccionados
        ]
        super().accept()

    def get_seleccionados(self) -> List[Dict[str, Any]]:
        return self.result
