"""Consolida los Excel crudos de XM por colección, sin modificar valores (solo detecta la fila de encabezado)."""
import glob, sys
import pandas as pd

RAW, OUT = sys.argv[1], sys.argv[2]
CARPETAS = {"aportes": "Aportes", "reservas": "Reservas", "demanda": "Demanda", "vertimientos": "Vertimentos",
            "generacion": "Generacion", "capacidad": "Capacidad", "compras_bolsa": "Precio"}
for nombre, carpeta in CARPETAS.items():
    partes = []
    for f in sorted(glob.glob(f"{RAW}/{carpeta}/*.xlsx")):
        x = pd.read_excel(f, header=None, engine="calamine", dtype=object)
        fila = x.index[x.iloc[:, 0].astype(str).str.strip().eq("Fecha") | x.iloc[:, 0].astype(str).str.strip().eq("Año")][0]
        titulo = " | ".join(str(v) for v in x.iloc[:fila].stack().dropna().tolist())
        cuerpo = x.iloc[fila + 1:].copy()
        cuerpo.columns = [str(c).strip() if pd.notna(c) else f"_vacia_{i}" for i, c in enumerate(x.iloc[fila])]
        cuerpo = cuerpo.dropna(how="all")
        cuerpo = cuerpo.loc[:, ~cuerpo.columns.str.startswith("_vacia_") | cuerpo.notna().any()]
        cuerpo["archivo_origen"] = f.split("/")[-1]
        partes.append(cuerpo)
        print(nombre, f.split("/")[-1], "titulo:", titulo, "| filas:", len(cuerpo), flush=True)
    df = pd.concat(partes, ignore_index=True)
    df.to_pickle(f"{OUT}/{nombre}.pkl")
    print("==>", nombre, df.shape, list(df.columns), flush=True)
