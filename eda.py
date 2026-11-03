"""Análisis exploratorio del caso 07 (Chicago Food Inspections).

Genera tablas (.csv), figuras (.png) y un resumen (resumen_eda.md) en
`resultados/eda/`.

Regla para no contaminar la reserva de prueba (2023-2024): todo lo que use
`results` o `violations` de las inspecciones objetivo se calcula sólo con el
periodo de desarrollo (2019-2022). Del periodo de prueba se informan únicamente
tamaños, fechas y tipos de visita.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from leer_datos import RAIZ, leer_datos  # noqa: E402
from preparacion import (  # noqa: E402
    ANIOS_DESARROLLO, RESULTADOS_NEGATIVOS, RESULTADO_POSITIVO, TIPO_OBJETIVO,
    construir_poblacion, normalizar_texto, periodo,
)

DIR_SALIDA = RAIZ / "resultados" / "eda"
DIR_TABLAS = DIR_SALIDA / "tablas"
DIR_FIGURAS = DIR_SALIDA / "figuras"

# Rectángulo aproximado que contiene la ciudad de Chicago (control de calidad).
LAT_CHICAGO = (41.60, 42.05)
LON_CHICAGO = (-87.95, -87.50)

# Estilo de figuras: marcas delgadas, ejes y grilla discretos.
AZUL, NARANJO = "#2a78d6", "#eb6834"
TEXTO, TEXTO_2, GRILLA = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 150, "savefig.bbox": "tight",
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": GRILLA, "axes.labelcolor": TEXTO_2,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": TEXTO,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRILLA, "grid.linewidth": 0.6,
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "font.size": 9, "legend.frameon": False, "lines.linewidth": 2,
})

resumen: list[str] = []


def anotar(texto: str = "") -> None:
    resumen.append(texto)


def guardar_tabla(tabla: pd.DataFrame, nombre: str, index: bool = True) -> pd.DataFrame:
    tabla.to_csv(DIR_TABLAS / f"{nombre}.csv", index=index, encoding="utf-8")
    return tabla


def guardar_figura(fig: plt.Figure, nombre: str) -> None:
    fig.savefig(DIR_FIGURAS / f"{nombre}.png")
    plt.close(fig)


def tabla_md(tabla: pd.DataFrame, index: bool = True) -> str:
    """Tabla en Markdown sin depender de paquetes adicionales."""
    t = tabla.reset_index() if index else tabla
    filas = ["| " + " | ".join(map(str, t.columns)) + " |",
             "|" + "---|" * len(t.columns)]
    for _, r in t.iterrows():
        filas.append("| " + " | ".join(_fmt(v) for v in r) + " |")
    return "\n".join(filas)


def _fmt(v) -> str:
    if isinstance(v, (float, np.floating)):
        return "" if pd.isna(v) else f"{v:,.3f}"
    if isinstance(v, (int, np.integer)):
        return f"{v:,}"
    return "" if v is pd.NA else str(v)


def tasa_fail(df: pd.DataFrame, por: str | list[str]) -> pd.DataFrame:
    """Tamaño, número de Fail y prevalencia por grupo (filas con respuesta)."""
    t = (df.loc[df["y_fail"].notna()]
         .groupby(por, dropna=False, observed=True)["y_fail"]
         .agg(n="size", n_fail="sum"))
    t["n_fail"] = t["n_fail"].astype(int)
    t["tasa_fail"] = t["n_fail"] / t["n"]
    return t


# ---------------------------------------------------------------------------
# 1. Estructura general y calidad de cada columna
# ---------------------------------------------------------------------------
def perfil_columnas(df: pd.DataFrame) -> None:
    perfil = pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "n_faltantes": df.isna().sum(),
        "pct_faltantes": df.isna().mean() * 100,
        "n_unicos": df.nunique(dropna=True),
    })
    guardar_tabla(perfil, "01_perfil_columnas")
    anotar("## 1. Estructura de la base\n")
    anotar(f"- Filas: {len(df):,}; columnas: {df.shape[1]}.")
    anotar(f"- `inspection_id` es clave única: {df['inspection_id'].is_unique}.")
    anotar(f"- Rango de fechas: {df['inspection_date'].min():%Y-%m-%d} a "
           f"{df['inspection_date'].max():%Y-%m-%d}.\n")
    anotar(tabla_md(perfil.round(2)))
    anotar()


# ---------------------------------------------------------------------------
# 2. Tipos de visita (sin mirar resultados de prueba)
# ---------------------------------------------------------------------------
def tipos_de_visita(df: pd.DataFrame) -> None:
    tipos = (df.assign(periodo=periodo(df["inspection_date"]))
             .pivot_table(index="inspection_type", columns="periodo",
                          values="inspection_id", aggfunc="size", fill_value=0))
    tipos["total"] = tipos.sum(axis=1)
    tipos = tipos.sort_values("total", ascending=False)
    guardar_tabla(tipos, "02_tipos_de_visita")

    dev = df.loc[df["inspection_date"].dt.year.between(*ANIOS_DESARROLLO)]
    cruce = pd.crosstab(dev["inspection_type"], dev["results"], margins=True,
                        margins_name="total")
    cruce = cruce.sort_values("total", ascending=False)
    guardar_tabla(cruce, "03_tipo_por_resultado_desarrollo")

    anotar("## 2. Tipos de visita\n")
    anotar("Conteo por periodo (incluye prueba, porque no usa resultados):\n")
    anotar(tabla_md(tipos))
    anotar("\nTipo de visita por resultado, **sólo desarrollo 2019-2022**:\n")
    anotar(tabla_md(cruce))
    anotar()

    # Figura: visitas por mes, Canvass frente al resto.
    mes = df["inspection_date"].dt.to_period("M").dt.to_timestamp()
    serie = (pd.crosstab(mes, df["inspection_type"] == TIPO_OBJETIVO)
             .rename(columns={True: "Canvass", False: "Otras visitas"}))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(serie.index, serie["Canvass"], color=AZUL, label="Canvass (población objetivo)")
    ax.plot(serie.index, serie["Otras visitas"], color=NARANJO, label="Otras visitas (historia)")
    ax.axvline(pd.Timestamp("2023-01-01"), color=TEXTO_2, lw=1, ls="--")
    ax.text(pd.Timestamp("2023-01-15"), ax.get_ylim()[1] * 0.95,
            "inicio reserva de prueba", color=TEXTO_2, va="top", fontsize=8)
    ax.set_title("Inspecciones por mes, 2019-2024")
    ax.set_ylabel("Inspecciones por mes")
    ax.set_ylim(0, serie.values.max() * 1.1)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    guardar_figura(fig, "fig01_inspecciones_por_mes")


# ---------------------------------------------------------------------------
# 3. Construcción de la muestra analítica
# ---------------------------------------------------------------------------
def construccion_muestra(df: pd.DataFrame, pob: pd.DataFrame) -> None:
    dev = pob.loc[pob["periodo"] == "desarrollo"]
    prueba = pob.loc[pob["periodo"] == "prueba"]
    pasos = [
        ("Todas las visitas del paquete", len(df), df["license_"].nunique()),
        ("Inspecciones Canvass 2019-2024", len(pob), pob["license_"].nunique()),
        ("  Canvass desarrollo 2019-2022", len(dev), dev["license_"].nunique()),
        ("    con respuesta Fail/Pass/Pass w/ Conditions", int(dev["y_fail"].notna().sum()),
         dev.loc[dev["y_fail"].notna(), "license_"].nunique()),
        ("    con licencia válida para enlazar historia",
         int((dev["y_fail"].notna() & dev["licencia_valida"]).sum()),
         dev.loc[dev["y_fail"].notna() & dev["licencia_valida"], "license_"].nunique()),
        ("  Canvass prueba 2023-2024 (resultados no examinados)", len(prueba),
         prueba["license_"].nunique()),
    ]
    tabla = pd.DataFrame(pasos, columns=["paso", "filas", "licencias_distintas"])
    guardar_tabla(tabla, "04_construccion_muestra", index=False)

    excluidos = (dev.loc[dev["y_fail"].isna(), "results"].value_counts()
                 .rename("n").to_frame())
    guardar_tabla(excluidos, "05_resultados_excluidos_desarrollo")

    anotar("## 3. Construcción de la muestra\n")
    anotar(tabla_md(tabla, index=False))
    anotar("\nResultados de Canvass en desarrollo que quedan fuera de la "
           "respuesta binaria (no se recodifican como 0):\n")
    anotar(tabla_md(excluidos))
    anotar()


# ---------------------------------------------------------------------------
# 4. Calidad de datos
# ---------------------------------------------------------------------------
def calidad(df: pd.DataFrame) -> None:
    anotar("## 4. Calidad de los datos\n")

    lic = df["license_"]
    anotar(f"- `license_` ausente: {int(lic.isna().sum())}; igual a 0: "
           f"{int((lic == 0).sum())}. Esas filas no permiten enlazar historia.")

    ciudades = df["city"].value_counts(dropna=False)
    guardar_tabla(ciudades.rename("n").to_frame(), "06_variantes_city")
    no_chicago = (normalizar_texto(df["city"]) != "chicago").sum()
    anotar(f"- `city`: {df['city'].nunique()} variantes; {int(no_chicago)} filas "
           "no dicen exactamente 'chicago' (errores de tipeo, vacíos o comunas vecinas).")
    anotar(f"- `state` distinto de IL o vacío: {int((df['state'] != 'IL').sum())} filas.")

    riesgo = df["risk"].value_counts(dropna=False).rename("n").to_frame()
    guardar_tabla(riesgo, "07_categorias_risk")
    anotar("- `risk` incluye categorías especiales ('All' y vacío):\n")
    anotar(tabla_md(riesgo))

    ft = normalizar_texto(df["facility_type"])
    conteo_ft = ft.value_counts(dropna=False)
    guardar_tabla(conteo_ft.rename("n").to_frame(), "08_facility_type_normalizado")
    anotar(f"\n- `facility_type`: {df['facility_type'].nunique()} valores originales, "
           f"{ft.nunique()} tras normalizar mayúsculas/espacios; "
           f"{int((conteo_ft < 30).sum())} categorías con menos de 30 visitas; "
           f"{int(ft.isna().sum())} vacíos.")

    lat, lon = df["latitude"], df["longitude"]
    fuera = lat.notna() & ~(lat.between(*LAT_CHICAGO) & lon.between(*LON_CHICAGO))
    anotar(f"- Coordenadas ausentes: {int(lat.isna().sum())}; fuera del rectángulo "
           f"de Chicago: {int(fuera.sum())}.")

    # Posibles duplicados: misma licencia, fecha y tipo de visita.
    validas = df.loc[lic.notna() & (lic > 0)]
    dup = validas.duplicated(["license_", "inspection_date", "inspection_type"], keep=False)
    dup_canvass = dup & (validas["inspection_type"] == TIPO_OBJETIVO)
    guardar_tabla(validas.loc[dup].sort_values(["license_", "inspection_date"])
                  [["inspection_id", "license_", "dba_name", "address",
                    "inspection_date", "inspection_type"]],
                  "09_posibles_duplicados", index=False)
    anotar(f"- Posibles duplicados (misma licencia, fecha y tipo): {int(dup.sum())} filas, "
           f"de ellas {int(dup_canvass.sum())} Canvass. La fuente advierte que pueden "
           "existir reportes duplicados; se revisarán antes de modelar.")

    # Numeración de violaciones: confirma el esquema posterior a julio de 2018.
    numeros = (df["violations"].str.findall(r"(?:^|\| )(\d+)\. ")
               .explode().dropna().astype(int))
    anotar(f"- Números de violación observados: {numeros.min()} a {numeros.max()} "
           f"({numeros.nunique()} distintos). Corresponde al esquema vigente desde "
           "el 1-7-2018, no a la numeración 1-44 y 70 del PDF del diccionario.\n")


# ---------------------------------------------------------------------------
# 5. Establecimientos e historia disponible
# ---------------------------------------------------------------------------
def entidades_e_historia(df: pd.DataFrame, pob: pd.DataFrame) -> None:
    validas = df.loc[df["license_"].notna() & (df["license_"] > 0)]
    visitas_por_lic = validas.groupby("license_").size()
    canvass_por_lic = pob.loc[pob["licencia_valida"]].groupby("license_").size()
    dir_por_lic = normalizar_texto(validas["address"]).groupby(validas["license_"]).nunique()
    nom_por_lic = validas.assign(n=normalizar_texto(validas["dba_name"])).groupby("license_")["n"].nunique()
    lic_por_dir = validas.groupby(normalizar_texto(validas["address"]))["license_"].nunique()

    desc = pd.DataFrame({
        "visitas_por_licencia": visitas_por_lic.describe(),
        "canvass_por_licencia": canvass_por_lic.describe(),
    })
    guardar_tabla(desc, "10_visitas_por_licencia")

    anotar("## 5. Establecimientos e historia\n")
    anotar(f"- Licencias válidas distintas: {visitas_por_lic.size:,}; con al menos un "
           f"Canvass: {canvass_por_lic.size:,}.")
    sin_norm = validas.groupby("license_")["address"].nunique()
    anotar(f"- `address` trae espacios finales inconsistentes: sin normalizar, "
           f"{int((sin_norm > 1).sum())} licencias parecen tener más de una dirección.")
    anotar(f"- Licencias con más de una dirección (normalizada): {int((dir_por_lic > 1).sum())}; "
           f"con más de un nombre (dba_name normalizado): {int((nom_por_lic > 1).sum())}.")
    anotar(f"- Direcciones con más de una licencia: {int((lic_por_dir > 1).sum())} "
           "(locales sucesivos en el mismo lugar o locales en el mismo edificio: "
           "por eso se enlaza por licencia y no por dirección).\n")
    anotar(tabla_md(desc.round(2)))

    # Disponibilidad de historia por año (no usa la respuesta, incluye prueba).
    hist_anio = (pob.loc[pob["licencia_valida"]]
                 .groupby(pob["inspection_date"].dt.year.astype(str).rename("anio"))["tiene_historia"]
                 .agg(n="size", con_historia="sum"))
    hist_anio["pct_con_historia"] = hist_anio["con_historia"] / hist_anio["n"] * 100
    guardar_tabla(hist_anio, "11_historia_por_anio")
    anotar("\nCanvass con alguna visita previa en el paquete, por año. En 2019 "
           "la historia está truncada porque el paquete parte el 2-1-2019:\n")
    anotar(tabla_md(hist_anio))
    anotar()


# ---------------------------------------------------------------------------
# 6. Respuesta en desarrollo
# ---------------------------------------------------------------------------
def respuesta_desarrollo(pob: pd.DataFrame) -> None:
    dev = pob.loc[(pob["periodo"] == "desarrollo") & pob["y_fail"].notna()].copy()
    anotar("## 6. Respuesta (sólo desarrollo 2019-2022)\n")
    anotar(f"- Inspecciones con respuesta: {len(dev):,}; Fail: {int(dev['y_fail'].sum()):,}; "
           f"prevalencia: {dev['y_fail'].mean():.3f}.")
    pwc = (dev["results"] == "Pass w/ Conditions").mean()
    anotar(f"- Dentro del grupo 0, 'Pass w/ Conditions' representa {pwc:.3f} del total "
           "de inspecciones con respuesta (relevante para la sensibilidad sugerida en la ficha).\n")

    por_anio = guardar_tabla(tasa_fail(dev, dev["inspection_date"].dt.year.astype(str).rename("anio")),
                             "12_fail_por_anio")
    anotar(tabla_md(por_anio))

    # Por mes.
    mes = dev["inspection_date"].dt.to_period("M").dt.to_timestamp().rename("mes")
    por_mes = guardar_tabla(tasa_fail(dev, mes), "13_fail_por_mes")
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(por_mes.index, por_mes["tasa_fail"], color=AZUL, marker="o", ms=3)
    ax.axhline(dev["y_fail"].mean(), color=TEXTO_2, lw=1, ls="--")
    ax.text(por_mes.index[0], dev["y_fail"].mean(), " promedio 2019-2022",
            color=TEXTO_2, va="bottom", fontsize=8)
    ax.set_ylim(0, max(0.5, por_mes["tasa_fail"].max() * 1.1))
    ax.set_title("Proporción de Fail en inspecciones Canvass por mes (desarrollo)")
    ax.set_ylabel("Proporción Fail")
    guardar_figura(fig, "fig02_fail_por_mes_desarrollo")
    pocos = por_mes.loc[por_mes["n"] < 100]
    anotar(f"\n- Inspecciones con respuesta por mes: mínimo {por_mes['n'].min():,} "
           f"({por_mes['n'].idxmin():%Y-%m}), máximo {por_mes['n'].max():,}. "
           + (f"Meses con menos de 100 (proporción inestable): "
              f"{', '.join(f'{m:%Y-%m}' for m in pocos.index)}." if len(pocos) else ""))

    # Por tipo de local (top 8 + otros).
    ft = normalizar_texto(dev["facility_type"]).fillna("(vacío)")
    top = ft.value_counts().head(8).index
    dev["tipo_local"] = ft.where(ft.isin(top), "otros")
    por_tipo = guardar_tabla(tasa_fail(dev, "tipo_local").sort_values("n"), "14_fail_por_tipo_local")
    _barras_tasa(por_tipo, "Proporción de Fail por tipo de local (desarrollo)",
                 "fig03_fail_por_tipo_local")

    por_riesgo = guardar_tabla(tasa_fail(dev, "risk"), "15_fail_por_risk")
    anotar("\nPor categoría de riesgo (su uso como predictor requiere justificar "
           "que el nivel se conocía antes de la visita):\n")
    anotar(tabla_md(por_riesgo))

    zip_ = guardar_tabla(tasa_fail(dev, "zip"), "16_fail_por_zip")
    anotar(f"\n- Códigos postales con respuesta: {len(zip_)}; con menos de 50 "
           f"inspecciones: {int((zip_['n'] < 50).sum())}. Proporción de Fail por zip: "
           f"mín. {zip_.loc[zip_['n'] >= 50, 'tasa_fail'].min():.3f}, "
           f"máx. {zip_.loc[zip_['n'] >= 50, 'tasa_fail'].max():.3f} (zips con n >= 50).")
    anotar()


def _barras_tasa(t: pd.DataFrame, titulo: str, nombre: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 0.42 * len(t) + 1))
    ax.barh(t.index.astype(str), t["tasa_fail"], color=AZUL, height=0.6)
    for i, (tasa, n) in enumerate(zip(t["tasa_fail"], t["n"])):
        ax.text(tasa, i, f"  {tasa:.2f}  (n={n:,})", va="center", color=TEXTO_2, fontsize=8)
    ax.set_xlim(0, t["tasa_fail"].max() * 1.35)
    ax.set_xlabel("Proporción Fail")
    ax.grid(axis="y", visible=False)
    ax.set_title(titulo)
    guardar_figura(fig, nombre)


# ---------------------------------------------------------------------------
# 7. Antecedentes frente a la respuesta (desarrollo)
# ---------------------------------------------------------------------------
def historia_y_respuesta(pob: pd.DataFrame) -> None:
    dev = pob.loc[(pob["periodo"] == "desarrollo") & pob["y_fail"].notna()
                  & pob["licencia_valida"]].copy()
    anotar("## 7. Antecedentes previos y respuesta (sólo desarrollo)\n")

    dev["historia"] = dev["tiene_historia"].map({True: "con visita previa", False: "sin visita previa"})
    con_hist = guardar_tabla(tasa_fail(dev, ["historia"]), "17_fail_por_tiene_historia")
    anotar(tabla_md(con_hist))
    anotar("\nOjo: casi todas las inspecciones 'sin visita previa' son de 2019, cuando la "
           "historia está truncada; la comparación mezcla el efecto del año.\n")
    por_anio_hist = guardar_tabla(
        tasa_fail(dev, [dev["inspection_date"].dt.year.astype(str).rename("anio"), "historia"]),
        "17b_fail_por_anio_e_historia")
    anotar(tabla_md(por_anio_hist))

    prev = dev["resultado_previo"].fillna("(sin visita previa)")
    dev["resultado_previo_g"] = prev
    por_prev = guardar_tabla(tasa_fail(dev, "resultado_previo_g").sort_values("n"),
                             "18_fail_por_resultado_previo")
    _barras_tasa(por_prev, "Proporción de Fail según el resultado de la visita previa",
                 "fig04_fail_por_resultado_previo")

    cortes = [0, 30, 90, 180, 365, 540, 730, np.inf]
    etiquetas = ["1-30", "31-90", "91-180", "181-365", "366-540", "541-730", ">730"]
    dev["dias_previa_g"] = pd.cut(dev["dias_desde_previa"], cortes, labels=etiquetas)
    por_dias = guardar_tabla(tasa_fail(dev, "dias_previa_g"), "19_fail_por_dias_desde_previa")
    _barras_tasa(por_dias.iloc[::-1], "Proporción de Fail según días desde la visita previa",
                 "fig05_fail_por_dias_desde_previa")

    dev["n_fail_previos_g"] = dev["n_fail_previos"].clip(upper=3).astype(int).astype(str).replace("3", "3+")
    por_nfail = guardar_tabla(tasa_fail(dev, "n_fail_previos_g"), "20_fail_por_n_fail_previos")
    anotar("\nPor número de Fail previos en el paquete (de cualquier tipo de visita):\n")
    anotar(tabla_md(por_nfail))
    anotar("\nVer figuras 4 y 5. Estas asociaciones son descriptivas: la frecuencia de "
           "visita depende del riesgo asignado y de denuncias, no son efectos causales.\n")


# ---------------------------------------------------------------------------
# 8. Violaciones (información posterior: sólo para entender la fuga)
# ---------------------------------------------------------------------------
def violaciones(pob: pd.DataFrame) -> None:
    dev = pob.loc[(pob["periodo"] == "desarrollo") & pob["y_fail"].notna()].copy()
    dev["n_violaciones"] = dev["violations"].fillna("").str.count(r"(?:^|\| )\d+\. ")
    t = guardar_tabla(dev.groupby("results")["n_violaciones"].describe(),
                      "21_violaciones_por_resultado_desarrollo")
    anotar("## 8. Violaciones de la inspección actual (no admisibles como predictor)\n")
    anotar("`violations` describe los hallazgos de la misma visita: revela la respuesta. "
           "Se muestra sólo para documentar por qué se excluye. Puede usarse en forma "
           "de antecedentes de visitas anteriores.\n")
    anotar(tabla_md(t.round(2)))

    fig, ax = plt.subplots(figsize=(7, 3.4))
    bins = np.arange(0, 27) - 0.5
    for valor, color, etiqueta in [(0, AZUL, "Pass / Pass w/ Conditions"), (1, NARANJO, "Fail")]:
        x = dev.loc[dev["y_fail"] == valor, "n_violaciones"].clip(upper=25)
        ax.hist(x, bins=bins, density=True, histtype="step", color=color, lw=2, label=etiqueta)
    ax.set_xlabel("Número de violaciones registradas en la inspección (25 = 25 o más)")
    ax.set_ylabel("Proporción de inspecciones")
    ax.set_title("Violaciones de la misma visita según resultado (desarrollo)")
    ax.legend()
    guardar_figura(fig, "fig06_violaciones_por_resultado")
    anotar()


# ---------------------------------------------------------------------------
# 9. Cobertura geográfica (sin respuesta)
# ---------------------------------------------------------------------------
def geografia(pob: pd.DataFrame) -> None:
    p = pob.loc[pob["latitude"].between(*LAT_CHICAGO) & pob["longitude"].between(*LON_CHICAGO)]
    fig, ax = plt.subplots(figsize=(5.2, 6.2))
    hb = ax.hexbin(p["longitude"], p["latitude"], gridsize=45, cmap="Blues", mincnt=1,
                   bins="log", linewidths=0.2, edgecolors="#fcfcfb")
    cb = fig.colorbar(hb, ax=ax, shrink=0.7)
    cb.set_label("Inspecciones Canvass (escala log)")
    ax.set_aspect(1 / np.cos(np.deg2rad(41.85)))
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(False)
    ax.set_title("Ubicación de inspecciones Canvass, 2019-2024")
    guardar_figura(fig, "fig07_mapa_canvass")


# ---------------------------------------------------------------------------
def ejecutar_eda() -> Path:
    for d in (DIR_TABLAS, DIR_FIGURAS):
        d.mkdir(parents=True, exist_ok=True)
    resumen.clear()

    df = leer_datos()
    pob = construir_poblacion(df)

    anotar("# Análisis exploratorio - Caso 07 Chicago Food Inspections\n")
    anotar("Archivo generado automáticamente por `eda.py`; no editar a mano.\n")
    anotar(f"Población objetivo: inspecciones `{TIPO_OBJETIVO}`. Respuesta: "
           f"`{RESULTADO_POSITIVO}` = 1 frente a {', '.join(RESULTADOS_NEGATIVOS)} = 0. "
           "Lo que usa resultados se calcula sólo en desarrollo (2019-2022).\n")

    perfil_columnas(df)
    tipos_de_visita(df)
    construccion_muestra(df, pob)
    calidad(df)
    entidades_e_historia(df, pob)
    respuesta_desarrollo(pob)
    historia_y_respuesta(pob)
    violaciones(pob)
    geografia(pob)

    anotar("## Figuras\n")
    for f in sorted(DIR_FIGURAS.glob("*.png")):
        anotar(f"![{f.stem}](figuras/{f.name})")

    ruta = DIR_SALIDA / "resumen_eda.md"
    ruta.write_text("\n".join(resumen) + "\n", encoding="utf-8")
    return ruta


if __name__ == "__main__":
    print(f"Resumen escrito en {ejecutar_eda()}")
