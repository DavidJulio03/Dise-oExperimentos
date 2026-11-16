"""
Módulo de Verificación Diagnóstica de los Supuestos del ANOVA
Evalúa normalidad de residuos, homocedasticidad, independencia y diagnóstico
de valores atípicos conforme a la Sección 9 de las especificaciones.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.stattools import durbin_watson

from src.config import TREATMENT_VARIABLE, ORDER_VARIABLE, DEFAULT_ALPHA
from src.utils import LOGGER


def extraer_residuos_y_ajustes(modelo, df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula y vincula valores ajustados, residuos ordinarios, residuos estandarizados
    y residuos estudentizados al DataFrame de análisis.
    """
    df_res = df.copy()
    df_res["valores_ajustados"] = modelo.fittedvalues
    df_res["residuos_ordinarios"] = modelo.resid
    
    # Residuos estandarizados internamente
    influencia = modelo.get_influence()
    df_res["residuos_estudentizados"] = influencia.resid_studentized_internal
    df_res["residuos_estandarizados"] = modelo.resid / (np.std(modelo.resid, ddof=1) or 1e-12)
    
    return df_res


def evaluar_normalidad_residuos(residuos: np.ndarray, alpha: float = DEFAULT_ALPHA) -> Dict[str, Any]:
    """
    Evalúa la normalidad de los residuos del modelo (Sección 9.1):
    - Shapiro-Wilk (prueba principal).
    - Jarque-Bera y D'Agostino-Pearson (respaldo).
    - Asimetría (skewness) y curtosis de Fisher.
    - Interpretación contextualizada considerando el tamaño muestral (n=27) y su potencia.
    """
    res_clean = residuos[~np.isnan(residuos)]
    n = len(res_clean)
    
    w_stat, p_shapiro = stats.shapiro(res_clean)
    jb_stat, p_jb = stats.jarque_bera(res_clean)
    
    try:
        dag_stat, p_dag = stats.normaltest(res_clean)
    except Exception:
        dag_stat, p_dag = np.nan, np.nan
        
    asimetria = float(stats.skew(res_clean, bias=False))
    curtosis = float(stats.kurtosis(res_clean, bias=False))
    
    cumple = bool(p_shapiro >= alpha)
    
    interpretacion = (
        f"Prueba Shapiro-Wilk: W = {w_stat:.4f}, p = {p_shapiro:.4f}. "
        + (f"No se rechaza la normalidad (p >= {alpha}). Los residuos se distribuyen normalmente."
           if cumple else
           f"Se detecta desviación de la normalidad (p < {alpha}). Al ser n={n}, considere la robustez del ANOVA en diseños balanceados o transformaciones.")
    )
    
    return {
        "shapiro_w": float(w_stat),
        "shapiro_p": float(p_shapiro),
        "jarque_bera_stat": float(jb_stat),
        "jarque_bera_p": float(p_jb),
        "dagostino_stat": float(dag_stat),
        "dagostino_p": float(p_dag),
        "asimetria": asimetria,
        "curtosis_exceso": curtosis,
        "cumple_normalidad": cumple,
        "interpretacion": interpretacion
    }


def evaluar_homocedasticidad(df_res: pd.DataFrame, grupo_col: str = TREATMENT_VARIABLE, alpha: float = DEFAULT_ALPHA) -> Dict[str, Any]:
    """
    Evalúa la homogeneidad de varianzas (Sección 9.2):
    - Prueba de Levene (Brown-Forsythe centrada en la mediana).
    - Prueba de Bartlett.
    - Razón entre la varianza máxima y la varianza mínima.
    """
    grupos_residuos = [g["residuos_ordinarios"].dropna().values for _, g in df_res.groupby(grupo_col)]
    # Filtrar grupos con al menos 2 datos
    grupos_validos = [g for g in grupos_residuos if len(g) > 1]
    
    if len(grupos_validos) < 2:
        return {
            "levene_stat": np.nan, "levene_p": np.nan,
            "bartlett_stat": np.nan, "bartlett_p": np.nan,
            "razon_var_max_min": np.nan, "cumple_homocedasticidad": True,
            "interpretacion": "Número insuficiente de grupos para contrastar varianzas."
        }
        
    lev_stat, p_levene = stats.levene(*grupos_validos, center="median")
    bart_stat, p_bartlett = stats.bartlett(*grupos_validos)
    
    varianzas = [float(np.var(g, ddof=1)) for g in grupos_validos]
    var_min = min(varianzas) if min(varianzas) > 1e-12 else 1e-12
    var_max = max(varianzas)
    razon_var = float(var_max / var_min)
    
    cumple = bool(p_levene >= alpha)
    interpretacion = (
        f"Prueba de Levene (Brown-Forsythe): Estadístico = {lev_stat:.4f}, p = {p_levene:.4f}. "
        + (f"No se detecta heterocedasticidad significativa (p >= {alpha}). Las varianzas son homogéneas."
           if cumple else
           f"Evidencia de heterocedasticidad (p < {alpha}). En diseños balanceados la prueba F mantiene solidez, aunque se recomienda verificar modelos ponderados o errores robustos HC3.")
    )
    
    return {
        "levene_stat": float(lev_stat),
        "levene_p": float(p_levene),
        "bartlett_stat": float(bart_stat),
        "bartlett_p": float(p_bartlett),
        "razon_var_max_min": razon_var,
        "cumple_homocedasticidad": cumple,
        "interpretacion": interpretacion
    }


