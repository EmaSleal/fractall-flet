import flet as ft

import catalogos
from diseno import tokens

_COLOR_POR_CATEGORIA = {
    "aceptado": tokens.ESTADO_ACEPTADO,
    "pendiente": tokens.ESTADO_PENDIENTE,
    "rechazado": tokens.ESTADO_RECHAZADO,
    "neutral": tokens.GRAFITO,
}

_ICONOS = {
    "DESCRIPTION": ft.Icons.DESCRIPTION,
    "SCHEDULE": ft.Icons.SCHEDULE,
    "CHECK_CIRCLE": ft.Icons.CHECK_CIRCLE,
    "CANCEL": ft.Icons.CANCEL,
}


def construir_sello_estado(estado: str, tamano_icono: float = 14) -> ft.Container:
    """El "sello cálido" del doc de diseño — Flet no soporta bordes
    punteados (`BorderStyle` solo tiene NONE/SOLID), así que se aproxima
    con un borde sólido grueso + forma de píldora en vez del borde
    punteado real que usa fractall-frontend."""
    etiqueta, nombre_icono, categoria = catalogos.info_estado_factura(estado)
    color = _COLOR_POR_CATEGORIA[categoria]
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border=ft.Border.all(2, color),
        border_radius=tokens.RADIO_SELLO,
        content=ft.Row(
            spacing=4,
            tight=True,
            controls=[
                ft.Icon(_ICONOS[nombre_icono], size=tamano_icono, color=color),
                ft.Text(etiqueta, theme_style=ft.TextThemeStyle.LABEL_MEDIUM, color=color),
            ],
        ),
    )
