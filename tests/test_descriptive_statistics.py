"""
Pruebas Unitarias para Estadística Descriptiva (descriptive_statistics.py)
Utiliza datos sintéticos exclusivamente en memoria.
"""

import pytest
import numpy as np
import pandas as pd
from src.descriptive_statistics import (
    calcular_estadisticas_univariadas,
    generar_descriptiva_general,
    generar_descriptiva_por_tratamiento,
    calcular_matrices_correlacion
)
from src.utils import calcular_intervalo_confianza


def test_calcular_estadisticas_univariadas_conocidas():
    valores = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    res = calcular_estadisticas_univariadas(valores)
    assert res["n"] == 5
    assert pytest.approx(res["media"], 0.001) == 30.0
    assert pytest.approx(res["mediana"], 0.001) == 30.0
    assert pytest.approx(res["min"], 0.001) == 10.0
    assert pytest.approx(res["max"], 0.001) == 50.0
    assert pytest.approx(res["iqr"], 0.001) == 20.0  # Q3(40) - Q1(20)


def test_calcular_intervalo_confianza():
    datos = np.array([10.0, 10.0, 10.0, 10.0])
    media, ic_inf, ic_sup = calcular_intervalo_confianza(datos, alpha=0.05)
    assert media == 10.0
    assert ic_inf == 10.0
    assert ic_sup == 10.0


def test_correlaciones_excluyen_orden_y_replica():
    df_prueba = pd.DataFrame({
        "Orden": [1, 2, 3, 4],
        "Replica": [1, 2, 1, 2],
        "m1": [0.1, 0.2, 0.1, 0.2],
        "m2": [0.01, 0.02, 0.01, 0.02],
        "vA": [1.0, 2.0, 1.1, 2.1],
        "vB": [2.0, 4.0, 2.2, 4.1],
        "t": [0.5, 0.5, 0.5, 0.5],
        "a_experimental": [2.0, 4.0, 2.2, 4.0],
        "a_teorica": [2.0, 4.0, 2.0, 4.0]
    })
    r_mat, p_mat, rho_mat = calcular_matrices_correlacion(df_prueba)
    assert "Orden" not in r_mat.columns
    assert "Replica" not in r_mat.columns
    assert "a_experimental" in r_mat.columns
