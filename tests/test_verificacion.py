import api.verificacion as verificacion_module
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from api.verificacion import RespuestaMensaje, reenviar_verificacion, verificar_email


def _mockear_peticion(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(verificacion_module, "peticion", _fake)


async def test_verificar_email(monkeypatch):
    _mockear_peticion(monkeypatch, ApiExito(datos={"mensaje": "Correo verificado."}))

    resultado = await verificar_email("token-verificacion")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, RespuestaMensaje)


async def test_verificar_email_token_invalido(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="Token inválido o expirado.", status=401)),
    )

    resultado = await verificar_email("token-malo")

    assert isinstance(resultado, ApiFallo)


async def test_reenviar_verificacion(monkeypatch):
    _mockear_peticion(monkeypatch, ApiExito(datos={"mensaje": "Reenviado."}))

    resultado = await reenviar_verificacion("ana@x.com")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, RespuestaMensaje)
