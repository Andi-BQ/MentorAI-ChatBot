import reflex as rx
from .state import State


class AppState(rx.State):
    show_settings: bool = False
    show_profile: bool = False

    def toggle_settings(self):
        self.show_settings = not self.show_settings

    def toggle_profile(self):
        self.show_profile = not self.show_profile



MIC_JS = """
window.__audioStream = null;
window.__mediaRecorder = null;
window.__audioChunks = [];

window.startMicRecording = function() {
    return navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            window.__audioStream = stream;
            window.__mediaRecorder = new MediaRecorder(stream);
            window.__audioChunks = [];
            window.__mediaRecorder.ondataavailable = function(e) {
                if (e.data.size > 0) window.__audioChunks.push(e.data);
            };
            window.__mediaRecorder.start();
        })
        .catch(function(err) {
            console.error('Error de micrófono:', err);
        });
};

window.stopMicRecording = function() {
    return new Promise(function(resolve) {
        if (!window.__mediaRecorder || window.__mediaRecorder.state === 'inactive') {
            resolve('');
            return;
        }
        window.__mediaRecorder.onstop = function() {
            var blob = new Blob(window.__audioChunks, { type: 'audio/webm' });
            var reader = new FileReader();
            reader.onload = function() {
                if (window.__audioStream) {
                    window.__audioStream.getTracks().forEach(function(t) { t.stop(); });
                }
                resolve(reader.result);
            };
            reader.readAsDataURL(blob);
        };
        window.__mediaRecorder.stop();
    });
};
"""

STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', -apple-system, sans-serif !important; }
.chat-user-msg {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 20px 20px 4px 20px !important;
    padding: 14px 18px !important;
    max-width: 80% !important;
    margin-left: auto !important;
    color: #1E293B !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
}
.chat-assistant-msg {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px 20px 20px 4px !important;
    padding: 18px 20px !important;
    max-width: 90% !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
    color: #1E293B !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}
.typing-dot {
    animation: blink 1.4s infinite both;
}
.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
    0% { opacity: 0.2; }
    20% { opacity: 1; }
    100% { opacity: 0.2; }
}
.recording-indicator {
    animation: recPulse 1s infinite;
}
@keyframes recPulse {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
}
"""


def render_message(msg: dict) -> rx.Component:
    is_user = msg["role"] == "user"
    return rx.box(
        rx.markdown(msg["content"]),
        class_name="chat-user-msg" if is_user else "chat-assistant-msg",
        margin_bottom="16px",
        width="100%",
    )


def suggestion_btn(text: str, label: str) -> rx.Component:
    return rx.button(
        label,
        on_click=lambda: State.send_suggestion(text),
        bg="#FFFFFF",
        color="#475569",
        border="1px solid #E2E8F0",
        border_radius="12px",
        padding="10px 16px",
        font_size="0.85rem",
        font_weight="500",
        cursor="pointer",
        _hover={
            "bg": "#F8FAFC",
            "border_color": "#2563EB",
            "color": "#2563EB",
        },
        width="100%",
    )


def suggestions() -> rx.Component:
    return rx.vstack(
        rx.text(
            "¿Por dónde quieres empezar?",
            color="#64748B",
            font_weight="500",
            font_size="0.9rem",
            text_align="center",
            margin_top="20px",
            margin_bottom="8px",
        ),
        rx.hstack(
            suggestion_btn(
                "Quiero empezar explorando mis opciones de carreras profesionales.",
                "🎓 Explorar carreras",
            ),
            suggestion_btn(
                "Me gustaría analizar cuáles son mis mayores habilidades y fortalezas.",
                "💡 Descubrir fortalezas",
            ),
            suggestion_btn(
                "Quiero armar una estrategia paso a paso para mi desarrollo futuro.",
                "🚀 Planificar futuro",
            ),
            spacing="8px",
            width="100%",
        ),
        width="100%",
        max_width="800px",
        margin="0 auto",
        padding="0 16px",
    )


def typing_indicator() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(rx.text("●", font_size="0.6rem", color="#2563EB"), class_name="typing-dot"),
            rx.box(rx.text("●", font_size="0.6rem", color="#2563EB"), class_name="typing-dot"),
            rx.box(rx.text("●", font_size="0.6rem", color="#2563EB"), class_name="typing-dot"),
            spacing="3px",
            align="center",
        ),
        class_name="chat-assistant-msg",
        margin_bottom="16px",
        width="auto",
        display="inline-block",
    )


def results_view() -> rx.Component:
    return rx.vstack(
        rx.markdown("---"),
        rx.heading(
            "🎯 Tu carrera ideal",
            font_size="1.3rem",
            color="#1E293B",
            text_align="center",
            margin_top="24px",
        ),
        rx.heading(
            State.top_career.replace("_", " ").title(),
            font_size="1.8rem",
            color="#2563EB",
            text_align="center",
            font_weight="700",
            margin_bottom="24px",
        ),
        rx.cond(
            State.radar_html != "",
            rx.hstack(
                rx.box(
                    rx.html(State.radar_html),
                    width="100%",
                ),
                rx.box(
                    rx.html(State.bar_html),
                    width="100%",
                ),
                spacing="16px",
                width="100%",
                max_width="800px",
                padding="0 16px",
                flex_wrap="wrap",
            ),
        ),
        rx.markdown("---"),
        rx.button(
            "🔄 Volver a comenzar",
            on_click=State.reset_chat,
            bg="#2563EB",
            color="#FFFFFF",
            font_weight="600",
            font_size="1rem",
            padding="14px 32px",
            border_radius="12px",
            cursor="pointer",
            _hover={"bg": "#1D4ED8"},
            width="100%",
            max_width="400px",
        ),
        width="100%",
        align="center",
        padding_bottom="40px",
    )


def input_pill() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.input(
                value=State.input_text,
                on_change=State.set_input,
                placeholder="Escribe tu respuesta aquí...",
                bg="#FFFFFF",
                border="none",
                outline="none",
                border_radius="32px",
                padding="12px 16px",
                font_size="0.95rem",
                width="100%",
                _focus={"outline": "none", "border": "none", "box_shadow": "none"},
            ),
            rx.button(
                rx.cond(
                    State.is_recording,
                    rx.text("🔴", class_name="recording-indicator"),
                    rx.text("🎤"),
                ),
                on_click=State.toggle_recording,
                bg="transparent",
                color="#64748B",
                border="none",
                font_size="1.2rem",
                width="40px",
                height="40px",
                border_radius="50%",
                cursor="pointer",
                _hover={"bg": "#F1F5F9", "color": "#2563EB"},
                flex_shrink="0",
                padding="0",
            ),
            rx.button(
                "↑",
                on_click=State.send_from_input,
                bg="#2563EB",
                color="#FFFFFF",
                border="none",
                border_radius="50%",
                width="40px",
                height="40px",
                font_size="1.3rem",
                font_weight="700",
                cursor="pointer",
                _hover={"bg": "#1D4ED8"},
                flex_shrink="0",
                padding="0",
                margin_right="4px",
            ),
            align="center",
            bg="#FFFFFF",
            border="1px solid #CBD5E1",
            border_radius="32px",
            padding="4px 4px 4px 16px",
            box_shadow="0 10px 30px -5px rgba(0,0,0,0.06)",
            width="100%",
        ),
        position="fixed",
        bottom="20px",
        left="50%",
        transform="translateX(-50%)",
        width="calc(100% - 32px)",
        max_width="800px",
        z_index="999",
    )


def index() -> rx.Component:
    return rx.box(
        rx.script(MIC_JS),
        rx.style(STYLES),

        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.text("🧠", font_size="1.5rem"),
                    rx.text(
                        "MentorAI",
                        font_size="1.25rem",
                        font_weight="700",
                        color="#00288E",
                    ),
                    spacing="8px",
                    align="center",
                ),
                rx.hstack(
                    rx.box(
                        rx.button(
                            "⚙️",
                            on_click=AppState.toggle_settings,
                            bg="#EFF6FF" if AppState.show_settings else "transparent",
                            border="none",
                            color="#00288E" if AppState.show_settings else "#64748B",
                            width="38px",
                            height="38px",
                            border_radius="50%",
                            font_size="1.2rem",
                            cursor="pointer",
                            _hover={"bg": "#F1F5F9", "color": "#00288E"},
                        ),
                        rx.cond(
                            AppState.show_settings,
                            rx.box(
                                rx.vstack(
                                    rx.text("⚙️ Preferencias", font_weight="600", font_size="1rem", color="#1E293B"),
                                    rx.text("Temperatura del modelo", font_size="0.8rem", color="#64748B", margin_top="8px"),
                                    rx.slider(
                                        default_value=State.temperature,
                                        min=0,
                                        max=100,
                                        on_change=State.set_temperature,
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        rx.text("0.0", font_size="0.75rem", color="#94A3B8"),
                                        rx.text("1.0", font_size="0.75rem", color="#94A3B8"),
                                        justify="between",
                                        width="100%",
                                    ),
                                    rx.text("Configuración de Llama-3.3", font_size="0.75rem", color="#94A3B8", margin_top="4px"),
                                    padding="16px",
                                    min_width="220px",
                                ),
                                position="absolute",
                                top="48px",
                                right="0",
                                bg="#FFFFFF",
                                border="1px solid #E2E8F0",
                                border_radius="12px",
                                box_shadow="0 10px 30px -5px rgba(0,0,0,0.1)",
                                z_index="1000",
                            ),
                        ),
                        position="relative",
                    ),
                    rx.box(
                        rx.button(
                            "👤",
                            on_click=AppState.toggle_profile,
                            bg="#EFF6FF" if AppState.show_profile else "transparent",
                            border="none",
                            color="#00288E" if AppState.show_profile else "#64748B",
                            width="38px",
                            height="38px",
                            border_radius="50%",
                            font_size="1.2rem",
                            cursor="pointer",
                            _hover={"bg": "#F1F5F9", "color": "#00288E"},
                        ),
                        rx.cond(
                            AppState.show_profile,
                            rx.box(
                                rx.vstack(
                                    rx.text("👤 Perfil del Estudiante", font_weight="600", font_size="1rem", color="#1E293B"),
                                    rx.box(
                                        rx.text("Estado:", font_size="0.85rem", color="#64748B"),
                                        rx.text("Evaluación Vocacional Activa", font_size="0.85rem", color="#2563EB", font_weight="500"),
                                        padding="8px 12px",
                                        bg="#EFF6FF",
                                        border_radius="8px",
                                        margin_top="8px",
                                        width="100%",
                                    ),
                                    rx.button(
                                        "Limpiar historial y reiniciar",
                                        on_click=State.reset_chat,
                                        bg="transparent",
                                        color="#EF4444",
                                        border="1px solid #FCA5A5",
                                        border_radius="8px",
                                        padding="8px 16px",
                                        font_size="0.85rem",
                                        cursor="pointer",
                                        _hover={"bg": "#FEF2F2"},
                                        width="100%",
                                        margin_top="12px",
                                    ),
                                    padding="16px",
                                    min_width="240px",
                                ),
                                position="absolute",
                                top="48px",
                                right="0",
                                bg="#FFFFFF",
                                border="1px solid #E2E8F0",
                                border_radius="12px",
                                box_shadow="0 10px 30px -5px rgba(0,0,0,0.1)",
                                z_index="1000",
                            ),
                        ),
                        position="relative",
                    ),
                    spacing="8px",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
                max_width="800px",
                margin="0 auto",
                height="100%",
                padding="0 24px",
            ),
            position="fixed",
            top="0",
            left="50%",
            transform="translateX(-50%)",
            width="100%",
            height="65px",
            bg="#FFFFFF",
            border_bottom="1px solid #E2E8F0",
            z_index="999",
        ),
        rx.box(
            rx.foreach(
                State.messages,
                lambda msg: rx.cond(
                    msg["role"] != "system",
                    render_message(msg),
                    rx.fragment(),
                ),
            ),
            rx.cond(
                State.show_suggestions,
                rx.cond(
                    State.finished,
                    rx.fragment(),
                    suggestions(),
                ),
            ),
            rx.cond(
                State.loading,
                rx.cond(
                    State.finished,
                    rx.fragment(),
                    typing_indicator(),
                ),
            ),
            rx.cond(
                State.finished,
                results_view(),
            ),
            max_width="800px",
            margin="0 auto",
            padding_top="85px",
            padding_bottom="100px",
            padding_left="16px",
            padding_right="16px",
            width="100%",
        ),
        rx.cond(
            State.finished,
            rx.fragment(),
            input_pill(),
        ),
        bg="#F8FAFC",
        min_height="100vh",
        width="100%",
    )


app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, sans-serif",
    },
)
app.add_page(index, route="/", title="MentorAI 🧠")
