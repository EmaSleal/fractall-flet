import api.unidades_medida as unidades_module
from api.cliente import ApiExito
from api.unidades_medida import UnidadMedida, listar_unidades_medida


async def test_listar_unidades_medida(monkeypatch):
    async def _fake(*args, **kwargs):
        return ApiExito(datos=[{"codigo": "Sp", "descripcion": "Servicios profesionales"}])

    monkeypatch.setattr(unidades_module, "peticion_autenticada", _fake)

    resultado = await listar_unidades_medida()

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos[0], UnidadMedida)
    assert resultado.datos[0].codigo == "Sp"
