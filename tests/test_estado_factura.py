from estado_factura import EstadoFactura, ExoneracionVigenteItem, LineaWizard, MedioPagoWizard


def test_estado_inicial():
    estado = EstadoFactura()
    assert estado.paso == 1
    assert len(estado.lineas) == 1
    assert estado.medios_pago == []
    assert estado.condicion_venta == "01"
    assert estado.moneda == "CRC"
    assert estado.tipo_cambio == 1.0


def test_establecer_cliente_resetea_exoneraciones_y_lineas():
    estado = EstadoFactura()
    estado.exoneraciones_vigentes = [ExoneracionVigenteItem(id="e-1", descripcion="X")]
    estado.lineas = [LineaWizard(exoneracion_id="e-1"), LineaWizard(exoneracion_id="e-1")]

    estado.establecer_cliente("c-2", "Otro cliente", "02 456")

    assert estado.cliente_id == "c-2"
    assert estado.exoneraciones_vigentes == []
    assert all(linea.exoneracion_id is None for linea in estado.lineas)


def test_establecer_condicion_venta_limpia_campos_dependientes():
    estado = EstadoFactura()
    estado.establecer_condicion_venta("02")
    estado.plazo_credito = 30
    estado.establecer_condicion_venta("01")
    assert estado.plazo_credito is None

    estado.establecer_condicion_venta("99")
    estado.condicion_venta_otros = "Detalle"
    estado.establecer_condicion_venta("01")
    assert estado.condicion_venta_otros == ""


def test_establecer_moneda_crc_fuerza_tipo_cambio_1():
    estado = EstadoFactura()
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 550.0
    estado.establecer_moneda("CRC")
    assert estado.tipo_cambio == 1.0


def test_agregar_y_quitar_linea():
    estado = EstadoFactura()
    estado.agregar_linea()
    assert len(estado.lineas) == 2

    estado.quitar_linea(0)
    assert len(estado.lineas) == 1


def test_quitar_linea_no_deja_la_lista_vacia():
    estado = EstadoFactura()
    estado.quitar_linea(0)
    assert len(estado.lineas) == 1


def test_a_cuerpo_creacion_omite_campos_no_aplicables():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["clienteId"] == "c-1"
    assert "plazoCredito" not in cuerpo
    assert "condicionVentaOtros" not in cuerpo
    assert "mediosPago" not in cuerpo
    assert "otrosCargos" not in cuerpo
    assert cuerpo["lineas"][0] == {
        "productoId": "p-1",
        "cantidad": 1,
        "precioUnitario": 100,
    }


def test_a_cuerpo_creacion_incluye_condicion_credito_y_descuento():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.establecer_condicion_venta("02")
    estado.plazo_credito = 30
    estado.lineas = [
        LineaWizard(
            producto_id="p-1",
            cantidad=1,
            precio_unitario=100,
            descuento_monto=10,
            descuento_razon="Pronto pago",
        )
    ]
    estado.medios_pago = [MedioPagoWizard(tipo_medio_pago="01", total_medio_pago=90)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["plazoCredito"] == 30
    assert cuerpo["lineas"][0]["descuentos"] == [
        {"montoDescuento": 10, "naturalezaDescuento": "Pronto pago"}
    ]
    assert cuerpo["mediosPago"] == [{"tipoMedioPago": "01", "totalMedioPago": 90}]


def test_a_cuerpo_creacion_medio_pago_otros_solo_si_tipo_99():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]
    estado.medios_pago = [
        MedioPagoWizard(tipo_medio_pago="99", medio_pago_otros="Cripto", total_medio_pago=100)
    ]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["mediosPago"][0]["medioPagoOtros"] == "Cripto"


def test_a_cuerpo_creacion_moneda_crc_fuerza_tipo_cambio():
    estado = EstadoFactura()
    estado.cliente_id = "c-1"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]
    # simular estado inconsistente (no debería pasar vía establecer_moneda,
    # pero a_cuerpo_creacion es la última línea de defensa, igual que en
    # acciones.ts del frontend)
    estado.moneda = "CRC"
    estado.tipo_cambio = 550.0

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["tipoCambio"] == 1.0
