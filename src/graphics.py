# src/graphics.py
import plotly.express as px

def plot_age_distribution(df):
    if "edad" not in df.columns:
        return {}
    return px.histogram(df, x="edad", nbins=20, title="Distribución de edades")

def plot_district_distribution(df):
    if "distrito" not in df.columns:
        return {}
    return px.bar(df["distrito"].value_counts(), title="Personas en lista por distrito")
