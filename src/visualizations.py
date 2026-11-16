"""
Módulo de Generación de Visualizaciones Estadísticas Editoriales (300 DPI)
Genera todas las figuras descriptivas, de ANOVA, diagnóstico y comparación física
con estilo académico riguroso, etiquetas en español y sin unidades no confirmadas (Sección 11).
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.nonparametric.smoothers_lowess import lowess

from src.config import (
    PLOTS_DIR,
    PLOT_DPI,
    RESPONSE_VARIABLE,
    THEORETICAL_VARIABLE,
    TREATMENT_VARIABLE,
    ORDER_VARIABLE,
    QUANTITATIVE_VARIABLES
)
from src.utils import LOGGER


# Configuración de estética editorial y científica
plt.rcParams.update({
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.family": "sans-serif",
    "axes.edgecolor": "#2D3748",
    "axes.linewidth": 1.0,
    "grid.color": "#E2E8F0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.7,
    "xtick.color": "#2D3748",
    "ytick.color": "#2D3748",
    "figure.titlesize": 12,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9
})


def _guardar_figura(fig, nombre_archivo: str, dir_salida: Path) -> Path:
    ruta = dir_salida / nombre_archivo
    fig.savefig(ruta, dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)
    return ruta


# --- GRÁFICAS DESCRIPTIVAS ---

def graficar_01_histogramas_cuantitativas(df: pd.DataFrame, dir_salida: Path) -> Path:
    cols = [c for c in QUANTITATIVE_VARIABLES if c in df.columns]
    n_cols = len(cols)
    n_filas = int(np.ceil(n_cols / 3))
    
    fig, axes = plt.subplots(n_filas, 3, figsize=(14, 3.5 * n_filas), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    axes_flat = axes.flatten()
    
    for i, col in enumerate(cols):
        ax = axes_flat[i]
        datos = df[col].dropna()
        sns.histplot(datos, kde=True, ax=ax, color="#2B6CB0", edgecolor="#1A365D", bins=7, alpha=0.6)
        ax.set_title(f"Distribución de {col}", fontweight="bold")
        ax.set_xlabel(col, fontweight="bold")
        ax.set_ylabel("Frecuencia", fontweight="bold")
        ax.grid(True)
        
    for j in range(i + 1, len(axes_flat)):
        fig.delaxes(axes_flat[j])
        
    fig.suptitle("Histogramas y Curvas de Densidad de Variables Cuantitativas", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    return _guardar_figura(fig, "01_histogramas_variables_cuantitativas.png", dir_salida)


def graficar_02_distribucion_cinematica(df: pd.DataFrame, dir_salida: Path) -> Path:
    cols_cin = [c for c in ["vA", "vB", "t"] if c in df.columns]
    fig, axes = plt.subplots(1, len(cols_cin), figsize=(5 * len(cols_cin), 4.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    if len(cols_cin) == 1:
        axes = [axes]
        
    colores = ["#319795", "#805AD5", "#DD6B20"]
    for i, col in enumerate(cols_cin):
        ax = axes[i]
        sns.violinplot(data=df, y=col, ax=ax, color=colores[i % len(colores)], inner="quartile", alpha=0.7)
        sns.stripplot(data=df, y=col, ax=ax, color="#1A202C", size=5, jitter=0.2, alpha=0.8)
        ax.set_title(f"Distribución de {col}", fontweight="bold")
        ax.set_ylabel(col, fontweight="bold")
        ax.grid(True)
        
    fig.suptitle("Distribución de Velocidades en Fotocompuertas y Tiempo de Tránsito", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "02_distribucion_velocidades_y_tiempo.png", dir_salida)


def graficar_03_matriz_correlaciones(r_matrix: pd.DataFrame, dir_salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    mascara = np.triu(np.ones_like(r_matrix, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        r_matrix, mask=mascara, cmap=cmap, vmin=-1.0, vmax=1.0,
        annot=True, fmt=".2f", square=True, linewidths=0.8,
        cbar_kws={"shrink": 0.8, "label": "Coeficiente de Correlación de Pearson (r)"}, ax=ax
    )
    ax.set_title("Matriz de Correlaciones Lineales entre Variables Cuantitativas", fontweight="bold", pad=12)
    plt.tight_layout()
    return _guardar_figura(fig, "03_matriz_correlaciones.png", dir_salida)


def graficar_04_boxplot_variables_tratamiento(df: pd.DataFrame, dir_salida: Path) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    orden_trat = sorted(df[TREATMENT_VARIABLE].unique())
    sns.boxplot(data=df, x=TREATMENT_VARIABLE, y="t", order=orden_trat, ax=ax1, hue=TREATMENT_VARIABLE, palette="Blues_r", legend=False)
    ax1.set_title("Tiempo de Tránsito (t) por Tratamiento", fontweight="bold")
    ax1.set_xlabel("Tratamiento", fontweight="bold")
    ax1.set_ylabel("t", fontweight="bold")
    ax1.grid(True)
    
    sns.boxplot(data=df, x=TREATMENT_VARIABLE, y="vB", order=orden_trat, ax=ax2, hue=TREATMENT_VARIABLE, palette="Greens_r", legend=False)
    ax2.set_title("Velocidad en Fotocompuerta 2 (vB) por Tratamiento", fontweight="bold")
    ax2.set_xlabel("Tratamiento", fontweight="bold")
    ax2.set_ylabel("vB", fontweight="bold")
    ax2.grid(True)
    
    fig.suptitle("Dispersión de Mediciones Cinemáticas Agrupadas por Tratamiento", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "04_boxplot_variables_por_tratamiento.png", dir_salida)


def graficar_05_boxplot_aceleracion_tratamiento(df: pd.DataFrame, dir_salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    orden_trat = sorted(df[TREATMENT_VARIABLE].unique())
    sns.boxplot(
        data=df, x=TREATMENT_VARIABLE, y=RESPONSE_VARIABLE, order=orden_trat,
        ax=ax, color="#EBF3FB", boxprops=dict(edgecolor="#2B6CB0", alpha=0.8),
        medianprops=dict(color="#1A365D", linewidth=2), width=0.5, showfliers=False
    )
    sns.stripplot(
        data=df, x=TREATMENT_VARIABLE, y=RESPONSE_VARIABLE, order=orden_trat,
        ax=ax, color="#0052CC", size=7, jitter=0.18, alpha=0.85, label="Réplicas Experimentales"
    )
    
    # Superponer aceleración teórica
    teoricos = df.groupby(TREATMENT_VARIABLE)[THEORETICAL_VARIABLE].mean().reindex(orden_trat)
    ax.scatter(
        np.arange(len(orden_trat)), teoricos.values, color="#D9381E",
        marker="D", s=65, zorder=5, edgecolor="#7A190B", label="Valor Teórico (a_teorica)"
    )
    
    ax.set_title("Aceleración Experimental por Tratamiento (Réplicas Crudas) vs. Aceleración Teórica", fontweight="bold", pad=12)
    ax.set_xlabel("Tratamiento", fontweight="bold")
    ax.set_ylabel(RESPONSE_VARIABLE, fontweight="bold")
    ax.grid(True, axis="y")
    
    # Manejar leyenda sin duplicados
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handles[0], handles[-1]], ["Réplicas Crudas", "Valor Teórico"], loc="upper left", framealpha=0.9)
    plt.tight_layout()
    return _guardar_figura(fig, "05_boxplot_aceleracion_por_tratamiento.png", dir_salida)


# --- GRÁFICAS DE ANOVA Y POST-HOC ---

def graficar_06_medias_aceleracion_ic(df_desc_trat: pd.DataFrame, dir_salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    x = np.arange(len(df_desc_trat))
    y = df_desc_trat["media_a_exp"].values
    yerr_inf = y - df_desc_trat["ic_inf_95"].values
    yerr_sup = df_desc_trat["ic_sup_95"].values - y
    
    ax.errorbar(
        x, y, yerr=[yerr_inf, yerr_sup], fmt="o", color="#2B6CB0",
        ecolor="#4A5568", elinewidth=1.8, capsize=5, capthick=1.5,
        markersize=8, label="Media Experimental (IC 95%)"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(df_desc_trat["Tratamiento"], rotation=0)
    ax.set_title("Medias de Aceleración Experimental por Tratamiento con Intervalos de Confianza al 95%", fontweight="bold", pad=12)
    ax.set_xlabel("Tratamiento", fontweight="bold")
    ax.set_ylabel(RESPONSE_VARIABLE, fontweight="bold")
    ax.grid(True)
    ax.legend(loc="upper left", framealpha=0.9)
    plt.tight_layout()
    return _guardar_figura(fig, "06_medias_aceleracion_intervalos_confianza.png", dir_salida)


def graficar_07_efectos_principales(df: pd.DataFrame, meta_diseno: Dict[str, Any], dir_salida: Path) -> Optional[Path]:
    if meta_diseno["tipo_diseno"] != "FACTORIAL_DOS_VIAS":
        return None
    f_a, f_b = meta_diseno["factores"][:2]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    # Factor A
    med_a = df.groupby(f_a)[RESPONSE_VARIABLE].mean().reset_index()
    ax1.plot(med_a[f_a], med_a[RESPONSE_VARIABLE], marker="o", color="#2B6CB0", linewidth=2.2, markersize=8)
    ax1.set_title(f"Efecto Principal: {f_a}", fontweight="bold")
    ax1.set_xlabel(f_a, fontweight="bold")
    ax1.set_ylabel(f"Media de {RESPONSE_VARIABLE}", fontweight="bold")
    ax1.grid(True)
    
    # Factor B
    med_b = df.groupby(f_b)[RESPONSE_VARIABLE].mean().reset_index()
    ax2.plot(med_b[f_b], med_b[RESPONSE_VARIABLE], marker="s", color="#C53030", linewidth=2.2, markersize=8)
    ax2.set_title(f"Efecto Principal: {f_b}", fontweight="bold")
    ax2.set_xlabel(f_b, fontweight="bold")
    ax2.set_ylabel(f"Media de {RESPONSE_VARIABLE}", fontweight="bold")
    ax2.grid(True)
    
    fig.suptitle("Gráfica de Efectos Principales de los Factores Experimentales", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "07_efectos_principales_factores.png", dir_salida)


def graficar_08_interaccion_factores(df: pd.DataFrame, meta_diseno: Dict[str, Any], dir_salida: Path) -> Optional[Path]:
    if meta_diseno["tipo_diseno"] != "FACTORIAL_DOS_VIAS":
        return None
    f_a, f_b = meta_diseno["factores"][:2]
    
    resumen = df.groupby([f_a, f_b])[RESPONSE_VARIABLE].agg(["mean", "std", "count"]).reset_index()
    resumen["se"] = resumen["std"] / np.sqrt(resumen["count"])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    # Panel 1: X = Factor_A, Líneas = Factor_B
    niveles_b = sorted(df[f_b].unique())
    colores_b = sns.color_palette("viridis", n_colors=len(niveles_b))
    for i, nb in enumerate(niveles_b):
        sub = resumen[resumen[f_b] == nb].sort_values(f_a)
        ax1.errorbar(sub[f_a], sub["mean"], yerr=sub["se"], label=f"{f_b}={nb}", marker="o", color=colores_b[i], linewidth=2, capsize=4)
    ax1.set_title(f"Interacción: {f_a} condicionado por {f_b}", fontweight="bold")
    ax1.set_xlabel(f_a, fontweight="bold")
    ax1.set_ylabel(f"Media de {RESPONSE_VARIABLE} (±1 EE)", fontweight="bold")
    ax1.grid(True)
    ax1.legend(title=f_b, framealpha=0.9)
    
    # Panel 2: X = Factor_B, Líneas = Factor_A
    niveles_a = sorted(df[f_a].unique())
    colores_a = sns.color_palette("plasma", n_colors=len(niveles_a))
    for i, na in enumerate(niveles_a):
        sub = resumen[resumen[f_a] == na].sort_values(f_b)
        ax2.errorbar(sub[f_b], sub["mean"], yerr=sub["se"], label=f"{f_a}={na}", marker="s", color=colores_a[i], linewidth=2, capsize=4)
    ax2.set_title(f"Interacción: {f_b} condicionado por {f_a}", fontweight="bold")
    ax2.set_xlabel(f_b, fontweight="bold")
    ax2.set_ylabel(f"Media de {RESPONSE_VARIABLE} (±1 EE)", fontweight="bold")
    ax2.grid(True)
    ax2.legend(title=f_a, framealpha=0.9)
    
    fig.suptitle(f"Gráfica de Interacción Factorial ({f_a} × {f_b})", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "08_grafica_interaccion_factores.png", dir_salida)


def graficar_09_comparaciones_post_hoc(df_tukey: pd.DataFrame, dir_salida: Path) -> Optional[Path]:
    if df_tukey.empty:
        return None
    # Si hay muchas comparaciones (ej. 36 pares), tomar las primeras 15 o filtrar para legibilidad
    df_plot = df_tukey.head(20).copy() if len(df_tukey) > 20 else df_tukey.copy()
    
    fig, ax = plt.subplots(figsize=(10, max(5, len(df_plot) * 0.35)), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    y_pos = np.arange(len(df_plot))
    etiquetas = [f"{r['group1']} vs {r['group2']}" for _, r in df_plot.iterrows()]
    
    ax.axvline(0, color="#E53E3E", linestyle="--", linewidth=1.5, alpha=0.8)
    for i, (_, r) in enumerate(df_plot.iterrows()):
        color = "#2B6CB0" if r["reject"] else "#A0AEC0"
        ax.plot([r["lower"], r["upper"]], [i, i], color=color, linewidth=2)
        ax.plot(r["meandiff"], i, "o", color=color, markersize=6)
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(etiquetas)
    ax.set_title("Comparaciones Múltiples (Diferencia de Medias e Intervalos de Confianza)", fontweight="bold", pad=12)
    ax.set_xlabel("Diferencia de Medias", fontweight="bold")
    ax.grid(True, axis="x")
    plt.tight_layout()
    return _guardar_figura(fig, "09_comparaciones_post_hoc.png", dir_salida)


# --- GRÁFICAS DE DIAGNÓSTICO DEL MODELO ---

def graficar_10_diagnostico_qq_histograma(df_res: pd.DataFrame, meta_norm: Dict[str, Any], dir_salida: Path) -> Path:
    res = df_res["residuos_ordinarios"].dropna().values
    n = len(res)
    std_res = np.std(res, ddof=1)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    # Q-Q plot con banda
    osm, osr = stats.probplot(res, dist="norm")
    teo_q, obs_q = osm[0], osm[1]
    slope, intercept, r_val, _, _ = stats.linregress(teo_q, obs_q)
    linea = slope * teo_q + intercept
    
    se_banda = (slope / stats.norm.pdf(teo_q)) * np.sqrt(stats.norm.cdf(teo_q) * (1 - stats.norm.cdf(teo_q)) / n)
    ax1.fill_between(teo_q, linea - 1.96 * se_banda, linea + 1.96 * se_banda, color="#CCE5FF", alpha=0.5, label="Banda 95%")
    ax1.plot(teo_q, linea, color="#C53030", linestyle="--", linewidth=1.8, label=f"Recta Teórica (R²={r_val**2:.3f})")
    ax1.scatter(teo_q, obs_q, color="#2B6CB0", edgecolor="#1A365D", s=45, zorder=4, label="Residuos")
    ax1.set_title("Gráfico Q-Q Normal de Residuos", fontweight="bold")
    ax1.set_xlabel("Cuantiles Teóricos Normales", fontweight="bold")
    ax1.set_ylabel("Residuos Muestrales", fontweight="bold")
    ax1.grid(True)
    ax1.legend(loc="upper left", framealpha=0.9)
    
    # Histograma
    sns.histplot(res, kde=True, ax=ax2, stat="density", color="#3182CE", edgecolor="#1A365D", bins=7, alpha=0.5)
    x_lin = np.linspace(min(res) - 0.5 * std_res, max(res) + 0.5 * std_res, 200)
    ax2.plot(x_lin, stats.norm.pdf(x_lin, loc=np.mean(res), scale=std_res), color="#C53030", linestyle="--", linewidth=2, label="Densidad Teórica")
    
    cuadro_texto = (
        f"Shapiro-Wilk: W = {meta_norm.get('shapiro_w', 0):.4f}, p = {meta_norm.get('shapiro_p', 0):.4f}\n"
        f"Asimetría: {meta_norm.get('asimetria', 0):.3f} | Curtosis: {meta_norm.get('curtosis_exceso', 0):.3f}"
    )
    ax2.text(0.05, 0.95, cuadro_texto, transform=ax2.transAxes, fontsize=9, verticalalignment="top",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#F7FAFC", edgecolor="#CBD5E0", alpha=0.95))
    ax2.set_title("Histograma y Densidad de Residuos", fontweight="bold")
    ax2.set_xlabel("Residuo Ordinario", fontweight="bold")
    ax2.set_ylabel("Densidad", fontweight="bold")
    ax2.grid(True)
    ax2.legend(loc="upper right", framealpha=0.9)
    
    fig.suptitle("Diagnóstico del Supuesto de Normalidad de Residuos", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "10_diagnostico_residuos_qq_histograma.png", dir_salida)


def graficar_11_residuos_vs_ajustados_y_orden(df_res: pd.DataFrame, dir_salida: Path) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    y_fit = df_res["valores_ajustados"].values
    res = df_res["residuos_ordinarios"].values
    
    # Panel 1: Residuos vs Ajustados
    ax1.axhline(0, color="#E53E3E", linestyle="--", linewidth=1.5, alpha=0.8)
    ax1.scatter(y_fit, res, color="#2B6CB0", edgecolor="#1A365D", s=50, alpha=0.85)
    try:
        lowess_fit = lowess(res, y_fit, frac=0.66)
        ax1.plot(lowess_fit[:, 0], lowess_fit[:, 1], color="#DD6B20", linewidth=2.2, label="LOWESS")
    except Exception:
        pass
    ax1.set_title("Residuos vs. Valores Ajustados (Homocedasticidad)", fontweight="bold")
    ax1.set_xlabel("Valores Ajustados", fontweight="bold")
    ax1.set_ylabel("Residuos Ordinarios", fontweight="bold")
    ax1.grid(True)
    ax1.legend(loc="upper right", framealpha=0.9)
    
    # Panel 2: Residuos vs Orden
    if ORDER_VARIABLE in df_res.columns:
        df_ord = df_res.sort_values(by=ORDER_VARIABLE)
        ord_vals = df_ord[ORDER_VARIABLE].values
        res_ord = df_ord["residuos_ordinarios"].values
        ax2.axhline(0, color="#E53E3E", linestyle="--", linewidth=1.5, alpha=0.8)
        ax2.plot(ord_vals, res_ord, color="#CBD5E0", linestyle="-", linewidth=1.0)
        ax2.scatter(ord_vals, res_ord, color="#319795", edgecolor="#234E52", s=50, zorder=3)
        slope, intercept, r_val, p_val, _ = stats.linregress(ord_vals.astype(float), res_ord)
        ax2.plot(ord_vals, slope * ord_vals + intercept, color="#805AD5", linestyle="-.", linewidth=2, label=f"Tendencia (r={r_val:.2f}, p={p_val:.2f})")
        ax2.set_title("Residuos vs. Secuencia de Medición (Independencia)", fontweight="bold")
        ax2.set_xlabel("Orden de Ejecución", fontweight="bold")
        ax2.set_ylabel("Residuos Ordinarios", fontweight="bold")
        ax2.grid(True)
        ax2.legend(loc="upper right", framealpha=0.9)
        
    fig.suptitle("Diagnóstico de Homocedasticidad e Independencia Residual", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "11_residuos_vs_ajustados_y_orden.png", dir_salida)


def graficar_12_escala_localizacion(df_res: pd.DataFrame, dir_salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    y_fit = df_res["valores_ajustados"].values
    sqrt_std_res = np.sqrt(df_res["residuos_estudentizados"].abs().values)
    
    ax.scatter(y_fit, sqrt_std_res, color="#805AD5", edgecolor="#44337A", s=55, alpha=0.85)
    try:
        lowess_fit = lowess(sqrt_std_res, y_fit, frac=0.66)
        ax.plot(lowess_fit[:, 0], lowess_fit[:, 1], color="#DD6B20", linewidth=2.2, label="Tendencia LOWESS")
    except Exception:
        pass
    ax.set_title("Gráfica de Escala-Localización (Scale-Location Plot)", fontweight="bold", pad=12)
    ax.set_xlabel("Valores Ajustados", fontweight="bold")
    ax.set_ylabel("$\\sqrt{|\\text{Residuos Estudentizados}|}$", fontweight="bold")
    ax.grid(True)
    ax.legend(loc="upper right", framealpha=0.9)
    plt.tight_layout()
    return _guardar_figura(fig, "12_diagnostico_heterocedasticidad_escala.png", dir_salida)


# --- GRÁFICAS DE COMPARACIÓN FÍSICA Y TEÓRICA ---

def graficar_13_dispersion_exp_vs_teo(df: pd.DataFrame, dir_salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 6.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    a_teo = df[THEORETICAL_VARIABLE].values
    a_exp = df[RESPONSE_VARIABLE].values
    
    val_min = min(np.min(a_teo), np.min(a_exp)) * 0.92
    val_max = max(np.max(a_teo), np.max(a_exp)) * 1.06
    eje_id = np.linspace(val_min, val_max, 100)
    
    # Línea identidad y=x
    ax.plot(eje_id, eje_id, color="#2D3748", linestyle="--", linewidth=1.8, label="Identidad Ideal (y = x)")
    
    # Regresión ajustada
    reg = stats.linregress(a_teo, a_exp)
    y_fit = reg.slope * eje_id + reg.intercept
    ax.plot(eje_id, y_fit, color="#2B6CB0", linestyle="-", linewidth=2.2, label=f"Ajuste Empírico: y = {reg.slope:.3f}x + {reg.intercept:.4f} (R²={reg.rvalue**2:.4f})")
    
    # Puntos experimentales
    palette = sns.color_palette("tab10", n_colors=df[TREATMENT_VARIABLE].nunique())
    sns.scatterplot(data=df, x=THEORETICAL_VARIABLE, y=RESPONSE_VARIABLE, hue=TREATMENT_VARIABLE, palette=palette, s=65, ax=ax, edgecolor="#1A202C", zorder=4)
    
    ax.set_title("Aceleración Experimental vs. Aceleración Teórica", fontweight="bold", pad=12)
    ax.set_xlabel(THEORETICAL_VARIABLE, fontweight="bold")
    ax.set_ylabel(RESPONSE_VARIABLE, fontweight="bold")
    ax.set_xlim(val_min, val_max)
    ax.set_ylim(val_min, val_max)
    ax.grid(True)
    ax.legend(loc="lower right", framealpha=0.9, fontsize=8)
    plt.tight_layout()
    return _guardar_figura(fig, "13_dispersion_experimental_vs_teorica.png", dir_salida)


def graficar_14_bland_altman(df_err: pd.DataFrame, metricas_glob: Dict[str, Any], dir_salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    promedios = (df_err[RESPONSE_VARIABLE] + df_err[THEORETICAL_VARIABLE]) / 2.0
    dif = df_err["error_con_signo"]
    
    bias = metricas_glob["bland_altman_bias"]
    loa_inf = metricas_glob["bland_altman_loa_inferior"]
    loa_sup = metricas_glob["bland_altman_loa_superior"]
    
    ax.scatter(promedios, dif, color="#2B6CB0", edgecolor="#1A365D", s=60, alpha=0.85, zorder=3, label="Observaciones Emparejadas")
    ax.axhline(bias, color="#C53030", linestyle="-", linewidth=2.0, label=f"Sesgo Medio (Bias = {bias:.4f})")
    ax.axhline(loa_sup, color="#DD6B20", linestyle="--", linewidth=1.8, label=f"Límite Sup. (+1.96 DE = {loa_sup:.4f})")
    ax.axhline(loa_inf, color="#DD6B20", linestyle="--", linewidth=1.8, label=f"Límite Inf. (-1.96 DE = {loa_inf:.4f})")
    
    ax.set_title("Gráfica de Concordancia de Bland-Altman (a_experimental vs. a_teorica)", fontweight="bold", pad=12)
    ax.set_xlabel("Promedio de Aceleraciones (a_exp + a_teo) / 2", fontweight="bold")
    ax.set_ylabel("Diferencia (a_exp - a_teo)", fontweight="bold")
    ax.grid(True)
    ax.legend(loc="lower left", framealpha=0.9)
    plt.tight_layout()
    return _guardar_figura(fig, "14_grafica_bland_altman.png", dir_salida)


def graficar_15_errores_por_tratamiento(df_err: pd.DataFrame, dir_salida: Path) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    orden_trat = sorted(df_err[TREATMENT_VARIABLE].unique())
    
    sns.boxplot(data=df_err, x=TREATMENT_VARIABLE, y="error_con_signo", order=orden_trat, ax=ax1, hue=TREATMENT_VARIABLE, palette="Blues_r", legend=False)
    ax1.axhline(0, color="#E53E3E", linestyle="--", linewidth=1.5)
    ax1.set_title("Error con Signo (a_exp - a_teo) por Tratamiento", fontweight="bold")
    ax1.set_xlabel("Tratamiento", fontweight="bold")
    ax1.set_ylabel("Error con Signo", fontweight="bold")
    ax1.grid(True)
    
    sns.boxplot(data=df_err, x=TREATMENT_VARIABLE, y="error_absoluto", order=orden_trat, ax=ax2, hue=TREATMENT_VARIABLE, palette="Oranges_r", legend=False)
    ax2.set_title("Error Absoluto (|a_exp - a_teo|) por Tratamiento", fontweight="bold")
    ax2.set_xlabel("Tratamiento", fontweight="bold")
    ax2.set_ylabel("Error Absoluto", fontweight="bold")
    ax2.grid(True)
    
    fig.suptitle("Distribución de Errores Emparejados por Tratamiento", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "15_diferencias_y_errores_por_tratamiento.png", dir_salida)


def graficar_16_distribucion_errores(df_err: pd.DataFrame, dir_salida: Path) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=PLOT_DPI)
    fig.patch.set_facecolor("white")
    
    e_sig = df_err["error_con_signo"].dropna()
    sns.histplot(e_sig, kde=True, ax=ax1, color="#3182CE", edgecolor="#1A365D", bins=7, alpha=0.6)
    ax1.set_title("Distribución del Error con Signo", fontweight="bold")
    ax1.set_xlabel("a_exp - a_teo", fontweight="bold")
    ax1.set_ylabel("Frecuencia", fontweight="bold")
    ax1.grid(True)
    
    e_rel = df_err["error_relativo_pct"].dropna()
    sns.histplot(e_rel, kde=True, ax=ax2, color="#DD6B20", edgecolor="#7B341E", bins=7, alpha=0.6)
    ax2.set_title("Distribución del Error Relativo Porcentual (%)", fontweight="bold")
    ax2.set_xlabel("Error Relativo (%)", fontweight="bold")
    ax2.set_ylabel("Frecuencia", fontweight="bold")
    ax2.grid(True)
    
    fig.suptitle("Análisis Distribucional de Errores de Medición", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return _guardar_figura(fig, "16_distribucion_errores_aceleracion.png", dir_salida)


def generar_todas_las_graficas(
    df: pd.DataFrame,
    df_desc_trat: pd.DataFrame,
    r_matrix: pd.DataFrame,
    meta_diseno: Dict[str, Any],
    df_tukey: pd.DataFrame,
    df_res: pd.DataFrame,
    meta_norm: Dict[str, Any],
    df_err: pd.DataFrame,
    metricas_glob: Dict[str, Any],
    dir_salida: Path = PLOTS_DIR
) -> List[Path]:
    """
    Genera el catálogo completo de figuras científicas obligatorias a 300 DPI (Sección 11).
    """
    LOGGER.info("Iniciando generación de figuras científicas a 300 DPI...", procedure="GENERADOR_GRAFICAS")
    dir_salida.mkdir(parents=True, exist_ok=True)
    rutas_generadas = []
    
    # 1. Descriptivas
    rutas_generadas.append(graficar_01_histogramas_cuantitativas(df, dir_salida))
    rutas_generadas.append(graficar_02_distribucion_cinematica(df, dir_salida))
    rutas_generadas.append(graficar_03_matriz_correlaciones(r_matrix, dir_salida))
    rutas_generadas.append(graficar_04_boxplot_variables_tratamiento(df, dir_salida))
    rutas_generadas.append(graficar_05_boxplot_aceleracion_tratamiento(df, dir_salida))
    
    # 2. ANOVA y Post-Hoc
    rutas_generadas.append(graficar_06_medias_aceleracion_ic(df_desc_trat, dir_salida))
    f7 = graficar_07_efectos_principales(df, meta_diseno, dir_salida)
    if f7: rutas_generadas.append(f7)
    f8 = graficar_08_interaccion_factores(df, meta_diseno, dir_salida)
    if f8: rutas_generadas.append(f8)
    f9 = graficar_09_comparaciones_post_hoc(df_tukey, dir_salida)
    if f9: rutas_generadas.append(f9)
    
    # 3. Diagnóstico de Supuestos
    rutas_generadas.append(graficar_10_diagnostico_qq_histograma(df_res, meta_norm, dir_salida))
    rutas_generadas.append(graficar_11_residuos_vs_ajustados_y_orden(df_res, dir_salida))
    rutas_generadas.append(graficar_12_escala_localizacion(df_res, dir_salida))
    
    # 4. Comparación Física
    rutas_generadas.append(graficar_13_dispersion_exp_vs_teo(df, dir_salida))
    rutas_generadas.append(graficar_14_bland_altman(df_err, metricas_glob, dir_salida))
    rutas_generadas.append(graficar_15_errores_por_tratamiento(df_err, dir_salida))
    rutas_generadas.append(graficar_16_distribucion_errores(df_err, dir_salida))
    
    LOGGER.info(f"Se generaron exitosamente {len(rutas_generadas)} figuras de alta resolución.", procedure="GENERADOR_GRAFICAS")
    return rutas_generadas
