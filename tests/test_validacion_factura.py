import validacion_factura as v
from estado_factura import EstadoFactura, LineaWizard, MedioPagoWizard, OtroCargoWizard


def test_validar_paso1_requiere_cliente():
    estado = EstadoFactura()
    errores = v.validar_paso1(estado)
    assert "cliente_id" in errores


def test_validar_paso1_credito_requiere_plazo():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.establecer_condicion_venta("02")
    errores = v.validar_paso1(estado)
    assert "plazo_credito" in errores


def test_validar_paso1_otros_requiere_detalle():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.establecer_condicion_venta("99")
    errores = v.validar_paso1(estado)
    assert "condicion_venta_otros" in errores


def test_validar_paso1_usd_fuera_de_rango():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 100.0
    errores = v.validar_paso1(estado)
    assert "tipo_cambio" in errores


def test_validar_paso1_usd_en_rango_es_valido():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 550.0
    assert v.validar_paso1(estado) == {}


def test_validar_paso2_requiere_producto_y_cantidad():
    estado = EstadoFactura()
    estado.lineas = [LineaWizard(producto_id=None, cantidad=0, precio_unitario=-1)]
    errores = v.validar_paso2(estado)
    assert "lineas.0.producto_id" in errores
    assert "lineas.0.cantidad" in errores
    assert "lineas.0.precio_unitario" in errores


def test_validar_paso2_valido():
    estado = EstadoFactura()
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]
    assert v.validar_paso2(estado) == {}


def test_validar_medio_pago_otros_requiere_detalle():
    assert v.validar_medio_pago(MedioPagoWizard(tipo_medio_pago="99")) is not None
    assert (
        v.validar_medio_pago(
            MedioPagoWizard(tipo_medio_pago="99", medio_pago_otros="Cripto")
        )
        is None
    )


def test_validar_otro_cargo_otros_requiere_detalle():
    assert v.validar_otro_cargo(OtroCargoWizard(tipo_documento_oc="99")) is not None
    assert (
        v.validar_otro_cargo(
            OtroCargoWizard(tipo_documento_oc="99", tipo_documento_otros="Detalle")
        )
        is None
    )


def test_validar_paso3_requiere_al_menos_un_medio_pago():
    estado = EstadoFactura()
    errores = v.validar_paso3(estado)
    assert "medios_pago" in errores


def test_validar_paso3_maximo_4_medios_pago():
    estado = EstadoFactura()
    estado.medios_pago = [
        MedioPagoWizard(tipo_medio_pago="01", total_medio_pago=1) for _ in range(5)
    ]
    errores = v.validar_paso3(estado)
    assert "medios_pago" in errores
