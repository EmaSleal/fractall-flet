"""Estado transitorio en memoria para pasar tokens de alcance mínimo entre
pantallas del flujo de auth (selección de tenant, MFA). A diferencia de
`api.sesion`, esto no usa SecureStorage: son tokens de 5-10 min de vida que
no necesitan sobrevivir un reinicio del proceso — si la app se cierra a
mitad del flujo, el usuario simplemente vuelve a iniciar sesión.

Guardado en un ContextVar (no en variables de módulo planas) por la misma
razón que api.sesion: Flet corre todas las sesiones concurrentes del deploy
web en un solo proceso, y una variable plana se pisaría entre dos usuarios
que estén a mitad del login al mismo tiempo. Ver la nota en api/sesion.py
para el detalle de por qué esto queda aislado correctamente incluso con
page.run_task()."""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class _EstadoAuth:
    token_seleccion_tenant: Optional[str] = None
    token_mfa_pendiente: Optional[str] = None
    requiere_enrolamiento_mfa: bool = False


_estado: ContextVar[_EstadoAuth] = ContextVar("estado_navegacion", default=_EstadoAuth())


def establecer_seleccion_tenant(token: str) -> None:
    _estado.set(_EstadoAuth(token_seleccion_tenant=token))


def establecer_mfa_pendiente(token: str, requiere_enrolamiento: bool) -> None:
    _estado.set(
        _EstadoAuth(token_mfa_pendiente=token, requiere_enrolamiento_mfa=requiere_enrolamiento)
    )


def obtener_token_seleccion_tenant() -> Optional[str]:
    return _estado.get().token_seleccion_tenant


def obtener_token_mfa_pendiente() -> Optional[str]:
    return _estado.get().token_mfa_pendiente


def requiere_enrolamiento_mfa() -> bool:
    return _estado.get().requiere_enrolamiento_mfa


def limpiar() -> None:
    _estado.set(_EstadoAuth())