def evaluar_independencia_y_control_temporal(df_res: pd.DataFrame, alpha: float = DEFAULT_ALPHA) -> Dict[str, Any]:
    """
    Evalúa indicios de dependencia temporal y deriva instrumental (Sección 9.3).
    Aclara explícitamente que la independencia se fundamenta en la aleatorización del diseño,
    no únicamente en una prueba matemática.
    """
    if ORDER_VARIABLE not in df_res.columns:
        return {
            "durbin_watson": np.nan, "corr_orden_pearson_r": np.nan,
            "corr_orden_pearson_p": np.nan, "cumple_independencia": True,
            "interpretacion": "Columna 'Orden' no disponible para evaluar secuencia temporal."
        }
        
    df_ordenado = df_res.sort_values(by=ORDER_VARIABLE).dropna(subset=["residuos_ordinarios", ORDER_VARIABLE])
    res_ord = df_ordenado["residuos_ordinarios"].values
    ord_num = df_ordenado[ORDER_VARIABLE].astype(float).values
    
    dw_val = float(durbin_watson(res_ord))
    r_val, p_val = stats.pearsonr(ord_num, res_ord)
    
    sin_autocorr = (1.5 <= dw_val <= 2.5)
    sin_deriva = (p_val >= alpha)
    cumple = sin_autocorr and sin_deriva
    
    interpretacion = (
        f"Estadístico Durbin-Watson: d = {dw_val:.4f} (ideal ~ 2.0). Correlación vs. Orden: r = {r_val:.4f} (p = {p_val:.4f}). "
        + ("No se observa evidencia de deriva temporal en los residuos; el orden aleatorizado garantizó la independencia."
           if cumple else
           "Advertencia de posible autocorrelación o deriva temporal durante la secuencia de medición.")
    )
    
    return {
        "durbin_watson": dw_val,
        "corr_orden_pearson_r": float(r_val),
        "corr_orden_pearson_p": float(p_val),
        "cumple_independencia": cumple,
        "interpretacion": interpretacion
    }


def diagnosticar_valores_atipicos(df_res: pd.DataFrame) -> Dict[str, Any]:
    """
    Identifica observaciones atípicas mediante el rango intercuartílico (IQR)
    y residuos estandarizados/estudentizados (|r| > 2.5 o 3.0) (Sección 9.4).
    Regla estricta: Los valores atípicos se reportan, NUNCA se eliminan automáticamente.
    """
    residuos = df_res["residuos_ordinarios"].dropna().values
    q1 = float(np.percentile(residuos, 25))
    q3 = float(np.percentile(residuos, 75))
    iqr = q3 - q1
    umbral_inf = q1 - 1.5 * iqr
    umbral_sup = q3 + 1.5 * iqr
    
    filtro_iqr = (df_res["residuos_ordinarios"] < umbral_inf) | (df_res["residuos_ordinarios"] > umbral_sup)
    filtro_std = df_res["residuos_estudentizados"].abs() > 2.5
    
    atipicos_iqr = df_res[filtro_iqr]
    atipicos_std = df_res[filtro_std]
    
    indices_atipicos = sorted(list(set(atipicos_iqr.index.tolist() + atipicos_std.index.tolist())))
    
    LOGGER.info(
        f"Diagnóstico de atípicos: {len(indices_atipicos)} observaciones señaladas (|r_std| > 2.5 o IQR). "
        "Se conservan íntegramente en el análisis principal.",
        procedure="DIAGNOSTICO_SUPUESTOS"
    )
    
    return {
        "total_atipicos_detectados": len(indices_atipicos),
        "indices_observaciones_atipicas": indices_atipicos,
        "umbral_iqr_inferior": umbral_inf,
        "umbral_iqr_superior": umbral_sup,
        "resumen_atipicos": df_res.loc[indices_atipicos, [ORDER_VARIABLE, TREATMENT_VARIABLE, "residuos_ordinarios", "residuos_estudentizados"]].to_dict(orient="records") if indices_atipicos else []
    }


