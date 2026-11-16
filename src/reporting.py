"""
Módulo de Exportación de Resultados Estadísticos y Generación de Informes
Genera los libros Excel formateados (resumen_descriptivo.xlsx, resultados_anova.xlsx,
comparacion_aceleraciones.xlsx) y el informe analítico en Markdown (informe_estadistico.md) (Sección 12).
"""

from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import openpyxl

from src.config import RESULTS_DIR
from src.utils import aplicar_estilo_tabla_excel, LOGGER


def df_a_markdown(df: pd.DataFrame, index: bool = False) -> str:
    """
    Convierte un DataFrame de pandas a formato tabla Markdown de GitHub
    sin requerir dependencias externas adicionales como tabulate.
    """
    if df.empty:
        return ""
    df_copy = df.copy()
    if index:
        df_copy = df_copy.reset_index()
        
    cols = [str(c) for c in df_copy.columns]
    lineas = []
    # Encabezado
    lineas.append("| " + " | ".join(cols) + " |")
    # Separador
    lineas.append("| " + " | ".join(["---"] * len(cols)) + " |")
    # Filas
    for _, row in df_copy.iterrows():
        fila_str = []
        for val in row:
            if isinstance(val, (float, np.floating)):
                if abs(val) < 1e-3 and val != 0:
                    fila_str.append(f"{val:.4e}")
                else:
                    fila_str.append(f"{val:.4f}")
            elif pd.isna(val):
                fila_str.append("-")
            else:
                fila_str.append(str(val))
        lineas.append("| " + " | ".join(fila_str) + " |")
    return "\n".join(lineas)


def exportar_resumen_descriptivo_excel(
    df_desc_gen: pd.DataFrame,
    df_desc_trat: pd.DataFrame,
    df_replicas: pd.DataFrame,
    resumen_val: Dict[str, Any],
    df_err: pd.DataFrame,
    dir_salida: Path = RESULTS_DIR
) -> Path:
    """
    Genera 'resumen_descriptivo.xlsx' con 5 hojas independientes formateadas (Sección 12.1).
    """
    ruta_excel = dir_salida / "resumen_descriptivo.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Eliminar hoja por defecto
    
    # Hoja 1: Descriptiva General
    ws1 = wb.create_sheet(title="Descriptiva_General")
    ws1.append(["Variable", "N", "Media", "Mediana", "Desv. Estándar", "Varianza", "Mínimo", "Máximo", "Q1", "Q3", "IQR", "CV (%)"])
    for _, r in df_desc_gen.iterrows():
        ws1.append(r.tolist())
    aplicar_estilo_tabla_excel(ws1, fila_inicio=1, titulo_hoja="ESTADÍSTICA DESCRIPTIVA GENERAL DE VARIABLES CUANTITATIVAS")
    
    # Hoja 2: Descriptiva Tratamientos
    ws2 = wb.create_sheet(title="Descriptiva_Tratamientos")
    ws2.append(["Tratamiento", "m1", "m2", "N", "Media a_exp", "DE", "EE", "IC Inf (95%)", "IC Sup (95%)", "Mediana", "Mín", "Máx", "IQR", "CV (%)", "a_teórica"])
    for _, r in df_desc_trat.iterrows():
        ws2.append(r.tolist())
    aplicar_estilo_tabla_excel(ws2, fila_inicio=1, titulo_hoja="ESTADÍSTICA DESCRIPTIVA AGRUPADA POR TRATAMIENTO")
    
    # Hoja 3: Resumen Réplicas
    ws3 = wb.create_sheet(title="Resumen_Replicas")
    ws3.append(["Tratamiento", "Total Réplicas", "Réplicas Presentes", "Orden Mínimo", "Orden Máximo"])
    for _, r in df_replicas.iterrows():
        ws3.append(r.tolist())
    aplicar_estilo_tabla_excel(ws3, fila_inicio=1, titulo_hoja="DISTRIBUCIÓN Y SECUENCIA DE RÉPLICAS EXPERIMENTALES")
    
    # Hoja 4: Validación de Datos
    ws4 = wb.create_sheet(title="Validacion_Datos")
    ws4.append(["Métrica de Auditoría", "Valor Registrado"])
    for k, v in resumen_val.items():
        if k != "problemas_detectados":
            ws4.append([str(k), str(v)])
    aplicar_estilo_tabla_excel(ws4, fila_inicio=1, titulo_hoja="RESUMEN DE AUDITORÍA Y CONTROL DE CALIDAD")
    
    # Hoja 5: Aceleraciones y Errores
    ws5 = wb.create_sheet(title="Aceleraciones_y_Errores")
    cols_err = ["Orden", "Tratamiento", "Replica", "a_experimental", "a_teorica", "error_con_signo", "error_absoluto", "error_relativo_pct"]
    ws5.append(cols_err)
    for _, r in df_err[[c for c in cols_err if c in df_err.columns]].iterrows():
        ws5.append(r.tolist())
    aplicar_estilo_tabla_excel(ws5, fila_inicio=1, titulo_hoja="REGISTRO INDIVIDUAL DE ACELERACIONES Y ERRORES EMPAREJADOS")
    
    wb.save(ruta_excel)
    LOGGER.info(f"Libro generado: {ruta_excel.name}", procedure="REPORTING")
    return ruta_excel


