import reflex as rx
from .state import State

# Tailwind classes usadas dinámicamente (fuerza compilación JIT):
# text-slate-900 text-white placeholder-slate-400 placeholder-slate-500
# bg-white bg-[#1e293b] text-slate-800 text-slate-100
# bg-indigo-100 border-indigo-200 bg-gradient-to-r from-blue-600 to-cyan-500
# bg-red-500 bg-red-600 overflow-y-auto z-[10000]
# animate-pulse [animation-delay:0.1s] [animation-delay:0.2s]
# [animation-delay:0.3s] [animation-delay:0.4s]

# ----------------------------------------------------------------------
# 1. BURBUJAS DE CHAT ADAPTATIVAS (rx.cond para tema, sin dark:)
# ----------------------------------------------------------------------


def render_chat_message(msg):
    return rx.cond(
        msg["role"] == "user",
        rx.hstack(
            rx.box(
                rx.text(msg["content"], style={"color": "#ffffff", "fontWeight": "500"}),
                style={
                    "backgroundColor": "#2563eb",
                    "padding": "12px 16px",
                    "borderRadius": "18px 18px 2px 18px",
                    "maxWidth": "70%",
                    "wordBreak": "break-word",
                },
            ),
            rx.avatar(fallback="U", size="2", color_scheme="indigo"),
            class_name="w-full justify-end items-end gap-3 px-4 py-2",
        ),
        rx.hstack(
            rx.avatar(fallback="AI", size="2", color_scheme="pink"),
            rx.box(
                rx.text(
                    msg["content"],
                    style={
                        "color": rx.cond(rx.color_mode == "light", "#0f172a", "#f8fafc"),
                    },
                ),
                style={
                    "backgroundColor": rx.cond(rx.color_mode == "light", "#f1f5f9", "#1e293b"),
                    "border": rx.cond(rx.color_mode == "light", "1px solid #e2e8f0", "1px solid #334155"),
                    "padding": "14px 18px",
                    "borderRadius": "18px 18px 18px 2px",
                    "maxWidth": "75%",
                    "wordBreak": "break-word",
                },
            ),
            class_name="w-full justify-start items-end gap-3 px-4 py-2",
        ),
    )


# ----------------------------------------------------------------------
# 2. TARJETAS DE SUGERENCIAS RESPONSIVAS (grid 1/2 columnas)
# ----------------------------------------------------------------------


