import api.auth as auth_module
from api.auth import RegistroExitoso, registro
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi


def _mockear_peticion(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(auth_module, "peticion", _fake)


async def test_registro_exitoso(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(
            datos={
                "usuarioId": "u-1",
                "empresaId": "e-1",
                "mensaje": "Revisá tu correo.",
            }
        ),
    )

    resultado = await registro("Ana", "ana@x.com", "Abc123!!", "Ana S.A.")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, RegistroExitoso)
    assert resultado.datos.usuario_id == "u-1"


async def test_registro_envia_activar_mfa_solo_si_fue_definido(monkeypatch):
    llamadas = []
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"usuarioId": "u-1", "empresaId": "e-1", "mensaje": ""}),
        capturar_en=llamadas,
    )

    await registro("Ana", "ana@x.com", "Abc123!!", "Ana S.A.")
    assert "activarMfa" not in llamadas[0]["cuerpo"]

    await registro("Ana", "ana@x.com", "Abc123!!", "Ana S.A.", activar_mfa=True)
    assert llamadas[1]["cuerpo"]["activarMfa"] is True


async def test_registro_email_duplicado(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="El correo ya está registrado.", status=409)),
    )

    resultado = await registro("Ana", "ana@x.com", "Abc123!!", "Ana S.A.")

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 409
