"""Orquestador de HidroData SIN: ejecuta ingesta, normalización y calidad en orden.

Uso: python run_pipeline.py
"""

import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
# Cada paso se ejecuta como script independiente, igual que a mano; limpieza.py lo importa normalizacion.py
PASOS = [("Ingesta", "src/ingesta.py"), ("Normalización", "src/normalizacion.py"), ("Calidad", "src/calidad.py")]
SALIDAS = ["data/processed/ingesta", "data/processed/normalizado", "data/processed/calidad"]

inicio_total = time.time()
for nombre, script in PASOS:
    print(f"\n===== PASO: {nombre} ({script}) =====", flush=True)
    inicio = time.time()
    # sys.executable usa el mismo intérprete (y entorno virtual) con el que se lanzó el orquestador
    resultado = subprocess.run([sys.executable, str(RAIZ / script)], cwd=RAIZ)
    if resultado.returncode != 0:
        # Se detiene aquí: los pasos siguientes dependen de las salidas de este
        sys.exit(f"\nERROR: el paso '{nombre}' falló (código {resultado.returncode}). Pipeline detenido.")
    print(f"===== {nombre} terminado en {time.time() - inicio:.1f} s =====", flush=True)

print(f"\nPipeline completo en {time.time() - inicio_total:.1f} s. Salidas:")
for carpeta in SALIDAS:
    print(f"  - {carpeta}")
