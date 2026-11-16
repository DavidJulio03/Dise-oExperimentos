"""
Módulo de Configuración Centralizada del Sistema de Análisis ANOVA
Define rutas, variables canónicas, parámetros estadísticos y mapeos de factores.
"""

from pathlib import Path
from typing import Dict, Any, Optional

# 1. Rutas del Proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCEL_FILENAME = "Datos Anova Factorial.xlsx"
EXCEL_PATH = PROJECT_ROOT / EXCEL_FILENAME

RESULTS_DIR = PROJECT_ROOT / "resultados_estadisticos"
PLOTS_DIR = PROJECT_ROOT / "graficas"
LOG_FILE = RESULTS_DIR / "registro_ejecucion.log"

# Asegurar que los directorios existan
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# 2. Configuración de Entrada de Datos
SHEET_NAME: Optional[str] = None  # None activa la selección automática de hoja válida

CANONICAL_COLUMNS = [
    "Orden",
    "Tratamiento",
    "Replica",
    "m1",
    "m2",
    "vA",
    "vB",
    "t",
    "a_experimental",
    "a_teorica"
]

# Clasificación rigurosa de variables según su naturaleza experimental
CATEGORICAL_VARIABLES = ["Orden", "Tratamiento", "Replica"]
QUANTITATIVE_VARIABLES = ["m1", "m2", "vA", "vB", "t", "a_experimental", "a_teorica"]

RESPONSE_VARIABLE = "a_experimental"
THEORETICAL_VARIABLE = "a_teorica"
ORDER_VARIABLE = "Orden"
TREATMENT_VARIABLE = "Tratamiento"
REPLICATE_VARIABLE = "Replica"

# 3. Unidades de Medida
# Conforme a la Sección 3.3 de las especificaciones, NO se deben inventar ni inferir
# unidades no confirmadas explícitamente en el archivo original.
# Este diccionario se mantiene vacío por defecto.
CONFIRMED_UNITS: Dict[str, str] = {}

# 4. Parámetros Estadísticos
DEFAULT_ALPHA = 0.05
CONFIDENCE_LEVEL = 0.95
ANOVA_TYPE = 3  # Sumas de cuadrados Tipo III para diseños factoriales con interacción

# 5. Mapeo Explícito de Factores (Sección 4.1)
# Estructura configurable para definir la correspondencia entre Tratamiento y factores.
# Si se deja vacío, el sistema activará el detector de patrones ortogonales automáticos.
FACTOR_MAP: Dict[str, Dict[str, str]] = {
    # Ejemplo de estructura configurable:
    # "A1B1": {"Factor_A": "A1", "Factor_B": "B1"},
    # "A1B2": {"Factor_A": "A1", "Factor_B": "B2"},
}

# 6. Configuración de Gráficas Científicas
PLOT_DPI = 300
PLOT_FORMAT = "png"
PLOT_PALETTE = "deep"
