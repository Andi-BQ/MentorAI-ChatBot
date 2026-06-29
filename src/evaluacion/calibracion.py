class CalibratedWrapper:
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def predict_proba(self, x):
        model = getattr(self, 'model', None) or getattr(self, 'base_model', None)
        if model is not None:
            return model.predict_proba(x)
        raise RuntimeError("CalibratedWrapper: no base model available")

    def predict(self, x):
        return self.predict_proba(x)


class TemperatureScaler:
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def predict_proba(self, x):
        model = getattr(self, 'model', None) or getattr(self, 'base_model', None)
        if model is not None:
            return model.predict_proba(x)
        return x

    def predict(self, x):
        return self.predict_proba(x)
