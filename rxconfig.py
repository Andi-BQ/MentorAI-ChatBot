import reflex as rx

config = rx.Config(
    app_name="mentorai",
    tailwind={
        "content": [
            "./mentorai/**/*.{js,jsx,ts,tsx,py}",
        ],
    },
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
)
