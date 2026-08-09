import api.tipo_cambio as tipo_cambio_module
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from api.tipo_cambio import obtener_tipo_cambio_dolar


def _mockear_peticion_autenticada(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(tipo_cambio_module, "peticion_autenticada", _fake)


async def test_obtener_tipo_cambio_exitoso(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiExito(datos={"venta": {"valor": 545.32}})
    )

    valor = await obtener_tipo_cambio_dolar()

    assert valor == 545.32


async def test_obtener_tipo_cambio_no_bloqueante_si_falla(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiFallo(error=ErrorApi(status=502, mensaje="No disponible"))
    )

    valor = await obtener_tipo_cambio_dolar()

    assert valor is None


async def test_obtener_tipo_cambio_no_bloqueante_si_shape_inesperado(monkeypatch):
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={"algo": "distinto"}))

    valor = await obtener_tipo_cambio_dolar()

    assert valor is None
