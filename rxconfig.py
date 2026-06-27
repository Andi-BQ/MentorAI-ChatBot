import reflex as rx

config = rx.Config(
    app_name="mentorai",
    backend_port=8080,
    tailwind={
        "content": [
            "./mentorai/**/*.py",
            "./.web/**/*.js",
        ],
    },
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
)
