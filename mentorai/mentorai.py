import reflex as rx
from .state import State


def user_bubble(content):
    return rx.box(
        rx.markdown(content),
        class_name="bg-indigo-600 text-white rounded-2xl rounded-tr-md px-4 py-3 max-w-[80%] shadow-sm",
    )


def assistant_bubble(content):
    return rx.box(
        rx.markdown(content),
        class_name="bg-white border border-slate-100 text-slate-800 rounded-2xl rounded-tl-md px-4 py-3 max-w-[80%] shadow-sm",
    )


def render_message(msg):
    return rx.cond(
        msg["role"] == "user",
        rx.box(user_bubble(msg["content"]), class_name="flex justify-end mb-3 w-full"),
        rx.box(assistant_bubble(msg["content"]), class_name="flex justify-start mb-3 w-full"),
    )


def suggestion_card(text, label, icon):
    return rx.box(
        rx.hstack(
            rx.text(icon, class_name="text-2xl flex-shrink-0"),
            rx.vstack(
                rx.text(label, class_name="font-semibold text-sm text-slate-800"),
                rx.text("Toca para empezar", class_name="text-xs text-slate-400"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        class_name="bg-white border border-slate-200 rounded-xl p-4 transition-all duration-200 cursor-pointer hover:border-indigo-500 hover:shadow-md",
        on_click=lambda: State.send_suggestion(text),
    )


def suggestions():
    return rx.vstack(
        rx.text(
            "¿Por dónde quieres empezar?",
            class_name="text-slate-500 font-medium text-sm text-center",
        ),
        rx.box(
            suggestion_card(
                "Quiero empezar explorando mis opciones de carreras profesionales.",
                "Explorar carreras",
                "🎓",
            ),
            suggestion_card(
                "Me gustaría analizar cuáles son mis mayores habilidades y fortalezas.",
                "Descubrir fortalezas",
                "💡",
            ),
            suggestion_card(
                "Quiero armar una estrategia paso a paso para mi desarrollo futuro.",
                "Planificar futuro",
                "🚀",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 w-full",
        ),
        class_name="w-full max-w-2xl mx-auto px-4 gap-4",
    )


def typing_indicator():
    return rx.box(
        rx.hstack(
            rx.box(class_name="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"),
            rx.box(class_name="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.1s]"),
            rx.box(class_name="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]"),
            spacing="1",
            align="center",
            class_name="px-3 py-2",
        ),
        class_name="bg-white border border-slate-100 shadow-sm rounded-2xl px-4 py-3 w-auto inline-block",
    )


def results_view():
    return rx.vstack(
        rx.box(class_name="w-full border-t border-slate-200 my-2"),
        rx.text("🎯 Tu carrera ideal", class_name="text-xl font-bold text-slate-800 text-center mt-4"),
        rx.text(
            State.top_career.replace("_", " ").title(),
            class_name="text-3xl font-bold text-indigo-600 text-center mb-6",
        ),
        rx.cond(
            State.radar_html != "",
            rx.box(
                rx.box(rx.html(State.radar_html), class_name="w-full md:w-1/2"),
                rx.box(rx.html(State.bar_html), class_name="w-full md:w-1/2"),
                class_name="flex flex-col md:flex-row gap-6 w-full max-w-4xl",
            ),
        ),
        rx.box(class_name="w-full border-t border-slate-200 my-4"),
        rx.button(
            rx.hstack(
                rx.text("🔄", class_name="text-lg"),
                rx.text("Volver a comenzar", class_name="font-semibold"),
                spacing="2",
                align="center",
            ),
            on_click=State.reset_chat,
            class_name="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 px-8 rounded-xl transition-all duration-200 shadow-sm w-full max-w-xs cursor-pointer border-none",
        ),
        class_name="w-full flex flex-col items-center gap-4 pb-16",
    )


def input_pill():
    return rx.box(
        rx.hstack(
            rx.input(
                value=State.input_text,
                on_change=State.set_input,
                placeholder="Escribe tu mensaje...",
                class_name="flex-1 bg-transparent border-none outline-none px-4 py-3.5 text-sm text-slate-700 placeholder:text-slate-400",
            ),
            rx.button(
                rx.cond(
                    State.is_recording,
                    rx.text("●", class_name="text-red-500 text-lg animate-pulse"),
                    rx.text("🎤", class_name="text-lg"),
                ),
                on_click=State.toggle_recording,
                class_name="w-9 h-9 flex items-center justify-center rounded-full bg-transparent hover:bg-slate-100 transition-colors duration-150 flex-shrink-0 border-none cursor-pointer",
            ),
            rx.button(
                rx.text("↑", class_name="text-white font-bold"),
                on_click=State.send_from_input,
                class_name="w-9 h-9 flex items-center justify-center rounded-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 transition-all duration-150 flex-shrink-0 border-none cursor-pointer shadow-sm",
            ),
            class_name="flex items-center gap-1.5 bg-white border border-slate-200 rounded-2xl pl-2 pr-1.5 py-1.5 shadow-[0_8px_30px_rgb(0,0,0,0.06)]",
            width="100%",
        ),
        class_name="fixed bottom-6 left-1/2 -translate-x-1/2 w-[calc(100%-32px)] max-w-3xl z-50",
    )


def settings_popup():
    return rx.box(
        rx.button(
            rx.text("⚙️", class_name="text-lg"),
            on_click=State.toggle_settings,
            class_name=rx.cond(
                State.show_settings,
                "w-9 h-9 flex items-center justify-center rounded-full bg-indigo-50 border-none cursor-pointer transition-colors duration-150",
                "w-9 h-9 flex items-center justify-center rounded-full bg-transparent hover:bg-slate-100 border-none cursor-pointer transition-colors duration-150",
            ),
        ),
        rx.cond(
            State.show_settings,
            rx.box(
                rx.vstack(
                    rx.text("Preferencias", class_name="font-semibold text-base text-slate-800"),
                    rx.text("Temperatura del modelo", class_name="text-xs text-slate-500 mt-2"),
                    rx.select(
                        ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"],
                        default_value="0.7",
                        on_change=State.set_temperature,
                        class_name="w-full",
                    ),
                    rx.text("Configuración de Llama-3.3", class_name="text-xs text-slate-400 mt-1"),
                    class_name="p-4 gap-1",
                ),
                class_name="absolute top-12 right-0 bg-white border border-slate-200 rounded-xl shadow-xl z-50 min-w-[220px]",
            ),
        ),
        class_name="relative",
    )


def profile_popup():
    return rx.box(
        rx.button(
            rx.text("👤", class_name="text-lg"),
            on_click=State.toggle_profile,
            class_name=rx.cond(
                State.show_profile,
                "w-9 h-9 flex items-center justify-center rounded-full bg-indigo-50 border-none cursor-pointer transition-colors duration-150",
                "w-9 h-9 flex items-center justify-center rounded-full bg-transparent hover:bg-slate-100 border-none cursor-pointer transition-colors duration-150",
            ),
        ),
        rx.cond(
            State.show_profile,
            rx.box(
                rx.vstack(
                    rx.text("Perfil del Estudiante", class_name="font-semibold text-base text-slate-800"),
                    rx.box(
                        rx.text("Estado:", class_name="text-xs text-slate-500"),
                        rx.text("Evaluación Vocacional Activa", class_name="text-xs text-indigo-600 font-medium"),
                        class_name="bg-indigo-50 rounded-lg p-3 w-full mt-2",
                    ),
                    rx.button(
                        "Limpiar historial y reiniciar",
                        on_click=State.reset_chat,
                        class_name="bg-transparent text-red-500 border border-red-200 rounded-lg px-4 py-2 text-sm cursor-pointer hover:bg-red-50 transition-colors w-full mt-3",
                    ),
                    class_name="p-4 gap-1",
                ),
                class_name="absolute top-12 right-0 bg-white border border-slate-200 rounded-xl shadow-xl z-50 min-w-[240px]",
            ),
        ),
        class_name="relative",
    )


def index():
    return rx.box(
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.text("🧠", class_name="text-2xl"),
                    rx.text("MentorAI", class_name="text-xl font-bold text-indigo-950"),
                    class_name="flex items-center gap-2",
                ),
                rx.hstack(
                    settings_popup(),
                    profile_popup(),
                    class_name="flex items-center gap-1",
                ),
                class_name="flex items-center justify-between w-full max-w-4xl mx-auto h-full px-6",
            ),
            class_name="fixed top-0 left-0 w-full h-16 bg-white/80 backdrop-blur-xl border-b border-slate-200/80 z-50",
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
                rx.cond(State.finished, rx.fragment(), suggestions()),
            ),
            rx.cond(
                State.loading,
                rx.cond(State.finished, rx.fragment(), typing_indicator()),
            ),
            rx.cond(State.finished, results_view()),
            class_name="max-w-3xl mx-auto pt-24 pb-32 px-4 w-full",
        ),
        rx.cond(State.finished, rx.fragment(), input_pill()),
        class_name="bg-slate-50 min-h-screen w-full",
    )


app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, sans-serif",
    },
    head_components=[
        rx.el.link(rel="stylesheet", href="/style.css"),
        rx.el.script(src="/mic.js"),
    ],
)
app.add_page(index, route="/", title="MentorAI 🧠")
