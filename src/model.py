import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

class ModeloPrediccion:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.metrics = {}
        
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
            
            # Dividir datos en entrenamiento y prueba
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Entrenar modelo
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = self.model.predict(X_test)
            self.metrics = {
                'MAE': mean_absolute_error(y_test, y_pred),
                'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
                'R2': r2_score(y_test, y_pred),
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
            
            print(f"Modelo entrenado. Métricas:")
            print(f"  MAE: {self.metrics['MAE']:.2f}")
            print(f"  RMSE: {self.metrics['RMSE']:.2f}")
            print(f"  R²: {self.metrics['R2']:.4f}")
            
            # Guardar modelo
            joblib.dump(self.model, 'modelo_espera.pkl')
            joblib.dump(self.label_encoders, 'label_encoders.pkl')
            joblib.dump(self.metrics, 'modelo_metrics.pkl')
            
            return True
            
        except Exception as e:
            print(f"Error entrenando modelo: {e}")
            return False
    
    def predecir_tiempo_espera(self, distrito, edad, sexo, bvd):
        """Predice el tiempo de espera para un paciente específico"""
        try:
            if self.model is None:
                return "Modelo no disponible"
            
            # Verificar que las categorías existen en los encoders
            for col, le in self.label_encoders.items():
                if col == 'DISTRITO_NOMBRE' and distrito not in le.classes_:
                    return f"Distrito '{distrito}' no encontrado en datos de entrenamiento"
                elif col == 'TRAMO_EDAD' and edad not in le.classes_:
                    return f"Edad '{edad}' no encontrada en datos de entrenamiento"
                elif col == 'SEXO' and sexo not in le.classes_:
                    return f"Sexo '{sexo}' no encontrado en datos de entrenamiento"
            
            # Codificar entradas
            distrito_enc = self.label_encoders['DISTRITO_NOMBRE'].transform([distrito])[0]
            edad_enc = self.label_encoders['TRAMO_EDAD'].transform([edad])[0]
            sexo_enc = self.label_encoders['SEXO'].transform([sexo])[0]
            
            # Crear array de características
            X_new = np.array([[distrito_enc, edad_enc, sexo_enc, bvd]])
            
            # Predecir
            prediccion = self.model.predict(X_new)[0]
            
            # Añadir intervalo de confianza (simulado basado en RMSE)
            intervalo_confianza = self.metrics.get('RMSE', 30) * 1.96
            
            return {
                'prediccion': max(0, int(prediccion)),
                'intervalo_min': max(0, int(prediccion - intervalo_confianza)),
                'intervalo_max': max(0, int(prediccion + intervalo_confianza)),
                'confianza': min(95, max(50, 100 - (intervalo_confianza / 10)))
            }
            
        except Exception as e:
            print(f"Error en predicción: {e}")
            return f"Error en predicción: {str(e)}"
    
    def obtener_importancia_caracteristicas(self):
        """Obtiene la importancia de cada característica en el modelo"""
        if self.model is None:
            return {}
        
        feature_names = ['Distrito', 'Edad', 'Sexo', 'BVD']
        importances = self.model.feature_importances_
        
        return dict(zip(feature_names, importances))

def recomendar_residencia(df, distrito, edad, sexo, modelo_ml, bvd=None):
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
    
    # Ordenar por BVD (prioridad) y tomar las top 5
    recomendaciones_raw = filtrado.nlargest(5, 'BVD')
    
    # Añadir predicción de tiempo de espera
    resultados = []
    for _, rec in recomendaciones_raw.iterrows():
        if modelo_ml and modelo_ml.model:
            prediccion = modelo_ml.predecir_tiempo_espera(
                rec['DISTRITO_NOMBRE'], 
                rec['TRAMO_EDAD'], 
                rec['SEXO'],
                rec['BVD']
            )
            
            if isinstance(prediccion, dict):
                tiempo_espera = prediccion['prediccion']
                intervalo = f"{prediccion['intervalo_min']}-{prediccion['intervalo_max']} días"
                confianza = prediccion['confianza']
            else:
                tiempo_espera = prediccion
                intervalo = "N/A"
                confianza = 0
        else:
            tiempo_espera = "Modelo no disponible"
            intervalo = "N/A"
            confianza = 0
        
        # Calcular score de recomendación (combinando BVD y tiempo de espera)
        if isinstance(tiempo_espera, (int, float)):
            # Score más alto = mejor recomendación (BVD alto, tiempo bajo)
            score_recomendacion = (rec['BVD'] * 0.7) + (100 - min(tiempo_espera, 100)) * 0.3
        else:
            score_recomendacion = rec['BVD']
        
        resultados.append({
            'DISTRITO_NOMBRE': rec['DISTRITO_NOMBRE'],
            'BVD': rec['BVD'],
            'TRAMO_EDAD': rec['TRAMO_EDAD'],
            'SEXO': rec['SEXO'],
            'DIAS_EN_ESPERA': rec['DIAS_EN_ESPERA'],
            'TIEMPO_ESPERA_DIAS': tiempo_espera,
            'INTERVALO_ESPERA': intervalo,
            'CONFIANZA_PREDICCION': confianza,
            'SCORE_RECOMENDACION': score_recomendacion
        })
    
    # Ordenar por score de recomendación (de mayor a menor)
    resultados.sort(key=lambda x: x['SCORE_RECOMENDACION'], reverse=True)
    
    # Tomar solo las 3 mejores
    return resultados[:3]