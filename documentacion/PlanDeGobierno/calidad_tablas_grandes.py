"""
Calidad de las tablas grandes (Generación, Capacidad y Compras en bolsa) sobre los Excel crudos de XM.

Estas tablas no se pueden medir con fórmulas en Excel:
  - Capacidad (~1,38 millones de filas) no cabe en una hoja (máx. 1.048.576).
  - Generación (~505.000) y Compras (~199.000) caben, pero la regla de unicidad
    compara cada fila contra todas y Excel no termina de calcularla.

Mide las mismas reglas del Plan de Gobierno (§7) y escribe un CSV con, por regla:
registros evaluados y registros que cumplen. Esos dos números se copian a la hoja
1_Calidad de cada Excel; el % y el semáforo los calcula la plantilla.

Uso:
    python calidad_tablas_grandes.py <carpeta HidrologiaYGeneracionEnergetica> <salida.csv> [AAAA-MM-DD descarga]

Capa medida: raw (los archivos tal como se descargan de Sinergox, sin el pipeline).
"""
import glob
import sys
from pathlib import Path

import pandas as pd

HORAS = [str(h) for h in range(24)]
FECHA_MIN = pd.Timestamp("2022-01-01")
TIPOS_GENERACION = {"HIDRAULICA", "TERMICA", "SOLAR", "EOLICA", "COGENERADOR"}
TOLERANCIA_GN04 = 0.001   # 0,1 % de diferencia relativa (propuesta, P8)
TOLERANCIA_CP04 = 1.05    # generación horaria hasta 5 % sobre la capacidad (propuesta)
MAX_REZAGO_DIAS = 2       # G-05, tentativo


def leer(carpeta: Path) -> pd.DataFrame:
    """Une los archivos anuales. Solo ubica la fila de encabezado; no cambia valores."""
    partes = []
    for f in sorted(glob.glob(str(carpeta / "*.xlsx"))):
        x = pd.read_excel(f, header=None, engine="calamine", dtype=object)
        fila = x.index[x.iloc[:, 0].astype(str).str.strip().eq("Fecha")][0]
        cuerpo = x.iloc[fila + 1:].copy()
        cuerpo.columns = [str(c).strip() if pd.notna(c) else f"_vacia_{i}" for i, c in enumerate(x.iloc[fila])]
        cuerpo = cuerpo.dropna(how="all")
        cuerpo = cuerpo.loc[:, [not c.startswith("_vacia_") or cuerpo[c].notna().any() for c in cuerpo.columns]]
        cuerpo["archivo_origen"] = Path(f).name
        partes.append(cuerpo)
    return pd.concat(partes, ignore_index=True)


def fila(tabla, regla, dimension, descripcion, evaluados, cumplen, detalle=""):
    return {"tabla": tabla, "regla": regla, "dimension": dimension, "descripcion": descripcion,
            "evaluados": int(evaluados), "cumplen": int(cumplen),
            "pct": round(100 * cumplen / evaluados, 4) if evaluados else None, "detalle": detalle}


def generacion(raiz, demanda, descarga):
    g = leer(raiz / "Generacion")
    g["fecha"] = pd.to_datetime(g["Fecha"])
    x = g[HORAS].apply(pd.to_numeric, errors="coerce")
    n = len(g)
    r = []
    r.append(fila("generacion", "GN-01", "Completitud", "Fila con las 24 horas registradas",
                  n, x.notna().all(axis=1).sum(), f"celdas horarias vacías: {int(x.isna().sum().sum())}"))
    r.append(fila("generacion", "GN-02a", "Validez", "Tipo de generación dentro de la lista",
                  n, g["Tipo Generación"].isin(TIPOS_GENERACION).sum()))
    con_valor = x.notna()
    r.append(fila("generacion", "GN-02b", "Exactitud", "Generación horaria ≥ 0 (sobre celdas con valor)",
                  con_valor.sum().sum(), (x >= 0).sum().sum()))
    # GN-04: la suma diaria de todos los recursos debe coincidir con la generación de la tabla de demanda
    diaria = x.sum(axis=1, min_count=1).groupby(g["fecha"]).sum()
    cruce = pd.concat([diaria, demanda], axis=1, keys=["gen", "dem"]).dropna()
    ok = ((cruce["gen"] / cruce["dem"] - 1).abs() <= TOLERANCIA_GN04).sum()
    r.append(fila("generacion", "GN-04", "Consistencia", "Suma diaria = generación de la tabla de Demanda (±0,1 %)",
                  len(cruce), ok, f"días cruzados: {len(cruce)}"))
    llave_plan = ["fecha", "Recurso", "Código Agente", "Version"]
    llave = llave_plan + ["Combustible"]
    dup_plan = g.duplicated(llave_plan, keep=False).sum()
    r.append(fila("generacion", "GN-03", "Unicidad", "Una fila por fecha, recurso, agente, versión y combustible",
                  n, n - g.duplicated(llave, keep=False).sum(),
                  f"con la llave del Plan (sin combustible) aparecen {int(dup_plan)} filas repetidas: plantas que usan 2 combustibles"))
    ultima = g["fecha"].max()
    r.append(fila("generacion", "G-05", "Oportunidad", f"Rezago ≤ {MAX_REZAGO_DIAS} días frente a la descarga",
                  1, int((descarga - ultima).days <= MAX_REZAGO_DIAS), f"último día: {ultima.date()}, rezago {(descarga - ultima).days} días"))
    sin_cols = g["Código Recurso"].isna().sum() if "Código Recurso" in g else n
    perfil = {"filas": n, "fecha_min": g["fecha"].min().date(), "fecha_max": ultima.date(),
              "filas_sin_codigo_recurso_es_menor_clasificacion": int(sin_cols),
              "versiones": ", ".join(sorted(g["Version"].dropna().unique()))}
    return r, perfil, g, x


