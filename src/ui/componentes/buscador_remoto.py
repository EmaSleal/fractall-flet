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
) -> ft.Column:
    """Combobox de búsqueda en vivo con debounce, genérico sobre el tipo de
    resultado — usado por CABYS, clientes y productos dentro del wizard de
    facturas. `buscar` recibe la consulta y devuelve una lista plana
    (no paginada) de resultados. Dispara una búsqueda inicial (consulta
    vacía incluida) apenas el campo gana foco por primera vez, mostrando
    una lista rápida sin exigir mínimo de caracteres."""
    campo = ft.TextField(label=etiqueta, hint_text=pista, value=valor_inicial)
    texto_estado = ft.Text(
        value="", theme_style=ft.TextThemeStyle.BODY_SMALL, color=tokens.GRAFITO, visible=False
    )
    resultados = ft.Column(spacing=2, visible=False)

    estado = {"generacion": 0, "enfocado": False}

    def _elegir(item: T) -> Callable[[ft.Event[ft.TextButton]], None]:
        def _handler(e: ft.Event[ft.TextButton]) -> None:
            al_seleccionar(item)
            campo.value = renderizar_opcion(item)
            resultados.visible = False
            texto_estado.visible = False
            page.update()

        return _handler

    async def _buscar(e: Optional[ft.Event[ft.TextField]] = None) -> None:
        estado["generacion"] += 1
        generacion = estado["generacion"]
        consulta = campo.value.strip()

        await asyncio.sleep(_DEMORA_DEBOUNCE_SEGUNDOS)
        if generacion != estado["generacion"]:
            return

        texto_estado.value = "Buscando..."
        texto_estado.visible = True
        resultados.visible = False
        page.update()

        try:
            resultado = await buscar(consulta)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        if generacion != estado["generacion"]:
            return

        if isinstance(resultado, ApiFallo):
            texto_estado.value = resultado.error.mensaje
            texto_estado.visible = True
            resultados.visible = False
            page.update()
            return

        items = resultado.datos
        if not items:
            texto_estado.value = "Sin resultados"
            texto_estado.visible = True
            resultados.visible = False
            page.update()
            return

        texto_estado.visible = False
        resultados.controls = [
            ft.TextButton(content=renderizar_opcion(item), on_click=_elegir(item))
            for item in items
        ]
        resultados.visible = True
        page.update()

    async def _al_enfocar(e: ft.Event[ft.TextField]) -> None:
        if estado["enfocado"]:
            return
        estado["enfocado"] = True
        await _buscar()

    campo.on_change = _buscar
    campo.on_focus = _al_enfocar

    return ft.Column(spacing=4, controls=[campo, texto_estado, resultados])
