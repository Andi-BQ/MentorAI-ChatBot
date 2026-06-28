import numpy as np


class CareerEngineES:
    """Engine serializado en motor_completo.joblib (nuevo modelo entrenado).

    Mantiene la misma API que CareerRecommendationEngine para compatibilidad
    con la deserialización joblib/cloudpickle.
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = [
            "analytical", "logical_reasoning", "problem_solving",
            "creativity", "design", "communication", "empathy",
            "social", "teamwork", "leadership", "technology",
            "business", "stress_tolerance", "education", "age",
        ]

    def recommend(self, perfil, top_k=5, include_details=True):
        features = np.array([[perfil.get(k, 0.5) for k in self.feature_names]])
        if self.scaler:
            features = self.scaler.transform(features)
        probas = self.model.predict_proba(features)[0]
        top_indices = np.argsort(probas)[::-1][:top_k]
        carreras = self.encoder.inverse_transform(top_indices)
        results = []
        for i, (idx, carrera) in enumerate(zip(top_indices, carreras)):
            results.append({
                "rank": i + 1,
                "carrera": carrera,
                "confidence": round(float(probas[idx]) * 100, 1),
            })
        return results


class CareerRecommendationEngine:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = [
            "analytical", "logical_reasoning", "problem_solving",
            "creativity", "design", "communication", "empathy",
            "social", "teamwork", "leadership", "technology",
            "business", "stress_tolerance", "education", "age",
        ]

    def recommend(self, perfil, top_k=5, include_details=True):
        features = np.array([[perfil.get(k, 0.5) for k in self.feature_names]])
        if self.scaler:
            features = self.scaler.transform(features)
        probas = self.model.predict_proba(features)[0]
        top_indices = np.argsort(probas)[::-1][:top_k]
        carreras = self.encoder.inverse_transform(top_indices)
        results = []
        for i, (idx, carrera) in enumerate(zip(top_indices, carreras)):
            results.append({
                "rank": i + 1,
                "carrera": carrera,
                "confidence": round(float(probas[idx]) * 100, 1),
            })
        return results
