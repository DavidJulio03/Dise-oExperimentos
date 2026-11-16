"""
Pruebas Unitarias para Carga y Normalización de Encabezados (data_loader.py)
Utiliza datos sintéticos exclusivamente en memoria.
"""

import pytest
import pandas as pd
from src.data_loader import normalizar_encabezados, limpiar_texto_encabezado, mapear_columna_individual
from src.config import CANONICAL_COLUMNS


def test_limpiar_texto_encabezado():
    assert limpiar_texto_encabezado("  Aceleración Experimental  ") == "aceleracion experimental"
    assert limpiar_texto_encabezado("Réplica ") == "replica"
    assert limpiar_texto_encabezado("t (tiempo entre fotocompuertas") == "t (tiempo entre fotocompuertas"


def test_mapear_columna_individual():
    assert mapear_columna_individual("Orden") == "Orden"
    assert mapear_columna_individual("Tratamiento ") == "Tratamiento"
    assert mapear_columna_individual("Replica") == "Replica"
    assert mapear_columna_individual("m1") == "m1"
    assert mapear_columna_individual("m2") == "m2"
    assert mapear_columna_individual("vA (velocidad en fotocompuerta 1)") == "vA"
    assert mapear_columna_individual("vB (velocidad en fotocompuerta 2)") == "vB"
    # Soporte explícito para encabezado sin paréntesis de cierre
    assert mapear_columna_individual("t (tiempo entre fotocompuertas") == "t"
    assert mapear_columna_individual("a_experimental") == "a_experimental"
    assert mapear_columna_individual("a_teorica") == "a_teorica"


def test_normalizar_encabezados_exitoso():
    columnas_prueba = [
        "Orden",
        "Tratamiento",
        "Replica",
        "m1",
        "m2",
        "vA (velocidad en fotocompuerta 1)",
        "vB (velocidad en fotocompuerta 2)",
        "t (tiempo entre fotocompuertas",
        "a_experimental",
        "a_teorica"
    ]
    df_dummy = pd.DataFrame(columns=columnas_prueba)
    df_norm, mapeo = normalizar_encabezados(df_dummy)
    assert list(df_norm.columns) == CANONICAL_COLUMNS
    assert len(mapeo) == 10


def test_normalizar_encabezados_columna_faltante():
    columnas_incompletas = [
        "Orden", "Tratamiento", "Replica", "m1", "m2", "vA", "vB", "t", "a_experimental"
        # falta a_teorica
    ]
    df_incompleto = pd.DataFrame(columns=columnas_incompletas)
    with pytest.raises(KeyError):
        normalizar_encabezados(df_incompleto)
