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

    * { font-family: 'Inter', -apple-system, sans-serif !important; }
    .stApp { background: #F8FAFC; }
    header, footer, .stDeployButton, section[data-testid="stSidebar"] { display: none !important; }

    /* Contenedor central de la app */
    .block-container { max-width: 800px !important; padding-top: 100px !important; margin: 0 auto !important; }

    /* ── Barra Superior Profesional (Fix de Iconos Rompibles) ── */
    .appbar {
        position: fixed; top: 0; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; height: 65px;
        background: #FFFFFF; border-bottom: 1px solid #E2E8F0;
        z-index: 999; padding: 0 24px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .appbar-logo { font-size: 1.2rem; font-weight: 700; color: #00288E; display: flex; align-items: center; gap: 8px; }
    .appbar-nav { display: flex; gap: 24px; align-items: center; }
    .appbar-nav span { font-size: 0.9rem; color: #64748B; cursor: pointer; font-weight: 500; transition: color 0.15s; }
    .appbar-nav span.active { color: #00288E; font-weight: 600; border-bottom: 2px solid #00288E; padding-bottom: 20px; }
    .appbar-actions { display: flex; gap: 16px; align-items: center; color: #64748B; }
    .appbar-actions svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 2; cursor: pointer; }

    /* ── Burbujas de Chat Premium ── */
    div[data-testid="stChatMessage"] { background: transparent !important; margin-bottom: 20px !important; padding: 0 !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: #EFF6FF !important; border: 1px solid #BFDBFE !important; border-radius: 20px 20px 4px 20px !important;
        padding: 14px 18px !important; max-width: 80% !important; margin-left: auto !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 20px 20px 20px 4px !important;
        padding: 18px 20px !important; max-width: 90% !important; box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
    }
    div[data-testid="chatAvatarIcon-user"], div[data-testid="chatAvatarIcon-assistant"] { display: none !important; }

    /* ── CAJA ESTILO GEMINI (Píldora Unificada) ── */
    div[data-testid="stChatInput"] {
        position: fixed !important; bottom: 20px !important; left: 50% !important; transform: translateX(-50%) !important;
        max-width: 800px !important; width: calc(100% - 32px) !important; padding: 0 !important; background: transparent !important; z-index: 999 !important;
    }
    div[data-testid="stChatInput"] > div {
        background: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 32px !important;
        padding: 4px 6px 4px 12px !important; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.06) !important;
        display: flex !important; align-items: center !important;
    }
    div[data-testid="stChatInput"] textarea {
        border: none !important; background: transparent !important; box-shadow: none !important;
        padding: 12px 90px 12px 14px !important; /* Espacio reservado para el micro flotante */
        font-size: 0.98rem !important; color: #1E293B !important;
    }

    /* Botón enviar circular azul */
    div[data-testid="stChatInput"] button {
        background: #2563EB !important; color: #FFFFFF !important; border-radius: 50% !important;
        width: 40px !important; height: 40px !important; display: flex !important; align-items: center !important; justify-content: center !important;
    }
    div[data-testid="stChatInput"] button::before { content: "↑" !important; font-size: 1.4rem !important; font-weight: bold; }
    div[data-testid="stChatInput"] button svg { display: none !important; }

    /* ── MICRÓFONO INCRUSTADO A LA DERECHA ── */
    .mic-container { position: fixed; bottom: 27px; left: calc(50% + 400px - 105px); z-index: 1000; }
    @media (max-width: 832px) { .mic-container { left: auto; right: 75px; } }
    .mic-container button {
        border: none !important; background: transparent !important; width: 36px !important; height: 36px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        color: #64748B !important; font-size: 1.25rem !important; cursor: pointer !important; box-shadow: none !important;
    }
    .mic-container button:hover { color: #2563EB !important; background: #F1F5F9 !important; border-radius: 50% !important; }

    /* Sugerencias en Grilla */
    .stButton > button {
        background: #FFFFFF !important; color: #334155 !important; border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important; height: 50px !important; font-size: 0.92rem !important; font-weight: 500 !important;
        transition: all 0.2s !important; width: 100% !important;
    }
    .stButton > button:hover { border-color: #3B82F6 !important; background: #EFF6FF !important; color: #1D4ED8 !important; transform: translateY(-1px); }
    .main > div { padding-bottom: 110px !important; }
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
        <svg viewBox="0 0 24 24"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.1a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
        <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
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
# 7. SUGGESTION CARDS (only before first user interaction)
# ============================================================
if "suggestion" not in st.session_state:
    st.session_state.suggestion = None

has_user_msgs = any(m["role"] == "user" for m in st.session_state.messages)
if not has_user_msgs and not st.session_state.get("suggestion"):
    st.markdown('<p style="text-align:center;color:#64748B;font-size:0.85rem;margin:20px 0 8px;font-weight:500;">¿Por dónde quieres empezar?</p>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3, gap="small")
    with g1:
        if st.button("🎓 Explorar carreras", key="sug_carreras", use_container_width=True):
            st.session_state.suggestion = "Quiero explorar opciones de carrera profesional"
            st.rerun()
    with g2:
        if st.button("💡 Descubrir fortalezas", key="sug_fortalezas", use_container_width=True):
            st.session_state.suggestion = "Ayúdame a descubrir mis fortalezas y habilidades"
            st.rerun()
    with g3:
        if st.button("🚀 Planificar futuro", key="sug_plan", use_container_width=True):
            st.session_state.suggestion = "Necesito ayuda para planificar mi futuro profesional"
            st.rerun()

# ============================================================
# 8. VOICE INPUT
# ============================================================
voice_prompt = None
if not st.session_state.finished:
    st.markdown('<div class="mic-container">', unsafe_allow_html=True)
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🔴", format="wav", key="mentor_mic")
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
# 9. TEXT INPUT & PROCESSING
# ============================================================
if st.session_state.get("suggestion"):
    prompt = st.session_state.suggestion
    st.session_state.suggestion = None
else:
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
