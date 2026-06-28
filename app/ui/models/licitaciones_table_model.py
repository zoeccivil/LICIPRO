from __future__ import annotations

from typing import Any, List, Optional, Sequence, Dict
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, QRect
from PyQt6.QtGui import QColor, QBrush, QIcon, QPixmap, QPainter, QFont, QPen
from PyQt6.QtCore import Qt, QVariant, QModelIndex
from PyQt6.QtGui import QColor, QBrush, QFont

from app.ui.theme.emerald_light import TOKENS

# --- Colores semánticos derivados del tema activo (Design Tokens) ---
# Texto de alertas
COLOR_DANGER = QColor(TOKENS["ERROR_TEXT"])      # Rojo sutil (vencida / negativo / perdida)
COLOR_SUCCESS = QColor(TOKENS["SUCCESS_TEXT"])   # Verde esmeralda (positivo / ganada)
COLOR_INFO = QColor(TOKENS["INFO_TEXT"])         # Azul info (hoy / en curso)
COLOR_WARNING = QColor(TOKENS["WARNING_TEXT"])   # Ámbar (faltan pocos días)
COLOR_MUTED = QColor(TOKENS["TEXT_MUTED"])       # Gris medio (desierta)
# Fondos de fila (tema claro)
COLOR_ROW_ALT = QColor(TOKENS["SURFACE_HOVER"])  # #F4F4F5 — filas alternas claras

IS_FINALIZADA_ROLE = Qt.ItemDataRole.UserRole + 1001
ROLE_RECORD_ROLE = Qt.ItemDataRole.UserRole + 1002
ESTADO_TEXT_ROLE = Qt.ItemDataRole.UserRole + 1003
EMPRESA_TEXT_ROLE = Qt.ItemDataRole.UserRole + 1004
LOTES_TEXT_ROLE = Qt.ItemDataRole.UserRole + 1005
PROCESO_NUM_ROLE = Qt.ItemDataRole.UserRole + 1010
CARPETA_PATH_ROLE = Qt.ItemDataRole.UserRole + 1011
DOCS_PROGRESS_ROLE = Qt.ItemDataRole.UserRole + 1012
DIFERENCIA_PCT_ROLE = Qt.ItemDataRole.UserRole + 1013
ROW_BG_ROLE = Qt.ItemDataRole.UserRole + 1201


