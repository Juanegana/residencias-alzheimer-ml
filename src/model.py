from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

model = None
feature_columns = None

def train_model(df):
    """Entrena un modelo mínimo usando todas las columnas numéricas excepto la última."""
    
    global model, feature_columns

    # Usamos todas las columnas numéricas
    numeric_df = df.select_dtypes(include=["int64", "float64"])

    # Suponemos que la última columna es el target (ajústalo si quieres)
    feature_columns = numeric_df.columns[:-1]
    target_column = numeric_df.columns[-1]

    X = numeric_df[feature_columns]
    y = numeric_df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    return model, feature_columns


def predict_wait_time(values_dict):
    """Recibe un diccionario con valores de entrada y devuelve la predicción."""
    global model, feature_columns

    import pandas as pd

    X = pd.DataFrame([values_dict])[feature_columns]
    pred = model.predict(X)[0]

    return pred
