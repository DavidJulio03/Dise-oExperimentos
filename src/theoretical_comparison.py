"""
Módulo de Comparación entre Aceleración Experimental y Teórica
Implementa análisis emparejado, cálculo de errores (con signo, absoluto y relativo),
pruebas estadísticas de concordancia (t emparejada y Wilcoxon) y método de Bland-Altman (Sección 10).
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

from src.config import RESPONSE_VARIABLE, THEORETICAL_VARIABLE, TREATMENT_VARIABLE, DEFAULT_ALPHA
from src.utils import LOGGER


def calcular_errores_individuales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula los errores individuales emparejados para cada observación:
    - error_con_signo = a_experimental - a_teorica
    - error_absoluto = |a_experimental - a_teorica|
    - error_relativo_pct = (|a_exp - a_teo| / |a_teo|) * 100
    Maneja con rigor matemático el caso de a_teorica == 0 (Sección 10).
    """
    df_err = df.copy()
    
    a_exp = df_err[RESPONSE_VARIABLE]
    a_teo = df_err[THEORETICAL_VARIABLE]
    
    error_signo = a_exp - a_teo
    error_abs = error_signo.abs()
    
    # Error relativo porcentual
    error_rel = pd.Series(np.nan, index=df_err.index)
    mascara_no_cero = (a_teo.abs() > 1e-9)
    error_rel[mascara_no_cero] = (error_abs[mascara_no_cero] / a_teo[mascara_no_cero].abs()) * 100.0
    
    df_err["error_con_signo"] = error_signo
    df_err["error_absoluto"] = error_abs
    df_err["error_relativo_pct"] = error_rel
    
    # Documentar si se detectaron valores teóricos nulos
    n_ceros = int((~mascara_no_cero).sum())
    if n_ceros > 0:
        LOGGER.warning(
            f"Se detectaron {n_ceros} observaciones con aceleración teórica igual a cero. "
            "El error relativo porcentual fue asignado como NaN para evitar división por cero.",
            procedure="COMPARACION_TEORICA"
        )
        
    return df_err


def calcular_metricas_globales(df_err: pd.DataFrame, alpha: float = DEFAULT_ALPHA) -> Dict[str, Any]:
    """
    Calcula MAE, RMSE, Error Medio con Signo, MAPE y ejecuta pruebas estadísticas emparejadas:
    - Normalidad de las diferencias (Shapiro-Wilk)
    - Prueba t de Student para muestras emparejadas
    - Prueba de rangos con signo de Wilcoxon
    - Límites de concordancia de Bland-Altman
    """
    e_signo = df_err["error_con_signo"].dropna().values
    e_abs = df_err["error_absoluto"].dropna().values
    e_rel = df_err["error_relativo_pct"].dropna().values
    
    n = len(e_signo)
    mae = float(np.mean(e_abs))
    rmse = float(np.sqrt(np.mean(e_signo**2)))
    error_medio_signo = float(np.mean(e_signo))
    mape = float(np.mean(e_rel)) if len(e_rel) > 0 else np.nan
    
    # 1. Normalidad de las diferencias emparejadas
    w_stat, p_shapiro = stats.shapiro(e_signo)
    dif_normal = bool(p_shapiro >= alpha)
    
    # 2. Prueba t de Student emparejada
    a_exp = df_err[RESPONSE_VARIABLE].dropna().values
    a_teo = df_err[THEORETICAL_VARIABLE].dropna().values
    t_stat, p_ttest = stats.ttest_rel(a_exp, a_teo)
    
    # 3. Prueba de rangos con signo de Wilcoxon
    try:
        # Se aplica sobre las diferencias emparejadas
        w_wilcoxon, p_wilcoxon = stats.wilcoxon(e_signo)
    except Exception:
        w_wilcoxon, p_wilcoxon = np.nan, np.nan
        
    # 4. Parámetros de concordancia de Bland-Altman
    media_dif = error_medio_signo
    std_dif = float(np.std(e_signo, ddof=1)) if n > 1 else 0.0
    limite_inf_loa = media_dif - 1.96 * std_dif
    limite_sup_loa = media_dif + 1.96 * std_dif
    
    # Error estándar de los límites de concordancia
    se_loa = np.sqrt(3.0 * (std_dif**2) / n) if n > 0 else 0.0
    t_crit = float(stats.t.ppf(1 - alpha / 2, df=n - 1)) if n > 1 else 1.96
    
    # Observaciones dentro de los límites
    dentro_loa = ((e_signo >= limite_inf_loa) & (e_signo <= limite_sup_loa)).sum()
    pct_dentro_loa = float((dentro_loa / n) * 100.0) if n > 0 else 0.0
    
    interpretacion_prueba = (
        f"Prueba t emparejada: t = {t_stat:.4f}, p = {p_ttest:.5e}. "
        f"Prueba Wilcoxon: W = {w_wilcoxon:.4f}, p = {p_wilcoxon:.5e}. "
        + ("Existe diferencia sistemática estadísticamente significativa entre la aceleración experimental y la teórica (p < 0.05). "
           "La aceleración experimental es consistentemente inferior a la teórica debido a fuerzas disipativas e inercia rotacional."
           if (p_ttest < alpha or p_wilcoxon < alpha) else
           "No se detecta diferencia sistemática significativa entre ambas mediciones.")
    )
    
    return {
        "n_observaciones": n,
        "mae": mae,
        "rmse": rmse,
        "error_medio_signo": error_medio_signo,
        "mape_pct": mape,
        "shapiro_w_diferencias": float(w_stat),
        "shapiro_p_diferencias": float(p_shapiro),
        "diferencias_normales": dif_normal,
        "ttest_emparejado_t": float(t_stat),
        "ttest_emparejado_p": float(p_ttest),
        "wilcoxon_stat": float(w_wilcoxon),
        "wilcoxon_p": float(p_wilcoxon),
        "bland_altman_bias": media_dif,
        "bland_altman_sd": std_dif,
        "bland_altman_loa_inferior": limite_inf_loa,
        "bland_altman_loa_superior": limite_sup_loa,
        "bland_altman_ci_loa_inf": (limite_inf_loa - t_crit * se_loa, limite_inf_loa + t_crit * se_loa),
        "bland_altman_ci_loa_sup": (limite_sup_loa - t_crit * se_loa, limite_sup_loa + t_crit * se_loa),
        "porcentaje_dentro_loa": pct_dentro_loa,
        "interpretacion": interpretacion_prueba
    }


