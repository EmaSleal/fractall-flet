import api.facturas as facturas_module
from api.cliente import ApiExito, ApiFallo, ArchivoDescargado
from api.errores import ErrorApi
from api.facturas import (
    FacturaDetalle,
    FacturaResumen,
    PaginaFacturas,
    crear_factura,
    crear_nota_debito,
    crear_tiquete,
    descargar_pdf,
    listar_facturas,
    obtener_factura,
    reenviar_factura,
)


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(facturas_module, "peticion_autenticada", _fake)


def _mockear_peticion_binaria(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(facturas_module, "peticion_autenticada_binaria", _fake)


async def test_listar_facturas_mapea_items(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "items": [
                    {
                        "id": "f-1",
                        "consecutivo": "00100001010000000001",
                        "clienteNombre": "Ana",
                        "moneda": "CRC",
                        "total": 1000,
                        "estado": "ACEPTADO",
                        "fechaEmision": "2026-01-01",
                    }
                ],
                "nextCursor": None,
            }
        ),
    )

    resultado = await listar_facturas()

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, PaginaFacturas)
    assert isinstance(resultado.datos.items[0], FacturaResumen)
    assert resultado.datos.items[0].moneda == "CRC"


async def test_listar_facturas_pasa_filtros(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch, ApiExito(datos={"items": [], "nextCursor": None}), capturar_en=llamadas
    )

    await listar_facturas(
        estado="ACEPTADO",
        tipo_comprobante="04",
        cliente_id="c-1",
        desde="2026-01-01",
        hasta="2026-01-31",
    )

    assert llamadas[0]["parametros"] == {
        "limit": 20,
        "estado": "ACEPTADO",
        "tipoComprobante": "04",
        "clienteId": "c-1",
        "desde": "2026-01-01",
        "hasta": "2026-01-31",
    }


async def test_listar_facturas_mapea_tipo_comprobante(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "items": [
                    {
                        "id": "f-1",
                        "consecutivo": "00100001010000000001",
                        "clienteNombre": "Ana",
                        "moneda": "CRC",
                        "total": 1000,
                        "estado": "ACEPTADO",
                        "tipoComprobante": "04",
                        "fechaEmision": "2026-01-01",
                    }
                ],
                "nextCursor": None,
            }
        ),
    )

    resultado = await listar_facturas()

    assert isinstance(resultado, ApiExito)
    assert resultado.datos.items[0].tipo_comprobante == "04"


async def test_obtener_factura_detalle_hardcodea_moneda_crc(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "f-1",
                "clienteNombre": "Ana",
                "subtotal": 1000,
                "totalImpuesto": 130,
                "total": 1130,
                "estado": "GENERADO",
                "consecutivo": "001",
                "claveNumerica": "506...",
            }
        ),
    )

    resultado = await obtener_factura("f-1")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, FacturaDetalle)
    # FacturaResponse del backend no trae moneda -> fallback CRC
    assert resultado.datos.moneda == "CRC"


async def test_obtener_factura_detalle_mapea_factura_referencia_id(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "nd-1",
                "clienteNombre": "Ana",
                "estado": "GENERADO",
                "consecutivo": "002",
                "claveNumerica": "506...",
                "tipoComprobante": "02",
                "facturaReferenciaId": "f-origen",
            }
        ),
    )

    resultado = await obtener_factura("nd-1")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos.factura_referencia_id == "f-origen"


async def test_obtener_factura_detalle_sin_factura_referencia_id_es_none(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "f-1",
                "clienteNombre": "Ana",
                "estado": "ACEPTADO",
                "consecutivo": "001",
                "claveNumerica": "506...",
                "tipoComprobante": "01",
            }
        ),
    )

    resultado = await obtener_factura("f-1")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos.factura_referencia_id is None


async def test_obtener_factura_404_devuelve_none(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="No encontrada.", status=404))
    )

    resultado = await obtener_factura("f-x")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos is None


async def test_reenviar_factura(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"id": "f-1", "estado": "ENVIADO", "consecutivo": "001", "claveNumerica": "x"}),
    )

    resultado = await reenviar_factura("f-1")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos.estado == "ENVIADO"


