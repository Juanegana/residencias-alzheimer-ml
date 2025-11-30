import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def crear_grafico_distritos(df):
    """Crea gráfico de barras por distrito"""
    if df.empty:
        return go.Figure()
    
    distrito_counts = df['DISTRITO_NOMBRE'].value_counts().reset_index()
    distrito_counts.columns = ['Distrito', 'Cantidad']
    
    fig = px.bar(distrito_counts, 
                 x='Distrito', 
                 y='Cantidad',
                 title='Personas en lista de espera por Distrito',
                 color='Cantidad')
    
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def crear_grafico_edad(df):
    """Crea gráfico de distribución por edad"""
    if df.empty:
        return go.Figure()
    
    edad_counts = df['TRAMO_EDAD'].value_counts().reset_index()
    edad_counts.columns = ['Tramo_Edad', 'Cantidad']
    
    fig = px.pie(edad_counts, 
                 values='Cantidad', 
                 names='Tramo_Edad',
                 title='Distribución por Tramo de Edad')
    
    return fig

def crear_grafico_sexo(df):
    """Crea gráfico de distribución por sexo"""
    if df.empty:
        return go.Figure()
    
    sexo_counts = df['SEXO'].value_counts().reset_index()
    sexo_counts.columns = ['Sexo', 'Cantidad']
    
    fig = px.bar(sexo_counts, 
                 x='Sexo', 
                 y='Cantidad',
                 title='Distribución por Sexo',
                 color='Sexo')
    
    return fig