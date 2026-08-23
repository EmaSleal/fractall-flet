from estado_nota_credito import (
    EstadoNotaCredito,
    LineaNcSeleccionable,
    calcular_iva_acreditar,
    calcular_iva_total_acreditar,
    calcular_subtotal_acreditar,
    calcular_subtotal_total_acreditar,
    calcular_total_acreditar,
    lineas_seleccionables_desde_factura,
)


def _linea(**overrides) -> LineaNcSeleccionable:
    base = dict(
        linea_factura_origen_id="l-1",
        numero_linea=1,
        codigo_cabys_aplicado="8399000000000",
        unidad_medida_comercial="Unid",
        cantidad_origen=10,
        precio_unitario=100,
        subtotal_origen=1000,
        porcentaje_impuesto_aplicado=13,
        seleccionada=False,
        cantidad_acreditar=10,
    )
    base.update(overrides)
    return LineaNcSeleccionable(**base)


def _estado(**overrides) -> EstadoNotaCredito:
    base = dict(
        factura_origen_id="f-1",
        factura_origen_consecutivo="00100001010000000001",
        cliente_nombre="Ana",
        lineas=[_linea()],
        moneda="CRC",
    )
    base.update(overrides)
    return EstadoNotaCredito(**base)


class _LineaFacturaFalsa:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.numero_linea = kwargs["numero_linea"]
        self.codigo_cabys_aplicado = kwargs["codigo_cabys_aplicado"]
        self.unidad_medida_comercial = kwargs["unidad_medida_comercial"]
        self.cantidad = kwargs["cantidad"]
        self.precio_unitario = kwargs["precio_unitario"]
        self.subtotal = kwargs["subtotal"]
        self.porcentaje_impuesto_aplicado = kwargs["porcentaje_impuesto_aplicado"]


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
    assert estado.lineas[0].seleccionada is False
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


def test_alternar_seleccion_linea():
    estado = _estado()
    assert estado.lineas[0].seleccionada is False

    estado.alternar_seleccion_linea(0)
    assert estado.lineas[0].seleccionada is True

    estado.alternar_seleccion_linea(0)
    assert estado.lineas[0].seleccionada is False


def test_establecer_cantidad_acreditar():
    estado = _estado()
    estado.establecer_cantidad_acreditar(0, 3)
    assert estado.lineas[0].cantidad_acreditar == 3


def test_lineas_seleccionables_desde_factura_mapea_campos_y_arranca_sin_seleccion():
    lineas_origen = [
        _LineaFacturaFalsa(
            id="l-1",
            numero_linea=1,
            codigo_cabys_aplicado="8399000000000",
            unidad_medida_comercial="Unid",
            cantidad=5,
            precio_unitario=200,
            subtotal=1000,
            porcentaje_impuesto_aplicado=13,
        )
    ]

    lineas = lineas_seleccionables_desde_factura(lineas_origen)

    assert len(lineas) == 1
    linea = lineas[0]
    assert linea.linea_factura_origen_id == "l-1"
    assert linea.numero_linea == 1
    assert linea.codigo_cabys_aplicado == "8399000000000"
    assert linea.unidad_medida_comercial == "Unid"
    assert linea.cantidad_origen == 5
    assert linea.precio_unitario == 200
    assert linea.subtotal_origen == 1000
    assert linea.porcentaje_impuesto_aplicado == 13
    assert linea.seleccionada is False
    assert linea.cantidad_acreditar == 5


def test_a_cuerpo_creacion_solo_incluye_lineas_seleccionadas():
    linea_seleccionada = _linea(
        linea_factura_origen_id="l-1", seleccionada=True, cantidad_acreditar=4
    )
    linea_no_seleccionada = _linea(linea_factura_origen_id="l-2", seleccionada=False)
    estado = _estado(lineas=[linea_seleccionada, linea_no_seleccionada])
    estado.codigo_referencia = "06"

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["facturaReferenciaId"] == "f-1"
    assert cuerpo["codigoReferencia"] == "06"
    assert cuerpo["lineas"] == [{"lineaFacturaOrigenId": "l-1", "cantidad": 4}]


