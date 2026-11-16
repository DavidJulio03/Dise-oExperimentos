"""
Módulo de Comparaciones Múltiples y Pruebas Post-Hoc
Implementa comparaciones con control de tasa de error familiar (Tukey HSD y Games-Howell)
bajo lógica condicional según la significancia del ANOVA y de las interacciones (Sección 8.4).
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from src.config import RESPONSE_VARIABLE, TREATMENT_VARIABLE, DEFAULT_ALPHA
from src.utils import LOGGER


def calcular_games_howell(grupo_nombres: np.ndarray, valores: np.ndarray, alpha: float = DEFAULT_ALPHA) -> pd.DataFrame:
    """
    Implementación del procedimiento post-hoc Games-Howell para comparaciones múltiples
    robusto a heterocedasticidad (varianzas desiguales) y tamaños muestrales variables.
    """
    df_temp = pd.DataFrame({"grupo": grupo_nombres, "valor": valores}).dropna()
    grupos = sorted(df_temp["grupo"].unique())
    k = len(grupos)
    
    # Calcular estadísticas por grupo
    stats_por_grupo = {}
    for g in grupos:
        vals = df_temp[df_temp["grupo"] == g]["valor"].values
        n_i = len(vals)
        mean_i = np.mean(vals)
        var_i = np.var(vals, ddof=1) if n_i > 1 else 0.0
        stats_por_grupo[g] = {"n": n_i, "mean": mean_i, "var": var_i}
        
    filas = []
    for i in range(k):
        for j in range(i + 1, k):
            g1, g2 = grupos[i], grupos[j]
            s1, s2 = stats_por_grupo[g1], stats_por_grupo[g2]
            
            diff = s1["mean"] - s2["mean"]
            var_term = (s1["var"] / s1["n"]) + (s2["var"] / s2["n"])
            se_diff = np.sqrt(var_term) if var_term > 0 else 1e-12
            
            # Grados de libertad Welch-Satterthwaite
            numerador_df = var_term**2
            denom_df = ((s1["var"] / s1["n"])**2 / (s1["n"] - 1)) + ((s2["var"] / s2["n"])**2 / (s2["n"] - 1)) if (s1["n"] > 1 and s2["n"] > 1) else 1
            df_ws = numerador_df / denom_df if denom_df > 0 else 1.0
            
            # Estadístico t de Welch y p-valor ajustado de Tukey-Kramer / Studentized Range
            t_val = abs(diff) / se_diff
            # Aproximación del rango estudentizado q = t * sqrt(2)
            q_val = t_val * np.sqrt(2)
            p_adj = float(stats.studentized_range.sf(q_val, k, df_ws))
            p_adj = min(1.0, max(0.0, p_adj))
            
            # Intervalo de confianza
            q_crit = float(stats.studentized_range.ppf(1 - alpha, k, df_ws))
            margen = (q_crit / np.sqrt(2)) * se_diff
            
            filas.append({
                "group1": g1,
                "group2": g2,
                "meandiff": float(diff),
                "p-adj": float(p_adj),
                "lower": float(diff - margen),
                "upper": float(diff + margen),
                "reject": bool(p_adj < alpha)
            })
            
    return pd.DataFrame(filas)


def ejecutar_pruebas_post_hoc(
    df: pd.DataFrame,
    meta_diseno: Dict[str, Any],
    resumen_modelo: Dict[str, Any],
    anova_tabla: pd.DataFrame,
    usar_games_howell: bool = False,
    alpha: float = DEFAULT_ALPHA
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta el protocolo de comparaciones múltiples condicional:
    - En Factorial con interacción significativa: evalúa tratamientos combinados.
    - En Factorial sin interacción: evalúa únicamente factores principales significativos.
    - En ANOVA de 1 factor: evalúa tratamientos si el factor fue significativo.
    """
    LOGGER.info("Determinando necesidad y alcance de comparaciones post-hoc...", procedure="POST_HOC")
    
    tipo_diseno = meta_diseno["tipo_diseno"]
    lista_dfs = []
    justificacion_posthoc = []
    
    if tipo_diseno == "FACTORIAL_DOS_VIAS":
        inter_sig = resumen_modelo.get("interaccion_significativa", False)
        f_a, f_b = meta_diseno["factores"][:2]
        
        if inter_sig:
            justificacion = (
                f"INTERACCIÓN SIGNIFICATIVA: Dado que la interacción C({f_a}):C({f_b}) resultó estadísticamente "
                f"significativa (p = {resumen_modelo.get('p_interaccion', 0):.5e} < {alpha}), los efectos principales no son aditivos. "
                "Por consiguiente, se ejecutan comparaciones post-hoc sobre los tratamientos combinados para identificar "
                "qué celdas difieren entre sí."
            )
            justificacion_posthoc.append(justificacion)
            LOGGER.info(justificacion, procedure="POST_HOC")
            
            if usar_games_howell:
                df_tukey = calcular_games_howell(df[TREATMENT_VARIABLE].values, df[RESPONSE_VARIABLE].values, alpha=alpha)
                df_tukey.insert(0, "Factor_Comparado", "Tratamiento_Combinado (Games-Howell)")
            else:
                res_tukey = pairwise_tukeyhsd(endog=df[RESPONSE_VARIABLE], groups=df[TREATMENT_VARIABLE], alpha=alpha)
                df_tukey = pd.DataFrame(data=res_tukey._results_table.data[1:], columns=res_tukey._results_table.data[0])
                df_tukey.insert(0, "Factor_Comparado", "Tratamiento_Combinado (Tukey HSD)")
            lista_dfs.append(df_tukey)
            
        else:
            justificacion = (
                f"INTERACCIÓN NO SIGNIFICATIVA: La interacción C({f_a}):C({f_b}) no es significativa "
                f"(p = {resumen_modelo.get('p_interaccion', 1):.4f} >= {alpha}). Siguiendo el principio de parsimonia "
                "y control de la tasa de error familiar, se evita comparar pares de combinaciones y se evalúan "
                "únicamente los factores principales significativos."
            )
            justificacion_posthoc.append(justificacion)
            LOGGER.info(justificacion, procedure="POST_HOC")
            
            # Evaluar factor A
            fila_fa = [idx for idx in anova_tabla.index if f_a in idx and ":" not in idx]
            if fila_fa and anova_tabla.loc[fila_fa[0], "PR(>F)"] < alpha:
                justificacion_posthoc.append(f"- Factor {f_a} significativo: Se evalúan contrastes entre sus niveles.")
                res_a = pairwise_tukeyhsd(endog=df[RESPONSE_VARIABLE], groups=df[f_a].astype(str), alpha=alpha)
                df_a = pd.DataFrame(data=res_a._results_table.data[1:], columns=res_a._results_table.data[0])
                df_a.insert(0, "Factor_Comparado", f"Factor_{f_a}")
                lista_dfs.append(df_a)
                
            # Evaluar factor B
            fila_fb = [idx for idx in anova_tabla.index if f_b in idx and ":" not in idx]
            if fila_fb and anova_tabla.loc[fila_fb[0], "PR(>F)"] < alpha:
                justificacion_posthoc.append(f"- Factor {f_b} significativo: Se evalúan contrastes entre sus niveles.")
                res_b = pairwise_tukeyhsd(endog=df[RESPONSE_VARIABLE], groups=df[f_b].astype(str), alpha=alpha)
                df_b = pd.DataFrame(data=res_b._results_table.data[1:], columns=res_b._results_table.data[0])
                df_b.insert(0, "Factor_Comparado", f"Factor_{f_b}")
                lista_dfs.append(df_b)
                
    else:  # ANOVA de un factor
        fila_trat = [idx for idx in anova_tabla.index if TREATMENT_VARIABLE in idx]
        p_trat = anova_tabla.loc[fila_trat[0], "PR(>F)"] if fila_trat else 1.0
        
        if p_trat < alpha:
            justificacion = f"El efecto del Tratamiento es significativo (p = {p_trat:.5e} < {alpha}). Se ejecuta Tukey HSD."
            justificacion_posthoc.append(justificacion)
            res_trat = pairwise_tukeyhsd(endog=df[RESPONSE_VARIABLE], groups=df[TREATMENT_VARIABLE], alpha=alpha)
            df_trat = pd.DataFrame(data=res_trat._results_table.data[1:], columns=res_trat._results_table.data[0])
            df_trat.insert(0, "Factor_Comparado", "Tratamiento")
            lista_dfs.append(df_trat)
        else:
            justificacion = f"El efecto del Tratamiento no es significativo (p = {p_trat:.4f} >= {alpha}). Se omiten comparaciones múltiples."
            justificacion_posthoc.append(justificacion)
            
    df_consolidado = pd.concat(lista_dfs, ignore_index=True) if lista_dfs else pd.DataFrame(
        columns=["Factor_Comparado", "group1", "group2", "meandiff", "p-adj", "lower", "upper", "reject"]
    )
    
    meta_posthoc = {
        "justificacion": "\n".join(justificacion_posthoc),
        "total_comparaciones": len(df_consolidado),
        "diferencias_significativas": int(df_consolidado["reject"].sum()) if not df_consolidado.empty else 0
    }
    
    return df_consolidado, meta_posthoc
