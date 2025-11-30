import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from src import etl, graphics, model

# Inicializar app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Cargar datos
df = etl.cargar_datos()
stats = etl.obtener_estadisticas_basicas(df)

# Obtener opciones para dropdowns
distritos = ["Todos"] + sorted(df['DISTRITO_NOMBRE'].unique().tolist()) if not df.empty else ["Todos"]
edades = ["Todos"] + sorted(df['TRAMO_EDAD'].unique().tolist()) if not df.empty else ["Todos"]
sexos = ["Todos"] + sorted(df['SEXO'].unique().tolist()) if not df.empty else ["Todos"]

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🏥 Residencias Alzheimer Madrid", 
                   className="text-center mt-4 mb-4",
                   style={'color': '#2c3e50'})
        ])
    ]),
    
    # Estadísticas rápidas
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{stats.get('total_personas', 0)}", className="card-title"),
                    html.P("Personas en lista de espera", className="card-text")
                ])
            ], color="primary", inverse=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{stats.get('distritos_unicos', 0)}", className="card-title"),
                    html.P("Distritos", className="card-text")
                ])
            ], color="success", inverse=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{stats.get('distribucion_sexo', {}).get('MUJER', 0)}", className="card-title"),
                    html.P("Mujeres", className="card-text")
                ])
            ], color="info", inverse=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{stats.get('distribucion_sexo', {}).get('HOMBRE', 0)}", className="card-title"),
                    html.P("Hombres", className="card-text")
                ])
            ], color="warning", inverse=True)
        ], width=3),
    ], className="mb-4"),
    
    # Filtros para recomendación
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🔍 Buscar Recomendaciones"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Distrito:"),
                            dcc.Dropdown(
                                id='distrito-dropdown',
                                options=[{'label': d, 'value': d} for d in distritos],
                                value='Todos'
                            )
                        ], width=4),
                        
                        dbc.Col([
                            html.Label("Tramo de Edad:"),
                            dcc.Dropdown(
                                id='edad-dropdown',
                                options=[{'label': e, 'value': e} for e in edades],
                                value='Todos'
                            )
                        ], width=4),
                        
                        dbc.Col([
                            html.Label("Sexo:"),
                            dcc.Dropdown(
                                id='sexo-dropdown',
                                options=[{'label': s, 'value': s} for s in sexos],
                                value='Todos'
                            )
                        ], width=4),
                    ]),
                    
                    dbc.Button("Buscar Recomendaciones", 
                              id='buscar-btn', 
                              color="primary", 
                              className="mt-3")
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Resultados de recomendación
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💡 Recomendaciones"),
                dbc.CardBody([
                    html.Div(id='recomendaciones-output')
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Gráficos
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-distritos')
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id='grafico-edad')
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-sexo')
        ], width=12)
    ])
], fluid=True)

# Callbacks
@app.callback(
    [Output('grafico-distritos', 'figure'),
     Output('grafico-edad', 'figure'),
     Output('grafico-sexo', 'figure')],
    [Input('buscar-btn', 'n_clicks')]
)
def actualizar_graficos(n_clicks):
    return (graphics.crear_grafico_distritos(df),
            graphics.crear_grafico_edad(df),
            graphics.crear_grafico_sexo(df))

@app.callback(
    Output('recomendaciones-output', 'children'),
    [Input('buscar-btn', 'n_clicks')],
    [Input('distrito-dropdown', 'value'),
     Input('edad-dropdown', 'value'),
     Input('sexo-dropdown', 'value')]
)
def generar_recomendaciones(n_clicks, distrito, edad, sexo):
    if n_clicks is None:
        return "Seleccione criterios y haga clic en 'Buscar Recomendaciones'"
    
    recomendaciones = model.recomendar_residencia(df, distrito, edad, sexo)
    
    if isinstance(recomendaciones, str):
        return html.P(recomendaciones)
    
    # Mostrar recomendaciones en tarjetas
    cards = []
    for i, rec in enumerate(recomendaciones, 1):
        card = dbc.Card([
            dbc.CardBody([
                html.H5(f"Recomendación #{i}", className="card-title"),
                html.P(f"Distrito: {rec['DISTRITO_NOMBRE']}"),
                html.P(f"Puntuación BVD: {rec['BVD']:.2f}"),
                html.P(f"Edad: {rec['TRAMO_EDAD']}"),
                html.P(f"Sexo: {rec['SEXO']}")
            ])
        ], className="mb-2")
        cards.append(card)
    
    return html.Div(cards)

if __name__ == "__main__":
    app.run(debug=True)