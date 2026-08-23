from estado_factura import LineaWizard
from estado_nota_debito import EstadoNotaDebito


def _estado(**overrides) -> EstadoNotaDebito:
    base = dict(
        factura_origen_id="f-1",
        factura_origen_consecutivo="00100001010000000001",
        cliente_nombre="Ana",
        moneda="CRC",
    )
    base.update(overrides)
    return EstadoNotaDebito(**base)


def test_estado_inicial():
    estado = _estado()
    assert estado.paso == 1
    assert estado.factura_origen_id == "f-1"
    assert estado.factura_origen_consecutivo == "00100001010000000001"
    assert estado.cliente_nombre == "Ana"
    assert estado.moneda == "CRC"
    assert estado.codigo_referencia == ""
    assert estado.codigo_referencia_otro == ""
    assert estado.razon == ""
    assert len(estado.lineas) == 1
    assert estado.error_servidor is None


def test_establecer_codigo_referencia_limpia_otro_si_deja_de_ser_99():
    estado = _estado()
    estado.establecer_codigo_referencia("99")
    estado.codigo_referencia_otro = "Detalle del motivo"

    estado.establecer_codigo_referencia("01")

    assert estado.codigo_referencia == "01"
    assert estado.codigo_referencia_otro == ""


def test_establecer_codigo_referencia_conserva_otro_si_sigue_siendo_99():
    estado = _estado()
    estado.establecer_codigo_referencia("99")
    estado.codigo_referencia_otro = "Detalle del motivo"

    estado.establecer_codigo_referencia("99")

    assert estado.codigo_referencia_otro == "Detalle del motivo"


def test_agregar_y_quitar_linea():
    estado = _estado()
    estado.agregar_linea()
    assert len(estado.lineas) == 2

    estado.quitar_linea(0)
    assert len(estado.lineas) == 1


def test_quitar_linea_no_deja_la_lista_vacia():
    estado = _estado()
    estado.quitar_linea(0)
    assert len(estado.lineas) == 1


def test_a_cuerpo_creacion_incluye_factura_referencia_id_y_codigo_referencia():
    estado = _estado()
    estado.codigo_referencia = "06"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["facturaReferenciaId"] == "f-1"
    assert cuerpo["codigoReferencia"] == "06"
    assert cuerpo["lineas"][0] == {
        "productoId": "p-1",
        "cantidad": 1,
        "precioUnitario": 100,
    }


def test_a_cuerpo_creacion_omite_codigo_referencia_otro_y_razon_si_no_aplican():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert "codigoReferenciaOtro" not in cuerpo
    assert "razon" not in cuerpo


def test_a_cuerpo_creacion_incluye_codigo_referencia_otro_si_es_99():
    estado = _estado()
    estado.codigo_referencia = "99"
    estado.codigo_referencia_otro = "Ajuste manual"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["codigoReferenciaOtro"] == "Ajuste manual"


def test_a_cuerpo_creacion_omite_codigo_referencia_otro_si_99_sin_texto():
    estado = _estado()
    estado.codigo_referencia = "99"
    estado.codigo_referencia_otro = "   "
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert "codigoReferenciaOtro" not in cuerpo


def test_a_cuerpo_creacion_incluye_razon_con_texto():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.razon = "  Ajuste de precio  "
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["razon"] == "Ajuste de precio"


def test_a_cuerpo_creacion_no_valida_tope_de_monto():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.lineas = [
        LineaWizard(producto_id="p-1", cantidad=1000, precio_unitario=1_000_000),
    ]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["lineas"][0]["cantidad"] == 1000
    assert cuerpo["lineas"][0]["precioUnitario"] == 1_000_000
