import flet as ft

from . import tokens


def registrar_fuentes(page: ft.Page) -> None:
    page.fonts = {
        tokens.FUENTE_DISPLAY: "fonts/BricolageGrotesque-Regular.ttf",
        tokens.FUENTE_DISPLAY_MEDIUM: "fonts/BricolageGrotesque-Medium.ttf",
        tokens.FUENTE_DISPLAY_SEMIBOLD: "fonts/BricolageGrotesque-SemiBold.ttf",
        tokens.FUENTE_CUERPO: "fonts/Karla-Regular.ttf",
        tokens.FUENTE_CUERPO_MEDIUM: "fonts/Karla-Medium.ttf",
        tokens.FUENTE_CUERPO_SEMIBOLD: "fonts/Karla-SemiBold.ttf",
        tokens.FUENTE_MONO: "fonts/IBMPlexMono-Regular.ttf",
        tokens.FUENTE_MONO_MEDIUM: "fonts/IBMPlexMono-Medium.ttf",
    }


def _forma_redondeada(radio: float) -> ft.RoundedRectangleBorder:
    return ft.RoundedRectangleBorder(radius=radio)


def construir_tema() -> ft.Theme:
    return ft.Theme(
        font_family=tokens.FUENTE_CUERPO,
        use_material3=True,
        color_scheme=ft.ColorScheme(
            primary=tokens.COSECHA,
            on_primary=tokens.LINO,
            secondary=tokens.MUSGO,
            on_secondary=tokens.LINO,
            surface=tokens.LINO,
            on_surface=tokens.TINTA,
            on_surface_variant=tokens.GRAFITO,
            # El backend/marca nunca reutiliza los colores de estado fiscal
            # (frontend-disenno.md 2.3), salvo este: fractall-frontend
            # (app/globals.css) sí mapea "rechazado" como el color de error
            # genérico de formularios (--destructive), y lo replicamos igual.
            error=tokens.ESTADO_RECHAZADO,
            on_error=tokens.LINO,
            outline=tokens.ARENA,
            outline_variant=tokens.ARENA,
        ),
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(
                font_family=tokens.FUENTE_DISPLAY_SEMIBOLD,
                size=tokens.FUENTE_3XL,
                color=tokens.TINTA,
            ),
            headline_large=ft.TextStyle(
                font_family=tokens.FUENTE_DISPLAY_SEMIBOLD,
                size=tokens.FUENTE_2XL,
                color=tokens.TINTA,
            ),
            headline_medium=ft.TextStyle(
                font_family=tokens.FUENTE_DISPLAY_SEMIBOLD,
                size=tokens.FUENTE_XL,
                color=tokens.TINTA,
            ),
            title_large=ft.TextStyle(
                font_family=tokens.FUENTE_DISPLAY_MEDIUM,
                size=tokens.FUENTE_LG,
                color=tokens.TINTA,
            ),
            title_medium=ft.TextStyle(
                font_family=tokens.FUENTE_CUERPO_SEMIBOLD,
                size=tokens.FUENTE_BASE,
                color=tokens.TINTA,
            ),
            body_large=ft.TextStyle(
                font_family=tokens.FUENTE_CUERPO,
                size=tokens.FUENTE_BASE,
                color=tokens.TINTA,
            ),
            body_medium=ft.TextStyle(
                font_family=tokens.FUENTE_CUERPO,
                size=tokens.FUENTE_SM,
                color=tokens.TINTA,
            ),
            body_small=ft.TextStyle(
                font_family=tokens.FUENTE_CUERPO,
                size=tokens.FUENTE_XS,
                color=tokens.GRAFITO,
            ),
            label_large=ft.TextStyle(
                font_family=tokens.FUENTE_CUERPO_MEDIUM,
                size=tokens.FUENTE_BASE,
                color=tokens.TINTA,
            ),
        ),
        button_theme=ft.ButtonTheme(
            style=ft.ButtonStyle(shape=_forma_redondeada(tokens.RADIO_MD)),
        ),
        outlined_button_theme=ft.OutlinedButtonTheme(
            style=ft.ButtonStyle(shape=_forma_redondeada(tokens.RADIO_MD)),
        ),
        card_theme=ft.CardTheme(
            color=tokens.LINO,
            shape=_forma_redondeada(tokens.RADIO_LG),
        ),
    )
