import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime

# Inicializar app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Cargar datos
try:
    df = pd.read_csv('data/lista_espera.csv', sep=';', encoding='utf-8')
    # Limpieza básica
    df['BVD'] = pd.to_numeric(df['BVD'], errors='coerce')
    df['FECHA_DE_ENTRADA'] = pd.to_datetime(df['FECHA_DE_ENTRADA'])
    df['DISTRITO_NOMBRE'] = df['DISTRITO'].str.strip()
    
    # Calcular días en espera (simulado)
    fecha_referencia = pd.to_datetime('2025-10-26')
    df['DIAS_EN_ESPERA'] = (fecha_referencia - df['FECHA_DE_ENTRADA']).dt.days
    
    # Estadísticas
    stats = {
        'promedio_dias_espera': df['DIAS_EN_ESPERA'].mean(),
        'promedio_bvd': df['BVD'].mean(),
        'mediana_bvd': df['BVD'].median(),
        'distritos_unicos': df['DISTRITO_NOMBRE'].nunique()
    }
    
    # Opciones para dropdowns
    distritos = ["Todos"] + sorted(df['DISTRITO_NOMBRE'].unique().tolist())
    edades = ["Todos"] + sorted(df['TRAMO_EDAD'].unique().tolist())
    sexos = ["Todos"] + sorted(df['SEXO'].unique().tolist())
    
except Exception as e:
    print(f"Error cargando datos: {e}")
    df = pd.DataFrame()
    stats = {'promedio_dias_espera': 0, 'promedio_bvd': 0, 'mediana_bvd': 0, 'distritos_unicos': 0}
    distritos = edades = sexos = ["Todos"]

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🏥 Residencias Alzheimer - Madrid", 
                   className="text-center mt-4 mb-4",
                   style={'color': '#2c3e50', 'fontWeight': 'bold'}),
            html.P("Sistema de Recomendación (Versión simplificada)", 
                  className="text-center text-muted mb-4"),
            html.P("✅ Funcionando en Render ✅", 
                  className="text-center text-success fw-bold")
        ])
    ]),
    
    # Filtros
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🔍 Buscar Recomendaciones", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.Label("Distrito:", className="fw-bold"),
                                dcc.Dropdown(id='distrito-dropdown', options=[{'label': d, 'value': d} for d in distritos], value='Todos')], width=4),
                        dbc.Col([html.Label("Edad:", className="fw-bold"),
                                dcc.Dropdown(id='edad-dropdown', options=[{'label': e, 'value': e} for e in edades], value='Todos')], width=4),
                        dbc.Col([html.Label("Sexo:", className="fw-bold"),
                                dcc.Dropdown(id='sexo-dropdown', options=[{'label': s, 'value': s} for s in sexos], value='Todos')], width=4),
                    ]),
                    dbc.Button("🎯 Buscar Recomendaciones", id='buscar-btn', color="primary", className="mt-3 w-100", n_clicks=0)
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Resultados
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💡 Recomendaciones", className="bg-success text-white"),
                dbc.CardBody(id='recomendaciones-output', children=[
                    dbc.Alert("👆 Seleccione criterios y haga clic en Buscar", color="info")
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Estadísticas
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 Métricas"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.H4(f"{stats['promedio_dias_espera']:.0f}", className="text-primary"), html.P("Días promedio espera")], width=3),
                        dbc.Col([html.H4(f"{stats['promedio_bvd']:.1f}", className="text-success"), html.P("BVD Promedio")], width=3),
                        dbc.Col([html.H4(f"{stats['mediana_bvd']:.1f}", className="text-info"), html.P("BVD Mediano")], width=3),
                        dbc.Col([html.H4(f"{stats['distritos_unicos']}", className="text-warning"), html.P("Distritos")], width=3),
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Gráficos
    dbc.Row([
        dbc.Col([dcc.Graph(id='grafico-distritos')], width=6),
        dbc.Col([dcc.Graph(id='grafico-bvd')], width=6),
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Sistema desarrollado con Dash | Datos: Ayuntamiento de Madrid | Versión básica para Render", 
                  className="text-center text-muted mt-4")
        ])
    ])
], fluid=True)

# Callbacks
@app.callback(
    [Output('grafico-distritos', 'figure'),
     Output('grafico-bvd', 'figure')],
    [Input('buscar-btn', 'n_clicks')]
)
def actualizar_graficos(n_clicks):
    if df.empty:
        empty = px.bar(x=[], y=[], title='No hay datos')
        return empty, empty
    
    # Gráfico 1: Distribución por distrito
    dist_counts = df['DISTRITO_NOMBRE'].value_counts().reset_index()
    fig1 = px.bar(dist_counts.head(10), x='DISTRITO_NOMBRE', y='count', 
                  title='Top 10 Distritos', labels={'DISTRITO_NOMBRE': 'Distrito', 'count': 'Pacientes'})
    
    # Gráfico 2: Distribución de BVD
    fig2 = px.histogram(df, x='BVD', title='Distribución de BVD', nbins=20)
    
    return fig1, fig2

@app.callback(
    Output('recomendaciones-output', 'children'),
    [Input('buscar-btn', 'n_clicks')],
    [State('distrito-dropdown', 'value'),
     State('edad-dropdown', 'value'),
     State('sexo-dropdown', 'value')]
)
def generar_recomendaciones(n_clicks, distrito, edad, sexo):
    if n_clicks == 0 or df.empty:
        return dbc.Alert("👆 Seleccione criterios y haga clic en Buscar", color="info")
    
    # Filtrar
    filtrado = df.copy()
    if distrito != "Todos":
        filtrado = filtrado[filtrado['DISTRITO_NOMBRE'] == distrito]
    if edad != "Todos":
        filtrado = filtrado[filtrado['TRAMO_EDAD'] == edad]
    if sexo != "Todos":
        filtrado = filtrado[filtrado['SEXO'] == sexo]
    
    if filtrado.empty:
        return dbc.Alert("No se encontraron coincidencias", color="warning")
    
    # Tomar top 3 por BVD
    top3 = filtrado.nlargest(3, 'BVD')
    
    cards = []
    for i, (_, row) in enumerate(top3.iterrows(), 1):
        card = dbc.Card([
            dbc.CardHeader(f"Recomendación #{i}"),
            dbc.CardBody([
                html.H5(f"Distrito: {row['DISTRITO_NOMBRE']}"),
                html.P(f"BVD: {row['BVD']:.2f}"),
                html.P(f"Edad: {row['TRAMO_EDAD']}"),
                html.P(f"Sexo: {row['SEXO']}"),
                html.P(f"Días en espera: {row['DIAS_EN_ESPERA']}")
            ])
        ], className="mb-3")
        cards.append(card)
    
    return html.Div(cards)

if __name__ == "__main__":
    app.run(debug=True)