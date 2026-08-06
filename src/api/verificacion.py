from .auth import RespuestaMensaje, respuesta_mensaje_desde
from .cliente import ApiExito, ApiFallo, ApiResultado, peticion


async def verificar_email(token: str) -> ApiResultado[RespuestaMensaje]:
    resultado = await peticion(
        "GET", "/auth/verificar-email", parametros={"token": token}
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=respuesta_mensaje_desde(resultado.datos))


async def reenviar_verificacion(email: str) -> ApiResultado[RespuestaMensaje]:
    resultado = await peticion(
        "POST", "/auth/reenviar-verificacion", cuerpo={"email": email}
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=respuesta_mensaje_desde(resultado.datos))
