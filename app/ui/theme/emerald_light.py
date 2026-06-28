"""
Sober Light Emerald — Modern Light PyQt6 Theme
================================================
Tema claro, limpio y corporativo (estilo Linear / Notion) con acento
Verde Esmeralda Ejecutivo (#059669).

Diseñado para reemplazar al tema oscuro "Titanium Construct v2".

Arquitectura:
- TOKENS: única fuente de verdad de color/diseño (Design Tokens).
- _build_stylesheet(): genera el QSS completo a partir de los TOKENS
  (los widgets dejan de inventarse colores; todo sale de aquí).
- apply_theme(app): función estándar detectada por theme_manager.
- get_theme_colors(): mapa de colores para el IconManager.
- apply_emerald_light_with_icons(app): aplica tema + recolorea iconos.
"""
from __future__ import annotations
from typing import Dict
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


# Título amigable que mostrará el selector de temas
THEME_NAME = "Sober Light Emerald"


# ============================================================================
#  DESIGN TOKENS — única fuente de verdad
#  Cualquier widget/QSS debe leer SIEMPRE de aquí, nunca hardcodear hex.
# ============================================================================
TOKENS: Dict[str, str] = {
    # --- Superficies y fondo ---
    "BACKGROUND":      "#F9F9FB",   # Gris ultra claro (fondo general)
    "SURFACE":         "#FFFFFF",   # Blanco puro (tarjetas, tablas, paneles)
    "SURFACE_HOVER":   "#F4F4F5",   # Hover sutil sobre superficies
    "SURFACE_ALT":     "#FAFAFA",   # Filas alternas / cabeceras suaves
    "BORDER":          "#E4E4E7",   # Gris sutil de 1px

    # --- Texto ---
    "TEXT_PRIMARY":    "#18181B",   # Zinc oscuro (máxima legibilidad)
    "TEXT_MUTED":      "#71717A",   # Gris medio (etiquetas secundarias)
    "TEXT_ON_ACCENT":  "#FFFFFF",   # Texto sobre botones primarios

    # --- Acento primario (Verde Esmeralda Ejecutivo) ---
    "PRIMARY_ACCENT":  "#059669",   # Botones primarios y focos
    "PRIMARY_HOVER":   "#10B981",   # Verde claro sutil (hover)
    "PRIMARY_PRESSED": "#047857",   # Verde profundo (pressed)
    "SELECTION_BG":    "#D1FAE5",   # Fondo menta pastel (selección)

    # --- Estados semánticos (pastel desaturado) ---
    "SUCCESS_TEXT":    "#10B981",   # Ganadas
    "SUCCESS_BG":      "#E6F4EA",
    "ERROR_TEXT":      "#DC2626",   # Perdidas
    "ERROR_BG":        "#FEE2E2",
    "WARNING_TEXT":    "#D97706",   # En curso / aviso
    "WARNING_BG":      "#FEF3C7",
    "INFO_TEXT":       "#2563EB",   # Información / neutral
    "INFO_BG":         "#DBEAFE",

    # --- Auxiliares de control ---
    "SCROLLBAR_HANDLE":     "#D4D4D8",
    "SCROLLBAR_HANDLE_HOV": "#A1A1AA",
    "DISABLED_BG":          "#F4F4F5",
    "DISABLED_TEXT":        "#A1A1AA",
    "DISABLED_BORDER":      "#E4E4E7",

    # --- Radios y tipografía ---
    "RADIUS":          "8px",
    "RADIUS_SM":       "6px",
    "FONT_FAMILY":     '"Segoe UI", "Inter", "Roboto", sans-serif',
    "FONT_SIZE":       "13px",
}


