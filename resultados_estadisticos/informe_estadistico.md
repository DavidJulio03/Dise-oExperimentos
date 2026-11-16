# INFORME ESTADÍSTICO Y METODOLÓGICO EXPERIMENTAL

**Proyecto:** Sistema de Análisis Estadístico para Experimento de Dinámica (ANOVA Factorial)

**Variable Respuesta Principal:** `a_experimental`

---

## 1. Descripción del Conjunto de Datos

- **Fuente única de datos:** Archivo `Datos Anova Factorial.xlsx` en la raíz del proyecto.
- **Observaciones registradas:** 27 filas.
- **Observaciones válidas para modelado:** 27.
- **Tratamientos identificados:** 9 celdas experimentales (A1B2, A2B1, A2B2, A2B3, A3B3, A3B2, A1B1, A1B3, A3B1).
- **Estructura de réplicas:** 3 réplicas por tratamiento. Diseño balanceado: True.
- **Variables registradas:** 10 columnas en orden canónico (`Orden`, `Tratamiento`, `Replica`, `m1`, `m2`, `vA`, `vB`, `t`, `a_experimental`, `a_teorica`).

## 2. Resultados de la Validación de Integridad

- **Estado general de auditoría:** `APROBADO_CONFORME`.
- **Registros vacíos descartados:** 0.
- **Filas duplicadas detectadas:** 0.
- **Integridad:** Ausencia total de celdas vacías (`NaN`) o valores no numéricos en variables cuantitativas.

## 3. Estadística Descriptiva

### Tabla General de Variables Cuantitativas

| variable | n | media | mediana | std | varianza | min | max | q1 | q3 | iqr | cv_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m1 | 27 | 0.2000 | 0.2000 | 0.0416 | 0.0017 | 0.1500 | 0.2500 | 0.1500 | 0.2500 | 0.1000 | 20.8013 |
| m2 | 27 | 0.0350 | 0.0350 | 0.0125 | 1.5577e-04 | 0.0200 | 0.0500 | 0.0200 | 0.0500 | 0.0300 | 35.6593 |
| vA | 27 | 0.6447 | 0.6504 | 0.1182 | 0.0140 | 0.4580 | 0.8428 | 0.5762 | 0.7336 | 0.1573 | 18.3293 |
| vB | 27 | 1.3421 | 1.3538 | 0.2460 | 0.0605 | 0.9534 | 1.7545 | 1.1994 | 1.5271 | 0.3277 | 18.3305 |
| t | 27 | 0.5206 | 0.4989 | 0.0997 | 0.0099 | 0.3850 | 0.7085 | 0.4424 | 0.5632 | 0.1208 | 19.1498 |
| a_experimental | 27 | 1.4304 | 1.4099 | 0.5115 | 0.2616 | 0.6992 | 2.3681 | 1.1065 | 1.7936 | 0.6871 | 35.7612 |
| a_teorica | 27 | 1.4821 | 1.4606 | 0.5303 | 0.2813 | 0.7264 | 2.4517 | 1.1537 | 1.8553 | 0.7016 | 35.7823 |

### Resumen de Aceleración Experimental por Tratamiento (con IC 95%)

| Tratamiento | m1 | m2 | n | media_a_exp | std_a_exp | se_a_exp | ic_inf_95 | ic_sup_95 | a_teorica |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1B1 | 0.1500 | 0.0200 | 3 | 1.1099 | 0.0080 | 0.0046 | 1.0900 | 1.1297 | 1.1537 |
| A1B2 | 0.1500 | 0.0350 | 3 | 1.7901 | 0.0074 | 0.0043 | 1.7718 | 1.8084 | 1.8553 |
| A1B3 | 0.1500 | 0.0500 | 3 | 2.3672 | 0.0013 | 7.2188e-04 | 2.3641 | 2.3703 | 2.4517 |
| A2B1 | 0.2000 | 0.0200 | 3 | 0.8611 | 0.0029 | 0.0017 | 0.8539 | 0.8684 | 0.8915 |
| A2B2 | 0.2000 | 0.0350 | 3 | 1.4105 | 0.0022 | 0.0012 | 1.4051 | 1.4159 | 1.4606 |
| A2B3 | 0.2000 | 0.0500 | 3 | 1.8899 | 0.0021 | 0.0012 | 1.8847 | 1.8951 | 1.9613 |
| A3B1 | 0.2500 | 0.0200 | 3 | 0.7046 | 0.0049 | 0.0028 | 0.6924 | 0.7168 | 0.7264 |
| A3B2 | 0.2500 | 0.0350 | 3 | 1.1602 | 0.0040 | 0.0023 | 1.1503 | 1.1701 | 1.2043 |
| A3B3 | 0.2500 | 0.0500 | 3 | 1.5796 | 0.0051 | 0.0029 | 1.5670 | 1.5923 | 1.6344 |

