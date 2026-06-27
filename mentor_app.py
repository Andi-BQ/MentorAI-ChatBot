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

    .block-container { max-width: 800px !important; padding-top: 100px !important; margin: 0 auto !important; }

    .appbar-container {
        position: fixed; top: 0; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 800px; height: 65px;
        background: #FFFFFF; border-bottom: 1px solid #E2E8F0;
        z-index: 999; padding: 0 24px;
        display: flex; align-items: center; justify-content: space-between;
        box-sizing: border-box;
    }
    .appbar-logo { font-size: 1.25rem; font-weight: 700; color: #00288E; display: flex; align-items: center; gap: 8px; }
    .appbar-right-zone { display: flex; gap: 12px; align-items: center; }

    div[data-testid="stPopover"] > button {
        background: transparent !important; border: none !important; padding: 0 !important;
        color: #64748B !important; width: 38px !important; height: 38px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        border-radius: 50% !important; box-shadow: none !important; transition: background 0.15s !important;
    }
    div[data-testid="stPopover"] > button:hover { background: #F1F5F9 !important; color: #00288E !important; }

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

    div[data-testid="stChatInput"] {
        position: fixed !important; bottom: 20px !important; left: 50% !important; transform: translateX(-50%) !important;
        max-width: 800px !important; width: calc(100% - 32px) !important; padding: 0 !important; background: transparent !important; z-index: 999 !important;
    }
    div[data-testid="stChatInput"] > div {
        background: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 32px !important;
        padding: 4px 6px 4px 14px !important; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.06) !important;
    }
    div[data-testid="stChatInput"] textarea {
        border: none !important; background: transparent !important; box-shadow: none !important;
        padding: 12px 105px 12px 0px !important;
        font-size: 0.98rem !important; color: #1E293B !important; min-height: 48px !important;
    }

    div[data-testid="stChatInput"] button {
        background: #2563EB !important; color: #FFFFFF !important; border-radius: 50% !important;
        width: 40px !important; height: 40px !important; display: flex !important; align-items: center !important; justify-content: center !important;
        position: absolute !important; right: 8px !important; bottom: 8px !important; border: none !important; z-index: 1002 !important;
    }
    div[data-testid="stChatInput"] button::before { content: "↑" !important; font-size: 1.4rem !important; font-weight: 700; }
    div[data-testid="stChatInput"] button svg { display: none !important; }

    .mic-container {
        position: fixed; bottom: 28px;
        left: calc(50% + 400px - 102px);
        z-index: 1001;
    }
    @media (max-width: 832px) { .mic-container { left: auto; right: 58px; } }
    .mic-container button {
        border: none !important; background: transparent !important; width: 40px !important; height: 40px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        color: #64748B !important; font-size: 1.25rem !important; cursor: pointer !important; box-shadow: none !important;
    }
    .mic-container button:hover { color: #2563EB !important; background: #F1F5F9 !important; border-radius: 50% !important; }

    .main > div { padding-bottom: 120px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TOP APPBAR CON POPOVERS INTERACTIVOS
# ============================================================
st.markdown('<div class="appbar-container"><div class="appbar-logo">🧠 MentorAI</div><div class="appbar-right-zone">', unsafe_allow_html=True)

col_icon1, col_icon2 = st.columns([1, 1])

with col_icon1:
    with st.popover("⚙️", help="Configuración del Sistema"):
        st.markdown("### ⚙️ Preferencias")
        st.toggle("Modo Oscuro", value=False)
        st.slider("Temperatura", 0.0, 1.0, 0.7)
        st.caption("Configuración de Llama-3.3")

with col_icon2:
    with st.popover("👤", help="Ver Perfil"):
        st.markdown("### 👤 Perfil del Estudiante")
        st.info("Estado: Evaluación Vocacional Activa")
        if st.button("Limpiar historial de chat"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================================
# 2. CARGA DEL MOTOR RECOMENDADOR
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
                carreras = ["Datos e IA", "Tecnología Core", "Diseño UX/UI", "Negocios Tech", "Marketing Digital"]
                random.shuffle(carreras)
                return [{"rank": i + 1, "carrera": c, "confidence": round(random.uniform(70, 95) - (i * 3), 1)} for i, c in enumerate(carreras[:top_k])]
        return MockEngine()

engine = load_mentor_engine()

# ============================================================
# 3. CONFIGURACIÓN API
# ============================================================
API_KEY = st.secrets.get("GROQ_API_KEY", "")
if not API_KEY:
    st.error("⚠️ Configura GROQ_API_KEY en tus Secrets de Streamlit.")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

SYSTEM_PROMPT = """
Eres MentorAI, un orientador vocacional empático y conversacional.
Evalúa al usuario en 13 áreas (del 1 al 10), además de conocer su 'age' y 'education' (1=Secundaria, 2=Universidad, 3=Maestría, 4=Doctorado).
Áreas: analytical, logical_reasoning, problem_solving, creativity, design, communication, empathy, social, teamwork, leadership, technology, business, stress_tolerance.

REGLAS:
1. Haz preguntas fluidas e investiga sus pasiones. Máximo 2 preguntas por mensaje.
2. Cuando tengas datos suficientes para los 15 valores, corta la conversación y responde ÚNICAMENTE con el bloque JSON solicitado.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "¡Hola! Soy MentorAI 🧠. Cuéntame un poco sobre ti: ¿qué actividades o materias disfrutas más en tu día a día?"}
    ]
    st.session_state.finished = False

def extract_json(text):
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            required_keys = {"analytical", "logical_reasoning", "problem_solving", "creativity", "design", "communication", "empathy", "social", "teamwork", "leadership", "technology", "business", "stress_tolerance", "age", "education"}
            if required_keys.issubset(data.keys()): return data
        except: pass
    return None

# ============================================================
# 4. RENDERING DE MENSAJES
# ============================================================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if len(st.session_state.messages) == 2 and not st.session_state.finished:
    st.markdown("<p style='text-align:center; color:#64748B; font-weight:500; margin-top:20px; margin-bottom:12px;'>¿Por dónde quieres empezar?</p>", unsafe_allow_html=True)
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        if st.button("🎓 Explorar carreras"): st.session_state.messages.append({"role": "user", "content": "Quiero empezar explorando mis opciones de carreras profesionales."}) ; st.rerun()
    with col_s2:
        if st.button("💡 Descubrir fortalezas"): st.session_state.messages.append({"role": "user", "content": "Me gustaría analizar cuáles son mis mayores habilidades y fortalezas."}) ; st.rerun()
    with col_s3:
        if st.button("🚀 Planificar futuro"): st.session_state.messages.append({"role": "user", "content": "Quiero armar una estrategia paso a paso para mi desarrollo futuro."}) ; st.rerun()

# ============================================================
# 5. ENTRADA DE AUDIO
# ============================================================
voice_prompt = None
if not st.session_state.finished:
    st.markdown('<div class="mic-container">', unsafe_allow_html=True)
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🔴", format="wav", key="mentor_mic")
    st.markdown('</div>', unsafe_allow_html=True)
    if audio is not None:
        try:
            with st.spinner("Transcribiendo..."):
                result = client.audio.transcriptions.create(model="whisper-large-v3", file=("audio.wav", audio["bytes"], "audio/wav"))
                voice_prompt = result.text
        except Exception as e:
            st.error(f"Error en audio: {e}")

# ============================================================
# 6. ENTRADA DE TEXTO Y PROCESAMIENTO
# ============================================================
prompt = voice_prompt or st.chat_input("Escribe tu respuesta aquí..." if not st.session_state.finished else "Evaluación finalizada")

if prompt and not st.session_state.finished:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if len(st.session_state.messages) > 2 and st.session_state.messages[-1]["role"] == "user" and not st.session_state.finished:
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, temperature=0.7)
            llm_reply = response.choices[0].message.content
            datos_llm = extract_json(llm_reply)

            if datos_llm:
                st.session_state.finished = True
                message_placeholder.success("✅ ¡Perfil completado! Generando mapa vocacional...")

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

                recomendaciones = engine.recommend(perfil_usuario, top_k=3, include_details=True)
                df_res = pd.DataFrame(recomendaciones)
                top_1 = df_res.iloc[0]

                st.markdown("---")
                st.markdown(f"<h2 style='text-align:center; color:#1E293B; font-size:1.3rem;'>🎯 Tu carrera ideal: <span style='color:#2563EB;'>{top_1['carrera'].replace('_', ' ').title()}</span></h2>", unsafe_allow_html=True)

                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    labels = ["Analítico", "Razonamiento", "Problemas", "Creatividad", "Diseño", "Comunicación", "Empatía", "Social", "Trabajo en Equipo", "Liderazgo", "Tecnología", "Negocios", "Tolerancia Estrés"]
                    values = [datos_llm.get(k, 5) for k in ["analytical", "logical_reasoning", "problem_solving", "creativity", "design", "communication", "empathy", "social", "teamwork", "leadership", "technology", "business", "stress_tolerance"]]
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=values + [values[0]], theta=labels + [labels[0]], fill="toself", fillcolor="rgba(37, 99, 235, 0.2)", line=dict(color="#2563EB", width=2.5)))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=9, color="#94A3B8"), gridcolor="#E2E8F0"), angularaxis=dict(tickfont=dict(size=9, color="#475569")), bgcolor="rgba(0,0,0,0)"), paper_bgcolor="rgba(0,0,0,0)", showlegend=False, height=320, margin=dict(l=40, r=40, t=10, b=10))
                    st.plotly_chart(fig_radar, width="stretch")

                with c2:
                    fig_bar = go.Figure(go.Bar(x=df_res["confidence"], y=df_res["carrera"].str.replace("_", " ").str.title(), orientation="h", marker=dict(color=df_res["confidence"], colorscale=[[0, "#BFDBFE"], [1, "#2563EB"]]), text=df_res["confidence"].apply(lambda v: f"{v}%"), textposition="outside"))
                    fig_bar.update_layout(yaxis=dict(autorange="reversed", tickfont=dict(size=12, color="#1E293B")), xaxis=dict(range=[0, 100], visible=False), height=240, margin=dict(l=10, r=40, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig_bar, width="stretch")

                st.markdown("---")
                if st.button("🔄 Volver a comenzar", use_container_width=True, type="primary"):
                    for key in list(st.session_state.keys()): del st.session_state[key]
                    st.session_state.finished = False
                    st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": llm_reply})
                message_placeholder.markdown(llm_reply)
                st.rerun()
        except Exception as e:
            message_placeholder.error(f"Error de API: {e}")
