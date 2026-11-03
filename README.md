# Proyecto-Topicos — EYP3407, caso 07: Chicago Food Inspections

Trabajo final de *Tópicos Aplicados en Estadística* (EYP3407, PUC, 2.º semestre 2026).

**Pregunta:** entre establecimientos sometidos a una inspección rutinaria
(`Canvass`), ¿cuáles tienen mayor probabilidad de obtener un resultado `Fail`?

| | |
|---|---|
| Población | Inspecciones `Canvass` 2019–2024 (sin reinspecciones ni denuncias) |
| Respuesta | `Fail` = 1; `Pass` / `Pass w/ Conditions` = 0; otros resultados se excluyen y se cuantifican |
| Desarrollo | 2019–2022 |
| Reserva de prueba | 2023–2024 (se usa una sola vez al final) |

## Integrantes

- _(completar)_
- _(completar)_
- _(completar)_
- _(completar)_

## Datos

- Paquete: `caso07_chicago_inspecciones.zip`, entregado por el curso (copia preparada el 12-10-2026).
- Productor: City of Chicago, Chicago Department of Public Health — *Food Inspections*
  (<https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5>).
  Consulta usada por el curso: `datos/LEEME.txt`.
- Descomprima el paquete en `datos/`. Debe quedar:

```
datos/
  datos.csv                  # 104 468 inspecciones (no se sube a Git: ~117 MB)
  diccionario.csv            # nombres y tipos publicados por la fuente
  diccionario (bueno).pdf    # descripción de la fuente
  LEEME.txt
```

- `datos.csv` no está en el repositorio porque supera el límite de 100 MB de GitHub.
  `leer_datos.py` comprueba su SHA-256:
  `6d250b8edf45f2f8cec3ee3a5ee91e648764ee3a32817faee4a35df16594d82a`.
  _(Pendiente: agregar un enlace de descarga del .zip, exigido por la pauta, §5.3.)_

## Entorno e instalación

Probado con Python 3.9.6 en macOS 27 (Apple M5, 24 GB RAM).

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

Hay dos formas equivalentes de ejecutar lo implementado hasta ahora:

**A. Notebook (todo el código en un solo archivo, con explicaciones):**

```bash
jupyter nbconvert --to notebook --execute --inplace proyecto_caso07.ipynb
```

También se puede abrir en Jupyter o VS Code y usar *Restart & Run All*. En VS Code hay que abrir
**la carpeta del proyecto** (*File → Open Folder*), no sólo el archivo, y elegir el kernel `.venv`;
si no, VS Code no ve el entorno y aparece `ModuleNotFoundError`. Tarda ~10 s y
escribe tablas y figuras en `resultados/notebook/`.

**B. Scripts:**

```bash
python analisis.py
```

1. `leer_datos.py` — lee `datos/datos.csv`, verifica hash, columnas y clave única `inspection_id`.
2. `preparacion.py` — define población, respuesta, periodos e historia previa por licencia.
3. `eda.py` — análisis exploratorio: tablas, figuras y `resultados/eda/resumen_eda.md`.

Ambas rutas producen las mismas cifras (verificado el 2026-11-03). Semilla global: `20261012`.

## Estructura

```
proyecto_caso07.ipynb  # notebook con todo el código del proyecto
analisis.py        # punto de entrada (scripts)
leer_datos.py      # lectura y validación
preparacion.py     # población, respuesta e historia sin fuga
eda.py             # análisis exploratorio
requirements.txt
datos/             # entradas del caso (datos.csv fuera de Git)
resultados/        # salidas generadas (fuera de Git)
docs/
  guia_caso07.md   # resumen del encargo y lista de pendientes
  USO_IA.md        # declaración de uso de IA (exigida por la pauta §6.4)
```

## Prueba desde copia limpia

| Fecha | Quién / equipo | Comando | Resultado |
|---|---|---|---|
| 2026-11-03 | _(completar)_ (macOS, Python 3.9.6) | `python analisis.py` | OK, EDA generado |
| 2026-11-03 | _(completar)_ (macOS, Python 3.9.6) | `jupyter nbconvert --execute` del notebook | OK, mismas cifras que los scripts |

## Uso de IA

Ver [`docs/USO_IA.md`](docs/USO_IA.md).
