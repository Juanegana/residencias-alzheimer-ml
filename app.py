import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd

from src.etl import load_data
from src.model import train_model, predict_wait_time
from src.graphics import create_feature_importance_fig, create_histogram_fig


# --------- CARGA DE DATOS ---------
df = load_data("lista_espera.csv")

model, feature_cols = train_model(df)

# --------- DASH APP ---------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Predicción Lista de Espera - Centros Alzheimer"),

    html.H2("Datos cargados"),
    dash_table.DataTable(
        data=df.head(10).to_dict("records"),
        page_size=10,
    ),

    html.H2("Gráfica de importancia de variables"),
    dcc.Graph(
        figure=create_feature_importance_fig(model, feature_cols)
    ),

    html.H2("Distribución de una variable"),
    dcc.Graph(
        figure=create_histogram_fig(df)
    ),

    html.H2("Predicción"),
    html.Div([
        html.P("Introduce valores para predecir:"),

        *[
            html.Div([
                html.Label(col),
                dcc.Input(id=f"input-{col}", type="number", step=1)
            ])
            for col in feature_cols
        ],

        html.Button("Predecir", id="btn-predict"),
        html.Div(id="prediction-output", style={"marginTop": "20px", "fontSize": "20px"})
    ])
])


@app.callback(
    Output("prediction-output", "children"),
    Input("btn-predict", "n_clicks"),
    [
        State(f"input-{col}", "value")
        for col in feature_cols
    ]
)
def make_prediction(n, *values):
    if not n:
        return ""

    values_dict = {col: val for col, val in zip(feature_cols, values)}

    pred = predict_wait_time(values_dict)

    return f"Predicción estimada: {pred:.2f}"


if __name__ == "__main__":
    app.run_server(debug=True)
