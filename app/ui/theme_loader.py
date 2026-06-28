"""
Sistema de carga de temas y configuración de iconos.
Tema único: Sober Light Emerald (emerald_light).
"""

from PyQt6.QtWidgets import QApplication
from typing import Dict, Optional

from app.ui.theme.emerald_light import get_theme_colors as _emerald_colors, THEME_NAME


# Tema actual (Sober Light Emerald)
THEMES = {
    "emerald_light": {
        "name": THEME_NAME,
        "colors": _emerald_colors(),
    }
}


def get_theme_colors(theme_name: str = "emerald_light") -> Dict[str, str]:
    """
    Obtiene los colores del tema especificado.

    Args:
        theme_name: Nombre del tema

    Returns:
        Diccionario con los colores del tema (por defecto, Sober Light Emerald)
    """
    return THEMES.get(theme_name, {}).get("colors", _emerald_colors())


def apply_theme_with_icons(app: Optional[QApplication] = None, theme_name: str = "emerald_light"):
    """
    Aplica un tema Y configura los iconos SVG.
    
    Args:
        app: QApplication (opcional)
        theme_name: Nombre del tema a aplicar
    """
    # Configurar iconos con los colores del tema
    from app.ui.components.icon_manager import get_icon_manager
    
    colors = get_theme_colors(theme_name)
    icon_manager = get_icon_manager()
    icon_manager.set_theme_colors(colors)
    
    print(f"[INFO] ✓ Iconos SVG configurados con tema {theme_name}")
    
    return colors