def suggestion_card(text, label, icon):
    return rx.box(
        rx.hstack(
            rx.center(
                rx.text(icon, class_name="text-2xl"),
                class_name=rx.cond(
                    rx.color_mode == "light",
                    "w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100/50 flex-shrink-0 shadow-inner",
                    "w-12 h-12 rounded-xl bg-slate-800/50 border border-slate-700/50 flex-shrink-0 shadow-inner",
                ),
            ),
            rx.vstack(
                rx.text(label, class_name="font-bold text-sm tracking-wide"),
                rx.text(
                    "Toca para empezar",
                    class_name="text-xs font-medium text-slate-400 dark:text-slate-500",
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        class_name=rx.cond(
            rx.color_mode == "light",
            "border border-slate-200/60 rounded-2xl p-4 transition-all duration-300 cursor-pointer hover:border-cyan-500/50 hover:shadow-[0_0_25px_rgba(6,182,212,0.15)] hover:-translate-y-0.5 bg-white/90",
            "border border-slate-800/80 rounded-2xl p-4 transition-all duration-300 cursor-pointer hover:border-cyan-500/50 hover:shadow-[0_0_25px_rgba(6,182,212,0.15)] hover:-translate-y-0.5 bg-[#0f172a]/40",
        ),
        style={"backdrop-filter": "blur(12px)"},
        on_click=lambda: State.send_suggestion(text),
    )


def suggestions():
    return rx.vstack(
        rx.text(
            "\u26a1 \u00bfPor d\u00f3nde quieres empezar?",
            class_name=rx.cond(
                rx.color_mode == "light",
                "text-indigo-600 font-bold text-xs tracking-widest uppercase mb-1 text-center w-full",
                "text-cyan-400 font-bold text-xs tracking-widest uppercase mb-1 text-center w-full",
            ),
        ),
        rx.box(
            suggestion_card(
                "Quiero empezar explorando mis opciones de carreras profesionales.",
                "Explorar carreras",
                "\U0001f393",
            ),
            suggestion_card(
                "Me gustar\u00eda analizar cu\u00e1les son mis mayores habilidades y fortalezas.",
                "Descubrir fortalezas",
                "\U0001f4a1",
            ),
            suggestion_card(
                "Quiero armar una estrategia paso a paso para mi desarrollo futuro.",
                "Planificar futuro",
                "\U0001f680",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mt-2",
        ),
        class_name="w-full max-w-3xl mx-auto px-4 gap-2 mt-4",
    )


# ----------------------------------------------------------------------
# 3. INDICADOR DE CARGA (TYPING INDICATOR)
# ----------------------------------------------------------------------


def typing_indicator():
    return rx.box(
        rx.hstack(
            rx.box(class_name="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"),
            rx.box(class_name="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.15s]"),
            rx.box(class_name="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:0.3s]"),
            spacing="1",
            align="center",
            class_name="px-2 py-1",
        ),
        class_name=rx.cond(
            rx.color_mode == "light",
            "border border-slate-200/60 shadow-md rounded-2xl px-4 py-3 w-auto inline-block ml-2 mb-4 bg-white/90",
            "border border-slate-800/60 shadow-md rounded-2xl px-4 py-3 w-auto inline-block ml-2 mb-4 bg-[#131c2e]/70",
        ),
        style={"backdrop-filter": "blur(10px)"},
    )


# ----------------------------------------------------------------------
# 4. INDICADOR DE GRABACIÓN (BARRAS DE AUDIO)
# ----------------------------------------------------------------------


def recording_indicator():
    return rx.hstack(
        rx.box(class_name="w-1 h-4 bg-red-500 rounded-full animate-pulse"),
        rx.box(class_name="w-1 h-6 bg-red-500 rounded-full animate-pulse [animation-delay:0.1s]"),
        rx.box(class_name="w-1 h-8 bg-red-500 rounded-full animate-pulse [animation-delay:0.2s]"),
        rx.box(class_name="w-1 h-6 bg-red-500 rounded-full animate-pulse [animation-delay:0.3s]"),
        rx.box(class_name="w-1 h-4 bg-red-500 rounded-full animate-pulse [animation-delay:0.4s]"),
        rx.text(
            "\U0001f399\ufe0f Grabando audio... Presiona el bot\u00f3n rojo para detener y enviar",
            class_name=rx.cond(
                rx.color_mode == "light",
                "text-xs text-slate-400 font-medium ml-2",
                "text-xs text-slate-500 font-medium ml-2",
            ),
        ),
        spacing="1",
        align="center",
        class_name="flex-1 px-3",
    )


# ----------------------------------------------------------------------
# 5. VISTA DE RESULTADOS FINAL (DASHBOARD PREDICTIVO)
# ----------------------------------------------------------------------


def results_view():
    return rx.vstack(
        rx.box(class_name="w-full border-t border-slate-200/60 dark:border-slate-800/60 my-4"),
        rx.text(
            "\U0001f3af Tu perfil se alinea con:",
            class_name="text-xs font-bold tracking-widest uppercase text-slate-400 dark:text-slate-500 text-center mt-2",
        ),
        rx.text(
            State.top_career.replace("_", " ").title(),
            class_name="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-cyan-500 dark:from-indigo-400 dark:to-cyan-400 text-center mb-6 px-4 drop-shadow-sm",
        ),
        rx.cond(
            State.radar_html != "",
            rx.box(
                rx.box(
                    rx.html(State.radar_html),
                    class_name=rx.cond(
                        rx.color_mode == "light",
                        "w-full md:w-1/2 p-2 bg-white border border-slate-100 rounded-2xl shadow-sm",
                        "w-full md:w-1/2 p-2 bg-slate-900/40 border border-slate-800/80 rounded-2xl shadow-sm",
                    ),
                ),
                rx.box(
                    rx.html(State.bar_html),
                    class_name=rx.cond(
                        rx.color_mode == "light",
                        "w-full md:w-1/2 p-2 bg-white border border-slate-100 rounded-2xl shadow-sm",
                        "w-full md:w-1/2 p-2 bg-slate-900/40 border border-slate-800/80 rounded-2xl shadow-sm",
                    ),
                ),
                class_name="flex flex-col md:flex-row gap-6 w-full max-w-4xl px-4",
            ),
        ),
        rx.box(class_name="w-full border-t border-slate-200/60 dark:border-slate-800/60 my-6"),
        rx.button(
            rx.hstack(
                rx.text("\U0001f504", class_name="text-base"),
                rx.text("Volver a comenzar", class_name="font-bold text-sm tracking-wide"),
                spacing="2",
                align="center",
            ),
            on_click=State.reset_chat,
            style={
                "background": "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
                "color": "#ffffff",
            },
            class_name="hover:opacity-90 font-semibold py-3.5 px-8 rounded-xl transition-all duration-200 shadow-md hover:shadow-indigo-500/20 w-full max-w-xs cursor-pointer border-none active:scale-[0.98]",
        ),
        class_name="w-full flex flex-col items-center gap-4 pb-16 animate-fade-in",
    )


# ----------------------------------------------------------------------
# 5. CAJA DE ENTRADA (TEXT_AREA + ENTER LAMBDA + CONTENEDOR FIJO)
# ----------------------------------------------------------------------


def input_pill():
    return rx.box(
        rx.hstack(
            rx.cond(
                State.is_recording,
                recording_indicator(),
                rx.cond(
                    rx.color_mode == "light",
                    rx.text_area(
                        value=State.input_text,
                        on_change=State.set_input,
                        placeholder="Escribe tu mensaje aquí...",
                        on_key_down=State.handle_keyboard,
                        class_name="w-full bg-transparent border-none focus:ring-0 text-slate-900 placeholder-slate-400 resize-none",
                        style={"minHeight": "44px", "maxHeight": "140px", "width": "100%"},
                    ),
                    rx.text_area(
                        value=State.input_text,
                        on_change=State.set_input,
                        placeholder="Escribe tu mensaje aquí...",
                        on_key_down=State.handle_keyboard,
                        class_name="w-full bg-transparent border-none focus:ring-0 text-white placeholder-slate-500 resize-none",
                        style={"minHeight": "44px", "maxHeight": "140px", "width": "100%"},
                    ),
                ),
            ),
            rx.hstack(
                rx.button(
                    rx.cond(
                        State.is_recording,
                        rx.text("\u25a0", class_name="text-white font-black text-sm"),
                        rx.text("\U0001f3a4", class_name="text-base"),
                    ),
                    on_click=State.toggle_recording,
                    variant="ghost",
                    class_name=rx.cond(
                        State.is_recording,
                        "w-10 h-10 rounded-full cursor-pointer flex items-center justify-center border-none bg-red-600 shadow-md",
                        rx.cond(
                            rx.color_mode == "light",
                            "w-10 h-10 rounded-full cursor-pointer hover:bg-slate-100 flex items-center justify-center border-none",
                            "w-10 h-10 rounded-full cursor-pointer hover:bg-slate-800 flex items-center justify-center border-none",
                        ),
                    ),
                ),
                rx.button(
                    rx.text("\u2191", class_name="text-white font-black text-lg"),
                    on_click=State.send_from_input,
                    style={"background": "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)"},
                    radius="full",
                    class_name="w-10 h-10 cursor-pointer shadow-md active:scale-95 transition-all duration-150 flex items-center justify-center border-none hover:brightness-110",
                ),
                spacing="2",
                align="center",
            ),
            align="center",
            class_name=rx.cond(
                rx.color_mode == "light",
                "bg-white border border-slate-200 rounded-xl shadow-sm flex items-center p-2 w-full max-w-3xl",
                "bg-[#1e293b] border border-slate-700 rounded-xl shadow-md flex items-center p-2 w-full max-w-3xl",
            ),
        ),
        class_name="fixed bottom-4 md:bottom-6 left-1/2 -translate-x-1/2 w-[calc(100%-24px)] max-w-3xl z-50 px-2",
    )


# ----------------------------------------------------------------------
# 6. MENÚS DESPLEGABLES (PREFERENCIAS & PERFIL)
# ----------------------------------------------------------------------


def settings_popup():
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.text("\u2699\ufe0f", class_name="text-base"),
                variant=rx.cond(State.show_settings, "surface", "ghost"),
                color_scheme="indigo",
                class_name="w-10 h-10 rounded-full cursor-pointer flex items-center justify-center border-none",
            ),
        ),
        rx.popover.content(
            rx.vstack(
                rx.text("Preferencias", class_name="font-bold text-sm"),
                rx.text(
                    "Temperatura del modelo",
                    class_name="text-[11px] font-semibold text-slate-400 dark:text-slate-500 mt-1 uppercase tracking-wider",
                ),
                rx.select.root(
                    rx.select.trigger(
                        variant="surface",
                        class_name="w-full mt-1 text-xs",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.select.item("0.1", value="0.1"),
                            rx.select.item("0.2", value="0.2"),
                            rx.select.item("0.3", value="0.3"),
                            rx.select.item("0.4", value="0.4"),
                            rx.select.item("0.5", value="0.5"),
                            rx.select.item("0.6", value="0.6"),
                            rx.select.item("0.7", value="0.7"),
                            rx.select.item("0.8", value="0.8"),
                            rx.select.item("0.9", value="0.9"),
                            rx.select.item("1.0", value="1.0"),
                        ),
                        style={"zIndex": 9999},
                    ),
                    default_value="0.7",
                    on_change=State.set_temperature,
                ),
                rx.text(
                    "Arquitectura Llama-3.3 Cloud",
                    class_name="text-[10px] text-slate-400 dark:text-slate-500 font-medium text-right w-full mt-1.5",
                ),
                class_name="p-4 gap-1 w-64",
            ),
            side="bottom",
            align="end",
            side_offset=8,
            class_name=rx.cond(
                rx.color_mode == "light",
                "bg-white border border-slate-200 rounded-2xl shadow-xl z-30",
                "bg-[#131c2e] border border-slate-800 rounded-2xl shadow-xl z-30",
            ),
        ),
        open=State.show_settings,
        on_open_change=State.toggle_settings,
    )


