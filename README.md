# Sistema de Análisis Estadístico para Experimento de Dinámica: ANOVA Factorial

Sistema integral, modular y reproducible desarrollado en Python para el procesamiento, validación de integridad, modelado estadístico inferencial (ANOVA factorial y de un factor), diagnóstico de supuestos, análisis de concordancia física y visualización científica de datos experimentales.

El proyecto está diseñado bajo principios rigurosos de **Diseño de Experimentos (DoE)** y **Metodología Científica**, alimentándose de forma estricta de una única fuente de datos:

```text
Datos Anova Factorial.xlsx
```

---

## 1. Introducción

### 1.1. Propósito y Objetivo General
El objetivo fundamental de este sistema es evaluar la influencia de factores experimentales controlados sobre la aceleración del sistema físico, determinando:
1. Si existen diferencias estadísticamente significativas entre tratamientos.
2. Si la variación de la aceleración responde a efectos principales independientes o a interacciones no aditivas entre factores.
3. El grado de concordancia y desviación sistemática entre la **aceleración experimental observada** ($a_{\text{experimental}}$) y la **aceleración predicha por el modelo teórico ideal** ($a_{\text{teorica}}$).

### 1.2. Problema Estadístico y Físico
En experimentos de laboratorio (como el deslizador en riel de aire con masa colgante), la aceleración suele modelarse teóricamente despreciando fuerzas disipativas y momentos de inercia:

$$a_{\text{teorica}} = \frac{m_2 \, g}{m_1 + m_2}$$

Sin embargo, en condiciones reales operan fuerzas de rozamiento viscoso con el flujo de aire ($f_k$) y resistencia inercial rotacional en la polea ($I_{\text{polea}}$):

$$a_{\text{real}} = \frac{m_2 \, g - f_k}{m_1 + m_2 + \frac{I_{\text{polea}}}{R^2}} < a_{\text{teorica}}$$

El sistema implementa los contrastes estadísticos necesarios para cuantificar este déficit con rigor empírico y validar si los supuestos matemáticos del modelo lineal se satisfacen a cabalidad.

---

## 2. Estructura del Repositorio

El proyecto implementa la arquitectura modular especificada en la Sección 5:

```text
Proyecto_ANOVA/
│
├── Datos Anova Factorial.xlsx       # Fuente única de datos experimentales (solo lectura)
├── requirements.txt                 # Dependencias exactas verificadas
├── README.md                        # Documentación técnica, metodológica y operativa
├── main.py                          # Envoltura directa para ejecución en raíz
│
├── src/                             # Código fuente modular del sistema
│   ├── __init__.py                  # Exposición de funciones principales del paquete
│   ├── main.py                      # Orquestador principal (python -m src.main)
│   ├── config.py                    # Parámetros configurables, rutas y mapeo de factores
│   ├── data_loader.py               # Ingesta determinista, selección de hoja y normalización
│   ├── data_validation.py           # Protocolo de 10 puntos de auditoría y control de calidad
│   ├── descriptive_statistics.py    # Estadísticas univariadas, por tratamiento y correlaciones
│   ├── assumption_tests.py          # Verificación de normalidad, homocedasticidad y atípicos
│   ├── factorial_anova.py           # Clasificación de diseño, modelos OLS y tablas Tipo III
│   ├── post_hoc.py                  # Tukey HSD y Games-Howell condicionales
│   ├── theoretical_comparison.py    # Errores emparejados, pruebas t/Wilcoxon y Bland-Altman
│   ├── visualizations.py            # Catálogo de 16 figuras científicas a 300 DPI
│   ├── reporting.py                 # Exportación de 3 libros Excel e informe Markdown
│   └── utils.py                     # Logger de ejecución, estilos openpyxl y auxiliares
│
├── graficas/                        # Salida exclusiva de figuras en alta resolución (300 DPI)
│   ├── 01_histogramas_variables_cuantitativas.png
│   ├── 02_distribucion_velocidades_y_tiempo.png
│   ├── 03_matriz_correlaciones.png
│   ├── 04_boxplot_variables_por_tratamiento.png
│   ├── 05_boxplot_aceleracion_por_tratamiento.png
│   ├── 06_medias_aceleracion_intervalos_confianza.png
│   ├── 07_efectos_principales_factores.png
│   ├── 08_grafica_interaccion_factores.png
│   ├── 09_comparaciones_post_hoc.png
│   ├── 10_diagnostico_residuos_qq_histograma.png
│   ├── 11_residuos_vs_ajustados_y_orden.png
│   ├── 12_diagnostico_heterocedasticidad_escala.png
│   ├── 13_dispersion_experimental_vs_teorica.png
│   ├── 14_grafica_bland_altman.png
│   ├── 15_diferencias_y_errores_por_tratamiento.png
│   └── 16_distribucion_errores_aceleracion.png
│
├── resultados_estadisticos/         # Salida de libros de cálculo, informes y registros
│   ├── resumen_descriptivo.xlsx     # 5 hojas de estadísticas descriptivas y validación
│   ├── resultados_anova.xlsx        # 7 hojas con modelos, tablas Tipo III y supuestos
│   ├── comparacion_aceleraciones.xlsx # 3 hojas con errores emparejados y Bland-Altman
│   ├── informe_estadistico.md       # Informe científico estructurado en 11 secciones
│   └── registro_ejecucion.log       # Bitácora cronológica de auditoría técnica
│
└── tests/                           # Suite de pruebas unitarias automatizadas (pytest)
    ├── __init__.py
    ├── test_data_loader.py          # Pruebas de mapeo y normalización de columnas
    ├── test_data_validation.py      # Pruebas de integridad y detección de fallos
    ├── test_descriptive_statistics.py # Pruebas de métricas univariadas e intervalos
    ├── test_factorial_anova.py      # Pruebas de lógica factorial y tamaños de efecto
    └── test_theoretical_comparison.py # Pruebas de errores y pruebas emparejadas
```

