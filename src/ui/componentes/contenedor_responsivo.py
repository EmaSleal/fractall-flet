import flet as ft

from ui.componentes.resize import registrar_oyente_resize

PADDING_LATERAL_MINIMO = 24


def contenedor_ancho_limitado(
    page: ft.Page, contenido: ft.Control, ancho_maximo: float
) -> ft.Container:
    """Centra `contenido` y limita su ancho a `ancho_maximo` en pantallas
    anchas (desktop/web), dejando que se angoste con margen en pantallas
    chicas (celular) en vez de estirarse de punta a punta.
    """
    contenedor = ft.Container(content=contenido, width=ancho_maximo)

    def ajustar_ancho(e: ft.PageResizeEvent | None = None) -> None:
        ancho_disponible = (page.width or ancho_maximo) - PADDING_LATERAL_MINIMO * 2
        contenedor.width = min(ancho_maximo, max(ancho_disponible, 0))
        if e is not None:
            page.update()

    ajustar_ancho()
    registrar_oyente_resize(page, ajustar_ancho)
    return contenedor
