import pytest

from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from api.facturas import FacturaDetalle, _factura_detalle_desde
from diseno import tokens
from ui.componentes.sello_estado import construir_sello_estado
from ui.paginas.facturas.detalle import _puede_reenviar, mensajes_tras_reenvio


def _datos(**extra):
    return {"id": "f-1", "estado": "FIRMADO", **extra}


def _factura(**extra) -> FacturaDetalle:
    return _factura_detalle_desde(_datos(**extra))


def test_reenviable_true_se_lee_de_la_respuesta():
    assert _factura(reenviable=True).reenviable is True


def test_reenviable_ausente_es_false():
    assert _factura().reenviable is False


def test_reenviable_false_es_false():
    assert _factura(reenviable=False).reenviable is False


@pytest.mark.parametrize(
    "estado",
    ["GENERADO", "FIRMADO", "ENVIADO", "ACEPTADO", "RECHAZADO", "ERROR"],
)
@pytest.mark.parametrize("ultimo", [None, "ERROR_COMUNICACION", "ACEPTADO"])
def test_puede_reenviar_solo_depende_de_reenviable(estado, ultimo):
    extra = {"estado": estado, "ultimoResultadoConsulta": ultimo}
    assert _puede_reenviar(_factura(reenviable=True, **extra)) is True
    assert _puede_reenviar(_factura(reenviable=False, **extra)) is False


def _textos(control):
    if hasattr(control, "value") and isinstance(control.value, str):
        yield control.value
    for hijo in getattr(control, "controls", None) or []:
        yield from _textos(hijo)
    if getattr(control, "content", None) is not None:
        yield from _textos(control.content)


def _iconos_y_textos(control):
    if hasattr(control, "color") and control.color is not None:
        yield control.color
    for hijo in getattr(control, "controls", None) or []:
        yield from _iconos_y_textos(hijo)
    if getattr(control, "content", None) is not None:
        yield from _iconos_y_textos(control.content)


def test_sello_error_tiene_etiqueta_y_color_de_error():
    sello = construir_sello_estado("ERROR")
    assert "Error" in list(_textos(sello))
    assert set(_iconos_y_textos(sello)) == {tokens.ESTADO_ERROR_COMUNICACION}
    assert sello.border.top.color == tokens.ESTADO_ERROR_COMUNICACION


async def test_reenviar_409_devuelve_fallo_con_mensaje(monkeypatch):
    import api.facturas as m

    async def _fake(*a, **kw):
        return ApiFallo(error=ErrorApi(mensaje="Reenvío en curso.", status=409))

    monkeypatch.setattr(m, "peticion_autenticada", _fake)
    resultado = await m.reenviar_factura("f-1")
    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 409
    assert resultado.error.mensaje == "Reenvío en curso."


def test_mensajes_409_muestra_mensaje_del_backend():
    r = ApiFallo(error=ErrorApi(mensaje="No reenviable.", status=409))
    assert mensajes_tras_reenvio(r) == ("No reenviable.", None)


def test_mensajes_exito_con_estado_error_muestra_mensaje_respuesta():
    r = ApiExito(datos=_factura(estado="ERROR", mensajeRespuesta="Hacienda no responde"))
    assert mensajes_tras_reenvio(r) == (None, "Hacienda no responde")


def test_mensajes_exito_con_estado_error_sin_mensaje_usa_respaldo():
    r = ApiExito(datos=_factura(estado="ERROR"))
    error, info = mensajes_tras_reenvio(r)
    assert error is None and info


@pytest.mark.parametrize("estado", ["ACEPTADO", "RECHAZADO", "ENVIADO"])
def test_mensajes_exito_otro_estado_sin_textos(estado):
    r = ApiExito(datos=_factura(estado=estado, mensajeRespuesta="x"))
    assert mensajes_tras_reenvio(r) == (None, None)