---

## 3. Fuente de Datos y Naturaleza de las Variables

### 3.1. Restricciones y Principios de Integridad
- **Solo lectura:** El archivo `Datos Anova Factorial.xlsx` no es modificado, sobrescrito ni alterado en ninguna circunstancia.
- **Sin datos ficticios:** No se imputan valores faltantes mediante interpolación ni se crean datos artificiales en el análisis real.
- **Sin promediado previo:** El ANOVA se ejecuta sobre las **27 observaciones crudas individuales**, preservando la varianza residual intrínseca y los 18 grados de libertad del error experimental ($3 \times 3 \times (3 - 1) = 18$).

### 3.2. Orden Canónico de Columnas

| Posición | Nombre Canónico | Tipo Experimental | Descripción Funcional |
|---|---|---|---|
| 1 | `Orden` | Categórica / Secuencia | Identificador del orden aleatorizado de corrida en laboratorio (1 a 27). |
| 2 | `Tratamiento` | Categórica | Código del tratamiento o combinación experimental (ej. `A1B1` a `A3B3`). |
| 3 | `Replica` | Categórica / Entero | Identificador de la repetición dentro del tratamiento (1, 2 o 3). |
| 4 | `m1` | Cuantitativa | Variable cuantitativa asociada al primer cuerpo (deslizador). |
| 5 | `m2` | Cuantitativa | Variable cuantitativa asociada al segundo cuerpo (masa colgante). |
| 6 | `vA` | Cuantitativa | Velocidad instantánea en la fotocompuerta 1. |
| 7 | `vB` | Cuantitativa | Velocidad instantánea en la fotocompuerta 2. |
| 8 | `t` | Cuantitativa | Intervalo temporal de tránsito entre fotocompuertas. |
| 9 | `a_experimental` | Cuantitativa (Respuesta) | Variable respuesta principal de aceleración medida. |
| 10 | `a_teorica` | Cuantitativa (Referencia) | Aceleración teórica calculada por modelo ideal. |

### 3.3. Unidades de Medida (Restricción Estricta)
Conforme a la Sección 3.3 de las directrices metodológicas, **no se asumen ni inventan unidades de medida** que no estén confirmadas explícitamente en el archivo. Las etiquetas de tablas y figuras presentan los nombres de las variables de forma neutra y rigurosa (ej. `a_experimental`, `m1`, `m2`, `t`), documentando esta limitación técnica.

