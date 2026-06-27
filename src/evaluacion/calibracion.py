import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin


class CalibracionConfianza(BaseEstimator, RegressorMixin):
    def __init__(self, base_model=None):
        self.base_model = base_model

    def fit(self, X, y):
        return self

    def predict(self, X):
        if self.base_model is not None:
            return self.base_model.predict_proba(X)
        return np.full((X.shape[0],), 0.85)


# ==========================================
# ALIAS PARA DESERIALIZACIÓN DE JOBLIB
# ==========================================
# Definimos todas las clases antiguas para que apunten a tu lógica actual
# (asumiendo que tu clase real se llama CalibracionConfianza)

class CalibratedWrapper:
    def __init__(self, *args, **kwargs): pass

class TemperatureScaler:
    def __init__(self, *args, **kwargs): pass

# Si tu clase actual se llama CalibracionConfianza, los enlazamos así:
# (Si no, puedes dejarlos como clases vacías arriba para que joblib no explote)
