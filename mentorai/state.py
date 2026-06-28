import os
import json
import re
import base64
import random
from typing import Dict, List, Any, Optional

import reflex as rx
import joblib
from dotenv import load_dotenv
from openai import OpenAI
import plotly.graph_objects as go
import numpy as np

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY", "")
if not API_KEY:
    print("ℹ️  GROQ_API_KEY no encontrada. Configúrala como variable de entorno en Reflex Cloud o crea un archivo .env.")

client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")


def load_mentor_engine():
    model_path = os.path.join("modelos", "motor_completo.joblib")
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception as e:
            print(f"Error cargando modelo {model_path}: {e}")

    class MockEngine:
        def recommend(self, perfil, top_k=5, include_details=True):
            carreras = [
                "Datos e IA",
                "Tecnología Core",
                "Diseño UX/UI",
                "Negocios Tech",
                "Marketing Digital",
            ]
            random.shuffle(carreras)
            return [
                {
                    "rank": i + 1,
                    "carrera": c,
                    "confidence": round(random.uniform(70, 95) - (i * 3), 1),
                }
                for i, c in enumerate(carreras[:top_k])
            ]

    return MockEngine()


engine = load_mentor_engine()

SYSTEM_PROMPT = """
Eres MentorAI, un orientador vocacional empático y conversacional.
Evalúa al usuario en 13 áreas (del 1 al 10), además de conocer su 'age' y 'education' (1=Secundaria, 2=Universidad, 3=Maestría, 4=Doctorado).
Áreas: analytical, logical_reasoning, problem_solving, creativity, design, communication, empathy, social, teamwork, leadership, technology, business, stress_tolerance.

REGLAS:
1. Haz preguntas fluidas e investiga sus pasiones. Máximo 2 preguntas por mensaje.
2. Cuando tengas datos suficientes para los 15 valores, corta la conversación y responde ÚNICAMENTE con el bloque JSON solicitado.
"""


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            required_keys = {
                "analytical",
                "logical_reasoning",
                "problem_solving",
                "creativity",
                "design",
                "communication",
                "empathy",
                "social",
                "teamwork",
                "leadership",
                "technology",
                "business",
                "stress_tolerance",
                "age",
                "education",
            }
            if required_keys.issubset(data.keys()):
                return data
        except Exception:
            pass
    return None


def build_radar_chart(values: List[int]) -> str:
    labels = [
        "Analítico", "Razonamiento Lógico", "Resolución Problemas",
        "Creatividad", "Diseño", "Comunicación", "Empatía",
        "Social", "Trabajo Equipo", "Liderazgo", "Tecnología",
        "Negocios", "Tol. Estrés",
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.2)",
        line=dict(color="#2563EB", width=2.5),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 10],
                tickfont=dict(size=9, color="#94A3B8"),
                gridcolor="#E2E8F0",
            ),
            angularaxis=dict(tickfont=dict(size=9, color="#475569")),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=10, b=10),
    )
    return fig.to_html(include_plotlyjs="cdn", full_html=False)


