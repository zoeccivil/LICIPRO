# Resumen Completo y Detallado de la Aplicación **LICIPRO**

> **Gestor de Licitaciones — Zoeccivil**
> Documento técnico-funcional para análisis y elaboración de prompt de mejora.
> Generado a partir de la lectura directa del código fuente (146 archivos `.py`).

---

## Índice

1. [Propósito general y qué hace la app](#1-propósito-general-y-qué-hace-la-app)
2. [Stack tecnológico](#2-stack-tecnológico)
3. [Arquitectura general (capas y carpetas)](#3-arquitectura-general-capas-y-carpetas)
4. [Punto de entrada y arranque (`modern_main.py`)](#4-punto-de-entrada-y-arranque-modern_mainpy)
5. [Capa de datos: backends, adaptadores, caché, tiempo real, backups](#5-capa-de-datos-backends-adaptadores-caché-tiempo-real-backups)
6. [Modelo de dominio (entidades y campos)](#6-modelo-de-dominio-entidades-y-campos)
7. [Lógica de negocio y todas las fórmulas de cálculo](#7-lógica-de-negocio-y-todas-las-fórmulas-de-cálculo)
8. [Ventanas, vistas y pestañas (UI)](#8-ventanas-vistas-y-pestañas-ui--manual-técnico)
9. [Catálogo completo de diálogos (39) y duplicidades](#9-catálogo-completo-de-diálogos-39-y-duplicidades)
10. [Sistema visual: temas, paleta, QSS, widgets, delegates, modelos, iconos](#10-sistema-visual-temas-paleta-qss-widgets-delegates-modelos-iconos)
11. [Reportes, exportaciones y generación documental](#11-reportes-exportaciones-y-generación-documental)
12. [Importación de datos](#12-importación-de-datos-importerpy--excelimporter)
13. [Flujos de uso típicos](#13-flujos-de-uso-típicos)
14. [Diagnóstico: fortalezas, problemas y deuda técnica](#14-diagnóstico-fortalezas-problemas-y-deuda-técnica)
15. [Áreas de mejora priorizadas](#15-áreas-de-mejora-priorizadas)
16. [Prompt base sugerido para mejorar la aplicación](#16-prompt-base-sugerido-para-mejorar-la-aplicación)

---

## 1. Propósito general y qué hace la app

**LICIPRO** es una aplicación de **escritorio (PyQt6)** para gestionar de forma integral procesos de **licitaciones públicas**. Permite registrar, organizar, analizar y dar seguimiento a:

- **Licitaciones** (procesos completos con estados, fases y cronograma).
- **Lotes** por licitación (montos base, montos ofertados, participación, ganadores).
- **Documentos** solicitados (checklist, presentación, subsanación, responsables).
- **Competidores/oferentes** y sus ofertas por lote.
- **Empresas propias, instituciones convocantes, responsables** (catálogos maestros).
- **Tareas** operativas (estilo Kanban), **auditoría** de cambios y **subsanaciones**.
- **KPIs**, reportes ejecutivos, análisis financiero y análisis de paquetes de ofertas.

Combina: gestión documental + seguimiento de pliegos + control de estados + analítica financiera + visualización (dashboards/gráficas) + generación de expedientes (PDF/ZIP) + importación masiva (Excel/CSV).

> Es una herramienta operativa y analítica para un departamento de licitaciones.

---

## 2. Stack tecnológico

| Área | Tecnología |
|------|-----------|
| Lenguaje | Python 3 |
| UI | PyQt6 (`QMainWindow`, `QDialog`, `QStackedWidget`, `QTableView`, delegates, QSS) |
| Gráficas | matplotlib (`FigureCanvas` embebido) cuando está disponible |
| BD principal | Google Firestore (`firebase-admin` / `google-cloud-firestore`) |
| Backends alternativos | SQLite (legacy `DatabaseManager`) y MySQL (SQLAlchemy + PyMySQL) |
| Generación documental | openpyxl (Excel), reportlab/PyPDF (PDF), python-docx + Jinja2 (DOCX/HTML), QR para portadas |
| Empaquetado | PyInstaller (`.spec`; soporta `sys._MEIPASS` para temas/iconos) |
| Configuración | JSON (`lic_config.json`, `licitaciones_config`), variables `.env` (python-dotenv) |

> **Nota de modelo:** la app **NO usa ningún modelo de lenguaje (LLM)** actualmente; toda la "inteligencia" es lógica de negocio determinista en Python.

---

## 3. Arquitectura general (capas y carpetas)

**Patrón general:** MVC con señales/slots de Qt + inyección de dependencias (el `DatabaseAdapter` y el `TableModel` se inyectan a las vistas).

```text
modern_main.py ............ Punto de entrada de la UI MODERNA (actual).
app/main.py ............... Punto de entrada de la UI LEGACY (anterior).

app/core/ ................. Lógica de negocio y persistencia
  models.py ............... Entidades de dominio + cálculos de licitación.
  logic/status_engine.py .. Estados, colores y vencimientos.
  logic/reporter.py ....... Reporte PDF de subsanaciones.
  logic/pdf_generator.py .. Expediente PDF (portada + índice + merge de PDFs).
  logic/zip_generator.py .. Expediente ZIP por categoría + index.csv.
  reporting.py ............ Cálculo de KPIs y exportación a Excel.
  reporting/report_generator.py . Reportes Excel/PDF (resultados, paquetes, evaluación).
  importer.py ............. Importación Excel/CSV (lotes, documentos, etc.).
  competitor_insights.py .. Inteligencia competitiva (win-rate, estadísticas de precio).
  template_engine.py ...... Generación de documentos desde plantillas (DOCX/HTML).
  tasks_manager.py ........ Gestión de tareas (Kanban) en Firestore.
  audit_logger.py ......... Auditoría de cambios (create/update/delete).
  utils.py ................ Utilidades (normalización de lotes, rutas Dropbox, etc.).
  db_adapter*.py .......... Adaptadores de BD (Firestore/SQLite/MySQL/Offline) + selector.
  firebase_adapter.py ..... Acceso de bajo nivel a Firestore (get/add/set/subscribe).
  firestore_connection.py . Verificación de conexión y fallback offline.
  firestore_backup.py ..... Backups comprimidos (gzip) y modo offline.
  config.py / lic_config.py / app_settings.py . Configuración persistente.
  log_utils.py ............ Logger a logs/app_YYYYMMDD.log.

app/ui/
  windows/ ................ Ventanas principales (moderna + legacy).
  views/ .................. Vistas (dashboard, listado, reportes).
  tabs/ ................... Pestañas del detalle de licitación.
  dialogs/ ................ 39 diálogos (CRUD, selección, evaluación, etc.).
  widgets/modern_widgets.py . Widgets reutilizables (StatCard, StatusBadge, etc.).
  delegates/ ............. Pintado de tablas (progress bars, heatmaps, colores fila).
  models/ ................ Modelos/proxies de tabla (filtros, estado).
  theme/ ................. 12 temas + theme_manager + utilidades + iconos.
  components/icon_manager.py . Generador de iconos por QPainter (sin QtSvg).
  helpers/dashboard_logic.py . Helpers de filtrado/orden/formato del dashboard.
```

> ⚠️ **Observación clave:** **coexisten DOS UI completas** (moderna y legacy), lo que genera duplicación significativa de ventanas y diálogos (ver secciones 8, 9 y 14).

---

## 4. Punto de entrada y arranque (`modern_main.py`)

Secuencia de arranque de la app moderna:

1. `load_dotenv()` — carga variables de entorno (`.env`).
2. Crea `QApplication`; `setApplicationName="Gestor de Licitaciones"`, organización `"Zoeccivil"`.
3. Aplica el tema `apply_titanium_construct_v2(app)` (tema oscuro principal).
4. `show_splash_screen(app)`: splash dibujado con `QPainter` (degradado `#1E1E1E → #2D2D30`, título "GESTOR DE LICITACIONES", "Modern UI Edition v4.0", "v4.0.0").
5. `initialize_database()`:
   - Lee `APP_DB_BACKEND` (default `"firestore"`).
   - Si firestore → `_initialize_firebase()` con esta **cascada de credenciales**:
     1. `lic_config.json` (`firebase_credentials_path`)
     2. `GOOGLE_APPLICATION_CREDENTIALS`
     3. `LICITACIONES_FIRESTORE_KEY_JSON` (JSON embebido)
     4. Si nada funciona → abre `firebase_config_dialog` (asistente).
   - Inicializa `firebase_admin`, crea `firestore.client` y lo inyecta al `firebase_adapter`.
   - `get_database_adapter(db_client)` → adaptador abierto (`db.open()`).
   - Manejo de errores detallado por backend (mensajes guía para firestore/sqlite/mysql).
6. Crea `ModernMainWindow(db=db)`, cierra splash y muestra la ventana.
7. Al cerrar: `db.close()` (cierra conexión y suscripciones).

> Si la BD falla, ofrece reintentar configuración de Firebase y pide reiniciar.

---

## 5. Capa de datos: backends, adaptadores, caché, tiempo real, backups

### 5.1 Selección de backend (`db_adapter_selector.py`)

Variable de entorno `APP_DB_BACKEND` (default `"firestore"`):

| Valor | Adaptador | Características |
|-------|-----------|----------------|
| `firestore` | `DatabaseAdapter` (`db_adapter.py`) | Tiempo real + caché `.pkl` |
| `sqlite` | `SQLiteDatabaseAdapter` | Envuelve el `DatabaseManager` legacy. Ruta: `SQLITE_DB_PATH` o `LICITACIONES_GENERALES.db` |
| `mysql` | `DatabaseAdapter` (`db_adapter_mysql.py`) | SQLAlchemy + PyMySQL, pool 10-30 conexiones, vars `DB_HOST/PORT/USER/PASSWORD/NAME` |

Toda la UI consume una **interfaz común, agnóstica del backend**.

### 5.2 Interfaz común del `DatabaseAdapter` (métodos principales)

- **Ciclo de vida:** `open()`, `close()`
- **Licitaciones:** `load_all_licitaciones(force_refresh=False)`, `list_licitaciones()`, `load_licitacion_by_id()`, `load_licitacion_by_numero()`, `save_licitacion()` *(upsert robusto + validaciones)*, `delete_licitacion()`, `subscribe_to_licitaciones(callback)`
- **Catálogos:** `get/save_empresas_maestras`, `get/save_instituciones_maestras`, `get/save_documentos_maestros`, `get/save_competidores_maestros`, `get/save_responsables_maestros`, `save_master_lists(**kwargs)`, `_get_master_table(name)`
- **Fase A / Fallas:** `get_fallas_fase_a()`, `insertar_falla_por_ids()`, `eliminar_fallas_por_ids()`, `eliminar_falla_por_campos()`, `actualizar_comentario_falla()`, `obtener_historial_subsanacion()`
- **Documentos:** `guardar_orden_documentos(lic_id, pares)`
- **Lotes/ganador:** `marcar_ganador_lote()`, `borrar_ganador_lote()`
- **Utilidades:** `is_institucion_en_uso()`, `is_empresa_en_uso()`, `get_all_data()`, `get_all_licitaciones_basic_info()`, `get_setting()/set_setting()`, `run_sanity_checks()`, `auto_repair(issues)`

### 5.3 Caché local (`.pkl`) — sólo Firestore

- **Archivo:** `.cache/licitaciones_firestore.pkl` (raíz del proyecto).
- **Validez:** 2 horas (`timedelta(hours=2)`).
- **Estrategia de `load_all_licitaciones()`:**
  1. `force_refresh` → invalida y consulta Firestore.
  2. Si ya está en memoria (`_all_licitaciones`) → retorna RAM.
  3. Si hay `.pkl` válido (<2h) → carga desde disco.
  4. Si no → consulta Firestore y guarda `.pkl`.
- Se invalida tras save/delete de licitaciones y cambios de maestros.
- **Motivo:** Firestore cobra por lectura; el caché reduce costos y acelera ~1000×.
- ⚠️ **Importante:** la suscripción en tiempo real **NO** invalida el caché (persiste entre sesiones).

### 5.4 Tiempo real (Firestore)

- `firebase_adapter.subscribe_collection(collection, callback)` usa `on_snapshot`.
- `DatabaseAdapter.subscribe_to_licitaciones()` mapea dicts → `Licitacion` y llama callback.
- La UI moderna (`ModernMainWindow`) y la legacy se suscriben para refrescar sin recargar.

### 5.5 Backups y modo offline (`firestore_backup.py` / `db_adapter_offline.py`)

- `FirestoreBackupManager`: respalda **todas** las colecciones a JSON comprimido (gzip): `licitaciones`, `empresas/instituciones/documentos/competidores/responsables_maestros`, `fallas_fase_a`, `subsanaciones_eventos`, `tasks`, `audits`, `competitors`, `settings`.
- `create_backup()`, `load_backup()`, `restore_from_backup(merge)`, `list_backups()`.
- Formato `backup_YYYYMMDD_HHMMSS.json.gz`; limpieza automática (últimos 30 días).
- `OfflineDatabaseAdapter`: solo-lectura desde último backup; lanza `RuntimeError` si se intenta guardar/eliminar sin conexión.

### 5.6 Configuración

- `lic_config.json` (raíz): `firebase_credentials_path`, `firebase_storage_bucket`. En ejecutable (frozen) usa la carpeta del `.exe` como base.
- `app_settings`: estado de UI en `~/.licitaciones/licitaciones_config.json` (geometría de ventanas, tamaños de splitters, tab activo, tema `ui_theme`).
- `config.py` (legacy): `db_path`, detección automática de Dropbox.

### 5.7 Estructura de datos / relaciones

- **Firestore** = documentos **anidados** (desnormalizado): una `licitacion` contiene arrays de `lotes`, `oferentes_participantes` (con `ofertas_por_lote`), `documentos_solicitados`, `cronograma` (objeto), `fallas_fase_a`, `parametros_evaluacion`.
- **MySQL** = tablas **relacionales** normalizadas (`licitaciones`, `lotes`, `documentos`, `oferentes`, `ofertas_lote_oferentes`, `licitacion_empresas_nuestras`, etc.).
- **SQLite** = híbrido (legacy) con JSON para relaciones complejas.
- **Canonicalización:** `_canon()` normaliza `numero_proceso` (mayúsculas, colapsa espacios) y se guarda en `numero_canon` para búsquedas robustas y upsert.
- Catálogos maestros se referencian por **NOMBRE** (`empresa_nuestra`, `institucion`, `responsable`, `oferente.nombre`) — claves lógicas, no IDs.

---

## 6. Modelo de dominio (entidades y campos)

> Definidas en `app/core/models.py`.

**LOTE:** `id`, `numero`, `nombre`, `monto_base`, `monto_base_personal`, `monto_ofertado`, `participamos` (bool), `fase_A_superada` (bool), `ganador_nombre`, `ganado_por_nosotros` (bool), `empresa_nuestra`.

**OFERENTE (competidor):** `nombre`, `comentario`, `ofertas_por_lote` (lista de dicts con: `lote_numero`, `monto`, `paso_fase_A`, `plazo_entrega`, `garantia_meses`).
Método `get_monto_total_ofertado(solo_habilitados)`: suma montos (si `solo_habilitados`, sólo los que pasaron Fase A).

**DOCUMENTO:** `id`, `codigo`, `nombre`, `categoria`, `comentario`, `presentado` (bool), `subsanable` (`"Subsanable"/"No Subsanable"`), `ruta_archivo`, `empresa_nombre`, `responsable`, `revisado` (bool), `obligatorio` (bool), `orden_pliego`, `requiere_subsanacion` (bool).

**EMPRESA:** `nombre` (entidad simple; el catálogo maestro tiene `rnc`, `rpe`, teléfono, correo, dirección, representante, cargo).

**LICITACION (entidad central):** `id`, `nombre_proceso`, `numero_proceso`, `institucion`, `empresas_nuestras` (lista), `estado`, `fase_A_superada`, `fase_B_superada`, `adjudicada`, `adjudicada_a`, `motivo_descalificacion`, `docs_completos_manual`, `last_modified`, `fecha_creacion`, `fallas_fase_a` (lista), `_parametros_evaluacion` (dict), `lotes` (lista de Lote), `oferentes_participantes` (lista de Oferente), `documentos_solicitados` (lista de Documento), `cronograma` (dict de hitos con fecha + estado).

---

## 7. Lógica de negocio y todas las fórmulas de cálculo

### 7.1 Cálculos en la licitación (`models.py`)

| Función | Fórmula |
|---------|---------|
| `get_monto_base_total(solo_participados)` | Σ `monto_base` de lotes (si `solo_participados` → sólo lotes con `participamos=True`) |
| `get_oferta_total(solo_participados)` | Σ `monto_ofertado` de lotes (filtro análogo) |
| `get_monto_base_personal_total(solo_participados)` | Σ por lote de: `monto_base_personal` si >0, de lo contrario `monto_base` |
| `get_diferencia_porcentual(solo_participados, usar_base_personal=True)` | base = (`monto_base_personal` o `monto_base`) si `usar_base_personal`, si no `monto_base`. Resultado = `((Σ oferta − Σ base) / Σ base) * 100` (0 si base=0). **Positivo = ofertamos por encima del presupuesto** |
| `get_porcentaje_completado()` | `total_docs=0` → 100 si `docs_completos_manual`, si no 0. Si hay docs: `(docs con presentado=True Y requiere_subsanacion=False / total) * 100` |
| `get_matriz_ofertas()` | Matriz pivote `{lote → {oferente → oferta}}` **sólo** con ofertas que pasaron Fase A y `monto>0`. **No** incluye nuestra propia oferta |
| `calcular_mejor_paquete_individual()` | Por cada lote elige la oferta **más barata** (puede mezclar oferentes; incluye la nuestra si `participamos + fase_A_superada + oferta>0`, prefijada con "➡️"). Devuelve `{monto_total, detalles_por_lote}` |
| `calcular_mejor_paquete_por_oferente()` | Considera **sólo** oferentes que ofertaron en **todos** los lotes (paquete completo). Incluye nuestra oferta si cubre todos los lotes con una única empresa. Devuelve el paquete con `monto_total` **mínimo** (o `None`) |

### 7.2 Estados y vencimientos (`logic/status_engine.py`)

**Paleta de colores de estado (pasteles):**

| Estado | Color |
|--------|-------|
| Iniciada | `#FFFDE7` |
| Sobre B | `#FFF3E0` |
| Fases | `#E0F7FA` |
| Adj. Ganada | `#E8F5E9` |
| Adj. Perdida | `#FFEBEE` |
| Descalificada | `#F8BBD0` |
| Desierta | `#ECEFF1` |
| Cancelada | `#F3E5F5` |
| En curso | `#FAFAFA` |

- `is_finalizada(lic)`: True si `adjudicada`, o estado contiene `"adjudicad/desierta/cancelada/descalificad"`, o `ganada=True`.
- `estatus_y_color(lic)`: mapea estado → (label legible, color). Distingue "Adjudicada (Ganada)" vs "Adjudicada (Perdida)" según flag `ganada`.
- `next_deadline(lic)`: según días restantes del próximo hito:
  - `<0` vencida (rojo `#EF9A9A`, "Vencida hace N días")
  - `=0` "Hoy" (`#EF9A9A`)
  - `=1` amarillo (`#FFE082`)
  - `≤3` amarillo `#FFF176`
  - `>3` verde `#C8E6C9`
- `kpis(licitaciones)` → `(ganadas, perdidas, lotes_ganados)`: `adjudicada+ganada=True` → ganadas (+ lotes con `ganado_por_nosotros`); `adjudicada+ganada=False` → perdidas; `"descalificad"` → perdidas.

### 7.3 KPIs y reportes (`reporting.py` — `ReportingEngine`, struct `ReportKPIs`)

`calculate_kpis(fecha_inicio, fecha_fin, institucion)` con filtros opcionales por `fecha_creacion` e institución. Calcula:

- `total_licitaciones`, `licitaciones_adjudicadas`, `licitaciones_ganadas`
- `tasa_adjudicacion = adjudicadas / total * 100`
- `tasa_exito = ganadas / adjudicadas * 100`
- `valor_total_ofertado = Σ monto_ofertado` de lotes con `participamos`
- `valor_total_ganado = Σ monto_ofertado` de lotes con `ganado_por_nosotros`
- `completitud_documentos_promedio` = media de `(presentados / total * 100)` por licitación
- `causas_perdida` = recuento por `motivo_descalificacion` (perdidas = adjudicadas a otro)
- `vencimientos_proximos` = hitos del cronograma dentro de los próximos 7 días

Otros: `export_to_excel()` (hoja "Licitaciones" + hoja "KPIs"); `generate_monthly_report(year, month)` (rango del mes → kpis del periodo).

### 7.4 Competidores (`competitor_insights.py`)

- **Competitor:** `nombre`, `rnc`, `participaciones`, `proyectos_ganados`, `categorias`, `win_rate`, `promedio_monto`, `mediana_monto`, `ultima_participacion`.
- `add_participation()`: recalcula `win_rate = ganados / participaciones * 100`, promedio y mediana de montos, última participación.
- `get_price_statistics_by_categoria()`: promedio/mediana/min/max/count de montos.
- `get_top_competitors(limit, by)`: ranking por win_rate, participaciones o monto.

### 7.5 Helpers del dashboard (`ui/helpers/dashboard_logic.py`)

Reimplementa cálculos de presentación: `sum_montos_ofertados`, `percent_docs` (`presentados/total*100`), `percent_diff` (`100*(oferta−base)/base`), `next_deadline` con `KNOWN_MILESTONES_ORDER`, `restan_text`, `urgency_color` (`<0 #ffebee`, `≤3 #fff8e1`, `≤10 #f1f8e9`, resto `transparent`), `sort_key_for_lic` (finalizadas al final, por proximidad de hito), `format_money` ("RD$ 1,234.56"), `matches_search / contains_lote / matches_estado / matches_empresa` (filtros).

> ⚠️ **Nota:** hay **lógica de cálculo duplicada** entre `models.py`, `status_engine.py` y `dashboard_logic.py` (riesgo de inconsistencia).

### 7.6 Auditoría (`audit_logger.py`)

- `log_change(entity, entity_id, action, old_values, new_values, summary)` → guarda en colección `audits` con `user_id` y `timestamp`.
- `get_history(filtros)`, `get_changes_diff()` produce líneas `"+ / - / ~ campo: a→b"`.

### 7.7 Tareas (`tasks_manager.py`)

- **Task:** `entity/entity_id`, `responsable`, `titulo`, `descripcion`, `estado` (To-Do/En curso/Hecho), `fecha_limite`, `prioridad` (Alta/Media/Baja), `comentarios`, timestamps.
- `update_task_estado()` marca `completed_at` al pasar a "Hecho".
- `get_overdue_tasks()`: tareas no "Hecho" con `fecha_limite < ahora`.

### 7.8 Utilidades (`utils.py`)

- `normalize_lote_numero()`: extrae el primer número → "LOTE N".
- `reconstruir_ruta_absoluta()`: reconstruye rutas relativas con base Dropbox.
- `previsualizar_archivo()`: abre archivo con app del sistema.

---

## 8. Ventanas, vistas y pestañas (UI) — manual técnico

### 8.1 UI Moderna (actual)

#### `ModernMainWindow` (`windows/modern_main_window.py`)

- **Layout:** `ModernSidebar` (izq.) + `QStackedWidget` (contenido).
- **Navegación sidebar:** "Dashboard General" (0), "Gestión Licitaciones" (1), "Reportes" (2). Atajos `Ctrl+1/2/3`, `Ctrl+N` (nueva), `F5` (refrescar), `Ctrl+Q` (salir).
- **Barra de menú:** Archivo (Configurar Firebase, Backup/Restore, Salir), Dashboards (Dashboard Global Analítico), Reportes (Global, Seleccionada, KPIs), Gestión (Tareas, Historial Auditoría, Plantillas, Importar Datos), Catálogos (Instituciones, Empresas, Documentos, Competidores, Responsables), Ayuda (Acerca de).
- **Status bar** con KPIs globales (Ganadas, Perdidas, Tasa de Éxito %).
- **Datos:** `LicitacionesTableModel` + suscripción en tiempo real (Firestore). `_refresh_all()` actualiza modelo, vistas y KPIs.

#### `DashboardView` (`views/dashboard_view.py`)

- ScrollArea. Título "Dashboard General".
- **4 StatCards:** Activas (📋 info), Ganadas (🏆 success), Perdidas (❌ danger), Total Procesos (📊 accent).
- Gráfico de pastel "Distribución por Estado" + gráfico de líneas "Tendencia" (matplotlib).
- Tabla "Top Instituciones (por cantidad)" + panel "Métricas Financieras" (Monto Base Total, Ofertado Total, Personal Total, Diferencia %, Tasa de Éxito).
- Colores tomados dinámicamente del tema. Solo lectura (analítico).
- *(Existen también `dashboard_widget.py` y `dashboard_widget2.py` como variantes/diálogos.)*

#### `LicitacionesListView` (`views/licitaciones_list_view.py`)

- **Toolbar:** "Nueva Licitación", "Editar Seleccionada", "Actualizar Datos" (recarga desde Firestore ignorando caché).
- **Panel de filtros:** Buscar Proceso, Contiene Lote, Estado (combo), Empresa (combo), botón Limpiar. Debounce 220 ms.
- **Badge "Próximo Vencimiento"** con color por urgencia (verde/amarillo/naranja/rojo).
- **Dos tabs:** "Licitaciones Activas (N)" / "Licitaciones Finalizadas (N)" (mismo modelo, distinto `StatusFilterProxyModel`).
- **Columnas:** Nº Proceso, Nombre, Empresa, (Lotes oculta), %Docs (progress bar), %Diferencia (heatmap), Monto Ofertado, Estado.
- **Footer KPIs:** Activas / Ganadas / Lotes Ganados / Perdidas.
- Persiste anchos de columnas y tab activa (QSettings). Emite `detail_requested(Licitacion)`.

#### `ReportesView` (`views/reportes_view.py`)

"Centro de Reportes". Grid de **6 tarjetas** (`ReportCard`):

1. Reporte Individual (📈) → `ReportWindow`.
2. KPIs y Métricas (🎯) → `DialogoReportes`.
3. Reporte Mensual (📅) → `ReportingEngine`.
4. Exportar a Excel (📗) → `ReportingEngine`.
5. Análisis Financiero (💰).
6. Licitaciones Ganadas (🏆).

> Tarjetas se deshabilitan si su módulo no cargó.

#### `LicitationDetailsWindow` (`windows/licitation_details_window.py`) — ventana clave de edición

- **Panel superior "Datos Iniciales"** en 4 columnas:
  - **A)** Institución (read-only + "Seleccionar…"/"Gestionar…").
  - **B)** Empresas Propias (display + "Seleccionar…").
  - **C)** Kit de Requisitos (combo de kits por institución; aplica documentos).
  - **D)** "Cambios Pendientes" (logger colapsable, deque máx. 200).
- **Regla:** en **creación** el header prevalece (institución + empresas); en **edición** el header se bloquea y se edita desde las pestañas.
- **3 pestañas:**
  - **Tab 0 `TabDetailsGeneral`:** identificación (código/nombre/institución), nuestras empresas, estado (combo de 9 estados), "Adjudicada a" (se habilita si estado=Adjudicada), progreso docs, checks (docs completos / Fase B), motivo, **cronograma** (grid dinámico: hito + `QDateEdit` + estado Pendiente/Cumplido/Incumplido) y bloque de **documentos** (8 botones: Ver checklist, Gestionar Documentos, Ordenar Docs, Generar Expediente PDF, Generar ZIP Categoría, Abrir Carpeta, Validar Faltantes, Ver Historial Subsanación).
  - **Tab 1 `TabLotes`:** tabla de **10 columnas** (Participar, Fase A OK, N°, Nombre, Base Licitación, Base Personal, Nuestra Oferta, %Dif.Licit., %Dif.Pers., Nuestra Empresa). Colores: ahorro verde (`#D1FAE5`/`#065F46`), pérdida rojo (`#FEF2F2`/`#DC2626`), nuestra empresa indigo (`#EEF2FF`/`#4F46E5`). Botones Agregar(`Ctrl+N`)/Editar(`Ctrl+E`)/Eliminar(`Del`). `%Dif = ((Base − Oferta)/Base)*100` (positivo=ahorro).
  - **Tab 2 `TabCompetitors`:** panel izq. de competidores (Agregar Manual / Agregar Catálogo / Importar / Editar / Eliminar / Analizar Paquetes / Editar Parámetros / Ejecutar Evaluación / Análisis de Fallas Fase A); panel der. superior "Ofertas por Lote" del competidor (Lote, Nombre, Monto, Adjudicada) con Agregar/Editar/Eliminar; panel der. inferior "Asignar Ganadores por Lote" (combos dinámicos por lote, ganador verde / nuestra empresa indigo).
- **Botonera:** "Guardar y Cerrar", "Guardar y Continuar", "Eliminar" (si existe id), "Cancelar". Atajos: `Ctrl+S` guardar y continuar, `Ctrl+Shift+D` eliminar.
- **Autosave** con debounce (~7 s) tras cambios.

### 8.2 UI Legacy (anterior, aún presente)

- **`MainWindow` (`windows/main_window.py`):** barra de menú clásica + `QToolBar` (Nueva/Editar) + `DashboardWindow` como widget central. Status bar muestra backend.
- **`DashboardWindow` (`windows/dashboard_window.py`):** tabla de licitaciones con panel "Filtros y Búsqueda" (Buscar Proceso, Contiene Lote, Estado, Empresa, Limpiar), panel "Próximo Vencimiento", dos tabs Activas/Finalizadas, KPIs inferiores y menú contextual (Abrir detalle, Ver Lotes, Copiar número, Abrir carpeta del proceso). `get_selected_licitacion_object()` entrega el objeto seleccionado.
- **Otras ventanas legacy/auxiliares:** `ventana_agregar_licitacion.py` (alta/edición clásica con atajos y persistencia), `ventana_detalles_licitacion.py` (detalle clásico), `ventana_perfil_empresa.py` (perfil de empresa), `reporte_window.py` (`ReportWindow`: reporte individual con gráficos/tablas/KPIs y exportación PDF/Excel).

> **Observación:** `DashboardWindow` (legacy) y `LicitacionesListView` (moderna) cumplen casi la misma función. Igual ocurre con las ventanas de alta/edición de licitación.

---

## 9. Catálogo completo de diálogos (39) y duplicidades

### A) Catálogos maestros

- `dialogo_gestionar_empresas` / `seleccionar_empresas_dialog` (gestión + selección).
- `dialogo_gestionar_instituciones` / `dialogo_seleccionar_institucion` / `seleccionar_institucion_dialog`.
- `dialogo_gestionar_competidores` / `dialogo_seleccionar_competidores`.
- `dialogo_gestionar_responsables`.
- `dialogo_gestionar_documentos_maestros` (plantillas globales de documentos).
- `dialogo_plantillas` (generación de documentos con variables: carta de oferta, etc.).

### B) Licitaciones / lotes / ofertas

- `dialogo_gestionar_lote` / `dialogo_vista_lotes` / `gestionar_lote_dialog` *(**triplicado**)*.
- `dialogo_gestionar_oferta_lote` (oferta de competidor por lote).
- `dialogo_analisis_paquetes` (tabla pivote lotes×competidores + mejores ofertas + export).
- `select_licitacion_dialog` / `seleccionar_licitacion_dialog` *(**duplicado** selector)*.

### C) Documentos / subsanación

- `gestion_documentos_dialog` / `gestionar_documento_dialog` / `visor_documentos_dialog` / `docs_dialog` (gestión, editor individual, visor — **solapados**).
- `dialogo_seleccionar_documentos` (importar del maestro).
- `dialogo_gestion_subsanacion` (marcar docs a subsanar + fecha límite).
- `historial_subsanacion_dialog` / `dialogo_historial` (auditoría/subsanación).
- `ordenar_documentos_dialog` (reordenar en pliego).

### D) Evaluación

- `dialogo_parametros_evaluacion` (método: Precio Más Bajo / Puntos Absolutos / Puntos Ponderados; pesos; puntajes técnicos; descalificados).
- `dialogo_resultados_evaluacion` (resultados por lote; export PDF/Excel).
- `dialogo_fallas_fase_a` (registrar descalificaciones por documento/participante).

### E) Importación

- `dialogo_importar` (asistente: archivo → preview → importar).
- `dialogo_confirmar_importacion` (categorizar documentos antes de importar).

### F) Reportes / respaldos / config

- `dialogo_reportes` (KPIs, filtros fecha/institución, export Excel, reporte mensual).
- `dialogo_respaldos_firestore` (crear/restaurar/eliminar backups; respaldo automático).
- `firebase_config_dialog` (credenciales JSON + bucket + validar conexión).

### G) Editores/utilidad genéricos

- `gestionar_entidad_dialog` (editor genérico Institución/Empresa).
- `gestionar_oferente_dialog` (editor de competidor).
- `dialogo_tareas` (Kanban: estado, responsable, prioridad, fecha límite, comentarios).

### ⚠️ Duplicidades detectadas (deuda de UI)

- **Empresas, Instituciones y Competidores:** cada uno con diálogo "gestionar" + "seleccionar".
- **Lotes:** **tres** diálogos (`dialogo_gestionar_lote`, `dialogo_vista_lotes`, `gestionar_lote_dialog`).
- **Documentos:** hasta **4** diálogos solapados (gestion/gestionar/visor/docs).
- **Selector de licitación:** dos versiones casi idénticas.
- Sin convención de nombres consistente (`DialogoXXX` vs `XXXDialog` vs `SeleccionarXXX`).

---

## 10. Sistema visual: temas, paleta, QSS, widgets, delegates, modelos, iconos

### 10.1 Temas (12 en `app/ui/theme/`)

- **Oscuros:** `titanium_construct_v2` (principal, morado `#7C4DFF`), `dim_theme` (`#3B82F6`), `amethyst_dim_theme`, `charcoal_theme` (`#007ACC`), `graphite_theme` (`#E67E22`), `oceanic_dim_theme`, `slate_theme`.
- **Claros:** `titanium_theme` (`#155E75`), `light_theme`, `fresh_light_theme`, `warm_light_theme`, `professional_light_theme`.
- **Utilidades:** `auto_theme` (punto de extensión, vacío), `theme_utils` (lee hex del tema).
- `theme_manager.py`: `list_themes()` descubre automáticamente módulos con `apply_theme()`, `apply_theme_by_id()`, `apply_theme_from_settings()`. Persiste preferencia en `app_settings` clave `ui_theme` (fallback `dim_theme → light_theme`).
- Compatible PyInstaller (carga desde `sys._MEIPASS`).

### 10.2 Paleta Titanium Construct v2 (tema principal)

| Categoría | Token | Hex |
|-----------|-------|-----|
| Base | BACKGROUND | `#1E1E1E` |
| Base | SURFACE | `#2D2D30` |
| Base | SURFACE_HOVER / BORDER | `#3E3E42` |
| Base | AlternateBase | `#252526` |
| Primario | PRIMARY | `#7C4DFF` |
| Primario | hover | `#651FFF` |
| Primario | pressed | `#5E35B1` |
| Texto | TEXT | `#FFFFFF` |
| Texto | TEXT_MUTED | `#B0B0B0` |
| Semántico | SUCCESS | `#00C853` |
| Semántico | WARNING | `#FFAB00` |
| Semántico | ERROR | `#D50000` |
| Semántico | DANGER | `#FF5252` |
| Semántico | INFO | `#448AFF` |

### 10.3 QSS (lo que estiliza `titanium_construct_v2.py`)

- Contenedores `QFrame`/`QGroupBox` (fondo `#2D2D30`, borde `#3E3E42`, radio 8px, título morado).
- Botones (primario morado; secundario transparente con borde; disabled gris).
- Inputs (`QLineEdit`/`QTextEdit`/`QSpinBox`: fondo `#121212`, foco borde `#7C4DFF`).
- ComboBox (fondo `#121212`, dropdown `#2D2D30`).
- Tablas (fondo `#2D2D30`, alternas `#252526`, selección `rgba(124,77,255,0.3)`; headers `#252526`, mayúsculas, letter-spacing).
- Scrollbars finas (handle `#3E3E42`, 12px, radio 6px).
- Tabs (activo `#2D2D30`/blanco; inactivo gris `#B0B0B0`).
- `QProgressBar` (fondo `#121212`, chunk `#448AFF`).
- MenuBar/Menu/ToolBar/StatusBar/CheckBox/RadioButton/ToolTip (borde morado).

### 10.4 Widgets personalizados (`widgets/modern_widgets.py`)

- **StatCard:** tarjeta KPI (fondo `#2D2D30`, borde inferior 3px de acento, radio 12px, título 12px gris uppercase, valor 32px blanco; `accent_color` configurable).
- **StatusBadge:** badge de estado con variantes success/warning/error/info/default (fondo translúcido del color + texto/borde del color; radio 12px).
- **ModernProgressBar:** barra 6px + porcentaje (`set_value(0..100)`).
- **ModernSidebar:** ancho fijo 200px, header "LICITA MANAGE" morado; items 45px con borde-izq morado 3px al seleccionar; señal `item_selected(id)`.

### 10.5 Delegates de tabla (`delegates/`)

- **HeatmapDelegate:** fondo verde (`#00C853`) si `%>0`, rojo (`#D50000`) si `%<0`, gris si 0; opacidad = `min(|%|/100, 0.7)`. Texto "+12.5% / -8.3% / 0.0%".
- **ProgressBarDelegate:** barra centrada; crece a la derecha si positivo (verde `#00C853`), a la izquierda si negativo (rojo `#FF5252`); línea central dash.
- **SimpleProgressBarDelegate:** barra 0→100% izq→der, color morado `#7C4DFF`.
- **RowColorDelegate:** pinta **toda** la fila con el color del role `ROW_BG_ROLE` (`UserRole+1201`) provisto por el modelo.

### 10.6 Modelos/proxies de tabla (`models/`)

**`LicitacionesTableModel`:** columnas Código (bold), Nombre, Empresa, Restan (días), %Docs, %Dif, Monto Ofertado, Estatus (con ícono), Lotes.
Roles `UserRole+1001..1201` (IS_FINALIZADA, RECORD, ESTADO_TEXT, EMPRESA_TEXT, LOTES_TEXT, PROCESO_NUM, CARPETA_PATH, DOCS_PROGRESS, DIFERENCIA_PCT, ROW_BG).

Coloreado:
- **Restan:** `<0 #DC2626` (vencida), `=0 #2563EB` (hoy), `≤5 #B45309` (pocos días).
- **%Dif:** `<0 #DC2626`, `>0 #16A34A`.
- **Estatus:** ganada/adjudicada/entregado `#16A34A`; perdida/cancelada/descalificada `#DC2626`; en curso `#2563EB`; desierta `#616161`.
- **Iconos de estatus:** ✓ verde, ✕ rojo, – gris (dibujados con QPainter).
- **Formato:** %Docs "85%", %Dif "-12.5%", Monto "RD$ 1,234.56" o "N/D".

**`MultiFilterProxyModel`:** `set_search_text` (col Código), `set_lote_filter` (col Nombre), `set_estado_filter` (col Estatus, exacto), `set_empresa_filter` (col Empresa). **AND lógico**.

**`StatusFilterProxyModel`:** `show_finalizadas` True/False usando `status_engine.is_finalizada`.

### 10.7 Iconos (`components/icon_manager.py`)

- `IconManager.get_icon(name, color, size)`: dibuja iconos vectoriales con QPainter (sin QtSvg). ~30 iconos (plus, edit, trash, save, refresh, search, filter, check, info, file, folder, calendar, clock, star, eye, settings, etc.). Caché por `{name}_{color}_{size}`.
- `set_theme_colors(dict)`: recolorea según el tema activo (accent/text/success/...). Integrado con `titanium_construct_v2.apply_*_with_icons()` y usado por el TableModel para los badges de estatus.

---

## 11. Reportes, exportaciones y generación documental

- **`reporting.py`:** KPIs + Excel (hojas Licitaciones/KPIs) + reporte mensual.
- **`reporting/report_generator.py` (`ReportGenerator`):**
  - `generate_bid_results_report` → Excel/PDF con Resumen (montos, %dif, %docs) y Resultados de Competidores (monto ofertado, monto habilitado Fase A, %dif por lote, ganador).
  - *package report* → tabla pivote lotes×oferentes (resalta mínimo por lote en verde), mejor oferta individual vs mejor paquete por oferente, análisis de nuestros lotes (diferencial vs mejor competidor, rojo si perdemos / verde si ganamos).
  - `generate_evaluation_report` → por lote: posición, califica técnica, puntaje técnico/económico/final, 🏆 al ganador.
  - `generate_subsanacion_report` → historial de subsanaciones.
- **`logic/reporter.py`:** PDF de subsanaciones (fecha, código, documento, fecha límite, estado, comentarios).
- **`logic/pdf_generator.py`:** expediente PDF combinando documentos (portada con datos + QR, índice con páginas, merge de PDFs; marca `[FALTANTE]`/`[OMITIDO - NO PDF]`).
- **`logic/zip_generator.py`:** expediente ZIP por categoría con `index.csv` (orden, código, nombre, categoría, archivo_en_zip); nombres "001 - <doc>"; avisos por faltantes.
- **`template_engine.py`:** genera DOCX (reemplazo `{{{var}}}`) o HTML (Jinja2); carta de oferta con datos de licitación/empresa.

---

## 12. Importación de datos (`importer.py` — `ExcelImporter`)

- Lee Excel (openpyxl) y CSV. `read_excel`/`read_csv` devuelven `(headers, filas)`.
- `map_columns(headers, entity_type)`: detecta columnas por sinónimos. Mapeos para:
  - **LOTES** (numero, nombre, monto_base, monto_ofertado)
  - **DOCUMENTOS** (codigo, nombre, categoria, obligatorio, subsanable)
  - **COMPETIDORES** (nombre, rnc, categoria)
  - **TAREAS** (titulo, descripcion, responsable, fecha_limite, prioridad)
- `validate_row()`: exige campos requeridos no vacíos.
- `_parse_float` (maneja separadores de miles) y `_parse_bool` (true/yes/sí/1/x/✓).
- `import_lotes()` / `import_documentos()`: crean objetos y persisten en la licitación.
- `preview_import()`: vista previa con el mapeo antes de confirmar.

---

## 13. Flujos de uso típicos

- **Arranque** → conexión a BD (Firestore por defecto, con caché de 2h) → carga de licitaciones → suscripción en tiempo real.
- **Crear licitación:** Nueva Licitación → header (institución + empresas + kit) → Tab General (estado/cronograma/docs) → Tab Lotes (montos) → Tab Competidores (ofertas/ganadores) → Guardar (autosave + upsert + invalida caché).
- **Editar:** doble clic / menú contextual → mismo detalle (header bloqueado).
- **Documentos:** gestionar checklist, marcar presentados/subsanación, adjuntar archivos, generar expediente PDF/ZIP, ordenar pliego.
- **Competencia:** registrar oferentes y ofertas por lote, asignar ganadores, analizar paquetes y evaluar (precio más bajo / puntos absolutos / ponderados), fallas Fase A.
- **Reportes:** dashboard, KPIs, reporte mensual, exportar Excel, análisis financiero, reporte individual (PDF/Excel).
- **Mantenimiento:** backups Firestore (gzip), auditoría de cambios, tareas Kanban.

---

## 14. Diagnóstico: fortalezas, problemas y deuda técnica

### ✅ Fortalezas

- Cobertura funcional amplia y específica del dominio de licitaciones.
- Arquitectura por capas con adaptador de BD agnóstico (Firestore/SQLite/MySQL).
- Caché `.pkl` bien pensado para reducir costos/latencia de Firestore.
- Tiempo real, backups comprimidos y modo offline.
- Cálculos de negocio claros y reportería rica (Excel/PDF/ZIP/DOCX).
- Sistema visual moderno con 12 temas, delegates y widgets reutilizables.

### ⚠️ Problemas / deuda técnica

- **DOS UI completas coexistiendo** (moderna + legacy): `ModernMainWindow` vs `MainWindow`, `LicitacionesListView` vs `DashboardWindow`, `LicitationDetailsWindow` vs `ventana_agregar/detalles_licitacion`. Duplicación y riesgo de divergencia.
- **39 diálogos** con muchas duplicidades (lotes ×3, documentos ×4, selectores de institución/empresa/competidor/licitación duplicados). Sin convención de nombres.
- **Lógica de cálculo duplicada** (`models.py` vs `dashboard_logic.py` vs `status_engine.py`): porcentajes de docs, diferencias, vencimientos y "finalizada" reimplementados.
- **Temas:** 12 archivos con mucho QSS repetido; colores hex hardcodeados también en delegates, tabs y modelos (no centralizados en tokens de diseño).
- **Catálogos referenciados por NOMBRE (no por ID):** frágil ante renombrados.
- **Autosave por debounce (~7s)** y multiplicidad de rutas de guardado: riesgo de condiciones de carrera con la sincronización en tiempo real.
- Archivos de depuración y logs en el repo (`debug.txt`, `*.log`, `.pkl` versionado).
- Sin pruebas automatizadas visibles más allá de tests de conexión.

---

## 15. Áreas de mejora priorizadas

1. **Unificar UI:** eliminar la legacy y dejar sólo la moderna (`ModernMainWindow` + vistas).
2. **Consolidar diálogos:** un diálogo por entidad con modos "gestionar/seleccionar"; un único diálogo de lote y uno de documento; un único selector de licitación. Extraer una clase base de "catálogo + selector".
3. **Centralizar lógica de negocio:** una única fuente de verdad para cálculos (servicio de dominio) consumida por modelos de tabla, dashboard y reportes.
4. **Sistema de diseño (design tokens):** paleta y tipografías en un único lugar; generar QSS desde tokens; que delegates/modelos lean colores del tema (no hex fijos). Mejorar accesibilidad (contraste, foco visible, tamaños).
5. **Integridad de datos:** usar IDs estables para catálogos; validaciones más fuertes; transacciones/optimistic locking para evitar choques autosave ↔ tiempo real.
6. **Reportes interactivos:** gráficas con drill-down, filtros guardados, exportes ricos.
7. **UX orientada a tareas:** asistentes guiados (alta de licitación, subsanación, evaluación) en lugar de saltar entre muchos diálogos. Alertas de riesgo/vencimiento.
8. **Limpieza de repo:** quitar logs/debug/`.pkl` del control de versiones; añadir tests.
9. **Rendimiento:** lazy-load de vistas pesadas y de matplotlib; paginación de tablas.

---

## 16. Prompt base sugerido para mejorar la aplicación

> Actúa como arquitecto de software senior y diseñador UI/UX para **LICIPRO**, una app de escritorio en Python/PyQt6 para gestión de licitaciones públicas con backend Firestore (y soporte SQLite/MySQL), caché local `.pkl`, sincronización en tiempo real y reportería en Excel/PDF/ZIP/DOCX. La base de código tiene **dos interfaces coexistiendo** (una moderna con sidebar+stack y temas Titanium Construct v2, y una legacy con menú + `DashboardWindow`), **39 diálogos** con muchas duplicidades (lote ×3, documentos ×4, selectores duplicados de institución/empresa/competidor/licitación), **lógica de cálculo duplicada** entre `models.py`, `dashboard_logic.py` y `status_engine.py`, y **12 temas** con QSS y colores hex repetidos.
>
> Propón e implementa por **fases** una mejora integral que: **(1)** unifique la UI eliminando la legacy y dejando una única experiencia moderna; **(2)** consolide los diálogos en componentes reutilizables (catálogo+selector, un diálogo de lote, uno de documento, un selector de licitación) con convención de nombres consistente; **(3)** centralice la lógica de negocio en un servicio de dominio único (cálculos de montos, % de documentos, diferencias, KPIs, estados y vencimientos) consumido por tablas, dashboard y reportes; **(4)** introduzca un sistema de diseño con design tokens (paleta, tipografía, espaciados) del que se genere el QSS y que delegates/modelos lean colores del tema, mejorando contraste y accesibilidad; **(5)** refuerce la integridad de datos (IDs estables para catálogos, validaciones, control de concurrencia entre autosave y tiempo real); **(6)** mejore reportes y dashboard con visualizaciones interactivas y alertas de riesgo; **(7)** reoriente la UX a tareas con asistentes guiados (alta de licitación, subsanación, evaluación de ofertas).
>
> **Entrega:** diagnóstico, arquitectura objetivo, plan de migración por fases con riesgos y criterios de aceptación, y los cambios de código priorizados, conservando la compatibilidad con los backends y los datos existentes en Firestore.

---

*Fin del documento.*