def _build_stylesheet(t: Dict[str, str]) -> str:
    """
    Construye el QSS completo a partir de los Design Tokens.
    Estilo sobrio, plano, con bordes finos y foco esmeralda.
    """
    return f"""
/* ===================================================================
   SOBER LIGHT EMERALD — LIGHT THEME
   Estilo limpio/corporativo (Linear / Notion) con acento esmeralda.
   Generado desde Design Tokens (emerald_light.TOKENS).
   =================================================================== */

/* === BASE & RESET === */
QWidget {{
    font-family: {t['FONT_FAMILY']};
    font-size: {t['FONT_SIZE']};
    color: {t['TEXT_PRIMARY']};
    background-color: {t['BACKGROUND']};
}}

QMainWindow, QDialog {{
    background-color: {t['BACKGROUND']};
}}

/* === FRAMES & CONTAINERS === */
QFrame {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS']};
}}

QGroupBox {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS']};
    margin-top: 1.2em;
    padding-top: 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {t['PRIMARY_ACCENT']};
    font-weight: bold;
    font-size: 13px;
    left: 10px;
}}

/* === BUTTONS === */
QPushButton {{
    background-color: {t['PRIMARY_ACCENT']};
    color: {t['TEXT_ON_ACCENT']};
    border: none;
    border-radius: {t['RADIUS_SM']};
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {t['PRIMARY_HOVER']};
}}

QPushButton:pressed {{
    background-color: {t['PRIMARY_PRESSED']};
}}

QPushButton:disabled {{
    background-color: {t['DISABLED_BG']};
    color: {t['DISABLED_TEXT']};
}}

/* Secondary Button Style: contorno sobrio */
QPushButton[class="secondary"] {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    color: {t['TEXT_PRIMARY']};
}}

QPushButton[class="secondary"]:hover {{
    border-color: {t['PRIMARY_ACCENT']};
    background-color: {t['SURFACE_HOVER']};
}}

QPushButton[class="secondary"]:pressed {{
    background-color: {t['SELECTION_BG']};
}}

/* === INPUT FIELDS === */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS_SM']};
    padding: 8px 12px;
    color: {t['TEXT_PRIMARY']};
    selection-background-color: {t['SELECTION_BG']};
    selection-color: {t['TEXT_PRIMARY']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {t['PRIMARY_ACCENT']};
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {t['DISABLED_BG']};
    color: {t['DISABLED_TEXT']};
}}

QLineEdit::placeholder {{
    color: {t['TEXT_MUTED']};
}}

/* === COMBO BOX === */
QComboBox {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS_SM']};
    padding: 8px 12px;
    color: {t['TEXT_PRIMARY']};
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: {t['PRIMARY_ACCENT']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {t['TEXT_MUTED']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    selection-background-color: {t['SELECTION_BG']};
    selection-color: {t['TEXT_PRIMARY']};
    color: {t['TEXT_PRIMARY']};
    outline: 0;
}}

/* === TABLES === */
QTableWidget, QTableView {{
    background-color: {t['SURFACE']};
    alternate-background-color: {t['SURFACE_ALT']};
    gridline-color: {t['BORDER']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS']};
    selection-background-color: {t['SELECTION_BG']};
    selection-color: {t['TEXT_PRIMARY']};
}}

QTableWidget::item, QTableView::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:hover, QTableView::item:hover {{
    background-color: {t['SURFACE_HOVER']};
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {t['SELECTION_BG']};
    color: {t['TEXT_PRIMARY']};
}}

QHeaderView::section {{
    background-color: {t['SURFACE_ALT']};
    color: {t['TEXT_MUTED']};
    padding: 12px 15px;
    border: none;
    border-bottom: 1px solid {t['BORDER']};
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:hover {{
    background-color: {t['SURFACE_HOVER']};
}}

QTableCornerButton::section {{
    background-color: {t['SURFACE_ALT']};
    border: none;
    border-bottom: 1px solid {t['BORDER']};
}}

/* === TREE / LIST === */
QTreeWidget, QTreeView, QListWidget, QListView {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS']};
    color: {t['TEXT_PRIMARY']};
    outline: 0;
}}

QTreeWidget::item:selected, QTreeView::item:selected,
QListWidget::item:selected, QListView::item:selected {{
    background-color: {t['SELECTION_BG']};
    color: {t['TEXT_PRIMARY']};
}}

QTreeWidget::item:hover, QTreeView::item:hover,
QListWidget::item:hover, QListView::item:hover {{
    background-color: {t['SURFACE_HOVER']};
}}

/* === SCROLLBARS === */
QScrollBar:vertical {{
    background-color: transparent;
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {t['SCROLLBAR_HANDLE']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {t['SCROLLBAR_HANDLE_HOV']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 12px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {t['SCROLLBAR_HANDLE']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {t['SCROLLBAR_HANDLE_HOV']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* === TABS === */
QTabWidget::pane {{
    border: 1px solid {t['BORDER']};
    background-color: {t['SURFACE']};
    border-radius: {t['RADIUS']};
    top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {t['TEXT_MUTED']};
    padding: 10px 20px;
    border-top-left-radius: {t['RADIUS']};
    border-top-right-radius: {t['RADIUS']};
    margin-right: 5px;
    font-weight: 600;
    font-size: 13px;
}}

QTabBar::tab:selected {{
    background-color: {t['SURFACE']};
    color: {t['PRIMARY_ACCENT']};
    border: 1px solid {t['BORDER']};
    border-bottom: none;
}}

QTabBar::tab:hover:!selected {{
    background-color: {t['SURFACE_HOVER']};
    color: {t['TEXT_PRIMARY']};
}}

/* === PROGRESS BAR === */
QProgressBar {{
    background-color: {t['SURFACE_HOVER']};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: {t['TEXT_PRIMARY']};
}}

QProgressBar::chunk {{
    background-color: {t['PRIMARY_ACCENT']};
    border-radius: 3px;
}}

/* === LABELS === */
QLabel {{
    background-color: transparent;
    color: {t['TEXT_PRIMARY']};
}}

/* === MENU BAR === */
QMenuBar {{
    background-color: {t['SURFACE']};
    border-bottom: 1px solid {t['BORDER']};
    color: {t['TEXT_PRIMARY']};
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {t['SURFACE_HOVER']};
}}

QMenuBar::item:pressed {{
    background-color: {t['SELECTION_BG']};
    color: {t['PRIMARY_PRESSED']};
}}

/* === MENU === */
QMenu {{
    background-color: {t['SURFACE']};
    border: 1px solid {t['BORDER']};
    border-radius: {t['RADIUS_SM']};
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    color: {t['TEXT_PRIMARY']};
}}

QMenu::item:selected {{
    background-color: {t['SELECTION_BG']};
    color: {t['PRIMARY_PRESSED']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {t['BORDER']};
    margin: 4px 8px;
}}

/* === TOOLBAR === */
QToolBar {{
    background-color: {t['SURFACE']};
    border: none;
    border-bottom: 1px solid {t['BORDER']};
    spacing: 6px;
    padding: 4px;
}}

QToolBar::separator {{
    background-color: {t['BORDER']};
    width: 1px;
    margin: 4px 8px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px;
    color: {t['TEXT_PRIMARY']};
}}

QToolButton:hover {{
    background-color: {t['SURFACE_HOVER']};
}}

QToolButton:pressed {{
    background-color: {t['SELECTION_BG']};
}}

/* === STATUS BAR === */
QStatusBar {{
    background-color: {t['SURFACE']};
    border-top: 1px solid {t['BORDER']};
    color: {t['TEXT_MUTED']};
}}

/* === CHECKBOXES & RADIO BUTTONS === */
QCheckBox, QRadioButton {{
    spacing: 8px;
    color: {t['TEXT_PRIMARY']};
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid {t['BORDER']};
    background-color: {t['SURFACE']};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border-color: {t['PRIMARY_ACCENT']};
}}

QCheckBox::indicator:checked {{
    background-color: {t['PRIMARY_ACCENT']};
    border-color: {t['PRIMARY_ACCENT']};
}}

QRadioButton::indicator {{
    border-radius: 9px;
}}

QRadioButton::indicator:checked {{
    background-color: {t['PRIMARY_ACCENT']};
    border-color: {t['PRIMARY_ACCENT']};
}}

/* === TOOLTIPS === */
QToolTip {{
    background-color: {t['TEXT_PRIMARY']};
    border: 1px solid {t['TEXT_PRIMARY']};
    color: {t['SURFACE']};
    padding: 6px;
    border-radius: 4px;
}}

/* === SPLITTER === */
QSplitter::handle {{
    background-color: {t['BORDER']};
}}

QSplitter::handle:hover {{
    background-color: {t['PRIMARY_ACCENT']};
}}
"""


