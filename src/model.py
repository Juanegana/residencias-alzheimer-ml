import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

class ModeloPrediccion:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        
    def entrenar_modelo(self, df):
        """Entrena un modelo para predecir tiempo de espera"""
        try:
            # Preparar datos para ML
            df_ml = df.copy()
            
            # Codificar variables categóricas
            categorical_cols = ['DISTRITO_NOMBRE', 'TRAMO_EDAD', 'SEXO']
            for col in categorical_cols:
                le = LabelEncoder()
                df_ml[col + '_encoded'] = le.fit_transform(df_ml[col].astype(str))
                self.label_encoders[col] = le
            
            # Características y objetivo
            features = ['DISTRITO_NOMBRE_encoded', 'TRAMO_EDAD_encoded', 'SEXO_encoded', 'BVD']
            X = df_ml[features]
            y = df_ml['DIAS_EN_ESPERA']  # Usamos días en espera como objetivo
            
            # Entrenar modelo
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            
            # Guardar modelo
            joblib.dump(self.model, 'modelo_espera.pkl')
            joblib.dump(self.label_encoders, 'label_encoders.pkl')
            
            return True
        except Exception as e:
            print(f"Error entrenando modelo: {e}")
            return False
    
    def predecir_tiempo_espera(self, distrito, edad, sexo, bvd):
        """Predice el tiempo de espera"""
        try:
            if self.model is None:
                return "Modelo no disponible"
            
            # Codificar entradas
            distrito_enc = self.label_encoders['DISTRITO_NOMBRE'].transform([distrito])[0]
            edad_enc = self.label_encoders['TRAMO_EDAD'].transform([edad])[0]
            sexo_enc = self.label_encoders['SEXO'].transform([sexo])[0]
            
            # Crear array de características
            X_new = np.array([[distrito_enc, edad_enc, sexo_enc, bvd]])
            
            # Predecir
            prediccion = self.model.predict(X_new)[0]
            
            return max(0, int(prediccion))
        except Exception as e:
            return f"Error en predicción: {e}"

# Instancia global del modelo
modelo_ml = ModeloPrediccion()

def recomendar_residencia(df, distrito, edad, sexo, bvd=None):
    """Recomienda residencias con ML"""
    if df.empty:
        return "No hay datos disponibles"
    
    # Si no se proporciona BVD, usar el promedio
    if bvd is None:
        bvd = df['BVD'].mean()
    
    # Filtrar por criterios
    filtrado = df.copy()
    
    if distrito != "Todos":
        filtrado = filtrado[filtrado['DISTRITO_NOMBRE'] == distrito]
    
    if edad != "Todos":
        filtrado = filtrado[filtrado['TRAMO_EDAD'] == edad]
    
    if sexo != "Todos":
        filtrado = filtrado[filtrado['SEXO'] == sexo]
    
    if len(filtrado) == 0:
        return "No se encontraron residencias que coincidan con los criterios"
    
    # Ordenar por BVD y tomar las top 3
    recomendaciones = filtrado.nlargest(3, 'BVD')
    
    # Añadir predicción de tiempo de espera
    resultados = []
    for _, rec in recomendaciones.iterrows():
        tiempo_espera = modelo_ml.predecir_tiempo_espera(
            rec['DISTRITO_NOMBRE'], 
            rec['TRAMO_EDAD'], 
            rec['SEXO'],
            rec['BVD']
        )
        
        resultados.append({
            'DISTRITO_NOMBRE': rec['DISTRITO_NOMBRE'],
            'BVD': rec['BVD'],
            'TRAMO_EDAD': rec['TRAMO_EDAD'],
            'SEXO': rec['SEXO'],
            'TIEMPO_ESPERA_DIAS': tiempo_espera
        })
    
    return resultados