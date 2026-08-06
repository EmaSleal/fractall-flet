from dataclasses import dataclass
from typing import Optional, Union

from .cliente import ApiExito, ApiFallo, ApiResultado, peticion
from .cliente_autenticado import peticion_autenticada


@dataclass
class AccessToken:
    """Sesión resuelta: mismo shape que devuelven login directo,
    seleccionar-tenant, mfa/verificar y mfa/confirmar."""

    access_token: str
    refresh_token: str
    empresa_id: str


@dataclass
class SeleccionTenantRequerida:
    token_seleccion_tenant: str


@dataclass
class MfaPendiente:
    token_mfa_pendiente: str
    requiere_enrolamiento: bool


def access_token_desde(datos: dict) -> AccessToken:
    return AccessToken(
        access_token=datos["accessToken"],
        refresh_token=datos["refreshToken"],
        empresa_id=datos["empresaId"],
    )


LoginResultado = Union[AccessToken, SeleccionTenantRequerida, MfaPendiente]


async def login(email: str, password: str) -> ApiResultado[LoginResultado]:
    resultado = await peticion(
        "POST", "/auth/login", cuerpo={"email": email, "password": password}
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos

    if "tokenSeleccionTenant" in datos:
        return ApiExito(
            datos=SeleccionTenantRequerida(
                token_seleccion_tenant=datos["tokenSeleccionTenant"],
            )
        )

    if "tokenMfaPendiente" in datos:
        return ApiExito(
            datos=MfaPendiente(
                token_mfa_pendiente=datos["tokenMfaPendiente"],
                requiere_enrolamiento=datos["requiereEnrolamiento"],
            )
        )

    # Asumido por eliminación — el backend no manda un discriminador explícito
    # en el JSON (oneOf sin "tipo"). Válido solo porque no hay una cuarta forma
    # documentada; si el backend agrega un campo discriminador, reemplazar esto
    # por un switch sobre ese campo en vez de inferir por las claves presentes.
    return ApiExito(datos=access_token_desde(datos))


async def seleccionar_tenant(
    token_seleccion_tenant: str, empresa_id: str
) -> ApiResultado[Union[AccessToken, MfaPendiente]]:
    resultado = await peticion(
        "POST",
        "/auth/seleccionar-tenant",
        cuerpo={"empresaId": empresa_id},
        token=token_seleccion_tenant,
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    if "tokenMfaPendiente" in datos:
        return ApiExito(
            datos=MfaPendiente(
                token_mfa_pendiente=datos["tokenMfaPendiente"],
                requiere_enrolamiento=datos["requiereEnrolamiento"],
            )
        )
    return ApiExito(datos=access_token_desde(datos))


@dataclass
class RegistroExitoso:
    usuario_id: str
    empresa_id: str
    mensaje: str


async def registro(
    nombre: str,
    email: str,
    password: str,
    razon_social: str,
    activar_mfa: Optional[bool] = None,
) -> ApiResultado[RegistroExitoso]:
    cuerpo = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "razonSocial": razon_social,
    }
    if activar_mfa is not None:
        cuerpo["activarMfa"] = activar_mfa

    resultado = await peticion("POST", "/auth/registro", cuerpo=cuerpo)
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=RegistroExitoso(
            usuario_id=datos.get("usuarioId", ""),
            empresa_id=datos.get("empresaId", ""),
            mensaje=datos.get("mensaje", ""),
        )
    )


@dataclass
class RespuestaMensaje:
    mensaje: str


def respuesta_mensaje_desde(datos: dict) -> RespuestaMensaje:
    return RespuestaMensaje(mensaje=datos.get("mensaje", ""))


async def recuperar_password(email: str) -> ApiResultado[RespuestaMensaje]:
    resultado = await peticion(
        "POST", "/auth/recuperar-password", cuerpo={"email": email}
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=respuesta_mensaje_desde(resultado.datos))


async def restablecer_password(
    token: str, nueva_password: str
) -> ApiResultado[RespuestaMensaje]:
    resultado = await peticion(
        "POST",
        "/auth/restablecer-password",
        cuerpo={"token": token, "nuevaPassword": nueva_password},
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=respuesta_mensaje_desde(resultado.datos))


@dataclass
class TenantCambiado:
    access_token: str
    empresa_id: str


async def cambiar_tenant(empresa_id: str) -> ApiResultado[TenantCambiado]:
    """A diferencia de login/seleccionar-tenant (llamadas pre-sesión con
    token explícito), esta usa la sesión ya activa — de ahí
    peticion_autenticada en vez de peticion. El backend NO rota el refresh
    token acá (mismo comportamiento que /auth/refrescar): `refreshToken`
    puede venir null, así que este resultado no lo incluye — quien llame
    conserva el refresh token que ya tenía guardado."""
    resultado = await peticion_autenticada(
        "POST", "/auth/cambiar-tenant", cuerpo={"empresaId": empresa_id}
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    datos = resultado.datos
    return ApiExito(
        datos=TenantCambiado(access_token=datos["accessToken"], empresa_id=datos["empresaId"])
    )
