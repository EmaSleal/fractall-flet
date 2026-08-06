import api.tipo_cambio as tipo_cambio_module
from api.tipo_cambio import obtener_tipo_cambio_dolar


class _RespuestaFalsa:
    def __init__(self, status_code, datos):
        self.status_code = status_code
        self._datos = datos

    def json(self):
        return self._datos


class _ClienteFalso:
    def __init__(self, respuesta):
        self._respuesta = respuesta

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url):
        return self._respuesta


def _mockear_cliente(monkeypatch, respuesta):
    monkeypatch.setattr(
        tipo_cambio_module.httpx, "AsyncClient", lambda **kw: _ClienteFalso(respuesta)
    )


async def test_obtener_tipo_cambio_exitoso(monkeypatch):
    _mockear_cliente(
        monkeypatch, _RespuestaFalsa(200, {"venta": {"valor": 545.32}})
    )

    valor = await obtener_tipo_cambio_dolar()

    assert valor == 545.32


async def test_obtener_tipo_cambio_no_bloqueante_si_falla(monkeypatch):
    _mockear_cliente(monkeypatch, _RespuestaFalsa(500, {}))

    valor = await obtener_tipo_cambio_dolar()

    assert valor is None


async def test_obtener_tipo_cambio_no_bloqueante_si_shape_inesperado(monkeypatch):
    _mockear_cliente(monkeypatch, _RespuestaFalsa(200, {"algo": "distinto"}))

    valor = await obtener_tipo_cambio_dolar()

    assert valor is None
