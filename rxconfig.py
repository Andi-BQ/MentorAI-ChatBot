import reflex as rx

config = rx.Config(
    app_name="mentorai",
    backend_port=8080,
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
)
