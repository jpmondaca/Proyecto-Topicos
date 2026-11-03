"""Punto de entrada único del proyecto (EYP3407, caso 07).

Uso:
    python analisis.py

Etapas actuales:
    1. Lectura y validación de datos (leer_datos.py).
    2. Análisis exploratorio (eda.py) -> resultados/eda/.

Las etapas de particiones, modelos, evaluación e informe se agregarán aquí.
"""

import platform
import sys
import time

import matplotlib
import numpy as np
import pandas as pd

from eda import ejecutar_eda

SEMILLA = 20261012


def main() -> None:
    np.random.seed(SEMILLA)
    inicio = time.time()
    print(f"Python {sys.version.split()[0]} | pandas {pd.__version__} | "
          f"numpy {np.__version__} | matplotlib {matplotlib.__version__} | "
          f"{platform.platform()}")

    print("[1/1] Análisis exploratorio...")
    ruta = ejecutar_eda()
    print(f"      -> {ruta}")

    print(f"Listo en {time.time() - inicio:.1f} s.")


if __name__ == "__main__":
    main()