def ejecutar_diagnostico_completo_supuestos(modelo, df: pd.DataFrame, alpha: float = DEFAULT_ALPHA) -> Tuple[pd.DataFrame, Dict[str, Any], pd.DataFrame]:
    """
    Orquestador de verificación diagnóstica de los supuestos del ANOVA.
    Retorna (df_residuos, resumen_supuestos, tabla_metricas_csv).
    """
    LOGGER.info("Iniciando evaluación completa de supuestos del modelo ANOVA...", procedure="DIAGNOSTICO_SUPUESTOS")
    
    df_res = extraer_residuos_y_ajustes(modelo, df)
    res_norm = evaluar_normalidad_residuos(df_res["residuos_ordinarios"].values, alpha=alpha)
    res_homo = evaluar_homocedasticidad(df_res, grupo_col=TREATMENT_VARIABLE, alpha=alpha)
    res_indep = evaluar_independencia_y_control_temporal(df_res, alpha=alpha)
    res_atip = diagnosticar_valores_atipicos(df_res)
    
    # Tabla consolidada para exportación tabular
    metricas = [
        {"Supuesto": "Normalidad", "Prueba": "Shapiro-Wilk", "Estadistico": res_norm["shapiro_w"], "p_valor": res_norm["shapiro_p"], "Cumple": res_norm["cumple_normalidad"]},
        {"Supuesto": "Normalidad", "Prueba": "Jarque-Bera", "Estadistico": res_norm["jarque_bera_stat"], "p_valor": res_norm["jarque_bera_p"], "Cumple": res_norm["jarque_bera_p"] >= alpha},
        {"Supuesto": "Homocedasticidad", "Prueba": "Levene (Brown-Forsythe)", "Estadistico": res_homo["levene_stat"], "p_valor": res_homo["levene_p"], "Cumple": res_homo["cumple_homocedasticidad"]},
        {"Supuesto": "Homocedasticidad", "Prueba": "Bartlett", "Estadistico": res_homo["bartlett_stat"], "p_valor": res_homo["bartlett_p"], "Cumple": res_homo["bartlett_p"] >= alpha},
        {"Supuesto": "Homocedasticidad", "Prueba": "Razón Varianza Máx/Mín", "Estadistico": res_homo["razon_var_max_min"], "p_valor": np.nan, "Cumple": res_homo["razon_var_max_min"] <= 4.0},
        {"Supuesto": "Independencia", "Prueba": "Durbin-Watson", "Estadistico": res_indep["durbin_watson"], "p_valor": np.nan, "Cumple": (1.5 <= res_indep["durbin_watson"] <= 2.5)},
        {"Supuesto": "Independencia", "Prueba": "Correlación vs Orden", "Estadistico": res_indep["corr_orden_pearson_r"], "p_valor": res_indep["corr_orden_pearson_p"], "Cumple": res_indep["corr_orden_pearson_p"] >= alpha},
        {"Supuesto": "Atípicos", "Prueba": "Residuos Estudentizados > 2.5", "Estadistico": res_atip["total_atipicos_detectados"], "p_valor": np.nan, "Cumple": res_atip["total_atipicos_detectados"] == 0}
    ]
    df_metricas = pd.DataFrame(metricas)
    
    resumen_supuestos = {
        "normalidad": res_norm,
        "homocedasticidad": res_homo,
        "independencia": res_indep,
        "atipicos": res_atip,
        "estado_global": "CUMPLE_SUPUESTOS" if (res_norm["cumple_normalidad"] and res_homo["cumple_homocedasticidad"] and res_indep["cumple_independencia"]) else "DESVIACION_MODERADA"
    }
    
    return df_res, resumen_supuestos, df_metricas
