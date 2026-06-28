"""
BaseMasterManagerDialog — componente genérico reutilizable (DRY) para catálogos
maestros (Empresas, Instituciones, Competidores, Responsables, ...).

Elimina la duplicación de los múltiples diálogos "gestionar"/"seleccionar" que
existían por entidad. Ofrece de forma automática:

  * Tabla para listar la entidad (columnas configurables).
  * Filtro de búsqueda rápida superior.
  * Botones CRUD estándar (Agregar / Editar / Eliminar) con un editor genérico
    construido a partir de los campos del formulario.
  * Dos MODOS:
      - "manage": mantenimiento puro (CRUD + "Guardar y Cerrar").
      - "select": selección (doble clic o "Seleccionar" emite el objeto y cierra;
        un botón "Gestionar Catálogo…" abre el mismo diálogo en modo manage).

Se configura inyectando un MasterEntityConfig con sus columnas, campos de
formulario y los adaptadores de carga/guardado de la base de datos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)


@dataclass
class MasterEntityConfig:
    """Configuración declarativa de una entidad de catálogo maestro."""
    title: str
    columns: List[Tuple[str, str]]              # (encabezado, clave_dict) en la tabla
    form_fields: List[Tuple[str, str]]          # (etiqueta, clave_dict) en el editor
    load_fn: Callable[[], List[Dict[str, Any]]]
    save_fn: Callable[[List[Dict[str, Any]]], Any]
    key_field: str = "nombre"                   # clave de identidad / anti-duplicados
    entity_name: str = "registro"               # para mensajes ("institución", etc.)
    en_uso_fn: Optional[Callable[[str], bool]] = None  # bloquea borrado si en uso


class _GenericEntityForm(QDialog):
    """Editor genérico de un registro construido desde form_fields."""

    def __init__(self, parent, titulo: str, form_fields: List[Tuple[str, str]],
                 initial: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumWidth(420)
        self._fields = form_fields
        self._edits: Dict[str, QLineEdit] = {}
        init = initial or {}

        root = QVBoxLayout(self)
        form = QFormLayout()
        for label, key in form_fields:
            edit = QLineEdit(str(init.get(key, "") or ""))
            self._edits[key] = edit
            form.addRow(f"{label}:", edit)
        root.addLayout(form)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        root.addWidget(bb)

    def data(self) -> Dict[str, Any]:
        return {key: self._edits[key].text().strip() for _, key in self._fields}


class BaseMasterManagerDialog(QDialog):
    """Diálogo base reutilizable para catálogos maestros (modos manage/select)."""

    MODE_MANAGE = "manage"
    MODE_SELECT = "select"

    # Emite el dict seleccionado al confirmar (modo selección).
    seleccion_realizada = pyqtSignal(object)

    def __init__(self, parent, config: MasterEntityConfig, mode: str = MODE_MANAGE):
        super().__init__(parent)
        self.config = config
        self.mode = mode
        self.setWindowTitle(config.title)
        self.setMinimumSize(760, 480)
        self.setModal(True)

        self._items: List[Dict[str, Any]] = list(config.load_fn() or [])
        self._sort()
        self.selected_data: Optional[Dict[str, Any]] = None

        self._build_ui()
        self._populate()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        # Filtro de búsqueda
        fl = QHBoxLayout()
        fl.addWidget(QLabel("Buscar:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filtrar…")
        self.search_edit.textChanged.connect(self._populate)
        fl.addWidget(self.search_edit, 1)
        root.addLayout(fl)

        # Tabla
        self.table = QTableWidget(0, len(self.config.columns))
        self.table.setHorizontalHeaderLabels([h for h, _ in self.config.columns])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, len(self.config.columns)):
            hdr.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self.table.doubleClicked.connect(self._on_double_click)
        root.addWidget(self.table, 1)

        # Botonera según modo
        actions = QHBoxLayout()
        if self.mode == self.MODE_MANAGE:
            self.btn_add = QPushButton("Agregar")
            self.btn_edit = QPushButton("Editar")
            self.btn_del = QPushButton("Eliminar")
            self.btn_add.clicked.connect(self._add)
            self.btn_edit.clicked.connect(self._edit)
            self.btn_del.clicked.connect(self._del)
            for b in (self.btn_add, self.btn_edit, self.btn_del):
                actions.addWidget(b)
            actions.addStretch(1)
            self.btn_save = QPushButton("Guardar y Cerrar")
            self.btn_save.clicked.connect(self._save_and_close)
            actions.addWidget(self.btn_save)
        else:
            self.btn_manage = QPushButton("Gestionar Catálogo…")
            self.btn_manage.setToolTip("Agregar, editar o eliminar registros del maestro")
            self.btn_manage.clicked.connect(self._open_manager)
            actions.addWidget(self.btn_manage)
            actions.addStretch(1)
            self.button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            self.button_box.accepted.connect(self._accept_selection)
            self.button_box.rejected.connect(self.reject)
            actions.addWidget(self.button_box)
        root.addLayout(actions)

        self.lbl_status = QLabel()
        root.addWidget(self.lbl_status)

    # --------------------------------------------------------------- datos
    def _sort(self) -> None:
        kf = self.config.key_field
        self._items.sort(key=lambda x: str(x.get(kf, "") or "").upper())

    def _filtered_items(self) -> List[Dict[str, Any]]:
        term = (self.search_edit.text() or "").strip().lower()
        if not term:
            return list(self._items)
        keys = [k for _, k in self.config.columns]
        out = []
        for it in self._items:
            hay = " ".join(str(it.get(k, "") or "") for k in keys).lower()
            if term in hay:
                out.append(it)
        return out

    def _populate(self) -> None:
        self.table.setRowCount(0)
        for it in self._filtered_items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, (_, key) in enumerate(self.config.columns):
                cell = QTableWidgetItem(str(it.get(key, "") or ""))
                if col == 0:
                    # Guardar el dict completo para recuperación robusta.
                    cell.setData(Qt.ItemDataRole.UserRole, it)
                self.table.setItem(row, col, cell)
        self.lbl_status.setText(f"Total: {len(self._items)} {self.config.entity_name}(s)")

    def _current(self) -> Optional[Dict[str, Any]]:
        row = self.table.currentRow()
        if row < 0:
            return None
        cell = self.table.item(row, 0)
        return cell.data(Qt.ItemDataRole.UserRole) if cell else None

    def _existe(self, nombre: str, excepto: Optional[Dict[str, Any]] = None) -> bool:
        kf = self.config.key_field
        n = nombre.lower()
        return any(
            it is not excepto and (it.get(kf, "") or "").strip().lower() == n
            for it in self._items
        )

    # ---------------------------------------------------------------- CRUD
    def _add(self) -> None:
        dlg = _GenericEntityForm(self, f"Agregar {self.config.entity_name}", self.config.form_fields)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.data()
        nombre = (data.get(self.config.key_field, "") or "").strip()
        if not nombre:
            QMessageBox.warning(self, "Dato requerido", f"El campo '{self.config.key_field}' es obligatorio.")
            return
        if self._existe(nombre):
            QMessageBox.critical(self, "Duplicado", f"Ya existe un registro con '{nombre}'.")
            return
        self._items.append(data)
        self._sort()
        self._populate()

    def _edit(self) -> None:
        item = self._current()
        if not item:
            QMessageBox.warning(self, "Sin selección", "Selecciona un registro para editar.")
            return
        dlg = _GenericEntityForm(self, f"Editar {self.config.entity_name}", self.config.form_fields, initial=item)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.data()
        nombre = (data.get(self.config.key_field, "") or "").strip()
        if not nombre:
            QMessageBox.warning(self, "Dato requerido", f"El campo '{self.config.key_field}' es obligatorio.")
            return
        if self._existe(nombre, excepto=item):
            QMessageBox.critical(self, "Duplicado", f"Ya existe otro registro con '{nombre}'.")
            return
        item.update(data)
        self._sort()
        self._populate()

    def _del(self) -> None:
        item = self._current()
        if not item:
            QMessageBox.warning(self, "Sin selección", "Selecciona un registro para eliminar.")
            return
        nombre = (item.get(self.config.key_field, "") or "").strip()
        if self.config.en_uso_fn is not None:
            try:
                if self.config.en_uso_fn(nombre):
                    QMessageBox.critical(self, "En uso", f"'{nombre}' está en uso y no se puede eliminar.")
                    return
            except Exception:
                pass
        if QMessageBox.question(
            self, "Confirmar", f"¿Eliminar '{nombre}' del catálogo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        self._items = [x for x in self._items if x is not item]
        self._populate()

    def _save_and_close(self) -> None:
        try:
            ok = self.config.save_fn(self._items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar.\n{e}")
            return
        if ok is False:
            QMessageBox.warning(self, "Error", "No se pudieron guardar los cambios.")
            return
        QMessageBox.information(self, "Guardado", "Catálogo guardado correctamente.")
        self.accept()

    # ----------------------------------------------------------- selección
    def _on_double_click(self, *_args) -> None:
        if self.mode == self.MODE_SELECT:
            self._accept_selection()

    def _accept_selection(self) -> None:
        item = self._current()
        if not item:
            QMessageBox.warning(self, "Sin selección", "Selecciona un registro de la lista.")
            return
        self.selected_data = item
        self.seleccion_realizada.emit(item)
        self.accept()

    def get_selected_data(self) -> Optional[Dict[str, Any]]:
        return self.selected_data

    def seleccionar_por_clave(self, valor: str) -> None:
        """Selecciona la fila cuyo key_field coincide con 'valor'."""
        if not valor:
            return
        for row in range(self.table.rowCount()):
            cell = self.table.item(row, 0)
            if cell and (cell.text() or "") == valor:
                self.table.selectRow(row)
                self.table.scrollToItem(cell, QAbstractItemView.ScrollHint.PositionAtCenter)
                break

    def _open_manager(self) -> None:
        dlg = BaseMasterManagerDialog(self, self.config, mode=self.MODE_MANAGE)
        dlg.exec()
        # Recargar la lista tras gestionar el catálogo.
        self._items = list(self.config.load_fn() or [])
        self._sort()
        self._populate()
