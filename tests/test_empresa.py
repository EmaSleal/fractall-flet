import api.empresa as empresa_module
from api.cliente import ApiExito, ApiFallo
from api.empresa import (
    DatosFiscales,
    Empresa,
    actualizar_datos_fiscales,
    cambiar_ambiente,
    cargar_certificado,
    configurar_credenciales_hacienda,
    obtener_empresa,
)
from api.errores import ErrorApi


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(empresa_module, "peticion_autenticada", _fake)


async def test_obtener_empresa(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "e-1",
                "razonSocial": "Ana S.A.",
                "status": "HABILITADA",
                "tieneCertificado": True,
            }
        ),
    )

    resultado = await obtener_empresa()

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, Empresa)
    assert resultado.datos.status == "HABILITADA"
    assert resultado.datos.tiene_certificado is True


async def test_actualizar_datos_fiscales_convierte_vacios_a_null(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"id": "e-1", "status": "REGISTRADA", "tieneCertificado": False}),
        capturar_en=llamadas,
    )

    await actualizar_datos_fiscales(
        DatosFiscales(razon_social="Ana S.A.", nombre_comercial="  ", email="")
    )

    cuerpo = llamadas[0]["cuerpo"]
    assert cuerpo["razonSocial"] == "Ana S.A."
    assert cuerpo["nombreComercial"] is None
    assert cuerpo["email"] is None


async def test_cargar_certificado_arma_multipart_correcto(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}), capturar_en=llamadas)

    await cargar_certificado("empresa.p12", b"contenido-binario", "1234")

    llamada = llamadas[0]
    assert llamada["archivos"] == {
        "certificado": ("empresa.p12", b"contenido-binario", "application/x-pkcs12")
    }
    assert llamada["datos_formulario"] == {"pin": "1234"}
    # el body JSON no debe ir junto con el multipart
    assert llamada.get("cuerpo") is None


async def test_cargar_certificado_error(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="PIN incorrecto.", status=400)),
    )

    resultado = await cargar_certificado("empresa.p12", b"x", "0000")

    assert isinstance(resultado, ApiFallo)


async def test_configurar_credenciales_hacienda(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}), capturar_en=llamadas)

    resultado = await configurar_credenciales_hacienda("usuario", "clave", "SANDBOX")

    assert isinstance(resultado, ApiExito)
    assert llamadas[0]["cuerpo"] == {
        "usuarioHacienda": "usuario",
        "password": "clave",
        "ambiente": "SANDBOX",
    }


async def test_cambiar_ambiente(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}), capturar_en=llamadas)

    resultado = await cambiar_ambiente("PRODUCCION")

    assert isinstance(resultado, ApiExito)
    assert llamadas[0]["cuerpo"] == {"ambiente": "PRODUCCION"}
