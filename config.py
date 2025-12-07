"""
Configuración de la aplicación
"""

# Configuración de la aplicación
APP_CONFIG = {
    'DEBUG': False,
    'TITLE': 'Residencias Alzheimer - Sistema Inteligente',
    'DESCRIPTION': 'Sistema de recomendación con Machine Learning para plazas en residencias',
    'AUTHOR': 'Equipo ML',
    'VERSION': '2.0.0',
    'DATA_PATH': 'data/lista_espera.csv'
}

# Configuración del modelo ML
ML_CONFIG = {
    'MODEL_PATH': 'modelo_espera.pkl',
    'ENCODERS_PATH': 'label_encoders.pkl',
    'METRICS_PATH': 'modelo_metrics.pkl',
    'N_ESTIMATORS': 100,
    'RANDOM_STATE': 42,
    'TEST_SIZE': 0.2
}

# Configuración de visualización
VISUALIZATION_CONFIG = {
    'COLORS': {
        'primary': '#3498db',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#17a2b8'
    },
    'CHART_TEMPLATE': 'plotly_white'
}