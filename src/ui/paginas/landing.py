from datetime import datetime

import flet as ft

import rutas
from diseno import tokens


def vista_landing(page: ft.Page) -> ft.View:
    """Landing público — calcado de `app/page.tsx` en fractall-frontend
    (única página fuera del shell/de auth que no requiere sesión ni
    redirige a login: es la puerta de entrada de un visitante anónimo)."""
    encabezado = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text(
                "FRACTALL",
                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                font_family=tokens.FUENTE_DISPLAY_SEMIBOLD,
            ),
            ft.OutlinedButton(
                content="Iniciar sesión",
                on_click=lambda e: page.navigate(rutas.LOGIN),
            ),
        ],
    )

    contenido_principal = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=32,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Text(
                        "Facturación electrónica para Costa Rica",
                        theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Emitir comprobantes electrónicos ante Hacienda, sin complicaciones.",
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        color=tokens.GRAFITO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                wrap=True,
                spacing=12,
                run_spacing=12,
                controls=[
                    ft.Button(
                        content="Crear cuenta gratis",
                        width=200,
                        on_click=lambda e: page.navigate(rutas.REGISTRO),
                    ),
                    ft.OutlinedButton(
                        content="Iniciar sesión",
                        width=200,
                        on_click=lambda e: page.navigate(rutas.LOGIN),
                    ),
                ],
            ),
        ],
    )

    pie = ft.Text(
        f"© {datetime.now().year} FRACTALL",
        theme_style=ft.TextThemeStyle.BODY_SMALL,
        color=tokens.GRAFITO,
        text_align=ft.TextAlign.CENTER,
    )

    return ft.View(
        route=rutas.LANDING,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    expand=True,
                    padding=24,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            encabezado,
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment.CENTER,
                                content=contenido_principal,
                            ),
                            pie,
                        ],
                    ),
                ),
            )
        ],
    )