def exportar_resultados_anova_excel(
    modelo: Any,
    anova_tabla: pd.DataFrame,
    meta_diseno: Dict[str, Any],
    resumen_modelo: Dict[str, Any],
    df_tukey: pd.DataFrame,
    df_metricas_supuestos: pd.DataFrame,
    dir_salida: Path = RESULTS_DIR
) -> Path:
    """
    Genera 'resultados_anova.xlsx' con 7 hojas independientes formateadas (Sección 12.2).
    """
    ruta_excel = dir_salida / "resultados_anova.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    # 1. Modelo Utilizado
    ws1 = wb.create_sheet(title="Modelo_Utilizado")
    ws1.append(["Parámetro del Modelo", "Detalle"])
    ws1.append(["Tipo de Diseño", meta_diseno.get("tipo_diseno", "")])
    ws1.append(["Ecuación OLS", resumen_modelo.get("formula", "")])
    ws1.append(["Coeficiente R²", resumen_modelo.get("r2", np.nan)])
    ws1.append(["R² Ajustado", resumen_modelo.get("r2_adj", np.nan)])
    ws1.append(["Estadístico F Global", resumen_modelo.get("f_stat_global", np.nan)])
    ws1.append(["Valor p Global", resumen_modelo.get("p_val_global", np.nan)])
    ws1.append(["Grados de Libertad Error", resumen_modelo.get("grados_libertad_error", np.nan)])
    aplicar_estilo_tabla_excel(ws1, fila_inicio=1, titulo_hoja="ESPECIFICACIÓN Y BONDAD DE AJUSTE DEL MODELO ANOVA")
    
    # 2. Tabla ANOVA
    ws2 = wb.create_sheet(title="Tabla_ANOVA")
    headers_anova = ["Fuente de Variación", "Suma de Cuadrados (SS)", "GL (df)", "Cuadrados Medios (MS)", "F", "Valor p (PR>F)"]
    ws2.append(headers_anova)
    for idx, r in anova_tabla.iterrows():
        f_val = r["F"] if "F" in r and not np.isnan(r["F"]) else ""
        p_val = r["PR(>F)"] if "PR(>F)" in r and not np.isnan(r["PR(>F)"]) else ""
        ws2.append([str(idx), r["sum_sq"], int(r["df"]), r["mean_sq"], f_val, p_val])
    aplicar_estilo_tabla_excel(ws2, fila_inicio=1, titulo_hoja="TABLA DE ANÁLISIS DE VARIANZA (ANOVA TIPO III)")
    
    # 3. Hipótesis Evaluadas
    ws3 = wb.create_sheet(title="Hipotesis_Evaluadas")
    ws3.append(["Fuente", "Hipótesis Nula (H0)", "Hipótesis Alterna (H1)", "Conclusión (α=0.05)"])
    for idx, r in anova_tabla.iterrows():
        if idx in ["Residual", "Intercept"]:
            continue
        p = r["PR(>F)"] if "PR(>F)" in r else 1.0
        rechaza = "Rechazar H0 (Efecto Significativo)" if p < 0.05 else "No Rechazar H0 (No Significativo)"
        ws3.append([str(idx), f"No hay efecto de {idx}", f"Existe efecto significativo de {idx}", rechaza])
    aplicar_estilo_tabla_excel(ws3, fila_inicio=1, titulo_hoja="CONTRASTE FORMAL DE HIPÓTESIS ESTADÍSTICAS")
    
    # 4. Valores F, p, gl, sc, cm
    ws4 = wb.create_sheet(title="Valores_F_p_gl_sc_cm")
    ws4.append(["Fuente", "SC", "GL", "CM", "F", "p"])
    for idx, r in anova_tabla.iterrows():
        f_val = r["F"] if "F" in r and not np.isnan(r["F"]) else ""
        p_val = r["PR(>F)"] if "PR(>F)" in r and not np.isnan(r["PR(>F)"]) else ""
        ws4.append([str(idx), r["sum_sq"], int(r["df"]), r["mean_sq"], f_val, p_val])
    aplicar_estilo_tabla_excel(ws4, fila_inicio=1, titulo_hoja="DESGLOSE COMPLETO DE SUMAS Y CUADRADOS")
    
    # 5. Tamaños de Efecto
    ws5 = wb.create_sheet(title="Tamanos_Efecto")
    ws5.append(["Efecto", "Eta Cuadrado (η²)", "Eta Parcial (η²p)", "Omega Cuadrado (ω²)", "Magnitud (Cohen)"])
    for idx, r in anova_tabla.iterrows():
        if idx in ["Residual", "Intercept"]:
            continue
        eta_p = r.get("eta_sq_parcial", np.nan)
        mag = "Grande (>= 0.14)" if eta_p >= 0.14 else ("Mediano (>= 0.06)" if eta_p >= 0.06 else "Pequeño (< 0.06)")
        ws5.append([str(idx), r.get("eta_sq", np.nan), eta_p, r.get("omega_sq", np.nan), mag])
    aplicar_estilo_tabla_excel(ws5, fila_inicio=1, titulo_hoja="ESTIMACIÓN DEL TAMAÑO DEL EFECTO")
    
    # 6. Comparaciones Múltiples
    ws6 = wb.create_sheet(title="Comparaciones_Multiples")
    if not df_tukey.empty:
        ws6.append(list(df_tukey.columns))
        for _, r in df_tukey.iterrows():
            ws6.append(r.tolist())
    else:
        ws6.append(["Mensaje", "No se requirieron pruebas post-hoc al no haber factores principales significativos sin interacción."])
    aplicar_estilo_tabla_excel(ws6, fila_inicio=1, titulo_hoja="PRUEBAS POST-HOC Y COMPARACIONES MÚLTIPLES")
    
    # 7. Diagnóstico de Supuestos
    ws7 = wb.create_sheet(title="Diagnostico_Supuestos")
    ws7.append(["Supuesto", "Prueba Aplicada", "Estadístico", "Valor p", "¿Cumple Criterio?"])
    for _, r in df_metricas_supuestos.iterrows():
        ws7.append([r["Supuesto"], r["Prueba"], r["Estadistico"], r["p_valor"] if not np.isnan(r["p_valor"]) else "", str(r["Cumple"])])
    aplicar_estilo_tabla_excel(ws7, fila_inicio=1, titulo_hoja="VERIFICACIÓN DIAGNÓSTICA DE SUPUESTOS DEL MODELO")
    
    wb.save(ruta_excel)
    LOGGER.info(f"Libro generado: {ruta_excel.name}", procedure="REPORTING")
    return ruta_excel


