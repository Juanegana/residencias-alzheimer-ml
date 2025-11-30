import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from src import etl, graphics, model

# Inicializar app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Cargar datos y entrenar modelo
df = etl.cargar_datos()
stats = etl.obtener_estadisticas_avanzadas(df)

# Entrenar modelo ML
if not df.empty:
    model.modelo_ml.entrenar_modelo(df)

# Obtener opciones para dropdowns
distritos = ["Todos"] + sorted(df['DISTRITO_NOMBRE'].unique().tolist()) if not df.empty else ["Todos"]
edades = ["Todos"] + sorted(df['TRAMO_EDAD'].unique().tolist()) if not df.empty else ["Todos"]
sexos = ["Todos"] + sorted(df['SEXO'].unique().tolist()) if not df.empty else ["Todos"]

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🏥 Residencias Alzheimer - Madrid", 
                   className="text-center mt-4 mb-4",
                   style={'color': '#2c3e50', 'fontWeight': 'bold'}),
            html.P("Sistema de Recomendación con Machine Learning", 
                  className="text-center text-muted mb-4")
        ])
    ]),
    
    # Filtros para recomendación
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🔍 Buscar Recomendaciones Personalizadas", 
                             className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Distrito:", className="fw-bold"),
                            dcc.Dropdown(
                                id='distrito-dropdown',
                                options=[{'label': d, 'value': d} for d in distritos],
                                value='Todos',
                                placeholder="Seleccione distrito..."
                            )
                        ], width=3),
                        
                        dbc.Col([
                            html.Label("Tramo de Edad:", className="fw-bold"),
                            dcc.Dropdown(
                                id='edad-dropdown',
                                options=[{'label': e, 'value': e} for e in edades],
                                value='Todos',
                                placeholder="Seleccione edad..."
                            )
                        ], width=3),
                        
                        dbc.Col([
                            html.Label("Sexo:", className="fw-bold"),
                            dcc.Dropdown(
                                id='sexo-dropdown',
                                options=[{'label': s, 'value': s} for s in sexos],
                                value='Todos',
                                placeholder="Seleccione sexo..."
                            )
                        ], width=3),
                        
                        dbc.Col([
                            html.Label("BVD (Opcional):", className="fw-bold"),
                            dcc.Input(
                                id='bvd-input',
                                type='number',
                                placeholder='Ej: 85.5',
                                min=0,
                                max=100,
                                step=0.1
                            )
                        ], width=3),
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("🎯 Buscar Recomendaciones con ML", 
                                      id='buscar-btn', 
                                      color="primary", 
                                      size="lg",
                                      className="mt-3 w-100")
                        ], width=12)
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Resultados de recomendación
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💡 Recomendaciones Inteligentes", 
                             className="bg-success text-white"),
                dbc.CardBody([
                    html.Div(id='recomendaciones-output')
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Nueva fila de estadísticas avanzadas
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 Métricas Avanzadas"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H4(f"{stats.get('promedio_dias_espera', 0):.0f}", 
                                   className="text-primary"),
                            html.P("Días promedio en espera", className="text-muted")
                        ], width=3),
                        dbc.Col([
                            html.H4(f"{stats.get('promedio_bvd', 0):.1f}", 
                                   className="text-success"),
                            html.P("BVD Promedio", className="text-muted")
                        ], width=3),
                        dbc.Col([
                            html.H4(f"{stats.get('mediana_bvd', 0):.1f}", 
                                   className="text-info"),
                            html.P("BVD Mediano", className="text-muted")
                        ], width=3),
                        dbc.Col([
                            html.H4(f"{stats.get('distritos_unicos', 0)}", 
                                   className="text-warning"),
                            html.P("Distritos cubiertos", className="text-muted")
                        ], width=3),
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Gráficos principales
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-distritos')
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id='grafico-evolucion')
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-tiempo-espera')
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id='grafico-bvd-espera')
        ], width=6),
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Sistema desarrollado con Dash y Machine Learning | Datos: Ayuntamiento de Madrid", 
                  className="text-center text-muted mt-4")
        ])
    ])
], fluid=True)

# Callbacks actualizados
@app.callback(
    [Output('grafico-distritos', 'figure'),
     Output('grafico-evolucion', 'figure'),
     Output('grafico-tiempo-espera', 'figure'),
     Output('grafico-bvd-espera', 'figure')],
    [Input('buscar-btn', 'n_clicks')]
)
def actualizar_graficos(n_clicks):
    return (graphics.crear_grafico_distritos(df),
            graphics.crear_grafico_evolucion_temporal(df),
            graphics.crear_grafico_tiempo_espera(df),
            graphics.crear_grafico_bvd_vs_espera(df))

@app.callback(
    Output('recomendaciones-output', 'children'),
    [Input('buscar-btn', 'n_clicks')],
    [Input('distrito-dropdown', 'value'),
     Input('edad-dropdown', 'value'),
     Input('sexo-dropdown', 'value'),
     Input('bvd-input', 'value')]
)
def generar_recomendaciones(n_clicks, distrito, edad, sexo, bvd):
    if n_clicks is None:
        return dbc.Alert("👆 Seleccione criterios y haga clic en 'Buscar Recomendaciones con ML'", 
                        color="info")
    
    recomendaciones = model.recomendar_residencia(df, distrito, edad, sexo, bvd)
    
    if isinstance(recomendaciones, str):
        return dbc.Alert(recomendaciones, color="warning")
    
    # Mostrar recomendaciones en tarjetas mejoradas
    cards = []
    for i, rec in enumerate(recomendaciones, 1):
        # Color basado en el tiempo de espera
        if rec['TIEMPO_ESPERA_DIAS'] < 30:
            color = "success"
        elif rec['TIEMPO_ESPERA_DIAS'] < 60:
            color = "warning"
        else:
            color = "danger"
        
        card = dbc.Card([
            dbc.CardHeader(f"🏆 Recomendación #{i}"),
            dbc.CardBody([
                html.H5(f"Distrito: {rec['DISTRITO_NOMBRE']}", className="card-title"),
                dbc.ListGroup([
                    dbc.ListGroupItem(f"📊 BVD: {rec['BVD']:.2f}"),
                    dbc.ListGroupItem(f"👵 Edad: {rec['TRAMO_EDAD']}"),
                    dbc.ListGroupItem(f"👤 Sexo: {rec['SEXO']}"),
                    dbc.ListGroupItem([
                        html.Span("⏱️ Tiempo estimado de espera: "),
                        html.Span(f"{rec['TIEMPO_ESPERA_DIAS']} días", 
                                 className=f"text-{color} fw-bold")
                    ])
                ], flush=True)
            ])
        ], color=color, outline=True, className="mb-3")
        cards.append(card)
    
    return html.Div(cards)

if __name__ == "__main__":
    app.run(debug=True)