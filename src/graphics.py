import plotly.express as px

def create_feature_importance_fig(model, feature_names):
    importances = model.feature_importances_
    fig = px.bar(
        x=importances,
        y=feature_names,
        orientation="h",
        title="Importancia de las variables"
    )
    return fig


def create_histogram_fig(df):
    # Primera columna numérica del dataset para ejemplo
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols) == 0:
        return None

    fig = px.histogram(df, x=numeric_cols[0], title=f"Distribución de {numeric_cols[0]}")
    return fig