def capacidad(raiz, g, xg, descarga):
    c = leer(raiz / "Capacidad")
    c["fecha"] = pd.to_datetime(c["Fecha"])
    cap = pd.to_numeric(c["Capacidad Efectiva Neta kW"], errors="coerce")
    campos = [col for col in c.columns if col not in ("archivo_origen", "fecha")]
    n = len(c)
    r = []
    r.append(fila("capacidad", "CP-01", "Completitud", "0 vacíos en los 9 campos", n, c[campos].notna().all(axis=1).sum()))
    r.append(fila("capacidad", "CP-02a", "Validez", "«Es Menor» ∈ {SI, NO}", n, c["Es Menor"].isin(["SI", "NO"]).sum()))
    r.append(fila("capacidad", "CP-02b", "Exactitud", "Capacidad efectiva neta > 0 kW", n, (cap > 0).sum()))
    # CP-04: la generación máxima horaria de un recurso no supera su capacidad del mismo día (+5 %)
    gen_max = pd.DataFrame({"fecha": g["fecha"], "Recurso": g["Recurso"], "max_h": xg.max(axis=1)})
    gen_max = gen_max.groupby(["fecha", "Recurso"])["max_h"].sum().reset_index()
    cap_dia = c.assign(cap=cap).groupby(["fecha", "Recurso"])["cap"].sum().reset_index()
    cruce = gen_max.merge(cap_dia, on=["fecha", "Recurso"], how="inner")
    ok = (cruce["max_h"] <= cruce["cap"] * TOLERANCIA_CP04).sum()
    sin_cap = len(gen_max) - len(cruce)
    peores = cruce.loc[cruce["max_h"] > cruce["cap"] * TOLERANCIA_CP04, "Recurso"].value_counts().head(3)
    r.append(fila("capacidad", "CP-04", "Consistencia", "Generación horaria máx. ≤ capacidad × 1,05 (recurso-día)",
                  len(cruce), ok,
                  f"{sin_cap} recurso-días de Generación no encuentran su recurso en Capacidad por nombre; "
                  f"más incumplimientos: {', '.join(f'{k} ({v})' for k, v in peores.items())}"))
    llave = ["fecha", "Recurso", "Código Agente"]
    r.append(fila("capacidad", "CP-03", "Unicidad", "Una fila por fecha, recurso y agente",
                  n, n - c.duplicated(llave, keep=False).sum(),
                  f"por fecha y recurso solamente: {int(c.duplicated(['fecha', 'Recurso'], keep=False).sum())} filas repetidas (mismo nombre, otro agente)"))
    ultima = c["fecha"].max()
    r.append(fila("capacidad", "G-05", "Oportunidad", f"Rezago ≤ {MAX_REZAGO_DIAS} días frente a la descarga",
                  1, int((descarga - ultima).days <= MAX_REZAGO_DIAS), f"último día: {ultima.date()}, rezago {(descarga - ultima).days} días"))
    perfil = {"filas": n, "fecha_min": c["fecha"].min().date(), "fecha_max": ultima.date(),
              "recursos_distintos": int(c["Recurso"].nunique()), "es_menor_SI": int((c["Es Menor"] == "SI").sum())}
    return r, perfil


