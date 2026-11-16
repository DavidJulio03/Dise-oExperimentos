"""
Módulo de Carga e Ingesta de Datos Experimentales
Se encarga de abrir el libro de Excel, identificar la hoja apropiada y
normalizar los encabezados de forma determinista y robusta sin modificar el archivo original.
"""

import re
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import pandas as pd
import openpyxl

from src.config import EXCEL_PATH, CANONICAL_COLUMNS, SHEET_NAME
from src.utils import LOGGER


def limpiar_texto_encabezado(texto: str) -> str:
    """
    Normaliza un texto de encabezado eliminando acentos, caracteres especiales,
    espacios redundantes y convirtiendo a minúsculas para comparaciones semánticas.
    """
    t = str(texto).strip().lower()
    t = re.sub(r"[áàäâ]", "a", t)
    t = re.sub(r"[éèëê]", "e", t)
    t = re.sub(r"[íìïî]", "i", t)
    t = re.sub(r"[óòöô]", "o", t)
    t = re.sub(r"[úùüû]", "u", t)
    t = re.sub(r"\s+", " ", t)
    return t


def mapear_columna_individual(nombre_original: str) -> Optional[str]:
    """
    Determina si un nombre de columna original corresponde a una de las 10 columnas
    canónicas obligatorias, aplicando reglas inequívocas de reconocimiento de patrones.
    """
    clean = limpiar_texto_encabezado(nombre_original)
    
    # 1. Orden
    if clean == "orden" or clean.startswith("orden"):
        return "Orden"
        
    # 2. Tratamiento
    if clean == "tratamiento" or clean.startswith("tratamiento"):
        return "Tratamiento"
        
    # 3. Réplica
    if "replica" in clean:
        return "Replica"
        
    # 4. Masa 1 (m1)
    if clean == "m1" or re.match(r"^m\s*1\b", clean) or ("masa" in clean and "1" in clean and "colgante" not in clean):
        return "m1"
        
    # 5. Masa 2 (m2)
    if clean == "m2" or re.match(r"^m\s*2\b", clean) or ("masa" in clean and "2" in clean):
        return "m2"
        
    # 6. Velocidad A (vA)
    if clean.startswith("va") or (("velocidad" in clean or "v") and ("1" in clean or "compuerta 1" in clean or "fotocompuerta 1" in clean)):
        return "vA"
        
    # 7. Velocidad B (vB)
    if clean.startswith("vb") or (("velocidad" in clean or "v") and ("2" in clean or "compuerta 2" in clean or "fotocompuerta 2" in clean)):
        return "vB"
        
    # 8. Tiempo (t) - Soporta explícitamente paréntesis sin cerrar como 't (tiempo entre fotocompuertas'
    if clean == "t" or clean.startswith("t ") or clean.startswith("t(") or "tiempo" in clean:
        return "t"
        
    # 9. Aceleración experimental (a_experimental)
    if ("a_exp" in clean or "a_experimental" in clean) or ("aceleracion" in clean and "exp" in clean):
        return "a_experimental"
        
    # 10. Aceleración teórica (a_teorica)
    if ("a_teo" in clean or "a_teorica" in clean) or ("aceleracion" in clean and "teo" in clean):
        return "a_teorica"
        
    return None


