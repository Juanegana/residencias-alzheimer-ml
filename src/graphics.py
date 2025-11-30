import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def crear_grafico_evolucion_temporal(df):
    """Crea gráfico de evolución temporal de entradas"""
    if df.empty:
        return go.Figure()
    
    mensual = df.groupby('MES_ENTRADA').size().reset_index(name='count')
    
    fig = px.line(mensual, 
                 x='MES_ENTRADA', 
                 y='count',
                 title='Evolución Mensual de Entradas en Lista de Espera',
                 markers=True)
    
    fig.update_layout(xaxis_title="Mes", yaxis_title="Número de Entradas")
    return fig

def crear_grafico_tiempo_espera(df):
    """Crea gráfico de distribución de tiempo de espera"""
    if df.empty:
        return go.Figure()
    
    fig = px.histogram(df, 
                      x='DIAS_EN_ESPERA',
                      title='Distribución de Días en Lista de Espera',
                      nbins=20)
    
    fig.update_layout(xaxis_title="Días en Espera", yaxis_title="Frecuencia")
    return fig

def crear_grafico_bvd_vs_espera(df):
    """Crea scatter plot de BVD vs tiempo de espera"""
    if df.empty:
        return go.Figure()
    
    fig = px.scatter(df, 
                    x='BVD', 
                    y='DIAS_EN_ESPERA',
                    color='TRAMO_EDAD',
                    title='Relación entre BVD y Tiempo de Espera',
                    hover_data=['DISTRITO_NOMBRE', 'SEXO'])
    
    fig.update_layout(xaxis_title="BVD", yaxis_title="Días en Espera")
    return fig

# Mantener las funciones originales también
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