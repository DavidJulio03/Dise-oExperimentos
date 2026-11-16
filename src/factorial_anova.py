"""
Módulo de Identificación del Diseño Experimental y Modelos ANOVA
Implementa la lógica de decisión metodológica (Sección 4.1, 4.2 y 8):
- Inspección rigurosa de factores o fallback a ANOVA de un factor.
- Ajuste de modelo OLS factorial con sumas de cuadrados Tipo III.
- Cálculo de estadísticos, tamaños del efecto (eta y omega cuadrado) e interpretación de interacción.
"""

import re
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from src.config import (
    RESPONSE_VARIABLE,
    TREATMENT_VARIABLE,
    FACTOR_MAP,
    DEFAULT_ALPHA,
    ANOVA_TYPE
)
from src.utils import calcular_tamanos_efecto, LOGGER


def identificar_diseno_experimental(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Analiza la columna Tratamiento para determinar si es metodológicamente justificable
    descomponerla en dos o más factores independientes (Sección 4.1).
    
    1. Revisa si existe un FACTOR_MAP explícito en config.py.
    2. Si está vacío, inspecciona si las etiquetas codifican inequívocamente combinaciones (ej. A1B1 a A3B3).
    3. Si no existe evidencia suficiente, activa el protocolo de fallback a ANOVA de un factor (Sección 4.2).
    """
    df_mod = df.copy()
    tratamientos_unicos = df_mod[TREATMENT_VARIABLE].dropna().unique().tolist()
    
    # Caso 1: Mapeo explícito en FACTOR_MAP
    if FACTOR_MAP:
        LOGGER.info("Se detectó configuración explícita en FACTOR_MAP (config.py).", procedure="IDENTIFICACION_DISENO")
        factor_names = list(next(iter(FACTOR_MAP.values())).keys())
        for f_name in factor_names:
            df_mod[f_name] = df_mod[TREATMENT_VARIABLE].map(lambda t: FACTOR_MAP.get(t, {}).get(f_name, np.nan))
            
        return df_mod, {
            "tipo_diseno": "FACTORIAL_DOS_VIAS",
            "justificacion": "Mapeo explícito configurado en FACTOR_MAP por el investigador.",
            "factores": factor_names,
            "niveles_por_factor": {f: sorted(df_mod[f].dropna().unique().tolist()) for f in factor_names}
        }
        
    # Caso 2: Inspección de patrón inequívoco en etiquetas (ej. 'A1B1', 'A1B2', ...)
    patron_ab = re.compile(r"^A(\d+)B(\d+)$", re.IGNORECASE)
    coincidencias = [patron_ab.match(str(t).strip()) for t in tratamientos_unicos]
    
    if all(m is not None for m in coincidencias) and len(coincidencias) > 0:
        LOGGER.info(
            "Patrón factorial inequívoco detectado en 'Tratamiento' (Formato AiBj). "
            "Descomponiendo en Factor_A (Deslizador) y Factor_B (Colgante).",
            procedure="IDENTIFICACION_DISENO"
        )
        # Extraer niveles
        df_mod["Factor_A"] = df_mod[TREATMENT_VARIABLE].apply(lambda x: f"A{patron_ab.match(str(x).strip()).group(1)}")
        df_mod["Factor_B"] = df_mod[TREATMENT_VARIABLE].apply(lambda x: f"B{patron_ab.match(str(x).strip()).group(2)}")
        
        # Validar consistencia con columnas cuantitativas m1 y m2 si existen
        consistencia_m1 = df_mod.groupby("Factor_A")["m1"].nunique().max() == 1 if "m1" in df_mod.columns else False
        consistencia_m2 = df_mod.groupby("Factor_B")["m2"].nunique().max() == 1 if "m2" in df_mod.columns else False
        
        justificacion = (
            "Codificación factorial ortogonal inequívoca AiBj en la columna Tratamiento. "
            f"Validación con masas: Factor_A corresponde estrictamente a m1 ({consistencia_m1}) "
            f"y Factor_B a m2 ({consistencia_m2})."
        )
        
        return df_mod, {
            "tipo_diseno": "FACTORIAL_DOS_VIAS",
            "justificacion": justificacion,
            "factores": ["Factor_A", "Factor_B"],
            "niveles_por_factor": {
                "Factor_A": sorted(df_mod["Factor_A"].unique().tolist()),
                "Factor_B": sorted(df_mod["Factor_B"].unique().tolist())
            }
        }
        
    # Caso 3: Fallback riguroso a ANOVA de un factor (Sección 4.2)
    LOGGER.warning(
        "No es posible descomponer objetivamente 'Tratamiento' en factores múltiples sin suposiciones no verificables. "
        "Activando protocolo metodológico: ANOVA de un factor con Tratamiento como variable explicativa.",
        procedure="IDENTIFICACION_DISENO"
    )
    return df_mod, {
        "tipo_diseno": "UN_FACTOR_TRATAMIENTOS",
        "justificacion": (
            "No se dispone de mapeo explícito ni codificación factorial inequívoca. "
            "Se implementa estrictamente ANOVA de un factor para preservar la validez metodológica."
        ),
        "factores": [TREATMENT_VARIABLE],
        "niveles_por_factor": {TREATMENT_VARIABLE: sorted(tratamientos_unicos)}
    }


def ajustar_modelo_anova(df_diseno: pd.DataFrame, meta_diseno: Dict[str, Any], alpha: float = DEFAULT_ALPHA) -> Tuple[Any, pd.DataFrame, Dict[str, Any]]:
    """
    Ajusta el modelo lineal OLS y construye la tabla ANOVA con sumas de cuadrados Tipo III,
    tamaños de efecto (eta y omega cuadrado) e interpretación rigurosa.
    """
    tipo_diseno = meta_diseno["tipo_diseno"]
    
    if tipo_diseno == "FACTORIAL_DOS_VIAS":
        f_a, f_b = meta_diseno["factores"][:2]
        formula = f"{RESPONSE_VARIABLE} ~ C({f_a}) + C({f_b}) + C({f_a}):C({f_b})"
        LOGGER.info(f"Ajustando modelo factorial OLS: {formula}", procedure="AJUSTE_ANOVA")
        modelo = smf.ols(formula, data=df_diseno).fit()
        
        # Tabla ANOVA Tipo III
        tabla_base = sm.stats.anova_lm(modelo, typ=ANOVA_TYPE)
        tabla_base["mean_sq"] = tabla_base["sum_sq"] / tabla_base["df"]
        
        # Tamaño del efecto
        ss_error = float(tabla_base.loc["Residual", "sum_sq"])
        ms_error = float(tabla_base.loc["Residual", "mean_sq"])
        ss_total = float(tabla_base["sum_sq"].sum())
        
        eta_sq_col, partial_eta_col, omega_sq_col = [], [], []
        for idx, row in tabla_base.iterrows():
            if idx in ["Residual", "Intercept"]:
                eta_sq_col.append(np.nan)
                partial_eta_col.append(np.nan)
                omega_sq_col.append(np.nan)
            else:
                eff = calcular_tamanos_efecto(row["sum_sq"], row["df"], ss_error, ms_error, ss_total)
                eta_sq_col.append(eff["eta_cuadrado"])
                partial_eta_col.append(eff["eta_cuadrado_parcial"])
                omega_sq_col.append(eff["omega_cuadrado"])
                
        tabla_base["eta_sq"] = eta_sq_col
        tabla_base["eta_sq_parcial"] = partial_eta_col
        tabla_base["omega_sq"] = omega_sq_col
        
        # Identificar significancia de interacción
        fila_inter = [idx for idx in tabla_base.index if ":" in idx]
        p_inter = tabla_base.loc[fila_inter[0], "PR(>F)"] if fila_inter else np.nan
        interaccion_significativa = (p_inter < alpha) if not np.isnan(p_inter) else False
        
        interpretacion_interaccion = (
            f"La interacción entre {f_a} y {f_b} es {'ESTADÍSTICAMENTE SIGNIFICATIVA' if interaccion_significativa else 'NO SIGNIFICATIVA'} "
            f"(F = {tabla_base.loc[fila_inter[0], 'F']:.4f}, p = {p_inter:.5e}). "
            + ("Los efectos principales no deben interpretarse de forma aislada; el efecto de un factor depende del nivel del otro."
               if interaccion_significativa else
               "Los efectos de ambos factores son aditivos e independientes.")
        )
        
        resumen_modelo = {
            "tipo_diseno": tipo_diseno,
            "formula": formula,
            "r2": float(modelo.rsquared),
            "r2_adj": float(modelo.rsquared_adj),
            "f_stat_global": float(modelo.fvalue),
            "p_val_global": float(modelo.f_pvalue),
            "interaccion_significativa": interaccion_significativa,
            "p_interaccion": float(p_inter),
            "interpretacion_interaccion": interpretacion_interaccion,
            "grados_libertad_error": int(modelo.df_resid)
        }
        
    else:  # ANOVA de un factor (Tratamiento)
        formula = f"{RESPONSE_VARIABLE} ~ C({TREATMENT_VARIABLE})"
        LOGGER.info(f"Ajustando modelo ANOVA de un factor OLS: {formula}", procedure="AJUSTE_ANOVA")
        modelo = smf.ols(formula, data=df_diseno).fit()
        
        tabla_base = sm.stats.anova_lm(modelo, typ=1)
        tabla_base["mean_sq"] = tabla_base["sum_sq"] / tabla_base["df"]
        
        ss_error = float(tabla_base.loc["Residual", "sum_sq"])
        ms_error = float(tabla_base.loc["Residual", "mean_sq"])
        ss_total = float(tabla_base["sum_sq"].sum())
        
        eta_sq_col, partial_eta_col, omega_sq_col = [], [], []
        for idx, row in tabla_base.iterrows():
            if idx == "Residual":
                eta_sq_col.append(np.nan)
                partial_eta_col.append(np.nan)
                omega_sq_col.append(np.nan)
            else:
                eff = calcular_tamanos_efecto(row["sum_sq"], row["df"], ss_error, ms_error, ss_total)
                eta_sq_col.append(eff["eta_cuadrado"])
                partial_eta_col.append(eff["eta_cuadrado_parcial"])
                omega_sq_col.append(eff["omega_cuadrado"])
                
        tabla_base["eta_sq"] = eta_sq_col
        tabla_base["eta_sq_parcial"] = partial_eta_col
        tabla_base["omega_sq"] = omega_sq_col
        
        resumen_modelo = {
            "tipo_diseno": tipo_diseno,
            "formula": formula,
            "r2": float(modelo.rsquared),
            "r2_adj": float(modelo.rsquared_adj),
            "f_stat_global": float(modelo.fvalue),
            "p_val_global": float(modelo.f_pvalue),
            "interaccion_significativa": False,
            "p_interaccion": np.nan,
            "interpretacion_interaccion": "No aplica interacción en diseño de un solo factor.",
            "grados_libertad_error": int(modelo.df_resid)
        }
        
    return modelo, tabla_base, resumen_modelo
