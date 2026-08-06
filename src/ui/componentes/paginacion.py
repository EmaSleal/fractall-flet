from dataclasses import dataclass
from typing import Awaitable, Callable, Optional, TypeVar

import flet as ft

import rutas
from api.cliente import ApiFallo, ApiResultado
from api.cliente_autenticado import SesionExpirada
from diseno import tokens

T = TypeVar("T")

LIMITE_MINIMO = 10
LIMITE_MAXIMO = 40
PIXELES_POR_ITEM = 40.0

# Debajo del punto de quiebre móvil (tokens.ANCHO_PUNTO_QUIEBRE_MOVIL) se usan
# dos tamaños fijos en vez de la fórmula por alto: un celular chico (ej.
# iPhone SE, ~667px de alto) y uno grande (ej. iPhone 14, Pixel, ~850-930px)
# tienen proporciones de UI muy distintas para una sola fórmula continua.
ALTO_CELULAR_CHICO = 700.0
LIMITE_CELULAR_CHICO = 8
LIMITE_CELULAR_GRANDE = 12


def calcular_limite_pagina(page: ft.Page) -> int:
    """Estima cuántos ítems pedir por página de listado según el dispositivo.
    En celular usa dos tamaños fijos (chico/grande, separados por el alto);
    en tablet/desktop escala con el alto disponible (`PIXELES_POR_ITEM` es
    una aproximación, no un valor exacto de layout, que varía por página).
    Se calcula una sola vez al construir la página, no se recalcula en cada
    resize — cambiar el tamaño de página a mitad de la paginación por cursor
    no tiene beneficio claro y complica el estado de `cursores`."""
    ancho = page.width or tokens.ANCHO_PUNTO_QUIEBRE_MOVIL
    alto = page.height or 800.0

    if ancho < tokens.ANCHO_PUNTO_QUIEBRE_MOVIL:
        return LIMITE_CELULAR_CHICO if alto < ALTO_CELULAR_CHICO else LIMITE_CELULAR_GRANDE

    limite = int(alto // PIXELES_POR_ITEM)
    return max(LIMITE_MINIMO, min(LIMITE_MAXIMO, limite))


@dataclass
class ListaPaginada:
    """Devuelto por `construir_lista_paginada`. `contenido` es lo que la
    página intercala en su propio Column (después de su encabezado y sus
    filtros); `recargar_desde_cero` es lo que cada filtro debe llamar en su
    propio `on_change`/`on_submit`/`on_select`."""

    contenido: ft.Control
    recargar_desde_cero: Callable[..., Awaitable[None]]


def construir_lista_paginada(
    page: ft.Page,
    buscar: Callable[[Optional[str]], Awaitable[ApiResultado]],
    renderizar_fila: Callable[[T], ft.Control],
    control_vacio: ft.Control,
) -> ListaPaginada:
    """Motor de listado con paginación por cursor, compartido por
    clientes/productos/facturas — antes estaba copiado casi línea por línea
    en los 3 `listado.py`. Encapsula el estado de cursores, cargando/error/
    vacío, la lista de filas y los botones anterior/siguiente.

    `buscar` recibe solo el cursor: cada página lo arma como una closure
    que ya trae horneados sus propios filtros (búsqueda, activo, fechas) y
    el `limit` calculado con `calcular_limite_pagina`. El encabezado de la
    página y los widgets de filtro quedan afuera — cada `listado.py` sigue
    dueño de su propio layout, esto solo resuelve la parte de paginación."""
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    texto_cargando = ft.Text(
        "Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL, visible=False
    )
    lista = ft.Column(spacing=8)
    boton_anterior = ft.TextButton(content="‹ Anterior", disabled=True)
    boton_siguiente = ft.TextButton(content="Siguiente ›", disabled=True)

    estado: dict = {"cursores": [], "next_cursor": None}

    async def cargar() -> None:
        texto_cargando.visible = True
        texto_error.visible = False
        control_vacio.visible = False
        page.update()

        cursor_actual = estado["cursores"][-1] if estado["cursores"] else None
        try:
            resultado = await buscar(cursor_actual)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        texto_cargando.visible = False

        if isinstance(resultado, ApiFallo):
            texto_error.value = resultado.error.mensaje
            texto_error.visible = True
            page.update()
            return

        pagina = resultado.datos
        estado["next_cursor"] = pagina.next_cursor

        if not pagina.items and not estado["cursores"]:
            lista.controls = []
            control_vacio.visible = True
        else:
            lista.controls = [renderizar_fila(item) for item in pagina.items]

        boton_anterior.disabled = len(estado["cursores"]) == 0
        boton_siguiente.disabled = pagina.next_cursor is None
        page.update()

    async def recargar_desde_cero(e: object = None) -> None:
        estado["cursores"] = []
        await cargar()

    async def ir_siguiente(e: ft.Event[ft.TextButton]) -> None:
        if estado["next_cursor"]:
            estado["cursores"].append(estado["next_cursor"])
            await cargar()

    async def ir_anterior(e: ft.Event[ft.TextButton]) -> None:
        if estado["cursores"]:
            estado["cursores"].pop()
            await cargar()

    boton_siguiente.on_click = ir_siguiente
    boton_anterior.on_click = ir_anterior

    page.run_task(cargar)

    contenido = ft.Column(
        spacing=16,
        controls=[
            texto_error,
            texto_cargando,
            control_vacio,
            lista,
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[boton_anterior, boton_siguiente],
            ),
        ],
    )

    return ListaPaginada(contenido=contenido, recargar_desde_cero=recargar_desde_cero)
