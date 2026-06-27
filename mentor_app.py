import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os
import json
import re
from openai import OpenAI

from streamlit_mic_recorder import mic_recorder

# ============================================================
# 1. CONFIGURACIÓN Y ESTILOS
# ============================================================
st.set_page_config(page_title="MentorAI", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }

    .stApp { background: #F8FAFC; }

    header { display: none !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    .stDeployButton { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    .block-container {
        max-width: 800px !important;
        padding: 0 !important;
        margin: 0 auto !important;
        background: transparent !important;
    }

    /* ── Scrollbar ── */
    .main > div::-webkit-scrollbar { width: 6px; }
    .main > div::-webkit-scrollbar-track { background: transparent; }
    .main > div::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }

    /* ── Top AppBar ── */
    .appbar {
        position: fixed; top: 0; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px;
        background: #FFFFFF; border-bottom: 1px solid #E2E8F0;
        z-index: 999; padding: 14px 24px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .appbar-logo {
        font-size: 1.25rem; font-weight: 700; color: #00288E;
        cursor: pointer; user-select: none;
    }
    .appbar-nav {
        display: flex; gap: 24px; align-items: center;
    }
    .appbar-nav span {
        font-size: 0.9rem; color: #64748B; cursor: pointer; padding-bottom: 2px;
        transition: color 0.15s;
    }
    .appbar-nav span.active { color: #00288E; font-weight: 600; border-bottom: 2px solid #00288E; }
    .appbar-nav span:hover { color: #00288E; }
    .appbar-actions {
        display: flex; gap: 8px; align-items: center;
    }
    .appbar-actions .material-symbols-outlined {
        font-size: 1.4rem; color: #00288E; cursor: pointer;
        padding: 6px; border-radius: 50%; transition: background 0.15s;
    }
    .appbar-actions .material-symbols-outlined:hover { background: #F1F5F9; }

    /* ── Executive Header ── */
    .exec-header {
        background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
        padding: 20px 24px; margin: 96px 0 24px 0;
        display: flex; align-items: center; justify-content: space-between;
    }
    .exec-header h2 {
        font-size: 1.25rem; font-weight: 600; color: #1E40AF; margin: 0;
    }
    .exec-badge {
        display: flex; align-items: center; gap: 8px;
        background: #F1F5F9; padding: 6px 16px; border-radius: 999px;
    }
    .exec-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: #1E40AF; }
    .exec-badge span { font-size: 0.75rem; font-weight: 600; color: #1E40AF; text-transform: uppercase; letter-spacing: 0.03em; }

    /* ── Chat Messages ── */
    div[data-testid="stChatMessage"] {
        padding: 0 !important; margin: 0 0 16px 0 !important;
        border: none !important; display: flex !important; align-items: flex-start !important;
    }

    /* User bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: #EFF6FF !important; border: 1px solid #BFDBFE !important;
        border-radius: 16px 16px 4px 16px !important;
        padding: 14px 18px !important; margin: 0 0 16px auto !important;
        max-width: 80% !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) p,
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) span,
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div {
        color: #1A1B22 !important;
    }

    /* Assistant bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
        border-radius: 16px 16px 16px 4px !important;
        padding: 18px 20px !important; margin: 0 auto 16px 0 !important;
        max-width: 90% !important;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) p,
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) span,
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div {
        color: #1A1B22 !important;
    }

    /* Avatars */
    div[data-testid="chatAvatarIcon-user"] {
        display: none !important;
    }
    div[data-testid="chatAvatarIcon-assistant"] {
        width: 40px !important; height: 40px !important; min-width: 40px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        background: #1E40AF !important; border-radius: 50% !important;
        font-size: 1.1rem !important; color: #FFFFFF !important;
        margin-right: 12px !important;
    }

    /* ── Chat Input (Command Center) ── */
    div[data-testid="stChatInput"] {
        position: fixed !important; bottom: 0 !important;
        left: 50% !important; transform: translateX(-50%) !important;
        max-width: 800px !important; width: calc(100% - 48px) !important;
        padding: 20px 0 28px !important;
        background: linear-gradient(to bottom, transparent, #F8FAFC 35%) !important;
        z-index: 100 !important;
    }
    div[data-testid="stChatInput"] > div {
        background: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important; padding: 4px !important;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stChatInput"] textarea {
        border: none !important; background: transparent !important;
        border-radius: 12px !important;
        padding: 14px 18px !important; font-size: 0.95rem !important;
        color: #1A1B22 !important; min-height: 52px !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder { color: #94A3B8 !important; }
    div[data-testid="stChatInput"] textarea:focus { box-shadow: none !important; }
    div[data-testid="stChatInput"] button {
        background: #1E40AF !important; color: #FFFFFF !important;
        border-radius: 12px !important; width: 44px !important; height: 44px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        border: none !important; cursor: pointer !important;
        transition: background 0.15s !important; margin-right: 4px !important;
    }
    div[data-testid="stChatInput"] button:hover { background: #00288E !important; }
    div[data-testid="stChatInput"] button::before { content: "send"; font-family: 'Material Symbols Outlined'; }

    .footer-note {
        text-align: center; font-size: 0.7rem; color: #94A3B8;
        margin-top: 8px; letter-spacing: 0.02em; font-weight: 500;
    }

    .main > div { padding-bottom: 120px !important; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 10px !important; font-weight: 500 !important;
        font-size: 0.9rem !important; height: 40px !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .stButton > button[kind="primary"] { background: #1E40AF !important; color: white !important; }

    hr { margin: 24px 0 !important; border: none !important; border-top: 1px solid #E2E8F0 !important; }

    .stAlert { border-radius: 12px !important; border: none !important; padding: 12px 16px !important; }
    .stSpinner > div { border-color: #1E40AF !important; }
    .stSuccess { background: #F0FDF4 !important; color: #166534 !important; border: 1px solid #BBF7D0 !important; }
    .stError { background: #FEF2F2 !important; color: #991B1B !important; border: 1px solid #FECACA !important; }

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) ul,
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) ol {
        padding-left: 1.5rem !important; margin: 0.5rem 0 !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) li {
        margin-bottom: 0.25rem !important;
    }

    /* ── Mic Container ── */
    .mic-container {
        display: flex !important; justify-content: center !important;
        margin: 8px auto 4px !important; max-width: 800px !important;
    }
    .mic-container button {
        border-radius: 50% !important; width: 40px !important; height: 40px !important;
        padding: 0 !important; display: flex !important; align-items: center !important;
        justify-content: center !important; border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important; cursor: pointer !important;
        font-size: 1.2rem !important; line-height: 1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important; transition: all 0.15s ease !important;
    }
    .mic-container button:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; border-color: #1E40AF !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TOP APPBAR
# ============================================================
st.markdown("""
<div class="appbar">
    <div class="appbar-logo">🧠 MentorAI</div>
    <div class="appbar-nav">
        <span class="active">Consultas</span>
        <span>Progreso</span>
        <span>Recursos</span>
    </div>
    <div class="appbar-actions">
        <span class="material-symbols-outlined">settings</span>
        <span class="material-symbols-outlined">account_circle</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# EXECUTIVE HEADER
# ============================================================
st.markdown("""
<div class="exec-header">
    <h2>🧠 MentorAI</h2>
    <div class="exec-badge">
        <div class="dot"></div>
        <span>Orientación Activa</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 2. CARGA DEL MOTOR XGBOOST
# ============================================================
@st.cache_resource
def load_mentor_engine():
    model_path = "modelos/motor_completo.joblib"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        class MockEngine:
            def recommend(self, perfil, top_k=5, include_details=True):
                import random
                carreras = [
                    "Datos e IA",
                    "Tecnología Core",
                    "Diseño UX/UI",
                    "Negocios Tech",
                    "Marketing Digital"
                ]
                random.shuffle(carreras)
                return [
                    {
                        "rank": i + 1,
                        "carrera": c,
                        "confidence": round(random.uniform(70, 95) - (i * 3), 1)
                    }
                    for i, c in enumerate(carreras[:top_k])
                ]
        return MockEngine()

engine = load_mentor_engine()

# ============================================================
# 3. CONFIGURACIÓN GROQ
# ============================================================
API_KEY = st.secrets.get("GROQ_API_KEY", "")
if not API_KEY:
    st.error("⚠️ Configura GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
Eres MentorAI, un orientador vocacional empático y conversacional.
Tu objetivo es evaluar al usuario en 13 áreas (del 1 al 10), además de conocer su 'age' (edad) y 'education' (1=Secundaria, 2=Universidad, 3=Maestría, 4=Doctorado).

Las 13 áreas son: analytical, logical_reasoning, problem_solving, creativity, design, communication, empathy, social, teamwork, leadership, technology, business, stress_tolerance.

REGLAS:
1. NO hagas una lista aburrida de preguntas. Haz preguntas conversacionales e indaga sobre sus gustos. Haz máximo 2 o 3 preguntas a la vez.
2. Ve estimando internamente su puntaje del 1 al 10 en cada área según lo que responda.
3. CUANDO YA TENGAS SUFICIENTE INFORMACIÓN para estimar los 15 valores, DEJA DE HABLAR normalmente.
4. Tu ÚLTIMO mensaje debe ser ÚNICAMENTE un bloque de código JSON con esta estructura exacta (sin texto antes ni después):

```json
{
  "analytical": 8,
  "logical_reasoning": 7,
  "problem_solving": 9,
  "creativity": 4,
  "design": 3,
  "communication": 8,
  "empathy": 9,
  "social": 8,
  "teamwork": 10,
  "leadership": 7,
  "technology": 6,
  "business": 5,
  "stress_tolerance": 8,
  "age": 22,
  "education": 2
}
"""

# ============================================================
# 4. ESTADO DE SESIÓN
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": (
                "¡Hola! Soy MentorAI 🧠. Cuéntame un poco sobre ti: "
                "¿qué actividades o materias disfrutas más en tu día a día?"
            )
        }
    ]
    st.session_state.finished = False

# ============================================================
# 5. FUNCIÓN AUXILIAR
# ============================================================
def extract_json(text):
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            required_keys = {
                "analytical", "logical_reasoning", "problem_solving",
                "creativity", "design", "communication", "empathy",
                "social", "teamwork", "leadership", "technology",
                "business", "stress_tolerance", "age", "education"
            }
            if required_keys.issubset(data.keys()):
                return data
        except (json.JSONDecodeError, ValueError):
            pass
    return None

# ============================================================
# 6. CHAT - Messages
# ============================================================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "👤" if msg["role"] == "user" else "🧠"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# ============================================================
# 7. VOICE INPUT
# ============================================================
voice_prompt = None
if not st.session_state.finished:
    st.markdown('<div class="mic-container">', unsafe_allow_html=True)
    audio = mic_recorder("🎤", "🔴 Grabando...", format="wav", key="mentor_mic")
    st.markdown('</div>', unsafe_allow_html=True)
    if audio is not None:
        try:
            with st.spinner("Transcribiendo audio..."):
                result = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=("audio.wav", audio["bytes"], "audio/wav")
                )
                voice_prompt = result.text
        except Exception as e:
            st.error(f"Error al transcribir audio: {e}")

# ============================================================
# 8. TEXT INPUT & PROCESSING
# ============================================================
prompt = voice_prompt or st.chat_input(
    "Escribe tu respuesta aquí..."
    if not st.session_state.finished
    else "La evaluación ha finalizado"
)

if prompt and not st.session_state.finished:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.7
            )
            llm_reply = response.choices[0].message.content

            datos_llm = extract_json(llm_reply)
            if datos_llm:
                st.session_state.finished = True
                with st.spinner("Analizando tus respuestas..."):
                    import time
                    time.sleep(0.5)
                message_placeholder.success(
                    "✅ ¡Perfil completado! Generando tu mapa vocacional..."
                )

                edu_map = {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.9}
                perfil_usuario = {
                    "analytical": datos_llm.get("analytical", 5) / 10.0,
                    "logical_reasoning": datos_llm.get("logical_reasoning", 5) / 10.0,
                    "problem_solving": datos_llm.get("problem_solving", 5) / 10.0,
                    "creativity": datos_llm.get("creativity", 5) / 10.0,
                    "design": datos_llm.get("design", 5) / 10.0,
                    "communication": datos_llm.get("communication", 5) / 10.0,
                    "empathy": datos_llm.get("empathy", 5) / 10.0,
                    "social": datos_llm.get("social", 5) / 10.0,
                    "teamwork": datos_llm.get("teamwork", 5) / 10.0,
                    "leadership": datos_llm.get("leadership", 5) / 10.0,
                    "technology": datos_llm.get("technology", 5) / 10.0,
                    "business": datos_llm.get("business", 5) / 10.0,
                    "stress_tolerance": datos_llm.get("stress_tolerance", 5) / 10.0,
                    "education": edu_map.get(int(datos_llm.get("education", 2)), 0.5),
                    "age": min(datos_llm.get("age", 20) / 65.0, 1.0)
                }

                recomendaciones = engine.recommend(
                    perfil_usuario, top_k=3, include_details=True
                )
                df_res = pd.DataFrame(recomendaciones)
                top_1 = df_res.iloc[0]

                st.markdown("---")
                st.markdown(
                    f"<h2 style='text-align:center; color:#1E293B; font-size:1.3rem;'>"
                    f"🎯 Tu carrera ideal: "
                    f"<span style='color:#2563EB;'>{top_1['carrera'].replace('_', ' ').title()}</span>"
                    f"</h2>",
                    unsafe_allow_html=True
                )

                c1, c2 = st.columns(2, gap="medium")

                with c1:
                    labels = [
                        "Analítico", "Razonamiento", "Problemas",
                        "Creatividad", "Diseño", "Comunicación",
                        "Empatía", "Social", "Trabajo en Equipo",
                        "Liderazgo", "Tecnología", "Negocios",
                        "Tolerancia al Estrés"
                    ]
                    values = [
                        datos_llm.get("analytical", 5),
                        datos_llm.get("logical_reasoning", 5),
                        datos_llm.get("problem_solving", 5),
                        datos_llm.get("creativity", 5),
                        datos_llm.get("design", 5),
                        datos_llm.get("communication", 5),
                        datos_llm.get("empathy", 5),
                        datos_llm.get("social", 5),
                        datos_llm.get("teamwork", 5),
                        datos_llm.get("leadership", 5),
                        datos_llm.get("technology", 5),
                        datos_llm.get("business", 5),
                        datos_llm.get("stress_tolerance", 5)
                    ]
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=labels + [labels[0]],
                        fill="toself",
                        fillcolor="rgba(37, 99, 235, 0.2)",
                        line=dict(color="#2563EB", width=2.5),
                        name="Tu perfil"
                    ))
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 10],
                                tickfont=dict(size=9, color="#94A3B8"),
                                gridcolor="#E2E8F0"
                            ),
                            angularaxis=dict(
                                tickfont=dict(size=9, color="#475569")
                            ),
                            bgcolor="rgba(0,0,0,0)"
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        height=320,
                        margin=dict(l=40, r=40, t=10, b=10)
                    )
                    st.plotly_chart(fig_radar, width="stretch")

                with c2:
                    fig_bar = go.Figure(go.Bar(
                        x=df_res["confidence"],
                        y=df_res["carrera"].str.replace("_", " ").str.title(),
                        orientation="h",
                        marker=dict(
                            color=df_res["confidence"],
                            colorscale=[[0, "#BFDBFE"], [1, "#2563EB"]]
                        ),
                        text=df_res["confidence"].apply(lambda v: f"{v}%"),
                        textposition="outside",
                        textfont=dict(size=12, color="#1E293B")
                    ))
                    fig_bar.update_layout(
                        yaxis=dict(
                            autorange="reversed",
                            tickfont=dict(size=12, color="#1E293B")
                        ),
                        xaxis=dict(range=[0, 100], visible=False),
                        height=240,
                        margin=dict(l=10, r=40, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False
                    )
                    st.plotly_chart(fig_bar, width="stretch")

                st.markdown("---")
                if st.button(
                    "🔄 Volver a comenzar",
                    use_container_width=True,
                    type="primary"
                ):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.finished = False
                    st.session_state.messages = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "assistant", "content": "¡Hola! Soy MentorAI 🧠. Cuéntame un poco sobre ti: ¿qué actividades o materias disfrutas más?"}
                    ]
                    st.rerun()

            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": llm_reply}
                )
                message_placeholder.markdown(llm_reply)

        except Exception as e:
            message_placeholder.error(f"Error de API: {e}")

# ============================================================
# REQUIREMENTS.TXT
# ============================================================
# Crea un archivo requirements.txt con:
#
# streamlit>=1.28.0
# pandas>=1.5.0
# numpy>=1.24.0
# plotly>=5.15.0
# joblib>=1.2.0
# openai>=1.0.0
# streamlit-mic-recorder>=0.0.8
#
# Secrets (.streamlit/secrets.toml):
# GROQ_API_KEY = "tu-api-key-de-groq-aqui"
