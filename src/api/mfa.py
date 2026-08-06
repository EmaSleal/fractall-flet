from dataclasses import dataclass

from .auth import AccessToken, access_token_desde
from .cliente import ApiExito, ApiFallo, ApiResultado, peticion


@dataclass
class MfaEnrolamiento:
    qr_code_base64_png: str
    secreto_base32: str


async def iniciar_enrolamiento(token_mfa_pendiente: str) -> ApiResultado[MfaEnrolamiento]:
    resultado = await peticion(
        "POST", "/auth/mfa/enrolar", token=token_mfa_pendiente
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=MfaEnrolamiento(
            qr_code_base64_png=datos.get("qrCodeBase64Png", ""),
            secreto_base32=datos.get("secretoBase32", ""),
        )
    )


async def confirmar_enrolamiento(
    token_mfa_pendiente: str, codigo: str
) -> ApiResultado[AccessToken]:
    resultado = await peticion(
        "POST",
        "/auth/mfa/confirmar",
        cuerpo={"codigo": codigo},
        token=token_mfa_pendiente,
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=access_token_desde(resultado.datos))


async def verificar_codigo(
    token_mfa_pendiente: str, codigo: str
) -> ApiResultado[AccessToken]:
    resultado = await peticion(
        "POST",
        "/auth/mfa/verificar",
        cuerpo={"codigo": codigo},
        token=token_mfa_pendiente,
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=access_token_desde(resultado.datos))
