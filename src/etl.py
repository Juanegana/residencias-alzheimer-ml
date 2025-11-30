import pandas as pd

def load_data(path="lista_espera.csv"):
    """Carga el CSV y hace una limpieza mínima."""
    df = pd.read_csv(path)

    # Limpieza básica (ajústala según el dataset real)
    df = df.dropna()

    return df