async def test_descargar_pdf(monkeypatch):
    _mockear_peticion_binaria(
        monkeypatch,
        ApiExito(
            datos=ArchivoDescargado(
                contenido=b"%PDF-1.4...",
                content_type="application/pdf",
                nombre_archivo="factura.pdf",
            )
        ),
    )

    resultado = await descargar_pdf("f-1")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos.contenido == b"%PDF-1.4..."


async def test_crear_factura(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "f-nueva",
                "estado": "GENERADO",
                "consecutivo": "001",
                "claveNumerica": "506...",
            }
        ),
        capturar_en=llamadas,
    )

    cuerpo = {"clienteId": "c-1", "lineas": [{"productoId": "p-1", "cantidad": 1, "precioUnitario": 100}]}
    resultado = await crear_factura(cuerpo)

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, FacturaDetalle)
    assert llamadas[0]["cuerpo"] == cuerpo


async def test_crear_factura_error(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="clienteId: no existe", status=400))
    )

    resultado = await crear_factura({"clienteId": "c-x", "lineas": []})

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 400


async def test_crear_tiquete(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "t-nueva",
                "estado": "GENERADO",
                "consecutivo": "004",
                "claveNumerica": "506...",
            }
        ),
        capturar_en=llamadas,
    )

    cuerpo = {
        "condicionVenta": "01",
        "medioPago": "01",
        "moneda": "CRC",
        "tipoCambio": 1.0,
        "lineas": [{"productoId": "p-1", "cantidad": 1, "precioUnitario": 100}],
    }
    resultado = await crear_tiquete(cuerpo)

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, FacturaDetalle)
    assert llamadas[0]["cuerpo"] == cuerpo


async def test_crear_tiquete_sin_cliente_no_manda_clienteid(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"id": "t-1", "estado": "GENERADO", "consecutivo": "004", "claveNumerica": "x"}),
        capturar_en=llamadas,
    )

    cuerpo = {
        "condicionVenta": "01",
        "medioPago": "01",
        "moneda": "CRC",
        "tipoCambio": 1.0,
        "lineas": [{"productoId": "p-1", "cantidad": 1, "precioUnitario": 100}],
    }
    await crear_tiquete(cuerpo)

    assert "clienteId" not in llamadas[0]["cuerpo"]


async def test_crear_tiquete_error(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="tipoCambio: fuera de rango", status=400))
    )

    resultado = await crear_tiquete({"moneda": "USD", "tipoCambio": 100.0, "lineas": []})

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 400


async def test_crear_nota_debito(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "nd-nueva",
                "estado": "GENERADO",
                "consecutivo": "002",
                "claveNumerica": "506...",
                "tipoComprobante": "02",
                "facturaReferenciaId": "f-origen",
            }
        ),
        capturar_en=llamadas,
    )

    cuerpo = {
        "facturaReferenciaId": "f-origen",
        "codigoReferencia": "01",
        "lineas": [{"productoId": "p-1", "cantidad": 1, "precioUnitario": 100}],
    }
    resultado = await crear_nota_debito(cuerpo)

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, FacturaDetalle)
    assert resultado.datos.factura_referencia_id == "f-origen"
    assert llamadas[0]["cuerpo"] == cuerpo


async def test_crear_nota_debito_llama_al_endpoint_correcto(monkeypatch):
    llamadas = []

    async def _fake(metodo, ruta, **kwargs):
        llamadas.append((metodo, ruta))
        return ApiExito(
            datos={"id": "nd-1", "estado": "GENERADO", "consecutivo": "002", "claveNumerica": "x"}
        )

    monkeypatch.setattr(facturas_module, "peticion_autenticada", _fake)

    await crear_nota_debito({"facturaReferenciaId": "f-1", "codigoReferencia": "01", "lineas": []})

    assert llamadas[0] == ("POST", "/notas-debito")


async def test_crear_nota_debito_error(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="La factura origen no está ACEPTADO", status=409)),
    )

    resultado = await crear_nota_debito(
        {"facturaReferenciaId": "f-1", "codigoReferencia": "01", "lineas": []}
    )

    assert isinstance(resultado, ApiFallo)
    assert resultado.error.status == 409
