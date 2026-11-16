"""
Pruebas Unitarias para Comparación Teórica y Medidas de Error (theoretical_comparison.py)
Utiliza datos sintéticos exclusivamente en memoria.
"""

import pytest
import numpy as np
import pandas as pd
from src.theoretical_comparison import (
    calcular_errores_individuales,
    calcular_metricas_globales
)


def test_calculo_errores_individuales():
    df_prueba = pd.DataFrame({
        "a_experimental": [1.0, 2.0, 3.0],
        "a_teorica": [1.2, 2.0, 2.5]
    })
    df_res = calcular_errores_individuales(df_prueba)
    
    # Error con signo
    np.testing.assert_allclose(df_res["error_con_signo"], [-0.2, 0.0, 0.5])
    # Error absoluto
    np.testing.assert_allclose(df_res["error_absoluto"], [0.2, 0.0, 0.5])
    # Error relativo porcentual: |0.2/1.2|*100, 0, |0.5/2.5|*100
    np.testing.assert_allclose(df_res["error_relativo_pct"], [(0.2/1.2)*100, 0.0, 20.0])


def test_manejo_seguro_division_cero_teorica():
    df_cero = pd.DataFrame({
        "a_experimental": [0.5],
        "a_teorica": [0.0]
    })
    df_res = calcular_errores_individuales(df_cero)
    assert np.isnan(df_res.loc[0, "error_relativo_pct"])
    assert df_res.loc[0, "error_con_signo"] == 0.5
    assert df_res.loc[0, "error_absoluto"] == 0.5


def test_metricas_globales_mae_rmse_bias():
    df_prueba = pd.DataFrame({
        "a_experimental": [1.0, 2.0, 3.0, 4.0],
        "a_teorica": [1.2, 1.8, 3.2, 3.8]
    })
    df_err = calcular_errores_individuales(df_prueba)
    glob = calcular_metricas_globales(df_err)
    
    # Diferencias: [-0.2, 0.2, -0.2, 0.2]
    # Absolutas:   [0.2, 0.2, 0.2, 0.2] -> MAE = 0.2
    # Cuadradas:   [0.04, 0.04, 0.04, 0.04] -> RMSE = 0.2
    # Media signo: (-0.2 + 0.2 - 0.2 + 0.2) / 4 = 0.0
    assert pytest.approx(glob["mae"], 0.001) == 0.2
    assert pytest.approx(glob["rmse"], 0.001) == 0.2
    assert pytest.approx(glob["error_medio_signo"], 0.001) == 0.0