def compras(raiz, descarga):
    b = leer(raiz / "Precio")
    b["fecha"] = pd.to_datetime(b["Fecha"], errors="coerce")
    version = b["Versión"] if "Versión" in b else pd.Series(index=b.index, dtype=object)
    if "Version" in b:
        version = version.fillna(b["Version"])
    b["version"] = version
    x = b[HORAS].apply(pd.to_numeric, errors="coerce")
    n = len(b)
    r = []
    vacias = x.isna().any(axis=1)
    por_anio = vacias.groupby(b["fecha"].dt.year).sum()
    r.append(fila("compras_bolsa", "B-04", "Completitud", "Fila con las 24 horas registradas", n, n - vacias.sum(),
                  "filas con alguna hora vacía por año: " + ", ".join(f"{a}: {int(v)}" for a, v in por_anio.items())))
    validas = b["fecha"].notna() & (b["fecha"] >= FECHA_MIN) & (b["fecha"] <= descarga)
    texto = b["Fecha"].map(lambda v: isinstance(v, str)).sum()
    r.append(fila("compras_bolsa", "G-02", "Validez", "Fecha válida, desde 2022-01-01 y no futura", n, validas.sum(),
                  f"{int(texto)} fechas vienen como texto (archivo 2026) en lugar de fecha"))
    r.append(fila("compras_bolsa", "B-03", "Exactitud", "Compras ≥ 0 kWh (sobre celdas con valor)",
                  x.notna().sum().sum(), (x >= 0).sum().sum(), f"negativos: {int((x < 0).sum().sum())}"))
    referencia = b["archivo_origen"].str.contains("2022")
    ref_cols = "Versión" in b and b.loc[referencia, "Versión"].notna().all()
    esquema_ok = b["Fecha"].map(lambda v: not isinstance(v, str)) & b.get("Versión", pd.Series(index=b.index)).notna()
    r.append(fila("compras_bolsa", "B-05 (propuesta)", "Consistencia",
                  "Mismo esquema en todos los años: fecha guardada como fecha y columna «Versión»", n, esquema_ok.sum(),
                  f"archivo 2026 con fecha como texto y columna «Version»; esquema 2022–2025 uniforme: {'sí' if ref_cols else 'no'}"))
    llave = ["fecha", "Código Agente", "version"]
    r.append(fila("compras_bolsa", "B-02", "Unicidad", "Una fila por fecha, agente y versión", n,
                  n - b.duplicated(llave, keep=False).sum()))
    ultima = b["fecha"].max()
    r.append(fila("compras_bolsa", "G-05", "Oportunidad", f"Rezago ≤ {MAX_REZAGO_DIAS} días frente a la descarga",
                  1, int((descarga - ultima).days <= MAX_REZAGO_DIAS), f"último día: {ultima.date()}, rezago {(descarga - ultima).days} días"))
    perfil = {"filas": n, "fecha_min": b["fecha"].min().date(), "fecha_max": ultima.date(),
              "agentes": int(b["Código Agente"].nunique()), "celdas_horarias_vacias": int(x.isna().sum().sum())}
    return r, perfil


def demanda_generacion(raiz):
    d = leer(raiz / "Demanda")
    return pd.to_numeric(d["Generación kWh"], errors="coerce").set_axis(pd.to_datetime(d["Fecha"]))


# Valores por defecto para correrlo con el botón ▶ de VS Code (sin argumentos).
# Cambie RAIZ_POR_DEFECTO si los datos crudos están en otra carpeta.
RAIZ_POR_DEFECTO = Path(r"C:\Users\rafae\OneDrive\Documentos\6to semestre\Data Office"
                        r"\HidrologiaYGeneracionEnergetica_7065\HidrologiaYGeneracionEnergetica")
SALIDA_POR_DEFECTO = Path(__file__).with_name("metricas_calidad_grandes.csv")


def guardar_csv(df, salida):
    """Guarda el CSV; si está abierto en Excel (Windows lo bloquea), usa otro nombre."""
    try:
        df.to_csv(salida, index=False, encoding="utf-8-sig")
        return salida
    except PermissionError:
        alterna = salida.with_name(f"{salida.stem}_{pd.Timestamp.now():%Y%m%d_%H%M%S}{salida.suffix}")
        print(f"AVISO: {salida.name} está abierto en otro programa; se guarda como {alterna.name}")
        df.to_csv(alterna, index=False, encoding="utf-8-sig")
        return alterna


def main():
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ_POR_DEFECTO
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else SALIDA_POR_DEFECTO
    descarga = pd.Timestamp(sys.argv[3] if len(sys.argv) > 3 else "2026-09-28")
    faltan = [c for c in ("Demanda", "Generacion", "Capacidad", "Precio") if not (raiz / c).is_dir()]
    if faltan:
        sys.exit(f"No encuentro las carpetas {faltan} dentro de:\n  {raiz}\n"
                 "Indique la carpeta HidrologiaYGeneracionEnergetica (la que sale al descomprimir el .rar).")
    print(f"Leyendo datos crudos de: {raiz}\n(tarda alrededor de 1 minuto)")
    dem = demanda_generacion(raiz)
    r_g, p_g, g, xg = generacion(raiz, dem, descarga)
    r_c, p_c = capacidad(raiz, g, xg, descarga)
    r_b, p_b = compras(raiz, descarga)
    metricas = pd.DataFrame(r_g + r_c + r_b)
    salida = guardar_csv(metricas, salida)
    print(f"Métricas guardadas en: {salida}")
    perfiles = {"generacion": p_g, "capacidad": p_c, "compras_bolsa": p_b}
    pd.Series({k: v for k, v in perfiles.items()}).to_json(salida.with_suffix(".perfil.json"), default_handler=str, force_ascii=False)
    print(metricas.to_string(index=False))
    print(perfiles)


if __name__ == "__main__":
    main()