def get_theme_colors() -> Dict[str, str]:
    """
    Mapa de colores para el IconManager (mismas claves que usa el resto de
    la app: accent/text/text_sec/window/base/alt/border/success/danger/
    warning/info). Permite recolorear iconos según el tema activo.
    """
    t = TOKENS
    return {
        "accent":    t["PRIMARY_ACCENT"],
        "text":      t["TEXT_PRIMARY"],
        "text_sec":  t["TEXT_MUTED"],
        "window":    t["BACKGROUND"],
        "base":      t["SURFACE"],
        "alt":       t["SURFACE_ALT"],
        "border":    t["BORDER"],
        "success":   t["SUCCESS_TEXT"],
        "danger":    t["ERROR_TEXT"],
        "warning":   t["WARNING_TEXT"],
        "info":      t["INFO_TEXT"],
    }


def apply_theme(app: QApplication) -> None:
    """
    Aplica el tema "Sober Light Emerald" a la aplicación.
    Función estándar detectada automáticamente por theme_manager.

    Args:
        app: Instancia de QApplication.
    """
    t = TOKENS

    # 1) Stylesheet generado desde tokens
    app.setStyleSheet(_build_stylesheet(t))

    # 2) Paleta nativa de Qt (coherente con los tokens)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(t["BACKGROUND"]))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(t["TEXT_PRIMARY"]))
    palette.setColor(QPalette.ColorRole.Base,            QColor(t["SURFACE"]))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(t["SURFACE_ALT"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(t["TEXT_PRIMARY"]))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(t["SURFACE"]))
    palette.setColor(QPalette.ColorRole.Text,            QColor(t["TEXT_PRIMARY"]))
    palette.setColor(QPalette.ColorRole.Button,          QColor(t["SURFACE"]))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(t["TEXT_PRIMARY"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(t["TEXT_MUTED"]))
    palette.setColor(QPalette.ColorRole.Link,            QColor(t["PRIMARY_ACCENT"]))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(t["SELECTION_BG"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(t["TEXT_PRIMARY"]))

    # Estados deshabilitados
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
        QColor(t["DISABLED_TEXT"]),
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
        QColor(t["DISABLED_TEXT"]),
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
        QColor(t["DISABLED_TEXT"]),
    )

    app.setPalette(palette)

    # 3) Recolorear iconos del IconManager con la paleta del tema.
    #    Se hace SIEMPRE aquí para que cualquier vía de aplicación del tema
    #    (arranque, selector de temas vía theme_manager.apply_theme, etc.)
    #    refresque el caché de pixmaps con los colores claros.
    _refresh_icon_theme()


def _refresh_icon_theme() -> None:
    """Invoca set_theme_colors() del IconManager para refrescar el caché."""
    try:
        from app.ui.components.icon_manager import get_icon_manager

        get_icon_manager().set_theme_colors(get_theme_colors())
        print(f"[INFO] ✓ Iconos configurados con tema {THEME_NAME}")
    except Exception as e:
        print(f"[WARNING] No se pudieron configurar iconos: {e}")


def apply_emerald_light_with_icons(app: QApplication) -> None:
    """
    Alias retrocompatible. apply_theme() ya recolorea los iconos, por lo que
    esta función simplemente aplica el tema.
    """
    apply_theme(app)
