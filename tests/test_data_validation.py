"""
Pruebas Unitarias para Validación de Integridad de Datos (data_validation.py)
Utiliza datos sintéticos exclusivamente en memoria.
"""

import pytest
import numpy as np
import pandas as pd
from src.data_validation import validar_integridad_dataset


@pytest.fixture
def dataset_valido_en_memoria():
    data = {
        "Orden": [1, 2, 3, 4, 5, 6],
        "Tratamiento": ["A1B1", "A1B1", "A1B1", "A1B2", "A1B2", "A1B2"],
        "Replica": [1, 2, 3, 1, 2, 3],
        "m1": [0.15, 0.15, 0.15, 0.15, 0.15, 0.15],
        "m2": [0.02, 0.02, 0.02, 0.035, 0.035, 0.035],
        "vA": [0.5, 0.51, 0.49, 0.6, 0.61, 0.59],
        "vB": [1.1, 1.12, 1.09, 1.3, 1.32, 1.29],
        "t": [0.6, 0.61, 0.59, 0.5, 0.51, 0.49],
        "a_experimental": [1.0, 1.01, 0.99, 1.4, 1.41, 1.39],
        "a_teorica": [1.15, 1.15, 1.15, 1.85, 1.85, 1.85]
    }
    return pd.DataFrame(data)


def test_validacion_dataset_limpio(dataset_valido_en_memoria):
    df_val, resumen = validar_integridad_dataset(dataset_valido_en_memoria)
    assert resumen["observaciones_validas"] == 6
    assert resumen["registros_completamente_vacios"] == 0
    assert resumen["duplicados_reportados"] == 0
    assert resumen["estado_general"] == "APROBADO_CONFORME"
    assert resumen["diseno_balanceado"] is True


def test_deteccion_filas_vacias(dataset_valido_en_memoria):
    df_con_vacia = dataset_valido_en_memoria.copy()
    fila_vacia = pd.DataFrame([{col: np.nan for col in df_con_vacia.columns}])
    df_con_vacia = pd.concat([df_con_vacia, fila_vacia], ignore_index=True)
    
    df_val, resumen = validar_integridad_dataset(df_con_vacia)
    assert resumen["total_registros_inicial"] == 7
    assert resumen["registros_completamente_vacios"] == 1
    assert len(df_val) == 6


def test_deteccion_valores_no_numericos(dataset_valido_en_memoria):
    df_corrupto = dataset_valido_en_memoria.copy()
    df_corrupto["a_experimental"] = df_corrupto["a_experimental"].astype(object)
    df_corrupto.loc[0, "a_experimental"] = "NO_NUMERICO"
    
    df_val, resumen = validar_integridad_dataset(df_corrupto)
    assert "a_experimental" in resumen["errores_conversion_numerica"]
    assert resumen["estado_general"] == "APROBADO_CON_OBSERVACIONES"
