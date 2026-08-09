import api.ubicacion as ubicacion_module
from api.cliente import ApiExito
from api.ubicacion import Canton, Distrito, Provincia, listar_cantones, listar_distritos, listar_provincias


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(args)
        return resultado

    monkeypatch.setattr(ubicacion_module, "peticion_autenticada", _fake)


async def test_listar_provincias(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiExito(datos=[{"codigo": "1", "nombre": "San José"}])
    )

    resultado = await listar_provincias()

    assert isinstance(resultado, ApiExito)
    assert resultado.datos == [Provincia(codigo="1", nombre="San José")]


async def test_listar_cantones(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos=[{"provinciaCodigo": "1", "codigo": "01", "nombre": "San José"}]),
        capturar_en=llamadas,
    )

    resultado = await listar_cantones("1")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos == [Canton(provincia_codigo="1", codigo="01", nombre="San José")]
    assert llamadas[0][1] == "/catalogo/ubicacion/provincias/1/cantones"


async def test_listar_distritos(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos=[
                {
                    "provinciaCodigo": "1",
                    "cantonCodigo": "01",
                    "codigo": "01",
                    "nombre": "Carmen",
                }
            ]
        ),
        capturar_en=llamadas,
    )

    resultado = await listar_distritos("1", "01")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos == [
        Distrito(provincia_codigo="1", canton_codigo="01", codigo="01", nombre="Carmen")
    ]
    assert llamadas[0][1] == "/catalogo/ubicacion/cantones/1/01/distritos"
