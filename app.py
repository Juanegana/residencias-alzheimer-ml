import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

# Importar módulos personalizados
from src.etl import cargar_datos, obtener_estadisticas_avanzadas, cargar_o_entrenar_modelo
from src.graphics import (
    crear_grafico_distritos, crear_grafico_edad, crear_grafico_sexo,
    crear_grafico_evolucion_temporal, crear_grafico_tiempo_espera,
    crear_grafico_bvd_vs_espera, crear_grafico_top_distritos
)
from src.model import recomendar_residencia

# Inicializar app
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
server = app.server

# Cargar datos
df = cargar_datos()
print(f"Datos cargados: {len(df)} registros")

# Cargar o entrenar modelo
modelo_ml, stats = cargar_o_entrenar_modelo(df)

# Opciones para dropdowns
distritos = ["Todos"] + sorted(df['DISTRITO_NOMBRE'].unique().tolist()) if not df.empty else ["Todos"]
edades = ["Todos"] + sorted(df['TRAMO_EDAD'].unique().tolist()) if not df.empty else ["Todos"]
sexos = ["Todos"] + sorted(df['SEXO'].unique().tolist()) if not df.empty else ["Todos"]

# Layout principal
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🏥 Residencias Alzheimer - Madrid", 
                   className="text-center mt-4 mb-3",
                   style={'color': '#2c3e50', 'fontWeight': 'bold'}),
            html.P("Sistema de Recomendación Inteligente con Machine Learning", 
                  className="text-center text-muted mb-3"),
            dbc.Badge("✅ DEPLOY EN RENDER", color="success", className="mb-4 mx-2"),
            dbc.Badge("🤖 ML ACTIVADO", color="info", className="mb-4 mx-2"),
            dbc.Badge(f"📊 {len(df)} REGISTROS", color="warning", className="mb-4 mx-2")
        ])
    ]),
    
    # Tabs para diferentes secciones
    dbc.Tabs([
        # Tab 1: Recomendaciones ML
        dbc.Tab(label="🤖 Recomendaciones ML", tab_id="tab-recomendaciones", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🔍 Configurar Búsqueda Inteligente", className="bg-primary text-white"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Distrito:", className="fw-bold mb-2"),
                                    dcc.Dropdown(
                                        id='distrito-dropdown',
                                        options=[{'label': d, 'value': d} for d in distritos],
                                        value='Todos',
                                        placeholder="Seleccione distrito..."
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Tramo de Edad:", className="fw-bold mb-2"),
                                    dcc.Dropdown(
                                        id='edad-dropdown',
                                        options=[{'label': e, 'value': e} for e in edades],
                                        value='Todos',
                                        placeholder="Seleccione edad..."
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Sexo:", className="fw-bold mb-2"),
                                    dcc.Dropdown(
                                        id='sexo-dropdown',
                                        options=[{'label': s, 'value': s} for s in sexos],
                                        value='Todos',
                                        placeholder="Seleccione sexo..."
                                    )
                                ], width=4),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("BVD Mínimo:", className="fw-bold mb-2"),
                                    dcc.Slider(
                                        id='bvd-slider',
                                        min=0,
                                        max=100,
                                        step=5,
                                        value=0,
                                        marks={i: str(i) for i in range(0, 101, 20)},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=12),
                            ]),
                            dbc.Button(
                                "🎯 Generar Recomendaciones Inteligentes", 
                                id='buscar-btn', 
                                color="primary", 
                                className="mt-4 w-100 py-2",
                                n_clicks=0
                            )
                        ])
                    ], className="mb-4")
                ])
            ]),
            
            # Resultados de ML
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("💡 Recomendaciones con Predicción ML", className="bg-success text-white"),
                        dbc.CardBody(id='recomendaciones-output', children=[
                            dbc.Alert(
                                "👆 Configure los filtros y haga clic en 'Generar Recomendaciones Inteligentes'",
                                color="info",
                                className="text-center"
                            )
                        ])
                    ])
                ])
            ]),
        ]),
        
        # Tab 2: Análisis de Datos
        dbc.Tab(label="📊 Análisis de Datos", tab_id="tab-analisis", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📈 Métricas Principales", className="bg-info text-white"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4(f"{stats.get('total_personas', 0):,}", className="text-primary text-center"),
                                            html.P("Personas en lista", className="text-center text-muted")
                                        ])
                                    ])
                                ], width=2),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4(f"{stats.get('promedio_dias_espera', 0):.0f}", className="text-success text-center"),
                                            html.P("Días promedio espera", className="text-center text-muted")
                                        ])
                                    ])
                                ], width=2),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4(f"{stats.get('promedio_bvd', 0):.1f}", className="text-warning text-center"),
                                            html.P("BVD Promedio", className="text-center text-muted")
                                        ])
                                    ])
                                ], width=2),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4(f"{stats.get('distritos_unicos', 0)}", className="text-danger text-center"),
                                            html.P("Distritos", className="text-center text-muted")
                                        ])
                                    ])
                                ], width=2),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4(f"{stats.get('mediana_bvd', 0):.1f}", className="text-info text-center"),
                                            html.P("BVD Mediano", className="text-center text-muted")
                                        ])
                                    ])
                                ], width=2),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4(f"{df['MES_ENTRADA'].nunique() if len(df) > 0 else 0}", className="text-secondary text-center"),
                                            html.P("Meses analizados", className="text-center text-muted")
                                        ])
                                    ])
                                ], width=2),
                            ])
                        ])
                    ], className="mb-4")
                ])
            ]),
            
            # Gráficos principales
            dbc.Row([
                dbc.Col([dcc.Graph(id='grafico-distritos')], width=6),
                dbc.Col([dcc.Graph(id='grafico-evolucion')], width=6),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='grafico-bvd-espera')], width=6),
                dbc.Col([dcc.Graph(id='grafico-tiempo-espera')], width=6),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([dcc.Graph(id='grafico-edad')], width=6),
                dbc.Col([dcc.Graph(id='grafico-sexo')], width=6),
            ]),
        ]),
        
        # Tab 3: Información del Modelo
        dbc.Tab(label="🧠 Modelo ML", tab_id="tab-modelo", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🤖 Información del Modelo de Machine Learning", className="bg-dark text-white"),
                        dbc.CardBody([
                            html.H4("Random Forest Regressor", className="text-primary"),
                            html.P("""
                                Este modelo predice el tiempo de espera estimado (en días) para cada paciente 
                                basándose en sus características demográficas y el Baremo de Valoración de la Dependencia (BVD).
                            """),
                            
                            html.H5("Características utilizadas:", className="mt-4"),
                            html.Ul([
                                html.Li("Distrito de residencia"),
                                html.Li("Tramo de edad"),
                                html.Li("Sexo"),
                                html.Li("Baremo de Valoración de la Dependencia (BVD)")
                            ]),
                            
                            html.H5("Métricas del modelo:", className="mt-4"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5("100", className="text-center text-success"),
                                            html.P("Árboles en el bosque", className="text-center")
                                        ])
                                    ])
                                ], width=4),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5(f"{len(df)}", className="text-center text-info"),
                                            html.P("Registros de entrenamiento", className="text-center")
                                        ])
                                    ])
                                ], width=4),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H5("4", className="text-center text-warning"),
                                            html.P("Características principales", className="text-center")
                                        ])
                                    ])
                                ], width=4),
                            ]),
                            
                            html.H5("Cómo funciona:", className="mt-4"),
                            html.P("""
                                El modelo analiza patrones históricos de asignación de plazas para predecir 
                                cuántos días podría esperar un paciente con características específicas. 
                                Las recomendaciones se priorizan combinando el BVD (mayor necesidad) con 
                                el tiempo de espera predicho (menor espera estimada).
                            """),
                            
                            html.Div(id='modelo-status', className="mt-4")
                        ])
                    ])
                ])
            ])
        ]),
        
        # Tab 4: Datos Crudos
        dbc.Tab(label="📋 Datos", tab_id="tab-datos", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Vista de Datos", className="bg-secondary text-white"),
                        dbc.CardBody([
                            html.Div(id='tabla-datos-container')
                        ])
                    ])
                ])
            ])
        ])
    ], id="tabs", active_tab="tab-recomendaciones", className="mt-4"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P(
                "Sistema desarrollado con Dash | Modelo ML: Random Forest | "
                "Datos: Ayuntamiento de Madrid | Deploy: Render",
                className="text-center text-muted mt-4 small"
            ),
            html.P(
                "Versión 2.0 - Sistema Inteligente de Recomendación",
                className="text-center text-muted mb-4 small"
            )
        ])
    ])
], fluid=True, style={'padding': '20px'})