def test_a_cuerpo_creacion_shape_minimo_sin_producto_ni_precio():
    linea = _linea(linea_factura_origen_id="l-1", seleccionada=True, cantidad_acreditar=2)
    estado = _estado(lineas=[linea])
    estado.codigo_referencia = "01"

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["lineas"][0] == {"lineaFacturaOrigenId": "l-1", "cantidad": 2}
    assert "productoId" not in cuerpo["lineas"][0]
    assert "precioUnitario" not in cuerpo["lineas"][0]
    assert "codigoCabysAplicado" not in cuerpo["lineas"][0]


def test_a_cuerpo_creacion_omite_codigo_referencia_otro_y_razon_si_no_aplican():
    linea = _linea(seleccionada=True)
    estado = _estado(lineas=[linea])
    estado.codigo_referencia = "01"

    cuerpo = estado.a_cuerpo_creacion()

    assert "codigoReferenciaOtro" not in cuerpo
    assert "razon" not in cuerpo


def test_a_cuerpo_creacion_incluye_codigo_referencia_otro_si_es_99():
    linea = _linea(seleccionada=True)
    estado = _estado(lineas=[linea])
    estado.codigo_referencia = "99"
    estado.codigo_referencia_otro = "Ajuste manual"

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["codigoReferenciaOtro"] == "Ajuste manual"


def test_a_cuerpo_creacion_incluye_razon_con_texto():
    linea = _linea(seleccionada=True)
    estado = _estado(lineas=[linea])
    estado.codigo_referencia = "01"
    estado.razon = "  Devolución parcial  "

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["razon"] == "Devolución parcial"


def test_a_cuerpo_creacion_no_valida_tope_de_monto():
    linea = _linea(
        seleccionada=True,
        cantidad_origen=1000,
        cantidad_acreditar=1000,
        subtotal_origen=1_000_000_000,
    )
    estado = _estado(lineas=[linea])
    estado.codigo_referencia = "01"

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["lineas"][0]["cantidad"] == 1000


def test_calcular_subtotal_acreditar_proporcional():
    linea = _linea(cantidad_origen=10, cantidad_acreditar=4, subtotal_origen=1000)
    assert calcular_subtotal_acreditar(linea) == 400


def test_calcular_subtotal_acreditar_cantidad_origen_cero_no_divide_por_cero():
    linea = _linea(cantidad_origen=0, cantidad_acreditar=0, subtotal_origen=0)
    assert calcular_subtotal_acreditar(linea) == 0


def test_calcular_iva_acreditar_proporcional():
    linea = _linea(
        cantidad_origen=10,
        cantidad_acreditar=4,
        subtotal_origen=1000,
        porcentaje_impuesto_aplicado=13,
    )
    assert calcular_iva_acreditar(linea) == 400 * 0.13


def test_calcular_totales_solo_suman_lineas_seleccionadas():
    seleccionada = _linea(
        linea_factura_origen_id="l-1",
        seleccionada=True,
        cantidad_origen=10,
        cantidad_acreditar=5,
        subtotal_origen=1000,
        porcentaje_impuesto_aplicado=13,
    )
    no_seleccionada = _linea(
        linea_factura_origen_id="l-2",
        seleccionada=False,
        cantidad_origen=10,
        cantidad_acreditar=10,
        subtotal_origen=5000,
        porcentaje_impuesto_aplicado=13,
    )
    lineas = [seleccionada, no_seleccionada]

    subtotal_esperado = 500  # 1000 * (5/10)
    iva_esperado = subtotal_esperado * 0.13

    assert calcular_subtotal_total_acreditar(lineas) == subtotal_esperado
    assert calcular_iva_total_acreditar(lineas) == iva_esperado
    assert calcular_total_acreditar(lineas) == subtotal_esperado + iva_esperado
