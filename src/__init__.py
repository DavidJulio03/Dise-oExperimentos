"""
Paquete Principal del Sistema de Análisis ANOVA
Módulos para carga, validación, estadística descriptiva, ANOVA factorial,
diagnóstico de supuestos, comparaciones teóricas y visualización.
"""

__version__ = "2.0.0"
__author__ = "Desarrollador Científico Especializado en Estadística y Física Experimental"

from src.data_loader import cargar_datos, normalizar_encabezados
from src.data_validation import validar_integridad_dataset
from src.descriptive_statistics import ejecutar_analisis_descriptivo
from src.factorial_anova import identificar_diseno_experimental, ajustar_modelo_anova
from src.post_hoc import ejecutar_pruebas_post_hoc
from src.assumption_tests import ejecutar_diagnostico_completo_supuestos
from src.theoretical_comparison import ejecutar_comparacion_teorica_completa
from src.visualizations import generar_todas_las_graficas
from src.reporting import (
    exportar_resumen_descriptivo_excel,
    exportar_resultados_anova_excel,
    exportar_comparacion_aceleraciones_excel,
    generar_informe_estadistico_markdown
)

__all__ = [
    "cargar_datos",
    "normalizar_encabezados",
    "validar_integridad_dataset",
    "ejecutar_analisis_descriptivo",
    "identificar_diseno_experimental",
    "ajustar_modelo_anova",
    "ejecutar_pruebas_post_hoc",
    "ejecutar_diagnostico_completo_supuestos",
    "ejecutar_comparacion_teorica_completa",
    "generar_todas_las_graficas",
    "exportar_resumen_descriptivo_excel",
    "exportar_resultados_anova_excel",
    "exportar_comparacion_aceleraciones_excel",
    "generar_informe_estadistico_markdown"
]
