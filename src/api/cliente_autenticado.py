from typing import Any, Optional

from . import sesion
from .cliente import ApiExito, ApiFallo, ApiResultado, peticion, peticion_binaria


class SesionExpirada(Exception):
    """El refresh token no existe, expiró o fue rechazado por el backend."""


async def peticion_autenticada(
    metodo: str,
    ruta: str,
    *,
    cuerpo: Optional[dict[str, Any]] = None,
    parametros: Optional[dict[str, Any]] = None,
    archivos: Optional[dict[str, Any]] = None,
    datos_formulario: Optional[dict[str, Any]] = None,
) -> ApiResultado:
    token = await sesion.obtener_token_acceso()
    resultado = await peticion(
        metodo,
        ruta,
        cuerpo=cuerpo,
        parametros=parametros,
        archivos=archivos,
        datos_formulario=datos_formulario,
        token=token,
    )

    if isinstance(resultado, ApiFallo) and resultado.error.status == 401:
        resultado = await _refrescar_y_reintentar(
            metodo, ruta, cuerpo, parametros, archivos, datos_formulario
        )

    return resultado


async def _refrescar_y_reintentar(
    metodo: str,
    ruta: str,
    cuerpo: Optional[dict[str, Any]],
    parametros: Optional[dict[str, Any]],
    archivos: Optional[dict[str, Any]] = None,
    datos_formulario: Optional[dict[str, Any]] = None,
) -> ApiResultado:
    refresh_token = await sesion.obtener_token_refresco()
    empresa_id = await sesion.obtener_empresa_activa()
    if not refresh_token or not empresa_id:
        await sesion.cerrar_sesion()
        raise SesionExpirada

    renovacion = await peticion(
        "POST",
        "/auth/refrescar",
        cuerpo={"refreshToken": refresh_token, "empresaId": empresa_id},
    )
    if isinstance(renovacion, ApiFallo):
        await sesion.cerrar_sesion()
        raise SesionExpirada

    nuevo_access_token = renovacion.datos["accessToken"]
    # POST /auth/refrescar no rota el refresh token (viene null): conservamos el existente.
    await sesion.guardar_tokens(nuevo_access_token, refresh_token)

    return await peticion(
        metodo,
        ruta,
        cuerpo=cuerpo,
        parametros=parametros,
        archivos=archivos,
        datos_formulario=datos_formulario,
        token=nuevo_access_token,
    )


async def peticion_autenticada_binaria(metodo: str, ruta: str) -> ApiResultado:
    token = await sesion.obtener_token_acceso()
    resultado = await peticion_binaria(metodo, ruta, token=token)

    if isinstance(resultado, ApiFallo) and resultado.error.status == 401:
        refresh_token = await sesion.obtener_token_refresco()
        empresa_id = await sesion.obtener_empresa_activa()
        if not refresh_token or not empresa_id:
            await sesion.cerrar_sesion()
            raise SesionExpirada

        renovacion = await peticion(
            "POST",
            "/auth/refrescar",
            cuerpo={"refreshToken": refresh_token, "empresaId": empresa_id},
        )
        if isinstance(renovacion, ApiFallo):
            await sesion.cerrar_sesion()
            raise SesionExpirada

        nuevo_access_token = renovacion.datos["accessToken"]
        await sesion.guardar_tokens(nuevo_access_token, refresh_token)
        resultado = await peticion_binaria(metodo, ruta, token=nuevo_access_token)

    return resultado


async def cerrar_sesion() -> None:
    token = await sesion.obtener_token_acceso()
    refresh_token = await sesion.obtener_token_refresco()
    if token and refresh_token:
        await peticion(
            "POST",
            "/auth/logout",
            cuerpo={"refreshToken": refresh_token},
            token=token,
        )
    await sesion.cerrar_sesion()