---

## 4. Fundamentos Estadísticos y Ecuaciones

### 4.1. ANOVA de Un Factor (Protocolo de Fallback)
Cuando no es posible descomponer inequívocamente la columna `Tratamiento` en múltiples factores ortogonales:

$$Y_{ij} = \mu + \alpha_i + \varepsilon_{ij}$$

- Hipótesis nula: $H_0: \mu_1 = \mu_2 = \dots = \mu_k$
- Hipótesis alterna: $H_1: \text{Al menos una media difiere}$

### 4.2. ANOVA Factorial de Dos Factores con Interacción
Cuando se identifica una estructura factorial ortogonal ($a$ niveles del Factor A y $b$ niveles del Factor B):

$$Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \varepsilon_{ijk}$$

Donde:
- $\mu$: Media global de la aceleración.
- $\alpha_i$: Efecto principal del nivel $i$ del Factor A.
- $\beta_j$: Efecto principal del nivel $j$ del Factor B.
- $(\alpha\beta)_{ij}$: Efecto de interacción entre factores.
- $\varepsilon_{ijk} \sim \mathcal{N}(0, \sigma^2)$: Error experimental aleatorio.

### 4.3. Tamaños del Efecto
El sistema calcula tres métricas complementarias del tamaño del efecto:

1. **Eta cuadrado total ($\eta^2$):**
   $$\eta^2 = \frac{SS_{\text{efecto}}}{SS_{\text{total}}}$$

2. **Eta cuadrado parcial ($\eta_p^2$):**
   $$\eta_p^2 = \frac{SS_{\text{efecto}}}{SS_{\text{efecto}} + SS_{\text{error}}}$$

3. **Omega cuadrado ($\omega^2$) (estimador insesgado de población):**
   $$\omega^2 = \frac{SS_{\text{efecto}} - df_{\text{efecto}} \cdot MS_{\text{error}}}{SS_{\text{total}} + MS_{\text{error}}}$$

*Criterios de magnitud de Cohen:* Pequeño ($\ge 0.01$), Mediano ($\ge 0.06$), Grande ($\ge 0.14$).

### 4.4. Supuestos Fundamentales
1. **Normalidad de residuos:** Contrastada mediante la prueba de Shapiro-Wilk:
   $$W = \frac{\left(\sum a_i x_{(i)}\right)^2}{\sum (x_i - \bar{x})^2}$$
2. **Homocedasticidad:** Evaluada con la prueba de Levene centrada en la mediana (Brown-Forsythe), calculando $F$ sobre las desviaciones absolutas $|e_{ij} - \tilde{e}_i|$.
3. **Independencia temporal:** Diagnosticada mediante el estadístico de Durbin-Watson sobre el orden de ejecución:
   $$d = \frac{\sum_{t=2}^N (e_t - e_{t-1})^2}{\sum_{t=1}^N e_t^2}$$

### 4.5. Comparación Emparejada y Medidas de Error
Para cada observación $i = 1, \dots, N$:
- **Error con signo:** $E_i = a_{\text{experimental},i} - a_{\text{teorica},i}$
- **Error absoluto:** $E_{\text{abs},i} = |a_{\text{experimental},i} - a_{\text{teorica},i}|$
- **Error relativo porcentual:** $E_{\text{rel},i} = \frac{|a_{\text{experimental},i} - a_{\text{teorica},i}|}{|a_{\text{teorica},i}|} \times 100$

Métricas agregadas:
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |E_i|, \quad \text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N E_i^2}, \quad \text{Bias} = \bar{E}$$

Pruebas de concordancia:
- Prueba $t$ de Student emparejada (si las diferencias son normales).
- Prueba de rangos con signo de Wilcoxon (alternativa no paramétrica).
- Límites de concordancia de Bland-Altman: $\bar{d} \pm 1.96 \, s_d$.

---

## 5. Funcionamiento de los Módulos (`src/`)

