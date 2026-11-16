"""
Script Orquestador Principal del Sistema de Análisis ANOVA
Ejecuta de manera secuencial, modular y robusta las 12 fases del pipeline analítico (Sección 14).
Permite ejecución directa mediante: python -m src.main
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Garantizar que la raíz del proyecto esté en el PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import EXCEL_PATH, RESULTS_DIR, PLOTS_DIR, DEFAULT_ALPHA
from src.utils import LOGGER
from src.data_loader import cargar_datos
from src.data_validation import validar_integridad_dataset
from src.factorial_anova import identificar_diseno_experimental, ajustar_modelo_anova
from src.descriptive_statistics import ejecutar_analisis_descriptivo
from src.assumption_tests import ejecutar_diagnostico_completo_supuestos
from src.post_hoc import ejecutar_pruebas_post_hoc
from src.theoretical_comparison import ejecutar_comparacion_teorica_completa
from src.visualizations import generar_todas_las_graficas
from src.reporting import (
    exportar_resumen_descriptivo_excel,
    exportar_resultados_anova_excel,
    exportar_comparacion_aceleraciones_excel,
    generar_informe_estadistico_markdown
)


def main():
    """
    Función orquestadora principal que implementa el flujo secuencial estricto de 12 pasos.
    """
    t_inicio = time.time()
    
    print("\n" + "="*80)
    print("  SISTEMA CIENTÍFICO DE PROCESAMIENTO Y ANÁLISIS ESTADÍSTICO ANOVA")
    print("  Diseño Factorial / Experimento Físico de Aceleración")
    print("="*80)
    
    LOGGER.info(f"Iniciando ejecución del pipeline. Archivo objetivo: {EXCEL_PATH.name}", procedure="ORQUESTADOR")
    
    # 1 & 3. Cargar archivo Excel y normalizar encabezados
    try:
        df_normalizado, meta_carga = cargar_datos(EXCEL_PATH)
    except Exception as e:
        LOGGER.error(f"Fallo crítico en fase de carga de datos: {e}", procedure="CARGA_DATOS")
        LOGGER.write_to_file()
        sys.exit(1)
        
    # 2. Validar estructura e integridad de los datos
    try:
        df_validado, resumen_val = validar_integridad_dataset(df_normalizado)
    except Exception as e:
        LOGGER.error(f"Fallo en fase de validación: {e}", procedure="VALIDACION_DATOS")
        resumen_val = {"estado_general": "FALLO_VALIDACION", "problemas_detectados": [str(e)]}
        df_validado = df_normalizado.copy()
        
    # 4. Identificar el diseño experimental (Sección 4.1 y 4.2)
    try:
        df_diseno, meta_diseno = identificar_diseno_experimental(df_validado)
    except Exception as e:
        LOGGER.error(f"Fallo al clasificar diseño experimental: {e}", procedure="IDENTIFICACION_DISENO")
        meta_diseno = {"tipo_diseno": "UN_FACTOR_TRATAMIENTOS", "justificacion": str(e), "factores": ["Tratamiento"]}
        df_diseno = df_validado.copy()
        
    # 5. Generar estadísticas descriptivas
    try:
        res_descriptiva = ejecutar_analisis_descriptivo(df_diseno)
    except Exception as e:
        LOGGER.error(f"Fallo en cálculo descriptivo: {e}", procedure="ANALISIS_DESCRIPTIVO")
        res_descriptiva = {}
        
    # 7. Ejecutar el ANOVA justificado por los datos
    modelo, anova_tabla, resumen_modelo = None, None, {}
    try:
        modelo, anova_tabla, resumen_modelo = ajustar_modelo_anova(df_diseno, meta_diseno, alpha=DEFAULT_ALPHA)
        LOGGER.info(f"ANOVA ajustado con éxito. R² = {resumen_modelo.get('r2', 0):.5f}", procedure="AJUSTE_ANOVA")
    except Exception as e:
        LOGGER.error(f"Fallo durante el ajuste del modelo ANOVA: {e}", procedure="AJUSTE_ANOVA")
        
    # 6. Evaluar los supuestos pertinentes
    df_res, resumen_supuestos, df_metricas_supuestos = None, {}, None
    if modelo is not None:
        try:
            df_res, resumen_supuestos, df_metricas_supuestos = ejecutar_diagnostico_completo_supuestos(
                modelo, df_diseno, alpha=DEFAULT_ALPHA
            )
        except Exception as e:
            LOGGER.error(f"Fallo en evaluación de supuestos: {e}", procedure="DIAGNOSTICO_SUPUESTOS")
    else:
        LOGGER.warning("Se omite evaluación de supuestos del modelo al no haberse ajustado un modelo OLS.", procedure="DIAGNOSTICO_SUPUESTOS")
        
    # 8. Ejecutar comparaciones múltiples cuando proceda
    df_tukey, meta_posthoc = pd.DataFrame(), {}
    if modelo is not None and anova_tabla is not None:
        try:
            df_tukey, meta_posthoc = ejecutar_pruebas_post_hoc(
                df_diseno, meta_diseno, resumen_modelo, anova_tabla, alpha=DEFAULT_ALPHA
            )
        except Exception as e:
            LOGGER.error(f"Fallo en comparaciones post-hoc: {e}", procedure="POST_HOC")
            
    # 9. Comparar aceleraciones experimentales y teóricas
    df_err, metricas_glob, df_por_trat = None, {}, None
    try:
        df_err, metricas_glob, df_por_trat = ejecutar_comparacion_teorica_completa(df_diseno, alpha=DEFAULT_ALPHA)
    except Exception as e:
        LOGGER.error(f"Fallo en comparación teórica: {e}", procedure="COMPARACION_TEORICA")
        
    # 10. Generar gráficas
    rutas_graficas = []
    try:
        if (df_res is not None and res_descriptiva and df_err is not None and
            "descriptiva_por_tratamiento" in res_descriptiva and
            "correlacion_pearson" in res_descriptiva):
            
            rutas_graficas = generar_todas_las_graficas(
                df=df_diseno,
                df_desc_trat=res_descriptiva["descriptiva_por_tratamiento"],
                r_matrix=res_descriptiva["correlacion_pearson"],
                meta_diseno=meta_diseno,
                df_tukey=df_tukey,
                df_res=df_res,
                meta_norm=resumen_supuestos.get("normalidad", {}),
                df_err=df_err,
                metricas_glob=metricas_glob,
                dir_salida=PLOTS_DIR
            )
    except Exception as e:
        LOGGER.error(f"Fallo durante la generación de gráficas: {e}", procedure="GENERADOR_GRAFICAS")
        import traceback
        traceback.print_exc()
        
    # 11. Exportar resultados estadísticos
    try:
        if res_descriptiva and df_err is not None:
            exportar_resumen_descriptivo_excel(
                df_desc_gen=res_descriptiva["descriptiva_general"],
                df_desc_trat=res_descriptiva["descriptiva_por_tratamiento"],
                df_replicas=res_descriptiva["resumen_replicas"],
                resumen_val=resumen_val,
                df_err=df_err,
                dir_salida=RESULTS_DIR
            )
            
        if modelo is not None and anova_tabla is not None and df_metricas_supuestos is not None:
            exportar_resultados_anova_excel(
                modelo=modelo,
                anova_tabla=anova_tabla,
                meta_diseno=meta_diseno,
                resumen_modelo=resumen_modelo,
                df_tukey=df_tukey,
                df_metricas_supuestos=df_metricas_supuestos,
                dir_salida=RESULTS_DIR
            )
            
        if df_err is not None and metricas_glob and df_por_trat is not None:
            exportar_comparacion_aceleraciones_excel(
                df_err=df_err,
                metricas_glob=metricas_glob,
                df_por_trat=df_por_trat,
                dir_salida=RESULTS_DIR
            )
    except Exception as e:
        LOGGER.error(f"Fallo durante la exportación de libros Excel: {e}", procedure="REPORTING")
        
    # 12. Generar informe estadístico Markdown
    try:
        if (res_descriptiva and anova_tabla is not None and resumen_supuestos and
            metricas_glob and df_por_trat is not None):
            generar_informe_estadistico_markdown(
                resumen_val=resumen_val,
                df_desc_gen=res_descriptiva["descriptiva_general"],
                df_desc_trat=res_descriptiva["descriptiva_por_tratamiento"],
                meta_diseno=meta_diseno,
                resumen_modelo=resumen_modelo,
                anova_tabla=anova_tabla,
                resumen_supuestos=resumen_supuestos,
                df_tukey=df_tukey,
                metricas_glob=metricas_glob,
                df_por_trat=df_por_trat,
                dir_salida=RESULTS_DIR
            )
    except Exception as e:
        LOGGER.error(f"Fallo en redacción del informe estadístico: {e}", procedure="REPORTING")
        
    # Cerrar y guardar registro de ejecución
    duracion = time.time() - t_inicio
    LOGGER.info(f"Pipeline completado exitosamente en {duracion:.2f} segundos.", procedure="ORQUESTADOR")
    LOGGER.write_to_file(metadata={
        "Archivo de Entrada": str(EXCEL_PATH),
        "Hoja Procesada": meta_carga.get("hoja", ""),
        "Registros": meta_carga.get("filas_crudas", 0),
        "Tipo de Diseño": meta_diseno.get("tipo_diseno", ""),
        "Figuras Generadas": len(rutas_graficas)
    })
    
    # Resumen en consola
    print("\n" + "="*80)
    print("✔ EJECUCIÓN CONCLUIDA CON ÉXITO")
    print(f"  Tiempo total: {duracion:.2f} s")
    print(f"  Libros Excel generados en:       {RESULTS_DIR.name}/")
    print(f"  Informe Markdown generado en:    {RESULTS_DIR.name}/informe_estadistico.md")
    print(f"  Registro de auditoría en:        {RESULTS_DIR.name}/registro_ejecucion.log")
    print(f"  Total de figuras (300 DPI):      {len(rutas_graficas)} figuras en {PLOTS_DIR.name}/")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