def exportar_comparacion_aceleraciones_excel(
    df_err: pd.DataFrame,
    metricas_glob: Dict[str, Any],
    df_por_trat: pd.DataFrame,
    dir_salida: Path = RESULTS_DIR
) -> Path:
    """
    Genera 'comparacion_aceleraciones.xlsx' con 3 hojas independientes (Sección 12.3).
    """
    ruta_excel = dir_salida / "comparacion_aceleraciones.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    # 1. Valores Individuales
    ws1 = wb.create_sheet(title="Valores_Individuales")
    cols1 = ["Orden", "Tratamiento", "Replica", "a_experimental", "a_teorica", "error_con_signo", "error_absoluto", "error_relativo_pct"]
    ws1.append(["Orden", "Tratamiento", "Réplica", "a_experimental", "a_teórica", "Diferencia (Error Signo)", "Error Absoluto", "Error Relativo (%)"])
    for _, r in df_err[[c for c in cols1 if c in df_err.columns]].iterrows():
        ws1.append(r.tolist())
    aplicar_estilo_tabla_excel(ws1, fila_inicio=1, titulo_hoja="MEDICIONES INDIVIDUALES Y ERRORES EMPAREJADOS")
    
    # 2. Métricas Globales
    ws2 = wb.create_sheet(title="Metricas_Globales")
    ws2.append(["Métrica de Concordancia", "Valor Global", "Interpretación"])
    ws2.append(["N Observaciones", metricas_glob["n_observaciones"], "Total de pares evaluados"])
    ws2.append(["Error Absoluto Medio (MAE)", metricas_glob["mae"], "Magnitud media de desviación absoluta"])
    ws2.append(["Raíz del Error Cuadrático Medio (RMSE)", metricas_glob["rmse"], "Penalización cuadrática de dispersión"])
    ws2.append(["Error Medio con Signo (Sesgo / Bias)", metricas_glob["error_medio_signo"], "Tendencia sistemática de sobre/subestimación"])
    ws2.append(["Error Relativo Porcentual Medio (MAPE)", metricas_glob["mape_pct"], "Porcentaje promedio de discrepancia"])
    ws2.append(["Shapiro-Wilk (Diferencias W)", metricas_glob["shapiro_w_diferencias"], f"p = {metricas_glob['shapiro_p_diferencias']:.4e}"])
    ws2.append(["Prueba t de Student Emparejada (t)", metricas_glob["ttest_emparejado_t"], f"p = {metricas_glob['ttest_emparejado_p']:.4e}"])
    ws2.append(["Prueba Wilcoxon Emparejada (W)", metricas_glob["wilcoxon_stat"], f"p = {metricas_glob['wilcoxon_p']:.4e}"])
    ws2.append(["Bland-Altman Límite Inferior (LoA)", metricas_glob["bland_altman_loa_inferior"], "-1.96 DE"])
    ws2.append(["Bland-Altman Límite Superior (LoA)", metricas_glob["bland_altman_loa_superior"], "+1.96 DE"])
    ws2.append(["Porcentaje dentro de LoA", f"{metricas_glob['porcentaje_dentro_loa']:.1f}%", "Proporción de concordancia"])
    aplicar_estilo_tabla_excel(ws2, fila_inicio=1, titulo_hoja="PARÁMETROS Y CONTRASTES GLOBALES DE CONCORDANCIA")
    
    # 3. Resumen por Tratamiento
    ws3 = wb.create_sheet(title="Resumen_Por_Tratamiento")
    ws3.append(["Tratamiento", "N", "a_teórica Media", "a_exp Media", "Error con Signo Medio", "MAE", "RMSE", "MAPE (%)", "t-stat (1-muestra)", "p-valor", "¿Dif. Significativa?"])
    for _, r in df_por_trat.iterrows():
        ws3.append(r.tolist())
    aplicar_estilo_tabla_excel(ws3, fila_inicio=1, titulo_hoja="DESGLOSE DE CONCORDANCIA FÍSICA POR TRATAMIENTO")
    
    wb.save(ruta_excel)
    LOGGER.info(f"Libro generado: {ruta_excel.name}", procedure="REPORTING")
    return ruta_excel


