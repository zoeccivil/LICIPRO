"""
Heatmap Delegate - Colorea el fondo según el valor.
"""
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from typing import Optional

from app.ui.theme.emerald_light import TOKENS

# Opacidad máxima del tinte sobre fondo claro. Se mantiene baja para que el
# texto oscuro (#18181B) conserve un contraste 100% legible/accesible.
_MAX_TINT_OPACITY = 0.30


class HeatmapDelegate(QStyledItemDelegate):
    """
    Delegate que colorea el fondo según el valor sobre el tema CLARO:
    - Positivo: tinte verde esmeralda.
    - Negativo: tinte rojo sutil.
    - Neutro: gris claro.
    El texto siempre se dibuja en TEXT_PRIMARY (#18181B) para máxima legibilidad.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._positive_color = QColor(TOKENS["PRIMARY_ACCENT"])  # Verde esmeralda #059669
        self._negative_color = QColor(TOKENS["ERROR_TEXT"])      # Rojo sutil #DC2626
        self._neutral_color = QColor(TOKENS["SURFACE_HOVER"])    # Gris claro #F4F4F5
        self._text_color = QColor(TOKENS["TEXT_PRIMARY"])        # Zinc oscuro #18181B
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        """
        Dibuja la celda con color de fondo según el valor.
        """
        # Obtener valor
        value = index.data(Qt.ItemDataRole.DisplayRole)
        
        # Convertir a float
        try:
            if isinstance(value, str):
                value = value.replace('%', '').strip()
                percentage = float(value)
            elif isinstance(value, (int, float)):
                percentage = float(value)
            else:
                percentage = 0.0
        except:
            percentage = 0.0
        
        # Elegir color según valor (copia para no mutar el color base cacheado)
        if percentage > 0:
            bg_color = QColor(self._positive_color)
        elif percentage < 0:
            bg_color = QColor(self._negative_color)
        else:
            bg_color = QColor(self._neutral_color)

        # Área de la celda
        rect = option.rect

        # Dibujar fondo con transparencia
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Ajustar opacidad según magnitud, con tope bajo (_MAX_TINT_OPACITY)
        # para que el tinte sea suave sobre blanco y el texto oscuro quede legible.
        opacity = min(abs(percentage) / 100.0, 1.0) * _MAX_TINT_OPACITY
        bg_color.setAlphaF(opacity)

        painter.fillRect(rect, bg_color)
        
        # Dibujar texto
        painter.setPen(QPen(self._text_color))
        text = f"{percentage:+.1f}%" if percentage != 0 else "0.0%"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        
        painter.restore()