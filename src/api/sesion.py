from contextvars import ContextVar
from typing import Optional

from flet_secure_storage import SecureStorage

_CLAVE_ACCESO = "fractall_access_token"
_CLAVE_REFRESCO = "fractall_refresh_token"
_CLAVE_EMPRESA = "fractall_empresa_id"

# ContextVar, no una variable de módulo plana: Flet corre todas las sesiones
# concurrentes del deploy web en un solo proceso Python (confirmado en
# flet/app.py::on_session_created y en page.run_task, que hacen exactamente
# esto mismo con su propio _context_page). Una variable plana se pisaría
# entre dos usuarios conectados al mismo tiempo — con un ContextVar, cada
# sesión (y cada tarea que dispare vía page.run_task dentro de ella) ve su
# propio valor, aislado del resto, sin tener que pasar `page` a mano por
# toda la capa api/. En desktop/mobile (un proceso = un usuario) se comporta
# igual que una variable plana.
_almacen: ContextVar[Optional[SecureStorage]] = ContextVar("almacen_sesion", default=None)


def inicializar(almacen: SecureStorage) -> None:
    """Se llama una vez desde main(page), con la instancia de SecureStorage
    de esa page/sesión. flet_secure_storage.SecureStorage se auto-registra en
    la page activa al construirse: acá solo guardamos la referencia para
    poder usarla desde fuera de la UI."""
    _almacen.set(almacen)


def _requerir_almacen() -> SecureStorage:
    almacen = _almacen.get()
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