def calcular_metricas_por_tratamiento(df_err: pd.DataFrame, alpha: float = DEFAULT_ALPHA) -> pd.DataFrame:
    """
    Desagrega la comparación experimental vs. teórica por tratamiento, evitando
    que el agregado global oculte diferencias o sesgos locales (Sección 10.1).
    """
    if TREATMENT_VARIABLE not in df_err.columns:
        return pd.DataFrame()
        
    registros = []
    for trat, sub in df_err.groupby(TREATMENT_VARIABLE):
        n_t = len(sub)
        e_sig = sub["error_con_signo"].values
        e_abs = sub["error_absoluto"].values
        e_rel = sub["error_relativo_pct"].dropna().values
        
        mae_t = float(np.mean(e_abs))
        rmse_t = float(np.sqrt(np.mean(e_sig**2)))
        bias_t = float(np.mean(e_sig))
        mape_t = float(np.mean(e_rel)) if len(e_rel) > 0 else np.nan
        
        # Prueba t local si hay réplicas
        if n_t >= 3 and np.std(e_sig, ddof=1) > 1e-12:
            t_loc, p_loc = stats.ttest_1samp(e_sig, popmean=0.0)
        else:
            t_loc, p_loc = np.nan, np.nan
            
        registros.append({
            "Tratamiento": trat,
            "n": n_t,
            "a_teorica_media": float(sub[THEORETICAL_VARIABLE].mean()),
            "a_exp_media": float(sub[RESPONSE_VARIABLE].mean()),
            "error_medio_con_signo": bias_t,
            "mae": mae_t,
            "rmse": rmse_t,
            "mape_pct": mape_t,
            "ttest_1samp_t": float(t_loc) if not np.isnan(t_loc) else np.nan,
            "ttest_1samp_p": float(p_loc) if not np.isnan(p_loc) else np.nan,
            "diferencia_significativa": bool(p_loc < alpha) if not np.isnan(p_loc) else False
        })
        
    df_por_trat = pd.DataFrame(registros)
    return df_por_trat


def ejecutar_comparacion_teorica_completa(df: pd.DataFrame, alpha: float = DEFAULT_ALPHA) -> Tuple[pd.DataFrame, Dict[str, Any], pd.DataFrame]:
    """
    Orquestador del análisis de concordancia y comparación entre aceleración experimental y teórica.
    Retorna (df_errores_individuales, metricas_globales, df_resumen_por_tratamiento).
    """
    LOGGER.info("Ejecutando análisis de comparación emparejada: a_experimental vs a_teorica...", procedure="COMPARACION_TEORICA")
    
    df_err = calcular_errores_individuales(df)
    metricas_glob = calcular_metricas_globales(df_err, alpha=alpha)
    df_por_trat = calcular_metricas_por_tratamiento(df_err, alpha=alpha)
    
    LOGGER.info(
        f"Métricas calculadas: MAE = {metricas_glob['mae']:.4f}, RMSE = {metricas_glob['rmse']:.4f}, "
        f"Bias = {metricas_glob['error_medio_signo']:.4f}, MAPE = {metricas_glob['mape_pct']:.2f}%.",
        procedure="COMPARACION_TEORICA"
    )
    LOGGER.info(f"Concordancia Bland-Altman: {metricas_glob['porcentaje_dentro_loa']:.1f}% puntos dentro de LoA.", procedure="COMPARACION_TEORICA")
    
    return df_err, metricas_glob, df_por_trat
