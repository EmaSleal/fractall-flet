import asyncio
from typing import Awaitable, Callable, Optional, TypeVar

import flet as ft

import rutas
from api.cliente import ApiFallo, ApiResultado
from api.cliente_autenticado import SesionExpirada
from diseno import tokens

T = TypeVar("T")

_DEMORA_DEBOUNCE_SEGUNDOS = 0.35


def construir_buscador_remoto(
    page: ft.Page,
    etiqueta: str,
    buscar: Callable[[str], Awaitable[ApiResultado[list[T]]]],
    renderizar_opcion: Callable[[T], str],
    al_seleccionar: Callable[[T], None],
    valor_inicial: str = "",
    pista: str = "Buscar...",
) -> ft.SearchBar:
    """Combobox de búsqueda en vivo con debounce, genérico sobre el tipo de
    resultado — usado por CABYS, clientes y productos dentro del wizard de
    facturas. `buscar` recibe la consulta y devuelve una lista plana
    (no paginada) de resultados.

    Sobre ft.SearchBar (no ft.TextField + ft.Column de resultados, como
    tenía antes): igual que combobox_local.py, así los resultados flotan en
    un overlay real (view de Flutter) en vez de empujar el layout hacia
    abajo. `on_tap` dispara una búsqueda inicial (consulta vacía) apenas se
    abre, mostrando una lista rápida sin exigir mínimo de caracteres;
    `on_change` la repite con debounce mientras el usuario tipea. Error de
    red y "sin resultados" se muestran con colores distintos (antes eran el
    mismo texto gris — indistinguibles para el usuario)."""

    estado = {"generacion": 0}

    def _opcion(item: T) -> ft.ListTile:
        async def _elegir(e: ft.Event[ft.ListTile]) -> None:
            al_seleccionar(item)
            await barra.close_view(renderizar_opcion(item))

        return ft.ListTile(title=ft.Text(renderizar_opcion(item)), on_click=_elegir)

    def _mensaje(texto: str, *, es_error: bool = False) -> ft.ListTile:
        color = tokens.ESTADO_RECHAZADO if es_error else tokens.GRAFITO
        return ft.ListTile(title=ft.Text(texto, color=color), disabled=True)

    async def _buscar(consulta: str, generacion: int) -> None:
        await asyncio.sleep(_DEMORA_DEBOUNCE_SEGUNDOS)
        if generacion != estado["generacion"]:
            return

        barra.controls = [_mensaje("Buscando...")]
        barra.update()

        try:
            resultado = await buscar(consulta)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        if generacion != estado["generacion"]:
            return

        if isinstance(resultado, ApiFallo):
            barra.controls = [_mensaje(resultado.error.mensaje, es_error=True)]
            barra.update()
            return

        items = resultado.datos
        if not items:
            barra.controls = [_mensaje("Sin resultados")]
            barra.update()
            return

        barra.controls = [_opcion(item) for item in items]
        barra.update()

    async def _abrir(e: Optional[ft.Event[ft.SearchBar]] = None) -> None:
        estado["generacion"] += 1
        await barra.open_view()
        await _buscar("", estado["generacion"])

    async def _cambiar(e: ft.Event[ft.SearchBar]) -> None:
        estado["generacion"] += 1
        await _buscar((e.control.value or "").strip(), estado["generacion"])

    borde = ft.BorderSide(width=1, color=tokens.ARENA)
    barra = ft.SearchBar(
        bar_hint_text=etiqueta,
        view_hint_text=pista,
        value=valor_inicial,
        on_tap=_abrir,
        on_change=_cambiar,
        controls=[],
        # Mismo lenguaje visual que combobox_local.py y el resto de la app
        # (diseno/tema.py no define un SearchBarTheme global).
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