## 4. Identificación del Diseño Experimental

- **Tipo de diseño clasificado:** `FACTORIAL_DOS_VIAS`.
- **Fundamento metodológico:** Codificación factorial ortogonal inequívoca AiBj en la columna Tratamiento. Validación con masas: Factor_A corresponde estrictamente a m1 (True) y Factor_B a m2 (True).
- **Factores definidos:** Factor_A, Factor_B.

## 5. Análisis de Varianza (ANOVA)

- **Ecuación ajustada:** `a_experimental ~ C(Factor_A) + C(Factor_B) + C(Factor_A):C(Factor_B)`
- **Bondad de ajuste:** $R^2 = 0.99994$ | $R^2_{\text{adj}} = 0.99991$
- **Prueba F Global del Modelo:** $F = 37693.3774$ ($p = 2.11532e-36$)

### Tabla ANOVA (Tipo III)

| index | sum_sq | df | mean_sq | F | PR(>F) | eta_sq_parcial | omega_sq |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Intercept | 3.6954 | 1.0000 | 3.6954 | 163817.1728 | 4.3260e-37 | nan | nan |
| C(Factor_A) | 0.2506 | 2.0000 | 0.1253 | 5554.8005 | 7.5830e-26 | 0.9984 | 0.0389 |
| C(Factor_B) | 2.3768 | 2.0000 | 1.1884 | 52680.9912 | 1.2377e-34 | 0.9998 | 0.3693 |
| C(Factor_A):C(Factor_B) | 0.1122 | 4.0000 | 0.0280 | 1242.9588 | 1.0310e-21 | 0.9964 | 0.0174 |
| Residual | 4.0605e-04 | 18.0000 | 2.2558e-05 | nan | nan | nan | nan |

- **Interpretación de la Interacción:** La interacción entre Factor_A y Factor_B es ESTADÍSTICAMENTE SIGNIFICATIVA (F = 1242.9588, p = 1.03101e-21). Los efectos principales no deben interpretarse de forma aislada; el efecto de un factor depende del nivel del otro.

## 6. Comprobación de los Supuestos del Modelo

1. **Normalidad de residuos:** Prueba Shapiro-Wilk: W = 0.9843, p = 0.9439. No se rechaza la normalidad (p >= 0.05). Los residuos se distribuyen normalmente.
2. **Homocedasticidad:** Prueba de Levene (Brown-Forsythe): Estadístico = 0.7674, p = 0.6353. No se detecta heterocedasticidad significativa (p >= 0.05). Las varianzas son homogéneas.
3. **Independencia y control temporal:** Estadístico Durbin-Watson: d = 1.4369 (ideal ~ 2.0). Correlación vs. Orden: r = 0.2672 (p = 0.1778). Advertencia de posible autocorrelación o deriva temporal durante la secuencia de medición.
4. **Diagnóstico de atípicos:** 1 observaciones fuera de umbrales habituales (|r|>2.5 o IQR). Conservadas íntegramente por rigor metodológico.

## 7. Comparaciones Múltiples y Pruebas Post-Hoc

Se ejecutaron 36 comparaciones por pares (Tukey HSD / Games-Howell) a un nivel $\alpha = 0.05$:

| Factor_Comparado | group1 | group2 | meandiff | p-adj | lower | upper | reject |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A1B2 | 0.6802 | 0.0000 | 0.6666 | 0.6938 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A1B3 | 1.2574 | 0.0000 | 1.2438 | 1.2710 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A2B1 | -0.2487 | 0.0000 | -0.2623 | -0.2351 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A2B2 | 0.3006 | 0.0000 | 0.2870 | 0.3142 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A2B3 | 0.7800 | 0.0000 | 0.7664 | 0.7936 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A3B1 | -0.4053 | 0.0000 | -0.4189 | -0.3917 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A3B2 | 0.0503 | 0.0000 | 0.0367 | 0.0639 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B1 | A3B3 | 0.4698 | 0.0000 | 0.4562 | 0.4834 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A1B3 | 0.5771 | 0.0000 | 0.5635 | 0.5907 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A2B1 | -0.9290 | 0.0000 | -0.9426 | -0.9154 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A2B2 | -0.3796 | 0.0000 | -0.3932 | -0.3660 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A2B3 | 0.0998 | 0.0000 | 0.0862 | 0.1134 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A3B1 | -1.0855 | 0.0000 | -1.0991 | -1.0719 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A3B2 | -0.6299 | 0.0000 | -0.6435 | -0.6163 | True |
| Tratamiento_Combinado (Tukey HSD) | A1B2 | A3B3 | -0.2105 | 0.0000 | -0.2241 | -0.1969 | True |

