import pandas as pd
import os

def cargar_datos():
    """Carga y limpia los datos de lista de espera"""
    try:
        # Cargar datos
        df = pd.read_csv('data/lista_espera.csv', sep=';', encoding='utf-8')
        
        # Limpieza básica
        df['BVD'] = pd.to_numeric(df['BVD'], errors='coerce')
        df['FECHA_DE_ENTRADA'] = pd.to_datetime(df['FECHA_DE_ENTRADA'])
        
        # Crear categorías simplificadas
        df['DISTRITO_NOMBRE'] = df['DISTRITO'].str.strip()
        
        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame()

def obtener_estadisticas_basicas(df):
    """Calcula estadísticas básicas para el dashboard"""
    if df.empty:
        return {}
    
    stats = {
        'total_personas': len(df),
        'promedio_edad_numerico': df['BVD'].mean(),
        'distritos_unicos': df['DISTRITO_NOMBRE'].nunique(),
        'distribucion_sexo': df['SEXO'].value_counts().to_dict(),
        'distribucion_edad': df['TRAMO_EDAD'].value_counts().to_dict(),
        'top_distritos': df['DISTRITO_NOMBRE'].value_counts().head(5).to_dict()
    }
    
    return stats