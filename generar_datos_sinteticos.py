"""
Utilidad: Generador de Datos Sintéticos para Calibración y Pruebas
Experimento: Diseño Factorial 3x3 en Riel de Aire con Masa Colgante
"""

import numpy as np
import pandas as pd
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


def generar_datos_prueba(ruta_salida: Path = None, seed: int = 42):
    """
    Genera el archivo Excel 'Datos Anova Factorial.xlsx' con:
    1. Hoja 'Datos': 27 observaciones experimentales crudas, 10 columnas limpias (vA, vB, t).
    2. Hoja 'Factores': Documentación formal de correspondencia entre 9 tratamientos y niveles Factor_A y Factor_B.
    3. Formato profesional: Encabezados en negrita, filtros automáticos y anchos adaptativos.
    """
    if ruta_salida is None:
        ruta_salida = Path(__file__).resolve().parent / "Datos Anova Factorial.xlsx"
        
    np.random.seed(seed)
    g = 9.80665

    # Factores:
    # m1: masa deslizador -> 0.150, 0.200, 0.250
    # m2: masa colgante   -> 0.020, 0.035, 0.050
    niveles_m1 = [0.150, 0.200, 0.250]
    niveles_m2 = [0.020, 0.035, 0.050]

    datos = []
    orden_aleatorio = np.random.permutation(27) + 1
    idx_orden = 0

    d_compuertas = 0.50  # 50 cm entre fotocompuertas
    x0 = 0.15           # distancia de salida antes de fotocompuerta A

    for i, m1 in enumerate(niveles_m1, 1):
        for j, m2 in enumerate(niveles_m2, 1):
            trat = f"A{i}B{j}"
            a_teo = (m2 * g) / (m1 + m2)
            
            # Efecto físico real de pérdidas (~3.5% fricción viscosa riel e inercia polea)
            a_base_real = a_teo * 0.965
            
            for rep in [1, 2, 3]:
                ord_i = int(orden_aleatorio[idx_orden])
                idx_orden += 1
                
                # Ruido experimental gaussiano pequeño
                ruido = np.random.normal(0, 0.005)
                a_exp = a_base_real + ruido
                
                # Cinemática entre fotocompuertas
                vA = np.sqrt(2 * a_exp * x0)
                vB = np.sqrt(2 * a_exp * (x0 + d_compuertas))
                t = (vB - vA) / a_exp
                
                # Discretización experimental
                vA_medida = round(float(vA), 4)
                vB_medida = round(float(vB), 4)
                t_medido = round(float(t), 4)
                a_exp_medida = round((vB_medida - vA_medida) / t_medido, 4)
                
                datos.append({
                    "Orden": ord_i,
                    "Tratamiento": trat,
                    "Replica": rep,
                    "m1": m1,
                    "m2": m2,
                    "vA": vA_medida,
                    "vB": vB_medida,
                    "t": t_medido,
                    "a_experimental": a_exp_medida,
                    "a_teorica": round(float(a_teo), 4)
                })

    df_datos = pd.DataFrame(datos)
    # Ordenar por Orden aleatorio para simular la secuencia de ejecución experimental real
    df_datos = df_datos.sort_values("Orden").reset_index(drop=True)

    # Tabla de correspondencia de Factores (Sección 3)
    df_factores = pd.DataFrame([
        {"Tratamiento": "A1B1", "Factor_A": "A1", "Factor_B": "B1"},
        {"Tratamiento": "A1B2", "Factor_A": "A1", "Factor_B": "B2"},
        {"Tratamiento": "A1B3", "Factor_A": "A1", "Factor_B": "B3"},
        {"Tratamiento": "A2B1", "Factor_A": "A2", "Factor_B": "B1"},
        {"Tratamiento": "A2B2", "Factor_A": "A2", "Factor_B": "B2"},
        {"Tratamiento": "A2B3", "Factor_A": "A2", "Factor_B": "B3"},
        {"Tratamiento": "A3B1", "Factor_A": "A3", "Factor_B": "B1"},
        {"Tratamiento": "A3B2", "Factor_A": "A3", "Factor_B": "B2"},
        {"Tratamiento": "A3B3", "Factor_A": "A3", "Factor_B": "B3"},
    ])

    # Creación del libro de Excel con openpyxl para formato profesional
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Eliminar hoja inicial vacía

    header_font = Font(name="Calibri", size=11, bold=True, color="000000")
    data_font = Font(name="Calibri", size=10, bold=False, color="000000")

    # --- 1. Hoja 'Datos' ---
    ws_datos = wb.create_sheet(title="Datos")
    ws_datos.views.sheetView[0].showGridLines = True

    # Encabezados
    headers_datos = list(df_datos.columns)
    ws_datos.append(headers_datos)
    ws_datos.row_dimensions[1].height = 22

    for col_idx in range(1, len(headers_datos) + 1):
        cell = ws_datos.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Filas de datos
    for r_idx, row in df_datos.iterrows():
        fila = [
            int(row["Orden"]),
            str(row["Tratamiento"]),
            int(row["Replica"]),
            float(row["m1"]),
            float(row["m2"]),
            float(row["vA"]),
            float(row["vB"]),
            float(row["t"]),
            float(row["a_experimental"]),
            float(row["a_teorica"])
        ]
        ws_datos.append(fila)
        curr_row = ws_datos.max_row
        ws_datos.row_dimensions[curr_row].height = 19
        for c_idx in range(1, len(fila) + 1):
            c_cell = ws_datos.cell(row=curr_row, column=c_idx)
            c_cell.font = data_font
            if c_idx in [1, 2, 3]:
                c_cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c_cell.alignment = Alignment(horizontal="right", vertical="center")
                c_cell.number_format = "0.0000"

    # Filtro automático en 'Datos'
    ws_datos.auto_filter.ref = ws_datos.dimensions

    # Autoajuste de ancho de columnas en 'Datos'
    for col in ws_datos.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_datos.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # --- 2. Hoja 'Factores' ---
    ws_factores = wb.create_sheet(title="Factores")
    ws_factores.views.sheetView[0].showGridLines = True

    headers_factores = list(df_factores.columns)
    ws_factores.append(headers_factores)
    ws_factores.row_dimensions[1].height = 22

    for col_idx in range(1, len(headers_factores) + 1):
        cell = ws_factores.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r_idx, row in df_factores.iterrows():
        fila = [str(row["Tratamiento"]), str(row["Factor_A"]), str(row["Factor_B"])]
        ws_factores.append(fila)
        curr_row = ws_factores.max_row
        ws_factores.row_dimensions[curr_row].height = 19
        for c_idx in range(1, len(fila) + 1):
            c_cell = ws_factores.cell(row=curr_row, column=c_idx)
            c_cell.font = data_font
            c_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Filtro automático en 'Factores'
    ws_factores.auto_filter.ref = ws_factores.dimensions

    # Autoajuste de ancho de columnas en 'Factores'
    for col in ws_factores.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_factores.column_dimensions[col_letter].width = max(max_len + 5, 14)

    wb.save(ruta_salida)
    print(f"✓ Archivo Excel generado exitosamente: '{ruta_salida.name}' con hojas 'Datos' (27 filas) y 'Factores' (9 filas).")


if __name__ == "__main__":
    generar_datos_prueba()
