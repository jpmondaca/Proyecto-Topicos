# Guía del caso 07 y lista de pendientes

Resumen de la pauta `EYP3407_trabajo_final.pdf` (12-10-2026) aplicado al caso 07.
La fuente oficial es siempre la pauta; esto es un apoyo de trabajo.

## Fechas

| Fecha | Entrega |
|---|---|
| **10 nov 2026, 20:00** | Informe PDF, presentación PDF, enlace al repositorio público y .zip de la versión final (Canvas) |
| **12 nov 2026** | Presentación de 10 min + 4 min de preguntas. Se sortea quién presenta cada sección |
| 13 nov 2026, 23:59 | Coevaluación individual (fuera del repositorio) |

Nota: presentación y defensa 50 %, informe 30 %, repositorio 20 %.

## Definiciones del caso (no cambiar después de mirar la prueba)

- **Unidad:** una inspección `Canvass` única.
- **Respuesta:** `Fail` = 1; `Pass` y `Pass w/ Conditions` = 0. `Out of Business`,
  `No Entry`, `Not Ready` y `Business Not Located` se cuantifican y se excluyen.
- **Historia:** las demás visitas del paquete (reinspecciones, denuncias, licencias)
  sirven sólo como antecedentes anteriores a la visita objetivo.
- **Prohibido como predictor:** `violations` de la visita actual y el `results` actual.
  `risk` sólo si se justifica que antecede a la visita.
- **Desarrollo:** 2019–2022, con ventanas temporales. **Prueba:** 2023–2024, una sola vez.
- **Referencia:** probabilidad constante de Fail estimada en entrenamiento.
- **Modelos:** M1 logística; M2 árbol podado o SVM; M3 random forest o boosting.
  Como máximo ~20 configuraciones por familia y 3 particiones internas.
- **Métricas:** log-loss (principal), Brier, AUC ROC, calibración, matriz de confusión,
  sensibilidad y VPP con un umbral fijado en desarrollo.
- **Incertidumbre:** remuestreo por establecimiento (licencia) o por bloques temporales.
- **Sensibilidades sugeridas:** (1) sin antecedentes de inspección; (2) locales nuevos
  (separar establecimientos completos), o `Pass w/ Conditions` evaluado aparte.

## Hallazgos del EDA que afectan decisiones

(ver `resultados/eda/resumen_eda.md` tras ejecutar `python analisis.py`)

- El paquete parte el 2-1-2019, así que sólo 12 % de los Canvass de 2019 tiene
  una visita previa observable, contra más de 95 % desde 2021. **Decisión pendiente:**
  ¿usar 2019 sólo como historia, o como entrenamiento con un indicador de "sin historia"?
- 803 Canvass comparten licencia, fecha y tipo con otra fila: posibles duplicados.
- `address` requiere normalizar espacios; enlazar por `license_` (249 filas con licencia 0).
- `facility_type`: 258 categorías normalizadas, la mayoría con menos de 30 visitas → agrupar
  categorías raras usando sólo entrenamiento.
- `risk` tiene categorías `All` y vacío.
- Prevalencia de Fail en desarrollo ≈ 0,25 (de 0,22 en 2019 a 0,27 en 2022).

## Checklist

- [x] Lectura reproducible y validación de datos
- [x] EDA inicial (desarrollo)
- [ ] Resolver duplicados y definir la tabla de construcción de la muestra final
- [ ] Tabla de predictores: nombre, interpretación, tipo, disponibilidad, decisión
- [ ] Variables de historia (último resultado, días desde la visita previa, n.º de Fail previos, violaciones previas)
- [ ] Particiones temporales de desarrollo
- [ ] Referencia + M1 + M2 + M3 con búsqueda de hiperparámetros acotada
- [ ] Umbral operativo fijado en desarrollo
- [ ] Evaluación única en prueba 2023–2024
- [ ] Incertidumbre por licencia; diagnóstico por tipo de local e historia
- [ ] Dos sensibilidades
- [ ] Informe (`informe.qmd` o equivalente) generado por `analisis.py`
- [ ] Presentación (≤ 10 diapositivas)
- [ ] Prueba en otro computador registrada en el README
- [ ] Enlace de descarga de los datos en el README
