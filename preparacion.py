"""Definiciones del caso 07 y construcción de la población objetivo.

Este módulo concentra las reglas que se reutilizarán en el análisis exploratorio
y, más adelante, en el modelamiento:

- Población: inspecciones de tipo exactamente "Canvass" (se excluyen
  "Canvass Re-Inspection", denuncias, licencias y otras visitas).
- Respuesta: Fail = 1; Pass o Pass w/ Conditions = 0. Los demás resultados
  (Out of Business, No Entry, Not Ready, Business Not Located) quedan sin
  respuesta (NA) y se excluyen de la definición binaria, sin recodificarlos
  como 0.
- Periodos: desarrollo 2019-2022; reserva de prueba 2023-2024.
- Historia: las otras visitas del paquete (de cualquier tipo) sirven como
  antecedentes, siempre que su fecha sea estrictamente anterior a la visita
  objetivo. Como la fuente no registra hora, las visitas del mismo día no se
  usan como historia.
"""

from __future__ import annotations

import pandas as pd

TIPO_OBJETIVO = "Canvass"
RESULTADO_POSITIVO = "Fail"
RESULTADOS_NEGATIVOS = ("Pass", "Pass w/ Conditions")
ANIOS_DESARROLLO = (2019, 2022)
ANIOS_PRUEBA = (2023, 2024)


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Minúsculas y espacios colapsados. Conserva NA."""
    return serie.str.strip().str.lower().str.replace(r"\s+", " ", regex=True)


def periodo(fecha: pd.Series) -> pd.Series:
    anio = fecha.dt.year
    salida = pd.Series(pd.NA, index=fecha.index, dtype="string")
    salida[anio.between(*ANIOS_DESARROLLO)] = "desarrollo"
    salida[anio.between(*ANIOS_PRUEBA)] = "prueba"
    return salida


def respuesta_binaria(resultados: pd.Series) -> pd.Series:
    """1 = Fail, 0 = Pass / Pass w/ Conditions, NA = otro resultado."""
    y = pd.Series(pd.NA, index=resultados.index, dtype="Int8")
    y[resultados == RESULTADO_POSITIVO] = 1
    y[resultados.isin(RESULTADOS_NEGATIVOS)] = 0
    return y


def licencia_valida(licencia: pd.Series) -> pd.Series:
    """La licencia 0 o ausente no permite enlazar historia."""
    return licencia.notna() & (licencia > 0)


def agregar_historia(objetivo: pd.DataFrame, todas: pd.DataFrame) -> pd.DataFrame:
    """Agrega antecedentes de visitas estrictamente anteriores, por licencia.

    Columnas nuevas:
    - tiene_historia: hubo alguna visita previa en el paquete (NA si la
      licencia no es válida).
    - fecha_previa, tipo_previo, resultado_previo: última visita anterior.
    - dias_desde_previa: días entre la visita previa y la objetivo.
    - n_visitas_previas, n_fail_previos: conteos acumulados anteriores.
    """
    obj = objetivo.copy()
    obj["licencia_valida"] = licencia_valida(obj["license_"])

    hist = todas.loc[licencia_valida(todas["license_"]),
                     ["license_", "inspection_id", "inspection_date",
                      "inspection_type", "results"]].copy()
    hist["license_"] = hist["license_"].astype("int64")

    # Última visita estrictamente anterior (merge_asof sin coincidencias exactas).
    previas = (hist.sort_values(["inspection_date", "inspection_id"])
               .rename(columns={"inspection_type": "tipo_previo",
                                "results": "resultado_previo"}))
    previas["fecha_previa"] = previas["inspection_date"]
    previas = previas.drop(columns="inspection_id")

    validas = obj.loc[obj["licencia_valida"]].copy()
    validas["license_"] = validas["license_"].astype("int64")
    validas = validas.sort_values(["inspection_date", "inspection_id"])
    validas = pd.merge_asof(
        validas, previas, on="inspection_date", by="license_",
        allow_exact_matches=False, direction="backward",
    )

    # Conteos acumulados de visitas y Fail en fechas anteriores.
    por_dia = (hist.assign(es_fail=(hist["results"] == RESULTADO_POSITIVO).astype(int))
               .groupby(["license_", "inspection_date"])
               .agg(n_dia=("inspection_id", "size"), fail_dia=("es_fail", "sum"))
               .sort_index())
    acumulado = por_dia.groupby(level=0).cumsum()
    previo = pd.DataFrame({
        "n_visitas_previas": acumulado["n_dia"] - por_dia["n_dia"],
        "n_fail_previos": acumulado["fail_dia"] - por_dia["fail_dia"],
    }).reset_index()
    validas = validas.merge(previo, on=["license_", "inspection_date"], how="left")

    validas["tiene_historia"] = validas["fecha_previa"].notna()
    validas["dias_desde_previa"] = (
        validas["inspection_date"] - validas["fecha_previa"]).dt.days

    cols_nuevas = ["tiene_historia", "fecha_previa", "tipo_previo",
                   "resultado_previo", "dias_desde_previa",
                   "n_visitas_previas", "n_fail_previos"]
    validas = validas.set_index("inspection_id")[cols_nuevas]
    obj = obj.join(validas, on="inspection_id")
    obj["tiene_historia"] = obj["tiene_historia"].astype("boolean")
    obj.loc[~obj["licencia_valida"], "tiene_historia"] = pd.NA
    return obj


def construir_poblacion(df: pd.DataFrame) -> pd.DataFrame:
    """Inspecciones Canvass con periodo, respuesta e historia previa."""
    canvass = df.loc[df["inspection_type"] == TIPO_OBJETIVO].copy()
    canvass["periodo"] = periodo(canvass["inspection_date"])
    canvass["y_fail"] = respuesta_binaria(canvass["results"])
    canvass = agregar_historia(canvass, df)
    return canvass.sort_values(["inspection_date", "inspection_id"]).reset_index(drop=True)

