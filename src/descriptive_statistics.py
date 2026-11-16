"""
Módulo de Análisis Estadístico Descriptivo y Exploratorio
Calcula métricas de tendencia central, dispersión, posición, intervalos de confianza
y correlaciones conforme a las Secciones 7.1 y 7.2.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from scipy import stats

from src.config import (
    QUANTITATIVE_VARIABLES,
    RESPONSE_VARIABLE,
    TREATMENT_VARIABLE,
    REPLICATE_VARIABLE,
    CONFIDENCE_LEVEL
)
from src.utils import calcular_intervalo_confianza, LOGGER


def calcular_estadisticas_univariadas(serie: pd.Series) -> Dict[str, Any]:
    """
    Calcula el conjunto completo de métricas descriptivas para una variable cuantitativa:
    n, media, mediana, desviación estándar, varianza, mín, máx, Q1, Q3, IQR y CV.
    """
    datos = serie.dropna().values
    n = len(datos)
    if n == 0:
        return {k: np.nan for k in [
            "n", "media", "mediana", "std", "varianza", "min", "max", "q1", "q3", "iqr", "cv_pct"
        ]}
        
    media = float(np.mean(datos))
    mediana = float(np.median(datos))
    std = float(np.std(datos, ddof=1)) if n > 1 else 0.0
    var = float(np.var(datos, ddof=1)) if n > 1 else 0.0
    min_val = float(np.min(datos))
    max_val = float(np.max(datos))
    q1 = float(np.percentile(datos, 25))
    q3 = float(np.percentile(datos, 75))
    iqr = q3 - q1
    
    # Coeficiente de variación (solo si la media no es cero ni extremadamente cercana a cero)
    if abs(media) > 1e-6:
        cv_pct = float((std / abs(media)) * 100.0)
    else:
        cv_pct = np.nan
        
    return {
        "n": n,
        "media": media,
        "mediana": mediana,
        "std": std,
        "varianza": var,
        "min": min_val,
        "max": max_val,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "cv_pct": cv_pct
    }


def generar_descriptiva_general(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la tabla de estadística descriptiva general para todas las variables cuantitativas.
    """
    registros = []
    for var in QUANTITATIVE_VARIABLES:
        if var in df.columns:
            stats_dict = calcular_estadisticas_univariadas(df[var])
            stats_dict["variable"] = var
            registros.append(stats_dict)
            
    df_desc = pd.DataFrame(registros)
    columnas_orden = ["variable", "n", "media", "mediana", "std", "varianza", "min", "max", "q1", "q3", "iqr", "cv_pct"]
    return df_desc[[c for c in columnas_orden if c in df_desc.columns]]


def generar_descriptiva_por_tratamiento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera estadísticas descriptivas agrupadas por Tratamiento, incorporando
    intervalos de confianza al 95% para la aceleración experimental media.
    """
    if TREATMENT_VARIABLE not in df.columns or RESPONSE_VARIABLE not in df.columns:
        return pd.DataFrame()
        
    registros = []
    alpha_ic = 1.0 - CONFIDENCE_LEVEL
    
    # Ordenar tratamientos si es posible
    tratamientos = df[TREATMENT_VARIABLE].unique()
    try:
        tratamientos = sorted(tratamientos)
    except Exception:
        pass
        
    for trat in tratamientos:
        sub = df[df[TREATMENT_VARIABLE] == trat]
        # Métricas de aceleración experimental
        stats_a_exp = calcular_estadisticas_univariadas(sub[RESPONSE_VARIABLE])
        
        # Intervalo de confianza de la media
        media, ic_inf, ic_sup = calcular_intervalo_confianza(sub[RESPONSE_VARIABLE].values, alpha=alpha_ic)
        
        # Descriptivas de soporte (m1, m2, a_teorica)
        m1_val = sub["m1"].iloc[0] if "m1" in sub.columns else np.nan
        m2_val = sub["m2"].iloc[0] if "m2" in sub.columns else np.nan
        a_teo_val = sub["a_teorica"].iloc[0] if "a_teorica" in sub.columns else np.nan
        
        # Error estándar de la media
        n = stats_a_exp["n"]
        se = (stats_a_exp["std"] / np.sqrt(n)) if n > 0 else np.nan
        
        reg = {
            "Tratamiento": trat,
            "m1": m1_val,
            "m2": m2_val,
            "n": n,
            "media_a_exp": stats_a_exp["media"],
            "std_a_exp": stats_a_exp["std"],
            "se_a_exp": se,
            "ic_inf_95": ic_inf,
            "ic_sup_95": ic_sup,
            "mediana_a_exp": stats_a_exp["mediana"],
            "min_a_exp": stats_a_exp["min"],
            "max_a_exp": stats_a_exp["max"],
            "iqr_a_exp": stats_a_exp["iqr"],
            "cv_pct_a_exp": stats_a_exp["cv_pct"],
            "a_teorica": a_teo_val
        }
        registros.append(reg)
        
    df_trat = pd.DataFrame(registros)
    return df_trat


def generar_resumen_replicas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un resumen detallado de la distribución de réplicas por tratamiento.
    """
    if TREATMENT_VARIABLE not in df.columns or REPLICATE_VARIABLE not in df.columns:
        return pd.DataFrame()
        
    resumen = df.groupby(TREATMENT_VARIABLE).agg(
        total_replicas=(REPLICATE_VARIABLE, "count"),
        replicas_presentes=(REPLICATE_VARIABLE, lambda x: ", ".join(map(str, sorted(x.dropna().unique())))),
        orden_min=("Orden", "min") if "Orden" in df.columns else (REPLICATE_VARIABLE, lambda x: np.nan),
        orden_max=("Orden", "max") if "Orden" in df.columns else (REPLICATE_VARIABLE, lambda x: np.nan)
    ).reset_index()
    
    return resumen