- **`config.py`:** Almacena rutas relativas (`pathlib.Path`), nombres canónicos, diccionario configurable `FACTOR_MAP` y parámetros globales ($\alpha = 0.05$).
- **`data_loader.py`:** Identifica automáticamente la hoja adecuada del Excel, normaliza encabezados (resolviendo paréntesis faltantes como `t (tiempo entre fotocompuertas` o espacios) y rechaza cargas ambiguas.
- **`data_validation.py`:** Valida tipos cuantitativos, descarta filas completamente vacías, reporta duplicados y valores atípicos sin eliminarlos arbitrariamente, y resume la estructura de tratamientos y réplicas.
- **`descriptive_statistics.py`:** Computa estadísticas univariadas completas, medias con intervalos de confianza al 95% para `a_experimental` y matrices de correlación (Pearson y Spearman), excluyendo estrictamente `Orden` y `Replica`.
- **`factorial_anova.py`:** Aplica la lógica de decisión metodológica: clasifica si el diseño es factorial o de un factor, ajusta el modelo lineal OLS con sumas de cuadrados Tipo III y calcula $\eta_p^2$ y $\omega^2$.
- **`post_hoc.py`:** Aplica comparaciones múltiples con control de tasa de error familiar (FWER): si la interacción es significativa compara celdas combinadas; si no, compara únicamente los factores principales significativos con Tukey HSD o Games-Howell.
- **`assumption_tests.py`:** Extrae residuos estandarizados y estudentizados; ejecuta Shapiro-Wilk, Levene (Brown-Forsythe), Bartlett, Durbin-Watson y diagnóstico de atípicos con regla IQR y residuos studentizados.
- **`theoretical_comparison.py`:** Computa errores individuales, MAE, RMSE, sesgo, prueba $t$ emparejada, test de Wilcoxon y análisis de Bland-Altman (global y por tratamiento).
- **`visualizations.py`:** Genera las 16 figuras en alta resolución (300 DPI) empleando backend `Agg` de Matplotlib y Seaborn con diseño editorial.
- **`reporting.py`:** Construye los 3 libros de Excel con formato profesional en `openpyxl` y redacta el informe científico estructurado en Markdown (`informe_estadistico.md`).
- **`utils.py`:** Gestiona el registro de auditoría (`ExecutionLogger`), utilidades de estilo para celdas y cálculo de tamaños del efecto.

---

## 6. Instalación y Requisitos

### 6.1. Requisitos del Sistema
- Python 3.10, 3.11 o 3.12 (64-bit).

### 6.2. Creación del Entorno Virtual e Instalación

En Windows (PowerShell):
```powershell
# Crear el entorno virtual
py -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias exactas
pip install -r requirements.txt
```

En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 7. Ejecución del Proyecto

El proyecto puede ejecutarse mediante cualquiera de los siguientes comandos desde la raíz del repositorio:

```bash
# Comando formal estándar especificado:
python -m src.main

# O mediante el script envoltura en la raíz:
python main.py
```

### Flujo de Ejecución Automatizado (12 Fases):
1. Carga del archivo Excel `Datos Anova Factorial.xlsx`.
2. Validación de estructura, completitud e integridad de tipos.
3. Normalización determinista de encabezados a nombres canónicos.
4. Identificación del diseño experimental (Factorial vs. Un Factor).
5. Cálculo de estadísticas descriptivas e intervalos de confianza.
6. Ajuste del modelo lineal ANOVA (Tipo III) y tamaños de efecto.
7. Diagnóstico de supuestos (Shapiro-Wilk, Levene, Durbin-Watson).
8. Comparaciones múltiples post-hoc condicionales (Tukey HSD / Games-Howell).
9. Comparación emparejada de aceleración experimental vs. teórica.
10. Generación de las 16 figuras científicas a 300 DPI en `graficas/`.
11. Exportación de 3 libros formateados en `resultados_estadisticos/`.
12. Redacción del informe estructurado `informe_estadistico.md` y cierre de log.

---

## 8. Guía de Interpretación de Salidas

### 8.1. Parámetros del ANOVA
- **Valor $p < 0.05$:** Evidencia estadísticamente significativa de efecto atribuible al factor o interacción.
- **Interacción significativa ($p < 0.05$):** Los efectos principales no deben interpretarse de manera aislada; el efecto de una masa sobre la aceleración depende del nivel en que se encuentre la otra masa.
- **$\eta_p^2$ y $\omega^2$:** Cuantifican la proporción de varianza explicada. Valores superiores a 0.14 denotan efectos de gran trascendencia experimental.

