# src/model.py

def recommend_residence(df, edad, distrito, sexo):
    """
    Recomendación mínima: filtrar por distrito y sugerir el centro más frecuente.
    """

    filtered = df.copy()

    if distrito and ("distrito" in df.columns):
        filtered = filtered[filtered["distrito"] == distrito]

    if filtered.empty:
        return "No hay datos suficientes."

    if "centro" not in filtered.columns:
        return "No disponible"

    return filtered["centro"].value_counts().idxmax()