# Callbacks

@app.callback(
    [Output('grafico-distritos', 'figure'),
     Output('grafico-evolucion', 'figure'),
     Output('grafico-bvd-espera', 'figure'),
     Output('grafico-tiempo-espera', 'figure'),
     Output('grafico-edad', 'figure'),
     Output('grafico-sexo', 'figure')],
    [Input('tabs', 'active_tab')]
)
def actualizar_graficos(active_tab):
    """Actualiza todos los gráficos cuando se cambia a la pestaña de análisis"""
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No hay datos disponibles", showarrow=False)
        return [empty_fig] * 6
    
    try:
        fig1 = crear_grafico_top_distritos(df)  # Usamos el top 10
        fig2 = crear_grafico_evolucion_temporal(df)
        fig3 = crear_grafico_bvd_vs_espera(df)
        fig4 = crear_grafico_tiempo_espera(df)
        fig5 = crear_grafico_edad(df)
        fig6 = crear_grafico_sexo(df)
        
        return fig1, fig2, fig3, fig4, fig5, fig6
    except Exception as e:
        print(f"Error creando gráficos: {e}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Error: {str(e)}", showarrow=False)
        return [empty_fig] * 6

@app.callback(
    Output('recomendaciones-output', 'children'),
    [Input('buscar-btn', 'n_clicks')],
    [State('distrito-dropdown', 'value'),
     State('edad-dropdown', 'value'),
     State('sexo-dropdown', 'value'),
     State('bvd-slider', 'value')]
)
def generar_recomendaciones_ml(n_clicks, distrito, edad, sexo, bvd_min):
    """Genera recomendaciones usando el modelo de ML"""
    if n_clicks == 0 or df.empty:
        return dbc.Alert(
            "👆 Configure los filtros y haga clic en 'Generar Recomendaciones Inteligentes'",
            color="info",
            className="text-center"
        )
    
    try:
        # Filtrar por BVD mínimo
        df_filtrado = df.copy()
        if bvd_min > 0:
            df_filtrado = df_filtrado[df_filtrado['BVD'] >= bvd_min]
        
        # Obtener recomendaciones con ML
        recomendaciones = recomendar_residencia(df_filtrado, distrito, edad, sexo, modelo_ml)
        
        if isinstance(recomendaciones, str):
            return dbc.Alert(recomendaciones, color="warning")
        
        # Crear cards para cada recomendación
        cards = []
        for i, rec in enumerate(recomendaciones, 1):
            # Determinar color según prioridad
            if i == 1:
                card_color = "success"
                badge_text = "MEJOR OPCIÓN"
            elif i == 2:
                card_color = "warning"
                badge_text = "ALTERNATIVA"
            else:
                card_color = "info"
                badge_text = "RECOMENDACIÓN"
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.H5(f"Recomendación #{i}", className="d-inline"),
                        dbc.Badge(badge_text, color=card_color, className="ms-2")
                    ], className="d-flex justify-content-between align-items-center")
                ], className=f"bg-{card_color} text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("📍 Distrito:", className="fw-bold"),
                            html.P(rec['DISTRITO_NOMBRE'], className="fs-5")
                        ], width=3),
                        dbc.Col([
                            html.H6("⭐ BVD:", className="fw-bold"),
                            html.P(f"{rec['BVD']:.2f}", className="fs-5 text-success")
                        ], width=2),
                        dbc.Col([
                            html.H6("👴 Edad:", className="fw-bold"),
                            html.P(rec['TRAMO_EDAD'])
                        ], width=2),
                        dbc.Col([
                            html.H6("👤 Sexo:", className="fw-bold"),
                            html.P(rec['SEXO'])
                        ], width=2),
                        dbc.Col([
                            html.H6("⏱️ Predicción ML:", className="fw-bold"),
                            html.P(f"{rec['TIEMPO_ESPERA_DIAS']} días", className="fs-5 text-primary")
                        ], width=3),
                    ]),
                    
                    # Barra de progreso para tiempo de espera
                    html.Div([
                        html.P("Probabilidad de asignación rápida:", className="mb-1 fw-bold"),
                        dbc.Progress(
                            value=min(100 - (rec['TIEMPO_ESPERA_DIAS'] / 10), 95),
                            color="success",
                            className="mb-3",
                            style={"height": "20px"}
                        ),
                        html.Small(
                            f"Basado en análisis histórico: {rec['TIEMPO_ESPERA_DIAS']} días estimados",
                            className="text-muted"
                        )
                    ]) if isinstance(rec.get('TIEMPO_ESPERA_DIAS'), (int, float)) else html.Div()
                ])
            ], className=f"mb-3 border-{card_color}")
            cards.append(card)
        
        # Añadir resumen
        resumen = dbc.Card([
            dbc.CardHeader("📋 Resumen de la Búsqueda", className="bg-light"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.P(f"Distrito: {distrito if distrito != 'Todos' else 'Todos los distritos'}"),
                        html.P(f"Edad: {edad if edad != 'Todos' else 'Todos los tramos'}"),
                    ], width=4),
                    dbc.Col([
                        html.P(f"Sexo: {sexo if sexo != 'Todos' else 'Ambos'}"),
                        html.P(f"BVD mínimo: {bvd_min}"),
                    ], width=4),
                    dbc.Col([
                        html.P(f"Recomendaciones encontradas: {len(recomendaciones)}"),
                        html.P(f"Modelo ML: Random Forest activado"),
                    ], width=4),
                ])
            ])
        ], className="mt-3")
        
        return html.Div([resumen] + cards)
        
    except Exception as e:
        print(f"Error generando recomendaciones: {e}")
        return dbc.Alert(f"Error al generar recomendaciones: {str(e)}", color="danger")

@app.callback(
    Output('modelo-status', 'children'),
    [Input('tabs', 'active_tab')]
)
def actualizar_info_modelo(active_tab):
    """Muestra el estado del modelo ML"""
    if modelo_ml and modelo_ml.model:
        return dbc.Alert(
            "✅ Modelo ML cargado y listo para realizar predicciones",
            color="success"
        )
    else:
        return dbc.Alert(
            "⚠️ Modelo ML no disponible. Se usarán criterios básicos para las recomendaciones.",
            color="warning"
        )

@app.callback(
    Output('tabla-datos-container', 'children'),
    [Input('tabs', 'active_tab')]
)
def actualizar_tabla_datos(active_tab):
    """Muestra la tabla de datos"""
    if df.empty:
        return html.P("No hay datos disponibles")
    
    # Crear tabla paginada
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_header={
            'backgroundColor': '#2c3e50',
            'color': 'white',
            'fontWeight': 'bold'
        },
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)