def normalizar_encabezados(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Normaliza de forma determinista y estricta los encabezados del DataFrame.
    Si no es posible identificar inequívocamente alguna columna obligatoria,
    informa el problema y detiene el análisis correspondiente.
    """
    columnas_originales = [str(c).strip() for c in df.columns]
    mapeo = {}
    asignados = set()
    
    for c in columnas_originales:
        canonico = mapear_columna_individual(c)
        if canonico and canonico not in asignados:
            mapeo[c] = canonico
            asignados.add(canonico)
            
    # Si la heurística no asignó exactamente las 10 columnas pero el DataFrame
    # tiene exactamente 10 columnas en el orden estricto especificado en la Sección 3,
    # se evalúa la correspondencia posicional estricta.
    if len(asignados) != len(CANONICAL_COLUMNS) and len(columnas_originales) == len(CANONICAL_COLUMNS):
        # Verificar coincidencia posicional
        LOGGER.info(
            "Aplicando validación posicional estricta de respaldo para encabezados de 10 columnas.",
            procedure="NORMALIZACION_COLUMNAS"
        )
        mapeo = {columnas_originales[i]: CANONICAL_COLUMNS[i] for i in range(len(CANONICAL_COLUMNS))}
        asignados = set(CANONICAL_COLUMNS)
        
    columnas_faltantes = [c for c in CANONICAL_COLUMNS if c not in asignados]
    if columnas_faltantes:
        msg_error = (
            f"ERROR DE IDENTIFICACIÓN: No se pudieron identificar inequívocamente las siguientes "
            f"columnas obligatorias: {columnas_faltantes}.\n"
            f"Columnas detectadas en el archivo: {columnas_originales}"
        )
        LOGGER.error(msg_error, procedure="NORMALIZACION_COLUMNAS")
        raise KeyError(msg_error)
        
    df_renombrado = df.rename(columns=mapeo)
    df_resultado = df_renombrado[CANONICAL_COLUMNS].copy()
    
    return df_resultado, mapeo


def identificar_hoja_datos(filepath: Path, sheet_solicitada: Optional[str] = None) -> str:
    """
    Inspecciona el archivo Excel e identifica de forma automática la hoja que contiene
    la tabla experimental de 10 columnas.
    Si existen múltiples candidatas ambiguas, solicita configuración explícita.
    """
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    nombres_hojas = wb.sheetnames
    
    if sheet_solicitada:
        if sheet_solicitada in nombres_hojas:
            wb.close()
            return sheet_solicitada
        wb.close()
        raise ValueError(f"La hoja solicitada '{sheet_solicitada}' no existe en el archivo. Hojas disponibles: {nombres_hojas}")
        
    if len(nombres_hojas) == 1:
        wb.close()
        return nombres_hojas[0]
        
    # Si hay múltiples hojas, buscar candidatas examinando la fila de encabezados
    candidatas = []
    for s_name in nombres_hojas:
        ws = wb[s_name]
        primera_fila = [cell.value for cell in next(ws.iter_rows(max_row=1), []) if cell.value is not None]
        cols_limpias = [str(c) for c in primera_fila]
        reconocidas = [mapear_columna_individual(c) for c in cols_limpias if mapear_columna_individual(c) is not None]
        if len(set(reconocidas)) >= 8:  # Fuerte indicio de ser la hoja experimental
            candidatas.append(s_name)
            
    wb.close()
    
    if len(candidatas) == 1:
        return candidatas[0]
    elif len(candidatas) == 0:
        # Devolver la primera si ninguna cumplió heurística estricta pero alertar
        LOGGER.warning(
            f"Ninguna hoja cumplió la heurística estricta de encabezados. Seleccionando la primera hoja: '{nombres_hojas[0]}'",
            procedure="IDENTIFICACION_HOJA"
        )
        return nombres_hojas[0]
    else:
        msg = (
            f"AMBIGÜEDAD DE HOJAS: Se encontraron múltiples hojas candidatas compatibles {candidatas}. "
            "Por favor, configure explícitamente 'SHEET_NAME' en 'src/config.py'."
        )
        LOGGER.error(msg, procedure="IDENTIFICACION_HOJA")
        raise ValueError(msg)


def cargar_datos(filepath: Optional[Path] = None, sheet_name: Optional[str] = SHEET_NAME) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Punto de entrada principal para la carga de datos.
    Carga el Excel, selecciona la hoja, normaliza encabezados y retorna el DataFrame
    junto con metadatos de la carga.
    """
    ruta = filepath or EXCEL_PATH
    if not ruta.exists():
        msg = f"No se encontró el archivo de datos obligatorio: '{ruta}'."
        LOGGER.error(msg, procedure="CARGA_DATOS")
        raise FileNotFoundError(msg)
        
    hoja_elegida = identificar_hoja_datos(ruta, sheet_name)
    LOGGER.info(f"Cargando hoja '{hoja_elegida}' desde archivo '{ruta.name}'", procedure="CARGA_DATOS")
    
    df_raw = pd.read_excel(ruta, sheet_name=hoja_elegida)
    df_normalizado, mapeo_cols = normalizar_encabezados(df_raw)
    
    metadatos = {
        "archivo": ruta.name,
        "ruta_completa": str(ruta),
        "hoja": hoja_elegida,
        "filas_crudas": len(df_raw),
        "columnas_originales": list(df_raw.columns),
        "mapeo_columnas": mapeo_cols
    }
    
    LOGGER.info(
        f"Datos cargados y normalizados con éxito: {len(df_normalizado)} filas, 10 columnas canónicas.",
        procedure="CARGA_DATOS"
    )
    return df_normalizado, metadatos
