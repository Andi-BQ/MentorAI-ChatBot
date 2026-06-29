import reflex as rx

config = rx.Config(
    app_name="mentorai",
    host="0.0.0.0",
    plugins=[
        rx.plugins.TailwindV3Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.radix.themes.theme(accent_color="indigo"),
        ),
    ],
)
