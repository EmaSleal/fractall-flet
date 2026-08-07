"""Estado transitorio en memoria para pasar tokens de alcance mínimo entre
pantallas del flujo de auth (selección de tenant, MFA). A diferencia de
`api.sesion`, esto no usa SecureStorage: son tokens de 5-10 min de vida que
no necesitan sobrevivir un reinicio del proceso — si la app se cierra a
mitad del flujo, el usuario simplemente vuelve a iniciar sesión.

Guardado como atributo de `page` (no en un ContextVar): Flet despacha cada
evento entrante del cliente (click, confirmación de cambio de ruta) en un
asyncio.Task independiente creado por el loop de mensajes de la conexión
(flet/messaging/flet_socket_server.py::_on_message) — no anidado dentro del
task que originó la navegación. Un ContextVar seteado en un handler (p. ej.
al_enviar) no es visible en el task del próximo evento, aunque sea la misma
sesión — esto es lo que hacía que, tras un login con MFA pendiente, la
pantalla de verificación no encontrara el token y rebotara a /login. `page`
sí es el mismo objeto en todos esos tasks, y `flet.context.page` lo
resuelve siempre a la sesión correcta porque Flet resetea su propio
ContextVar interno (_context_page) al principio de cada dispatch_event."""

from dataclasses import dataclass
from typing import Optional

import flet as ft

_ATRIBUTO_ESTADO = "_fractall_estado_navegacion"


@dataclass(frozen=True)
class _EstadoAuth:
    token_seleccion_tenant: Optional[str] = None
    token_mfa_pendiente: Optional[str] = None
    requiere_enrolamiento_mfa: bool = False


def _obtener_estado() -> _EstadoAuth:
    return getattr(ft.context.page, _ATRIBUTO_ESTADO, _EstadoAuth())


def _guardar_estado(estado: _EstadoAuth) -> None:
    setattr(ft.context.page, _ATRIBUTO_ESTADO, estado)


def establecer_seleccion_tenant(token: str) -> None:
    _guardar_estado(_EstadoAuth(token_seleccion_tenant=token))


def establecer_mfa_pendiente(token: str, requiere_enrolamiento: bool) -> None:
    _guardar_estado(
        _EstadoAuth(token_mfa_pendiente=token, requiere_enrolamiento_mfa=requiere_enrolamiento)
    )


def obtener_token_seleccion_tenant() -> Optional[str]:
    return _obtener_estado().token_seleccion_tenant


def obtener_token_mfa_pendiente() -> Optional[str]:
    return _obtener_estado().token_mfa_pendiente


def requiere_enrolamiento_mfa() -> bool:
    return _obtener_estado().requiere_enrolamiento_mfa


def limpiar() -> None:
    _guardar_estado(_EstadoAuth())