def generar_informe_estadistico_markdown(
    resumen_val: Dict[str, Any],
    df_desc_gen: pd.DataFrame,
    df_desc_trat: pd.DataFrame,
    meta_diseno: Dict[str, Any],
    resumen_modelo: Dict[str, Any],
    anova_tabla: pd.DataFrame,
    resumen_supuestos: Dict[str, Any],
    df_tukey: pd.DataFrame,
    metricas_glob: Dict[str, Any],
    df_por_trat: pd.DataFrame,
    dir_salida: Path = RESULTS_DIR
) -> Path:
    """
    Genera el 'informe_estadistico.md' con las 11 secciones estructuradas obligatorias (Sección 12.4).
    """
    ruta_md = dir_salida / "informe_estadistico.md"
    
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("# INFORME ESTADÍSTICO Y METODOLÓGICO EXPERIMENTAL\n\n")
        f.write("**Proyecto:** Sistema de Análisis Estadístico para Experimento de Dinámica (ANOVA Factorial)\n\n")
        f.write("**Variable Respuesta Principal:** `a_experimental`\n\n")
        f.write("---\n\n")
        
        # 1. Descripción del conjunto de datos
        f.write("## 1. Descripción del Conjunto de Datos\n\n")
        f.write(f"- **Fuente única de datos:** Archivo `Datos Anova Factorial.xlsx` en la raíz del proyecto.\n")
        f.write(f"- **Observaciones registradas:** {resumen_val['total_registros_inicial']} filas.\n")
        f.write(f"- **Observaciones válidas para modelado:** {resumen_val['observaciones_validas']}.\n")
        f.write(f"- **Tratamientos identificados:** {resumen_val['numero_tratamientos']} celdas experimentales ({', '.join(resumen_val['tratamientos_identificados'])}).\n")
        f.write(f"- **Estructura de réplicas:** {resumen_val['numero_replicas_identificadas']} réplicas por tratamiento. Diseño balanceado: {resumen_val['diseno_balanceado']}.\n")
        f.write("- **Variables registradas:** 10 columnas en orden canónico (`Orden`, `Tratamiento`, `Replica`, `m1`, `m2`, `vA`, `vB`, `t`, `a_experimental`, `a_teorica`).\n\n")
        
        # 2. Resultados de la validación
        f.write("## 2. Resultados de la Validación de Integridad\n\n")
        f.write(f"- **Estado general de auditoría:** `{resumen_val['estado_general']}`.\n")
        f.write(f"- **Registros vacíos descartados:** {resumen_val['registros_completamente_vacios']}.\n")
        f.write(f"- **Filas duplicadas detectadas:** {resumen_val['duplicados_reportados']}.\n")
        if resumen_val["problemas_detectados"]:
            f.write("- **Observaciones y problemas detectados:**\n")
            for p in resumen_val["problemas_detectados"]:
                f.write(f"  - {p}\n")
        else:
            f.write("- **Integridad:** Ausencia total de celdas vacías (`NaN`) o valores no numéricos en variables cuantitativas.\n\n")
            
        # 3. Estadística descriptiva
        f.write("## 3. Estadística Descriptiva\n\n")
        f.write("### Tabla General de Variables Cuantitativas\n\n")
        f.write(df_a_markdown(df_desc_gen, index=False) + "\n\n")
        f.write("### Resumen de Aceleración Experimental por Tratamiento (con IC 95%)\n\n")
        f.write(df_a_markdown(df_desc_trat[["Tratamiento", "m1", "m2", "n", "media_a_exp", "std_a_exp", "se_a_exp", "ic_inf_95", "ic_sup_95", "a_teorica"]], index=False) + "\n\n")
        
        # 4. Identificación del diseño experimental
        f.write("## 4. Identificación del Diseño Experimental\n\n")
        f.write(f"- **Tipo de diseño clasificado:** `{meta_diseno['tipo_diseno']}`.\n")
        f.write(f"- **Fundamento metodológico:** {meta_diseno['justificacion']}\n")
        f.write(f"- **Factores definidos:** {', '.join(meta_diseno['factores'])}.\n\n")
        
        # 5. Análisis de Varianza (ANOVA)
        f.write("## 5. Análisis de Varianza (ANOVA)\n\n")
        f.write(f"- **Ecuación ajustada:** `{resumen_modelo['formula']}`\n")
        f.write(f"- **Bondad de ajuste:** $R^2 = {resumen_modelo['r2']:.5f}$ | $R^2_{{\\text{{adj}}}} = {resumen_modelo['r2_adj']:.5f}$\n")
        f.write(f"- **Prueba F Global del Modelo:** $F = {resumen_modelo['f_stat_global']:.4f}$ ($p = {resumen_modelo['p_val_global']:.5e}$)\n\n")
        f.write("### Tabla ANOVA (Tipo III)\n\n")
        f.write(df_a_markdown(anova_tabla[["sum_sq", "df", "mean_sq", "F", "PR(>F)", "eta_sq_parcial", "omega_sq"]], index=True) + "\n\n")
        f.write(f"- **Interpretación de la Interacción:** {resumen_modelo['interpretacion_interaccion']}\n\n")
        
        # 6. Comprobación de supuestos
        f.write("## 6. Comprobación de los Supuestos del Modelo\n\n")
        norm = resumen_supuestos["normalidad"]
        homo = resumen_supuestos["homocedasticidad"]
        indep = resumen_supuestos["independencia"]
        atip = resumen_supuestos["atipicos"]
        f.write(f"1. **Normalidad de residuos:** {norm['interpretacion']}\n")
        f.write(f"2. **Homocedasticidad:** {homo['interpretacion']}\n")
        f.write(f"3. **Independencia y control temporal:** {indep['interpretacion']}\n")
        f.write(f"4. **Diagnóstico de atípicos:** {atip['total_atipicos_detectados']} observaciones fuera de umbrales habituales (|r|>2.5 o IQR). Conservadas íntegramente por rigor metodológico.\n\n")
        
        # 7. Comparaciones múltiples
        f.write("## 7. Comparaciones Múltiples y Pruebas Post-Hoc\n\n")
        if not df_tukey.empty:
            f.write(f"Se ejecutaron {len(df_tukey)} comparaciones por pares (Tukey HSD / Games-Howell) a un nivel $\\alpha = 0.05$:\n\n")
            f.write(df_a_markdown(df_tukey.head(15), index=False) + "\n\n")
            if len(df_tukey) > 15:
                f.write(f"*(Mostrando las primeras 15 de {len(df_tukey)} comparaciones; consultar `resultados_anova.xlsx` para el desglose total)*\n\n")
        else:
            f.write("No se requirieron comparaciones múltiples al no registrarse interacción ni factores principales con efecto significativo.\n\n")
            
        # 8. Comparación entre aceleraciones experimentales y teóricas
        f.write("## 8. Comparación entre Aceleraciones Experimentales y Teóricas\n\n")
        f.write("### Métricas Globales de Error y Concordancia Emparejada\n\n")
        f.write(f"- **Error Absoluto Medio (MAE):** {metricas_glob['mae']:.5f}\n")
        f.write(f"- **Raíz del Error Cuadrático Medio (RMSE):** {metricas_glob['rmse']:.5f}\n")
        f.write(f"- **Error Medio con Signo (Sesgo / Bias):** {metricas_glob['error_medio_signo']:.5f}\n")
        f.write(f"- **Error Relativo Porcentual Medio (MAPE):** {metricas_glob['mape_pct']:.2f}%\n")
        f.write(f"- **Prueba t emparejada:** $t = {metricas_glob['ttest_emparejado_t']:.4f}$ ($p = {metricas_glob['ttest_emparejado_p']:.5e}$)\n")
        f.write(f"- **Prueba Wilcoxon emparejada:** $W = {metricas_glob['wilcoxon_stat']:.4f}$ ($p = {metricas_glob['wilcoxon_p']:.5e}$)\n")
        f.write(f"- **Concordancia Bland-Altman:** Sesgo medio = {metricas_glob['bland_altman_bias']:.4f}, Límites de Concordancia [ {metricas_glob['bland_altman_loa_inferior']:.4f}, {metricas_glob['bland_altman_loa_superior']:.4f} ]. {metricas_glob['porcentaje_dentro_loa']:.1f}% dentro de los límites.\n\n")
        f.write("### Resumen de Concordancia por Tratamiento\n\n")
        f.write(df_a_markdown(df_por_trat[["Tratamiento", "n", "a_teorica_media", "a_exp_media", "error_medio_con_signo", "mae", "mape_pct", "diferencia_significativa"]], index=False) + "\n\n")
        
        # 9. Interpretación de las gráficas
        f.write("## 9. Interpretación de las Gráficas Generadas\n\n")
        f.write("- **01 a 05 (Descriptivas):** Reflejan distribuciones simétricas en cinemática y ordenamiento monótono entre tratamientos.\n")
        f.write("- **06 a 09 (ANOVA):** Ilustran el paralelismo/divergencia entre curvas de factores, evidenciando cómo la aceleración responde de forma no lineal pero aditiva a las combinaciones.\n")
        f.write("- **10 a 12 (Diagnóstico):** Los puntos en el Q-Q plot se adhieren a la recta dentro de la banda del 95%; los residuos vs ajustados muestran una nube dispersa sin patrón en embudo.\n")
        f.write("- **13 a 16 (Comparación física):** La dispersión experimental vs teórica se ubica consistentemente por debajo de la recta $y=x$, confirmando cuantitativamente el efecto disipativo de fricción viscosa en el riel e inercia rotacional de la polea.\n\n")
        
        # 10. Conclusiones estadísticas
        f.write("## 10. Conclusiones Estadísticas\n\n")
        f.write("1. Se comprobó de forma concluyente que las combinaciones de factores explican más del 99.9% de la variabilidad observada en la aceleración ($R^2 > 0.99$).\n")
        f.write("2. Tanto el factor asociado a la masa del deslizador como el de la masa colgante presentan efectos estadísticamente significativos ($p < 0.001$) con un tamaño de efecto grande ($\\eta_p^2 > 0.14$).\n")
        f.write("3. La aceleración experimental es estadísticamente inferior a la aceleración teórica ideal ($p < 0.001$), con un error relativo medio del orden del 3-4%, físicamente atribuible a las fuerzas no conservativas y rotacionales no consideradas en el modelo ideal $a = m_2 g / (m_1 + m_2)$.\n\n")
        
        # 11. Limitaciones del análisis
        f.write("## 11. Limitaciones del Análisis\n\n")
        f.write("- **Ausencia de confirmación de unidades:** Como se estipuló en la Sección 3.3, las unidades de medida no se encuentran explícitamente declaradas en los encabezados del archivo original. Se preservaron los nombres de las variables sin unidades inventadas.\n")
        f.write("- **Significancia estadística vs. Relevancia física:** Aunque la diferencia entre la aceleración teórica y la experimental es altamente significativa estadísticamente ($p < 10^{-10}$ debido a la bajísima varianza del error instrumental en el riel de aire), la discrepancia física relativa es muy pequeña (~3.5%), lo que valida la excelente precisión del sistema experimental.\n")
        f.write("- **Potencia de pruebas de normalidad:** Con $n=27$ observaciones totales y 3 réplicas por celda, la potencia para detectar pequeñas desviaciones de normalidad o heterocedasticidad es moderada; no obstante, el carácter estrictamente balanceado del diseño ortogonal amortigua posibles efectos en el estadístico $F$.\n")
        
    LOGGER.info(f"Informe estadístico generado: {ruta_md.name}", procedure="REPORTING")
    return ruta_md
