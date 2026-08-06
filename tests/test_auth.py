import api.auth as auth_module
from api.auth import (
    AccessToken,
    MfaPendiente,
    RespuestaMensaje,
    SeleccionTenantRequerida,
    TenantCambiado,
    cambiar_tenant,
    login,
    recuperar_password,
    restablecer_password,
    seleccionar_tenant,
)
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi


def _mockear_peticion(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(auth_module, "peticion", _fake)


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(auth_module, "peticion_autenticada", _fake)


async def test_login_acceso_directo(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(
            datos={
                "accessToken": "a",
                "refreshToken": "r",
                "empresaId": "e-1",
            }
        ),
    )

    resultado = await login("u@x.com", "pass")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, AccessToken)
    assert resultado.datos.access_token == "a"
    assert resultado.datos.empresa_id == "e-1"


async def test_login_seleccion_tenant_requerida(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"tokenSeleccionTenant": "t"}),
    )

    resultado = await login("u@x.com", "pass")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, SeleccionTenantRequerida)
    assert resultado.datos.token_seleccion_tenant == "t"


async def test_login_mfa_pendiente(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(
            datos={"tokenMfaPendiente": "m", "requiereEnrolamiento": True}
        ),
    )

    resultado = await login("u@x.com", "pass")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, MfaPendiente)
    assert resultado.datos.requiere_enrolamiento is True


async def test_login_credenciales_invalidas(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="Credenciales inválidas.", status=401)),
    )

    resultado = await login("u@x.com", "mal")

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 401


async def test_seleccionar_tenant_acceso_directo(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"accessToken": "a", "refreshToken": "r", "empresaId": "e-1"}),
    )

    resultado = await seleccionar_tenant("token-seleccion", "e-1")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, AccessToken)


async def test_seleccionar_tenant_mfa_pendiente(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"tokenMfaPendiente": "m", "requiereEnrolamiento": False}),
    )

    resultado = await seleccionar_tenant("token-seleccion", "e-1")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, MfaPendiente)


async def test_recuperar_password(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(datos={"mensaje": "Si el correo existe, se envió un enlace."}),
    )

    resultado = await recuperar_password("ana@x.com")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, RespuestaMensaje)


async def test_restablecer_password(monkeypatch):
    _mockear_peticion(monkeypatch, ApiExito(datos={"mensaje": "Contraseña actualizada."}))

    resultado = await restablecer_password("token-reset", "Abc123!!")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, RespuestaMensaje)


async def test_restablecer_password_token_invalido(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="Token inválido o expirado.", status=401)),
    )

    resultado = await restablecer_password("token-malo", "Abc123!!")

    assert isinstance(resultado, ApiFallo)


async def test_cambiar_tenant(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"accessToken": "nuevo-token", "refreshToken": None, "empresaId": "e-2"}),
        capturar_en=llamadas,
    )

    resultado = await cambiar_tenant("e-2")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, TenantCambiado)
    assert resultado.datos.access_token == "nuevo-token"
    assert resultado.datos.empresa_id == "e-2"
    assert llamadas[0]["cuerpo"] == {"empresaId": "e-2"}


async def test_cambiar_tenant_error(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="Membresía inactiva.", status=403))
    )

    resultado = await cambiar_tenant("e-2")

    assert isinstance(resultado, ApiFallo)
