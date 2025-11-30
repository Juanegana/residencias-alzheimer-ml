# src/etl.py
import pandas as pd

def load_and_clean(path="data/lista_espera.csv"):
    """Carga datos del CSV y hace limpieza sencilla."""

    df = pd.read_csv(path)

    # Renombramos columnas si vienen en mayúsculas
    df.columns = df.columns.str.lower()

    # Normalizar algunas columnas comunes
    rename_map = {
        "sexo": "sexo",
        "edad": "edad",
        "distrito": "distrito",
        "centro": "centro",
        "grado_dependencia": "dependencia"
    }

    # Reemplazar solo si existen
    for old, new in rename_map.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)

    # Limpiar valores
    if "edad" in df.columns:
        df["edad"] = pd.to_numeric(df["edad"], errors="coerce")

    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].str.strip().str.upper()

    if "distrito" in df.columns:
        df["distrito"] = df["distrito"].str.title()

    return df
