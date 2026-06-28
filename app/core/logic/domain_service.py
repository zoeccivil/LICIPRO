"""
Servicio de Dominio Único (Single Source of Truth) — LICIPRO.

Centraliza las fórmulas de negocio que estaban DUPLICADAS e inconsistentes entre:
  - app/core/models.py
  - app/core/logic/status_engine.py
  - app/ui/helpers/dashboard_logic.py
  - app/ui/models/licitaciones_table_model.py

Discrepancias que este módulo elimina:
  * % de documentos: unas versiones contaban solo 'presentado', otras
    'presentado AND NOT requiere_subsanacion'. -> Se unifica a la segunda.
  * % de diferencia: unas usaban base personal, otras solo base de licitación.
  * Próximo vencimiento: distintas jerarquías de hitos y distintos nombres de
    campo de fecha ('fecha_limite' vs 'fecha'/'date'/'deadline'). -> Tolerante.
  * Estado finalizado: una versión marcaba 'fases cumplidas' como finalizada y
    otra como activa. -> Se unifica: 'fases cumplidas' NO finaliza el proceso.

Reglas de diseño:
  * Módulo PURO: sin dependencias de PyQt6 ni de la capa de UI.
  * Duck typing sobre la entidad Licitacion (NO importa models -> sin ciclos).
  * Determinista: mismas entradas -> mismas salidas, sin estado global.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Jerarquía canónica de hitos del cronograma (orden cronológico real del proceso)
# ---------------------------------------------------------------------------
KNOWN_MILESTONES_ORDER: Tuple[str, ...] = (
    "presentacion_ofertas",
    "presentación_ofertas",
    "apertura_ofertas",
    "apertura",
    "informe_evaluacion",
    "notificacion",
    "notificaciones_subsanables",
    "entrega_subsanaciones",
    "habilitacion_sobre_b",
    "apertura_economica",
    "apertura_oferta_economica",
    "adjudicacion",
    "adjudicación",
    "firma_contrato",
)

# Etiquetas legibles por hito (para badges y reportes)
_MILESTONE_LABELS: Dict[str, str] = {
    "presentacion_ofertas": "Presentación de Ofertas",
    "presentación_ofertas": "Presentación de Ofertas",
    "apertura_ofertas": "Apertura de Ofertas",
    "apertura": "Apertura",
    "informe_evaluacion": "Informe de Evaluación",
    "notificacion": "Notificación",
    "notificaciones_subsanables": "Notificación de Subsanables",
    "entrega_subsanaciones": "Entrega de Subsanaciones",
    "habilitacion_sobre_b": "Habilitación Sobre B",
    "apertura_economica": "Apertura Oferta Económica",
    "apertura_oferta_economica": "Apertura Oferta Económica",
    "adjudicacion": "Adjudicación",
    "adjudicación": "Adjudicación",
    "firma_contrato": "Firma de Contrato",
}

# Campos de fecha aceptados dentro de un nodo de cronograma (tolerante a formatos)
_DATE_FIELDS: Tuple[str, ...] = ("fecha_limite", "fecha", "date", "deadline")
_DATE_FORMATS: Tuple[str, ...] = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")

# Palabras clave de estado que implican proceso finalizado/congelado
_FINALIZED_KEYWORDS: Tuple[str, ...] = (
    "adjudicad", "desierta", "cancelada", "descalificad",
)

# Umbrales canónicos de urgencia (días restantes)
URGENCIA_CRITICA_DIAS = 5
URGENCIA_PROXIMA_DIAS = 30


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------
def _today() -> _dt.date:
    return _dt.date.today()


def _parse_date(val: Any) -> Optional[_dt.date]:
    """Parseo tolerante de fechas (date, datetime o string en varios formatos)."""
    if val is None or val == "":
        return None
    if isinstance(val, _dt.datetime):
        return val.date()
    if isinstance(val, _dt.date):
        return val
    s = str(val).strip()[:10]
    for fmt in _DATE_FORMATS:
        try:
            return _dt.datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


def _to_float(val: Any) -> float:
    try:
        return float(val or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _estado_norm(licitacion: Any) -> str:
    return (
        getattr(licitacion, "estatus", None)
        or getattr(licitacion, "estado", None)
        or ""
    ).strip().lower()


# ===========================================================================
# 1) COMPLETITUD DOCUMENTAL
# ===========================================================================
def calcular_porcentaje_documentos(licitacion: Any) -> float:
    """
    Porcentaje de avance documental en [0, 100].

    Un documento cuenta como COMPLETO solo si está PRESENTADO y NO requiere
    subsanación. Si la licitación no tiene documentos, se usa el flag
    'docs_completos_manual' (100 si está marcado, 0 si no).
    """
    docs = list(getattr(licitacion, "documentos_solicitados", None) or [])
    total = len(docs)
    if total == 0:
        return 100.0 if bool(getattr(licitacion, "docs_completos_manual", False)) else 0.0
    completados = sum(
        1
        for d in docs
        if bool(getattr(d, "presentado", False))
        and not bool(getattr(d, "requiere_subsanacion", False))
    )
    return (completados / total) * 100.0


# ===========================================================================
# 2) DIFERENCIA FINANCIERA (oferta vs base)
# ===========================================================================
@dataclass(frozen=True)
class DiferenciaFinanciera:
    base_total: float
    oferta_total: float
    diferencia_abs: float             # oferta - base (negativo = ahorro)
    diferencia_pct: Optional[float]   # None si base_total == 0 (sin referencia)


def calcular_diferencia_financiera(
    licitacion: Any,
    *,
    usar_base_personal: bool = True,
    solo_participados: bool = False,
) -> DiferenciaFinanciera:
    """
    Compara la oferta total contra el presupuesto base.

    - usar_base_personal: usa monto_base_personal (si >0) y cae a monto_base.
    - solo_participados: incluye solo lotes donde participamos o con oferta>0.

    'diferencia_pct' es None cuando la base total es 0 (no hay referencia => N/D).
    """
    lotes = list(getattr(licitacion, "lotes", None) or [])
    if solo_participados:
        lotes = [
            l for l in lotes
            if getattr(l, "participamos", False)
            or _to_float(getattr(l, "monto_ofertado", 0)) > 0
        ]

    base_total = 0.0
    oferta_total = 0.0
    for lote in lotes:
        oferta_total += _to_float(getattr(lote, "monto_ofertado", 0))
        if usar_base_personal:
            base = _to_float(getattr(lote, "monto_base_personal", 0)) or _to_float(
                getattr(lote, "monto_base", 0)
            )
        else:
            base = _to_float(getattr(lote, "monto_base", 0))
        base_total += base

    diferencia_abs = oferta_total - base_total
    diferencia_pct = (diferencia_abs / base_total) * 100.0 if base_total else None
    return DiferenciaFinanciera(base_total, oferta_total, diferencia_abs, diferencia_pct)


def diferencia_porcentual(
    licitacion: Any,
    *,
    usar_base_personal: bool = True,
    solo_participados: bool = False,
) -> float:
    """Conveniencia: % de diferencia como float (0.0 cuando no hay base)."""
    pct = calcular_diferencia_financiera(
        licitacion,
        usar_base_personal=usar_base_personal,
        solo_participados=solo_participados,
    ).diferencia_pct
    return pct if pct is not None else 0.0


# ===========================================================================
# 3) PRÓXIMO VENCIMIENTO / URGENCIA
# ===========================================================================
@dataclass(frozen=True)
class ProximoVencimiento:
    key: Optional[str]
    label: str
    date: Optional[_dt.date]
    days_left: Optional[int]   # None si no hay cronograma con fechas
    urgencia: str              # sin_cronograma|vencida|hoy|critico|proximo|normal
    vencida: bool


def _clasificar_urgencia(days_left: Optional[int]) -> str:
    if days_left is None:
        return "sin_cronograma"
    if days_left < 0:
        return "vencida"
    if days_left == 0:
        return "hoy"
    if days_left <= URGENCIA_CRITICA_DIAS:
        return "critico"
    if days_left <= URGENCIA_PROXIMA_DIAS:
        return "proximo"
    return "normal"


def _milestone_priority(key: str) -> int:
    """Índice de prioridad del hito (menor = más temprano en el proceso)."""
    try:
        return KNOWN_MILESTONES_ORDER.index(key)
    except ValueError:
        return len(KNOWN_MILESTONES_ORDER)  # claves desconocidas al final


def evaluar_proximo_vencimiento(licitacion: Any) -> ProximoVencimiento:
    """
    Calcula el próximo hito relevante del cronograma de forma UNIFICADA.

    Estrategia determinista:
      1. Recolecta todos los hitos con fecha parseable, tolerante a los campos
         'fecha_limite', 'fecha', 'date' o 'deadline'.
      2. Si hay hitos hoy o futuros: elige el MÁS PRÓXIMO (menor fecha; ante
         empate, el de mayor prioridad en KNOWN_MILESTONES_ORDER).
      3. Si todos están vencidos: elige el MÁS RECIENTE (para reportar 'Vencida').
      4. Si no hay fechas: days_left=None, urgencia='sin_cronograma'.
    """
    cronograma = getattr(licitacion, "cronograma", None) or {}
    today = _today()

    futuros: List[Tuple[_dt.date, int, str]] = []
    pasados: List[Tuple[_dt.date, int, str]] = []

    if isinstance(cronograma, dict):
        for key, node in cronograma.items():
            fecha: Optional[_dt.date] = None
            if isinstance(node, dict):
                for f in _DATE_FIELDS:
                    fecha = _parse_date(node.get(f))
                    if fecha:
                        break
            else:
                fecha = _parse_date(node)
            if not fecha:
                continue
            prio = _milestone_priority(str(key))
            (futuros if fecha >= today else pasados).append((fecha, prio, str(key)))

    if futuros:
        # Más próximo: menor fecha; ante empate, mayor prioridad (menor índice).
        fecha, _prio, key = min(futuros, key=lambda t: (t[0], t[1]))
    elif pasados:
        # Más reciente vencido: mayor fecha; ante empate, mayor prioridad.
        fecha, _prio, key = max(pasados, key=lambda t: (t[0], -t[1]))
    else:
        return ProximoVencimiento(
            None, "Sin cronograma", None, None, "sin_cronograma", False
        )

    days_left = (fecha - today).days
    label = _MILESTONE_LABELS.get(key, key.replace("_", " ").strip().capitalize())
    return ProximoVencimiento(
        key, label, fecha, days_left, _clasificar_urgencia(days_left), days_left < 0
    )


def calcular_dias_restantes(licitacion: Any) -> Optional[int]:
    """Días hasta el próximo hito (negativo si vencido, None si sin cronograma)."""
    return evaluar_proximo_vencimiento(licitacion).days_left


# ===========================================================================
# 4) ESTADO FINALIZADO (criterio único de cierre)
# ===========================================================================
def evaluar_estado_finalizado(licitacion: Any) -> bool:
    """
    Criterio ÚNICO para considerar una licitación finalizada / congelada:
      - adjudicada == True, o
      - estado/estatus contiene 'adjudicad', 'desierta', 'cancelada' o
        'descalificad', o
      - ganada == True.

    NOTA: 'Fases cumplidas' NO se considera finalizada (el proceso sigue activo).
    """
    if bool(getattr(licitacion, "adjudicada", False)):
        return True
    if any(k in _estado_norm(licitacion) for k in _FINALIZED_KEYWORDS):
        return True
    if getattr(licitacion, "ganada", None) is True:
        return True
    return False


# ===========================================================================
# 5) MÉTRICAS GLOBALES (KPIs agregados) — consumido por el State Store
# ===========================================================================
def calcular_metricas_globales(licitaciones: Any) -> Dict[str, Any]:
    """
    Calcula los KPIs agregados de una colección de licitaciones de forma
    determinista y centralizada. Es la fuente única para el dashboard, la barra
    de estado y el State Store.

    Devuelve un dict con:
      total, activas, finalizadas, ganadas, perdidas, lotes_ganados,
      tasa_exito (%), monto_base_total, monto_ofertado_total,
      monto_ganado_total, diferencia_total, completitud_promedio (%),
      vencimientos_proximos.
    """
    lics = list(licitaciones or [])
    total = len(lics)
    activas = ganadas = perdidas = lotes_ganados = 0
    monto_base_total = monto_ofertado_total = monto_ganado_total = 0.0
    completitudes: List[float] = []
    vencimientos_proximos = 0

    for lic in lics:
        estado = _estado_norm(lic)

        if not evaluar_estado_finalizado(lic):
            activas += 1
        if "ganada" in estado or "adjudicad" in estado:
            ganadas += 1
        if any(k in estado for k in ("perdida", "descalificad", "rechazad")):
            perdidas += 1

        for lote in (getattr(lic, "lotes", None) or []):
            mo = _to_float(getattr(lote, "monto_ofertado", 0))
            monto_base_total += _to_float(getattr(lote, "monto_base", 0))
            monto_ofertado_total += mo
            if bool(getattr(lote, "ganado_por_nosotros", False)):
                lotes_ganados += 1
                monto_ganado_total += mo

        completitudes.append(calcular_porcentaje_documentos(lic))
        dias = evaluar_proximo_vencimiento(lic).days_left
        if dias is not None and 0 <= dias <= URGENCIA_PROXIMA_DIAS:
            vencimientos_proximos += 1

    denom = ganadas + perdidas
    return {
        "total": total,
        "activas": activas,
        "finalizadas": total - activas,
        "ganadas": ganadas,
        "perdidas": perdidas,
        "lotes_ganados": lotes_ganados,
        "tasa_exito": (ganadas / denom * 100.0) if denom else 0.0,
        "monto_base_total": monto_base_total,
        "monto_ofertado_total": monto_ofertado_total,
        "monto_ganado_total": monto_ganado_total,
        "diferencia_total": monto_ofertado_total - monto_base_total,
        "completitud_promedio": (sum(completitudes) / len(completitudes)) if completitudes else 0.0,
        "vencimientos_proximos": vencimientos_proximos,
    }
