import pandas as pd
import random

def recomendar_residencia(df, distrito, edad, sexo):
    """
    Recomienda residencias basado en criterios simples
    En una versión futura, esto se mejorará con ML
    """
    if df.empty:
        return "No hay datos disponibles"
    
    # Filtrar por criterios (versión básica)
    filtrado = df.copy()
    
    if distrito != "Todos":
        filtrado = filtrado[filtrado['DISTRITO_NOMBRE'] == distrito]
    
    if edad != "Todos":
        filtrado = filtrado[filtrado['TRAMO_EDAD'] == edad]
    
    if sexo != "Todos":
        filtrado = filtrado[filtrado['SEXO'] == sexo]
    
    if len(filtrado) == 0:
        return "No se encontraron residencias que coincidan con los criterios"
    
    # Ordenar por BVD (mayor puntuación primero) y tomar las top 3
    recomendaciones = filtrado.nlargest(3, 'BVD')[['DISTRITO_NOMBRE', 'BVD', 'TRAMO_EDAD', 'SEXO']]
    
    return recomendaciones.to_dict('records')