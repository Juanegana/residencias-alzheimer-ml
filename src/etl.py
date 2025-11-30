import pandas as pd
import numpy as np
from datetime import datetime
import os

def cargar_datos():
    """Carga y limpia los datos de lista de espera"""
    try:
        df = pd.read_csv('data/lista_espera.csv', sep=';', encoding='utf-8')
        
        # Limpieza avanzada
        df['BVD'] = pd.to_numeric(df['BVD'], errors='coerce')
        df['FECHA_DE_ENTRADA'] = pd.to_datetime(df['FECHA_DE_ENTRADA'])
        df['DISTRITO_NOMBRE'] = df['DISTRITO'].str.strip()
        
        # Crear características adicionales
        df['MES_ENTRADA'] = df['FECHA_DE_ENTRADA'].dt.month
        df['DIA_SEMANA'] = df['FECHA_DE_ENTRADA'].dt.day_name()
        
        # Calcular "días en espera" (simulado para el ejemplo)
        fecha_referencia = pd.to_datetime('2025-10-26')
        df['DIAS_EN_ESPERA'] = (fecha_referencia - df['FECHA_DE_ENTRADA']).dt.days
        
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame()

def obtener_estadisticas_avanzadas(df):
    """Calcula estadísticas avanzadas"""
    if df.empty:
        return {}
    
    stats = {
        'total_personas': len(df),
        'promedio_bvd': df['BVD'].mean(),
        'mediana_bvd': df['BVD'].median(),
        'distritos_unicos': df['DISTRITO_NOMBRE'].nunique(),
        'distribucion_sexo': df['SEXO'].value_counts().to_dict(),
        'distribucion_edad': df['TRAMO_EDAD'].value_counts().to_dict(),
        'top_distritos': df['DISTRITO_NOMBRE'].value_counts().head(5).to_dict(),
        'promedio_dias_espera': df['DIAS_EN_ESPERA'].mean(),
        'tendencia_mensual': df['MES_ENTRADA'].value_counts().sort_index().to_dict()
    }
    
    return stats