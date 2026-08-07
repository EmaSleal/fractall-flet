from typing import Optional

import flet as ft
from flet_secure_storage import SecureStorage

_CLAVE_ACCESO = "fractall_access_token"
_CLAVE_REFRESCO = "fractall_refresh_token"
_CLAVE_EMPRESA = "fractall_empresa_id"

_ATRIBUTO_ALMACEN = "_fractall_almacen_seguro"

# Guardado como atributo de `page`, no en un ContextVar: Flet despacha cada
# evento entrante del cliente (click, confirmación de cambio de ruta) en un
# asyncio.Task independiente creado por el loop de mensajes de la conexión
# (flet/messaging/flet_socket_server.py::_on_message) — no anidado dentro
# del task que originó la navegación. Un ContextVar seteado en un handler
# (p. ej. dentro de al_enviar) no es visible en el task del próximo evento,
# aunque sea la misma sesión — confirmado leyendo el código de Flet, y es lo
# que causaba que guardar_tokens() fallara en silencio. `page` sí es el
# mismo objeto en todos esos tasks, y `flet.context.page` lo resuelve
# siempre a la sesión correcta porque Flet resetea su propio ContextVar
# interno (_context_page) al principio de cada dispatch_event.


def inicializar(page: ft.Page, almacen: SecureStorage) -> None:
    """Se llama una vez desde main(page), con la instancia de SecureStorage
    de esa page/sesión, ya montada en page.services."""
    setattr(page, _ATRIBUTO_ALMACEN, almacen)


def _requerir_almacen() -> SecureStorage:
    almacen = getattr(ft.context.page, _ATRIBUTO_ALMACEN, None)
    if almacen is None:
        raise RuntimeError("La sesión no fue inicializada. Llamá a inicializar() en main().")
    return almacen


async def guardar_tokens(access_token: str, refresh_token: str) -> None:
    almacen = _requerir_almacen()
    await almacen.set(_CLAVE_ACCESO, access_token)
    await almacen.set(_CLAVE_REFRESCO, refresh_token)


async def obtener_token_acceso() -> Optional[str]:
    return await _requerir_almacen().get(_CLAVE_ACCESO)


async def obtener_token_refresco() -> Optional[str]:
    return await _requerir_almacen().get(_CLAVE_REFRESCO)


async def guardar_empresa_activa(empresa_id: str) -> None:
    await _requerir_almacen().set(_CLAVE_EMPRESA, empresa_id)


async def obtener_empresa_activa() -> Optional[str]:
    return await _requerir_almacen().get(_CLAVE_EMPRESA)


async def hay_sesion_activa() -> bool:
    return await _requerir_almacen().contains_key(_CLAVE_ACCESO)


async def cerrar_sesion() -> None:
    await _requerir_almacen().clear()