class LicitacionesTableModel(QAbstractTableModel):
    HEADERS = [
        "Código",
        "Nombre Proceso",
        "Empresa",
        "Restan",
        "% Docs",
        "% Dif.",
        "Monto Ofertado",
        "Estatus",
        "Lotes",
    ]

    def __init__(self, status_engine, parent=None):
        super().__init__(parent)
        self._rows: List[Any] = []
        self._status_engine = status_engine
        # Cache de íconos por clave
        self._icon_cache: Dict[str, QIcon] = {}

    def set_rows(self, licitaciones: Sequence[Any]):
        self.beginResetModel()
        self._rows = list(licitaciones or [])
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            try:
                return self.HEADERS[section]
            except Exception:
                return QVariant()
        return QVariant()

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def _empresas_text(self, lic) -> str:
        emps = getattr(lic, "empresas_nuestras", None) or getattr(lic, "empresas", None) or []
        names = []
        for e in emps:
            n = getattr(e, "nombre", None) or (e if isinstance(e, str) else None)
            if n:
                names.append(str(n))
        return ", ".join(names)

    def _lotes_text(self, lic) -> str:
        lotes = getattr(lic, "lotes", []) or []
        try:
            return ", ".join([str(getattr(l, "numero", "")) for l in lotes if getattr(l, "numero", "")])
        except Exception:
            return ""

    # ---------------- Íconos para Estatus ----------------
    def _badge_icon(self, color: QColor, glyph: str, size: int = 16) -> QIcon:
        # Clave de cache
        key = f"{color.name()}|{glyph}|{size}"
        if key in self._icon_cache:
            return self._icon_cache[key]

        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)

        # Círculo
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawEllipse(0, 0, size - 1, size - 1)

        # Glifo en blanco
        pen = QPen(QColor("#FFFFFF"))
        p.setPen(pen)
        font = QFont()
        # Ajusto tamaño relativo al badge
        font.setPointSize(max(8, int(size * 0.68)))
        font.setBold(True)
        p.setFont(font)
        p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, glyph)
        p.end()

        icon = QIcon(pm)
        self._icon_cache[key] = icon
        return icon

    def _status_icon_for_text(self, text: str) -> Optional[QIcon]:
        n = (text or "").lower()
        # Verde ✓ para ganada
        if "adjudicada" in n and "ganada" in n:
            return self._badge_icon(COLOR_SUCCESS, "✓")
        # Rojo ✕ para perdida/cancelada/descalificada
        if any(k in n for k in ("perdida", "cancel", "descalific")):
            return self._badge_icon(COLOR_DANGER, "✕")
        # Gris – para desierta
        if "desierta" in n:
            return self._badge_icon(COLOR_MUTED, "–")
        # Sin ícono para el resto
        return None

    # -----------------------------------------------------

    def get_dias_restantes(self, lic) -> Optional[int]:
        """
        Días hasta el próximo hito relevante del cronograma (negativo si vencido,
        None si no hay cronograma). Fuente única de verdad: servicio de dominio.
        """
        from app.core.logic.domain_service import calcular_dias_restantes
        return calcular_dias_restantes(lic)



    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()
        lic = self._rows[row]

        # --- 1. ROLES PERSONALIZADOS ---
        if role == ROLE_RECORD_ROLE:
            return lic
        if role == PROCESO_NUM_ROLE:
            return getattr(lic, "numero_proceso", None) or getattr(lic, "numero", None)
        if role == CARPETA_PATH_ROLE:
            return getattr(lic, "carpeta_destino", None) or getattr(lic, "carpeta", None)
        if role == ESTADO_TEXT_ROLE:
            texto, _ = self._status_engine.estatus_y_color(lic)
            return texto
        if role == EMPRESA_TEXT_ROLE:
            return self._empresas_text(lic)
        if role == LOTES_TEXT_ROLE:
            return self._lotes_text(lic)
        if role == DOCS_PROGRESS_ROLE:
            try:
                return float(getattr(lic, "get_porcentaje_completado")())
            except:
                return 0.0
        if role == DIFERENCIA_PCT_ROLE:
            try:
                return float(getattr(lic, "get_diferencia_porcentual")(usar_base_personal=True))
            except:
                return float("nan")
        if role == IS_FINALIZADA_ROLE:
            try:
                return bool(self._status_engine.is_finalizada(lic))
            except:
                return False
        if role == ROW_BG_ROLE:
            # Color de fondo de fila según estado (pasteles claros del status_engine).
            # Lo consume RowColorDelegate para pintar toda la fila.
            return getattr(lic, "__row_bg__", None)

        # --- 1b. FONDO DE FILAS ALTERNAS (tema claro) ---
        if role == Qt.ItemDataRole.BackgroundRole:
            # Si la fila tiene color de estado explícito, lo pinta RowColorDelegate
            # vía ROW_BG_ROLE; aquí no interferimos.
            if getattr(lic, "__row_bg__", None):
                return QVariant()
            # Filas alternas con gris claro del token (#F4F4F5); pares en blanco (SURFACE).
            if row % 2 == 1:
                return QBrush(COLOR_ROW_ALT)
            return QVariant()

        # --- 2. FORMATO DE FUENTE (Negrita en Código) ---
        if role == Qt.ItemDataRole.FontRole:
            if col == 0:  # Columna Código
                font = QFont()
                font.setBold(True)
                return font

        # --- 3. COLORES DE TEXTO (ForegroundRole) ---
        if role == Qt.ItemDataRole.ForegroundRole:
            # --- Columna Restan (idx 3) ---
            if col == 3:
                dias = self.get_dias_restantes(lic)
                if dias is not None:
                    if dias < 0: return QBrush(COLOR_DANGER)   # Rojo sutil (Vencida)
                    if dias == 0: return QBrush(COLOR_INFO)    # Azul info (Hoy)
                    if dias <= 5: return QBrush(COLOR_WARNING) # Ámbar (Faltan pocos días)

            # --- Columna % Dif (idx 5) ---
            if col == 5:
                val = self.data(index, DIFERENCIA_PCT_ROLE)
                if val == val: # Verificar que no sea NaN
                    if val < 0: return QBrush(COLOR_DANGER)  # Rojo sutil (Negativo)
                    if val > 0: return QBrush(COLOR_SUCCESS) # Verde esmeralda (Positivo)

            # --- Columna Estatus (idx 7) ---
            if col == 7:
                txt = str(self.data(index, ESTADO_TEXT_ROLE) or "").lower()
                # Verde para Entregados o Ganadas
                if any(k in txt for k in ("entregado", "ganada", "adjudicada")):
                    return QBrush(COLOR_SUCCESS)
                # Rojo para Perdidas o Canceladas
                if any(k in txt for k in ("perdida", "cancel", "descalific")):
                    return QBrush(COLOR_DANGER)
                # Azul para En Curso
                if "en curso" in txt:
                    return QBrush(COLOR_INFO)
                # Gris para Desiertas
                if "desierta" in txt:
                    return QBrush(COLOR_MUTED)

        # --- 4. ÍCONOS EN ESTATUS (DecorationRole) ---
        if role == Qt.ItemDataRole.DecorationRole and col == 7:
            try:
                txt = str(self.data(index, ESTADO_TEXT_ROLE) or "")
                return self._status_icon_for_text(txt)
            except:
                pass

        # --- 5. TEXTO A MOSTRAR (DisplayRole) ---
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0: return getattr(lic, "numero_proceso", None) or getattr(lic, "numero", "")
            if col == 1: return getattr(lic, "nombre_proceso", None) or getattr(lic, "nombre", "")
            if col == 2: return self._empresas_text(lic)
            if col == 3:
                dias = self.get_dias_restantes(lic)
                if dias is None: return "Sin cronograma"
                if dias < 0: return f"Vencida hace {abs(dias)} día{'s' if abs(dias) != 1 else ''}"
                if dias == 0: return "Hoy"
                return f"Falta{'n' if dias > 1 else ''} {dias} día{'s' if dias > 1 else ''}"
            if col == 4:
                v = self.data(index, DOCS_PROGRESS_ROLE)
                return f"{int(round(float(v)))}%"
            if col == 5:
                v = self.data(index, DIFERENCIA_PCT_ROLE)
                if v != v: return "N/D"
                return f"{float(v):.1f}%"
            if col == 6:
                try:
                    v = float(getattr(lic, "get_oferta_total")() or 0.0)
                    return f"RD$ {v:,.2f}" if v > 0 else "N/D"
                except: return "N/D"
            if col == 7: return str(self.data(index, ESTADO_TEXT_ROLE) or "")
            if col == 8: return self._lotes_text(lic)

        return QVariant()

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        if role == ROW_BG_ROLE:
            lic = self._rows[index.row()]
            setattr(lic, "__row_bg__", value)
            self.dataChanged.emit(
                index.siblingAtColumn(0),
                index.siblingAtColumn(self.columnCount() - 1),
                [ROW_BG_ROLE],
            )
            return True
        return False
    
    def proximo_vencimiento_info(lic):
        import datetime
        hoy = datetime.date.today()
        fechas = []
        prioridad = [
            "presentacion_ofertas", "presentación_ofertas", "apertura_ofertas",
            "apertura", "ofertas", "adjudicacion", "adjudicación"
        ]
        cronograma = getattr(lic, "cronograma", {}) or {}
        for key in prioridad:
            for k, v in cronograma.items():
                if key in str(k).lower() and v:
                    fecha_str = v.get("fecha_limite") if isinstance(v, dict) else v
                    if fecha_str:
                        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                            try:
                                d = datetime.datetime.strptime(str(fecha_str).strip()[:10], fmt).date()
                                fechas.append((d, k, fecha_str))
                                break
                            except Exception:
                                continue
        if not fechas:
            for k, v in cronograma.items():
                fecha_str = v.get("fecha_limite") if isinstance(v, dict) else v
                if fecha_str:
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            d = datetime.datetime.strptime(str(fecha_str).strip()[:10], fmt).date()
                            fechas.append((d, k, fecha_str))
                            break
                        except Exception:
                            continue
        if not fechas:
            return None, None, None
        fechas.sort(key=lambda x: x[0])
        for fecha, nombre, fecha_str in fechas:
            if fecha >= hoy:
                return (fecha - hoy).days, nombre, fecha_str
        fecha, nombre, fecha_str = fechas[-1]
        return (fecha - hoy).days, nombre, fecha_str
    
    def _sync_right_panel_with_selection(self):
        # Selección activa o finalizada según tab
        view = self.tableActivas if self.tabs.currentIndex() == 0 else self.tableFinalizadas
        if not view.selectionModel():
            self.nextDueArea.setText("-- Selecciona una Fila --")
            return
        sel = view.selectionModel().selectedRows()
        if not sel:
            self.nextDueArea.setText("-- Selecciona una Fila --")
            return
        idx = sel[0]
        src_idx = view.model().mapToSource(idx)
        lic = src_idx.siblingAtColumn(0).data(ROLE_RECORD_ROLE)
        if lic is None:
            self.nextDueArea.setText("-- Selecciona una Fila --")
            return

        import datetime

        hoy = datetime.date.today()
        cronograma = getattr(lic, "cronograma", {}) or {}
        eventos_futuros = []
        for k, v in cronograma.items():
            fecha_str = None
            estado = None
            if isinstance(v, dict):
                fecha_str = v.get("fecha_limite")
                estado = v.get("estado", "")
            else:
                fecha_str = v

            if fecha_str and ("pendiente" in (estado or "").lower() or not estado):
                try:
                    fecha = datetime.datetime.strptime(str(fecha_str).strip()[:10], "%Y-%m-%d").date()
                    eventos_futuros.append((fecha, k, fecha_str))
                except Exception:
                    continue

        if eventos_futuros:
            eventos_futuros.sort(key=lambda x: x[0])
            fecha, nombre_hito, fecha_str = eventos_futuros[0]
            diferencia = (fecha - hoy).days
            lic_nombre = getattr(lic, "nombre_proceso", None) or getattr(lic, "nombre", None) or ""
            header = f"<b>{lic_nombre}</b><br>"

            if diferencia < 0:
                color = TOKENS["ERROR_TEXT"]
                texto = f"{header}<span style='color:{color};font-weight:bold'>Vencida hace {abs(diferencia)} día{'s' if abs(diferencia)!=1 else ''} para:<br><b>{nombre_hito.replace('_', ' ').capitalize()}</b> <br><span style='font-size:11pt'>({fecha_str})</span></span>"
            elif diferencia == 0:
                color = TOKENS["WARNING_TEXT"]
                texto = f"{header}<span style='color:{color};font-weight:bold'>Hoy:<br><b>{nombre_hito.replace('_', ' ').capitalize()}</b> <br><span style='font-size:11pt'>({fecha_str})</span></span>"
            elif diferencia <= 7:
                color = TOKENS["WARNING_TEXT"]
                texto = f"{header}<span style='color:{color};font-weight:bold'>Faltan {diferencia} días para:<br><b>{nombre_hito.replace('_', ' ').capitalize()}</b> <br><span style='font-size:11pt'>({fecha_str})</span></span>"
            elif diferencia <= 30:
                color = TOKENS["INFO_TEXT"]
                texto = f"{header}<span style='color:{color};font-weight:bold'>Faltan {diferencia} días para:<br><b>{nombre_hito.replace('_', ' ').capitalize()}</b> <br><span style='font-size:11pt'>({fecha_str})</span></span>"
            else:
                color = TOKENS["SUCCESS_TEXT"]
                texto = f"{header}<span style='color:{color};font-weight:bold'>Faltan {diferencia} días para:<br><b>{nombre_hito.replace('_', ' ').capitalize()}</b> <br><span style='font-size:11pt'>({fecha_str})</span></span>"
            self.nextDueArea.setText(texto)
            return

        self.nextDueArea.setText("<b>Sin cronograma</b>")