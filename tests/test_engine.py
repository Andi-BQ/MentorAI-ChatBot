import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.recomendacion.motor_recomendacion import CareerEngineES


def make_engine():
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    engine = CareerEngineES()

    class DummyModel:
        def predict_proba(self, x):
            n_classes = 5
            probas = np.full((x.shape[0], n_classes), 0.2)
            probas[0, 0] = 0.6
            probas[0, 1] = 0.3
            return probas

    engine.model = DummyModel()
    engine.scaler = StandardScaler()
    engine.scaler.fit(np.array([[0.5] * 15]))
    engine.encoder = LabelEncoder()
    engine.encoder.fit(["carrera_a", "carrera_b", "carrera_c", "carrera_d", "carrera_e"])
    return engine


class TestCareerEngineES:
    def test_recommend_returns_list(self):
        engine = make_engine()
        perfil = {k: 0.5 for k in engine.feature_names}
        results = engine.recommend(perfil, top_k=3)
        assert isinstance(results, list)
        assert len(results) == 3

    def test_recommend_returns_top_k(self):
        engine = make_engine()
        perfil = {k: 0.5 for k in engine.feature_names}
        results = engine.recommend(perfil, top_k=2)
        assert len(results) == 2

    def test_recommend_includes_confidence(self):
        engine = make_engine()
        perfil = {k: 0.5 for k in engine.feature_names}
        results = engine.recommend(perfil, top_k=1)
        assert "confidence" in results[0]
        assert 0 <= results[0]["confidence"] <= 100

    def test_recommend_includes_rank(self):
        engine = make_engine()
        perfil = {k: 0.5 for k in engine.feature_names}
        results = engine.recommend(perfil, top_k=3)
        for i, r in enumerate(results):
            assert r["rank"] == i + 1

    def test_recommend_sorted_by_confidence(self):
        engine = make_engine()
        perfil = {k: 0.5 for k in engine.feature_names}
        results = engine.recommend(perfil, top_k=5)
        confidences = [r["confidence"] for r in results]
        assert confidences == sorted(confidences, reverse=True)
