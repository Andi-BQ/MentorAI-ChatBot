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


# Crear un alias para que joblib pueda deserializar el modelo antiguo
CalibratedWrapper = CalibracionConfianza
