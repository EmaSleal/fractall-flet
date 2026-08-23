import polling_estado as pe
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi


async def _sin_espera(_segundos):
    return None


async def test_no_consulta_si_estado_inicial_ya_es_terminal(monkeypatch):
    monkeypatch.setattr(pe.asyncio, "sleep", _sin_espera)
    llamadas = []

    async def consultar():
        llamadas.append(1)
        return ApiExito(datos={"estado": "ACEPTADO"})

    resultado = await pe.esperar_estado_final(
        consultar=consultar, estado_inicial="ACEPTADO", extraer_estado=lambda d: d["estado"]
    )

    assert resultado is None
    assert llamadas == []


async def test_devuelve_datos_en_cuanto_el_estado_deja_de_ser_no_terminal(monkeypatch):
    monkeypatch.setattr(pe.asyncio, "sleep", _sin_espera)
    estados = iter(["ENVIADO", "ENVIADO", "ACEPTADO"])

    async def consultar():
        return ApiExito(datos={"estado": next(estados)})

    resultado = await pe.esperar_estado_final(
        consultar=consultar, estado_inicial="GENERADO", extraer_estado=lambda d: d["estado"]
    )

    assert resultado == {"estado": "ACEPTADO"}


async def test_devuelve_none_si_se_agotan_los_intentos(monkeypatch):
    monkeypatch.setattr(pe.asyncio, "sleep", _sin_espera)
    monkeypatch.setattr(pe, "MAX_INTENTOS", 3)

    async def consultar():
        return ApiExito(datos={"estado": "ENVIADO"})

    resultado = await pe.esperar_estado_final(
        consultar=consultar, estado_inicial="ENVIADO", extraer_estado=lambda d: d["estado"]
    )

    assert resultado is None


async def test_devuelve_none_si_la_consulta_falla(monkeypatch):
    monkeypatch.setattr(pe.asyncio, "sleep", _sin_espera)

    async def consultar():
        return ApiFallo(error=ErrorApi(mensaje="falló", status=500))

    resultado = await pe.esperar_estado_final(
        consultar=consultar, estado_inicial="GENERADO", extraer_estado=lambda d: d["estado"]
    )

    assert resultado is None
