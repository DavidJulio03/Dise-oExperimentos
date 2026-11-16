"""
Pruebas Unitarias para Modelado ANOVA y Post-Hoc (factorial_anova.py, post_hoc.py)
Utiliza datos sintéticos exclusivamente en memoria.
"""

import pytest
import numpy as np
import pandas as pd
from src.factorial_anova import identificar_diseno_experimental, ajustar_modelo_anova
from src.utils import calcular_tamanos_efecto
from src.post_hoc import calcular_games_howell


def test_identificacion_patron_factorial():
    df_factorial = pd.DataFrame({
        "Tratamiento": ["A1B1", "A1B2", "A2B1", "A2B2"],
        "m1": [0.1, 0.1, 0.2, 0.2],
        "m2": [0.01, 0.02, 0.01, 0.02],
        "a_experimental": [1.0, 1.5, 0.8, 1.2]
    })
    df_mod, meta = identificar_diseno_experimental(df_factorial)
    assert meta["tipo_diseno"] == "FACTORIAL_DOS_VIAS"
    assert "Factor_A" in df_mod.columns
    assert "Factor_B" in df_mod.columns


def test_fallback_un_factor_cuando_no_hay_patron():
    df_no_patron = pd.DataFrame({
        "Tratamiento": ["Control", "Tratamiento_X", "Tratamiento_Y"],
        "a_experimental": [1.0, 1.5, 2.0]
    })
    df_mod, meta = identificar_diseno_experimental(df_no_patron)
    assert meta["tipo_diseno"] == "UN_FACTOR_TRATAMIENTOS"


def test_calculo_tamanos_efecto():
    # SS_efecto = 10, df = 2, SS_error = 20, MS_error = 2, SS_total = 30
    eff = calcular_tamanos_efecto(ss_efecto=10.0, df_efecto=2.0, ss_error=20.0, ms_error=2.0, ss_total=30.0)
    assert pytest.approx(eff["eta_cuadrado"], 0.001) == 10.0 / 30.0
    assert pytest.approx(eff["eta_cuadrado_parcial"], 0.001) == 10.0 / (10.0 + 20.0)
    # Omega cuadrado = (10 - 2*2) / (30 + 2) = 6 / 32 = 0.1875
    assert pytest.approx(eff["omega_cuadrado"], 0.001) == 6.0 / 32.0


def test_procedimiento_games_howell():
    grupos = np.array(["G1", "G1", "G1", "G2", "G2", "G2"])
    valores = np.array([10.0, 11.0, 10.5, 20.0, 21.0, 20.5])
    df_gh = calcular_games_howell(grupos, valores)
    assert len(df_gh) == 1
    assert bool(df_gh.iloc[0]["reject"]) is True  # Diferencia clara entre 10 y 20
