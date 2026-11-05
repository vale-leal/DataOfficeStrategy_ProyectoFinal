"""Etapa 2 - Ingesta: lee los .xlsx de data/raw/<Coleccion>/, une los años y guarda un parquet por colección.

No limpia ni transforma: todo se guarda como texto tal como viene en Excel.
Uso: python src/ingesta.py
"""

import re
import time
from pathlib import Path

import pandas as pd

# Rutas relativas a la raíz del repo, para que funcione sin importar desde dónde se ejecute
RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_SALIDA = RAIZ / "data" / "processed" / "ingesta"

FILAS_A_REVISAR = 15  # el encabezado siempre está entre las primeras filas
UMBRAL_ANCHO = 0.8    # el encabezado ocupa casi todo el ancho; los títulos, una o dos celdas


def detectar_fila_encabezado(crudo):
    """Devuelve el índice (base 0) de la primera fila con al menos el 80% del ancho máximo."""
    no_nulas = crudo.head(FILAS_A_REVISAR).notna().sum(axis=1)
    minimo = UMBRAL_ANCHO * no_nulas.max()
    # idxmax sobre un booleano devuelve la primera fila que cumple la condición
    return (no_nulas >= minimo).idxmax()


def nombres_columnas(fila):
    """Convierte la fila de encabezado en nombres de columna de texto, sin espacios sobrantes."""
    nombres = []
    for posicion, valor in enumerate(fila):
        nombre = "" if pd.isna(valor) else str(valor).strip()
        # Una celda vacía en el encabezado (p. ej. por celdas combinadas) necesita un nombre único
        nombres.append(nombre if nombre else f"sin_nombre_{posicion}")
    return nombres


def leer_archivo(ruta):
    """Lee un .xlsx una sola vez y devuelve (tabla, fila del encabezado en Excel)."""
    # header=None: el encabezado no está en la fila 1; dtype=str: no mezclar tipos entre años
    crudo = pd.read_excel(ruta, header=None, dtype=str)
    fila = detectar_fila_encabezado(crudo)
    tabla = crudo.iloc[fila + 1:].copy()
    tabla.columns = nombres_columnas(crudo.iloc[fila])
    # Las filas totalmente vacías (separadores al final de la hoja) no son registros
    tabla = tabla.dropna(how="all").reset_index(drop=True)
    tabla["archivo_origen"] = ruta.name
    tabla["anio_archivo"] = re.search(r"20\d\d", ruta.name).group(0)
    # +1 porque Excel numera las filas desde 1
    return tabla, fila + 1


def ordenar_por_anio(archivos):
    """Ordena los archivos por el año de su nombre (los nombres no siempre comparten prefijo)."""
    return sorted(archivos, key=lambda ruta: re.search(r"20\d\d", ruta.name).group(0))


def ingestar_coleccion(carpeta):
    """Lee todos los años de una colección, los une y guarda el parquet; devuelve la tabla unida."""
    coleccion = carpeta.name
    tablas = []
    columnas_anteriores = None
    for ruta in ordenar_por_anio(carpeta.glob("*.xlsx")):
        inicio = time.time()
        tabla, fila_encabezado = leer_archivo(ruta)
        segundos = time.time() - inicio
        print(f"{coleccion} | {ruta.name} | fila encabezado {fila_encabezado} | "
              f"{len(tabla)} filas | {tabla.shape[1]} columnas | {segundos:.1f} s")
        # Comparar con el año anterior permite ver la deriva de esquema en el momento de leer
        columnas = set(tabla.columns)
        if columnas_anteriores is not None and columnas != columnas_anteriores:
            anadidas = sorted(columnas - columnas_anteriores)
            eliminadas = sorted(columnas_anteriores - columnas)
            print(f"  CAMBIO DE COLUMNAS: añadidas {anadidas} eliminadas {eliminadas}")
        columnas_anteriores = columnas
        tablas.append(tabla)

    # concat alinea por nombre de columna; lo que no existe en un año queda nulo
    unida = pd.concat(tablas, ignore_index=True)
    unida.to_parquet(DIR_SALIDA / f"{coleccion}.parquet", index=False)
    return unida


def main():
    """Recorre cada subcarpeta de data/raw como una colección e imprime el resumen final."""
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    resumen = []
    # El nombre de la colección sale de la carpeta, no de una lista fija
    for carpeta in sorted(p for p in DIR_RAW.iterdir() if p.is_dir()):
        unida = ingestar_coleccion(carpeta)
        resumen.append((carpeta.name, len(unida), unida.shape[1]))
        print()

    print("RESUMEN")
    print(f"{'colección':<12} | {'filas totales':>13} | columnas")
    for coleccion, filas, columnas in resumen:
        print(f"{coleccion:<12} | {filas:>13} | {columnas}")


if __name__ == "__main__":
    main()