def profile_popup():
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.text("\U0001f464", class_name="text-base"),
                variant=rx.cond(State.show_profile, "surface", "ghost"),
                color_scheme="indigo",
                class_name="w-10 h-10 rounded-full cursor-pointer flex items-center justify-center border-none",
            ),
        ),
        rx.popover.content(
            rx.vstack(
                rx.text("Perfil del Estudiante", class_name="font-bold text-sm"),
                rx.box(
                    rx.text(
                        "Estado actual:",
                        class_name="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider",
                    ),
                    rx.text(
                        "Evaluaci\u00f3n Vocacional Activa",
                        class_name="text-xs font-bold mt-0.5",
                    ),
                    class_name=rx.cond(
                        rx.color_mode == "light",
                        "bg-indigo-50/60 rounded-xl p-3 w-full mt-2 border border-indigo-100/30 text-indigo-600",
                        "bg-slate-800/40 rounded-xl p-3 w-full mt-2 border border-slate-700/30 text-cyan-400",
                    ),
                ),
                rx.button(
                    "Limpiar historial y reiniciar",
                    on_click=State.reset_chat,
                    variant="soft",
                    color_scheme="red",
                    class_name="text-xs cursor-pointer w-full mt-3 font-semibold py-2 rounded-xl",
                ),
                class_name="p-4 gap-1 w-64",
            ),
            side="bottom",
            align="end",
            side_offset=8,
            class_name=rx.cond(
                rx.color_mode == "light",
                "bg-white border border-slate-200 rounded-2xl shadow-xl z-50",
                "bg-[#131c2e] border border-slate-800 rounded-2xl shadow-xl z-50",
            ),
        ),
        open=State.show_profile,
        on_open_change=State.toggle_profile,
    )


