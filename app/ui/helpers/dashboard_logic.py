"""
Helpers de presentación del dashboard.

NOTA: las fórmulas de negocio (% docs, % diferencia, vencimientos y estado
finalizado) viven ahora EXCLUSIVAMENTE en app/core/logic/domain_service.py.
Las funciones de este módulo delegan en ese servicio para evitar lógica
duplicada e inconsistente.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable, Tuple, List, Dict
import datetime as _dt

from app.core.models import Licitacion, Documento, Lote
from app.core.logic import domain_service
# Reexport de la jerarquía canónica de hitos (fuente única de verdad)
from app.core.logic.domain_service import KNOWN_MILESTONES_ORDER

@dataclass
class DeadlineInfo:
    key: str
    label: str
    date: _dt.date
    days_left: int

def _parse_date(val) -> Optional[_dt.date]:
    if not val:
        return None
    if isinstance(val, _dt.date):
        return val
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return _dt.datetime.strptime(val.strip(), fmt).date()
            except Exception:
                continue
    return None

def _today() -> _dt.date:
    return _dt.date.today()

def is_finalizada(lic: Licitacion) -> bool:
    """Delegado al servicio de dominio (criterio único de finalización)."""
    return domain_service.evaluar_estado_finalizado(lic)

def sum_montos_ofertados(lic: Licitacion) -> float:
    lotes: List[Lote] = list(getattr(lic, "lotes", []) or [])
    return float(sum((getattr(l, "monto_ofertado", 0.0) or 0.0) for l in lotes))

def percent_docs(lic: Licitacion) -> float:
    """Delegado al servicio de dominio (% de documentos completos)."""
    return domain_service.calcular_porcentaje_documentos(lic)

def percent_diff(lic: Licitacion) -> Optional[float]:
    """Delegado al servicio de dominio. Devuelve None si no hay base de referencia.
    Usa la base de licitación (no la personal) para mantener el comportamiento
    histórico de esta vista."""
    return domain_service.calcular_diferencia_financiera(
        lic, usar_base_personal=False
    ).diferencia_pct

def next_deadline(lic: Licitacion) -> Optional[DeadlineInfo]:
    """Delegado al servicio de dominio. Mantiene el tipo DeadlineInfo de esta capa."""
    pv = domain_service.evaluar_proximo_vencimiento(lic)
    if pv.date is None:
        return None
    return DeadlineInfo(key=pv.key or "", label=pv.label, date=pv.date, days_left=pv.days_left or 0)

def restan_text(info: Optional[DeadlineInfo]) -> str:
    if not info:
        return "Fases cumplidas"  # o "--"
    if info.days_left == 0:
        return "Hoy: " + info.label
    if info.days_left == 1:
        return f"Falta 1 día para: {info.label}"
    return f"Faltan {info.days_left} días para: {info.label}"

def urgency_color(info: Optional[DeadlineInfo]) -> str:
    # Devuelve un color CSS para el fondo según urgencia
    if not info:
        return "#e8f5e9"  # verde suave (completo o sin pendientes)
    d = info.days_left
    if d < 0:
        return "#ffebee"  # rojo claro (vencido)
    if d <= 3:
        return "#fff8e1"  # ámbar (muy próximo)
    if d <= 10:
        return "#f1f8e9"  # verde/amarillo (próximo)
    return "transparent"

def format_money(val: Optional[float], currency: str = "RD$") -> str:
    if val is None:
        return "N/D"
    return f"{currency} {val:,.2f}"

def matches_search(lic: Licitacion, s: str) -> bool:
    s = (s or "").strip().lower()
    if not s:
        return True
    haystack = " ".join([
        lic.numero_proceso or "",
        lic.nombre_proceso or "",
        lic.institucion or "",
        lic.estado or "",
    ]).lower()
    return s in haystack

def contains_lote(lic: Licitacion, lotestr: str) -> bool:
    lotestr = (lotestr or "").strip()
    if not lotestr:
        return True
    for l in lic.lotes or []:
        if lotestr in str(getattr(l, "numero", "")):
            return True
    return False

def matches_estado(lic: Licitacion, estado: str) -> bool:
    estado = (estado or "").strip()
    if not estado or estado == "(Todos)":
        return True
    return (lic.estado or "") == estado

def matches_empresa(lic: Licitacion, empresa: str) -> bool:
    empresa = (empresa or "").strip()
    if not empresa or empresa == "(Todas)":
        return True
    empresas = [(str(e) if hasattr(e, "__str__") else getattr(e, "nombre", "")) for e in (lic.empresas_nuestras or [])]
    return empresa in empresas

def sort_key_for_lic(lic: Licitacion) -> Tuple[int, _dt.date, str]:
    """
    Ordenar: primero por proximidad de hito (el más próximo primero), luego número/nombre.
    Para finalizadas: empujar al final.
    """
    fin = is_finalizada(lic)
    info = next_deadline(lic)
    date = info.date if info else _today()
    return (1 if fin else 0, date, lic.numero_proceso or lic.nombre_proceso or "")