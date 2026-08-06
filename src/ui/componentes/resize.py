import flet as ft

_ATRIBUTO_OYENTES = "_oyentes_resize"


def registrar_oyente_resize(page: ft.Page, oyente) -> None:
    """Suscribe `oyente` a los eventos de resize de `page` sin pisar otros
    oyentes ya registrados. `page.on_resize` es un único slot (no un evento
    con múltiples suscriptores); esto permite que el shell (sidebar/topbar)
    y el contenedor de ancho limitado reaccionen al resize de forma
    independiente."""
    oyentes = getattr(page, _ATRIBUTO_OYENTES, None)
    if oyentes is None:
        oyentes = []
        setattr(page, _ATRIBUTO_OYENTES, oyentes)

        def _despachar(e: ft.PageResizeEvent) -> None:
            for cada in list(oyentes):
                cada(e)

        page.on_resize = _despachar

    oyentes.append(oyente)
