import sys
from pathlib import Path

import plotly.io as pio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mentorai.state import build_bar_chart, build_radar_chart, extract_json, translate_career


class TestExtractJson:
    def test_valid_json_with_all_keys(self):
        text = '{"analytical":8,"logical_reasoning":7,"problem_solving":9,"creativity":6,"design":5,"communication":8,"empathy":9,"social":7,"teamwork":8,"leadership":6,"technology":9,"business":4,"stress_tolerance":7,"age":22,"education":3}'
        result = extract_json(text)
        assert result is not None
        assert result["analytical"] == 8
        assert result["age"] == 22
        assert result["education"] == 3

    def test_json_missing_keys_returns_none(self):
        text = '{"analytical":8,"age":22,"education":3}'
        assert extract_json(text) is None

    def test_invalid_text_returns_none(self):
        assert extract_json("Hola, ¿cómo estás?") is None

    def test_empty_string_returns_none(self):
        assert extract_json("") is None

    def test_json_with_extra_keys_still_valid(self):
        text = '{"analytical":8,"logical_reasoning":7,"problem_solving":9,"creativity":6,"design":5,"communication":8,"empathy":9,"social":7,"teamwork":8,"leadership":6,"technology":9,"business":4,"stress_tolerance":7,"age":22,"education":3,"extra":"ignored"}'
        result = extract_json(text)
        assert result is not None
        assert "extra" in result

    def test_malformed_json_returns_none(self):
        text = '{"analytical":8, broken}'
        assert extract_json(text) is None


class TestBuildRadarChart:
    def test_empty_values_returns_empty_figure(self):
        result = build_radar_chart([])
        fig = pio.from_json(result)
        assert len(fig.data) == 0

    def test_valid_values_returns_scatterpolar(self):
        values = [8, 7, 9, 6, 5, 8, 9, 7, 8, 6, 9, 4, 7]
        result = build_radar_chart(values)
        fig = pio.from_json(result)
        assert len(fig.data) == 1
        assert fig.data[0].type == "scatterpolar"

    def test_dark_mode_uses_dark_font(self):
        values = [8, 7, 9, 6, 5, 8, 9, 7, 8, 6, 9, 4, 7]
        light_result = build_radar_chart(values, "light")
        dark_result = build_radar_chart(values, "dark")
        light_fig = pio.from_json(light_result)
        dark_fig = pio.from_json(dark_result)
        assert light_fig.layout.font.color != dark_fig.layout.font.color

    def test_light_mode_default(self):
        values = [8, 7, 9, 6, 5, 8, 9, 7, 8, 6, 9, 4, 7]
        result = build_radar_chart(values)
        fig = pio.from_json(result)
        assert fig.layout.font.color == "#0F172A"


class TestBuildBarChart:
    def test_valid_recommendations_returns_bar(self):
        recs = [
            {"carrera": "Ingeniería", "confidence": 85.3},
            {"carrera": "Medicina", "confidence": 72.1},
            {"carrera": "Derecho", "confidence": 64.8},
        ]
        result = build_bar_chart(recs)
        fig = pio.from_json(result)
        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"

    def test_dark_mode_bar_chart(self):
        recs = [{"carrera": "Test", "confidence": 50.0}]
        light_result = build_bar_chart(recs, "light")
        dark_result = build_bar_chart(recs, "dark")
        light_fig = pio.from_json(light_result)
        dark_fig = pio.from_json(dark_result)
        assert light_fig.layout.font.color != dark_fig.layout.font.color

    def test_empty_recommendations(self):
        result = build_bar_chart([])
        fig = pio.from_json(result)
        assert len(fig.data) == 1
        assert len(fig.data[0].y) == 0


class TestTranslateCareer:
    def test_known_key_returns_translation(self):
        result = translate_career("software_developer")
        assert isinstance(result, str)
        assert result != ""

    def test_unknown_key_returns_title_case(self):
        result = translate_career("some_unknown_career")
        assert result == "Some Unknown Career"
