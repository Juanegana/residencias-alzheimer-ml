"""
Paquete src para el sistema de residencias Alzheimer
"""

__version__ = "2.0.0"
__author__ = "Equipo ML"

from .etl import cargar_datos, obtener_estadisticas_avanzadas, cargar_o_entrenar_modelo
from .graphics import (
    crear_grafico_distritos,
    crear_grafico_edad,
    crear_grafico_sexo,
    crear_grafico_evolucion_temporal,
    crear_grafico_tiempo_espera,
    crear_grafico_bvd_vs_espera,
    crear_grafico_top_distritos,
    crear_grafico_bvd_distribucion,
    crear_grafico_correlacion
)
from .model import ModeloPrediccion, recomendar_residencia

__all__ = [
    'cargar_datos',
    'obtener_estadisticas_avanzadas',
    'cargar_o_entrenar_modelo',
    'crear_grafico_distritos',
    'crear_grafico_edad',
    'crear_grafico_sexo',
    'crear_grafico_evolucion_temporal',
    'crear_grafico_tiempo_espera',
    'crear_grafico_bvd_vs_espera',
    'crear_grafico_top_distritos',
    'crear_grafico_bvd_distribucion',
    'crear_grafico_correlacion',
    'ModeloPrediccion',
    'recomendar_residencia'
]