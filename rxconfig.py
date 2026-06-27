import reflex as rx

config = rx.Config(
    app_name="mentorai",
    backend_port=8080,  # CRÍTICO: Corrige el error 502 en la nube
    tailwind={
        "content": [
            "./mentorai/**/*.{js,jsx,ts,tsx,py}",
        ],
    },
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
)
