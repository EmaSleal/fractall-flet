from typing import Callable, Optional, TypeVar

import flet as ft

from diseno import tokens

T = TypeVar("T")


def construir_combobox_local(
    etiqueta: str,
    items: list[T],
    texto_busqueda: Callable[[T], str],
    renderizar_opcion: Callable[[T], str],
    al_seleccionar: Callable[[T], None],
    valor_inicial: str = "",
    pista: str = "Filtrá por texto",
) -> ft.SearchBar:
    """Combobox con filtro local sobre ft.SearchBar (SearchAnchor de
    Flutter) — overlay flotante real (no empuja el layout), con control
    total desde Python sobre qué se muestra: on_tap carga todos los items
    sin importar el texto actual (así el catálogo completo aparece al
    clickear con el campo vacío), on_change los va acotando mientras el
    usuario tipea. Equivalente a SelectorUnidadMedida (Popover+Command/cmdk)
    de fractall-frontend."""

    def _opcion(item: T) -> ft.ListTile:
        async def _elegir(e: ft.Event[ft.ListTile]) -> None:
            al_seleccionar(item)
            await barra.close_view(renderizar_opcion(item))

        return ft.ListTile(title=ft.Text(renderizar_opcion(item)), on_click=_elegir)

    async def _abrir(e: Optional[ft.Event[ft.SearchBar]] = None) -> None:
        barra.controls = [_opcion(item) for item in items]
        await barra.open_view()

    def _filtrar(e: ft.Event[ft.SearchBar]) -> None:
        consulta = (e.control.value or "").strip().lower()
        barra.controls = [
            _opcion(item) for item in items if consulta in texto_busqueda(item).lower()
        ]
        barra.update()

    borde = ft.BorderSide(width=1, color=tokens.ARENA)
    barra = ft.SearchBar(
        bar_hint_text=etiqueta,
        view_hint_text=pista,
        value=valor_inicial,
        on_tap=_abrir,
        on_change=_filtrar,
        controls=[_opcion(item) for item in items],
        # Mismo lenguaje visual que el resto de los campos/tarjetas de la
        # app (diseno/tema.py no define un SearchBarTheme global, así que
        # sin esto el SearchBar cae al estilo "pill" filled por defecto de
        # Material 3 en vez del outline plano ARENA/RADIO_MD que usa todo
        # lo demás).
        bar_bgcolor=tokens.LINO,
        bar_elevation=0,
        bar_shape=ft.RoundedRectangleBorder(radius=tokens.RADIO_MD),
        bar_border_side=borde,
        bar_text_style=ft.TextStyle(color=tokens.TINTA, size=tokens.FUENTE_BASE),
        bar_hint_text_style=ft.TextStyle(color=tokens.GRAFITO, size=tokens.FUENTE_BASE),
        view_bgcolor=tokens.LINO,
        view_elevation=0,
        view_shape=ft.RoundedRectangleBorder(radius=tokens.RADIO_LG),
        view_side=borde,
        view_header_text_style=ft.TextStyle(color=tokens.TINTA, size=tokens.FUENTE_BASE),
        view_hint_text_style=ft.TextStyle(color=tokens.GRAFITO, size=tokens.FUENTE_BASE),
        divider_color=tokens.ARENA,
    )
    return barra
