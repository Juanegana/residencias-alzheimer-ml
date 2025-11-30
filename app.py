# app.py
import dash
from dash import html, dcc, Input, Output
import dash_table

from src.etl import load_and_clean
from src.model import recommend_residence
from src.graphics import plot_age_distribution, plot_district_distribution

# --- Cargar CSV ---
df = load_and_clean()

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Recomendador de Residencias Alzheimer – Madrid"),
    html.P("Datos cargados desde un archivo CSV local."),

    html.Div([
        html.Label("Edad:"),
        dcc.Input(id="input-edad", type="number", value=80),

        html.Br(), html.Br(),

        html.Label("Sexo:"),
        dcc.Dropdown(
            id="input-sexo",
            options=[{"label": s, "value": s} for s in sorted(df["sexo"].dropna().unique())]
            if "sexo" in df.columns else [],
            value=None
        ),

        html.Br(),

        html.Label("Distrito:"),
        dcc.Dropdown(
            id="input-distrito",
            options=[{"label": d, "value": d} for d in sorted(df["distrito"].dropna().unique())]
            if "distrito" in df.columns else [],
            value=None
        ),

        html.Br(), html.H3("Residencia recomendada:"),
        html.Div(id="output-reco", style={"fontWeight": "bold", "fontSize": "22px"}),

        html.Hr(),

        html.H3("Tabla de datos"),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=12,
            style_table={"overflowX": "auto"}
        ),

        html.Hr(),

        html.H3("Gráficas"),
        dcc.Graph(id="graf-edad"),
        dcc.Graph(id="graf-distrito")
    ])
])

# --- CALLBACK RECOMENDACIÓN ---
@app.callback(
    Output("output-reco", "children"),
    Input("input-edad", "value"),
    Input("input-distrito", "value"),
    Input("input-sexo", "value")
)
def actualizar_reco(edad, distrito, sexo):
    reco = recommend_residence(df, edad, distrito, sexo)
    return reco

# --- CALLBACK GRÁFICAS ---
@app.callback(
    Output("graf-edad", "figure"),
    Output("graf-distrito", "figure"),
    Input("input-distrito", "value")
)
def actualizar_graficos(_):
    return plot_age_distribution(df), plot_district_distribution(df)

if __name__ == "__main__":
    app.run(debug=True)
