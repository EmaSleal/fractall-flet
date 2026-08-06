import flet as ft

from diseno import tokens


def construir_badge(texto: str, color: str, compacto: bool = False) -> ft.Container:
    """Píldora rellena de color con texto — para estados binarios/simples
    (activo/inactivo, vigente/no vigente, estado de empresa). Estaba
    duplicada casi igual en empresa.py, clientes/exoneraciones.py y
    productos/detalle.py.

    No confundir con `sello_estado.py`: ese es el "sello cálido" con borde
    grueso + ícono, específico del estado de una factura — visualmente
    distinto (contorneado, no relleno) y no parte de esta duplicación."""
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=8 if compacto else 10, vertical=2 if compacto else 4),
        border_radius=tokens.RADIO_SELLO,
        bgcolor=color,
        content=ft.Text(
            texto,
            theme_style=ft.TextThemeStyle.LABEL_SMALL if compacto else ft.TextThemeStyle.LABEL_MEDIUM,
            color=tokens.LINO,
        ),
    )