def calcular_matrices_correlacion(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calcula correlaciones entre variables cuantitativas (Pearson y Spearman).
    Regla estricta (Sección 7.2): No incluye 'Orden' ni 'Replica'.
    Retorna (df_pearson_r, df_pearson_p, df_spearman_rho).
    """
    cols_cuantitativas = [c for c in QUANTITATIVE_VARIABLES if c in df.columns and c not in ["Orden", "Replica"]]
    df_clean = df[cols_cuantitativas].dropna()
    
    k = len(cols_cuantitativas)
    r_matrix = pd.DataFrame(np.ones((k, k)), index=cols_cuantitativas, columns=cols_cuantitativas)
    p_matrix = pd.DataFrame(np.zeros((k, k)), index=cols_cuantitativas, columns=cols_cuantitativas)
    rho_matrix = pd.DataFrame(np.ones((k, k)), index=cols_cuantitativas, columns=cols_cuantitativas)
    
    for i in range(k):
        for j in range(k):
            if i != j:
                col_i = cols_cuantitativas[i]
                col_j = cols_cuantitativas[j]
                
                std_i = np.std(df_clean[col_i])
                std_j = np.std(df_clean[col_j])
                
                if std_i > 1e-12 and std_j > 1e-12:
                    # Pearson
                    r_val, p_val = stats.pearsonr(df_clean[col_i], df_clean[col_j])
                    # Spearman
                    rho_val, _ = stats.spearmanr(df_clean[col_i], df_clean[col_j])
                else:
                    r_val, p_val = np.nan, np.nan
                    rho_val = np.nan
                    
                r_matrix.iloc[i, j] = r_val
                p_matrix.iloc[i, j] = p_val
                rho_matrix.iloc[i, j] = rho_val
                
    return r_matrix, p_matrix, rho_matrix


def ejecutar_analisis_descriptivo(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Orquestador del análisis descriptivo. Genera todas las tablas requeridas.
    """
    LOGGER.info("Calculando estadísticas descriptivas generales y por tratamiento...", procedure="ANALISIS_DESCRIPTIVO")
    
    df_general = generar_descriptiva_general(df)
    df_por_tratamiento = generar_descriptiva_por_tratamiento(df)
    df_replicas = generar_resumen_replicas(df)
    r_matrix, p_matrix, rho_matrix = calcular_matrices_correlacion(df)
    
    LOGGER.info(
        f"Estadísticas calculadas: {len(df_general)} variables cuantitativas, {len(df_por_tratamiento)} tratamientos.",
        procedure="ANALISIS_DESCRIPTIVO"
    )
    
    return {
        "descriptiva_general": df_general,
        "descriptiva_por_tratamiento": df_por_tratamiento,
        "resumen_replicas": df_replicas,
        "correlacion_pearson": r_matrix,
        "p_valores_pearson": p_matrix,
        "correlacion_spearman": rho_matrix
    }
