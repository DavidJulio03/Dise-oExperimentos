"""
Módulo de Utilidades Auxiliares Reutilizables
Incluye registro de ejecución (logger), formateo de Excel y cálculos estadísticos auxiliares.
"""

import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.config import LOG_FILE


class ExecutionLogger:
    """
    Registrador de eventos de ejecución para auditoría técnica y trazabilidad.
    Escribe tanto en consola como en el archivo de registro especificado.
    """
    def __init__(self, log_path: Path = LOG_FILE):
        self.log_path = log_path
        self.events: List[Dict[str, Any]] = []
        self.start_time = datetime.datetime.now()
        
    def log(self, level: str, message: str, procedure: Optional[str] = None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "timestamp": timestamp,
            "level": level.upper(),
            "procedure": procedure or "GENERAL",
            "message": message
        }
        self.events.append(record)
        
        # Formato de consola
        prefix = f"[{record['level']}]"
        if record["level"] == "INFO":
            print(f"  {prefix} {message}")
        elif record["level"] in ["WARNING", "WARN"]:
            print(f"  \033[93m{prefix} {message}\033[0m")
        elif record["level"] == "ERROR":
            print(f"  \033[91m{prefix} {message}\033[0m", file=sys.stderr)
        else:
            print(f"  {prefix} {message}")
            
    def info(self, message: str, procedure: Optional[str] = None):
        self.log("INFO", message, procedure)
        
    def warning(self, message: str, procedure: Optional[str] = None):
        self.log("WARNING", message, procedure)
        
    def error(self, message: str, procedure: Optional[str] = None):
        self.log("ERROR", message, procedure)
        
    def write_to_file(self, metadata: Optional[Dict[str, Any]] = None):
        end_time = datetime.datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("REGISTRO DE EJECUCIÓN DEL SISTEMA DE ANÁLISIS ESTADÍSTICO\n")
            f.write("="*80 + "\n")
            f.write(f"Fecha y hora de inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Fecha y hora de cierre: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duración total:         {duration:.2f} segundos\n")
            
            if metadata:
                f.write("\nMETADATOS DE ENTRADA Y AMBIENTE:\n")
                f.write("-" * 50 + "\n")
                for k, v in metadata.items():
                    f.write(f"- {k}: {v}\n")
                    
            f.write("\nEVENTOS Y PROCEDIMIENTOS REGISTRADOS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'FECHA/HORA':<20} {'NIVEL':<10} {'PROCEDIMIENTO':<25} {'MENSAJE'}\n")
            f.write("-" * 80 + "\n")
            for ev in self.events:
                f.write(f"{ev['timestamp']:<20} {ev['level']:<10} {ev['procedure']:<25} {ev['message']}\n")
            f.write("="*80 + "\n")


# Instancia global por defecto del logger
LOGGER = ExecutionLogger()


# --- FUNCIONES DE CÁLCULO ESTADÍSTICO AUXILIAR ---

def calcular_intervalo_confianza(datos: np.ndarray, alpha: float = 0.05) -> Tuple[float, float, float]:
    """
    Calcula la media y su intervalo de confianza al (1 - alpha) utilizando la distribución t de Student.
    Retorna (media, limite_inferior, limite_superior).
    """
    datos_limpios = np.asarray(datos)[~np.isnan(datos)]
    n = len(datos_limpios)
    if n == 0:
        return np.nan, np.nan, np.nan
    media = float(np.mean(datos_limpios))
    if n == 1:
        return media, media, media
        
    s = float(np.std(datos_limpios, ddof=1))
    se = s / np.sqrt(n)
    t_crit = float(stats.t.ppf(1 - alpha / 2, df=n - 1))
    margen = t_crit * se
    return media, media - margen, media + margen


def calcular_tamanos_efecto(ss_efecto: float, df_efecto: float, ss_error: float, ms_error: float, ss_total: float) -> Dict[str, float]:
    """
    Calcula medidas del tamaño del efecto:
    - eta_sq (Eta cuadrado total = SS_efecto / SS_total)
    - partial_eta_sq (Eta cuadrado parcial = SS_efecto / (SS_efecto + SS_error))
    - omega_sq (Omega cuadrado = (SS_efecto - df_efecto * MS_error) / (SS_total + MS_error))
    """
    eta_sq = ss_efecto / ss_total if ss_total > 0 else np.nan
    partial_eta_sq = ss_efecto / (ss_efecto + ss_error) if (ss_efecto + ss_error) > 0 else np.nan
    
    # Omega cuadrado
    numerador_omega = ss_efecto - (df_efecto * ms_error)
    denominador_omega = ss_total + ms_error
    omega_sq = (numerador_omega / denominador_omega) if denominador_omega > 0 else np.nan
    omega_sq = max(0.0, omega_sq) if not np.isnan(omega_sq) else np.nan
    
    return {
        "eta_cuadrado": float(eta_sq),
        "eta_cuadrado_parcial": float(partial_eta_sq),
        "omega_cuadrado": float(omega_sq)
    }


# --- UTILIDADES DE EXCEL OPENPYXL ---

def aplicar_estilo_tabla_excel(ws, fila_inicio: int = 1, titulo_hoja: Optional[str] = None):
    """
    Aplica diseño profesional de reporte técnico a una hoja de openpyxl:
    - Encabezados en azul marino con fuente blanca y negrita.
    - Líneas de división sutiles.
    - Filas alternas con sombreado tenue.
    - Alineación automática y anchos de columna adaptativos.
    """
    ws.views.sheetView[0].showGridLines = True
    
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10, bold=False, color="000000")
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9")
    )
    
    offset_encabezado = fila_inicio
    if titulo_hoja:
        max_col = ws.max_column or 1
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
        title_cell = ws.cell(row=1, column=1, value=titulo_hoja)
        title_cell.font = Font(name="Calibri", size=13, bold=True, color="1F497D")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28
        offset_encabezado = 3
        
    for row_idx, row in enumerate(ws.iter_rows(min_row=offset_encabezado), start=offset_encabezado):
        is_header = (row_idx == offset_encabezado)
        is_even = ((row_idx - offset_encabezado) % 2 == 0)
        
        ws.row_dimensions[row_idx].height = 24 if is_header else 20
        
        for col_idx, cell in enumerate(row, start=1):
            cell.border = thin_border
            if is_header:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            else:
                cell.font = data_font
                if not is_even:
                    cell.fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
                    
                # Formato y alineación según tipo
                if isinstance(cell.value, (int, np.integer)):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif isinstance(cell.value, (float, np.floating)):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    if abs(cell.value) < 1e-3 and cell.value != 0:
                        cell.number_format = "0.0000E+00"
                    else:
                        cell.number_format = "0.0000"
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    
    # Auto-ajuste de anchos de columna
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row < offset_encabezado:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
