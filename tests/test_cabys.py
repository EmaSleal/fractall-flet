import api.cabys as cabys_module
from api.cabys import CabysResultado, buscar_cabys
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(cabys_module, "peticion_autenticada", _fake)


async def test_buscar_cabys_exitoso(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "total": 1,
                "cantidad": 1,
                "exitosa": True,
                "mensajeError": None,
                "cabys": [
                    {
                        "codigo": "1234567890123",
                        "codigoFormateado": "12345678901.23",
                        "descripcion": "Arroz",
                        "impuesto": 13,
                    }
                ],
            }
        ),
    )

    resultado = await buscar_cabys("arroz")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos[0], CabysResultado)
    assert resultado.datos[0].impuesto == 13


async def test_buscar_cabys_no_exitosa_se_reporta_como_fallo(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "exitosa": False,
                "mensajeError": "Servicio de Hacienda no disponible.",
                "cabys": [],
            }
        ),
    )

    resultado = await buscar_cabys("arroz")

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.mensaje == "Servicio de Hacienda no disponible."


async def test_buscar_cabys_pasa_parametros_correctos(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"exitosa": True, "cabys": []}),
        capturar_en=llamadas,
    )

    await buscar_cabys("arroz", top=5)

    assert llamadas[0]["parametros"] == {"q": "arroz", "top": 5}
