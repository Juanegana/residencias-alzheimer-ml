import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def crear_grafico_distritos(df):
    """Crea gráfico de barras por distrito (todos)"""
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

def crear_grafico_top_distritos(df, n=10):
    """Crea gráfico de barras para los top n distritos"""
    if df.empty:
        return go.Figure()
    
    distrito_counts = df['DISTRITO_NOMBRE'].value_counts().head(n).reset_index()
    distrito_counts.columns = ['Distrito', 'Cantidad']
    
    fig = px.bar(distrito_counts, 
                 x='Distrito', 
                 y='Cantidad',
                 title=f'Top {n} Distritos con más personas en lista de espera',
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

def crear_grafico_bvd_distribucion(df):
    """Crea histograma de distribución de BVD"""
    if df.empty:
        return go.Figure()
    
    fig = px.histogram(df, 
                      x='BVD',
                      title='Distribución de Baremo de Valoración de la Dependencia (BVD)',
                      nbins=20,
                      color_discrete_sequence=['#3498db'])
    
    fig.update_layout(xaxis_title="BVD", yaxis_title="Frecuencia")
    return fig

def crear_grafico_correlacion(df):
    """Crea heatmap de correlación entre variables numéricas"""
    if df.empty:
        return go.Figure()
    
    # Seleccionar solo columnas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(corr_matrix,
                       title='Matriz de Correlación entre Variables Numéricas',
                       color_continuous_scale='RdBu',
                       zmin=-1, zmax=1)
        
        return fig
    else:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No hay variables numéricas para calcular correlación", showarrow=False)
        return empty_fig