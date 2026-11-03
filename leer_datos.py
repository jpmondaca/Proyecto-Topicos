"""Lectura y validación de los datos del caso 07 (Chicago Food Inspections).

Lee `datos/datos.csv` sin modificar el archivo original, comprueba que sea la
copia entregada (hash SHA-256), que las columnas coincidan con
`datos/diccionario.csv` y que `inspection_id` sea una clave única.

Decisiones de lectura (ver LEEME.txt):
- UTF-8, coma separadora, punto decimal.
- Sólo la celda vacía se interpreta como ausente. No se usan los valores
  ausentes por defecto de pandas ("NA", "null", ...), para no convertir texto
  válido en faltante.
- Un valor ausente no equivale a cero: los identificadores se leen como
  enteros anulables (Int64) y `zip` como texto.
- Los textos (`results`, `violations`, nombres, etc.) se conservan sin
  recodificar. La limpieza se hace en pasos posteriores y documentados.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
DIR_DATOS = RAIZ / "datos"
ARCHIVO_DATOS = DIR_DATOS / "datos.csv"
ARCHIVO_DICCIONARIO = DIR_DATOS / "diccionario.csv"

# Hash de la copia entregada el 12-10-2026 (caso07_chicago_inspecciones.zip).
SHA256_ESPERADO = "6d250b8edf45f2f8cec3ee3a5ee91e648764ee3a32817faee4a35df16594d82a"

COLUMNAS_ENTERAS = ["inspection_id", "license_"]
COLUMNAS_REALES = ["latitude", "longitude"]
COLUMNA_FECHA = "inspection_date"


def sha256_archivo(ruta: Path, bloque: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def leer_diccionario(ruta: Path = ARCHIVO_DICCIONARIO) -> pd.DataFrame:
    return pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8")


def leer_datos(ruta: Path = ARCHIVO_DATOS, verificar_hash: bool = True) -> pd.DataFrame:
    """Lee el CSV de inspecciones y devuelve un DataFrame con tipos explícitos."""
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Descomprima caso07_chicago_inspecciones.zip "
            "en la carpeta datos/ (ver README.md)."
        )
    if verificar_hash:
        obtenido = sha256_archivo(ruta)
        if obtenido != SHA256_ESPERADO:
            raise ValueError(
                f"El hash de {ruta.name} ({obtenido}) no coincide con la copia "
                f"entregada ({SHA256_ESPERADO})."
            )

    df = pd.read_csv(
        ruta,
        dtype=str,
        keep_default_na=False,
        na_values=[""],
        encoding="utf-8",
    )

    # Columnas según el diccionario de la fuente.
    dicc = leer_diccionario()
    esperadas = list(dicc["variable"])
    if list(df.columns) != esperadas:
        raise ValueError(f"Columnas distintas al diccionario: {list(df.columns)}")

    # Conversión de tipos. errors="raise" para detectar valores no numéricos.
    for col in COLUMNAS_ENTERAS:
        df[col] = pd.to_numeric(df[col], errors="raise").astype("Int64")
    for col in COLUMNAS_REALES:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df[COLUMNA_FECHA] = pd.to_datetime(
        df[COLUMNA_FECHA], format="%Y-%m-%dT%H:%M:%S.%f", errors="raise"
    )

    # Clave de fila.
    if df["inspection_id"].isna().any():
        raise ValueError("Hay inspection_id ausentes.")
    if df["inspection_id"].duplicated().any():
        raise ValueError("inspection_id no es una clave única.")

    return df


if __name__ == "__main__":
    datos = leer_datos()
    print(f"Filas: {len(datos):,}  Columnas: {datos.shape[1]}")
    print(datos.dtypes)
    print(datos.head())
