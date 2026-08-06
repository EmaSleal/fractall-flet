import re
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, Union

import httpx

from core.config import BACKEND_URL

from .errores import ErrorApi, normalizar_error

_RE_CONTENT_DISPOSITION_FILENAME = re.compile(r'filename="([^"]+)"')

T = TypeVar("T")

_cliente_http: Optional[httpx.AsyncClient] = None


def _obtener_cliente_http() -> httpx.AsyncClient:
    global _cliente_http
    if _cliente_http is None:
        _cliente_http = httpx.AsyncClient(base_url=BACKEND_URL, timeout=15.0)
    return _cliente_http


@dataclass
class ApiExito(Generic[T]):
    datos: T


@dataclass
class ApiFallo:
    error: ErrorApi


ApiResultado = Union[ApiExito[T], ApiFallo]


async def peticion(
    metodo: str,
    ruta: str,
    *,
    cuerpo: Optional[dict[str, Any]] = None,
    parametros: Optional[dict[str, Any]] = None,
    archivos: Optional[dict[str, Any]] = None,
    datos_formulario: Optional[dict[str, Any]] = None,
    token: Optional[str] = None,
) -> ApiResultado[T]:
    """`archivos`/`datos_formulario` arman un multipart/form-data (para
    subir el certificado .p12) — httpx calcula el Content-Type con el
    boundary correcto solo, nunca hay que setearlo a mano (igual que hace
    fetch en el frontend)."""
    encabezados = {"Authorization": f"Bearer {token}"} if token else None
    respuesta = await _obtener_cliente_http().request(
        metodo,
        ruta,
        json=cuerpo,
        params=parametros,
        files=archivos,
        data=datos_formulario,
        headers=encabezados,
    )

    if respuesta.status_code >= 400:
        try:
            cuerpo_error = respuesta.json()
        except ValueError:
            cuerpo_error = None
        return ApiFallo(error=normalizar_error(respuesta.status_code, cuerpo_error))

    if not respuesta.content:
        return ApiExito(datos=None)
    return ApiExito(datos=respuesta.json())


@dataclass
class ArchivoDescargado:
    contenido: bytes
    content_type: str
    nombre_archivo: Optional[str]


async def peticion_binaria(
    metodo: str, ruta: str, *, token: Optional[str] = None
) -> ApiResultado[ArchivoDescargado]:
    """Para descargas (PDF/XML) — no intenta parsear la respuesta exitosa
    como JSON, a diferencia de peticion()."""
    encabezados = {"Authorization": f"Bearer {token}"} if token else None
    respuesta = await _obtener_cliente_http().request(metodo, ruta, headers=encabezados)

    if respuesta.status_code >= 400:
        try:
            cuerpo_error = respuesta.json()
        except ValueError:
            cuerpo_error = None
        return ApiFallo(error=normalizar_error(respuesta.status_code, cuerpo_error))

    disposicion = respuesta.headers.get("content-disposition")
    coincidencia = (
        _RE_CONTENT_DISPOSITION_FILENAME.search(disposicion) if disposicion else None
    )

    return ApiExito(
        datos=ArchivoDescargado(
            contenido=respuesta.content,
            content_type=respuesta.headers.get("content-type", "application/octet-stream"),
            nombre_archivo=coincidencia.group(1) if coincidencia else None,
        )
    )
