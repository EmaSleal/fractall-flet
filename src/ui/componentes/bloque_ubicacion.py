from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

import flet as ft

from api.cliente import ApiFallo
from api.ubicacion import listar_cantones, listar_distritos, listar_provincias


@dataclass
class BloqueUbicacion:
    """Réplica de use-ubicacion-cascada.ts + BloqueUbicacion de
    fractall-frontend: 3 Dropdown poblados desde el catálogo real de
    ubicación de Costa Rica, en cascada (provincia -> cantón -> distrito).
    Elegir un nivel resetea sus hijos y los deshabilita hasta que el padre
    tenga un valor — imposible mandar una combinación inválida desde la UI."""

    provincia: ft.Dropdown
    canton: ft.Dropdown
    distrito: ft.Dropdown
    cargar_provincias: Callable[[], Awaitable[None]]
    sincronizar_cascada: Callable[[], Awaitable[None]]


def construir_bloque_ubicacion(page: ft.Page, *, col: Optional[dict] = None) -> BloqueUbicacion:
    campo_provincia = ft.Dropdown(label="Provincia", hint_text="Seleccioná una provincia", col=col)
    campo_canton = ft.Dropdown(
        label="Cantón", hint_text="Elegí primero una provincia", disabled=True, col=col
    )
    campo_distrito = ft.Dropdown(
        label="Distrito", hint_text="Elegí primero un cantón", disabled=True, col=col
    )

    async def _cargar_cantones() -> None:
        provincia_codigo = campo_provincia.value
        if not provincia_codigo:
            campo_canton.options = []
            campo_canton.disabled = True
            campo_canton.hint_text = "Elegí primero una provincia"
            return
        resultado = await listar_cantones(provincia_codigo)
        if isinstance(resultado, ApiFallo):
            return
        campo_canton.options = [
            ft.DropdownOption(key=c.codigo, text=c.nombre) for c in resultado.datos
        ]
        campo_canton.disabled = False
        campo_canton.hint_text = "Seleccioná un cantón"

    async def _cargar_distritos() -> None:
        provincia_codigo = campo_provincia.value
        canton_codigo = campo_canton.value
        if not provincia_codigo or not canton_codigo:
            campo_distrito.options = []
            campo_distrito.disabled = True
            campo_distrito.hint_text = "Elegí primero un cantón"
            return
        resultado = await listar_distritos(provincia_codigo, canton_codigo)
        if isinstance(resultado, ApiFallo):
            return
        campo_distrito.options = [
            ft.DropdownOption(key=d.codigo, text=d.nombre) for d in resultado.datos
        ]
        campo_distrito.disabled = False
        campo_distrito.hint_text = "Seleccioná un distrito"

    async def _al_cambiar_provincia(e: ft.Event[ft.Dropdown]) -> None:
        campo_canton.value = None
        campo_distrito.value = None
        campo_distrito.options = []
        campo_distrito.disabled = True
        campo_distrito.hint_text = "Elegí primero un cantón"
        page.update()
        await _cargar_cantones()
        page.update()

    async def _al_cambiar_canton(e: ft.Event[ft.Dropdown]) -> None:
        campo_distrito.value = None
        page.update()
        await _cargar_distritos()
        page.update()

    campo_provincia.on_select = _al_cambiar_provincia
    campo_canton.on_select = _al_cambiar_canton

    async def cargar_provincias() -> None:
        resultado = await listar_provincias()
        if isinstance(resultado, ApiFallo):
            return
        campo_provincia.options = [
            ft.DropdownOption(key=p.codigo, text=p.nombre) for p in resultado.datos
        ]
        page.update()

    async def sincronizar_cascada() -> None:
        """Reconstruye las opciones de cantón/distrito a partir de los
        valores ya seleccionados en los 3 Dropdown — para edición, donde el
        valor inicial se asigna por código antes de que exista una opción
        que lo respalde (ver aplicar_empresa / cliente_inicial)."""
        await _cargar_cantones()
        await _cargar_distritos()
        page.update()

    return BloqueUbicacion(
        provincia=campo_provincia,
        canton=campo_canton,
        distrito=campo_distrito,
        cargar_provincias=cargar_provincias,
        sincronizar_cascada=sincronizar_cascada,
    )
