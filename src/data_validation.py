"""
Módulo de Validación y Control de Integridad de Datos Experimentales
Comprueba exhaustivamente la consistencia, completitud, tipado y ausencia
de anomalías que comprometan la validez de los modelos estadísticos.
"""

from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd

from src.config import (
    QUANTITATIVE_VARIABLES,
    CATEGORICAL_VARIABLES,
    RESPONSE_VARIABLE,
    THEORETICAL_VARIABLE,
    TREATMENT_VARIABLE,
    REPLICATE_VARIABLE
)
from src.utils import LOGGER


def validar_integridad_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta el protocolo de validación de 10 puntos establecido en la Sección 6.
    Retorna el DataFrame validado (con tipos coherentes) y el diccionario resumen de validación.
    """
    LOGGER.info("Iniciando auditoría de integridad y validación de datos...", procedure="VALIDACION_DATOS")
    
    problemas_detectados: List[str] = []
    total_registros_inicial = len(df)
    
    # 1. Detección y descarte justificado de filas completamente vacías
    filas_vacias = df.isna().all(axis=1)
    n_filas_vacias = int(filas_vacias.sum())
    if n_filas_vacias > 0:
        problemas_detectados.append(f"Se detectaron {n_filas_vacias} registros completamente vacíos (se descartan justificadamente).")
        df_val = df[~filas_vacias].copy()
    else:
        df_val = df.copy()
        
    # 2. Detección de posibles duplicados (reportar, no eliminar)
    filas_duplicadas = df_val.duplicated()
    n_duplicados = int(filas_duplicadas.sum())
    if n_duplicados > 0:
        problemas_detectados.append(f"ADVERTENCIA: Se detectaron {n_duplicados} filas con valores idénticos en todas las columnas.")
        
    # 3. Conteo de valores faltantes por columna
    valores_faltantes = df_val.isna().sum().to_dict()
    total_faltantes = sum(valores_faltantes.values())
    if total_faltantes > 0:
        problemas_detectados.append(f"Se detectaron {total_faltantes} celdas con valores faltantes: {valores_faltantes}")
        
    # 4. Conversión y validación de tipos cuantitativos
    errores_conversion = {}
    for col in QUANTITATIVE_VARIABLES:
        if col in df_val.columns:
            serie_num = pd.to_numeric(df_val[col], errors="coerce")
            n_invalidos = int(serie_num.isna().sum() - df_val[col].isna().sum())
            if n_invalidos > 0:
                errores_conversion[col] = n_invalidos
                problemas_detectados.append(f"Columna '{col}' contiene {n_invalidos} valores no numéricos o corruptos.")
            df_val[col] = serie_num
            
    # 5. Validación de variables categóricas
    if TREATMENT_VARIABLE in df_val.columns:
        df_val[TREATMENT_VARIABLE] = df_val[TREATMENT_VARIABLE].astype(str).str.strip()
    if REPLICATE_VARIABLE in df_val.columns:
        df_val[REPLICATE_VARIABLE] = pd.to_numeric(df_val[REPLICATE_VARIABLE], errors="coerce").astype("Int64")
    if "Orden" in df_val.columns:
        df_val["Orden"] = pd.to_numeric(df_val["Orden"], errors="coerce").astype("Int64")
        
    # 6. Comprobación de valores imposibles o inconsistencias físicas
    # Tiempo no debe ser menor o igual a cero
    if "t" in df_val.columns:
        tiempos_invalidos = (df_val["t"] <= 0).sum()
        if tiempos_invalidos > 0:
            problemas_detectados.append(f"Se detectaron {tiempos_invalidos} registros con tiempo t <= 0 (incompatible con cinemática).")
            
    # Masas no deben ser negativas o cero
    for m_col in ["m1", "m2"]:
        if m_col in df_val.columns:
            masas_invalidas = (df_val[m_col] <= 0).sum()
            if masas_invalidas > 0:
                problemas_detectados.append(f"Se detectaron {masas_invalidas} registros con masa {m_col} <= 0.")
                
    # Aceleración experimental no debe ser nula o negativa si el sistema parte del reposo
    if RESPONSE_VARIABLE in df_val.columns:
        a_invalidas = (df_val[RESPONSE_VARIABLE] <= 0).sum()
        if a_invalidas > 0:
            problemas_detectados.append(f"Se detectaron {a_invalidas} registros con aceleración experimental <= 0.")
            
    # 7. Resumen de tratamientos y réplicas
    tratamientos_unicos = df_val[TREATMENT_VARIABLE].unique().tolist() if TREATMENT_VARIABLE in df_val.columns else []
    conteo_por_tratamiento = df_val.groupby(TREATMENT_VARIABLE)[REPLICATE_VARIABLE].count().to_dict() if TREATMENT_VARIABLE in df_val.columns else {}
    replicas_unicas = df_val[REPLICATE_VARIABLE].dropna().unique().tolist() if REPLICATE_VARIABLE in df_val.columns else []
    
    # Determinar si el diseño es balanceado
    cuentas_rep = list(conteo_por_tratamiento.values())
    es_balanceado = len(set(cuentas_rep)) == 1 if cuentas_rep else False
    
    # Contar observaciones válidas (filas sin NaN en las variables críticas de análisis)
    columnas_criticas = [TREATMENT_VARIABLE, RESPONSE_VARIABLE, THEORETICAL_VARIABLE]
    filas_validas = df_val.dropna(subset=[c for c in columnas_criticas if c in df_val.columns])
    n_observaciones_validas = len(filas_validas)
    
    resumen_validacion = {
        "total_registros_inicial": total_registros_inicial,
        "registros_completamente_vacios": n_filas_vacias,
        "observaciones_validas": n_observaciones_validas,
        "duplicados_reportados": n_duplicados,
        "valores_faltantes_por_columna": valores_faltantes,
        "errores_conversion_numerica": errores_conversion,
        "numero_tratamientos": len(tratamientos_unicos),
        "tratamientos_identificados": tratamientos_unicos,
        "numero_replicas_identificadas": len(replicas_unicas),
        "replicas_identificadas": replicas_unicas,
        "observaciones_por_tratamiento": conteo_por_tratamiento,
        "diseno_balanceado": es_balanceado,
        "problemas_detectados": problemas_detectados,
        "estado_general": "APROBADO_CON_OBSERVACIONES" if problemas_detectados else "APROBADO_CONFORME"
    }
    
    if problemas_detectados:
        for p in problemas_detectados:
            LOGGER.warning(p, procedure="VALIDACION_DATOS")
    else:
        LOGGER.info("Control de calidad y validación superado al 100% sin anomalías.", procedure="VALIDACION_DATOS")
        
    return df_val, resumen_validacion