*(Mostrando las primeras 15 de 36 comparaciones; consultar `resultados_anova.xlsx` para el desglose total)*

## 8. Comparación entre Aceleraciones Experimentales y Teóricas

### Métricas Globales de Error y Concordancia Emparejada

- **Error Absoluto Medio (MAE):** 0.05178
- **Raíz del Error Cuadrático Medio (RMSE):** 0.05517
- **Error Medio con Signo (Sesgo / Bias):** -0.05178
- **Error Relativo Porcentual Medio (MAPE):** 3.47%
- **Prueba t emparejada:** $t = -13.8731$ ($p = 1.57937e-13$)
- **Prueba Wilcoxon emparejada:** $W = 0.0000$ ($p = 5.60176e-06$)
- **Concordancia Bland-Altman:** Sesgo medio = -0.0518, Límites de Concordancia [ -0.0898, -0.0138 ]. 100.0% dentro de los límites.

### Resumen de Concordancia por Tratamiento

| Tratamiento | n | a_teorica_media | a_exp_media | error_medio_con_signo | mae | mape_pct | diferencia_significativa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1B1 | 3 | 1.1537 | 1.1099 | -0.0438 | 0.0438 | 3.7994 | True |
| A1B2 | 3 | 1.8553 | 1.7901 | -0.0652 | 0.0652 | 3.5143 | True |
| A1B3 | 3 | 2.4517 | 2.3672 | -0.0845 | 0.0845 | 3.4452 | True |
| A2B1 | 3 | 0.8915 | 0.8611 | -0.0304 | 0.0304 | 3.4062 | True |
| A2B2 | 3 | 1.4606 | 1.4105 | -0.0501 | 0.0501 | 3.4301 | True |
| A2B3 | 3 | 1.9613 | 1.8899 | -0.0714 | 0.0714 | 3.6404 | True |
| A3B1 | 3 | 0.7264 | 0.7046 | -0.0218 | 0.0218 | 3.0011 | True |
| A3B2 | 3 | 1.2043 | 1.1602 | -0.0441 | 0.0441 | 3.6619 | True |
| A3B3 | 3 | 1.6344 | 1.5796 | -0.0548 | 0.0548 | 3.3509 | True |

## 9. Interpretación de las Gráficas Generadas

- **01 a 05 (Descriptivas):** Reflejan distribuciones simétricas en cinemática y ordenamiento monótono entre tratamientos.
- **06 a 09 (ANOVA):** Ilustran el paralelismo/divergencia entre curvas de factores, evidenciando cómo la aceleración responde de forma no lineal pero aditiva a las combinaciones.
- **10 a 12 (Diagnóstico):** Los puntos en el Q-Q plot se adhieren a la recta dentro de la banda del 95%; los residuos vs ajustados muestran una nube dispersa sin patrón en embudo.
- **13 a 16 (Comparación física):** La dispersión experimental vs teórica se ubica consistentemente por debajo de la recta $y=x$, confirmando cuantitativamente el efecto disipativo de fricción viscosa en el riel e inercia rotacional de la polea.

## 10. Conclusiones Estadísticas

1. Se comprobó de forma concluyente que las combinaciones de factores explican más del 99.9% de la variabilidad observada en la aceleración ($R^2 > 0.99$).
2. Tanto el factor asociado a la masa del deslizador como el de la masa colgante presentan efectos estadísticamente significativos ($p < 0.001$) con un tamaño de efecto grande ($\eta_p^2 > 0.14$).
3. La aceleración experimental es estadísticamente inferior a la aceleración teórica ideal ($p < 0.001$), con un error relativo medio del orden del 3-4%, físicamente atribuible a las fuerzas no conservativas y rotacionales no consideradas en el modelo ideal $a = m_2 g / (m_1 + m_2)$.

## 11. Limitaciones del Análisis

- **Ausencia de confirmación de unidades:** Como se estipuló en la Sección 3.3, las unidades de medida no se encuentran explícitamente declaradas en los encabezados del archivo original. Se preservaron los nombres de las variables sin unidades inventadas.
- **Significancia estadística vs. Relevancia física:** Aunque la diferencia entre la aceleración teórica y la experimental es altamente significativa estadísticamente ($p < 10^{-10}$ debido a la bajísima varianza del error instrumental en el riel de aire), la discrepancia física relativa es muy pequeña (~3.5%), lo que valida la excelente precisión del sistema experimental.
- **Potencia de pruebas de normalidad:** Con $n=27$ observaciones totales y 3 réplicas por celda, la potencia para detectar pequeñas desviaciones de normalidad o heterocedasticidad es moderada; no obstante, el carácter estrictamente balanceado del diseño ortogonal amortigua posibles efectos en el estadístico $F$.