def build_bar_chart(recommendations: List[dict]) -> str:
    labels = [r["carrera"].replace("_", " ").title() for r in recommendations]
    values = [r["confidence"] for r in recommendations]
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=values,
            colorscale=[[0, "#BFDBFE"], [1, "#2563EB"]],
        ),
        text=[f"{c}%" for c in values],
        textposition="outside",
    ))
    fig.update_layout(
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12, color="#1E293B"),
        ),
        xaxis=dict(range=[0, 100], visible=False),
        height=240,
        margin=dict(l=10, r=40, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig.to_html(include_plotlyjs="cdn", full_html=False)


class State(rx.State):
    messages: List[Dict[str, str]] = []
    finished: bool = False
    show_suggestions: bool = True
    loading: bool = False
    is_recording: bool = False
    temperature: str = "0.7"
    input_text: str = ""
    show_settings: bool = False
    show_profile: bool = False

    top_career: str = ""
    recommendations: List[Dict[str, Any]] = []
    radar_html: str = ""
    bar_html: str = ""

    def init_chat(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "assistant",
                "content": "¡Hola! Soy MentorAI 🧠. Cuéntame un poco sobre ti: ¿qué actividades o materias disfrutas más en tu día a día?",
            },
        ]
        self.finished = False
        self.show_suggestions = True
        self.loading = False
        self.is_recording = False
        self.input_text = ""
        self.show_settings = False
        self.show_profile = False
        self.top_career = ""
        self.recommendations = []
        self.radar_html = ""
        self.bar_html = ""

    def toggle_settings(self, is_open=None):
        if is_open is not None:
            self.show_settings = is_open
        else:
            self.show_settings = not self.show_settings

    def toggle_profile(self, is_open=None):
        if is_open is not None:
            self.show_profile = is_open
        else:
            self.show_profile = not self.show_profile

    def set_temperature(self, value: str):
        self.temperature = value

    def set_input(self, value: str):
        self.input_text = value

    def handle_keyboard(self, e: str):
        if e == "Enter":
            return [rx.prevent_default, State.send_from_input]

    def send_from_input(self):
        text = self.input_text.strip()
        if text and not self.finished:
            self.messages.append({"role": "user", "content": text})
            self.input_text = ""
            self.show_suggestions = False
            self.loading = True
            return State.process_chat

    def send_suggestion(self, text: str):
        self.messages.append({"role": "user", "content": text})
        self.show_suggestions = False
        self.loading = True
        return State.process_chat

    def send_message(self, text: str):
        if not text.strip() or self.finished:
            return
        self.messages.append({"role": "user", "content": text.strip()})
        self.show_suggestions = False
        self.loading = True
        return State.process_chat

    async def process_chat(self):
        if not client:
            self.messages.append({
                "role": "assistant",
                "content": "⚠️ GROQ_API_KEY no configurada. Agrégala como variable de entorno en Reflex Cloud (Settings → Secrets) o crea un archivo .env en la raíz del proyecto.",
            })
            self.loading = False
            return

        try:
            api_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *[
                    {"role": m["role"], "content": m["content"]}
                    for m in self.messages
                    if m["role"] != "system"
                ],
            ]

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                temperature=float(self.temperature),
            )
            llm_reply = response.choices[0].message.content
            datos_llm = extract_json(llm_reply)

            if datos_llm:
                self.finished = True
                self.loading = False

                edu_map = {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.9}
                skill_keys = [
                    "analytical", "logical_reasoning", "problem_solving",
                    "creativity", "design", "communication", "empathy",
                    "social", "teamwork", "leadership", "technology",
                    "business", "stress_tolerance",
                ]
                perfil_usuario = {
                    k: datos_llm.get(k, 5) / 10.0 for k in skill_keys
                }
                perfil_usuario["education"] = edu_map.get(
                    int(datos_llm.get("education", 2)), 0.5
                )
                perfil_usuario["age"] = min(
                    datos_llm.get("age", 20) / 65.0, 1.0
                )

                recomendaciones = engine.recommend(
                    perfil_usuario, top_k=3, include_details=True
                )
                recomendaciones = [
                    {k: (v.item() if hasattr(v, 'item') else v) for k, v in r.items()}
                    for r in recomendaciones
                ]
                self.recommendations = recomendaciones
                self.top_career = (
                    recomendaciones[0]["carrera"] if recomendaciones else ""
                )

                values = [datos_llm.get(k, 5) for k in skill_keys]
                self.radar_html = build_radar_chart(values)
                self.bar_html = build_bar_chart(recomendaciones)
            else:
                self.messages.append({
                    "role": "assistant",
                    "content": llm_reply,
                })
                self.loading = False
        except Exception as e:
            self.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error de conexión con la IA: {str(e)}",
            })
            self.loading = False

    def reset_chat(self):
        self.init_chat()

    def toggle_recording(self):
        if not self.is_recording:
            return State.start_recording()
        else:
            return State.stop_recording()

    def start_recording(self):
        self.is_recording = True
        return rx.call_script("window.startMicRecording()")

    def stop_recording(self):
        self.is_recording = False
        return rx.call_script(
            "window.stopMicRecording()",
            callback=State.handle_audio_data,
        )

    async def handle_audio_data(self, audio_b64: str):
        if not audio_b64 or not client:
            self.is_recording = False
            return
        self.loading = True
        try:
            clean_b64 = audio_b64.split(",")[-1] if "," in audio_b64 else audio_b64
            audio_bytes = base64.b64decode(clean_b64)
            result = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=("audio.wav", audio_bytes, "audio/wav"),
            )
            text = result.text.strip()
            if text:
                self.messages.append({"role": "user", "content": text})
                self.show_suggestions = False
                return State.process_chat
            self.loading = False
        except Exception as e:
            self.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error transcribiendo audio: {str(e)}",
            })
            self.loading = False
        finally:
            self.is_recording = False