# ----------------------------------------------------------------------
# 7. MAQUETACIÓN PRINCIPAL (INDEX)
# ----------------------------------------------------------------------


def index():
    return rx.theme(
        rx.box(
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.center(
                            rx.text("\U0001f9e0", class_name="text-xl"),
                            class_name=rx.cond(
                                rx.color_mode == "light",
                                "w-9 h-9 bg-indigo-600/10 rounded-xl",
                                "w-9 h-9 bg-cyan-400/10 rounded-xl",
                            ),
                        ),
                        rx.text("MentorAI", class_name="text-lg font-black tracking-tight"),
                        class_name="flex items-center gap-2.5",
                    ),
                    rx.hstack(
                        rx.color_mode.button(
                            variant="ghost",
                            class_name=rx.cond(
                                rx.color_mode == "light",
                                "cursor-pointer rounded-full text-indigo-600 hover:bg-slate-100 w-10 h-10 flex items-center justify-center border-none",
                                "cursor-pointer rounded-full text-cyan-400 hover:bg-slate-800 w-10 h-10 flex items-center justify-center border-none",
                            ),
                        ),
                        settings_popup(),
                        profile_popup(),
                        class_name="flex items-center gap-4",
                    ),
                    class_name="flex items-center justify-between w-full max-w-4xl mx-auto h-full px-4 md:px-6",
                ),
                class_name=rx.cond(
                    rx.color_mode == "light",
                    "fixed top-0 left-0 w-full h-16 border-b border-slate-200/60 z-50 transition-colors duration-300",
                    "fixed top-0 left-0 w-full h-16 border-b border-slate-800/60 z-50 transition-colors duration-300",
                ),
                style={
                    "background-color": rx.cond(rx.color_mode == "light", "rgba(255,255,255,0.8)", "rgba(11,15,25,0.7)"),
                    "backdrop-filter": "blur(20px)",
                },
            ),
            rx.box(
                rx.foreach(
                    State.messages,
                    lambda msg: rx.cond(
                        msg["role"] != "system",
                        render_chat_message(msg),
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
                class_name="max-w-3xl mx-auto pt-24 pb-40 px-3 w-full overflow-y-auto",
                style={"maxHeight": "calc(100vh - 180px)"},
            ),
            rx.cond(State.finished, rx.fragment(), input_pill()),
        ),
        color_mode=rx.color_mode,
        class_name=rx.cond(
            rx.color_mode == "light",
            "bg-slate-50 text-slate-900 min-h-screen w-full transition-colors",
            "bg-[#0b0f19] text-white min-h-screen w-full transition-colors",
        ),
    )


# ----------------------------------------------------------------------
# 8. INICIALIZACIÓN DE LA APLICACIÓN
# ----------------------------------------------------------------------

app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, sans-serif",
    },
    head_components=[
        rx.el.link(rel="stylesheet", href="/style.css"),
        rx.el.script(src="/mic.js"),
    ],
)
app.add_page(index, route="/", title="MentorAI \U0001f9e0 | Orientaci\u00f3n Profesional Vocacional", on_load=State.init_chat)