### 8.2. Diagnóstico de Supuestos y Protocolo ante Incumplimientos
- **Normalidad ($p_{\text{Shapiro}} \ge 0.05$):** Los errores se distribuyen normalmente. Si $p < 0.05$, el ANOVA mantiene robustez al ser un diseño balanceado ($n=3$ por celda); no obstante, se aconseja verificar transformaciones Box-Cox o análisis bootstrap.
- **Homocedasticidad ($p_{\text{Levene}} \ge 0.05$):** Varianzas residuales homogéneas. Si se incumple, se reporta y se evalúa Games-Howell o modelos ponderados (WLS).
- **Independencia ($1.5 \le d \le 2.5$):** Ausencia de autocorrelación de primer orden entre mediciones secuenciales. Valores fuera de este rango alertan de posibles derivas térmicas o pérdidas de presión en el riel de aire.

### 8.3. Comparación Física: Experimental vs. Teórica
- **Sesgo negativo ($\text{Bias} < 0$):** La aceleración experimental observada es sistemáticamente menor a la teórica ideal ($a_{\text{exp}} < a_{\text{teo}}$), lo cual es físicamente coherente con el frenado por arrastre viscoso en el colchón de aire y la inercia rotacional de la polea.
- **Bland-Altman:** Límites de concordancia ($\bar{d} \pm 1.96 s_d$) que engloban el 95% o más de las observaciones ratifican la reproducibilidad y estabilidad de las mediciones de laboratorio.

---

## 9. Catálogo de Entregables Generados

### 9.1. Libros de Cálculo (`resultados_estadisticos/`)
- **`resumen_descriptivo.xlsx`:** Hojas `Descriptiva_General`, `Descriptiva_Tratamientos`, `Resumen_Replicas`, `Validacion_Datos`, `Aceleraciones_y_Errores`.
- **`resultados_anova.xlsx`:** Hojas `Modelo_Utilizado`, `Tabla_ANOVA`, `Hipotesis_Evaluadas`, `Valores_F_p_gl_sc_cm`, `Tamanos_Efecto`, `Comparaciones_Multiples`, `Diagnostico_Supuestos`.
- **`comparacion_aceleraciones.xlsx`:** Hojas `Valores_Individuales`, `Metricas_Globales`, `Resumen_Por_Tratamiento`.

### 9.2. Informes y Logs (`resultados_estadisticos/`)
- **`informe_estadistico.md`:** Documento científico con las 11 secciones estructuradas, tablas en formato Markdown e interpretación física y estadística.
- **`registro_ejecucion.log`:** Archivo cronológico con trazabilidad de cada fase ejecutada.

### 9.3. Figuras Editoriales (`graficas/`, 300 DPI)
- `01_histogramas_variables_cuantitativas.png`
- `02_distribucion_velocidades_y_tiempo.png`
- `03_matriz_correlaciones.png`
- `04_boxplot_variables_por_tratamiento.png`
- `05_boxplot_aceleracion_por_tratamiento.png`
- `06_medias_aceleracion_intervalos_confianza.png`
- `07_efectos_principales_factores.png`
- `08_grafica_interaccion_factores.png`
- `09_comparaciones_post_hoc.png`
- `10_diagnostico_residuos_qq_histograma.png`
- `11_residuos_vs_ajustados_y_orden.png`
- `12_diagnostico_heterocedasticidad_escala.png`
- `13_dispersion_experimental_vs_teorica.png`
- `14_grafica_bland_altman.png`
- `15_diferencias_y_errores_por_tratamiento.png`
- `16_distribucion_errores_aceleracion.png`

---

## 10. Pruebas Unitarias Automatizadas

El proyecto incluye 17 pruebas unitarias desarrolladas en `pytest` que validan el comportamiento matemático y la lógica de negocio sin tocar el archivo Excel original:

```bash
pytest -v
```

Todas las pruebas se ejecutan sobre datos sintéticos en memoria y validan normalización, manejo de errores de conversión, cálculo de IQR/CV, intervalos de confianza, contrastes de hipótesis, lógica factorial y métricas de Bland-Altman.
