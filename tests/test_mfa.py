import api.mfa as mfa_module
from api.auth import AccessToken
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from api.mfa import MfaEnrolamiento, confirmar_enrolamiento, iniciar_enrolamiento, verificar_codigo


def _mockear_peticion(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(mfa_module, "peticion", _fake)


async def test_iniciar_enrolamiento_usa_nombres_de_campo_reales(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"qrCodeBase64Png": "iVBORw0K...", "secretoBase32": "ABC234"}),
    )

    resultado = await iniciar_enrolamiento("token-mfa")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, MfaEnrolamiento)
    assert resultado.datos.qr_code_base64_png == "iVBORw0K..."
    assert resultado.datos.secreto_base32 == "ABC234"


async def test_confirmar_enrolamiento_devuelve_access_token(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"accessToken": "a", "refreshToken": "r", "empresaId": "e-1"}),
    )

    resultado = await confirmar_enrolamiento("token-mfa", "123456")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, AccessToken)


async def test_verificar_codigo_incorrecto(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="Código incorrecto.", status=401)),
    )

    resultado = await verificar_codigo("token-mfa", "000000")

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 401
