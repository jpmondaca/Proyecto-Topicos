# Declaración de uso de inteligencia artificial

La pauta (§6.4) permite apoyo de IA para programación, depuración, explicaciones
y revisión de redacción, con declaración de herramienta, fecha, propósito, partes
afectadas y comprobaciones. El equipo es responsable de verificar todo y debe
poder explicarlo sin asistencia en la defensa.

Cada entrada registra una sesión de trabajo.

---

## Sesión 1 — 2026-11-03

- **Herramienta:** Claude Code (modelo Claude Opus 5.5, Anthropic).
- **Rama:** `eda-inicial`.

### Propósito

1. Leer la pauta (`EYP3407_trabajo_final.pdf`), el diccionario de la fuente y
   `LEEME.txt`, y resumir qué exige el caso 07. Resultado en
   [`guia_caso07.md`](guia_caso07.md).
2. Escribir el código de lectura de datos y el análisis exploratorio.

### Partes afectadas

| Archivo | Qué hizo la IA |
|---|---|
| `leer_datos.py` | Lectura con tipos explícitos (sólo la celda vacía es NA), verificación de hash SHA-256, columnas contra `diccionario.csv` y unicidad de `inspection_id`. |
| `preparacion.py` | Población Canvass, respuesta binaria (otros resultados = NA, no 0), periodos desarrollo/prueba e historia por licencia usando sólo fechas estrictamente anteriores (`merge_asof` sin coincidencias exactas). |
| `eda.py` | Tablas, figuras y `resumen_eda.md`. Todo lo que usa `results` o `violations` se restringe a 2019–2022. |
| `analisis.py`, `requirements.txt`, `.gitignore`, `README.md` | Punto de entrada único, versiones, exclusión de `datos.csv` (117 MB) y documentación. |

### Comprobaciones realizadas

- `python analisis.py` se ejecutó completo desde el entorno virtual (Python 3.9.6, pandas 2.3.3); tarda ~10 s.
- Se revisaron a mano las cifras del resumen contra conteos directos: 104 468 filas, 52 675 Canvass y `inspection_id` único.
- Se revisaron visualmente las figuras. Hubo dos ajustes: la leyenda de la fig. 1 tapaba las líneas y el último intervalo del histograma de la fig. 6 quedaba fuera.
- Se detectó un problema de datos: `address` trae espacios finales inconsistentes. Sin normalizar, 9 540 licencias parecían tener varias direcciones; tras normalizar quedan 107.
- Se comprobó que `violations` usa números 1–64, que es el esquema posterior a julio de 2018 y no el 1–44 y 70 que describe el PDF.

### Advertencias para el equipo

- Durante la primera exploración, la IA imprimió una vez el conteo de `results`
  de Canvass para **todo** 2019–2024 (incluida la reserva de prueba), sólo como
  tabla de frecuencias, sin variables ni modelos. Desde entonces el código restringe
  todo análisis de resultados a desarrollo. Se declara por transparencia (pauta §4.1).
- El equipo debe revisar y entender `preparacion.py::agregar_historia` antes de
  la defensa: es donde se puede introducir fuga de información.

### Pendiente de verificación humana

- [ ] Leer y validar `preparacion.py` y `eda.py` línea por línea.
- [ ] Decidir cómo tratar los 803 Canvass posiblemente duplicados (misma licencia, fecha y tipo).
- [ ] Decidir si `risk` es admisible como predictor.

---

## Sesión 2 — 2026-11-03

- **Herramienta:** Claude Code (modelo Claude Opus 5.5, Anthropic).
- **Rama:** `eda-inicial`.

### Propósito

Reunir todo el código (lectura, preparación y exploratorio) en un solo notebook,
`proyecto_caso07.ipynb`, con explicaciones en markdown antes de cada sección.

### Partes afectadas

| Archivo | Qué hizo la IA |
|---|---|
| `proyecto_caso07.ipynb` | Notebook nuevo con 60 celdas: configuración, lectura y validación, definiciones del caso, historia sin fuga, construcción de la muestra, calidad, entidades, respuesta, antecedentes, violaciones, mapa y síntesis. Guarda salidas en `resultados/notebook/`. |
| `requirements.txt`, `README.md` | Dependencias para ejecutar el notebook e instrucciones de ejecución. |

### Comprobaciones realizadas

- El notebook se ejecutó completo desde un kernel nuevo con `jupyter nbconvert --execute` (~10 s), sin errores ni advertencias.
- Se agregó una aserción que comprueba que ninguna visita previa tenga fecha igual o posterior a la inspección objetivo.
- Se compararon 7 tablas clave del notebook con las de `eda.py`: las cifras son idénticas (sólo cambia el texto de una etiqueta).

### Advertencia para el equipo

El código existe por ahora en dos lugares: el notebook y los scripts `.py`. Si se modifica
uno, hay que modificar el otro, o bien elegir uno solo como fuente oficial. Si no, el
informe podría no coincidir con lo que produce el repositorio (criterio "Ejecución y concordancia").

---

## Sesión 3 — 2026-11-03

- **Problema:** en VS Code el notebook falló con `ModuleNotFoundError: No module named 'matplotlib'`.
- **Causa:** el kernel elegido era el Python del sistema (`/usr/bin/python3`, también 3.9.6), no el `.venv` del proyecto.
- **Cambio:** se agregó al inicio del notebook una celda que muestra qué Python se usa y da un mensaje claro si faltan librerías. También se creó `.vscode/settings.json` (local, no versionado) para que VS Code use el `.venv`.
- **Comprobación:** el notebook se volvió a ejecutar completo con el kernel `.venv`, sin errores.
- **Causa final:** VS Code tenía abierto sólo el archivo del notebook, sin la carpeta del proyecto, y por eso no detectaba `.venv`. Se resolvió abriendo la carpeta (`code ~/projects/Proyecto-Topicos`) y eligiendo el kernel `.venv`. El notebook corrió completo en VS Code.
